/**
 * wiki.mjs — Wikipedia-style Knowledge Base Pipeline
 *
 * Usage:
 *   node wiki.mjs create "<title>" --category <cat> --tags <tags>  创建条目
 *   node wiki.mjs ingest <url-or-path> [--analyze]         抓取并创建条目
 *   node wiki.mjs view <title-or-id>                      阅读条目
 *   node wiki.mjs search <query>                           搜索
 *   node wiki.mjs list [category]                          列出条目
 *   node wiki.mjs link <id1> <id2>                        创建条目关联
 *   node wiki.mjs backlinks <title>                       反向链接查询
 *   node wiki.mjs orphan                                  孤立条目检测
 *   node wiki.mjs sync                                   同步索引
 *   node wiki.mjs linkcheck                              检测断链
 *   node wiki.mjs edit <title-or-id>                     用Obsidian编辑条目
 *   node wiki.mjs scene-parse <title> [--dry-run] [--register]  解析视频脚本配图
 *   node wiki.mjs quality [--json] [--limit=20]          条目质量评分
 */

// ── Setup ────────────────────────────────────────────────────────────────────
import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync, unlinkSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const __DIR = dirname(fileURLToPath(import.meta.url));
const INDEX_FILE = join(__DIR, 'index.json');
const ARTICLES_DIR = join(__DIR, 'articles');

const INDEX_HTML = `<!DOCTYPE html>
<html lang="zh">
<head><meta charset="UTF-8"><title>Wikipedia Knowledge Base</title>
<style>
  body{font-family:system-ui;max-width:900px;margin:2rem auto;padding:0 1rem;background:#f9f9f9}
  h1{color:#1a1a2e;border-bottom:2px solid #1a1a2e;padding-bottom:.5rem}
  .cat{margin:1.5rem 0}
  .cat h2{color:#16213e;font-size:1.1rem;margin:.5rem 0}
  .art{background:white;border-radius:8px;padding:0.75rem 1rem;margin:.25rem 0;box-shadow:0 1px 3px rgba(0,0,0,.1)}
  .art a{color:#1a1a2e;text-decoration:none;font-weight:500}
  .art a:hover{color:#0f3460}
  .tags{font-size:0.8rem;color:#888;margin-top:.25rem}
  .tag{background:#e8e8f0;padding:0.1rem .4rem;border-radius:4px;margin-right:.3rem}
  .orphan{opacity:.5}
  .count{color:#888;font-size:0.9rem;float:right}
  form{margin:1rem 0}
  input{padding:.5rem;border:1px solid #ccc;border-radius:4px;width:300px}
  button{padding:.5rem 1rem;background:#1a1a2e;color:white;border:none;border-radius:4px;cursor:pointer}
</style>
</head>
<body>
<h1>📚 Wikipedia Knowledge Base <span id="count" class="count"></span></h1>
<form onsubmit="event.preventDefault();window.location.search='?q='+encodeURIComponent(this.q.value)">
<input name="q" placeholder="搜索知识点..." autofocus><button>搜索</button>
</form>
<div id="content">加载中...</div>
<script>
fetch('/api/articles').then(r=>r.json()).then(arts=>{
  document.getElementById('count').textContent=arts.length+' 条目';
  if(!arts.length){document.getElementById('content').innerHTML='<p>暂无条目</p>';return}
  const params=new URLSearchParams(window.location.search);
  const q=params.get('q')||'';
  const filtered=q?arts.filter(a=>a.title.includes(q)||(a.tags||[]).some(t=>t.includes(q))):arts;
  if(!filtered.length){document.getElementById('content').innerHTML='<p>无结果</p>';return}
  const cats=[...new Set(filtered.map(a=>a.category))];
  document.getElementById('content').innerHTML=cats.map(cat=>{
    const catArts=filtered.filter(a=>a.category===cat);
    return '<div class="cat"><h2>'+cat+' ('+catArts.length+')</h2>'+catArts.map(a=>
      '<div class="art'+(a.orphan?' orphan':'')+'"><a href="/'+a.id+'">'+a.title+'</a>'+
      (a.tags&&a.tags.length?'<div class="tags">'+a.tags.map(t=>'<span class="tag">'+t+'</span>').join('')+'</div>':'')+'</div>'
    ).join('')+'</div>';
  }).join('');
});
</script>
</body>
</html>`;
` + '<!DOCTYPE html>' +
'<html lang="zh">' +
'<head><meta charset="UTF-8"><title>Wikipedia Knowledge Base</title>' +
'<style>' +
'  body{font-family:system-ui;max-width:900px;margin:2rem auto;padding:0 1rem;background:#f9f9f9}' +
'  h1{color:#1a1a2e;border-bottom:2px solid #1a1a2e;padding-bottom:.5rem}' +
'  .cat{margin:1.5rem 0}' +
'  .cat h2{color:#16213e;font-size:1.1rem;margin:.5rem 0}' +
'  .art{background:white;border-radius:8px;padding:0.75rem 1rem;margin:.25rem 0;box-shadow:0 1px 3px rgba(0,0,0,.1)}' +
'  .art a{color:#1a1a2e;text-decoration:none;fontweight:500}' +
'  .art a:hover{color:#0f3460}' +
'  .tags{font-size:0.8rem;color:#888;margin-top:.25rem}' +
'  .tag{background:#e8e8f0;padding:0.1rem .4rem;border-radius:4px;margin-right:.3rem}' +
'  .orphan{opacity:.5}' +
'  .count{color:#888;font-size:0.9rem;float:right}' +
'  form{margin:1rem 0}' +
'  input{padding:.5rem;border:1px solid #ccc;border-radius:4px;width:300px}' +
'  button{padding:.5rem 1rem;background:#1a1a2e;color:white;border:none;border-radius:4px;cursor:pointer}' +
'</style>' +
'</head>' +
'<body>' +
'<h1>📚 Wikipedia Knowledge Base <span id="count" class="count"></span></h1>' +
'<form onsubmit="event.preventDefault();window.location.search=\'?q=\'+encodeURIComponent(this.q.value)">' +
'<input name="q" placeholder="搜索知识点..." autofocus><button>搜索</button>' +
'</form>' +
'<div id="content">加载中...</div>' +
'<script>' +
'fetch(\'/api/articles\').then(r=>r.json()).then(arts=>{' +
'  document.getElementById(\'count\').textContent=arts.length+\' 条目\';' +
'  if(!arts.length){document.getElementById(\'content\').innerHTML=\'<p>暂无条目</p>\';return}' +
'  const params=new URLSearchParams(window.location.search);' +
'  const q=params.get(\'q\')||\'\';' +
'  const filtered=q?arts.filter(a=>a.title.includes(q)||(a.tags||[]).some(t=>t.includes(q))):arts;' +
'  if(!filtered.length){document.getElementById(\'content\').innerHTML=\'<p>无结果</p>\';return}' +
'  const cats=[...new Set(filtered.map(a=>a.category))];' +
'  let html=\'\';' +
'  cats.forEach(cat=>{' +
'    const catArts=filtered.filter(a=>a.category===cat);' +
'    html+=\'<div class="cat"><h2>\'+cat+\' (\'+catArts.length+\')</h2>\';' +
'    catArts.forEach(a=>{' +
'      html+=\'<div class="art\'+(a.orphan?\' orphan\':\'\')+\'><a href="/\'+a.id+\'">\'+a.title+\'</a>\';' +
'      if(a.tags&&a.tags.length){' +
'        html+=\'<div class="tags">\';' +
'        a.tags.forEach(t=>{ html+=\'<span class="tag">\'+t+\'</span>\'; });' +
'        html+=\'</div>\';' +
'      }' +
'      html+=\'</div>\';' +
'    });' +
'    html+=\'</div>\';' +
'  });' +
'  document.getElementById(\'content\').innerHTML=html;' +
'});' +
'</script>' +
'</body>' +
'</html>';
function loadIndex() {
  if (!existsSync(INDEX_FILE)) return { articles: [], categories: [] };
  try {
    return JSON.parse(readFileSync(INDEX_FILE, 'utf8'));
  } catch {
    return { articles: [], categories: [] };
  }
}

function saveIndex(idx) {
  writeFileSync(INDEX_FILE, JSON.stringify(idx, null, 2), 'utf8');
}

function slugify(text) {
  return text.toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^\w\u4e00-\u9fa5-]/g, '')
    .replace(/--+/g, '-')
    .trim();
}

function createArticle(title, content, category = '未分类', tags = []) {
  mkdirSync(join(ARTICLES_DIR, category), { recursive: true });
  const id = slugify(title);
  const file = join(ARTICLES_DIR, category, `${id}.md`);
  if (existsSync(file)) {
    console.error(`[wiki] Article already exists: ${file}`);
    process.exit(1);
  }
  const tagLine = tags.length ? `\ntags: [${tags.join(', ')}]` : '';
  writeFileSync(file,
    `---
