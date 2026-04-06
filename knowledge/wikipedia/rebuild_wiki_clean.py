#!/usr/bin/env python3
"""Rebuild wiki.mjs cleanly: proper INDEX_HTML, generateSceneCode, all commands."""
import os, re

os.chdir(r'D:\OpenClaw\workspace\knowledge\wikipedia')

# ============================================================
# PART 1: INDEX_HTML constant (fixed, no nested template)
# ============================================================
INDEX_HTML = r'''<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wiki</title>
  <style>
    body { font-family: sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; background: #f9f9f9; }
    h1 { border-bottom: 2px solid #ddd; padding-bottom: .5rem; }
    .cat { margin: 1.5rem 0; }
    .cat h2 { color: #333; font-size: 1.2rem; }
    .art { padding: .4rem 0; border-bottom: 1px solid #eee; }
    .art.orphan { color: #888; }
    .art a { text-decoration: none; color: #1a5f7a; }
    .art.orphan a { color: #aaa; }
    .tags { font-size: .85rem; color: #666; margin-top: .2rem; }
    .tag { background: #e8f4f8; padding: .1rem .4rem; border-radius: 3px; margin-right: .3rem; }
    .orphan-badge { background: #ffe0e0; color: #c00; font-size: .75rem; padding: .1rem .3rem; border-radius: 3px; margin-left: .5rem; }
    .search-box { width: 100%; padding: .6rem; font-size: 1rem; border: 2px solid #ddd; border-radius: 6px; margin-bottom: 1.5rem; box-sizing: border-box; }
    .search-box:focus { border-color: #1a5f7a; outline: none; }
  </style>
</head>
<body>
  <h1>Wiki</h1>
  <input class="search-box" id="searchBox" placeholder="搜索..." oninput="filter()">
  <div id="content"></div>
  <script src="index.json" defer></script>
  <script>
    const cats = ['AI','math','security','未分类'];
    const filtered = idx.articles.slice();
    function filter() {
      const q = document.getElementById('searchBox').value.toLowerCase();
      const filtered = q ? idx.articles.filter(a => a.title.toLowerCase().includes(q) || (a.tags && a.tags.some(t => t.toLowerCase().includes(q)))) : idx.articles.slice();
      document.getElementById('content').innerHTML = cats.map(cat => {
        const catArts = filtered.filter(a => a.category === cat);
        return '<div class="cat"><h2>' + cat + ' (' + catArts.length + ')</h2>' + catArts.map(a =>
          '<div class="art' + (a.orphan ? ' orphan' : '') + '"><a href="/' + a.id + '">' + a.title + '</a>' +
          (a.tags && a.tags.length ? '<div class="tags">' + a.tags.map(t => '<span class="tag">' + t + '</span>').join('') + '</div>' : '') + '</div>'
        ).join('') + '</div>';
      }).join('');
    }
    document.getElementById('content').innerHTML = cats.map(cat => {
      const catArts = filtered.filter(a => a.category === cat);
      return '<div class="cat"><h2>' + cat + ' (' + catArts.length + ')</h2>' + catArts.map(a =>
        '<div class="art' + (a.orphan ? ' orphan' : '') + '"><a href="/' + a.id + '">' + a.title + '</a>' +
        (a.tags && a.tags.length ? '<div class="tags">' + a.tags.map(t => '<span class="tag">' + t + '</span>').join('') + '</div>' : '') + '</div>'
      ).join('') + '</div>';
    }).join('');
  </script>
</body>
</html>'''

