"""Fix draw_scene.py: replace all hardcoded savefig paths with out_path param"""
import re

path = r'D:\OpenClaw\workspace\knowledge\wikipedia\video\draw_scene.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all plt.savefig('video/XXX.png', ...) with out_path
pattern = r"plt\.savefig\('video/[^']+\.png', dpi=150, bbox_inches='tight', facecolor=COLORS\['bg'\]\)"
replacement = "plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])"
new_content = re.sub(pattern, replacement, content)

count_before = len(re.findall(r"plt\.savefig\('video/", content))
count_after = len(re.findall(r"plt\.savefig\('video/", new_content))
print(f'Before: {count_before} hardcoded, After: {count_after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Saved')