id: ${id}
title: ${title}
category: ${category}${tagLine}
created: ${new Date().toISOString()}
---

${content}
`, 'utf8');
  console.log(`[wiki] Created: ${file}`);
  const idx = loadIndex();
  if (!idx.categories.includes(category)) idx.categories.push(category);
  idx.articles.push({ id, title, category, file: `${category}/${id}.md`, tags, created: new Date().toISOString() });
  saveIndex(idx);
}

// ── ArXiv API ────────────────────────────────────────────────────────────────
async function fetchArxivMeta(arxivUrl) {
  const absMatch = arxivUrl.match(/arxiv\.org\/abs\/(\d+\.\d+)/);
  if (!absMatch) return null;
  const id = absMatch[1];
  try {
    const res = await fetch(`http://export.arxiv.org/api/v1/id_list_map/${id}`);
    if (!res.ok) throw new Error('API error');
    const text = await res.text();
    // Parse arXiv API response
    const lines = text.split('\n');
    const meta = {};
    for (const line of lines) {
      if (line.includes(': ')) {
        const [key, ...vals] = line.split(': ');
        const val = vals.join(': ').trim();
        if (['id', 'title', 'authors', 'abstract', 'doi', 'categories'].includes(key.toLowerCase())) {
          meta[key.toLowerCase()] = val;
        }
      }
    }
    if (!meta.title) return null;
    return {
      title: meta.title.replace(/\n/g, ' ').trim(),
      authors: meta.authors ? meta.authors.replace(/\n/g, ' ').trim() : 'Unknown',
      abstract: meta.abstract ? meta.abstract.replace(/\n/g, ' ').trim() : '',
      arxivId: id,
      category: 'AI',
    };
  } catch {
    return null;
  }
}

async function extractWebpage(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) return null;
    const html = await res.text();
    return html
      .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
      .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
      .replace(/<[^>]+>/g, ' ')
      .replace(/\s+/g, ' ').trim().slice(0, 6000);
  } catch {
    return null;
  }
}

async function extractPDF(filePath) {
  try {
    const buf = readFileSync(filePath);
    return buf.toString('utf8').replace(/[^\x20-\x7E\n]/g, ' ').slice(0, 6000);
  } catch {
    return null;
  }
}

