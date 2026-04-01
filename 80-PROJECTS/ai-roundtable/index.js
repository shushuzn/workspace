import 'dotenv/config';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ─── 配置 ───────────────────────────────────────────────
const API_KEY = process.env.MINIMAX_API_KEY;
const API_URL = 'https://api.minimaxi.com/v1/chat/completions';
const MODEL = process.env.MINIMAX_MODEL || 'MiniMax-M2.7-highspeed';
const DEFAULT_ROUNDS = 3;
const REQUEST_TIMEOUT_MS = 30_000;

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
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出自己的反对意见，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须指出一个具体的、真实存在的风险或问题。不要使用括号，不要说"我认为"，直接说质疑。`,
  },
  {
    id: 'analyst',
    name: '分析师',
    icon: '🔬',
    color: 32,
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出自己的数据分析，不能有任何内心独白或思考过程。说话要短，2句以内，必须包含一个真实的具体数字（如百分比、统计、年份、数量）。不要使用括号，不要说"根据数据"，直接说数字和分析结论。`,
  },
  {
    id: 'harmonizer',
    name: '调和者',
    icon: '🌱',
    color: 35,
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出综合方案，不能有任何内心独白或思考过程。说话要短，2句以内，结尾必须给出一个具体可操作的平衡做法。不要使用括号，不要铺垫，直接说方案。`,
  },
  {
    id: 'historian',
    name: '历史家',
    icon: '📜',
    color: 33,
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出历史类比，不能有任何内心独白或思考过程。说话要短，2句以内，必须引用一个真实的历史事件、时代或人物。不要使用括号，不要铺垫，直接说历史案例和教训。`,
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

function mergeSignals(...signals) {
  const controller = new AbortController();
  for (const s of signals) {
    if (s) s.addEventListener('abort', () => controller.abort(), { once: true });
  }
  return controller.signal;
}

// ─── 保存结果 ───────────────────────────────────────────
function saveResult(topic, rounds, transcript) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const safeTopic = topic.replace(/[\\/:*?"<>|]/g, '_').slice(0, 30);
  const filename = `讨论_${safeTopic}_${timestamp}.txt`;
  const filepath = path.join(__dirname, filename);

  const lines = [
    '═'.repeat(60),
    `  AI 圆桌讨论`,
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

  printBanner(topic, rounds);

  const abortController = new AbortController();
  const transcript = [];

  process.on('SIGINT', () => {
    console.log('\n\n已停止。');
    abortController.abort();
    process.exit(0);
  });

  const history = [{ role: 'user', content: `话题：${topic}` }];

  try {
    for (let round = 0; round < rounds; round++) {
      console.log(color(`📍 第 ${round + 1} / ${rounds} 轮`, 90) + '\n');

      for (const persona of personas) {
        const pName = color(`${persona.icon} ${persona.name}`, persona.color);
        process.stdout.write(`  ${pName} 思考中...`);

        const dotTimer = setInterval(() => {
          process.stdout.write(color('.', persona.color));
        }, 150);

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

  } catch (err) {
    console.error(color(`\n错误：${err.message}`, 31));
    process.exit(1);
  }
}

main();
