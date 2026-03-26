import 'dotenv/config';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { fetch, ProxyAgent } from 'undici';

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

// ─── 全局中止控制器 ──────────────────────────────────────────
let globalAbort = new AbortController();

// ─── MCP Server ───────────────────────────────────────────
const server = new Server(
  { name: 'ai-roundtable', version: '1.6.0' },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, () => ({
  tools: [
    {
      name: 'roundtable_discuss',
      description: '开始 AI 圆桌讨论。6种人格按顺序发言，后发言者能看到前面所有人的具体内容，形成真正的讨论。',
      inputSchema: {
        type: 'object',
        properties: {
          topic: { type: 'string', description: '讨论话题' },
          rounds: { type: 'number', description: '轮数，默认3轮', default: 3, minimum: 1, maximum: 10 },
        },
        required: ['topic'],
      },
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

  if (name === 'roundtable_stop') {
    globalAbort.abort();
    globalAbort = new AbortController();
    return { content: [{ type: 'text', text: '讨论已停止。' }] };
  }

  if (name === 'roundtable_discuss') {
    const topic = args?.topic as string;
    const rounds = Math.min(Math.max((args?.rounds as number) || 3, 1), 10);

    if (!topic?.trim()) {
      return { content: [{ type: 'text', text: '请提供讨论话题。' }], isError: true };
    }
    if (!API_KEY) {
      return { content: [{ type: 'text', text: '错误：未设置 MINIMAX_API_KEY' }], isError: true };
    }

    globalAbort.abort();
    globalAbort = new AbortController();
    const abortSignal = globalAbort.signal;

    // 发言链条：按时间顺序记录所有发言
    const chain: { persona: typeof personas[0]; text: string }[] = [];

    let output = `🔥 AI 圆桌讨论\n话题：${topic}\n轮数：${rounds}\n${'─'.repeat(50)}\n\n`;

    try {
      for (let round = 0; round < rounds; round++) {
        if (abortSignal.aborted) {
          return { content: [{ type: 'text', text: '讨论已中止。' }] };
        }

        output += `📍 第 ${round + 1} / ${rounds} 轮\n`;

        // 按顺序遍历每轮中的 6 个人格
        for (const persona of personas) {
          if (abortSignal.aborted) {
            return { content: [{ type: 'text', text: '讨论已中止。' }] };
          }

          // 构建之前所有发言的文本（链条历史）
          const priorStatements = chain.length > 0
            ? chain.map(e => `${e.persona.name}：${e.text}`).join('\n')
            : '（暂无）';

          // 完整的 system prompt
          const systemFull = `${persona.systemPrompt}\n\n重要：直接输出你的观点，不要使用括号、不要输出思考过程、不要输出引号、不要解释。只输出纯文本。`;

          // 用户消息 = 话题 + 链条历史
          const content = `话题：${topic}\n\n以下是之前的发言（按时间顺序）：\n${priorStatements}\n\n现在轮到 ${persona.name} 发言：`;

          try {
            const answer = await callMinimax(systemFull, content, abortSignal);
            chain.push({ persona, text: answer });
            output += `  ${persona.icon} ${persona.name}：${answer}\n`;
          } catch (err) {
            if (err instanceof Error && err.name === 'AbortError') {
              return { content: [{ type: 'text', text: '讨论已中止。' }] };
            }
            const errMsg = err instanceof Error ? err.message : String(err);
            chain.push({ persona, text: `⚠ ${errMsg}` });
            output += `  ${persona.icon} ${persona.name}：⚠ ${errMsg}\n`;
          }
        }

        output += '\n';
      }

      output += `${'─'.repeat(50)}\n✅ 讨论结束（共 ${rounds} 轮，共 ${chain.length} 条发言）`;
      return { content: [{ type: 'text', text: output }] };
    } catch (err) {
      return {
        content: [{
          type: 'text',
          text: `讨论出错：${err instanceof Error ? err.message : String(err)}`,
        }],
        isError: true,
      };
    }
  }

  return { content: [{ type: 'text', text: `未知工具：${name}` }], isError: true };
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('ai-roundtable MCP Server 已启动 (v1.6.0)', { mode: 'stdio' });
}

main().catch((err) => {
  console.error('启动失败:', err);
  process.exit(1);
});
