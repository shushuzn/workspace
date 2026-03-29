#!/usr/bin/env python3
"""解析 OpenClaw 技能列表"""

import os
import re

# 解析所有分类文件中的技能链接
skills = []
categories_dir = 'temp-skills-repo/categories'

for filename in os.listdir(categories_dir):
    if filename.endswith('.md'):
        filepath = os.path.join(categories_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配技能链接格式: [技能名](https://clawskills.sh/skills/作者-技能名)
        matches = re.findall(r'\[([^\]]+)\]\(https://clawskills\.sh/skills/([^)]+)\)', content)
        for name, slug in matches:
            skills.append({'name': name, 'slug': slug, 'category': filename.replace('.md', '')})

print(f'总共找到: {len(skills)} 个技能')

# 按分类统计
categories = {}
for s in skills:
    cat = s['category']
    if cat not in categories:
        categories[cat] = 0
    categories[cat] += 1

print('\n分类统计:')
for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
    print(f'  {cat}: {count}')

# 保存到文件
with open('all-skills-list.txt', 'w', encoding='utf-8') as f:
    f.write('slug|name|category\n')
    for s in skills:
        f.write(f"{s['slug']}|{s['name']}|{s['category']}\n")

print(f'\n已保存到 all-skills-list.txt')