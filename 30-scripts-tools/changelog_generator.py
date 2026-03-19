#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Changelog Generator - 变更日志生成器

从 Git 历史自动生成 CHANGELOG.md
"""

import os
import subprocess
import re
from datetime import datetime
from collections import defaultdict

WORKSPACE = "D:\\OpenClaw\\workspace"

def get_git_log():
    """获取 Git 提交历史"""
    try:
        result = subprocess.run(
            ['git', 'log', '--pretty=format:%H|%ai|%s|%b', '--no-merges'],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            print(f"Git 错误：{result.stderr}")
            return []
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                parts = line.split('|', 3)
                if len(parts) >= 3:
                    commit = {
                        'hash': parts[0][:7],
                        'date': parts[1][:10],
                        'message': parts[2],
                        'body': parts[3] if len(parts) > 3 else ''
                    }
                    commits.append(commit)
        
        return commits
    except Exception as e:
        print(f"获取 Git 历史失败：{e}")
        return []

def categorize_commits(commits):
    """分类提交"""
    categories = defaultdict(list)
    
    for commit in commits:
        msg = commit['message'].lower()
        
        # 根据提交信息分类
        if msg.startswith('feat:') or 'add' in msg or 'new' in msg:
            categories['Features'].append(commit)
        elif msg.startswith('fix:') or 'fix' in msg or 'bug' in msg:
            categories['Bug Fixes'].append(commit)
        elif msg.startswith('docs:') or 'doc' in msg or 'readme' in msg:
            categories['Documentation'].append(commit)
        elif msg.startswith('refactor:') or 'refactor' in msg:
            categories['Refactoring'].append(commit)
        elif msg.startswith('perf:') or 'performance' in msg or 'optimize' in msg:
            categories['Performance'].append(commit)
        elif msg.startswith('test:') or 'test' in msg:
            categories['Tests'].append(commit)
        elif msg.startswith('chore:') or 'chore' in msg or 'config' in msg:
            categories['Chores'].append(commit)
        else:
            categories['Other'].append(commit)
    
    return categories

def generate_changelog(commits, categories):
    """生成变更日志"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    changelog = f"""# 📝 变更日志 (CHANGELOG)

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**项目:** OpenClaw Workspace  
**总提交数:** {len(commits)}

---

## [{today}] - Latest

"""
    
    # 按类别组织
    category_order = ['Features', 'Bug Fixes', 'Refactoring', 'Performance', 'Documentation', 'Tests', 'Chores', 'Other']
    category_names = {
        'Features': '✨ 新功能',
        'Bug Fixes': '🐛 修复',
        'Refactoring': '♻️ 重构',
        'Performance': '⚡ 性能优化',
        'Documentation': '📚 文档',
        'Tests': '✅ 测试',
        'Chores': '🔧 杂项',
        'Other': '📦 其他'
    }
    
    for category in category_order:
        if category not in categories:
            continue
        
        commits_list = categories[category]
        if not commits_list:
            continue
        
        changelog += f"### {category_names.get(category, category)}\n\n"
        
        for commit in commits_list[:20]:  # 每个类别最多显示 20 个
            date = commit['date']
            hash_short = commit['hash']
            message = commit['message']
            
            # 清理消息
            message = re.sub(r'^(feat|fix|docs|refactor|perf|test|chore):\s*', '', message)
            message = message[0].upper() + message[1:]
            
            changelog += f"- {message} ([`{hash_short}`](https://github.com/shushuzn/workspace/commit/{hash_short})) - {date}\n"
        
        changelog += "\n"
    
    # 统计信息
    changelog += f"""---

## 📊 统计信息

- **总提交数:** {len(commits)}
- **新功能:** {len(categories.get('Features', []))}
- **修复:** {len(categories.get('Bug Fixes', []))}
- **文档:** {len(categories.get('Documentation', []))}
- **重构:** {len(categories.get('Refactoring', []))}
- **性能优化:** {len(categories.get('Performance', []))}

---

*本变更日志由 changelog_generator.py 自动生成*
"""
    
    return changelog

def main():
    """主函数"""
    print("=" * 60)
    print("Changelog Generator v1.0 - 变更日志生成器")
    print("=" * 60)
    
    # 获取 Git 历史
    print("\n[1/3] 获取 Git 提交历史...")
    commits = get_git_log()
    print(f"✅ 获取到 {len(commits)} 个提交")
    
    if not commits:
        print("⚠️ 没有找到提交记录")
        return
    
    # 分类提交
    print("\n[2/3] 分类提交...")
    categories = categorize_commits(commits)
    for cat, items in categories.items():
        print(f"  - {cat}: {len(items)}")
    
    # 生成变更日志
    print("\n[3/3] 生成变更日志...")
    changelog = generate_changelog(commits, categories)
    
    # 保存
    changelog_path = os.path.join(WORKSPACE, "CHANGELOG.md")
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(changelog)
    
    print(f"\n✅ 已保存：{changelog_path}")
    
    print("\n" + "=" * 60)
    print("✅ 变更日志生成完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()
