import 'dotenv/config';
import { HttpsProxyAgent } from 'https-proxy-agent';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Shared Memory integration
import { getSharedMemoryManager } from '../../.omc/patrol-agent/src/memory/sharedMemoryManager.js';
let sharedMemoryManager = null;

// A2A integration
import { getA2AClient } from '../../.omc/patrol-agent/src/a2a/a2aClient.js';
let a2aClient = null;

const API_KEY = process.env.MINIMAX_API_KEY;
const API_URL = 'https://api.minimaxi.com/v1/text/anthropic_api';
const MODEL = 'MiniMax-M2.7-highspeed';
const DEFAULT_ROUNDS = 3;

const proxyUrl = process.env.HTTPS_PROXY || process.env.https_proxy || process.env.HTTP_PROXY || process.env.http_proxy;
const agent = proxyUrl ? new HttpsProxyAgent(proxyUrl) : undefined;

// ─── Shared Memory Functions ────────────────────────────
async function initSharedMemory() {
  try {
    sharedMemoryManager = getSharedMemoryManager();
    const health = await sharedMemoryManager.healthCheck();
    if (health.healthy) {
      console.log('🌐 Shared Memory: Connected to OpenViking v' + health.version);
    } else {
      console.log('🌐 Shared Memory: Using local fallback');
    }
  } catch (error) {
    console.log('🌐 Shared Memory: Not available (' + error.message + ')');
  }
}

// ─── A2A Functions ─────────────────────────────────────
async function initA2A() {
  try {
    a2aClient = getA2AClient('ai-roundtable', [
      'discuss',
      'analyze',
      'decide',
      'consensus-building',
      'problem-solving'
    ]);
    
    // Register message handlers
    a2aClient.on('TASK', handleA2ATask);
    a2aClient.on('QUERY', handleA2AQuery);
    
    // Note: MCP caller needs to be set externally
    console.log('📡 A2A: Client initialized');
    return true;
  } catch (error) {
    console.log('📡 A2A: Initialization failed:', error.message);
    return false;
  }
}

async function handleA2ATask(message) {
  console.log(`📡 A2A: Received TASK from ${message.from}`);
  
  const { task, problemId, title, description, severity, context } = message.payload;
  
  if (task === 'discuss_problem') {
    console.log(`📡 A2A: Running discussion on "${title}"`);
    
    // Run the roundtable discussion
    const result = await runDiscussion(title, 3);
    
    // Send result back
    await a2aClient.send({
      type: 'TASK_RESULT',
      to: message.from,
      priority: 'NORMAL',
      payload: {
        taskId: message.id,
        success: true,
        consensus: result.consensus,
        confidence: result.confidence,
        steps: result.steps,
        discussionId: result.discussionId
      },
      metadata: {
        correlationId: message.metadata?.correlationId
      }
    });
    
    // Store decision in shared memory
    if (sharedMemoryManager) {
      await storeDecision({
        title: `Consensus: ${title}`,
        consensus: result.consensus,
        confidence: result.confidence,
        sourceAgent: message.from,
        problemId,
        tags: ['a2a', 'roundtable', 'consensus']
      });
    }
    
    console.log(`📡 A2A: Sent result back to ${message.from}`);
  }
}

async function handleA2AQuery(message) {
  console.log(`📡 A2A: Received QUERY from ${message.from}`);
  
  const { query } = message.payload;
  
  if (query === 'capabilities') {
    await a2aClient.send({
      type: 'RESPONSE',
      to: message.from,
      priority: 'NORMAL',
      payload: {
        agentId: 'ai-roundtable',
        capabilities: [
          'discuss',
          'analyze',
          'decide',
          'consensus-building',
          'problem-solving'
        ],
        status: 'idle',
        load: 0
      },
      metadata: {
        correlationId: message.metadata?.correlationId
      }
    });
  }
}

async function loadSharedProblems(limit = 5) {
  if (!sharedMemoryManager) return [];
  
  try {
    const result = await sharedMemoryManager.retrieveSharedMemories('problem', { limit });
    if (result.success && result.memories.length > 0) {
      return result.memories.map(m => ({
        type: m.type || 'problem',
        content: m.content || m.abstract || 'No content',
        source: m.metadata?.sourceAgent || 'unknown'
      }));
    }
    return [];
  } catch (error) {
    console.error('Failed to load shared problems:', error.message);
    return [];
  }
}

async function storeSharedDecision(decision, relatedProblems = []) {
  if (!sharedMemoryManager) return { success: false };
  
  try {
    const result = await sharedMemoryManager.storeSharedMemory('decision', {
      title: decision.title || 'Roundtable Decision',
      description: decision.description || '',
      consensus: decision.consensus || '',
      recommendations: decision.recommendations || [],
      timestamp: Date.now()
    }, {
      sourceAgent: 'ai-roundtable',
      tags: ['decision', 'roundtable', 'consensus'],
      relatedTo: relatedProblems.length > 0 ? relatedProblems[0] : null
    });
    
    if (result.success) {
      console.log('🌐 Shared: Decision recorded -> ' + result.memoryId);
    }
    return result;
  } catch (error) {
    console.error('Failed to store shared decision:', error.message);
    return { success: false, error: error.message };
  }
}

