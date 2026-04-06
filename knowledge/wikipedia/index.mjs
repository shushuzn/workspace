/**
 * index.mjs — Generate Wikipedia-style index page
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const INDEX_FILE = join(__DIR, 'index.json');
const OUTPUT = join(__DIR, 'index.html');

function loadIndex() {
  if (!existsSync(INDEX_FILE)) return { articles: [], categories: [] };
  return JSON.parse(readFileSync(INDEX_FILE, 'utf8'));
}

function render() {
  const idx = loadIndex();
  const cats = idx.categories || [];
  const arts = idx.articles || [];

  // Category sections
  const catSections = cats.map(cat => {
    const catArts = arts.filter(a => a.category === cat);
    const artLis = catArts.map(a =>
      `      <li><a href="${a.file}">${a.title}</a> <span class="tags">${(a.tags||[]).map(t => `#${t}`).join(' ')}</span></li>`
    ).join('\n');
    return `    <section>
      <h2>${cat}</h2>
      <ul>${artLis || '<li>（暂无条目）</li>'}</ul>
    </section>`;
  }).join('\n');

  const html = `<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${idx.title || 'Workspace Wiki'}</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f6f6f6; color: #222; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 2rem; }
  header { border-bottom: 1px solid #ccc; margin-bottom: 2rem; padding-bottom: 1rem; }
  h1 { font-size: 2rem; } h2 { font-size: 1.3rem; color: #444; margin: 1.5rem 0 0.5rem; border-bottom: 1px solid #eee; padding-bottom: 0.3rem; }
  ul { list-style: none; }
  li { padding: 0.3rem 0; }
  a { color: #0645ad; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .tags { font-size: 0.85rem; color: #666; }
  .search { margin: 1rem 0; }
  input { width: 100%; padding: 0.6rem; font-size: 1rem; border: 1px solid #ccc; border-radius: 4px; }
  .recent { background: #f0f7ff; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; }
  .recent h2 { margin-top: 0; border: none; }
  footer { margin-top: 3rem; text-align: center; color: #666; font-size: 0.9rem; }
  section { background: white; padding: 1rem 1.5rem; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
</style>
</head>
<body>
<header>
  <h1>📚 ${idx.title || 'Workspace Wiki'}</h1>
  <p>${idx.description || '维基百科风格知识库'} · 共 ${arts.length} 条目</p>
</header>

<div class="search">
  <input type="text" id="search" placeholder="搜索标签、标题、分类..." oninput="filter()">
</div>

<div id="content">
${catSections || '<p>暂无条目，运行 <code>node wiki.mjs create</code> 创建</p>'}
</div>

<script>
function filter() {
  const q = document.getElementById('search').value.toLowerCase();
  const sections = document.querySelectorAll('section');
  sections.forEach(sec => {
    const text = sec.textContent.toLowerCase();
    sec.style.display = q && !text.includes(q) ? 'none' : 'block';
  });
}
</script>

<footer>
  <p>由 <code>wiki.mjs</code> 管理 · ${new Date().toLocaleDateString('zh-CN')}</p>
</footer>
</body>
</html>`;

  writeFileSync(OUTPUT, html);
  console.log(`[wiki] index.html updated — ${arts.length} articles, ${cats.length} categories`);
}

render();
