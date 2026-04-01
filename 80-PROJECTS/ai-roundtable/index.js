import 'dotenv/config';
import { TemperatureScheduler } from './shared/temperatureScheduler.js';
import { ConceptJumpTracker } from './shared/conceptJumpTracker.js';
import { MiniMaxEmbedder } from './shared/embedder.js';
import { QualityScorer } from './shared/qualityScorer.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ─── 配置 ───────────────────────────────────────────────
const API_KEY = process.env.MINIMAX_API_KEY;
const API_URL = 'https://api.minimaxi.com/v1/chat/completions';
const MODEL = process.env.MINIMAX_MODEL || 'MiniMax-M2.7-highspeed';
const OLLAMA_URL = process.env.OLLAMA_URL || 'http://localhost:11434';
const OLLAMA_MODEL = process.env.OLLAMA_MODEL || 'llama3.2:1b';
const USE_OLLAMA = process.env.USE_OLLAMA === 'true';
const DEFAULT_ROUNDS = 5;
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
];

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
];

// ─── 工具函数 ───────────────────────────────────────────
function color(text, code) {
  return `\x1b[${code}m${text}\x1b[0m`;
}

function cleanResponse(text) {
  text = text.replace(/\*/g, '');
  text = text.replace(/[（（].*?[）)]/gs, '');
  text = text.replace(/<think>.*?\n<\/think>/gs, '');
  text = text.replace(/<think>.*$/gs, '');
  text = text.replace(/\(.*?\)/gs, '');
  text = text.replace(/[(:].*?(用户要求|用户发送|用户输入|根据规则|扮演|我需要|让我|这是一个|Style Guidance|只输出|不要|禁止|回复格式)/g, '');
  text = text.replace(/\n[^\n]*(用户|规则|扮演|我需要|让我|回复格式)[^\n]*\n/gs, '\n');
  text = text.replace(/\n{3,}/g, '\n\n');
  text = text.replace(/^\s*\n/, '');
  const sentences = text
    .split(/[。\！？\n]/)
    .map(s => s.trim())
    .filter(s => {
      if (s.length < 4) return false;
      if (/^['"'']$/.test(s)) return false;
      if (s.includes('要求我') || s.includes('扮演') || s.includes('根据规则') || s.includes('Style Guidance') || s.includes('只输出') || s.includes('不要') || s.includes('禁止') || s.includes('回复格式')) return false;
      if (/^\(?[0-9a-zA-Z]?\s?[.、:：]?\s?(立刻|直接)/.test(s)) return false;
      return true;
    })
    .slice(0, 2);
  text = sentences.join('。').trim();
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

  // USE_OLLAMA 模式：跳过 API 直接用本地模型
  if (USE_OLLAMA) {
    return chatOllama(allMessages, temperature, 1500);
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  const signal = abortSignal
    ? mergeSignals(abortSignal, controller.signal)
    : controller.signal;

  let res;
  try {
    res = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${API_KEY}`,
      },
      body: JSON.stringify({
        model: MODEL,
        messages: allMessages,
        max_tokens: 1500,
        temperature: temperature,
        stream: false,
      }),
      signal,
    });
  } finally {
    clearTimeout(timeoutId);
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const msg = err.error?.message || `HTTP ${res.status}`;
    if (msg.includes('not support') || msg.includes('model')) {
      throw new Error(`模型不可用：${msg}。请在 .env 中设置 MINIMAX_MODEL 为可用模型名称。`);
    }
    throw new Error(msg);
  }

  const data = await res.json();
  const raw = data.choices?.[0]?.message?.content || '';
  return cleanResponse(raw);
}

// ─── Ollama chat helper ──────────────────────────────────
async function chatOllama(messages, temperature = 0.7, maxTokens = 1500) {
  // Convert messages to Ollama format
  const ollamaMessages = messages.map(m => ({
    role: m.role === 'system' ? 'system' : m.role === 'assistant' ? 'assistant' : 'user',
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
  if (!res.ok) throw new Error(`Ollama error: ${res.status}`);
  const data = await res.json();
  return cleanResponse(data.message?.content || '');
}

function mergeSignals(...signals) {
  const controller = new AbortController();
  for (const s of signals) {
    if (s) s.addEventListener('abort', () => controller.abort(), { once: true });
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
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
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
      if (s.quality !== undefined) { avgQuality += s.quality; count++; }
    }
  }
  avgQuality = count > 0 ? avgQuality / count : 0;

  const record = {
    id: filename.replace('.json', ''),
    topic,
    mode,
    rounds,
    timestamp,
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
    annealing: stats?.roundStats ? {
      initialTemp: stats.roundStats[0]?.temp ?? null,
      finalTemp: stats.roundStats[stats.roundStats.length - 1]?.temp ?? null,
      peakDeltaS: Math.max(...(stats.roundStats.map(s => s.deltaS ?? 0))),
      roundsRun: stats.roundStats.length,
    } : null,
  };

  fs.writeFileSync(filepath, JSON.stringify(record, null, 2), 'utf8');

  // 更新索引
  const index = loadDebateIndex();
  const existingIdx = index.findIndex(e => e.id === record.id);
  if (existingIdx >= 0) {
    index[existingIdx] = { id: record.id, topic, mode, timestamp, avgQuality: record.avgQuality, summary: record.summary ? '(见文件)' : null };
  } else {
    index.unshift({ id: record.id, topic, mode, timestamp, avgQuality: record.avgQuality, summary: record.summary ? '(见文件)' : null });
  }
  saveDebateIndex(index);

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
    console.log(`  正方 ${debate.votes.pro} 票 | 反方 ${debate.votes.con} 票 | 中立 ${debate.votes.neutral} 票`);
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
    const modeTag = e.mode === MODE_DEBATE ? color('辩论', 32) : color('讨论', 33);
    const qualityBar = '★'.repeat(Math.round((e.avgQuality ?? 0) / 20)) + '☆'.repeat(5 - Math.round((e.avgQuality ?? 0) / 20));
    console.log(`  ${e.id}`);
    console.log(`    话题: ${e.topic} | ${modeTag} | 质量: ${qualityBar} ${e.avgQuality ?? '?'}/100 | ${new Date(e.timestamp).toLocaleString('zh-CN')}`);
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
  const avgQuality = index.reduce((sum, e) => sum + (e.avgQuality ?? 0), 0) / total;
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

  lines.push(...transcript.map(e => `${e.persona.icon} ${e.persona.name}：${e.text}`));
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
    const dotTimer = setInterval(() => process.stdout.write(color('.', persona.color)), 150);

    try {
      const systemPrompt = `${persona.systemPrompt}\n\n重要：直接输出你的投票，不要输出思考过程。只输出一个字：支持正方请输出"正"，支持反方请输出"反"，中立请输出"中"。`;
      const messages = [
        { role: 'system', name: 'system', content: systemPrompt },
        ...history.filter(m => m.role !== 'system'),
      ];

      const raw = USE_OLLAMA
        ? await chatOllama(messages, 0.3, 50)
        : await (async () => {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
            const signal = mergeSignals(abortSignal, controller.signal);
            const res = await fetch(API_URL, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${API_KEY}` },
              body: JSON.stringify({ model: MODEL, messages, max_tokens: 50, temperature: 0.3, stream: false }),
              signal,
            });
            clearTimeout(timeoutId);
            const data = await res.json();
            return data.choices?.[0]?.message?.content || '';
          })();

      clearInterval(dotTimer);
      process.stdout.write('\r' + '\x1b[K');
      const vote = raw.trim();

      if (vote.includes('正')) { votes.pro++; reasons[persona.id] = '正'; }
      else if (vote.includes('反')) { votes.con++; reasons[persona.id] = '反'; }
      else { votes.neutral++; reasons[persona.id] = '中'; }

      console.log(`  ${pName} → ${vote.includes('正') ? '✅ 正' : vote.includes('反') ? '❌ 反' : '⚪ 中'}`);
    } catch (err) {
      clearInterval(dotTimer);
      process.stdout.write('\r' + '\x1b[K');
      votes.neutral++;
      reasons[persona.id] = '中';
      console.log(`  ${pName} → ⚪ 中 (超时)`);
    }
  }

  console.log(color(`\n📊 投票结果：正方 ${votes.pro} 票 | 反方 ${votes.con} 票 | 中立 ${votes.neutral} 票`, votes.pro > votes.con ? 32 : votes.con > votes.pro ? 31 : 33));
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
      : await (async () => {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS * 2);
          const signal = mergeSignals(abortSignal, controller.signal);
          const res = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${API_KEY}` },
            body: JSON.stringify({ model: MODEL, messages, max_tokens: 800, temperature: 0.4, stream: false }),
            signal,
          });
          clearTimeout(timeoutId);
          const data = await res.json();
          return data.choices?.[0]?.message?.content || '';
        })();
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
    console.log('  人格贡献度（与上轮均值的余弦距离，越高 = 推动概念跳跃越多）');
    console.log('  轮次 |', personas.map(p => `${p.icon}${p.name}`.slice(0, 4)).join(' | '), '| 均值');
    console.log('  -----|' + '------|'.repeat(personas.length) + '------|');

    for (const s of roundStats) {
      if (!s.contributions?.length) continue;
      const mean = s.contributions.reduce((a, b) => a + b, 0) / s.contributions.length;
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
        for (let i = 0; i < s.contributions.length; i++) totals[i] += s.contributions[i];
        count++;
      }
    }
    if (count > 0) {
      console.log('  累计贡献排名（越高越活跃）');
      const ranked = personas.map((p, i) => ({ icon: p.icon, name: p.name, avg: totals[i] / count }))
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

  const avgQuality = roundStats.reduce((sum, s) => sum + (s.quality ?? 0), 0) / roundStats.length;
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

  // 离线命令：--list, --replay, --stats
  if (args.includes('--list')) {
    listDebates(args);
    process.exit(0);
  }
  if (args.includes('--stats')) {
    debateStats();
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
    } else if ((args[i] === '--temp' || args[i] === '-t') && args[i + 1] && !args[i + 1].startsWith('-')) {
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

  return { topic, rounds, customInitialTemp, mode };
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
  --list              查看辩论记录索引
  --replay <id>       回放指定辩论
  --stats             查看辩论统计
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
  let { topic, rounds, customInitialTemp, mode } = parseArgs(process.argv);

  if (!topic) {
    const rl = await import('readline');
    const iface = rl.createInterface({ input: process.stdin, output: process.stdout });
    topic = await new Promise(resolve => iface.question('请输入讨论话题：', resolve));
    iface.close();
    if (!topic.trim()) {
      console.log('话题不能为空。');
      process.exit(1);
    }
  }

  if (!USE_OLLAMA && !API_KEY) {
    console.error(color('错误：未设置 MINIMAX_API_KEY', 31));
    console.error('请在 .env 文件中设置：MINIMAX_API_KEY=你的密钥');
    console.error('或设置 USE_OLLAMA=true 使用本地模型');
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
      scheduler.pushTempHistory(T);  // 每轮只 push 一次
      const roundUtterances = [];
      roundResponses[round] = [];

      const roundHint = mode === MODE_DEBATE
        ? `第 ${round + 1} 轮：请亮明立场，进行有力论证。`
        : `第 ${round + 2} 轮：请继续讨论，从另一角度深入。`;

      console.log(color(`📍 第 ${round + 1} / ${rounds} 轮  [T=${T.toFixed(3)}]`, 90) + '\n');

      for (const persona of activePersonas) {
        const pName = color(`${persona.icon} ${persona.name}`, persona.color);
        process.stdout.write(`  ${pName} 思考中...`);

        const dotTimer = setInterval(() => process.stdout.write(color('.', persona.color)), 150);

        let fullText = '';
        try {
          fullText = await askPersona(history, persona, topic, T, abortController.signal);
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
      const { deltaS, contributions } = await tracker.processRound(roundUtterances);
      scheduler.recordDeltaS(deltaS);

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
      roundStats.push({ round: round + 1, temp: T, deltaS, contributions, quality, status });

      // ─── 早停检查 ───────────────────────────────────
      if (round >= scheduler.config.minRoundsBeforeEarlyStop - 1 &&
          scheduler.getRoundsSinceLastSignificantDelta() > 3) {
        console.log(color('\n⚠ 讨论已收敛，提前结束', 33));
        break;
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
    if (mode === MODE_DEBATE) {
      await runVoting(topic, history, activePersonas, abortController.signal);
      summary = await generateSummary(topic, history, mode, abortController.signal);
    }

    // ─── 输出退火报告 ───────────────────────────────────
    const stats = scheduler.getStats();
    printAnnealingReport(topic, rounds, stats, roundStats);

    const filename = saveResult(topic, rounds, roundResponses.flat(), mode, summary, { ...scheduler.getStats(), roundStats });
    console.log(color(`💾 讨论记录已保存：${filename}`, 32));

  } catch (err) {
    console.error(color(`\n错误：${err.message}`, 31));
    process.exit(1);
  }
}

main();
