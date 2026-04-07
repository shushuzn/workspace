import 'dotenv/config';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { fetch, ProxyAgent } from 'undici';
import { personas } from './shared/personas.js';
import {
  readChain,
  writeChain,
  clearChain,
  type ChainState,
  type ChainEntry,
} from './shared/chainState.js';
import {
  getLatestNews,
  analyzeSentiment,
  searchNews,
  getTrendingTopics,
  getStockNews,
} from './shared/adapters/newshub.js';

// ─── Signal Subscription System ─────────────────────────

type SignalFilter = {
  event?: string;       // e.g. 'debate.complete', 'news.fetch', 'code.analyze'
  topic?: string;       // match topic containing string (case-insensitive)
  minQualityScore?: number; // fire only if quality score >= threshold
};

interface Subscription {
  id: string;
  filter: SignalFilter;
  callback: (event: SignalEvent) => void;
  createdAt: number;
}

interface SignalEvent {
  type: string;         // 'debate.complete' | 'news.fetch' | 'code.analyze' | 'debate.round'
  timestamp: number;
  topic?: string;
  data: unknown;
  qualityScore?: number;
}

const subscriptions = new Map<string, Subscription>();
let subIdCounter = 0;

function emitSignal(event: SignalEvent): void {
  for (const sub of subscriptions.values()) {
    const f = sub.filter;
    if (f.event && f.event !== event.type) continue;
    if (f.topic && !(event.topic?.toLowerCase().includes(f.topic.toLowerCase()) ?? false)) continue;
    if (f.minQualityScore !== undefined && (event.qualityScore === undefined || event.qualityScore < f.minQualityScore)) continue;
    try { sub.callback(event); } catch { /* ignore callback errors */ }
  }
}

// ─── Cognitive Load Balancer ──────────────────────────

/**
 * TaskType → capability mapping
 * keyword matching routes prompts to the most appropriate agent
 */
const TASK_KEYWORDS: Record<string, { type: TaskType; keywords: string[] }> = {
  debate: {
    type: 'debate',
    keywords: ['讨论', '辩论', '争议', '观点', '争论', '看法', '圆桌', '座谈', '大家觉得', '你怎么看', '哪个更好'],
  },
  news: {
    type: 'news',
    keywords: ['新闻', '最新', '资讯', '市场', '行情', '大盘', '涨跌', '财经', '宏观', '行业', '公司', '股票'],
  },
  code: {
    type: 'code',
    keywords: ['代码', '编程', '函数', 'bug', '重构', '优化', '实现', '接口', '算法', '测试', 'debug'],
  },
};

type TaskType = 'debate' | 'news' | 'code' | 'unknown';

/**
 * Keyword-based simple router: maps natural language to best-fit agent
 */
function routePrompt(prompt: string): { type: TaskType; confidence: number; reason: string } {
  const lower = prompt.toLowerCase();
  const scores: Record<TaskType, number> = { debate: 0, news: 0, code: 0, unknown: 0 };

  for (const [type, cfg] of Object.entries(TASK_KEYWORDS)) {
    for (const kw of cfg.keywords) {
      if (lower.includes(kw)) scores[type as TaskType] += 1;
    }
  }

  // Find highest scoring type
  let bestType: TaskType = 'unknown';
  let bestScore = 0;
  for (const [type, score] of Object.entries(scores)) {
    if (score > bestScore) { bestScore = score; bestType = type as TaskType; }
  }

  if (bestType === 'unknown') {
    return { type: 'unknown', confidence: 0, reason: '无匹配关键词，默认news' };
  }

  const reasons: Record<TaskType, string> = {
    debate: `命中讨论/辩论类关键词（得分${bestScore}）`,
    news: `命中财经/新闻类关键词（得分${bestScore}）`,
    code: `命中编程/代码类关键词（得分${bestScore}）`,
    unknown: '',
  };

  return { type: bestType, confidence: bestScore / 5, reason: reasons[bestType] };
}

// ─── 配置 ───────────────────────────────────────────
const API_KEY = process.env.MINIMAX_API_KEY!;
const API_URL = 'https://api.minimaxi.com/v1/text/chatcompletion_v2';
const MODEL = 'MiniMax-M2.7-highspeed';
const proxyUrl = process.env.HTTPS_PROXY || process.env.https_proxy;