# ============================================================
# PART 2: generateSceneCode function
# ============================================================
GENERATE_SCENE_CODE = r'''// ── Scene Code Generator ──────────────────────────────────────────────────────
function generateSceneCode(sceneNum, desc, funcName) {
  const kw = desc.toLowerCase();
  let figType = 'generic';
  if (kw.includes('graph') || kw.includes('iam') || kw.includes('network') || kw.includes('网络') || kw.includes('图')) figType = 'network';
  else if (kw.includes('compare') || kw.includes('method') || kw.includes('对比') || kw.includes('比较') || kw.includes('三种')) figType = 'comparison';
  else if (kw.includes('pipeline') || kw.includes('burau') || kw.includes('流程') || kw.includes('路')) figType = 'pipeline';
  else if (kw.includes('proof') || kw.includes('theorem') || kw.includes('数学') || kw.includes('公式')) figType = 'math';
  else if (kw.includes('transfer') || kw.includes('cross') || kw.includes('迁移') || kw.includes('跨域')) figType = 'transfer';
  else if (kw.includes('attack') || kw.includes('defense') || kw.includes('对抗') || kw.includes('攻防')) figType = 'attack';
  else if (kw.includes('formula') || kw.includes('equation') || kw.includes('le') || kw.includes('指数')) figType = 'formula';
  else if (kw.includes('cover') || kw.includes('封面')) figType = 'cover';
  const n = String(sceneNum).padStart(2, '0');
  const d = desc.replace(/"/g, '\\\\"');

  if (figType === 'cover') {
    return 'def ' + funcName + '(fig, ax):\\n' +
           '    ax.clear()\\n' +
           '    ax.set_xlim(0, 12)\\n' +
           '    ax.set_ylim(0, 8)\\n' +
           '    ax.axis("off")\\n' +
           '    ax.text(6, 4.5, "' + d + '", ha="center", va="center", fontsize=24, fontweight="bold")';
  } else if (figType === 'network') {
    return 'def ' + funcName + '(fig, ax):\\n' +
           '    ax.clear()\\n' +
           '    ax.set_xlim(0, 12)\\n' +
           '    ax.set_ylim(0, 8)\\n' +
           '    ax.axis("off")\\n' +
           '    ax.text(0.5, 7.5, "[' + n + '] ' + d + '", fontsize=11, color="#444")\\n' +
           '    draw_iam_graph(ax, "' + d + '")';
  } else if (figType === 'comparison') {
    return 'def ' + funcName + '(fig, ax):\\n' +
           '    ax.clear()\\n' +
           '    ax.set_xlim(0, 12)\\n' +
           '    ax.set_ylim(0, 8)\\n' +
           '    ax.axis("off")\\n' +
           '    ax.text(0.5, 7.5, "[' + n + '] ' + d + '", fontsize=11, color="#444")\\n' +
           '    draw_comparison(fig, ax, "' + d + '")';
  } else if (figType === 'pipeline') {
    return 'def ' + funcName + '(fig, ax):\\n' +
           '    ax.clear()\\n' +
           '    ax.set_xlim(0, 12)\\n' +
           '    ax.set_ylim(0, 8)\\n' +
           '    ax.axis("off")\\n' +
           '    ax.text(0.5, 7.5, "[' + n + '] ' + d + '", fontsize=11, color="#444")\\n' +
           '    draw_burau_pipeline(ax, "' + d + '")';
  } else if (figType === 'math') {
    return 'def ' + funcName + '(fig, ax):\\n' +
           '    ax.clear()\\n' +
           '    ax.set_xlim(0, 12)\\n' +
           '    ax.set_ylim(0, 8)\\n' +
           '    ax.axis("off")\\n' +
           '    ax.text(0.5, 7.5, "[' + n + '] ' + d + '", fontsize=11, color="#444")\\n' +
           '    ax.text(6, 4, "' + d + '", ha="center", va="center", fontsize=16, style="italic")';
  } else if (figType === 'transfer') {
    return 'def ' + funcName + '(fig, ax):\\n' +
           '    ax.clear()\\n' +
           '    ax.set_xlim(0, 12)\\n' +
           '    ax.set_ylim(0, 8)\\n' +
           '    ax.axis("off")\\n' +
           '    ax.text(0.5, 7.5, "[' + n + '] ' + d + '", fontsize=11, color="#444")\\n' +
           '    draw_transfer_diagram(ax, "' + d + '")';
  } else if (figType === 'attack') {
    return 'def ' + funcName + '(fig, ax):\\n' +
           '    ax.clear()\\n' +
           '    ax.set_xlim(0, 12)\\n' +
           '    ax.set_ylim(0, 8)\\n' +
           '    ax.axis("off")\\n' +
           '    ax.text(0.5, 7.5, "[' + n + '] ' + d + '", fontsize=11, color="#444")\\n' +
           '    draw_attack_path(ax, "' + d + '")';
  } else if (figType === 'formula') {
    return 'def ' + funcName + '(fig, ax):\\n' +
           '    ax.clear()\\n' +
           '    ax.set_xlim(0, 12)\\n' +
           '    ax.set_ylim(0, 8)\\n' +
           '    ax.axis("off")\\n' +
           '    ax.text(0.5, 7.5, "[' + n + '] ' + d + '", fontsize=11, color="#444")\\n' +
           '    ax.text(6, 4, "LE = ' + d + '", ha="center", va="center", fontsize=14, color="#1a1a2e")';
  } else {
    return 'def ' + funcName + '(fig, ax):\\n' +
           '    ax.clear()\\n' +
           '    ax.set_xlim(0, 12)\\n' +
           '    ax.set_ylim(0, 8)\\n' +
           '    ax.axis("off")\\n' +
           '    ax.text(6, 4, "' + d + '", ha="center", va="center", fontsize=14)';
  }
}
'''