// ─── 人格定义 ───────────────────────────────────────────
const personas = [
  {
    id: 'optimist',
    name: '乐观者',
    icon: '🔥',
    color: 31,
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出自己的观点，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须有一个你亲眼见过或读过的真实例子。不要使用括号，不要说"我认为""我觉得"，直接说观点。`,
  },
  {
    id: 'skeptic',
    name: '怀疑者',
    icon: '🧊',
    color: 34,
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出自己的质疑，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须指出一个具体的风险或漏洞。不要使用括号，不要铺垫，直接说质疑。`,
  },
  {
    id: 'analyst',
    name: '分析师',
    icon: '🔬',
    color: 32,
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出自己的分析，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须给出一个具体的数据或趋势。不要使用括号，不要铺垫，直接说分析。`,
  },
  {
    id: 'harmonizer',
    name: '调和者',
    icon: '🌱',
    color: 35,
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出自己的综合观点，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须给出一个平衡的结论。不要使用括号，不要铺垫，直接说观点。`,
  },
  {
    id: 'historian',
    name: '历史家',
    icon: '📜',
    color: 33,
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出自己的历史类比，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须引用一个真实的历史案例。不要使用括号，不要铺垫，直接说类比。`,
  },
  {
    id: 'pragmatist',
    name: '务实者',
    icon: '⚙️',
    color: 36,
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出可执行的下一步方案，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须列出一个具体的工具、步骤或操作。不要使用括号，不要铺垫，直接说执行方案。`,
  },
];

// ─── 工具函数 ───────────────────────────────────────────
function color(text, code) {
  return `\x1b[${code}m${text}\x1b[0m`;
}

function c(name, text) {
  const p = personas.find(x => x.id === name);
  return p ? color(`${p.icon} ${p.name}`, p.color) : text;
}

// ─── 清理回答 ─────────────────────────────────────────
function cleanResponse(text) {
  text = text.replace(/\*/g, '');
  text = text.replace(/<think>.*?</think>/gs, '');
  text = text.replace(/<think>.*$/gs, '');
  const sentences = text
    .split(/[。\！？\n]/)
    .map(s => s.trim())
    .filter(s => {
      if (s.length < 4) return false;
      if (/^['"'']$/.test(s)) return false;
      return true;
    })
    .slice(0, 2);
  text = sentences.join('。').trim();
  if (!text) return '(无有效回答)';
  if (!/[。！？]$/.test(text)) text += '。';
  return text;
}

// ─── 调用 ───────────────────────────────────────────
async function askPersona(messages, persona, topic, abortSignal) {
  const systemPrompt = `${persona.systemPrompt}\n\n重要：直接输出你的观点，不要使用括号、不要输出思考过程、不要输出引号、不要解释。只输出纯文本。`;

  const res = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: 800,
      temperature: 0.2,
      stream: false,
      thinking: { type: 'disabled' },
      system: systemPrompt,
      messages: messages
        .filter(m => m.role !== 'system')
        .map(m => ({ role: m.role, content: m.content })),
    }),
    signal: abortSignal,
    agent,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error?.message || `HTTP ${res.status}`);
  }

  const data = await res.json();

  // 从 Anthropic 格式提取文本
  let text = '';
  if (data.content && Array.isArray(data.content)) {
    for (const block of data.content) {
      if (block.type === 'text') {
        text += block.text;
      }
      // 忽略 thinking 块（已禁用，但以防万一）
    }
  }

  return cleanResponse(text || data.choices?.[0]?.message?.content || '');
}

