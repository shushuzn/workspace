import os

drafts_dir = 'D:/OpenClaw/workspace/50-novels/drafts'

# 找到第 1 章文件
chapter1_files = [f for f in os.listdir(drafts_dir) if f.startswith('第 1 章')]

print('第 1 章文件:')
for f in chapter1_files:
    print(f'  - {f}')

# 读取第一个文件
if chapter1_files:
    first_file = chapter1_files[0]
    path = os.path.join(drafts_dir, first_file)
    with open(path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    print(f'\n=== {first_file} 内容 (前 1000 字) ===\n')
    print(content[:1000])
