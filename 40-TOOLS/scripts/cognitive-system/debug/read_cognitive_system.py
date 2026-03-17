import os

wb_dir = 'D:/OpenClaw/workspace/50-novels/world-building'
files = os.listdir(wb_dir)

print("Files in world-building:")
for i, f in enumerate(files):
    print(f"{i}: {f}")

# Read the cognitive skill tree file (index 2 or 3 based on earlier output)
for f in files:
    if '认知' in f or '技能' in f:
        path = os.path.join(wb_dir, f)
        print(f"\n=== Reading {f} ===")
        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        print(f"Length: {len(content)} chars")
        print(content[:1500])
        break
