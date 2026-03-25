import os
import json

wb_dir = 'D:/OpenClaw/workspace/50-novels/world-building'
files = os.listdir(wb_dir)

# Find cognitive skill tree files
cog_files = [f for f in files if '认知' in f or '技能' in f]

result = {'files': cog_files, 'content': {}}

for f in cog_files:
    path = os.path.join(wb_dir, f)
    with open(path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    result['content'][f] = {
        'length': len(content),
        'first_500': content[:500]
    }

# Write to output file
with open('D:/OpenClaw/workspace/30-scripts/cognitive_system_dump.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"[OK] Dumped {len(cog_files)} files to cognitive_system_dump.json")
print(f"Files: {cog_files}")
