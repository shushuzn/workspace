import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync } from 'fs';
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
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_]+/g, '-')
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
    const title = (html.match(/<title>([^<]+)<\/title>/i) || [])[1] || '';
    const authors = (html.match(/<meta name="citation_authors" content="([^"]+)"/i) || [])[1] || '';
    const abstract = (html.match(/<meta name="citation_abstract" content="([^"]+)"/i) || [])[1] || '';
    const match = id.match(/(\d+\.\d+)/);
    const ver = match ? match[1] : id;
    if (!title) return null;
    return {
      title: title.replace(/\s+/g, ' ').trim(),
      authors: authors.replace(/\s+/g, ' ').trim(),
      abstract: abstract.replace(/\s+/g, ' ').trim(),
      arxivId: ver,
      category: 'AI',
    };
  } catch { return null; }
}

// ── Scene Parse ──────────────────────────────────────────────
// ── Scene Code Generator ──────────────────────────────────────────────────────
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
    const tagLine = tags.length ? `\ntags: [${tags.join(', ')}]` : '';
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

  const idMatch = url.match(/(\d+\.\d+)/);
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
  const tagLine = `\ntags: [${tags.join(', ')}]`;

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
  const rawArgs = process.argv.slice(3);
  const fuzzy = rawArgs.includes('--fuzzy') || rawArgs.includes('-f');
  const title = rawArgs.find(a => !a.startsWith('--'));
  if (!title) { console.log('Usage: node wiki.mjs edit <title> [--fuzzy]'); process.exit(1); }
  const idx = loadIndex();
  const exact = idx.articles.find(a => a.title.includes(title) || a.id.includes(title));
  if (fuzzy && !exact) {
    // fuzzy: rank by match score
    const q = title.toLowerCase();
    const scored = idx.articles.map(a => {
      const tl = a.title.toLowerCase();
      let score = 0;
      if (tl.includes(q)) score = 3;
      else if (tl.split(/\s+/).some(w => w.startsWith(q))) score = 2;
      else if (tl.includes(q.split(/\s+/)[0])) score = 1;
      return { art: a, score };
    }).filter(x => x.score > 0).sort((a, b) => b.score - a.score);
    if (scored.length === 0) { console.error('[wiki] Article not found:', title); process.exit(1); }
    console.log('[wiki] 找到', scored.length, '个候选:');
    scored.slice(0, 5).forEach((x, i) => console.log('  ' + (i+1) + '. [' + x.art.category + '] ' + x.art.title + '  (score=' + x.score + ')'));
    const pick = scored[0].art;
    try {
      exec(`obsidian vault="3cb50ee5e304a7ea" open file="${pick.file}"`, { stdio: 'inherit' });
      console.log('[wiki] Opened in Obsidian:', pick.title);
    } catch { console.error('[wiki] Failed to open Obsidian'); }
  } else {
    const art = exact || idx.articles.find(a => a.title.includes(title) || a.id.includes(title));
    if (!art) { console.error('[wiki] Article not found:', title); process.exit(1); }
    try {
      exec(`obsidian vault="3cb50ee5e304a7ea" open file="${art.file}"`, { stdio: 'inherit' });
      console.log('[wiki] Opened in Obsidian:', art.title);
    } catch { console.error('[wiki] Failed to open Obsidian'); }
  }

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
  console.log('\n[wiki] Synced', idx.articles.length, 'articles');

} else if (cmd === 'batch-export') {
  const args = process.argv.slice(3);
  const fromIdx = args.indexOf('--from');
  const toIdx = args.indexOf('--to');
  const outIdx = args.indexOf('--output');
  const from = fromIdx >= 0 ? args[fromIdx + 1] : null;
  const to = toIdx >= 0 ? args[toIdx + 1] : null;
  const outputDir = outIdx >= 0 ? args[outIdx + 1] : null;
  if (!outputDir) { console.log('Usage: node wiki.mjs batch-export --from YYYY-MM-DD --to YYYY-MM-DD --output DIR'); process.exit(1); }
  const { copyFileSync, mkdirSync, existsSync, readdirSync, statSync } = await import('fs');
  const { join, basename } = await import('path');
  function walkVideos(dir, results) {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const full = join(dir, entry.name);
      if (entry.isFile() && entry.name.endsWith('.mp4')) results.push(full);
      else if (entry.isDirectory()) walkVideos(full, results);
    }
  }
  const videos = []; walkVideos(join(__DIR, 'articles'), videos);
  const fromMs = from ? new Date(from).getTime() : 0;
  const toMs = to ? new Date(to + 'T23:59:59').getTime() : Infinity;
  if (!existsSync(outputDir)) mkdirSync(outputDir, { recursive: true });
  let copied = 0, skipped = 0;
  for (const v of videos) {
    const st = statSync(v);
    if (st.mtimeMs < fromMs || st.mtimeMs > toMs) { skipped++; continue; }
    try { copyFileSync(v, join(outputDir, basename(v))); console.log('[+] ' + basename(v)); copied++; }
    catch { skipped++; }
  }
  console.log('\nDone: copied=' + copied + ', skipped=' + skipped);

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
  console.log('\nTotal:', results.length);

} else if (cmd === 'list') {
  const idx = loadIndex();
  for (const cat of idx.categories) {
    const arts = idx.articles.filter(a => a.category === cat);
    console.log('\n# ' + cat + ' (' + arts.length + ')\n');
    arts.forEach(a => console.log('  - ' + a.title));
  }
  console.log('\nTotal articles:', idx.articles.length);

} else if (cmd === 'recent') {
  const limit = parseInt(process.argv[3]) || 20;
  const idx = loadIndex();
  const { readdirSync, statSync } = await import('fs');
  const { join, relative } = await import('path');
  const vaultDir = 'C:/Users/adm/Documents/Obsidian Vault';
  let files = [];
  try {
    function walk(dir) {
      const entries = readdirSync(dir, { withFileTypes: true });
      for (const e of entries) {
        const full = join(dir, e.name);
        if (e.isFile() && e.name.endsWith('.md')) files.push(full);
        else if (e.isDirectory() && !e.name.startsWith('.')) walk(full);
      }
    }
    walk(vaultDir);
  } catch {
    console.error('[wiki] Cannot read Obsidian vault directory');
    process.exit(1);
  }
  const withMtime = files.map(f => {
    try {
      const s = statSync(f);
      return { name: String(f), mtime: s.mtimeMs };
    } catch { return null; }
  }).filter(Boolean).sort((a, b) => b.mtime - a.mtime).slice(0, limit);
  withMtime.forEach((f, i) => {
    const date = new Date(f.mtime).toISOString().slice(0, 16).replace('T', ' ');
    const rel = relative(vaultDir, f.name);
    console.log((i+1) + '. [' + date + '] ' + rel);
  });
  console.log('\nTotal: ' + withMtime.length);

} else if (cmd === 'linkcheck') {
  const autoFix = process.argv.includes('--auto');
  const idx = loadIndex();
  const byId = {};
  for (const a of idx.articles) byId[a.id] = a;
  let errors = 0;
  const fixes = [];
  for (const a of idx.articles) {
    const file = join(ARTICLES_DIR, a.file);
    if (!existsSync(file)) continue;
    const content = readFileSync(file, 'utf8');
    const links = [...content.matchAll(/\[\[([^\]]+)\]\]/g)].map(m => m[1]);
    for (const link of links) {
      const target = byId[link] || byId[link.replace(/\s+/g, '-').toLowerCase()];
      if (!target) {
        console.log('  [BROKEN]', link, '-> in', a.title);
        errors++;
        if (autoFix) {
          // Try to find closest matching article id
          const linkLower = link.toLowerCase().replace(/\s+/g, '-');
          let bestMatch = null;
          for (const id of Object.keys(byId)) {
            if (id.includes(linkLower) || linkLower.includes(id)) {
              bestMatch = id;
              break;
            }
          }
          if (bestMatch) {
            const newContent = content.replace(/\[\[" + link + "\]\]/, '[[' + bestMatch + ']]');
            writeFileSync(file, newContent, 'utf8');
            fixes.push({ file: a.file, from: link, to: bestMatch });
          }
        }
      }
    }
  }
  if (errors === 0) console.log('All links OK.');
  else {
    console.log('\nTotal broken:', errors);
    if (autoFix && fixes.length > 0) {
      console.log('\nAuto-fixed:', fixes.length);
      for (const f of fixes) console.log('  ', f.file, ':', f.from, '->', f.to);
    } else if (autoFix) {
      console.log('  No auto-fix candidates found.');
    }
  }

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
  const frontmatterMatch = content.match(/^---\n([\s\S]+?)\n---\n/);
  if (!frontmatterMatch) { console.error('[wiki] No frontmatter found'); process.exit(1); }

  const frontmatter = frontmatterMatch[1];
  const titleMatch = frontmatter.match(/^title:\s*(.+)$/m);
  const title = titleMatch ? titleMatch[1].trim() : 'Untitled';

  const body = content.slice(frontmatterMatch[0].length);
  const sceneBlocks = [];
  const sceneRegex = /\[画面：([^\]]+)\]/g;
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
  console.log('\n# Scene Parse:', title);
  console.log('\n## Scene Keys (add to SCENE_DRAWERS):\n');
  for (const { key, desc, func } of sceneKeys) {
    console.log("  '" + key + "': " + func + ',');
  }
  console.log('\n## Generated Code (add to draw_scene.py):\n');
  for (let i = 0; i < sceneKeys.length; i++) {
    const { key, desc, func, text } = sceneKeys[i];
    const code = generateSceneCode(i + 1, desc, func);
    console.log('# ' + (i + 1) + '. ' + desc);
    console.log(code);
    if (i < sceneKeys.length - 1) console.log('');
  }

} else if (cmd === 'scene-parse') {
  const scriptFile = process.argv[3];
  if (!scriptFile) { console.log('Usage: node wiki.mjs scene-parse <video-script.md>'); process.exit(1); }
  if (!existsSync(scriptFile)) { console.error('[wiki] File not found:', scriptFile); process.exit(1); }

  const content = readFileSync(scriptFile, 'utf8');
  const frontmatterMatch = content.match(/^---\n([\s\S]+?)\n---\n/);
  if (!frontmatterMatch) { console.error('[wiki] No frontmatter found'); process.exit(1); }

  const frontmatter = frontmatterMatch[1];
  const titleMatch = frontmatter.match(/^title:\s*(.+)$/m);
  const title = titleMatch ? titleMatch[1].trim() : 'Untitled';

  const body = content.slice(frontmatterMatch[0].length);
  const sceneBlocks = [];
  const sceneRegex = /\[画面：([^\]]+)\]/g;
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
  console.log('\n# Scene Parse:', title);
  console.log('\n## Scene Keys (add to SCENE_DRAWERS):\n');
  for (const { key, desc, func } of sceneKeys) {
    console.log("  '" + key + "': " + func + ',');
  }
  console.log('\n## Generated Code (add to draw_scene.py):\n');
  for (let i = 0; i < sceneKeys.length; i++) {
    const { key, desc, func, text } = sceneKeys[i];
    const code = generateSceneCode(i + 1, desc, func);
    console.log('# ' + (i + 1) + '. ' + desc);
    console.log(code);
    if (i < sceneKeys.length - 1) console.log('');
  }

} else if (cmd === 'video-pipeline') {
  // 视频流水线优化版：node wiki.mjs video-pipeline [--force] [--resume] [--workers N] [--batch N]
  const [_, __, forceFlag, resumeFlag, workersFlag, batchFlag] = process.argv;
  const force = forceFlag === '--force';
  const resume = resumeFlag === '--resume';
  const workers = workersFlag?.startsWith('--workers=') ? parseInt(workersFlag.split('=')[1]) : 4;
  const batch = batchFlag?.startsWith('--batch=') ? parseInt(batchFlag.split('=')[1]) : 5;

  // 调用 pipeline.py
  const { spawn } = await import('child_process');
  const pipelinePy = join(__DIR, 'video', 'pipeline.py');
  const args = ['--workers', workers, '--batch', batch];
  if (force) args.push('--force');
  if (resume) args.push('--resume');

  const py = spawn(sys.executable, [pipelinePy, ...args], { stdio: 'inherit' });
  py.on('close', code => process.exit(code));

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
  orphan
  scene-parse <video-script.md>
  video-pipeline [--force] [--resume] [--workers=N] [--batch=N]
`);
}
