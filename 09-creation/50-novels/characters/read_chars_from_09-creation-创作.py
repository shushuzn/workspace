import os

chars_dir = 'D:/OpenClaw/workspace/50-novels/characters'
output = []

for f in os.listdir(chars_dir):
    if f.endswith('.md'):
        path = os.path.join(chars_dir, f)
        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            output.append(f'=== {f} ===\n{content[:500]}\n\n')

with open('D:/OpenClaw/workspace/50-novels/characters/角色设定汇总.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print('OK')