// ── Scene Code Generator ──────────────────────────────────────────────────────
function generateSceneCode(sceneNum, desc, funcName) {
  const kw = desc.toLowerCase();
  let figType = 'generic';
  if (kw.includes('graph') || kw.includes('iam') || kw.includes('network') || kw.includes('网络')) figType = 'network';
  else if (kw.includes('compare') || kw.includes('method') || kw.includes('对比') || kw.includes('比较')) figType = 'comparison';
  else if (kw.includes('pipeline') || kw.includes('burau') || kw.includes('流程')) figType = 'pipeline';
  else if (kw.includes('proof') || kw.includes('theorem') || kw.includes('数学')) figType = 'math';
  else if (kw.includes('transfer') || kw.includes('cross') || kw.includes('迁移')) figType = 'transfer';
  else if (kw.includes('attack') || kw.includes('defense') || kw.includes('对抗')) figType = 'attack';
  else if (kw.includes('formula') || kw.includes('equation') || kw.includes('le')) figType = 'formula';
  else if (kw.includes('cover') || kw.includes('封面')) figType = 'cover';
  const n = String(sceneNum).padStart(2, '0');
  const d = desc.replace(/"/g, '\\"');
  let code = 'def ' + funcName + '(fig, ax):\n';
  code += '    ax.clear()\n    ax.set_xlim(0, 12)\n    ax.set_ylim(0, 8)\n    ax.axis("off")\n';
  if (figType === 'cover') {
    code += '    ax.text(6, 4.5, "' + d + '", ha="center", va="center", fontsize=24, fontweight="bold")';
  } else if (figType === 'network') {
    code += '    ax.text(0.5, 7.5, "[' + '"+"' + 'n+' + '"+] " + "' + d + '", fontsize=11, color="#444")\n';
    code += '    draw_iam_graph(ax, "' + d + '")';
  } else if (figType === 'comparison') {
    code += '    ax.text(0.5, 7.5, "[' + '"+"' + 'n+' + '"+] " + "' + d + '", fontsize=11, color="#444")\n';
    code += '    draw_comparison(fig, ax, "' + d + '")';
  } else if (figType === 'pipeline') {
    code += '    ax.text(0.5, 7.5, "[' + '"+"' + 'n+' + '"+] " + "' + d + '", fontsize=11, color="#444")\n';
    code += '    draw_burau_pipeline(ax, "' + d + '")';
  } else if (figType === 'math') {
    code += '    ax.text(0.5, 7.5, "[' + '"+"' + 'n+' + '"+] " + "' + d + '", fontsize=11, color="#444")\n';
    code += '    ax.text(6, 4, "' + d + '", ha="center", va="center", fontsize=16, style="italic")';
  } else if (figType === 'transfer') {
    code += '    ax.text(0.5, 7.5, "[' + '"+"' + 'n+' + '"+] " + "' + d + '", fontsize=11, color="#444")\n';
    code += '    draw_transfer_diagram(ax, "' + d + '")';
  } else if (figType === 'attack') {
    code += '    ax.text(0.5, 7.5, "[' + '"+"' + 'n+' + '"+] " + "' + d + '", fontsize=11, color="#444")\n';
    code += '    draw_attack_path(ax, "' + d + '")';
  } else if (figType === 'formula') {
    code += '    ax.text(0.5, 7.5, "[' + '"+"' + 'n+' + '"+] " + "' + d + '", fontsize=11, color="#444")\n';
    code += '    ax.text(6, 4, "LE = ' + d + '", ha="center", va="center", fontsize=14, color="#1a1a2e")';
  } else {
    code += '    ax.text(6, 4, "' + d + '", ha="center", va="center", fontsize=14)';
  }
  return code;
}



// ── Commands ────────────────────────────────────────────────────────────────

const cmd = process.argv[2];

if (cmd === 'create') {
  const titleIdx = process.argv.indexOf('create') + 1;
  const title = process.argv[titleIdx];
  if (!title) { console.log('Usage: node wiki.mjs create "<title>" [--type video-script] [--category C] [--tags t1,t2]'); process.exit(1); }
  const catIdx = process.argv.indexOf('--category');
  const tagsIdx = process.argv.indexOf('--tags');
  const typeIdx = process.argv.indexOf('--type');
  const articleType = typeIdx > -1 ? process.argv[typeIdx + 1] : 'article';
  const category = catIdx > -1 ? process.argv[catIdx + 1] : '未分类';
  const tags = tagsIdx > -1 ? process.argv[tagsIdx + 1].split(',') : [];

  if (articleType === 'video-script') {
    const template = `---
title: ${title}
duration: ~3min
style: 轻松
target_audience: 科普观众
---

# ${title}

## 开场（介绍研究背景）

[画面：封面图]

本视频介绍...

## 展开（核心方法）

[画面：场景1描述]

[画面：场景2描述]

## 总结（关键发现）

[画面：总结图]

本视频的核心要点...
`;
    const slug = title.toLowerCase().replace(/[^\w\s\u4e00-\u9fa5]/g, '').replace(/\s+/g, '-');
    const catDir = category || '未分类';
    mkdirSync(join(ARTICLES_DIR, catDir), { recursive: true });
    const file = join(ARTICLES_DIR, catDir, `01-${slug}.md`);
    writeFileSync(file, template, 'utf8');
    console.log(`[wiki] 视频脚本已创建: ${file}`);
    process.exit(0);
  }

  const content = process.argv.slice(titleIdx + 1).join(' ') || '待补充内容';
  createArticle(title, content, category, tags);
}

else if (cmd === 'ingest') {
  const input = process.argv[3];
  const analyzeIdx = process.argv.indexOf('--analyze');
  if (!input) { console.log('Usage: node wiki.mjs ingest <url-or-path> [--analyze] [--category C] [--tags t1,t2]'); process.exit(1); }
  const catIdx = process.argv.indexOf('--category');
  const tagsIdx = process.argv.indexOf('--tags');
  const category = catIdx > -1 ? process.argv[catIdx + 1] : '待分类';
  const tags = tagsIdx > -1 ? process.argv[tagsIdx + 1].split(',') : [];

  if (analyzeIdx > -1 && /arxiv\.org\/(abs|pdf)\//.test(input)) {
    const meta = await fetchArxivMeta(input);
    if (!meta) { console.error('[wiki] Failed to fetch arXiv metadata'); process.exit(1); }
    const { execSync: exec } = await import('child_process');
    const analysisIdx = process.argv.indexOf('--analyze');
    if (analysisIdx > -1) {
      try {
        const out = exec(`python3 -c "
import sys
try:
    import arxiv
    client = arxiv.Client()
    search = arxiv.Search(id_list=['${meta.arxivId}'])
    papers = list(client.results(search))
    if papers:
        p = papers[0]
        print('TITLE:', p.title)
        print('AUTHORS:', ', '.join(str(a) for a in p.authors))
        print('ABSTRACT:', p.summary[:500])
except Exception as e:
    print('ERROR:', e, file=sys.stderr)
    sys.exit(1)
"`, { encoding: 'utf8', timeout: 15000 });
        console.log(out.stdout || out.stderr);
      } catch (e) {
        console.error('[wiki] Analysis error:', e.message);
      }
    }
    const noteContent = `---
id: ${slugify(meta.title)}
title: ${meta.title}
category: ${meta.category || category}
tags: [${tags.join(', ')}]
arxiv: ${meta.arxivId}
created: ${new Date().toISOString()}
---

## 论文信息

- **标题**: ${meta.title}
- **作者**: ${meta.authors}
- **arXiv**: ${meta.arxivId}

## 研究动机

（人工补充：为什么这项研究重要？解决了什么问题？）

## 核心方法

（人工补充：论文的主要技术方法是什么？）

## 关键发现

（人工补充：实验结果和关键结论是什么？）

## 个人评价

（人工补充：对这项研究的思考、局限性和应用前景）
`;
    mkdirSync(join(ARTICLES_DIR, meta.category || category), { recursive: true });
    const file = join(ARTICLES_DIR, meta.category || category, `${slugify(meta.title)}.md`);
    writeFileSync(file, noteContent, 'utf8');
    console.log(`[wiki] Created: ${file}`);
    process.exit(0);
  }

  let content = '';
  if (input.startsWith('http')) {
    content = await extractWebpage(input);
  } else {
    content = await extractPDF(input);
  }
  if (!content) { console.error('Failed to extract content'); process.exit(1); }
  const titleMatch = content.match(/^#\s+(.+)/m);
  const title = titleMatch ? titleMatch[1] : 'Untitled';
  createArticle(title, content, category, tags);
}

else if (cmd === 'edit') {
  const args = process.argv.slice(3);
  if (!args.length) { console.log('Usage: node wiki.mjs edit <title-or-id> [--exact]'); process.exit(1); }
  const useExact = args.includes('--exact');
  const query = (useExact ? args[0] : args[args.length - 1]).toLowerCase();
  const idx = loadIndex();

  let matches = idx.articles.filter(a =>
    a.id.toLowerCase().includes(query) || a.title.toLowerCase().includes(query)
  );

  if (!matches.length) { console.error('Article not found'); process.exit(1); }

  if (matches.length > 1) {
    console.log(`\n找到 ${matches.length} 个匹配结果：`);
    matches.slice(0, 10).forEach((a, i) => {
      console.log(`  ${i + 1}. [${a.category}] ${a.title}`);
    });
    if (matches.length > 10) console.log(`  ...（共 ${matches.length} 个）`);
    console.log(`\n使用 --exact 精确匹配，或直接运行 wiki.mjs edit <完整标题>`);
    process.exit(1);
  }

  const art = matches[0];
  const { execSync: exec } = await import('child_process');
  try {
    exec(`obsidian vault="3cb50ee5e304a7ea" open file="${art.file}"`, { stdio: 'inherit' });
    console.log(`[wiki] Opened in Obsidian: ${art.title}`);
  } catch {
    console.error('[wiki] Obsidian CLI not found or vault not open');
    process.exit(1);
  }
}

else if (cmd === 'obsidian') {
  const { execSync: exec } = await import('child_process');
  const args = process.argv.slice(3);
  if (!args.length) {
    console.log('Usage: node wiki.mjs obsidian <obsidian-command> [args...]');
    console.log('Example: node wiki.mjs obsidian search query=AI');
    process.exit(1);
  }
  try {
    const result = exec(`obsidian ${args.join(' ')}`, { encoding: 'utf8', stdio: 'pipe' });
    if (result.stdout) process.stdout.write(result.stdout);
    if (result.stderr) process.stderr.write(result.stderr);
  } catch (e) {
    console.error('[wiki] Obsidian CLI error:', e.message);
    process.exit(1);
  }
}

else if (cmd === 'view') {
  const query = process.argv[3]?.toLowerCase();
  if (!query) { console.log('Usage: node wiki.mjs view <title-or-id>'); process.exit(1); }
  const idx = loadIndex();
  const art = idx.articles.find(a => a.id.toLowerCase().includes(query) || a.title.toLowerCase().includes(query));
  if (!art) { console.error('Article not found'); process.exit(1); }
  const file = join(__DIR, art.file);
  if (!existsSync(file)) { console.error('File not found on disk:', file); process.exit(1); }
  const content = readFileSync(file, 'utf8');
  const lines = content.split('\n');
  console.log(lines.slice(0, 40).join('\n'));
  if (lines.length > 40) console.log('\n  [... ' + (lines.length - 40) + ' more lines]');
}

else if (cmd === 'search') {
  const query = process.argv[3]?.toLowerCase();
  if (!query) { console.log('Usage: node wiki.mjs search <query>'); process.exit(1); }
  const idx = loadIndex();
  const results = idx.articles.filter(a =>
    a.title.toLowerCase().includes(query) ||
    (a.tags || []).some(t => t.toLowerCase().includes(query)) ||
    a.category.toLowerCase().includes(query)
  );
  if (!results.length) { console.log('No results'); process.exit(0); }
  console.log(`\n# 搜索结果: ${results.length}\n`);
  results.forEach(r => console.log(`  • ${r.title} [${r.category}]`));
  console.log();
}

else if (cmd === 'list') {
  const cat = process.argv[3];
  const idx = loadIndex();
  if (cat) {
    const arts = idx.articles.filter(a => a.category === cat);
    console.log(`\n# ${cat} (${arts.length})\n`);
    arts.forEach(a => console.log(`  • ${a.title}`));
  } else {
    console.log(`\n# 全部类别\n`);
    idx.categories.forEach(c => {
      const count = idx.articles.filter(a => a.category === c).length;
      console.log(`  ${c} (${count})`);
    });
    console.log(`\n总条目: ${idx.articles.length}`);
  }
  console.log();
}

else if (cmd === 'import') {
  const dir = process.argv[3];
  if (!dir) { console.log('Usage: node wiki.mjs import <dir>'); process.exit(1); }
  const idx = loadIndex();
  const { readdirSync: rd, statSync: st } = await import('fs');
  let errors = 0;
  const mdFiles = [];
  function scan(d) {
    for (const f of rd(d, { withFileTypes: true })) {
      if (f.isDirectory()) scan(join(d, f.name));
      else if (f.name.endsWith('.md')) mdFiles.push(join(d, f.name));
    }
  }
  scan(dir);
  for (const file of mdFiles) {
    try {
      const content = readFileSync(file, 'utf8');
      const fmMatch = content.match(/^---\n([\s\S]*?)\n---\n/);
      if (!fmMatch) continue;
      const fm = fmMatch[1];
      const idMatch = fm.match(/^id:\s*(.+)$/m);
      const titleMatch = fm.match(/^title:\s*(.+)$/m);
      const catMatch = fm.match(/^category:\s*(.+)$/m);
      const tagsMatch = fm.match(/^tags:\s*\[(.+)\]/m);
      if (!idMatch || !titleMatch) { errors++; continue; }
      const id = idMatch[1].trim();
      const title = titleMatch[1].trim();
      const category = catMatch ? catMatch[1].trim() : '未分类';
      const tags = tagsMatch ? tagsMatch[1].split(',').map(t => t.trim()) : [];
      const relPath = file.replace(__DIR + '\\', '').replace(__DIR + '/', '');
      if (!idx.categories.includes(category)) idx.categories.push(category);
      if (!idx.articles.find(a => a.id === id)) {
        idx.articles.push({ id, title, category, file: relPath, tags, created: new Date().toISOString() });
        console.log(`  + ${title}`);
      }
    } catch {}
  }
  saveIndex(idx);
  if (errors) console.log(`\n[wiki] ${errors} files skipped (no frontmatter)`);
  console.log(`\n[wiki] Indexed ${idx.articles.length} articles`);
}

else if (cmd === 'link') {
  const id1 = process.argv[3];
  const id2 = process.argv[4];
  if (!id1 || !id2) { console.log('Usage: node wiki.mjs link <id1> <id2>'); process.exit(1); }
  const idx = loadIndex();
  const art1 = idx.articles.find(a => a.id === id1 || a.title.toLowerCase().includes(id1.toLowerCase()));
  const art2 = idx.articles.find(a => a.id === id2 || a.title.toLowerCase().includes(id2.toLowerCase()));
  if (!art1 || !art2) { console.error('Article not found'); process.exit(1); }
  const file1 = join(__DIR, art1.file);
  let content = readFileSync(file1, 'utf8');
  if (!content.includes(`[[${art2.title}]]`)) {
    content += `\n\n参见：[[${art2.title}]]\n`;
    writeFileSync(file1, content, 'utf8');
    console.log(`[wiki] Added link: [[${art1.title}]] → [[${art2.title}]]`);
  } else {
    console.log('[wiki] Link already exists');
  }
}

else if (cmd === 'delete') {
  const id = process.argv[3];
  if (!id) { console.log('Usage: node wiki.mjs delete <id>'); process.exit(1); }
  const idx = loadIndex();
  const art = idx.articles.find(a => a.id === id || a.title.toLowerCase().includes(id.toLowerCase()));
  if (!art) { console.error('Article not found'); process.exit(1); }
  const file = join(__DIR, art.file);
  if (existsSync(file)) unlinkSync(file);
  idx.articles = idx.articles.filter(a => a.id !== art.id);
  saveIndex(idx);
  console.log(`[wiki] Deleted: ${art.title}`);
}

else if (cmd === 'category-rename') {
  const oldCat = process.argv[3];
  const newCat = process.argv[4];
  if (!oldCat || !newCat) { console.log('Usage: node wiki.mjs category-rename <old> <new>'); process.exit(1); }
  const idx = loadIndex();
  if (!idx.categories.includes(oldCat)) { console.error('Category not found'); process.exit(1); }
  for (const art of idx.articles) {
    if (art.category === oldCat) {
      art.category = newCat;
      const oldFile = join(__DIR, art.file);
      const newFile = join(__DIR, newCat, art.file.split('/').pop());
      if (existsSync(oldFile)) {
        mkdirSync(join(__DIR, newCat), { recursive: true });
        const { renameSync: rename } = await import('fs');
        rename(oldFile, newFile);
        art.file = `${newCat}/${art.file.split('/').pop()}`;
      }
    }
  }
  idx.categories = idx.categories.map(c => c === oldCat ? newCat : c);
  saveIndex(idx);
  console.log(`[wiki] Renamed: ${oldCat} → ${newCat}`);
}

else if (cmd === 'orphan') {
  const idx = loadIndex();
  const inboundCount = {};
  for (const art of idx.articles) {
    const file = join(__DIR, art.file);
    if (!existsSync(file)) continue;
    const content = readFileSync(file, 'utf8');
    const wikiLinkPattern = /\[\[([^\]]+)\]\]/g;
    let m;
    while ((m = wikiLinkPattern.exec(content)) !== null) {
      const refSlug = slugify(m[1]);
      const target = idx.articles.find(a => a.id.includes(refSlug) || slugify(a.title) === refSlug);
      if (target) inboundCount[target.id] = (inboundCount[target.id] || 0) + 1;
    }
  }
  const orphans = idx.articles.filter(a => !inboundCount[a.id]);
  if (!orphans.length) { console.log('No orphan articles — all articles have inbound links'); }
  else {
    console.log(`\n# 孤立条目 (${orphans.length}) — 无其他条目引用\n`);
    orphans.forEach(a => console.log(`  • ${a.title} [${a.id}]`));
    console.log();
  }
}

else if (cmd === 'quality') {
  const jsonMode = process.argv.includes('--json');
  const limit = parseInt(process.argv.find(a => a.startsWith('--limit='))?.split('=')[1]) || 20;
  const idx = loadIndex();

  const inboundCount = {};
  const outboundCount = {};
  const articleSize = {};
  for (const art of idx.articles) {
    inboundCount[art.id] = 0;
    outboundCount[art.id] = 0;
    const file = join(__DIR, art.file);
    if (!existsSync(file)) continue;
    const content = readFileSync(file, 'utf8');
    articleSize[art.id] = content.length;
    const wikiLinkPattern = /\[\[([^\]]+)\]\]/g;
    let m;
    while ((m = wikiLinkPattern.exec(content)) !== null) {
      const refSlug = slugify(m[1]);
      const target = idx.articles.find(a => a.id.includes(refSlug) || slugify(a.title) === refSlug);
      if (target) {
        inboundCount[target.id] = (inboundCount[target.id] || 0) + 1;
        outboundCount[art.id]++;
      }
    }
  }

  const scored = idx.articles.map(a => ({
    id: a.id,
    title: a.title,
    category: a.category,
    inDegree: inboundCount[a.id] || 0,
    outDegree: outboundCount[a.id] || 0,
    score: (inboundCount[a.id] || 0) * 3 + (outboundCount[a.id] || 0),
    size: articleSize[a.id] || 0,
  }));

  const sorted = scored.sort((a, b) => a.score - b.score);
  const mostIsolated = sorted.slice(0, limit);
  const mostConnected = sorted.slice(-limit).reverse();
  const avgScore = scored.length ? (scored.reduce((s, a) => s + a.score, 0) / scored.length).toFixed(2) : 0;

  if (jsonMode) {
    console.log(JSON.stringify({ mostIsolated, mostConnected, avgScore, total: scored.length }));
    process.exit(0);
  }

  console.log(`\n# 条目质量评分（分数 = 入度×3 + 出度）`);
  console.log(`  平均分数: ${avgScore} | 总条目: ${scored.length}`);
  console.log(`\n## 最孤立条目 TOP ${limit}（需要更多引用）`);
  mostIsolated.forEach((a, i) => {
    const warn = a.inDegree === 0 ? ' ⚠️ 入度=0' : '';
    console.log(`  ${i + 1}. [${a.category}] ${a.title} 分数=${a.score}(入${a.inDegree}出${a.outDegree})${warn}`);
  });
  console.log(`\n## 最核心条目 TOP ${limit}（知识枢纽）`);
  mostConnected.forEach((a, i) => {
    console.log(`  ${i + 1}. [${a.category}] ${a.title} 分数=${a.score}(入${a.inDegree}出${a.outDegree})`);
  });
  console.log();
}

