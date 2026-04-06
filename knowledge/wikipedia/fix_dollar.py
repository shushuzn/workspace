f=open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki.mjs','r',encoding='utf-8')
c=f.read()
f.close()
lines=c.splitlines()

# The generateSceneCode block spans ~line 183 to ~line 300
# Find the function boundaries
start=None; end=None
for i,l in enumerate(lines):
    if 'function generateSceneCode' in l: start=i
    if start is not None and l.strip() == '}' and i > start: end=i; break

if start is None: print("ERROR: generateSceneCode function not found"); exit(1)
print(f"Function: lines {start+1}-{end+1}")

# Write correct function as pure Python raw string (no escaping issues)
gen = r"""// ── Scene Code Generator ──────────────────────────────────────────────────────
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

  if (figType === 'cover') {
    return `def ${funcName}(fig, ax):\n    ax.clear()\n    ax.set_xlim(0, 12)\n    ax.set_ylim(0, 8)\n    ax.axis('off')\n    ax.text(6, 4.5, "${desc}", ha='center', va='center', fontsize=24, fontweight='bold', wrap=True)`;
  } else if (figType === 'network') {
    return `def ${funcName}(fig, ax):\n    ax.clear()\n    ax.set_xlim(0, 12)\n    ax.set_ylim(0, 8)\n    ax.axis('off')\n    ax.text(0.5, 7.5, "[${n}] ${desc}", fontsize=11, color='#444')\n    draw_iam_graph(ax, "${desc}")`;
  } else if (figType === 'comparison') {
    return `def ${funcName}(fig, ax):\n    ax.clear()\n    ax.set_xlim(0, 12)\n    ax.set_ylim(0, 8)\n    ax.axis('off')\n    ax.text(0.5, 7.5, "[${n}] ${desc}", fontsize=11, color='#444')\n    draw_comparison(fig, ax, "${desc}")`;
  } else if (figType === 'pipeline') {
    return `def ${funcName}(fig, ax):\n    ax.clear()\n    ax.set_xlim(0, 12)\n    ax.set_ylim(0, 8)\n    ax.axis('off')\n    ax.text(0.5, 7.5, "[${n}] ${desc}", fontsize=11, color='#444')\n    draw_burau_pipeline(ax, "${desc}")`;
  } else if (figType === 'math') {
    return `def ${funcName}(fig, ax):\n    ax.clear()\n    ax.set_xlim(0, 12)\n    ax.set_ylim(0, 8)\n    ax.axis('off')\n    ax.text(0.5, 7.5, "[${n}] ${desc}", fontsize=11, color='#444')\n    ax.text(6, 4, "${desc}", ha='center', va='center', fontsize=16, style='italic')`;
  } else if (figType === 'transfer') {
    return `def ${funcName}(fig, ax):\n    ax.clear()\n    ax.set_xlim(0, 12)\n    ax.set_ylim(0, 8)\n    ax.axis('off')\n    ax.text(0.5, 7.5, "[${n}] ${desc}", fontsize=11, color='#444')\n    draw_transfer_diagram(ax, "${desc}")`;
  } else if (figType === 'attack') {
    return `def ${funcName}(fig, ax):\n    ax.clear()\n    ax.set_xlim(0, 12)\n    ax.set_ylim(0, 8)\n    ax.axis('off')\n    ax.text(0.5, 7.5, "[${n}] ${desc}", fontsize=11, color='#444')\n    draw_attack_path(ax, "${desc}")`;
  } else if (figType === 'formula') {
    return `def ${funcName}(fig, ax):\n    ax.clear()\n    ax.set_xlim(0, 12)\n    ax.set_ylim(0, 8)\n    ax.axis('off')\n    ax.text(0.5, 7.5, "[${n}] ${desc}", fontsize=11, color='#444')\n    ax.text(6, 4, "LE = ${desc}", ha='center', va='center', fontsize=14, color='#1a1a2e')`;
  } else {
    return `def ${funcName}(fig, ax):\n    ax.clear()\n    ax.set_xlim(0, 12)\n    ax.set_ylim(0, 8)\n    ax.axis('off')\n    ax.text(6, 4, "${desc}", ha='center', va='center', fontsize=14, wrap=True)`;
  }
}
"""

new_lines = lines[:start] + gen.split('\n') + lines[end+1:]
with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki.mjs','w',encoding='utf-8') as f:
    f.write('\n'.join(new_lines))
print(f'Done: {len(new_lines)} lines')