// ─── 保存结果 ───────────────────────────────────────────
function saveResult(topic, rounds, transcript) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const safeTopic = topic.replace(/[\\/:*?"<>|]/g, '_').slice(0, 30);
  const filename = `讨论_${safeTopic}_${timestamp}.txt`;
  const filepath = path.join(__dirname, filename);

  const lines = [
    '═'.repeat(60),
    '  AI 圆桌讨论',
    '═'.repeat(60),
    `话题：${topic}`,
    `轮数：${rounds}`,
    `时间：${new Date().toLocaleString('zh-CN')}`,
    '─'.repeat(60),
    '',
    ...transcript.map(e => `${e.persona.icon} ${e.persona.name}：${e.text}`),
    '',
    '─'.repeat(60),
    `共 ${transcript.length} 条发言`,
  ];

  fs.writeFileSync(filepath, lines.join('\n'), 'utf8');
  return filename;
}

// ─── 打印函数 ───────────────────────────────────────────
function printBanner(topic, rounds) {
  console.log('\n' + color('═'.repeat(60), 1));
  console.log(color('  🔥 AI 圆桌讨论', 1));
  console.log(color('═'.repeat(60), 1));
  console.log(`  话题：${topic}`);
  console.log(`  人格：${personas.length} 位`);
  console.log(`  轮次：${rounds} 轮\n`);
}

function printDivider() {
  console.log(color('─'.repeat(60), 90));
}

// ─── 参数解析 ───────────────────────────────────────────
function parseArgs(argv) {
  const args = argv.slice(2);
  let topic = '';
  let rounds = DEFAULT_ROUNDS;

  for (let i = 0; i < args.length; i++) {
    if ((args[i] === '-r' || args[i] === '--rounds') && args[i + 1]) {
      const n = parseInt(args[i + 1], 10);
      if (!isNaN(n) && n > 0) rounds = Math.min(n, 10);
      i++;
    } else if (args[i].startsWith('-')) {
      // ignore unknown flags
    } else {
      topic = args[i];
    }
  }

  return { topic, rounds };
}

// ─── 主函数 ───────────────────────────────────────────
async function main() {
  // Initialize shared memory
  await initSharedMemory();
  
  // Initialize A2A
  await initA2A();
  
  const { topic: argTopic, rounds } = parseArgs(process.argv);
  let topic = argTopic;

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

  if (!API_KEY) {
    console.error(color('错误：未设置 MINIMAX_API_KEY', 31));
    console.error('请在 .env 文件中设置：MINIMAX_API_KEY=你的密钥');
    process.exit(1);
  }

  // Check for shared problems related to topic
  const sharedProblems = await loadSharedProblems(3);
  if (sharedProblems.length > 0) {
    console.log(color(`\n📚 发现 ${sharedProblems.length} 个相关问题来自 Patrol Agent:`, 90));
    sharedProblems.forEach((p, i) => {
      console.log(color(`   ${i + 1}. ${p.content.title || p.content.description || 'Unknown'}`, 90));
    });
    console.log();
  }

  printBanner(topic, rounds);

  const abortController = new AbortController();

  process.on('SIGINT', () => {
    console.log('\n\n已停止。');
    abortController.abort();
    process.exit(0);
  });

  const history = [{ role: 'user', content: `话题：${topic}` }];
  const transcript = [];

  try {
    for (let round = 0; round < rounds; round++) {
      console.log(color(`📍 第 ${round + 1} / ${rounds} 轮`, 90) + '\n');

      for (const persona of personas) {
        const pName = color(`${persona.icon} ${persona.name}`, persona.color);
        process.stdout.write(`  ${pName} 思考中...`);

        let dotCount = 0;
        const dotTimer = setInterval(() => {
          dotCount++;
          process.stdout.write(color('.', persona.color));
        }, 150);

        let fullText = '';
        try {
          fullText = await askPersona(history, persona, topic, abortController.signal);
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

        transcript.push({ persona, text: fullText });
        history.push({ role: 'assistant', content: fullText });
      }

      if (round < rounds - 1) {
        printDivider();
        history.push({
          role: 'user',
          content: `第 ${round + 2} 轮：请继续讨论，从另一角度深入。`,
        });
      }
    }

    printDivider();
    console.log(color('\n✅ 讨论结束\n', 32));

    const filename = saveResult(topic, rounds, transcript);
    console.log(color(`💾 讨论记录已保存：${filename}`, 32));

    // Store decision in shared memory
    const decision = {
      title: `Roundtable Discussion: ${topic}`,
      description: `Multi-persona discussion on "${topic}" with ${personas.length} participants over ${rounds} rounds`,
      consensus: extractConsensus(transcript),
      recommendations: extractRecommendations(transcript)
    };
    
    const relatedProblems = sharedProblems.map(p => p.memoryId).filter(Boolean);
    await storeSharedDecision(decision, relatedProblems);

  } catch (err) {
    console.error(color(`\n错误：${err.message}`, 31));
    process.exit(1);
  }
}

// Helper functions for decision extraction
function extractConsensus(transcript) {
  // Simple extraction - in production, use LLM to summarize
  const keyPoints = transcript
    .filter(t => t.text.includes('应该') || t.text.includes('需要') || t.text.includes('必须'))
    .map(t => t.text)
    .slice(0, 3);
  return keyPoints.join('; ') || 'No clear consensus reached';
}

function extractRecommendations(transcript) {
  // Extract actionable items
  return transcript
    .filter(t => t.text.includes('建议') || t.text.includes('可以') || t.text.includes('试试'))
    .map(t => ({
      from: t.persona.name,
      recommendation: t.text.slice(0, 100) + (t.text.length > 100 ? '...' : '')
    }))
    .slice(0, 5);
}

main();