else if (cmd === 'backlinks') {
  const query = process.argv[3]?.toLowerCase() || '';
  if (!query) { console.log('Usage: node wiki.mjs backlinks <title>'); process.exit(1); }
  const idx = loadIndex();
  const results = [];
  for (const art of idx.articles) {
    const file = join(__DIR, art.file);
    if (!existsSync(file)) continue;
    if (art.title.toLowerCase().includes(query)) continue;
    const content = readFileSync(file, 'utf8');
    const refs = [];
    const wikiLinkPattern = /\[\[([^\]]+)\]\]/g;
    let m;
    while ((m = wikiLinkPattern.exec(content)) !== null) refs.push(m[1]);
    if (refs.some(r => r.toLowerCase().includes(query)) || content.toLowerCase().includes(query)) {
      results.push(art);
    }
  }
  if (!results.length) { console.log('No articles link to this entry'); process.exit(0); }
  console.log(`\n# 反向链接: ${results.length}\n`);
  results.forEach(a => console.log(`  • ${a.title} [${a.category}]`));
  console.log();
}

else if (cmd === 'stats') {
  const idx = loadIndex();
  const jsonIdx = process.argv.includes('--json');
  const inboundCount = {};
  const outboundMap = {};
  let totalLength = 0;
  let totalWords = 0;
  const tagCount = {};
  const latestArticle = idx.articles.reduce((latest, a) => {
    const aTime = new Date(a.id.match(/(\d+)$/)?.[1] || 0).getTime();
    const lTime = latest ? new Date(latest.id.match(/(\d+)$/)?.[1] || 0).getTime() : 0;
    return aTime > lTime ? a : latest;
  }, null);

  for (const art of idx.articles) {
    const file = join(__DIR, art.file);
    if (!existsSync(file)) continue;
    const content = readFileSync(file, 'utf8');
    const body = content.replace(/---[\s\S]*?---\n/, '').replace(/<[^>]+>/g, '');
    totalLength += content.length;
    totalWords += body.split(/\s+/).filter(Boolean).length;
    const wikiLinkPattern = /\[\[([^\]]+)\]\]/g;
    let m;
    outboundMap[art.id] = 0;
    while ((m = wikiLinkPattern.exec(content)) !== null) {
      outboundMap[art.id]++;
      const refSlug = slugify(m[1]);
      const target = idx.articles.find(a => a.id.includes(refSlug) || slugify(a.title) === refSlug);
      if (target) inboundCount[target.id] = (inboundCount[target.id] || 0) + 1;
    }
    const tags = (art.tags || []);
    for (const t of tags) tagCount[t] = (tagCount[t] || 0) + 1;
  }

  const sortedTags = Object.entries(tagCount).sort((a, b) => b[1] - a[1]);
  const topTags = sortedTags.slice(0, 10);
  const avgLen = totalLength / (idx.articles.length || 1);
  const avgWords = totalWords / (idx.articles.length || 1);

  if (jsonIdx) {
    console.log(JSON.stringify({
      total: idx.articles.length,
      categories: idx.categories.length,
      totalLength,
      totalWords,
      avgLen: Math.round(avgLen),
      avgWords: Math.round(avgWords),
      topTags,
      latestArticle,
    }));
    process.exit(0);
  }

  console.log(`\n# 统计\n`);
  console.log(`  条目总数: ${idx.articles.length}`);
  console.log(`  类别总数: ${idx.categories.length}`);
  console.log(`  平均长度: ${Math.round(avgLen)} 字符 / ${Math.round(avgWords)} 词`);
  console.log(`  最新条目: ${latestArticle ? latestArticle.title : 'N/A'}`);
  console.log(`\n## 热门标签`);
  topTags.forEach(([tag, count]) => console.log(`  ${tag} (${count})`));
  console.log();
}

