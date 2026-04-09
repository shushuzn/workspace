import { dirname } from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
const __selfDir = dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: __selfDir + '/.env' });
import { TemperatureScheduler } from './shared/temperatureScheduler.js';
import { ConceptJumpTracker } from './shared/conceptJumpTracker.js';
import { MiniMaxEmbedder } from './shared/embedder.js';
import { QualityScorer } from './shared/qualityScorer.js';
import {
  discoverBridgeConcepts,
  extractBridgePool,
} from './shared/bridgeDiscovery.js';
import { withRetry, RetryError } from './shared/retryUtils.js';
import { limiters } from './shared/rateLimiter.js';
import { ChatCache } from './shared/chatCache.js';
import { loadConfig } from './shared/configLoader.js';
import {
  llmCallsTotal,
  cacheHitsTotal,
  cacheMissesTotal,
} from './shared/metrics.js';
import { Tournament } from './shared/tournament.js';
import { MemoryStore } from './shared/memoryStore.js';
import fs from 'fs';
import path from 'path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ─── 配置 ───────────────────────────────────────────────
const cfg = loadConfig();
const API_KEY = cfg.minimaxApiKey;
const API_URL = 'https://api.minimaxi.com/v1/chat/completions';
const MODEL = cfg.minimaxModel;
const OLLAMA_URL = cfg.ollamaUrl;
const OLLAMA_MODEL = cfg.ollamaModel;
const USE_OLLAMA = cfg.useOllama;
const DEFAULT_ROUNDS = cfg.defaultRounds;

// ─── 多模型路由 ────────────────────────────────────────
const LLM_PROVIDERS = [];
if (cfg.openaiApiKey) {
  LLM_PROVIDERS.push({
    name: 'openai',
    priority: 1,
    call: (msgs, temp, maxTok, signal) =>
      chatOpenAI(msgs, temp, maxTok, signal),
  });
}
if (cfg.anthropicApiKey) {
  LLM_PROVIDERS.push({
    name: 'anthropic',
    priority: 2,
    call: (msgs, temp, maxTok, signal) =>
      chatAnthropic(msgs, temp, maxTok, signal),
  });
}
// MiniMax 兜底（默认启用，不在 LLM_PROVIDERS 列表里避免优先级冲突）
const USE_MINIMAX_FALLBACK = !USE_OLLAMA && API_KEY;

// ─── Chat Cache (LRU, session-scoped) ─────────────────────
const chatCache = new ChatCache(100);

// ─── Tournament (Elo ratings) ─────────────────────────
const TOURNAMENT_FILE = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  'tournament.json'
);
let tournament = new Tournament();
const memoryStore = new MemoryStore();

function loadTournament() {
  try {
    if (fs.existsSync(TOURNAMENT_FILE)) {
      const data = JSON.parse(fs.readFileSync(TOURNAMENT_FILE, 'utf8'));
      tournament = Tournament.fromJSON(data);
    }
  } catch {
    tournament = new Tournament();
  }
  for (const p of debatePersonas) tournament.register(p.name);
  for (const p of personas) tournament.register(p.name);
}

function saveTournament() {
  fs.writeFileSync(
    TOURNAMENT_FILE,
    JSON.stringify(tournament.toJSON(), null, 2)
  );
}

async function chatWithRouter(messages, temperature, maxTokens, signal) {
  // Cache lookup — keyed on content only (signal is an abort handle, not request identity)
  const cached = chatCache.get(messages, temperature, maxTokens);
  if (cached !== null) {
    cacheHitsTotal.inc();
    console.log(
      color('  🔁 [cache hit] ', 90) +
        `(hit rate: ${chatCache.stats().hitRate})`
    );
    return cached;
  }
  cacheMissesTotal.inc();

  let result;
  // 1. 尝试所有已配置的第三方模型
  for (const provider of LLM_PROVIDERS) {
    try {
      result = await provider.call(messages, temperature, maxTokens, signal);
      llmCallsTotal.inc({ provider: provider.name, cached: 'false' });
      break;
    } catch (err) {
      console.warn(
        color(
          `  ⚠ ${provider.name} 不可用: ${err.message}，切换下一 provider…`,
          33
        )
      );
    }
  }
  if (result === undefined) {
    // 2. MiniMax兜底
    if (USE_MINIMAX_FALLBACK) {
      result = await chatMinimax(messages, temperature, maxTokens, signal);
      llmCallsTotal.inc({ provider: 'minimax', cached: 'false' });
      // 3. Ollama兜底
    } else if (USE_OLLAMA) {
      result = await chatOllama(messages, temperature, maxTokens);
      llmCallsTotal.inc({ provider: 'ollama', cached: 'false' });
    } else {
      throw new Error('没有任何可用 LLM provider');
    }
  }

  // Cache successful result (string responses only)
  if (typeof result === 'string' && result.length > 0) {
    chatCache.set(messages, temperature, maxTokens, result);
  }
  return result;
}

async function chatMinimax(messages, temperature, maxTokens, signal) {
  await limiters.minimax.acquire(30000, signal);
  return withRetry(
    async () => {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
      const s = signal
        ? mergeSignals(signal, controller.signal)
        : controller.signal;
      try {
        const res = await fetch(API_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${API_KEY}`,
          },
          body: JSON.stringify({
            model: MODEL,
            messages,
            max_tokens: maxTokens,
            temperature,
            stream: false,
          }),
          signal: s,
        });
        clearTimeout(timer);
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          const retryErr = new Error(
            err.error?.message || `HTTP ${res.status}`
          );
          retryErr.status = res.status;
          throw retryErr;
        }
        const data = await res.json();
        return data.choices?.[0]?.message?.content || '';
      } finally {
        clearTimeout(timer);
      }
    },
    {
      maxRetries: 3,
      baseDelayMs: 1000,
      maxDelayMs: 16000,
      signal,
      onRetry: (err, attempt, delay) => {
        console.warn(
          color(
            `  ⚠ MiniMax 请求失败(${err.message})，${delay.toFixed(0)}ms 后重试第 ${attempt} 次…`,
            33
          )
        );
      },
    }
  );
}

async function chatOpenAI(messages, temperature, maxTokens, signal) {
  await limiters.openai.acquire(30000, signal);
  const url = cfg.openaiUrl || 'https://api.openai.com/v1/chat/completions';
  return withRetry(
    async () => {
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${cfg.openaiApiKey}`,
        },
        body: JSON.stringify({
          model: cfg.openaiModel || 'gpt-4o-mini',
          messages: messages.map(m => ({
            role: m.role,
            content: m.content,
            ...(m.name ? { name: m.name } : {}),
          })),
          max_tokens: maxTokens,
          temperature,
          stream: false,
        }),
        signal,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        const retryErr = new Error(err.error?.message || `HTTP ${res.status}`);
        retryErr.status = res.status;
        throw retryErr;
      }
      const data = await res.json();
      return data.choices?.[0]?.message?.content || '';
    },
    {
      maxRetries: 3,
      baseDelayMs: 1000,
      maxDelayMs: 16000,
      signal,
      onRetry: (err, attempt, delay) => {
        console.warn(
          color(
            `  ⚠ OpenAI 请求失败(${err.message})，${delay.toFixed(0)}ms 后重试第 ${attempt} 次…`,
            33
          )
        );
      },
    }
  );
}

async function chatAnthropic(messages, temperature, maxTokens, signal) {
  await limiters.anthropic.acquire(30000, signal);
  const url = cfg.anthropicUrl || 'https://api.anthropic.com/v1/messages';
  const systemMsg = messages.find(m => m.role === 'system');
  const nonSystem = messages.filter(m => m.role !== 'system');
  return withRetry(
    async () => {
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': cfg.anthropicApiKey,
          'anthropic-version': '2023-06-01',
          'anthropic-dangerous-direct-browser-access': 'true',
        },
        body: JSON.stringify({
          model: cfg.anthropicModel || 'claude-sonnet-4-20250514',
          system: systemMsg?.content || '',
          messages: nonSystem,
          max_tokens: maxTokens,
          temperature,
        }),
        signal,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        const retryErr = new Error(err.error?.message || `HTTP ${res.status}`);
        retryErr.status = res.status;
        throw retryErr;
      }
      const data = await res.json();
      return data.content?.[0]?.text || '';
    },
    {
      maxRetries: 3,
      baseDelayMs: 1000,
      maxDelayMs: 16000,
      signal,
      onRetry: (err, attempt, delay) => {
        console.warn(
          color(
            `  ⚠ Anthropic 请求失败(${err.message})，${delay.toFixed(0)}ms 后重试第 ${attempt} 次…`,
            33
          )
        );
      },
    }
  );
}

