/**
 * analyze.mjs — Multi-modal Content Analysis Pipeline
 *
 * Usage:
 *   node analyze.mjs <url-or-path> [--output DIR]
 *
 * Supported:
 *   - News/Article URLs (webpage)
 *   - PDF files (local path)
 *   - Video URLs (B站, YouTube)
 *
 * Output: Markdown file in docs/analysis/
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import { join, basename, extname } from 'path';
import { fileURLToPath } from 'url';

// ── Config ───────────────────────────────────────────────────────────────────

const OUTPUT_DIR = join(fileURLToPath(import.meta.url), '..');
const OLLAMA_URL = 'http://127.0.0.1:11434/api/chat';
const MODEL = 'llama3.2:1b';

// ── arXiv API ───────────────────────────────────────────────────────────────

async function arxivLookup(url) {
  const idMatch = url.match(/arxiv\.org\/(?:abs|pdf)\/(\d+\.\d+)/);
  if (!idMatch) return null;
  const id = idMatch[1];
  try {
    const res = await fetch(`http://export.arxiv.org/api/query?id_list=${id}&max_results=1`, { signal: AbortSignal.timeout(15000) });
    const xml = await res.text();
    const entryMatch = xml.match(/<entry>([\s\S]*?)<\/entry>/);
    if (!entryMatch) return null;
    const entry = entryMatch[1];
    const get = (tag) => {
      const m = entry.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`));
      return m ? m[1].replace(/\s+/g, ' ').trim() : '';
    };
    const title = get('title');
    const abstract = get('summary');
    const authors = [...entry.matchAll(/<author>[\s\S]*?<name>([^<]+)<\/name>[\s\S]*?<\/author>/g)].map(m => m[1]);
    const subjects = [...entry.matchAll(/<category term="([^"]+)"/g)].map(m => m[1]);
    return { title, abstract, authors, subjects };
  } catch { return null; }
}

// ── URL Type Detection ────────────────────────────────────────────────────────

function detectType(input) {
  if (input.startsWith('http')) {
    if (input.includes('bilibili.com') || input.includes('youtube.com')) return 'video';
    if (input.includes('.pdf')) return 'pdf-url';
    if (/\/abs\/\d+\.\d+/.test(input)) return 'arxiv';
    return 'webpage';
  }
  if (existsSync(input) && input.endsWith('.pdf')) return 'pdf-file';
  return 'unknown';
}

// ── Webpage Extraction ───────────────────────────────────────────────────────

async function extractWebpage(url) {
  try {
    const res = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0' },
      signal: AbortSignal.timeout(15000)
    });
    const html = await res.text();
    // Simple text extraction
    const text = html
      .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
      .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
      .replace(/<[^>]+>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
    return text.slice(0, 8000);
  } catch (e) {
    return `Failed to extract: ${e.message}`;
  }
}

// ── PDF Extraction ──────────────────────────────────────────────────────────

async function extractPDF(filePath) {
  try {
    const buffer = readFileSync(filePath);
    const text = buffer.toString('utf8').replace(/[^\x20-\x7E\n]/g, ' ').slice(0, 8000);
    return text;
  } catch (e) {
    return `Failed to read PDF: ${e.message}`;
  }
}

// ── Video Transcript ────────────────────────────────────────────────────────

async function extractVideo(url) {
  // B站short video BV号提取
  const bvMatch = url.match(/bilibili\.com\/video\/(BV[\w]+)/);
  if (bvMatch) {
    return `[B站视频 ${bvMatch[1]}] 请访问 https://www.bilibili.com/video/${bvMatch[1]} 获取字幕` +
           `\n\n提示：可使用 WebFetch 访问字幕页面提取文字`;
  }
  if (url.includes('youtube.com')) {
    return `[YouTube视频] 请访问 ${url} 获取字幕` +
           `\n\n提示：YouTube字幕可通过 ytfzf 或直接WebFetch访问`;
  }
  return `[视频] 无法解析，请提供字幕文件`;
}

// ── Summarization ────────────────────────────────────────────────────────────

async function summarize(text, type, source) {
  let prompt;
  if (type === 'arxiv') {
    // For arXiv, use structured extraction (no LLM needed for metadata)
    const lines = text.split('\n');
    const titleLine = lines.find(l => l.startsWith('Title:')) || '';
    const authorsLine = lines.find(l => l.startsWith('Authors:')) || '';
    const abstractLine = lines.find(l => l.startsWith('Abstract:')) || '';
    const subjectsLine = lines.find(l => l.startsWith('Subjects:')) || '';
    prompt = `以下是arXiv论文的元数据，请直接整理为百科格式，不要添加不存在的内容：

${text.slice(0, 3000)}

格式：
# ${source}

## 论文信息
- **作者**：${authorsLine.replace('Authors:', '').trim()}
- **分类**：${subjectsLine.replace('Subjects:', '').trim()}

## 摘要
${abstractLine.replace('Abstract:', '').trim()}

## 关键术语
（从摘要中提取3-5个关键术语，用逗号分隔）`;
  } else {
    prompt = `你是内容分析助手。分析以下${type}内容，提取关键信息，输出结构化Markdown。

格式：
# ${source} 分析

## 概要
- 核心主题：
- 来源类型：

## 关键内容
- 要点1
- 要点2
- 要点3

## 标签
#category

## 原始摘要
\`\`\`
${text.slice(0, 2000)}
\`\`\``;
  }

  try {
    const res = await fetch(OLLAMA_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: MODEL,
        messages: [{ role: 'user', content: prompt }],
        stream: false
      }),
      signal: AbortSignal.timeout(60000)
    });
    const data = await res.json();
    return data.message?.content || text.slice(0, 500);
  } catch (e) {
    return `## 原始摘要\n\n${text.slice(0, 1000)}`;
  }
}

// ── Main ────────────────────────────────────────────────────────────────────

async function main() {
  const input = process.argv[2];
  if (!input) {
    console.log('Usage: node analyze.mjs <url-or-path> [--output DIR]');
    process.exit(1);
  }

  const outputArg = process.argv.indexOf('--output');
  const outputDir = outputArg > -1 ? process.argv[outputArg + 1] : OUTPUT_DIR;
  mkdirSync(outputDir, { recursive: true });

  const type = detectType(input);
  console.log(`[analyze] Type: ${type}`);

  let content = '';
  let source = basename(input, extname(input));
  if (type === 'arxiv') {
    const meta = await arxivLookup(input);
    if (!meta) { console.error('Failed to fetch arXiv metadata'); process.exit(1); }
    source = meta.title;
    content = `Title: ${meta.title}\n\nAuthors: ${meta.authors.join(', ')}\n\nSubjects: ${meta.subjects.slice(0, 3).join(' / ')}\n\nAbstract: ${meta.abstract}`;
  } else if (type === 'webpage') content = await extractWebpage(input);
  else if (type === 'pdf-file') content = await extractPDF(input);
  else if (type === 'pdf-url') content = await extractWebpage(input);
  else if (type === 'video') content = await extractVideo(input);
  else { console.error('Unknown type'); process.exit(1); }

  const summary = await summarize(content, type, source);

  const timestamp = new Date().toISOString().slice(0, 10);
  const filename = `analysis-${timestamp}-${Date.now()}.md`;
  const filepath = join(outputDir, filename);

  const frontmatter = `---
source: ${input}
type: ${type}
analyzed: ${new Date().toISOString()}
---

`;
  writeFileSync(filepath, frontmatter + summary);
  console.log(`[analyze] Saved: ${filepath}`);
}

main().catch(console.error);
