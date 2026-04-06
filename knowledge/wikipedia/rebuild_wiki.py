#!/usr/bin/env python3
"""Rebuild wiki.mjs cleanly: fix INDEX_HTML, add generateSceneCode."""
import os
os.chdir(r'D:\OpenClaw\workspace\knowledge\wikipedia')

with open('wiki.mjs', 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

# 1. Find INDEX_HTML boundaries
html_start = None
for i, l in enumerate(lines):
    if "const INDEX_HTML = `" in l:
        html_start = i
        break

# Find the line after the opening backtick
print(f"html_start line {html_start+1}")

# Find where the inner ${cat} etc appear - lines 66-72
# The problem lines are 66-76 which contain ${ expressions
# Strategy: keep everything up to line 65, replace lines 66-76 with concatenation approach

# Find the closing `; line after </html>`
html_end = None
for i in range(html_start+1, len(lines)):
    if lines[i].strip() == '`;':
        html_end = i
        break

print(f"html_end line {html_end+1}")

# Build replacement for lines 66-76 (0-indexed 65-75)
# We replace the broken template literal content with string concatenation
# Lines before broken section (1-65), broken lines (66-76), after (77+)
before = '\n'.join(lines[:65])
broken_end = html_end  # line index where `; is
after = '\n'.join(lines[broken_end+1:])

# The fixed content using simple string concatenation
fixed_middle = """  document.getElementById('content').innerHTML=cats.map(cat=>{
    const catArts=filtered.filter(a=>a.category===cat);
    return '<div class="cat"><h2>'+cat+' ('+catArts.length+')</h2>'+catArts.map(a=>
      '<div class="art'+(a.orphan?' orphan':'')+'><a href="/'+a.id+'">'+a.title+'</a>'+
      (a.tags&&a.tags.length?'<div class="tags">'+a.tags.map(t=>'<span class="tag">'+t+'</span>').join('')+'</div>':'')+'</div>'
    ).join('')+'</div>';
  }).join('');"""

new_content = before + '\n' + fixed_middle + '\n' + after

# 2. Now add generateSceneCode before the Commands section
# Find the Commands section marker
cmd_marker = None
for i, l in enumerate(new_content.splitlines()):
    if '// ── Commands ──' in l:
        cmd_marker = i
        break

gen_code = """
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
  const d = desc.replace(/"/g, '\\\\"');
  let code = 'def ' + funcName + '(fig, ax):\\n';
  code += '    ax.clear()\\n    ax.set_xlim(0, 12)\\n    ax.set_ylim(0, 8)\\n    ax.axis("off")\\n';
  if (figType === 'network') {
    code += '    ax.text(0.5, 7.5, "["+' + 'n' + '+"] ' + d + '", fontsize=11, color="#444")\\n';
    code += '    draw_iam_graph(ax, "' + d + '")';
  } else if (figType === 'comparison') {
    code += '    ax.text(0.5, 7.5, "["+' + 'n' + '+"] ' + d + '", fontsize=11, color="#444")\\n';
    code += '    draw_comparison(fig, ax, "' + d + '")';
  } else if (figType === 'pipeline') {
    code += '    ax.text(0.5, 7.5, "["+' + 'n' + '+"] ' + d + '", fontsize=11, color="#444")\\n';
    code += '    draw_burau_pipeline(ax, "' + d + '")';
  } else if (figType === 'math') {
    code += '    ax.text(0.5, 7.5, "["+' + 'n' + '+"] ' + d + '", fontsize=11, color="#444")\\n';
    code += '    ax.text(6, 4, "' + d + '", ha="center", va="center", fontsize=16, style="italic")';
  } else if (figType === 'transfer') {
    code += '    ax.text(0.5, 7.5, "["+' + 'n' + '+"] ' + d + '", fontsize=11, color="#444")\\n';
    code += '    draw_transfer_diagram(ax, "' + d + '")';
  } else if (figType === 'attack') {
    code += '    ax.text(0.5, 7.5, "["+' + 'n' + '+"] ' + d + '", fontsize=11, color="#444")\\n';
    code += '    draw_attack_path(ax, "' + d + '")';
  } else if (figType === 'formula') {
    code += '    ax.text(0.5, 7.5, "["+' + 'n' + '+"] ' + d + '", fontsize=11, color="#444")\\n';
    code += '    ax.text(6, 4, "LE = ' + d + '", ha="center", va="center", fontsize=14, color="#1a1a2e")';
  } else if (figType === 'cover') {
    code += '    ax.text(6, 4.5, "' + d + '", ha="center", va="center", fontsize=24, fontweight="bold")';
  } else {
    code += '    ax.text(6, 4, "' + d + '", ha="center", va="center", fontsize=14)';
  }
  return code;
}
"""

parts = new_content.splitlines(keepends=True)
# Insert gen_code before the Commands line
cmds_idx = None
for i, l in enumerate(parts):
    if '// ── Commands ──' in l:
        cmds_idx = i
        break

result = parts[:cmds_idx] + [gen_code + '\n'] + parts[cmds_idx:]
final = ''.join(result)

with open('wiki.mjs', 'w', encoding='utf-8') as f:
    f.write(final)

print(f"Done: {len(final.splitlines())} lines")
