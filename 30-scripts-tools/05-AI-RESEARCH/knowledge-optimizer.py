#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识分布优化器
- 自动分类整理笔记
- 生成知识图谱索引
- 优化目录结构
- AI 分析热点话题
"""

import os
import json
from datetime import datetime
from pathlib import Path
import re

# ============ 代理配置 (Clash) ============
# 解决 Python 进程无法继承系统代理的问题
PROXY_ADDR = "http://127.0.0.1:7897"
os.environ['HTTP_PROXY'] = PROXY_ADDR
os.environ['HTTPS_PROXY'] = PROXY_ADDR
# ==========================================

VAULT_PATH = Path("D:/obsidian/Vault")
MEDIUM_PATH = VAULT_PATH / "Medium"
REDDIT_PATH = VAULT_PATH / "Reddit"
X_PATH = VAULT_PATH / "X-Twitter"
MEMORY_PATH = VAULT_PATH / "memory"

# 话题分类关键词
TOPIC_KEYWORDS = {
    "AI-ML": ["AI", "machine learning", "LLM", "neural", "deep learning", "GPT", "Claude", "transformer"],
    "Programming": ["python", "javascript", "code", "programming", "software", "dev", "API"],
    "Data-Science": ["data", "analytics", "visualization", "statistics", "pandas", "numpy"],
    "Cloud-DevOps": ["cloud", "AWS", "kubernetes", "docker", "devops", "infrastructure"],
    "Security": ["security", "privacy", "encryption", "hack", "vulnerability"],
    "Business": ["business", "startup", "investment", "market", "finance", "economy"],
    "Research": ["paper", "research", "arxiv", "academic", "study", "benchmark"],
    "Product": ["product", "launch", "feature", "release", "update"],
    "Ethics-Policy": ["ethics", "policy", "regulation", "government", "military", "ban"],
}

def analyze_content(filepath):
    """分析笔记内容，提取话题标签"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()[:2000]  # 只读前 2000 字符

        topics = []
        content_lower = content.lower()

        for topic, keywords in TOPIC_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    topics.append(topic)
                    break

        return topics
    except Exception as e:
        return ["Uncategorized"]

def generate_daily_index():
    """生成每日知识索引"""
    today = datetime.now().strftime("%Y-%m-%d")
    index_path = MEMORY_PATH / f"{today}-index.md"

    # 收集今日笔记
    today_notes = []
    for path in [MEDIUM_PATH, REDDIT_PATH, X_PATH]:
        if path.exists():
            for file in path.glob("*.md"):
                if file.stat().st_mtime > (datetime.now().timestamp() - 86400):
                    today_notes.append({
                        'name': file.name,
                        'path': file.relative_to(VAULT_PATH),
                        'source': path.name,
                        'size': file.stat().st_size
                    })

    # 按话题分类
    topic_groups = {}
    for note in today_notes:
        filepath = VAULT_PATH / note['path']
        topics = analyze_content(filepath)
        for topic in topics:
            if topic not in topic_groups:
                topic_groups[topic] = []
            topic_groups[topic].append(note)

    # 生成索引
    content = f"""# 📚 知识索引 - {today}

## 概览
- 总笔记数：{len(today_notes)}
- 话题分布：{len(topic_groups)} 个类别

## 话题分布

"""

    for topic, notes in sorted(topic_groups.items(), key=lambda x: -len(x[1])):
        content += f"### {topic} ({len(notes)}篇)\n\n"
        for note in notes[:5]:  # 只显示前 5 篇
            content += f"- [[{note['path']}]]\n"
        if len(notes) > 5:
            content += f"- ... 还有 {len(notes) - 5} 篇\n"
        content += "\n"

    content += f"""## 来源统计
- Medium: {len([n for n in today_notes if n['source'] == 'Medium'])}篇
- Reddit: {len([n for n in today_notes if n['source'] == 'Reddit'])}篇
- X-Twitter: {len([n for n in today_notes if n['source'] == 'X-Twitter'])}篇

---
*自动生成于 {datetime.now().strftime("%Y-%m-%d %H:%M")}*
"""

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return len(today_notes), topic_groups

def optimize_folder_structure():
    """优化文件夹结构"""
    # 创建话题子文件夹（如果不存在）
    for topic in TOPIC_KEYWORDS.keys():
        topic_dir = REDDIT_PATH / topic
        if not topic_dir.exists():
            topic_dir.mkdir(exist_ok=True)

    # 移动旧笔记到子文件夹（基于内容分析）
    moved_count = 0
    for file in REDDIT_PATH.glob("*.md"):
        if file.is_file():
            topics = analyze_content(file)
            if topics and topics[0] != "Uncategorized":
                # 只移动 7 天前的笔记
                if file.stat().st_mtime < (datetime.now().timestamp() - 604800):
                    target_dir = REDDIT_PATH / topics[0]
                    if target_dir.exists():
                        # 避免重复移动
                        if not (target_dir / file.name).exists():
                            file.rename(target_dir / file.name)
                            moved_count += 1

    return moved_count

def main():
    print("=" * 60)
    print("Knowledge Optimizer")
    print("=" * 60)

    # 生成每日索引
    print("\n[INFO] Generating daily knowledge index...")
    total_notes, topic_groups = generate_daily_index()
    print(f"   Notes processed: {total_notes}")
    print(f"   Topic categories: {len(topic_groups)}")

    for topic, notes in sorted(topic_groups.items(), key=lambda x: -len(x[1])):
        print(f"   - {topic}: {len(notes)} notes")

    # 优化文件夹结构
    print("\n[INFO] Optimizing folder structure...")
    moved = optimize_folder_structure()
    print(f"   Notes moved: {moved}")

    print("\n[SUCCESS] Optimization complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