// ─── MiniMax 调用（正确参数）────────────────────────────────
async function callMinimax(
  systemPrompt: string,
  content: string,
  signal?: AbortSignal
): Promise<string> {
  const dispatcher = proxyUrl ? new ProxyAgent(proxyUrl) : undefined;

  const res = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${API_KEY}`,
    },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: 800,
      temperature: 0.2,
      system: systemPrompt,
      messages: [{ role: 'user', content }],
    }),
    signal,
    dispatcher,
  });

  if (!res.ok) {
    const err = (await res.json().catch(() => ({}))) as {
      base_resp?: { status_msg?: string };
    };
    throw new Error(err.base_resp?.status_msg || `HTTP ${res.status}`);
  }

  const data = (await res.json()) as {
    choices?: { message?: { content?: string; reasoning_content?: string } }[];
  };

  const msg = data.choices?.[0]?.message;
  const text = (
    msg?.content?.trim() ||
    msg?.reasoning_content?.trim() ||
    ''
  ).trim();
  if (!text) return '(无有效回答)';
  return text;
}

let globalAbort = new AbortController();

// ─── MCP Server ───────────────────────────────────────────
const server = new Server(
  { name: 'ai-roundtable', version: '2.0.0' },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, () => ({
  tools: [
    // ─── 圆桌讨论工具 ───────────────────────────────
    {
      name: 'roundtable_start',
      description:
        '开始圆桌讨论。传入话题和轮数，初始化链条并返回第一个人格的发言。',
      inputSchema: {
        type: 'object',
        properties: {
          topic: { type: 'string', description: '讨论话题' },
          rounds: {
            type: 'number',
            description: '轮数',
            default: 3,
            minimum: 1,
            maximum: 10,
          },
        },
        required: ['topic'],
      },
    },
    {
      name: 'roundtable_next',
      description: '获取下一个发言。每次调用返回一条发言内容。',
      inputSchema: { type: 'object', properties: {} },
    },
    {
      name: 'roundtable_stop',
      description: '强制停止当前讨论',
      inputSchema: { type: 'object', properties: {} },
    },
    // ─── 财经新闻工具 ───────────────────────────────
    {
      name: 'news_get_latest',
      description: '获取最新财经新闻，支持多源聚合、分类筛选',
      inputSchema: {
        type: 'object',
        properties: {
          sources: {
            type: 'array',
            items: { type: 'string' },
            description: '新闻源: sina, ifeng, eastmoney, caixin, reuters',
          },
          categories: {
            type: 'array',
            items: { type: 'string' },
            description: '分类: macro, tech, industry, finance, international',
          },
          maxItems: {
            type: 'number',
            default: 50,
            description: '最大返回条数',
          },
        },
      },
    },
    {
      name: 'news_sentiment',
      description: '分析新闻情绪，判断市场情绪走向',
      inputSchema: {
        type: 'object',
        properties: {
          market: {
            type: 'string',
            enum: ['a-share', 'hk', 'us', 'crypto'],
            default: 'a-share',
          },
        },
      },
    },
    {
      name: 'news_search',
      description: '搜索特定主题的新闻',
      inputSchema: {
        type: 'object',
        properties: {
          query: { type: 'string', description: '搜索关键词' },
          stocks: {
            type: 'array',
            items: { type: 'string' },
            description: '关联股票代码',
          },
        },
      },
    },
    {
      name: 'news_trending',
      description: '获取当前热门话题',
      inputSchema: {
        type: 'object',
        properties: {
          limit: { type: 'number', default: 10 },
        },
      },
    },
    {
      name: 'news_stock',
      description: '获取特定股票的新闻',
      inputSchema: {
        type: 'object',
        properties: {
          stockCode: { type: 'string', description: '股票代码，如 600519' },
          stockName: { type: 'string', description: '股票名称' },
          days: { type: 'number', default: 7 },
        },
      },
    },
    // ─── Cognitive Load Balancer ───────────────────────
    {
      name: 'hub_dispatch',
      description: '自然语言分发器：分析任务类型，自动路由到最适agent并聚合结果。输入任意自然语言任务，返回路由决策和执行结果。',
      inputSchema: {
        type: 'object',
        properties: {
          prompt: { type: 'string', description: '自然语言任务描述，如"帮我分析一下茅台最近的新闻"或"讨论一下AI的未来"' },
        },
        required: ['prompt'],
      },
    },
    // ─── Signal Subscription ───────────────────────────
    {
      name: 'signal_subscribe',
      description: '订阅hub事件信号。当指定类型的事件发生时，返回事件内容。支持按topic过滤、按质量分数阈值触发。',
      inputSchema: {
        type: 'object',
        properties: {
          event: {
            type: 'string',
            enum: ['debate.complete', 'debate.round', 'news.fetch', 'news.sentiment', 'code.analyze', 'hub.dispatch'],
            description: '事件类型',
          },
          topic: {
            type: 'string',
            description: '按话题关键词过滤（可选，不区分大小写）',
          },
          minQualityScore: {
            type: 'number',
            description: '最低质量分数阈值（0-100），仅当分数>=阈值时触发',
          },
        },
      },
    },
    {
      name: 'signal_list',
      description: '查询当前已订阅的信号列表，返回所有活跃订阅',
      inputSchema: { type: 'object', properties: {} },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async request => {
  const { name, arguments: args } = request.params;

  // ─── roundtable_stop ────────────────────────────────
  if (name === 'roundtable_stop') {
    globalAbort.abort();
    globalAbort = new AbortController();
    clearChain();
    return { content: [{ type: 'text', text: '讨论已停止。' }] };
  }

  // ─── roundtable_start ───────────────────────────
  if (name === 'roundtable_start') {
    const topic = (args as { topic?: string })?.topic || '';
    const rounds = Math.min(
      Math.max((args as { rounds?: number })?.rounds || 3, 1),
      10
    );

    if (!topic.trim())
      return {
        content: [{ type: 'text', text: '请提供讨论话题。' }],
        isError: true,
      };
    if (!API_KEY)
      return {
        content: [{ type: 'text', text: '错误：未设置 MINIMAX_API_KEY' }],
        isError: true,
      };

    globalAbort.abort();
    globalAbort = new AbortController();

    const chain: ChainEntry[] = [];
    const state: ChainState = {
      topic,
      totalRounds: rounds,
      chain,
      currentRound: 0,
      currentOrder: 0,
    };
    writeChain(state);

    const firstPersona = personas[0];
    const systemFull = `${firstPersona.systemPrompt}\n\n重要：直接输出你的观点，不要使用括号、不要输出思考过程、不要输出引号、不要解释。只输出纯文本。严格控制在2句话以内。`;
    const content = `话题：${topic}\n\n以下是之前的发言（按时间顺序）：\n（暂无）\n\n现在轮到 ${firstPersona.name} 发言：`;

    let answer: string;
    try {
      answer = await callMinimax(systemFull, content, globalAbort.signal);
    } catch (err) {
      answer = `⚠ ${err instanceof Error ? err.message : String(err)}`;
    }

    chain.push({
      persona: {
        id: firstPersona.id,
        name: firstPersona.name,
        icon: firstPersona.icon,
      },
      text: answer,
      round: 0,
      order: 0,
    });
    state.currentOrder = 1;
    writeChain(state);

    return {
      content: [
        {
          type: 'text',
          text: `🔥 AI 圆桌讨论\n话题：${topic}\n轮数：${rounds}\n${'─'.repeat(50)}\n\n📍 第 1 / ${rounds} 轮\n\n  ${firstPersona.icon} ${firstPersona.name}：${answer}`,
        },
      ],
    };
  }

  // ─── roundtable_next ─────────────────────────────
  if (name === 'roundtable_next') {
    const state = readChain();
    if (!state)
      return {
        content: [
          { type: 'text', text: '无进行中的讨论，请先调用 roundtable_start。' },
        ],
        isError: true,
      };

    const { topic, totalRounds, chain, currentRound, currentOrder } = state;

    // 当前轮已结束，进入下一轮
    if (currentOrder >= personas.length) {
      const newRound = currentRound + 1;
      if (newRound >= totalRounds) {
        emitSignal({ type: 'debate.complete', timestamp: Date.now(), topic, data: chain.length });
        clearChain();
        return {
          content: [
            {
              type: 'text',
              text: `${'─'.repeat(50)}\n✅ 讨论结束（共 ${totalRounds} 轮，共 ${chain.length} 条发言）`,
            },
          ],
        };
      }
      const roundHeader = `📍 第 ${newRound + 1} / ${totalRounds} 轮\n`;
      emitSignal({ type: 'debate.round', timestamp: Date.now(), topic, data: { round: newRound, totalRounds } });
      state.currentRound = newRound;
      state.currentOrder = 0;
      writeChain(state);

      const firstPersona = personas[0];
      const priorStatements = chain
        .map(e => `${e.persona.name}：${e.text}`)
        .join('\n');
      const systemFull = `${firstPersona.systemPrompt}\n\n重要：直接输出你的观点，不要使用括号、不要输出思考过程、不要输出引号、不要解释。只输出纯文本。严格控制在2句话以内。`;
      const content = `话题：${topic}\n\n以下是之前的发言（按时间顺序）：\n${priorStatements}\n\n现在轮到 ${firstPersona.name} 发言：`;

      let answer: string;
      try {
        answer = await callMinimax(systemFull, content, globalAbort.signal);
      } catch (err) {
        answer = `⚠ ${err instanceof Error ? err.message : String(err)}`;
      }

      chain.push({
        persona: {
          id: firstPersona.id,
          name: firstPersona.name,
          icon: firstPersona.icon,
        },
        text: answer,
        round: newRound,
        order: 0,
      });
      state.currentOrder = 1;
      writeChain(state);

      return {
        content: [
          {
            type: 'text',
            text: `${roundHeader}\n  ${firstPersona.icon} ${firstPersona.name}：${answer}`,
          },
        ],
      };
    }

    // 获取下一个发言
    const nextPersona = personas[currentOrder];
    const priorStatements = chain
      .map(e => `${e.persona.name}：${e.text}`)
      .join('\n');
    const systemFull = `${nextPersona.systemPrompt}\n\n重要：直接输出你的观点，不要使用括号、不要输出思考过程、不要输出引号、不要解释。只输出纯文本。严格控制在2句话以内。`;
    const content = `话题：${topic}\n\n以下是之前的发言（按时间顺序）：\n${priorStatements}\n\n现在轮到 ${nextPersona.name} 发言：`;

    let answer: string;
    try {
      answer = await callMinimax(systemFull, content, globalAbort.signal);
    } catch (err) {
      answer = `⚠ ${err instanceof Error ? err.message : String(err)}`;
    }

    chain.push({
      persona: {
        id: nextPersona.id,
        name: nextPersona.name,
        icon: nextPersona.icon,
      },
      text: answer,
      round: currentRound,
      order: currentOrder,
    });
    state.currentOrder++;
    writeChain(state);

    return {
      content: [
        {
          type: 'text',
          text: `  ${nextPersona.icon} ${nextPersona.name}：${answer}`,
        },
      ],
    };
  }

  // ─── 新闻工具 ───────────────────────────────
  emitSignal({ type: 'news.fetch', timestamp: Date.now(), data: name });
  if (name === 'news_get_latest') {
    const a = args as {
      sources?: string[];
      categories?: string[];
      maxItems?: number;
    };
    const result = getLatestNews({
      sources: a.sources,
      categories: a.categories,
      maxItems: a.maxItems,
    });
    return {
      content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
    };
  }

  if (name === 'news_sentiment') {
    const a = args as { market?: string };
    const result = analyzeSentiment(undefined, a.market);
    return {
      content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
    };
  }

  if (name === 'news_search') {
    const a = args as { query?: string; stocks?: string[] };
    const result = searchNews(a.query || '', a.stocks);
    return {
      content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
    };
  }

  if (name === 'news_trending') {
    const a = args as { limit?: number };
    const result = getTrendingTopics(a.limit);
    return {
      content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
    };
  }

  if (name === 'news_stock') {
    const a = args as { stockCode?: string; stockName?: string; days?: number };
    const result = getStockNews(a.stockCode || '', a.stockName, a.days);
    return {
      content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
    };
  }

  // ─── Signal Subscription ───────────────────────────
  if (name === 'signal_subscribe') {
    const a = args as { event?: string; topic?: string; minQualityScore?: number };
    const id = `sub_${++subIdCounter}`;
    const filter: SignalFilter = {};
    if (a.event) filter.event = a.event;
    if (a.topic) filter.topic = a.topic;
    if (a.minQualityScore !== undefined) filter.minQualityScore = a.minQualityScore;
    subscriptions.set(id, {
      id,
      filter,
      callback: (event: SignalEvent) => {
        // result stored in subscriptions map — caller polls via signal_list
      },
      createdAt: Date.now(),
    });
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({ ok: true, subscriptionId: id, filter }, null, 2),
      }],
    };
  }

  if (name === 'signal_list') {
    const list = Array.from(subscriptions.values()).map(s => ({
      id: s.id,
      filter: s.filter,
      age: Date.now() - s.createdAt,
    }));
    return { content: [{ type: 'text', text: JSON.stringify(list, null, 2) }] };
  }

  // ─── hub_dispatch ─────────────────────────────────
  if (name === 'hub_dispatch') {
    const { prompt } = (args as { prompt?: string }) || {};
    if (!prompt?.trim()) {
      return { content: [{ type: 'text', text: '请提供任务描述。' }], isError: true };
    }

    const routing = routePrompt(prompt);

    if (routing.type === 'debate') {
      emitSignal({ type: 'hub.dispatch', timestamp: Date.now(), topic: prompt, data: { type: 'debate' } });
      // Auto-start a 3-round debate
      globalAbort.abort();
      globalAbort = new AbortController();
      const chain: ChainEntry[] = [];
      const state: ChainState = { topic: prompt, totalRounds: 3, chain, currentRound: 0, currentOrder: 0 };
      writeChain(state);
      const firstPersona = personas[0];
      const systemFull = `${firstPersona.systemPrompt}\n\n重要：直接输出你的观点，不要使用括号、不要输出思考过程、不要输出引号、不要解释。只输出纯文本。严格控制在2句话以内。`;
      const content = `话题：${prompt}\n\n以下是之前的发言（按时间顺序）：\n（暂无）\n\n现在轮到 ${firstPersona.name} 发言：`;
      let answer = '';
      try { answer = await callMinimax(systemFull, content, globalAbort.signal); } catch (e) { answer = `⚠ ${e instanceof Error ? e.message : String(e)}`; }
      chain.push({ persona: { id: firstPersona.id, name: firstPersona.name, icon: firstPersona.icon }, text: answer, round: 0, order: 0 });
      state.currentOrder = 1;
      writeChain(state);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ router: routing, agent: 'TournamentAgent', result: `${firstPersona.icon} ${firstPersona.name}：${answer}` }, null, 2),
        }],
      };
    }

    if (routing.type === 'news') {
      const result = getLatestNews({ maxItems: 5 });
      emitSignal({ type: 'hub.dispatch', timestamp: Date.now(), topic: prompt, data: { type: 'news' } });
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ router: routing, agent: 'NewsAdapter', result }, null, 2),
        }],
      };
    }

    if (routing.type === 'code') {
      emitSignal({ type: 'hub.dispatch', timestamp: Date.now(), topic: prompt, data: { type: 'code' } });
      // Code routing: return a stub hint (CodeAgent not yet integrated)
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ router: routing, agent: 'CodeAgent', result: 'CodeAgent 路由已配置，集成待完成。当前支持：代码分析、bug定位、重构建议。' }, null, 2),
        }],
      };
    }

    // Fallback: news
    const result = getLatestNews({ maxItems: 5 });
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({ router: routing, agent: 'NewsAdapter (fallback)', result }, null, 2),
      }],
    };
  }

  return {
    content: [{ type: 'text', text: `未知工具：${name}` }],
    isError: true,
  };
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('ai-roundtable MCP Server 已启动 (v2.0.0)', { mode: 'stdio' });
}

main().catch(err => {
  console.error('启动失败:', err);
  process.exit(1);
});
