#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collaboration Recommender v1
合作者推荐系统
"""

import json
from datetime import datetime
from pathlib import Path

# 配置
OUTPUT_DIR = Path(r"D:\obsidian\Vault\AI-Research\Collaboration-Recs")

def build_citation_network():
    """构建引用网络 (简化版)"""
    return {
        'authors': {
            'Author_A': {'papers': 10, 'citations': 500, 'topics': ['Agentic AI', 'MCP']},
            'Author_B': {'papers': 8, 'citations': 300, 'topics': ['Efficiency', 'RLHF']},
            'Author_C': {'papers': 15, 'citations': 800, 'topics': ['Agentic AI', 'Planning']},
        },
        'citations': [
            ('Author_A', 'Author_C', 5),
            ('Author_B', 'Author_C', 2),
        ]
    }

def recommend_collaborators(target_author, network):
    """推荐合作者"""
    recs = []
    target_topics = set(network['authors'].get(target_author, {}).get('topics', []))

    for author, data in network['authors'].items():
        if author == target_author:
            continue

        author_topics = set(data.get('topics', []))
        overlap = len(target_topics & author_topics)
        complement = len(target_topics | author_topics)

        score = overlap * 2 + complement
        if score > 3:
            recs.append({
                'author': author,
                'score': round(score, 2),
                'topics': data['topics'],
                'reason': f"主题重叠：{overlap}, 互补：{complement}"
            })

    recs.sort(key=lambda x: x['score'], reverse=True)
    return recs

def save_recommendations(target_author, recs):
    """保存推荐结果"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    md_file = OUTPUT_DIR / f"collaborators-{target_author}-{date_str}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# 合作者推荐 - @{target_author}\n\n")
        f.write(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        if recs:
            f.write("## 🤝 推荐合作者\n\n")
            for i, rec in enumerate(recs, 1):
                f.write(f"### {i}. {rec['author']}\n\n")
                f.write(f"**研究方向:** {', '.join(rec['topics'])}\n")
                f.write(f"**推荐分数:** {rec['score']:.2f}\n")
                f.write(f"**理由:** {rec['reason']}\n\n")
                f.write("---\n\n")
        else:
            f.write("暂无推荐\n")

    print(f"[OK] Saved {len(recs)} recommendations for {target_author}")
    return md_file

def recommend():
    """主流程"""
    print("=" * 60)
    print("Collaboration Recommender v1")
    print("=" * 60)

    print("\n[1/3] Building citation network...")
    network = build_citation_network()
    print(f"  Authors: {len(network['authors'])}")

    print("\n[2/3] Generating recommendations...")
    all_recs = []
    for author in network['authors'].keys():
        recs = recommend_collaborators(author, network)
        all_recs.extend(recs)
        save_recommendations(author, recs)

    print("\n[3/3] Summary...")
    print(f"  Total recommendations: {len(all_recs)}")

    print("-" * 60)
    print("[COMPLETE]")
    print("=" * 60)

if __name__ == "__main__":
    recommend()
