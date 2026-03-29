import 'dotenv/config';
import { fetch, ProxyAgent } from 'undici';

const API_KEY = process.env.MINIMAX_API_KEY;
const API_URL = 'https://api.minimaxi.com/v1/text/chatcompletion_v2';
const proxyUrl = process.env.HTTPS_PROXY;
const dispatcher = proxyUrl ? new ProxyAgent(proxyUrl) : undefined;

function stripMarkdown(text) {
  return text
    .replace(/#{1,6}\s/g, '')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\*(.+?)\*/g, '$1')
    .replace(/\[(.+?)\]\(.+?\)/g, '$1')
    .replace(/[-*+]\s/g, '')
    .replace(/\d+\.\s/g, '')
    .replace(/^---+$/gm, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function truncateSentences(text, maxChars = 100) {
  if (text.length <= maxChars) return text;
  const sentences = text.match(/[^。！？.!?]+[。！？.!?]+/g) || [];
  let result = '';
  for (const s of sentences) {
    if ((result + s).length > maxChars) break;
    result += s;
  }
  return result.trim() || text.slice(0, maxChars);
}

async function test() {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
    },
    body: JSON.stringify({
      model: 'MiniMax-M2.7-highspeed',
      max_tokens: 800,
      temperature: 0.2,
      system: '你正在一个圆桌讨论现场。轮到你发言，立刻说2句观点，结尾要有一个真实例子。禁止括号，禁止Markdown，只输出纯文本。',
      messages: [{ role: 'user', content: '话题：AI是否会取代白领工作，轮到乐观者发言' }],
    }),
    dispatcher,
  });

  const data = await res.json();
  const msg = data.choices?.[0]?.message;
  const raw = (msg?.content?.trim() || msg?.reasoning_content?.trim() || '').trim();

  const plain = stripMarkdown(raw);
  const short80 = truncateSentences(plain, 80);
  const short120 = truncateSentences(plain, 120);

  console.log('=== 原始纯文本 (stripMarkdown后) ===');
  console.log(plain.slice(0, 200));
  console.log('');
  console.log('=== 截断到80字符 ===');
  console.log(short80);
  console.log('长度:', short80.length);
  console.log('');
  console.log('=== 截断到120字符 ===');
  console.log(short120);
  console.log('长度:', short120.length);
}

test().catch(e => { console.error('Error:', e.message); process.exit(1); });