# ============================================================
# PART 3: Main wiki.mjs content
# ============================================================
WIKI_MJS = '''import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync, execSync } from 'fs';
import { join, dirname, basename } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const ARTICLES_DIR = join(__DIR, 'articles');
const INDEX_JSON = join(__DIR, 'index.json');
const INDEX_HTML = join(__DIR, 'index.html');

// ── Helpers ──────────────────────────────────────────────────
const { execSync: exec } = await import('child_process');

function slugify(text) {
  return text.toLowerCase()
    .replace(/[^\\w\\s-]/g, '')
    .replace(/[\\s_]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function loadIndex() {
  if (!existsSync(INDEX_JSON)) return { articles: [], categories: [] };
  return JSON.parse(readFileSync(INDEX_JSON, 'utf8'));
}

function saveIndex(idx) {
  writeFileSync(INDEX_JSON, JSON.stringify(idx, null, 2));
}

// ── arXiv API ────────────────────────────────────────────────
async function fetchArxivMeta(id) {
  try {
    const res = await fetch(`http://arxiv.org/abs/${id}`);
    if (!res.ok) return null;
    const html = await res.text();
    const title = (html.match(/<title>([^<]+)<\\/title>/i) || [])[1] || '';
    const authors = (html.match(/<meta name="citation_authors" content="([^"]+)"/i) || [])[1] || '';
    const abstract = (html.match(/<meta name="citation_abstract" content="([^"]+)"/i) || [])[1] || '';
    const match = id.match(/(\\d+\\.\\d+)/);
    const ver = match ? match[1] : id;
    if (!title) return null;
    return {
      title: title.replace(/\\s+/g, ' ').trim(),
      authors: authors.replace(/\\s+/g, ' ').trim(),
      abstract: abstract.replace(/\\s+/g, ' ').trim(),
      arxivId: ver,
      category: 'AI',
    };
  } catch { return null; }
}

// ── Scene Parse ──────────────────────────────────────────────
''' + GENERATE_SCENE_CODE + '''

// ── Commands ─────────────────────────────────────────────────
const cmd = process.argv[2];

if (cmd === 'create') {
  const titleIdx = process.argv.indexOf('create') + 1;
  const title = process.argv[titleIdx];
  if (!title) { console.log('Usage: node wiki.mjs create "<title>" [--type video-script] [--category C] [--tags t1,t2]'); process.exit(1); }
  const catIdx = process.argv.indexOf('--category');
  const tagsIdx = process.argv.indexOf('--tags');
  const typeIdx = process.argv.indexOf('--type');
  const articleType = typeIdx > -1 ? process.argv[typeIdx + 1] : 'article';
  const category = catIdx > -1 ? process.argv[catIdx + 1] : 'AI';
  const tags = tagsIdx > -1 ? process.argv[tagsIdx + 1].split(',') : [];

  mkdirSync(join(ARTICLES_DIR, category), { recursive: true });
  const id = slugify(title);
  const slugDir = '00-' + slugify(title).slice(0, 40);
  const file = join(ARTICLES_DIR, category, slugDir, id + '.md');
  mkdirSync(dirname(file), { recursive: true });
  if (existsSync(file)) { console.error('[wiki] Article already exists:', file); process.exit(1); }

  if (articleType === 'video-script') {
    const content = `---
title: ${title}
duration: ~3min
style: 轻松
target_audience: 科普观众
---

# ${title}

## 开场（介绍研究背景）

[画面：封面图]

## 核心内容

[画面：相关图表]

## 总结

[画面：总结图]
`;
    writeFileSync(file, content);
    console.log('[wiki] Video script created:', file);
  } else {
    const tagLine = tags.length ? `\\ntags: [${tags.join(', ')}]` : '';
    writeFileSync(file,
`---
id: ${id}
title: ${title}
category: ${category}${tagLine}
created: ${new Date().toISOString()}
---

# ${title}

`
    );
    console.log('[wiki] Created:', file);
  }

  // Update index
  const idx = loadIndex();
  idx.articles.push({ id, title, category, file: `${category}/${slugDir}/${id}.md`, tags });
  if (!idx.categories.includes(category)) idx.categories.push(category);
  saveIndex(idx);

} else if (cmd === 'ingest') {
  const url = process.argv[3];
  if (!url) { console.log('Usage: node wiki.mjs ingest <arxiv-url>'); process.exit(1); }

  const idMatch = url.match(/(\\d+\\.\\d+)/);
  if (!idMatch) { console.error('[wiki] Invalid arXiv URL'); process.exit(1); }
  const id = idMatch[1];

  console.log('[wiki] Fetching arXiv', id, '...');
  const meta = await fetchArxivMeta(id);
  if (!meta) { console.error('[wiki] Failed to fetch metadata'); process.exit(1); }

  const slugDir = '00-' + slugify(meta.title).slice(0, 40);
  const category = meta.category || 'AI';
  mkdirSync(join(ARTICLES_DIR, category, slugDir), { recursive: true });
  const slug = slugify(meta.title);
  const file = join(ARTICLES_DIR, category, slugDir, slug + '.md');

  const tags = ['论文解读', meta.arxivId];
  const tagLine = `\\ntags: [${tags.join(', ')}]`;

  writeFileSync(file, `---
id: ${slug}
title: ${meta.title}
category: ${category}${tagLine}
arxiv: ${meta.arxivId}
created: ${new Date().toISOString()}
---

# ${meta.title}

**arXiv**: ${meta.arxivId} | **Author**: ${meta.authors}

## 摘要

${meta.abstract || '(暂无摘要)'}

## 研究动机

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）
`);

  // Update index
  const idx = loadIndex();
  idx.articles.push({ id: slug, title: meta.title, category, file: `${category}/${slugDir}/${slug}.md`, tags, arxiv: meta.arxivId });
  if (!idx.categories.includes(category)) idx.categories.push(category);
  saveIndex(idx);
  console.log('[wiki] Created:', file);

} else if (cmd === 'edit') {
  const title = process.argv[3];
  if (!title) { console.log('Usage: node wiki.mjs edit <title>'); process.exit(1); }
  const idx = loadIndex();
  const art = idx.articles.find(a => a.title.includes(title) || a.id.includes(title));
  if (!art) { console.error('[wiki] Article not found:', title); process.exit(1); }
  try {
    exec(`obsidian vault="3cb50ee5e304a7ea" open file="${art.file}"`, { stdio: 'inherit' });
    console.log('[wiki] Opened in Obsidian:', art.title);
  } catch { console.error('[wiki] Failed to open Obsidian'); }

} else if (cmd === 'sync') {
  const idx = loadIndex();
  const byCat = {};
  for (const a of idx.articles) byCat[a.category] = byCat[a.category] || [];
  for (const a of idx.articles) byCat[a.category].push(a);
  for (const [cat, arts] of Object.entries(byCat)) {
    const dir = join(ARTICLES_DIR, cat);
    if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  }
  saveIndex(idx);
  writeFileSync(INDEX_HTML, INDEX_HTML);
  console.log('\\n[wiki] Synced', idx.articles.length, 'articles');

} else if (cmd === 'search') {
  const query = process.argv[3];
  if (!query) { console.log('Usage: node wiki.mjs search <query>'); process.exit(1); }
  const q = query.toLowerCase();
  const idx = loadIndex();
  const results = idx.articles.filter(a =>
    a.title.toLowerCase().includes(q) ||
    (a.tags && a.tags.some(t => t.toLowerCase().includes(q)))
  );
  if (results.length === 0) { console.log('No results.'); process.exit(0); }
  results.forEach((a, i) => console.log('  ' + (i+1) + '. [' + a.category + '] ' + a.title));
  console.log('\\nTotal:', results.length);

} else if (cmd === 'list') {
  const idx = loadIndex();
  for (const cat of idx.categories) {
    const arts = idx.articles.filter(a => a.category === cat);
    console.log('\\n# ' + cat + ' (' + arts.length + ')\\n');
    arts.forEach(a => console.log('  - ' + a.title));
  }
  console.log('\\nTotal articles:', idx.articles.length);

} else if (cmd === 'linkcheck') {
  const idx = loadIndex();
  const byId = {};
  for (const a of idx.articles) byId[a.id] = a;
  let errors = 0;
  for (const a of idx.articles) {
    const file = join(ARTICLES_DIR, a.file);
    if (!existsSync(file)) continue;
    const content = readFileSync(file, 'utf8');
    const links = [...content.matchAll(/\\[\\[([^\\]]+)\\]\\]/g)].map(m => m[1]);
    for (const link of links) {
      const target = byId[link] || byId[link.replace(/\\s+/g, '-').toLowerCase()];
      if (!target) { console.log('  [BROKEN]', link, '-> in', a.title); errors++; }
    }
  }
  if (errors === 0) console.log('All links OK.');
  else console.log('\\nTotal broken:', errors);

} else if (cmd === 'backlinks') {
  const title = process.argv[3];
  if (!title) { console.log('Usage: node wiki.mjs backlinks <title>'); process.exit(1); }
  const idx = loadIndex();
  const art = idx.articles.find(a => a.title.includes(title) || a.id.includes(title));
  if (!art) { console.error('[wiki] Article not found:', title); process.exit(1); }
  const byId = {}; for (const a of idx.articles) byId[a.id] = a;
  const results = [];
  for (const a of idx.articles) {
    if (a.id === art.id) continue;
    const file = join(ARTICLES_DIR, a.file);
    if (!existsSync(file)) continue;
    const content = readFileSync(file, 'utf8');
    if (content.includes('[[' + art.title + ']]') || content.includes('[[' + art.id + ']]')) {
      results.push(a);
    }
  }
  if (results.length === 0) { console.log('No backlinks.'); }
  else { results.forEach(a => console.log('  - ' + a.title + ' [' + a.category + ']')); }

} else if (cmd === 'orphan') {
  const idx = loadIndex();
  const byId = {}; for (const a of idx.articles) byId[a.id] = a;
  const orphans = [];
  for (const a of idx.articles) {
    const file = join(ARTICLES_DIR, a.file);
    if (!existsSync(file)) { orphans.push(a); continue; }
    const content = readFileSync(file, 'utf8');
    let hasLink = false;
    for (const a2 of idx.articles) {
      if (a2.id === a.id) continue;
      if (content.includes('[[' + a2.title + ']]')) { hasLink = true; break; }
    }
    if (!hasLink) orphans.push(a);
  }
  if (orphans.length === 0) { console.log('No orphan articles.'); }
  else { orphans.forEach(a => console.log('  - ' + a.title + ' [' + a.id + ']')); }

} else if (cmd === 'scene-parse') {
  const scriptFile = process.argv[3];
  if (!scriptFile) { console.log('Usage: node wiki.mjs scene-parse <video-script.md>'); process.exit(1); }
  if (!existsSync(scriptFile)) { console.error('[wiki] File not found:', scriptFile); process.exit(1); }

  const content = readFileSync(scriptFile, 'utf8');
  const frontmatterMatch = content.match(/^---\\n([\\s\\S]+?)\\n---\\n/);
  if (!frontmatterMatch) { console.error('[wiki] No frontmatter found'); process.exit(1); }

  const frontmatter = frontmatterMatch[1];
  const titleMatch = frontmatter.match(/^title:\\s*(.+)$/m);
  const title = titleMatch ? titleMatch[1].trim() : 'Untitled';

  const body = content.slice(frontmatterMatch[0].length);
  const sceneBlocks = [];
  const sceneRegex = /\\[画面：([^\\]]+)\\]/g;
  let match;
  let lastEnd = 0;
  const textBlocks = [];

  while ((match = sceneRegex.exec(body)) !== null) {
    const pos = match.index;
    if (pos > lastEnd) {
      const text = body.slice(lastEnd, pos).trim();
      if (text) textBlocks.push(text);
    }
    sceneBlocks.push({ desc: match[1], textBefore: '' });
    lastEnd = match.index + match[0].length;
  }
  const remaining = body.slice(lastEnd).trim();
  if (remaining) textBlocks.push(remaining);

  // Assign text to scenes
  for (let i = 0; i < Math.min(sceneBlocks.length, textBlocks.length); i++) {
    sceneBlocks[i].textBefore = textBlocks[i] || '';
  }

  // Generate code
  const sceneKeys = [];
  for (let i = 0; i < sceneBlocks.length; i++) {
    const { desc, textBefore } = sceneBlocks[i];
    const keyName = 'scene_' + String(i + 1).padStart(2, '0');
    const funcName = 'draw_' + slugify(title).slice(0, 20) + '_' + String(i + 1).padStart(2, '0');
    sceneKeys.push({ key: keyName, desc, func: funcName, text: textBefore });
  }

  // Output
  const slug = slugify(title);
  console.log('\\n# Scene Parse:', title);
  console.log('\\n## Scene Keys (add to SCENE_DRAWERS):\\n');
  for (const { key, desc, func } of sceneKeys) {
    console.log("  '" + key + "': " + func + ',');
  }
  console.log('\\n## Generated Code (add to draw_scene.py):\\n');
  for (let i = 0; i < sceneKeys.length; i++) {
    const { key, desc, func, text } = sceneKeys[i];
    const code = generateSceneCode(i + 1, desc, func);
    console.log('# ' + (i + 1) + '. ' + desc);
    console.log(code);
    if (i < sceneKeys.length - 1) console.log('');
  }

} else {
  console.log(`Usage: node wiki.mjs <command>
Commands:
  create "<title>" [--category C] [--tags t1,t2] [--type video-script]
  ingest <arxiv-url>
  edit <title>
  sync
  search <query>
  list
  linkcheck
  backlinks <title>
  orphan
  scene-parse <video-script.md>
`);
}
'''

# Write the complete file
with open('wiki.mjs', 'w', encoding='utf-8') as f:
    f.write(WIKI_MJS)

print('wiki.mjs written, lines:', WIKI_MJS.count('\n'))
