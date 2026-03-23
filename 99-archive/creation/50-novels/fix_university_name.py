import os

# 需要替换的内容
replacements = {
    '清华': '华夏',
    '清华大学': '华夏大学',
}

# 需要修改的文件
files = [
    'D:/OpenClaw/workspace/50-novels/15-docs/第二卷 101-200 章详细大纲.md',
    'D:/OpenClaw/workspace/50-novels/characters/CHAR_陈舟_女主角_2026-03-10_v1.0.md',
]

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for old, new in replacements.items():
        content = content.replace(old, new)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print('OK: ' + file_path)

print('Done! All replaced.')
