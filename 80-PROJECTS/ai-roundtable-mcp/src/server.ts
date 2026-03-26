import 'dotenv/config';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { fetch, ProxyAgent } from 'undici';
import fs from 'fs';
import os from 'os';
import path from 'path';

// ─── 配置 ───────────────────────────────────────────
const API_KEY = process.env.MINIMAX_API_KEY!;
const API_URL = 'https://api.minimaxi.com/v1/text/chatcompletion_v2';
const MODEL = 'MiniMax-M2.7-highspeed';
const proxyUrl = process.env.HTTPS_PROXY || process.env.https_proxy;

// ─── 人格定义 ───────────────────────────────────────────
const personas = [
  { id: 'optimist', name: '乐观者', icon: '🔥',
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出自己的观点，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须有一个你亲眼见过或读过的真实例子。不要使用括号，不要说"我认为""我觉得"，直接说观点。` },
  { id: 'skeptic', name: '怀疑者', icon: '🧊',
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出自己的质疑，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须指出一个具体的风险或漏洞。不要使用括号，不要铺垫，直接说质疑。` },
  { id: 'analyst', name: '分析师', icon: '🔬',
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出自己的分析，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须给出一个具体的数据或趋势。不要使用括号，不要铺垫，直接说分析。` },
  { id: 'harmonizer', name: '调和者', icon: '🌱',
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出自己的综合观点，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须给出一个平衡的结论。不要使用括号，不要铺垫，直接说观点。` },
  { id: 'historian', name: '历史家', icon: '📜',
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出自己的历史类比，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须引用一个真实的历史案例。不要使用括号，不要铺垫，直接说类比。` },
  { id: 'pragmatist', name: '务实者', icon: '⚙️',
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出可执行的下一步方案，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须列出一个具体的工具、步骤或操作。不要使用括号，不要铺垫，直接说执行方案。` },
];

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
      'Authorization': `Bearer ${API_KEY}`,
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
    const err = (await res.json().catch(() => ({}))) as { base_resp?: { status_msg?: string } };
    throw new Error(err.base_resp?.status_msg || `HTTP ${res.status}`);
  }

  const data = (await res.json()) as {
    choices?: { message?: { content?: string; reasoning_content?: string } }[];
  };

  const msg = data.choices?.[0]?.message;
  const text = (msg?.content?.trim() || msg?.reasoning_content?.trim() || '').trim();
  if (!text) return '(无有效回答)';
  return text;
}

// ─── chain 持久化 ───────────────────────────────────────
const CHAIN_FILE = path.join(os.tmpdir(), 'ai-roundtable-chain.json');

interface ChainEntry {
  persona: { id: string; name: string; icon: string };
  text: string;
  round: number;
  order: number;
}

interface ChainState {
  topic: string;
  totalRounds: number;
  chain: ChainEntry[];
  currentRound: number;
  currentOrder: number;
}

function readChain(): ChainState | null {
  try {
    if (!fs.existsSync(CHAIN_FILE)) return null;
    return JSON.parse(fs.readFileSync(CHAIN_FILE, 'utf8'));
  } catch { return null; }
}

function writeChain(state: ChainState): void {
  fs.writeFileSync(CHAIN_FILE, JSON.stringify(state, null, 2), 'utf8');
}

let globalAbort = new AbortController();

