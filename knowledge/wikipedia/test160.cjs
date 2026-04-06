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





const require = createRequire(import.meta.url);
const __DIR = dirname(fileURLToPath(import.meta.url));
const INDEX_FILE = join(__DIR, 'index.json');
const ARTICLES_DIR = join(__DIR, 'articles');

const INDEX_HTML = `<!DOCTYPE html>
<html lang="zh">
<head><meta charset="UTF-8"><title>Wikipedia Knowledge Base</title>
<style>
  bodyfont-family:system-ui;max-width:900px;margin:2rem auto;padding:0 1rem;background:#f9f9f9
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