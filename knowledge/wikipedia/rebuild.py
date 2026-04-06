#!/usr/bin/env python3
"""Rebuild wiki.mjs - fix the broken INDEX_HTML template literal."""
import re, sys

with open('wiki.mjs', 'r', encoding='utf-8') as f:
    content = f.read()

# The INDEX_HTML section is broken - lines 68-71 have truncated template literals
# Let's find where INDEX_HTML starts and ends
idx_start = content.find('const INDEX_HTML = `')
idx_end = content.find('`;', idx_start + 20) + 2

old_html = content[idx_start:idx_end]
print(f"Old INDEX_HTML length: {len(old_html)}")
print(f"Old backtick count: {old_html.count('`')}")
print(f"First 100: {repr(old_html[:100])}")

# Rebuild proper INDEX_HTML
INDEX_HTML = '''const INDEX_HTML = `<!DOCTYPE html>
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
</html>`;'''

print(f"\nNew INDEX_HTML length: {len(INDEX_HTML)}")
print(f"New backtick count: {INDEX_HTML.count('`')}")

# Replace
new_content = content[:idx_start] + INDEX_HTML + content[idx_end:]

# Verify the new content has matching backticks in INDEX_HTML
test_section = new_content[new_content.find('const INDEX_HTML = `'):new_content.find('`;', new_content.find('const INDEX_HTML = `')+20)+2]
print(f"\nTest section backticks: {test_section.count('`')}")
print(f"Test section length: {len(test_section)}")

with open('wiki.mjs', 'w', encoding='utf-8') as f:
    f.write(new_content)
print("\nFile written successfully!")