// ─── MCP Server ───────────────────────────────────────────
const server = new Server(
  { name: 'ai-roundtable', version: '2.0.0' },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, () => ({
  tools: [
    {
      name: 'roundtable_start',
      description: '开始圆桌讨论。传入话题和轮数，初始化链条并返回第一个人格的发言。',
      inputSchema: {
        type: 'object',
        properties: {
          topic: { type: 'string', description: '讨论话题' },
          rounds: { type: 'number', description: '轮数', default: 3, minimum: 1, maximum: 10 },
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
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  // ─── roundtable_stop ────────────────────────────────
  if (name === 'roundtable_stop') {
    globalAbort.abort();
    globalAbort = new AbortController();
    try { fs.unlinkSync(CHAIN_FILE); } catch {}
    return { content: [{ type: 'text', text: '讨论已停止。' }] };
  }

  // ─── roundtable_start ───────────────────────────
  if (name === 'roundtable_start') {
    const topic = (args as { topic?: string })?.topic || '';
    const rounds = Math.min(Math.max((args as { rounds?: number })?.rounds || 3, 1), 10);

    if (!topic.trim()) return { content: [{ type: 'text', text: '请提供讨论话题。' }], isError: true };
    if (!API_KEY) return { content: [{ type: 'text', text: '错误：未设置 MINIMAX_API_KEY' }], isError: true };

    globalAbort.abort();
    globalAbort = new AbortController();

    const chain: ChainEntry[] = [];
    const state: ChainState = { topic, totalRounds: rounds, chain, currentRound: 0, currentOrder: 0 };
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

    chain.push({ persona: { id: firstPersona.id, name: firstPersona.name, icon: firstPersona.icon }, text: answer, round: 0, order: 0 });
    state.currentOrder = 1;
    writeChain(state);

    return {
      content: [{ type: 'text', text: `🔥 AI 圆桌讨论\n话题：${topic}\n轮数：${rounds}\n${'─'.repeat(50)}\n\n📍 第 1 / ${rounds} 轮\n\n  ${firstPersona.icon} ${firstPersona.name}：${answer}` }]
    };
  }

  // ─── roundtable_next ─────────────────────────────
  if (name === 'roundtable_next') {
    const state = readChain();
    if (!state) return { content: [{ type: 'text', text: '无进行中的讨论，请先调用 roundtable_start。' }], isError: true };

    const { topic, totalRounds, chain, currentRound, currentOrder } = state;

    // 当前轮已结束，进入下一轮
    if (currentOrder >= personas.length) {
      const newRound = currentRound + 1;
      if (newRound >= totalRounds) {
        try { fs.unlinkSync(CHAIN_FILE); } catch {}
        return { content: [{ type: 'text', text: `${'─'.repeat(50)}\n✅ 讨论结束（共 ${totalRounds} 轮，共 ${chain.length} 条发言）` }] };
      }
      // 输出轮次分隔并立即执行第一个人格
      const roundHeader = `📍 第 ${newRound + 1} / ${totalRounds} 轮\n`;
      state.currentRound = newRound;
      state.currentOrder = 0;
      writeChain(state);

      const firstPersona = personas[0];
      const priorStatements = chain.map(e => `${e.persona.name}：${e.text}`).join('\n');
      const systemFull = `${firstPersona.systemPrompt}\n\n重要：直接输出你的观点，不要使用括号、不要输出思考过程、不要输出引号、不要解释。只输出纯文本。严格控制在2句话以内。`;
      const content = `话题：${topic}\n\n以下是之前的发言（按时间顺序）：\n${priorStatements}\n\n现在轮到 ${firstPersona.name} 发言：`;

      let answer: string;
      try {
        answer = await callMinimax(systemFull, content, globalAbort.signal);
      } catch (err) {
        answer = `⚠ ${err instanceof Error ? err.message : String(err)}`;
      }

      chain.push({ persona: { id: firstPersona.id, name: firstPersona.name, icon: firstPersona.icon }, text: answer, round: newRound, order: 0 });
      state.currentOrder = 1;
      writeChain(state);

      return { content: [{ type: 'text', text: `${roundHeader}\n  ${firstPersona.icon} ${firstPersona.name}：${answer}` }] };
    }

    // 获取下一个发言
    const nextPersona = personas[currentOrder];
    const priorStatements = chain.map(e => `${e.persona.name}：${e.text}`).join('\n');
    const systemFull = `${nextPersona.systemPrompt}\n\n重要：直接输出你的观点，不要使用括号、不要输出思考过程、不要输出引号、不要解释。只输出纯文本。严格控制在2句话以内。`;
    const content = `话题：${topic}\n\n以下是之前的发言（按时间顺序）：\n${priorStatements}\n\n现在轮到 ${nextPersona.name} 发言：`;

    let answer: string;
    try {
      answer = await callMinimax(systemFull, content, globalAbort.signal);
    } catch (err) {
      answer = `⚠ ${err instanceof Error ? err.message : String(err)}`;
    }

    chain.push({ persona: { id: nextPersona.id, name: nextPersona.name, icon: nextPersona.icon }, text: answer, round: currentRound, order: currentOrder });
    state.currentOrder++;
    writeChain(state);

    return { content: [{ type: 'text', text: `  ${nextPersona.icon} ${nextPersona.name}：${answer}` }] };
  }

  return { content: [{ type: 'text', text: `未知工具：${name}` }], isError: true };
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('ai-roundtable MCP Server 已启动 (v2.0.0)', { mode: 'stdio' });
}

main().catch((err) => {
  console.error('启动失败:', err);
  process.exit(1);
});