else if (cmd === 'sync') {
  const { readdirSync: rd, statSync: st } = await import('fs');
  const idx = { articles: [], categories: [] };
  const mdFiles = [];
  function scan(d) {
    for (const f of rd(d, { withFileTypes: true })) {
      if (f.isDirectory()) scan(join(d, f.name));
      else if (f.name.endsWith('.md')) mdFiles.push(join(d, f.name));
    }
  }
  scan(ARTICLES_DIR);
  const newArticles = [];
  for (const file of mdFiles) {
    const content = readFileSync(file, 'utf8');
    const fmMatch = content.match(/^---\n([\s\S]*?)\n---\n/);
    if (!fmMatch) continue;
    const fm = fmMatch[1];
    const idMatch = fm.match(/^id:\s*(.+)$/m);
    const titleMatch = fm.match(/^title:\s*(.+)$/m);
    const catMatch = fm.match(/^category:\s*(.+)$/m);
    const tagsMatch = fm.match(/^tags:\s*\[(.+)\]/m);
    const createdMatch = fm.match(/^created:\s*(.+)$/m);
    if (!idMatch || !titleMatch) continue;
    const id = idMatch[1].trim();
    const title = titleMatch[1].trim();
    const category = catMatch ? catMatch[1].trim() : '未分类';
    const tags = tagsMatch ? tagsMatch[1].split(',').map(t => t.trim()) : [];
    const created = createdMatch ? createdMatch[1].trim() : new Date().toISOString();
    const relPath = file.replace(__DIR + '\\', '').replace(__DIR + '/', '');
    if (!idx.categories.includes(category)) idx.categories.push(category);
    idx.articles.push({ id, title, category, file: relPath, tags, created });
    if (newArticles.length < 5) console.log(`  + ${title}`);
    newArticles.push(title);
  }
  saveIndex(idx);
  console.log(`\n[wiki] Synced ${idx.articles.length} articles (${newArticles.length} new)`);
  const broken = [];
  for (const art of idx.articles) {
    const file = join(__DIR, art.file);
    if (!existsSync(file)) continue;
    const content = readFileSync(file, 'utf8');
    const wikiLinkPattern = /\[\[([^\]]+)\]\]/g;
    let m;
    while ((m = wikiLinkPattern.exec(content)) !== null) {
      const refSlug = slugify(m[1]);
      const target = idx.articles.find(a => a.id.includes(refSlug) || slugify(a.title) === refSlug);
      if (!target) broken.push({ from: art.title, link: m[1] });
    }
  }
  if (!broken.length) { console.log('No broken links — all wiki-links resolve correctly'); process.exit(0); }
  console.log(`\n# 断链报告 (${broken.length}):`);
  broken.forEach(b => console.log(`  • [[${b.link}]] 在 "${b.from}" — 目标不存在`));
  const fixIdx = process.argv.indexOf('--fix');
  if (fixIdx > -1) {
    for (const b of broken) {
      const art = idx.articles.find(a => a.title === b.from);
      if (!art) continue;
      const file = join(__DIR, art.file);
      let content = readFileSync(file, 'utf8');
      const before = content.length;
      content = content.replace(new RegExp('\\[\\[' + b.link.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\]\\]', 'g'), b.link);
      if (content.length !== before) {
        writeFileSync(file, content, 'utf8');
        console.log(`  ✓ Fixed in: ${art.title}`);
      }
    }
  }
}