const REQUEST_TIMEOUT_MS = 30_000;
const MODE_DISCUSS = 'discuss';
const MODE_DEBATE = 'debate';
const DEBATES_DIR = path.join(__dirname, 'debates');
const INDEX_FILE = path.join(DEBATES_DIR, 'index.json');

// ─── 人格定义 ───────────────────────────────────────────
const personas = [
  {
    id: 'optimist',
    name: '乐观者',
    icon: '🔥',
    color: 31,
    side: null,
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出自己的观点，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须有一个你亲眼见过或读过的真实例子。不要使用括号，不要说"我认为""我觉得"，直接说观点。`,
  },
  {
    id: 'skeptic',
    name: '怀疑者',
    icon: '🧊',
    color: 34,
    side: null,
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出自己的反对意见，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须指出一个具体的、真实存在的风险或问题。不要使用括号，不要说"我认为"，直接说质疑。`,
  },
  {
    id: 'analyst',
    name: '分析师',
    icon: '🔬',
    color: 32,
    side: null,
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出自己的数据分析，不能有任何内心独白或思考过程。说话要短，2句以内，必须包含一个真实的具体数字（如百分比、统计、年份、数量）。不要使用括号，不要说"根据数据"，直接说数字和分析结论。`,
  },
  {
    id: 'harmonizer',
    name: '调和者',
    icon: '🌱',
    color: 35,
    side: null,
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出综合方案，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须给出一个具体可操作的平衡做法。不要使用括号，不要铺垫，直接说方案。`,
  },
  {
    id: 'historian',
    name: '历史家',
    icon: '📜',
    color: 33,
    side: null,
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出历史类比，不能有任何内心独白或思考过程。说话要短，2句以内，必须引用一个真实的历史事件、时代或人物。不要使用括号，不要铺垫，直接说历史案例和教训。`,
  },
  {
    id: 'pragmatist',
    name: '务实者',
    icon: '⚙️',
    color: 36,
    side: null,
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出可执行的下一步方案，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须列出一个具体的工具、步骤或操作。不要使用括号，不要铺垫，直接说执行方案。`,
  },
  {
    id: 'wechat_writer',
    name: '公众号写手',
    icon: '✍️',
    color: 208,
    side: null,
    systemPrompt: `你是一位资深微信公众号作者，擅长写爆款文案。轮到你发言，你必须立刻给出专业的公众号文案建议，不能有任何内心独白或思考过程。
风格要求：
- 标题：数字+悬念+情绪化词汇，例："3个习惯，让我收入翻倍"
- 开头：直击痛点，用"你是不是也…"句式引发共鸣
- 正文：段落≤3行，多用短句，每段要有信息增量
- 结尾：必用"点赞+在看+分享"引导，留钩子让读者评论
不要使用括号，不要说"我认为"，直接给出可用的文案内容。`,
  },
];

// ─── 观众提问人格 ─────────────────────────────────────────
const audiencePersona = {
  id: 'audience_questioner',
  name: '现场观众',
  icon: '🙋',
  color: 35,
  side: null,
  systemPrompt: `你是一个尖锐的现场观众。轮到你提问，你必须立刻问出一个最尖锐的问题，不能有任何内心独白或思考过程。问题必须针对刚才辩论中最薄弱的论点，用一句简短的话问出来。不要用"请问""我想问"这种客气开场白，直接问。`,
};

// ─── 辩论模式人格 ─────────────────────────────────────────
const debatePersonas = [
  {
    id: 'pro_side',
    name: '正方',
    icon: '✅',
    color: 32,
    side: 'pro',
    systemPrompt: `你是一场辩论赛的正方辩手。轮到你发言，你必须立刻亮明立场、说出论据，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须有一个具体的事实、数据或真实案例支撑。不要说"我认为"，直接说"正因为…所以…"来强化立场。`,
  },
  {
    id: 'con_side',
    name: '反方',
    icon: '❌',
    color: 31,
    side: 'con',
    systemPrompt: `你是一场辩论赛的反方辩手。轮到你发言，你必须立刻亮明反对立场、说出反驳，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须指出对方论据的漏洞或一个相反的具体事实。不要说"我认为"，直接说"然而…实际上…"来动摇正方。`,
  },
  {
    id: 'analyst',
    name: '分析师',
    icon: '🔬',
    color: 34,
    side: null,
    systemPrompt: `你是一场辩论赛的事实核查官。轮到你发言，你必须立刻指出哪一方的论据更有数据支撑、哪一方存在逻辑漏洞。说话要短，2句以内，必须引用具体数字或事实来评判。不要偏袒任何一方，只认数据和逻辑。`,
  },
  {
    id: 'skeptic',
    name: '质疑者',
    icon: '🧊',
    color: 36,
    side: null,
    systemPrompt: `你是一场辩论赛的悲观者。轮到你发言，你必须立刻从反方视角提出最有力的质疑，找出正方论据的最大弱点。说话要短，2句以内，结尾必须指出一个真实的、不可忽视的风险或漏洞。`,
  },
  {
    id: 'synthesizer',
    name: '综合者',
    icon: '⚖️',
    color: 33,
    side: null,
    systemPrompt: `你是一场辩论赛的裁判长。轮到你发言，你必须立刻综合双方观点，指出共识点和最大分歧，给出一个超越对立的综合判断。说话要短，2句以内，结尾必须说出中立但有价值的结论。不要说"我认为公平地说"，直接给出判断。`,
  },
  {
    id: 'neutral',
    name: '中立者',
    icon: '😐',
    color: 90,
    side: null,
    systemPrompt: `你是一场辩论赛的中立观察者。轮到你发言，你必须从第三方视角提出正反双方都忽略的盲点，或者指出双方论点中最有说服力的共同点。说话要短，2句以内。不要站队，只找共识和盲区。`,
  },
  {
    id: 'socratic',
    name: '苏格拉底',
    icon: '❓',
    color: 35,
    side: null,
    systemPrompt: `你是一场辩论赛的苏格拉底式提问者。轮到你发言，你必须用反问和追问来暴露双方论点中的矛盾或未证明的假设。不要直接否定，而是连续追问让逻辑漏洞自我暴露。说话要短，2句以内，以问句结尾。`,
  },
];

// ─── 工具函数 ───────────────────────────────────────────
function color(text, code) {
  return `\x1b[${code}m${text}\x1b[0m`;
}

function isEnglishCoT(sentence) {
  const enChars = (sentence.match(/[a-zA-Z]/g) || []).length;
  const totalLen = sentence.replace(/\s/g, '').length;
  if (totalLen > 0 && enChars / totalLen > 0.4) return true;
  const trimmed = sentence.trim();
  return /^(The user|Let me|I need to|I think|I believe|In my opinion|I should|I will|Speaker note)\b/i.test(
    trimmed
  );
}

function cleanSentence(s) {
  if (s.length < 4) return false;
  if (isEnglishCoT(s)) return false;
  if (/^['"'']$/.test(s)) return false;
  if (/^[1-9][.、]\s*[^，。！？]{1,15}[。]?$/.test(s.trim())) return false;
  const instructionKeywords = [
    '句以内',
    '结尾必须',
    '真实',
    '具体',
    '立刻',
    '直接',
    '2句',
    '1句',
    '3句',
  ];
  const hasInstruction = instructionKeywords.some(k => s.includes(k));
  if (hasInstruction && s.length < 20) return false;
  if (
    s.includes('要求我') ||
    s.includes('扮演') ||
    s.includes('根据规则') ||
    s.includes('Style Guidance') ||
    s.includes('只输出') ||
    s.includes('不要') ||
    s.includes('禁止') ||
    s.includes('回复格式')
  )
    return false;
  return true;
}

function cleanResponse(text) {
  // 移除 ANSI 颜色码（放在最前面，防止干扰分句）
  // eslint-disable-next-line no-control-regex
  text = text.replace(/\u001b\[[0-9;]*m/g, '');
  // 剥离 HTML 标签和 think 标签
  text = text.replace(
    /<\/?(?:span|div|p|br|b|i|strong|em|think)[^>]*>/gi,
    '\n'
  );
  text = text.replace(/<[^>]+>/g, '');
  text = text.replace(/<think>[\s\S]*?<\/think>/gi, '');
  // 清理星号和括号
  text = text.replace(/\*{1,3}([^*]+)\*{1,3}/g, '$1');
  text = text.replace(/[（（].*?[）)]/gs, '');
  text = text.replace(/\(.*?\)/gs, '');
  // 移除行首编号（独立成行的指令）
  text = text.replace(/^[1-9][.、]\s*/gm, '');
  // 先按句号分割（英文+中文），逐句过滤
  const sentences = text
    .split(/(?<=[。！？])|(?<=[.!?])\s+/)
    .map(s => s.trim())
    .filter(s => cleanSentence(s))
    .slice(0, 2);
  text = sentences.join(' ').trim();
  if (!text) return '(无有效回答)';
  if (!/[。！？]$/.test(text)) text += '。';
  return text;
}

// ─── API 调用 ───────────────────────────────────────────
async function askPersona(messages, persona, topic, temperature, abortSignal) {
  const systemPrompt = `${persona.systemPrompt}\n\n重要：直接输出你的观点，不要使用括号、不要输出思考过程、不要输出引号、不要解释。只输出纯文本。`;
  const allMessages = [
    { role: 'system', name: 'system', content: systemPrompt },
    ...messages.filter(m => m.role !== 'system'),
  ];

  const signal = abortSignal;
  const raw = await chatWithRouter(allMessages, temperature, 1500, signal);
  return cleanResponse(raw);
}

// ─── Ollama chat helper ──────────────────────────────────
async function chatOllama(messages, temperature = 0.7, maxTokens = 1500) {
  await limiters.ollama.acquire(30000);
  return withRetry(
    async () => {
      const ollamaMessages = messages.map(m => ({
        role:
          m.role === 'system'
            ? 'system'
            : m.role === 'assistant'
              ? 'assistant'
              : 'user',
        content: m.content,
        ...(m.name ? { name: m.name } : {}),
      }));

      const res = await fetch(`${OLLAMA_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: OLLAMA_MODEL,
          messages: ollamaMessages,
          options: { temperature, num_predict: maxTokens },
          stream: false,
        }),
      });
      if (!res.ok) {
        const err = new Error(`Ollama error: ${res.status}`);
        err.status = res.status;
        throw err;
      }
      const data = await res.json();
      return cleanResponse(data.message?.content || '');
    },
    {
      maxRetries: 2,
      baseDelayMs: 500,
      maxDelayMs: 4000,
      onRetry: (err, attempt, delay) => {
        console.warn(
          color(
            `  ⚠ Ollama 请求失败(${err.message})，${delay.toFixed(0)}ms 后重试第 ${attempt} 次…`,
            33
          )
        );
      },
    }
  );
}

function mergeSignals(...signals) {
  const controller = new AbortController();
  for (const s of signals) {
    if (s)
      s.addEventListener('abort', () => controller.abort(), { once: true });
  }
  return controller.signal;
}

// ─── 辩论持久化 ─────────────────────────────────────────
function ensureDebatesDir() {
  if (!fs.existsSync(DEBATES_DIR)) {
    fs.mkdirSync(DEBATES_DIR, { recursive: true });
  }
}

function loadDebateIndex() {
  ensureDebatesDir();
  if (!fs.existsSync(INDEX_FILE)) return [];
  try {
    return JSON.parse(fs.readFileSync(INDEX_FILE, 'utf8'));
  } catch {
    return [];
  }
}

function saveDebateIndex(index) {
  ensureDebatesDir();
  fs.writeFileSync(INDEX_FILE, JSON.stringify(index, null, 2), 'utf8');
}

function saveResultAsJson(topic, rounds, transcript, mode, summary, stats) {
  const timestampIso = new Date().toISOString();
  const timestamp = timestampIso.replace(/[:.]/g, '-').slice(0, 19);
  const safeTopic = topic.replace(/[\\/:*?"<>|]/g, '_').slice(0, 30);
  const filename = `debate_${safeTopic}_${timestamp}.json`;
  const filepath = path.join(DEBATES_DIR, filename);

  // 计算投票结果（从 transcript 中推算）
  const votes = { pro: 0, con: 0, neutral: 0 };
  if (mode === MODE_DEBATE) {
    for (const entry of transcript) {
      const text = entry.text || '';
      if (text.includes('✅') || text.includes('正')) votes.pro++;
      else if (text.includes('❌') || text.includes('反')) votes.con++;
      else votes.neutral++;
    }
  }

  // 计算质量分
  let avgQuality = 0;
  let count = 0;
  if (stats?.roundStats) {
    for (const s of stats.roundStats) {
      if (s.quality !== undefined) {
        avgQuality += s.quality;
        count++;
      }
    }
  }
  avgQuality = count > 0 ? avgQuality / count : 0;

  const record = {
    id: filename.replace('.json', ''),
    topic,
    mode,
    rounds,
    timestamp: timestampIso,
    summary,
    votes: mode === MODE_DEBATE ? votes : null,
    avgQuality: Math.round(avgQuality),
    // 保留 transcript（flat 格式：每条发言含 persona info）
    transcript: transcript.map(e => ({
      persona: { id: e.persona.id, name: e.persona.name, icon: e.persona.icon },
      text: e.text,
      temp: e.temp,
    })),
    // 保留退火统计
    annealing: stats?.roundStats
      ? {
          initialTemp: stats.roundStats[0]?.temp ?? null,
          finalTemp:
            stats.roundStats[stats.roundStats.length - 1]?.temp ?? null,
          peakDeltaS: Math.max(...stats.roundStats.map(s => s.deltaS ?? 0)),
          roundsRun: stats.roundStats.length,
        }
      : null,
  };

  fs.writeFileSync(filepath, JSON.stringify(record, null, 2), 'utf8');

  // 更新索引
  const index = loadDebateIndex();
  const existingIdx = index.findIndex(e => e.id === record.id);
  if (existingIdx >= 0) {
    index[existingIdx] = {
      id: record.id,
      topic,
      mode,
      timestamp,
      avgQuality: record.avgQuality,
      summary: record.summary ? '(见文件)' : null,
    };
  } else {
    index.unshift({
      id: record.id,
      topic,
      mode,
      timestamp,
      avgQuality: record.avgQuality,
      summary: record.summary ? '(见文件)' : null,
    });
  }
  saveDebateIndex(index);

  return filename;
}

function exportDebateAsHtml(
  topic,
  rounds,
  transcript,
  mode,
  summary,
  stats,
  votes
) {
  const timestamp = new Date().toISOString().slice(0, 19).replace(/T/, ' ');
  const safeTopic = topic.replace(/[\\/:*?"<>|]/g, '_').slice(0, 30);
  const exportDir = path.join(DEBATES_DIR, 'export');
  if (!fs.existsSync(exportDir)) fs.mkdirSync(exportDir, { recursive: true });
  const filename = `辩论_${safeTopic}_${Date.now()}.html`;
  const filepath = path.join(exportDir, filename);

  const voteData = votes || { pro: 0, con: 0, neutral: 0 };
  const totalVotes = voteData.pro + voteData.con + voteData.neutral;
  const proPct =
    totalVotes > 0 ? Math.round((voteData.pro / totalVotes) * 100) : 0;
  const conPct =
    totalVotes > 0 ? Math.round((voteData.con / totalVotes) * 100) : 0;

  // 提取每轮温度用于图表
  const roundTemps = (stats?.roundStats || []).map(s => s.temp ?? 0);
  const roundDeltaS = (stats?.roundStats || []).map(s => s.deltaS ?? 0);

  const html = `<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${topic} - AI 辩论记录</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#0d1117;color:#e6edf3;line-height:1.6;padding:2rem}
h1{font-size:1.6rem;margin-bottom:.5rem;color:#58a6ff}
.meta{color:#8b949e;font-size:.85rem;margin-bottom:1.5rem}
.section{margin-bottom:2rem}
h2{font-size:1.1rem;color:#8b949e;border-bottom:1px solid #21262d;padding-bottom:.4rem;margin-bottom:.8rem}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:1rem;margin-bottom:1rem}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
@media(max-width:600px){.grid{grid-template-columns:1fr}}
.bar-wrap{background:#21262d;border-radius:4px;height:24px;overflow:hidden;display:flex}
.bar-pro{background:#238636;height:100%;display:flex;align-items:center;padding:0 .5rem;font-size:.8rem}
.bar-con{background:#da3633;height:100%;display:flex;align-items:center;padding:0 .5rem;font-size:.8rem;margin-left:auto}
.utterance{border-left:3px solid #30363d;padding:.5rem 1rem;margin-bottom:.6rem}
.utterance .persona{font-weight:600;font-size:.85rem;margin-bottom:.2rem}
.utterance .text{font-size:.95rem}
.utterance .meta{font-size:.75rem;margin:0}
.summary{background:#1f2937;border-radius:8px;padding:1.2rem;font-style:italic;color:#d1d5db}
.badge{display:inline-block;padding:.2rem .6rem;border-radius:20px;font-size:.8rem;font-weight:600}
.badge-good{background:#238636;color:#fff}
.badge-mid{background:#9e6a03;color:#fff}
.badge-low{background:#da3633;color:#fff}
</style>
</head>
<body>
<h1>${topic}</h1>
<p class="meta">模式：${mode} &nbsp;|&nbsp; 轮次：${rounds} &nbsp;|&nbsp; ${timestamp}</p>

${
  mode === 'debate'
    ? `
<div class="section">
<h2>📊 投票结果</h2>
<div class="card">
<div style="display:flex;gap:1rem;font-size:1.2rem;font-weight:700;margin-bottom:.6rem">
<span style="color:#238636">✅ 正方 ${voteData.pro} 票</span>
<span style="color:#da3633">❌ 反方 ${voteData.con} 票</span>
<span style="color:#8b949e">⚪ 中立 ${voteData.neutral} 票</span>
</div>
<div class="bar-wrap">
<div class="bar-pro" style="width:${proPct}%">正 ${proPct}%</div>
<div class="bar-con" style="width:${conPct}%">反 ${conPct}%</div>
</div>
</div>
</div>
`
    : ''
}

${
  roundTemps.length > 0
    ? `
<div class="section">
<h2>🌡️ 温度曲线</h2>
<div class="card">
<canvas id="tempChart" height="120"></canvas>
</div>
</div>
`
    : ''
}

${
  summary
    ? `
<div class="section">
<h2>📝 综合总结</h2>
<div class="summary">${summary}</div>
</div>
`
    : ''
}

<div class="section">
<h2>💬 辩论记录</h2>
${transcript
  .map(
    e => `
<div class="utterance" style="border-left-color:${e.persona.color === 32 ? '#238636' : e.persona.color === 31 ? '#da3633' : '#8b949e'}">
<div class="persona">${e.persona.icon} ${e.persona.name}</div>
<div class="text">${e.text.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>')}</div>
<div class="meta" style="color:#6e7681">温度: ${e.temp}</div>
</div>
`
  )
  .join('')}
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
${
  roundTemps.length > 0
    ? `
new Chart(document.getElementById('tempChart'), {
  type:'line',
  data:{
    labels:${JSON.stringify(roundTemps.map((_, i) => 'R' + i))},
    datasets:[{
      label:'温度',
      data:${JSON.stringify(roundTemps)},
      borderColor:'#58a6ff',
      backgroundColor:'rgba(88,166,255,0.1)',
      fill:true,
      tension:0.4
    },{
      label:'ΔS (概念跳跃)',
      data:${JSON.stringify(roundDeltaS)},
      borderColor:'#f78166',
      backgroundColor:'rgba(247,129,102,0.1)',
      fill:true,
      tension:0.4
    }]
  },
  options:{responsive:true,scales:{y:{grid:{color:'#21262d'}},x:{grid:{color:'#21262d'}}},plugins:{legend:{labels:{color:'#e6edf3'}}}}
});
`
    : ''
}
</script>
</body>
</html>`;

  fs.writeFileSync(filepath, html, 'utf8');
  return filename;
}

function replayDebate(id) {
  const filepath = path.join(DEBATES_DIR, `${id}.json`);
  if (!fs.existsSync(filepath)) {
    console.log(color(`辩论记录不存在: ${id}`, 31));
    return;
  }
  const debate = JSON.parse(fs.readFileSync(filepath, 'utf8'));
  console.log(color('═'.repeat(60), 1));
  console.log(color(`  🔁 辩论回放: ${debate.topic}`, 1));
  console.log(color('═'.repeat(60), 1));
  console.log(`  模式: ${debate.mode === MODE_DEBATE ? '辩论赛' : '圆桌讨论'}`);
  console.log(`  轮数: ${debate.rounds}`);
  console.log(`  时间: ${new Date(debate.timestamp).toLocaleString('zh-CN')}`);
  if (debate.summary) {
    console.log(color('\n📋 综合总结:', 1));
    console.log(`  ${debate.summary.replace(/\n/g, '\n  ')}`);
  }
  if (debate.votes) {
    console.log(color('\n📊 投票结果:', 1));
    console.log(
      `  正方 ${debate.votes.pro} 票 | 反方 ${debate.votes.con} 票 | 中立 ${debate.votes.neutral} 票`
    );
  }
  console.log(color('\n' + '─'.repeat(60), 90));
  for (const entry of debate.transcript) {
    const pName = color(`${entry.persona.icon} ${entry.persona.name}`, 90);
    console.log(`  ${pName}：${entry.text}`);
  }
  console.log(color('─'.repeat(60), 90));
}

function listDebates(args) {
  const index = loadDebateIndex();
  if (index.length === 0) {
    console.log('暂无辩论记录。运行一次辩论后会自动保存。');
    return;
  }

  // 过滤
  let filtered = index;
  if (args.includes('--debate')) {
    filtered = filtered.filter(e => e.mode === MODE_DEBATE);
  } else if (args.includes('--discuss')) {
    filtered = filtered.filter(e => e.mode === MODE_DISCUSS);
  }

  const limitMatch = args.find(a => a.match(/^--limit=(\d+)$/));
  if (limitMatch) {
    filtered = filtered.slice(0, parseInt(limitMatch.split('=')[1]));
  }

  console.log(color('辩论记录索引', 1));
  console.log(color('─'.repeat(60), 90));
  for (const e of filtered) {
    const modeTag =
      e.mode === MODE_DEBATE ? color('辩论', 32) : color('讨论', 33);
    const qualityBar =
      '★'.repeat(Math.round((e.avgQuality ?? 0) / 20)) +
      '☆'.repeat(5 - Math.round((e.avgQuality ?? 0) / 20));
    console.log(`  ${e.id}`);
    console.log(
      `    话题: ${e.topic} | ${modeTag} | 质量: ${qualityBar} ${e.avgQuality ?? '?'}/100 | ${new Date(e.timestamp).toLocaleString('zh-CN')}`
    );
    if (e.summary) console.log(`    总结: ${e.summary}`);
  }
  console.log(color('─'.repeat(60), 90));
  console.log(`共 ${filtered.length} 条记录`);
  console.log('\n使用 --replay <id> 回放，--stats 查看统计');
}

function debateStats() {
  const index = loadDebateIndex();
  if (index.length === 0) {
    console.log('暂无辩论记录。');
    return;
  }

  const total = index.length;
  const debates = index.filter(e => e.mode === MODE_DEBATE);
  const discusses = index.filter(e => e.mode === MODE_DISCUSS);
  const avgQuality =
    index.reduce((sum, e) => sum + (e.avgQuality ?? 0), 0) / total;
  const topics = [...new Set(index.map(e => e.topic))];

  console.log(color('辩论统计', 1));
  console.log(color('─'.repeat(60), 90));
  console.log(`  总记录: ${total} 条`);
  console.log(`  辩论赛: ${debates.length} 条`);
  console.log(`  自由讨论: ${discusses.length} 条`);
  console.log(`  平均质量: ${avgQuality.toFixed(1)} / 100`);
  console.log(`  涉及话题: ${topics.length} 个`);
  console.log(color('─'.repeat(60), 90));
  console.log('  话题分布:');
  for (const t of topics) {
    const cnt = index.filter(e => e.topic === t).length;
    console.log(`    ${t}: ${cnt} 次`);
  }
}

function showLeaderboard() {
  loadTournament();
  const rankings = tournament.getRankings();
  if (rankings.length === 0) {
    console.log('暂无排行榜数据。');
    return;
  }
  console.log(color('🏆 辩论锦标赛排行榜', 1));
  console.log(color('─'.repeat(60), 90));
  for (let i = 0; i < rankings.length; i++) {
    const r = rankings[i];
    const medal =
      i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `  ${i + 1}.`;
    const bar = '█'.repeat(Math.round((r.rating - 1400) / 20));
    const games = r.games < 5 ? ` (${r.games}场)` : '';
    console.log(
      `${medal} ${r.name.padEnd(8)} ${color(bar, 32)} ${r.rating}${games}  胜${r.wins} 负${r.losses}`
    );
  }
}

function showMemoryStats() {
  memoryStore._ensureLoaded();
  const total = memoryStore.size;
  if (total === 0) {
    console.log('暂无记忆数据。');
    return;
  }
  const topics = memoryStore.entries.map(e => e.topic);
  const uniqueTopics = [...new Set(topics)];
  const recent = memoryStore.entries
    .slice(-5)
    .reverse()
    .map(e => e.storedAt?.slice(0, 10) || '?');
  console.log(color('🧠 记忆统计', 1));
  console.log(color('─'.repeat(60), 90));
  console.log(`  总条目: ${total} 条`);
  console.log(`  涉及话题: ${uniqueTopics.size} 个`);
  console.log(`  最近5条:`);
  for (const e of memoryStore.entries.slice(-5).reverse()) {
    console.log(
      `    ${e.storedAt?.slice(0, 10) || '?'}  ${e.topic.slice(0, 40)}`
    );
  }
}

async function suggestTopic() {
  console.log(color('💡 正在生成推荐话题...', 90));
  const prompt = `你是一个辩论话题生成器。请生成3个适合进行辩论的热门话题，每个话题必须满足：
1. 有明确的对立双方（正方和反方）
2. 与科技、AI、社会或未来相关
3. 不是过于宽泛的题目

格式：每行一个话题，前面加数字序号，例如：
1. AI应该在招聘过程中取代人类面试官
2. 开放式办公室是否有利于团队协作
3. 社交媒体对青少年的影响弊大于利

请直接输出3个话题，不要解释。`;

  try {
    const messages = [{ role: 'user', content: prompt }];
    const result = USE_OLLAMA
      ? await chatOllama(messages, 0.8, 200)
      : await chatMinimax(messages, 0.8, 200);
    console.log(color('\n📋 推荐辩论话题：\n', 1));
    const lines = result.split('\n').filter(l => l.trim());
    for (const line of lines) {
      console.log(color(`  ${line}`, 33));
    }
    console.log(color('\n使用方式：node index.js "话题" --debate', 90));
  } catch (err) {
    console.error(color(`生成失败：${err.message}`, 31));
  }
}

// ─── 保存 TXT ───────────────────────────────────────────
function saveResultTxt(topic, rounds, transcript, mode, summary) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const safeTopic = topic.replace(/[\\/:*?"<>|]/g, '_').slice(0, 30);
  const filename = `讨论_${safeTopic}_${timestamp}.txt`;
  const filepath = path.join(__dirname, filename);

  const lines = [
    '═'.repeat(60),
    `  AI ${mode === MODE_DEBATE ? '辩论赛' : '圆桌讨论'}`,
    '═'.repeat(60),
    `话题：${topic}`,
    `轮数：${rounds}`,
    `模式：${mode === MODE_DEBATE ? '辩论赛' : '自由讨论'}`,
    `时间：${new Date().toLocaleString('zh-CN')}`,
    '─'.repeat(60),
  ];

  if (summary) {
    lines.push('', '【综合总结】', summary, '');
  }

  lines.push(
    ...transcript.map(e => `${e.persona.icon} ${e.persona.name}：${e.text}`)
  );
  lines.push('', '─'.repeat(60), `共 ${transcript.length} 条发言`);

  fs.writeFileSync(filepath, lines.join('\n'), 'utf8');
  return filename;
}

// ─── 保存结果（调用 TXT + JSON） ─────────────────────────
function saveResult(topic, rounds, transcript, mode, summary, stats) {
  const txtFile = saveResultTxt(topic, rounds, transcript, mode, summary);
  saveResultAsJson(topic, rounds, transcript, mode, summary, stats);
  return txtFile;
}

// ─── 投票 ───────────────────────────────────────────────
async function runVoting(topic, history, personas, abortSignal) {
  console.log(color('\n📊 正在收集投票...', 90));

  const votes = { pro: 0, con: 0, neutral: 0 };
  const reasons = {};

  for (const persona of personas) {
    const pName = color(`${persona.icon} ${persona.name}`, persona.color);
    process.stdout.write(`  ${pName} 投票中...`);
    const dotTimer = setInterval(
      () => process.stdout.write(color('.', persona.color)),
      150
    );

    try {
      const systemPrompt = `${persona.systemPrompt}\n\n重要：直接输出你的投票，不要输出思考过程。只输出一个字：支持正方请输出"正"，支持反方请输出"反"，中立请输出"中"。`;
      const messages = [
        { role: 'system', name: 'system', content: systemPrompt },
        ...history.filter(m => m.role !== 'system'),
      ];

      const raw = USE_OLLAMA
        ? await chatOllama(messages, 0.3, 50)
        : await chatMinimax(messages, 0.3, 50, abortSignal);

      clearInterval(dotTimer);
      process.stdout.write('\r' + '\x1b[K');
      const vote = raw.trim();

      if (vote.includes('正')) {
        votes.pro++;
        reasons[persona.id] = '正';
      } else if (vote.includes('反')) {
        votes.con++;
        reasons[persona.id] = '反';
      } else {
        votes.neutral++;
        reasons[persona.id] = '中';
      }

      console.log(
        `  ${pName} → ${vote.includes('正') ? '✅ 正' : vote.includes('反') ? '❌ 反' : '⚪ 中'}`
      );
    } catch (err) {
      clearInterval(dotTimer);
      process.stdout.write('\r' + '\x1b[K');
      votes.neutral++;
      reasons[persona.id] = '中';
      console.log(`  ${pName} → ⚪ 中 (超时)`);
    }
  }

  console.log(
    color(
      `\n📊 投票结果：正方 ${votes.pro} 票 | 反方 ${votes.con} 票 | 中立 ${votes.neutral} 票`,
      votes.pro > votes.con ? 32 : votes.con > votes.pro ? 31 : 33
    )
  );
  return { votes, reasons };
}

// ─── 总结生成 ───────────────────────────────────────────
async function generateSummary(topic, history, mode, abortSignal) {
  console.log(color('\n📝 正在生成综合总结...', 90));

  const modeLabel = mode === MODE_DEBATE ? '辩论赛' : '圆桌讨论';
  const systemPrompt = `你是一场${modeLabel}的裁判。请根据以下讨论记录，写一段200字以内的综合总结。\n\n要求：\n1. 概括双方或各方核心观点\n2. 指出最重要的共识和分歧\n3. 给出一个有价值的综合判断\n4. 直接输出总结内容，不要前缀不要署名`;

  const messages = [
    { role: 'system', name: 'system', content: systemPrompt },
    ...history.filter(m => m.role !== 'system'),
  ];

  try {
    const raw = USE_OLLAMA
      ? await chatOllama(messages, 0.4, 800)
      : await chatMinimax(messages, 0.4, 800, abortSignal);
    const summary = raw.trim();
    console.log(color('\n📋 综合总结：', 1));
    console.log(`  ${summary.replace(/\n/g, '\n  ')}`);
    return summary;
  } catch (err) {
    if (err.name !== 'AbortError') {
      console.log(color(`  ⚠ 总结生成失败：${err.message}`, 31));
    }
    return null;
  }
}

// ─── 观众提问 ───────────────────────────────────────────
async function generateAudienceQuestion(topic, history, abortSignal) {
  const systemPrompt = `你是一个尖锐的现场观众。刚才这段辩论中，某个论点有明显的漏洞或薄弱之处。\n\n直接问出那个最尖锐的问题——一句话，越短越狠越好。不要客气，不要铺垫，不要说"请问"。`;

  // 只取最近 2 轮对话，减少上下文干扰
  const recentHistory = history.filter(m => m.role !== 'system').slice(-4);

  // 过滤残留指令词
  const cleanHistory = recentHistory.map(m => ({
    ...m,
    content: m.content
      .replace(/[（（].*?[）)]/gs, '')
      .replace(/\(.*?\)/gs, '')
      .replace(
        /[,:].*?(你的任务是?|我的任务是?|辩手|正方|反方|分析师|质疑者|综合者)/g,
        ''
      )
      .trim(),
  }));

  const messages = [
    { role: 'system', name: 'system', content: systemPrompt },
    ...cleanHistory,
  ];

  try {
    const raw = USE_OLLAMA
      ? await chatOllama(messages, 0.7, 120)
      : await chatMinimax(messages, 0.7, 120, abortSignal);
    return cleanResponse(raw.trim());
  } catch (err) {
    if (err.name !== 'AbortError') {
      console.log(color(`  ⚠ 观众提问生成失败：${err.message}`, 31));
    }
    return null;
  }
}

async function runAudienceQuestion(
  topic,
  history,
  activePersonas,
  abortSignal
) {
  console.log(color('\n🙋 正在生成观众提问...', 90));

  const question = await generateAudienceQuestion(topic, history, abortSignal);
  if (!question) return null;

  const qLine = color(`🙋 现场观众：${question}`, 35);
  console.log(`\n  ${qLine}\n`);

  const historyWithQ = [
    ...history,
    { role: 'user', content: `观众追问：${question}` },
  ];
  const answers = [];

  for (const persona of activePersonas) {
    const pName = color(`${persona.icon} ${persona.name}`, persona.color);
    process.stdout.write(`  ${pName} 回答中...`);
    const dotTimer = setInterval(
      () => process.stdout.write(color('.', persona.color)),
      150
    );

    try {
      const pSystemPrompt = `${persona.systemPrompt}\n\n重要：直接输出你的回答，不要输出思考过程。观众的问题是："${question}"。`;
      const messages = [
        { role: 'system', name: 'system', content: pSystemPrompt },
        ...historyWithQ.filter(m => m.role !== 'system'),
      ];
      const raw = USE_OLLAMA
        ? await chatOllama(messages, 0.8, 300)
        : await chatMinimax(messages, 0.8, 300, abortSignal);

      clearInterval(dotTimer);
      process.stdout.write('\r' + '\x1b[K');
      const answer = cleanResponse(raw);
      console.log(`  ${pName}：${answer}`);
      answers.push({ persona, text: answer });
      historyWithQ.push({ role: 'assistant', content: answer });
    } catch (err) {
      clearInterval(dotTimer);
      process.stdout.write('\r' + '\x1b[K');
      if (err.name !== 'AbortError') {
        console.log(`  ${pName} → ⚠ ${err.message}`);
      }
    }
  }

  return { question, answers, historyWithQ };
}

// ─── 打印函数 ───────────────────────────────────────────
function printBanner(topic, rounds, mode, personaCount) {
  const modeStr = mode === MODE_DEBATE ? '辩论赛' : '圆桌讨论';
  console.log('\n' + color('═'.repeat(60), 1));
  console.log(color(`  🔥 AI ${modeStr}`, 1));
  console.log(color('═'.repeat(60), 1));
  console.log(`  话题：${topic}`);
  console.log(`  人格：${personaCount} 位`);
  console.log(`  轮次：${rounds} 轮\n`);
}

function printDivider() {
  console.log(color('─'.repeat(60), 90));
}

// ─── Markdown 摘要导出 ───────────────────────────────────
function printSummaryMarkdown(topic, roundResponses, roundStats, stats, summary, debateVotes) {
  const md = [];
  md.push(`# ${topic}`);
  md.push('');
  md.push(`> Generated by multi-agent-hub (Cognitive Annealing)`);
  md.push('');

  // 1. 发言摘要表格
  md.push('## 发言摘要');
  md.push('');
  md.push('| 轮次 | 人格 | 核心观点 | ΔS |');
  md.push('|------|------|---------|----|');
  for (let i = 0; i < roundStats.length; i++) {
    const stat = roundStats[i];
    const responses = roundResponses[i] || [];
    // 取每轮第一个发言人的观点作为代表
    const resp = responses[0];
    const personaName = resp ? `${resp.persona.icon} ${resp.persona.name}` : '—';
    const text = resp ? resp.text.replace(/\n/g, ' ').slice(0, 60) + (resp.text.length > 60 ? '…' : '') : '—';
    md.push(`| ${stat.round} | ${personaName} | ${text} | ${stat.deltaS.toFixed(3)} |`);
  }
  md.push('');

  // 2. 立场分布（辩论模式）
  if (debateVotes) {
    md.push('## 立场分布');
    md.push('');
    const total = debateVotes.pro + debateVotes.con + (debateVotes.neutral || 0);
    if (total > 0) {
      const proPct = ((debateVotes.pro / total) * 100).toFixed(0);
      const conPct = ((debateVotes.con / total) * 100).toFixed(0);
      const neuPct = ((debateVotes.neutral || 0) / total * 100).toFixed(0);
      md.push(`- 🟢 正方支持: ${debateVotes.pro} 票 (${proPct}%)`);
      md.push(`- 🔴 反方支持: ${debateVotes.con} 票 (${conPct}%)`);
      if (debateVotes.neutral) md.push(`- ⚪ 中立: ${debateVotes.neutral} 票 (${neuPct}%)`);
    }
    md.push('');
  }

  // 3. ΔS 峰值
  const peakDeltaS = Math.max(...stats.roundStats.map(s => s.deltaS ?? 0));
  const peakRound = stats.roundStats.find(s => s.deltaS === peakDeltaS)?.round ?? '?';
  md.push('## 概念跳跃');
  md.push('');
  md.push(`- **峰值 ΔS**: ${peakDeltaS.toFixed(3)} (第 ${peakRound} 轮)`);
  md.push(`- **触发阈值**: 0.35 (★ 标记)`);
  const peaks = stats.roundStats.filter(s => (s.deltaS ?? 0) > 0.35);
  if (peaks.length > 0) {
    md.push(`- **显著跳跃轮次**: ${peaks.map(p => `#${p.round}`).join(', ')}`);
  }
  md.push('');

  // 4. 综合总结
  if (summary) {
    md.push('## 综合判断');
    md.push('');
    md.push(summary.trim());
    md.push('');
  }

  // 5. 参数信息
  md.push('## 讨论参数');
  md.push('');
  md.push(`| 参数 | 值 |`);
  md.push('|------|----|');
  md.push(`| 轮次 | ${roundStats.length} |`);
  md.push(`| 初始温度 | ${stats.tempHistory?.[0]?.toFixed(2) ?? 'N/A'} |`);
  md.push(`| 临界温度 | ${stats.criticalTemp?.toFixed(2) ?? 'N/A'} |`);
  md.push(`| 辩论模式 | ${debateVotes ? '是' : '否'} |`);
  md.push('');

  console.log(md.join('\n'));
}

// ─── 退火报告 ───────────────────────────────────────────
function printAnnealingReport(topic, totalRounds, stats, roundStats) {
  const { tempHistory, deltaSHistory, criticalTemp, criticalDetected } = stats;

  console.log(color('══════════════════════════════════════════════', 1));
  console.log(color('  自适应温度探索报告', 1));
  console.log(color('══════════════════════════════════════════════', 1));
  console.log(`  话题：${topic}`);
  console.log(`  轮次：${roundStats.length}`);
  console.log('');
  console.log('  温度调度参数');
  console.log(`    初始温度：${tempHistory[0]?.toFixed(2) ?? 'N/A'}`);
  console.log(`    冷却速率：0.88`);
  console.log(`    临界 plateau：2 轮`);
  console.log('');
  console.log('  概念跳跃曲线（ΔS）');
  console.log('    ΔS 越高 = 讨论方向偏移越大');
  console.log('');
  console.log('  轮次 | 温度  | ΔS   | 质量分 | 状态');
  console.log('  -----|-------|------|--------|------');

  for (const s of roundStats) {
    const bar = s.deltaS > 0.35 ? '★'.repeat(Math.round(s.deltaS * 5)) : '';
    console.log(
      `    ${String(s.round).padStart(2)}  | ${s.temp.toFixed(2)}  | ${s.deltaS.toFixed(2)} | ${(s.quality ?? 0).toFixed(0).padStart(4)} | ${s.status} ${bar}`
    );
  }

  // ─── Per-persona 贡献度 ─────────────────────────────
  const hasContributions = roundStats.some(s => s.contributions?.length > 0);
  if (hasContributions) {
    console.log('');
    console.log(
      '  人格贡献度（与上轮均值的余弦距离，越高 = 推动概念跳跃越多）'
    );
    console.log(
      '  轮次 |',
      personas.map(p => `${p.icon}${p.name}`.slice(0, 4)).join(' | '),
      '| 均值'
    );
    console.log('  -----|' + '------|'.repeat(personas.length) + '------|');

    for (const s of roundStats) {
      if (!s.contributions?.length) continue;
      const mean =
        s.contributions.reduce((a, b) => a + b, 0) / s.contributions.length;
      const vals = s.contributions.map((v, i) => {
        const icon = personas[i]?.icon ?? '?';
        const flag = v > mean * 1.3 ? '↑' : v < mean * 0.7 ? '↓' : ' ';
        return `${v.toFixed(2)}${flag}`;
      });
      console.log(
        `    ${String(s.round).padStart(2)}  | ${vals.join(' | ')} | ${mean.toFixed(2)}`
      );
    }

    // 累计贡献排名
    console.log('');
    const totals = Array(personas.length).fill(0);
    let count = 0;
    for (const s of roundStats) {
      if (s.contributions?.length) {
        for (let i = 0; i < s.contributions.length; i++)
          totals[i] += s.contributions[i];
        count++;
      }
    }
    if (count > 0) {
      console.log('  累计贡献排名（越高越活跃）');
      const ranked = personas
        .map((p, i) => ({ icon: p.icon, name: p.name, avg: totals[i] / count }))
        .sort((a, b) => b.avg - a.avg);
      ranked.forEach((r, i) => {
        console.log(`    ${i + 1}. ${r.icon} ${r.name}: ${r.avg.toFixed(3)}`);
      });
    }
  }

  console.log('');
  if (criticalDetected && criticalTemp !== null) {
    console.log(`  临界温度：${criticalTemp.toFixed(2)}（ΔS 峰值）`);
  } else {
    console.log('  临界温度：未检测到显著峰值');
  }

  const avgQuality =
    roundStats.reduce((sum, s) => sum + (s.quality ?? 0), 0) /
    roundStats.length;
  console.log(`  本轮讨论综合评分：${avgQuality.toFixed(0)} / 100`);

  console.log(color('══════════════════════════════════════════════\n', 1));
}

// ─── 参数解析 ───────────────────────────────────────────
function parseArgs(argv) {
  const args = argv.slice(2);
  let topic = '';
  let rounds = DEFAULT_ROUNDS;
  let customInitialTemp = null;
  let mode = MODE_DISCUSS;
  let exportSummary = false;
  let exportCsv = false;

  // 离线命令：--list, --replay, --stats, --leaderboard
  if (args.includes('--list')) {
    listDebates(args);
    process.exit(0);
  }
  if (args.includes('--stats')) {
    debateStats();
    process.exit(0);
  }
  if (args.includes('--leaderboard')) {
    showLeaderboard();
    process.exit(0);
  }
  if (args.includes('--memory-stats')) {
    showMemoryStats();
    process.exit(0);
  }
  if (args.includes('--suggest-topic')) {
    suggestTopic();
    process.exit(0);
  }
  const replayIdx = args.indexOf('--replay');
  if (replayIdx >= 0 && args[replayIdx + 1]) {
    replayDebate(args[replayIdx + 1]);
    process.exit(0);
  }

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--help' || args[i] === '-h') {
      printHelp();
      process.exit(0);
    }
    if ((args[i] === '-r' || args[i] === '--rounds') && args[i + 1]) {
      const n = parseInt(args[i + 1], 10);
      if (!isNaN(n) && n > 0) rounds = Math.min(n, 10);
      i++;
    } else if (
      (args[i] === '--temp' || args[i] === '-t') &&
      args[i + 1] &&
      !args[i + 1].startsWith('-')
    ) {
      const t = parseFloat(args[i + 1]);
      if (!isNaN(t) && t > 0) customInitialTemp = Math.min(t, 2.0);
      i++;
    } else if (args[i] === '--debate') {
      mode = MODE_DEBATE;
    } else if (args[i].startsWith('-')) {
      // ignore unknown flags
    } else {
      topic = args[i];
    }
  }

  return {
    topic,
    rounds,
    customInitialTemp,
    mode,
    audienceMode: args.includes('--audience'),
    exportSummary: args.includes('--export-summary'),
    exportCsv: args.includes('--export-csv'),
  };
}

function printHelp() {
  console.log(`
🔥 AI 圆桌讨论 — Cognitive Annealing 版

用法:
  node index.js <话题> [选项]
  node index.js              # 交互模式

模式:
  默认         自由讨论模式（6种人格圆桌）
  --debate    辩论赛模式（正方/反方/分析师/质疑者/综合者）

选项:
  -r, --rounds <N>     讨论轮数 (默认 8, 最大 10)
  -t, --temp <T>       初始温度 (默认 1.2, 最大 2.0)
  --debate              启用辩论赛模式（正反双方明确立场）
  --export-summary      输出标准化 Markdown 摘要（发言摘要表格、立场分布、ΔS峰值）
  --export-csv          将每轮温度/能量/ΔS导出为CSV文件
  --list              查看辩论记录索引
  --replay <id>       回放指定辩论
  --stats             查看辩论统计
  --leaderboard       显示锦标赛排行榜
  --memory-stats      显示记忆统计
  --suggest-topic     AI 推荐辩论话题
  -h, --help          显示此帮助

示例:
  node index.js "AI是否会取代人类工作"
  node index.js "气候变化" -r 6 -t 1.0
  node index.js "气候变化" --debate -r 6
  node index.js --list                    # 查看辩论记录
  node index.js --stats                  # 查看辩论统计
  node index.js --replay debate_xxx      # 回放辩论

辩论赛模式特点:
  - 正方/反方明确亮出立场
  - 每轮结束后自动投票
  - 讨论结束后自动生成综合总结
  - 辩论人格：正方、反方、分析师、质疑者、综合者

温度调度:
  初始 1.2, 冷却率 0.88, 最低 0.3
  ΔS 峰值时进入 plateau (温度不变 2 轮)
  连续 4 轮 ΔS < 0.05 时早停

嵌入:
  优先 MiniMax embedding API
  余额不足时自动降级到 Ollama 本地 (llama3.2:1b)
`);
}

// ─── 主函数 ───────────────────────────────────────────
async function main() {
  let { topic, rounds, customInitialTemp, mode, audienceMode, exportSummary, exportCsv } = parseArgs(
    process.argv
  );

  if (!topic) {
    const rl = await import('readline');
    const iface = rl.createInterface({
      input: process.stdin,
      output: process.stdout,
    });
    topic = await new Promise(resolve =>
      iface.question('请输入讨论话题：', resolve)
    );
    iface.close();
    if (!topic.trim()) {
      console.log('话题不能为空。');
      process.exit(1);
    }
  }

  if (!USE_OLLAMA && !API_KEY && LLM_PROVIDERS.length === 0) {
    console.error(color('错误：未设置任何 LLM API Key', 31));
    console.error('请在 .env 文件中设置：MINIMAX_API_KEY=你的密钥');
    console.error('或者设置 OPENAI_API_KEY / ANTHROPIC_API_KEY');
    console.error('或者设置 USE_OLLAMA=true 使用本地模型');
    process.exit(1);
  }

  // 选择人格
  const activePersonas = mode === MODE_DEBATE ? debatePersonas : personas;
  printBanner(topic, rounds, mode, activePersonas.length);

  const abortController = new AbortController();

  process.on('SIGINT', () => {
    console.log('\n\n已停止。');
    abortController.abort();
    process.exit(0);
  });

  const history = [{ role: 'user', content: `话题：${topic}` }];

  // ─── 记忆检索：注入相关历史上下文 ────────────────────
  const pastDiscussions = memoryStore.search(topic, 3);
  if (pastDiscussions.length > 0) {
    console.log(
      color(`\n📖 发现 ${pastDiscussions.length} 条相关历史讨论：`, 90)
    );
    for (const pd of pastDiscussions) {
      console.log(color(`  话题：${pd.topic}`, 90));
      console.log(color(`  摘要：${pd.summary.slice(0, 120)}…`, 90));
      history.push({
        role: 'system',
        content: `【相关历史讨论 - 话题：${pd.topic}】${pd.summary}`,
      });
    }
    console.log(color('─'.repeat(60), 90));
  }

  if (mode === MODE_DEBATE) loadTournament();

  try {
    // ─── 退火模式主循环 ───────────────────────────────────────
    const scheduler = new TemperatureScheduler(
      customInitialTemp ? { initialTemp: customInitialTemp } : {}
    );
    const embedder = new MiniMaxEmbedder();
    const tracker = new ConceptJumpTracker(embedder);
    const scorer = new QualityScorer();
    const roundResponses = [];

    // 记录 { round, temp, deltaS, status } 用于报告
    const roundStats = [];

    for (let round = 0; round < rounds; round++) {
      const T = scheduler.getTemperature();
      scheduler.pushTempHistory(T); // 每轮只 push 一次
      const roundUtterances = [];
      roundResponses[round] = [];

      const roundHint =
        mode === MODE_DEBATE
          ? `第 ${round + 1} 轮：请亮明立场，进行有力论证。`
          : `第 ${round + 2} 轮：请继续讨论，从另一角度深入。`;

      console.log(
        color(`📍 第 ${round + 1} / ${rounds} 轮  [T=${T.toFixed(3)}]`, 90) +
          '\n'
      );

      for (const persona of activePersonas) {
        const pName = color(`${persona.icon} ${persona.name}`, persona.color);
        process.stdout.write(`  ${pName} 思考中...`);

        const dotTimer = setInterval(
          () => process.stdout.write(color('.', persona.color)),
          150
        );

        let fullText = '';
        try {
          fullText = await askPersona(
            history,
            persona,
            topic,
            T,
            abortController.signal
          );
        } catch (err) {
          if (err.name === 'AbortError') {
            clearInterval(dotTimer);
            console.log('\n\n已停止。');
            return;
          }
          fullText = color(`⚠ ${err.message}`, 31);
        }

        clearInterval(dotTimer);
        process.stdout.write('\r' + '\x1b[K');
        console.log(`  ${pName}：${fullText}`);

        roundResponses[round].push({ persona, text: fullText, temp: T });
        roundUtterances.push(fullText);
        history.push({ role: 'assistant', content: fullText });
      }

      // ─── 轮结束：计算 ΔS ──────────────────────────────
      const { deltaS, contributions } =
        await tracker.processRound(roundUtterances);
      scheduler.recordDeltaS(deltaS);

      // ─── 桥接概念发现 ────────────────────────────────
      {
        const history = scheduler.deltaSHistory;
        const prevDeltaS =
          history.length >= 2 ? history[history.length - 2] : null;
        if (prevDeltaS !== null && deltaS < 0.1 && prevDeltaS < 0.1) {
          const prevRoundResponses = roundResponses[round - 1] ?? [];
          const allTexts = roundResponses.flat().map(r => r.text);
          const bridgePool = extractBridgePool(allTexts);
          const prevTexts = prevRoundResponses.map(r => r.text);
          // positive = deltaS 最高的发言（取最后轮均值最远的那几条发言）
          const posUtterances = prevTexts.slice(-Math.min(2, prevTexts.length));
          const negUtterances = prevTexts.slice(
            0,
            Math.min(2, prevTexts.length)
          );
          if (bridgePool.length > 0) {
            const bridges = await discoverBridgeConcepts({
              positiveUtterances: posUtterances,
              negativeUtterances: negUtterances,
              bridgePool,
              topK: 3,
            });
            if (bridges.length > 0) {
              console.log(`\n  🌉 桥接概念：${bridges.join(', ')}`);
            }
          }
        }
      }

      // 记录本轮统计
      let status = '';
      if (scheduler.shouldEnterPlateau()) {
        scheduler.enterPlateau();
        status = '⭐ ΔS 峰值（触发 plateau）';
      } else if (scheduler.plateauRemaining > 0) {
        status = '🐢 plateau';
      } else if (T <= scheduler.config.minTemp) {
        status = '❄️ 最低温度';
      } else {
        status = '🔥 高温探索';
      }
      const { quality } = scorer.scoreRound(
        tracker.personaEmbeddings[tracker.personaEmbeddings.length - 1],
        deltaS,
        contributions
      );
      roundStats.push({
        round: round + 1,
        temp: T,
        deltaS,
        contributions,
        quality,
        status,
      });

      // ─── 早停检查 ───────────────────────────────────
      if (
        round >= scheduler.config.minRoundsBeforeEarlyStop - 1 &&
        scheduler.getRoundsSinceLastSignificantDelta() > 3
      ) {
        console.log(color('\n⚠ 讨论已收敛，提前结束', 33));
        break;
      }

      // ─── 观众提问阶段（辩论模式 + --audience）────────────────
      if (mode === MODE_DEBATE && audienceMode && round < rounds - 1) {
        printDivider();
        const audienceResult = await runAudienceQuestion(
          topic,
          history,
          activePersonas,
          abortController.signal
        );
        if (audienceResult) {
          const { question, answers } = audienceResult;
          history.push({ role: 'user', content: `观众追问：${question}` });
          for (const { persona, text } of answers) {
            history.push({ role: 'assistant', content: text });
          }
          roundResponses[round].push(
            { persona: audiencePersona, text: question, temp: T },
            ...answers.map(a => ({ persona: a.persona, text: a.text, temp: T }))
          );
        }
        printDivider();
      }

      scheduler.nextRound();

      if (round < rounds - 1) {
        history.push({ role: 'user', content: roundHint });
      }
    }

    printDivider();
    console.log(color('\n✅ 讨论结束\n', 32));

    // ─── 辩论模式：投票 + 总结 ─────────────────────────
    let summary = null;
    let debateVotes = null;
    if (mode === MODE_DEBATE) {
      debateVotes = await runVoting(
        topic,
        history,
        activePersonas,
        abortController.signal
      );
      summary = await generateSummary(
        topic,
        history,
        mode,
        abortController.signal
      );
    }

    // ─── 记忆持久化 ─────────────────────────────────────
    if (summary) {
      memoryStore.add({ topic, summary, mode, rounds });
    }

    // ─── 输出报告 ───────────────────────────────────────
    const stats = scheduler.getStats();
    if (exportSummary) {
      printSummaryMarkdown(topic, roundResponses, roundStats, stats, summary, debateVotes);
    } else {
      printAnnealingReport(topic, rounds, stats, roundStats);
    }

    // ─── CSV导出 ──────────────────────────────────────────
    if (exportCsv) {
      const csvLines = ['round,temp,deltaS,quality,status'];
      for (const s of roundStats) {
        csvLines.push(`${s.round},${s.temp?.toFixed(4)??''},${s.deltaS?.toFixed(4)??''},${s.quality??''},${s.status??''}`);
      }
      const csv = csvLines.join('\n');
      const path = `annealing_${Date.now()}.csv`;
      require('fs').writeFileSync(path, csv);
      console.log(`\n[CSV] Saved to ${path}`);
    }

    const filename = saveResult(
      topic,
      rounds,
      roundResponses.flat(),
      mode,
      summary,
      { ...scheduler.getStats(), roundStats }
    );
    const cacheStats = chatCache.stats();

    // ─── 导出为可分享 HTML ───────────────────────────────
    const htmlFile = exportDebateAsHtml(
      topic,
      rounds,
      roundResponses.flat(),
      mode,
      summary,
      { ...scheduler.getStats(), roundStats },
      mode === MODE_DEBATE ? debateVotes : null
    );
    console.log(color(`💾 讨论记录已保存：${filename}`, 32));
    console.log(color(`🌐 HTML 导出：${htmlFile}`, 32));
    console.log(
      color(
        `🔁 Chat cache | size: ${cacheStats.size} | hits: ${cacheStats.hits} | misses: ${cacheStats.misses} | hit rate: ${cacheStats.hitRate}`,
        90
      )
    );

    // ─── 锦标赛模式：记录辩论结果 ─────────────────────────
    if (mode === MODE_DEBATE && summary) {
      const proVotes = debateVotes?.pro ?? 0;
      const conVotes = debateVotes?.con ?? 0;
      if (proVotes !== conVotes) {
        const winner = proVotes > conVotes ? '正方' : '反方';
        const loser = proVotes > conVotes ? '反方' : '正方';
        tournament.recordResult(winner, loser, false);
        saveTournament();
        const rankings = tournament.getRankings();
        console.log(
          color(
            `🏆 排行榜: ${rankings.map(r => `${r.name}(${r.rating})`).join(' | ')}`,
            32
          )
        );
      }
    }
  } catch (err) {
    console.error(color(`\n错误：${err.message}`, 31));
    process.exit(1);
  }
}

main();