else if (cmd === 'linkcheck') {
  const idx = loadIndex();
  const broken = [];
  for (const art of idx.articles) {
    const file = join(__DIR, art.file);
    if (!existsSync(file)) continue;
    const content = readFileSync(file, 'utf8');
    const wikiLinkPattern = /\[\[([^\]]+)\]\]/g;
    let m;
    while ((m = wikiLinkPattern.exec(content)) !== null) {
      const refSlug = slugify(m[1]);
      const target = idx.articles.find(a => a.id.includes(refSlug) || slugify(a.title) === refSlug);
      if (!target) broken.push({ from: art.title, link: m[1] });
    }
  }
  if (!broken.length) { console.log('No broken links — all wiki-links resolve correctly'); process.exit(0); }
  console.log(`\n# 断链报告 (${broken.length}):`);
  broken.forEach(b => console.log(`  • [[${b.link}]] 在 "${b.from}" — 目标不存在`));
}

else if (cmd === 'scene-parse') {
  const args = process.argv.slice(3);
  if (!args.length) { console.log('Usage: node wiki.mjs scene-parse <title> [--dry-run] [--register]'); process.exit(1); }
  const title = args[0];
  const dryRun = args.includes('--dry-run');
  const doRegister = args.includes('--register');

  const { readdirSync: rd } = await import('fs');
  let foundScript = null;
  const searchBase = join(__DIR, 'articles');
  const stopWords = new Set(['of','and','the','a','an','in','on','at','to','for','i','s']);
  const titleWords = title.toLowerCase().replace(/-/g, " ").split(/[\s,.;:!?]+/).filter(w => w.length > 2 && !stopWords.has(w));
  const titleSlug = titleWords.join('');
  outer:
  for (const catDir of rd(searchBase, { withFileTypes: true })) {
    if (!catDir.isDirectory()) continue;
    for (const subDir of rd(join(searchBase, catDir.name), { withFileTypes: true })) {
      if (!subDir.isDirectory()) continue;
      const subSlug = subDir.name.toLowerCase().replace(/[^\w]/g, '');
      const fullPath = join(searchBase, catDir.name, subDir.name);
      const files = rd(fullPath);
      const matches = files.filter(f => {
        const lc = f.toLowerCase();
        return lc.includes('论文解读') && lc.endsWith('.md') && titleWords.every(w => subSlug.includes(w));
      });
      if (matches.length > 0) { foundScript = join(fullPath, matches[0]); break outer; }
    }
  }

  if (!foundScript) { console.error('Video script not found (looking for *论文解读.md)'); process.exit(1); }

  const script = readFileSync(foundScript, 'utf8');
  const sceneLines = [];
  for (const line of script.split('\n')) {
    const m = line.match(/^\[画面：(.+)\]$/);
    if (m) sceneLines.push(m[1]);
  }

  if (!sceneLines.length) { console.log('No [画面：] annotations found in script'); process.exit(0); }

  const drawScenePy = join(__DIR, 'video', 'draw_scene.py');
  const existingCode = existsSync(drawScenePy) ? readFileSync(drawScenePy, 'utf8') : '';
  const newFuncs = [];
  const newRegs = [];

  for (let i = 0; i < sceneLines.length; i++) {
    const desc = sceneLines[i];
    const sceneNum = i + 1;
    const keyName = desc.replace(/[^\w\u4e00-\u9fa5]/g, '').slice(0, 12);
    const funcName = `draw_scene_${keyName}`;
    const code = generateSceneCode(sceneNum, desc, funcName);
    if (existingCode.includes(`def ${funcName}(`)) {
      console.log(`  [skip] ${funcName} already exists`);
      continue;
    }
    newFuncs.push(code);
    newRegs.push(`    '${keyName}': ${funcName},`);
    console.log(`  + ${funcName}: ${desc}`);
  }

  if (!newFuncs.length) { console.log('All scenes already registered.'); process.exit(0); }

  console.log(`\n--- SCENE_DRAWERS 新增条目 ---`);
  newRegs.forEach(r => console.log(r));

  if (dryRun) {
    console.log('\n[DRY-RUN] 以下代码未写入:');
    newFuncs.forEach(f => console.log(f));
    process.exit(0);
  }

  if (doRegister) {
    let py = existingCode;
    // 找到 SCENE_DRAWERS = { 末尾，插入新条目
    const drawerMatch = py.match(/^(SCENE_DRAWERS\s*=\s*\{[\s\S]*?)(\})$/m);
    if (drawerMatch) {
      const indent = drawerMatch[1].match(/(\s*)\S/)[1];
      py = py.replace(/^(SCENE_DRAWERS\s*=\s*\{[\s\S]*?)(\})$/m, drawerMatch[1] + '\n' + newRegs.map(r => indent + r).join('\n') + '\n' + drawerMatch[2]);
    }
    writeFileSync(drawScenePy, py, 'utf8');
    console.log(`\n[wiki] Updated SCENE_DRAWERS in: ${drawScenePy}`);
  } else {
    console.log('\n[wiki] 生成代码预览（使用 --register 写入 draw_scene.py）:');
    newFuncs.forEach(f => console.log(f));
  }
}

else {
  console.log(`Usage:
  node wiki.mjs create "<title>" [--category C] [--tags t1,t2]
  node wiki.mjs ingest <url-or-path> [--analyze]
  node wiki.mjs search <query>
  node wiki.mjs list [category]
  node wiki.mjs link <id1> <id2>
  node wiki.mjs backlinks <title>
  node wiki.mjs orphan
  node wiki.mjs quality [--json] [--limit=20]
  node wiki.mjs sync
  node wiki.mjs linkcheck
  node wiki.mjs edit <title-or-id>
  node wiki.mjs scene-parse <title> [--dry-run] [--register]
  node wiki.mjs view <title-or-id>
`);
}
