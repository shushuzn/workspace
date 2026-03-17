#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collaboration Network Builder v1
协作网络构建 - 合作者推荐
"""

import json
from datetime import datetime
from pathlib import Path

# 配置
OUTPUT_DIR = Path(r"D:\obsidian\Vault\AI-Research\Collaboration-Network")

def build_author_graph():
    """构建作者关系图谱 (简化版)"""
    # 实际应从论文元数据构建
    authors = {
        'Author_A': {
            'papers': 10,
            'citations': 500,
            'topics': ['Agentic AI', 'MCP'],
            'institution': 'Stanford'
        },
        'Author_B': {
            'papers': 8,
            'citations': 300,
            'topics': ['Efficiency', 'RLHF'],
            'institution': 'MIT'
        },
        'Author_C': {
            'papers': 15,
            'citations': 800,
            'topics': ['Agentic AI', 'Planning'],
            'institution': 'Berkeley'
        },
    }
    
    # 合著关系
    coauthorships = [
        ('Author_A', 'Author_C', 3),  # 合著 3 篇
        ('Author_B', 'Author_C', 1),
    ]
    
    return authors, coauthorships

def recommend_collaborators(target_author, authors, coauthorships):
    """推荐合作者"""
    recommendations = []
    
    target_topics = set(authors.get(target_author, {}).get('topics', []))
    
    for author, data in authors.items():
        if author == target_author:
            continue
        
        # 计算主题重叠
        author_topics = set(data.get('topics', []))
        topic_overlap = len(target_topics & author_topics)
        
        # 计算互补性
        topic_complement = len(target_topics | author_topics)
        
        # 检查是否已有合作
        existing_collab = sum(1 for c in coauthorships if (c[0] == target_author and c[1] == author) or (c[1] == target_author and c[0] == author))
        
        # 推荐分数
        score = (topic_overlap * 2 + topic_complement) / (1 + existing_collab * 5)
        
        if score > 1.5:  # 阈值
            recommendations.append({
                'author': author,
                'institution': data.get('institution', 'Unknown'),
                'topics': data.get('topics', []),
                'score': round(score, 2),
                'reason': f"主题重叠：{topic_overlap}, 互补性：{topic_complement}"
            })
    
    # 按分数排序
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations

def save_collaboration_network(recommendations, target_author):
    """保存协作网络"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    filename = f"collaborators-{target_author}-{date_str}.md"
    filepath = OUTPUT_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# 合作者推荐 - @{target_author}\n\n")
        f.write(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**推荐数量:** {len(recommendations)}\n\n")
        f.write("---\n\n")
        
        if recommendations:
            f.write("## 🤝 推荐合作者\n\n")
            for i, rec in enumerate(recommendations, 1):
                f.write(f"### {i}. {rec['author']}\n\n")
                f.write(f"**机构:** {rec['institution']}\n")
                f.write(f"**研究方向:** {', '.join(rec['topics'])}\n")
                f.write(f"**推荐分数:** {rec['score']:.2f}\n")
                f.write(f"**理由:** {rec['reason']}\n\n")
                f.write("---\n\n")
        else:
            f.write("暂无推荐合作者\n")
    
    print(f"[OK] Saved {len(recommendations)} recommendations for {target_author}")
    return filepath

def build_network():
    """构建协作网络"""
    print("=" * 60)
    print("Collaboration Network Builder v1")
    print("=" * 60)
    
    # 1. 构建作者图谱
    print("\n[1/3] Building author graph...")
    authors, coauthorships = build_author_graph()
    print(f"  Authors: {len(authors)}")
    print(f"  Co-authorships: {len(coauthorships)}")
    
    # 2. 推荐合作者
    print("\n[2/3] Recommending collaborators...")
    all_recommendations = []
    for author in authors.keys():
        recs = recommend_collaborators(author, authors, coauthorships)
        all_recommendations.extend(recs)
        print(f"  {author}: {len(recs)} recommendations")
    
    # 3. 保存结果
    print("\n[3/3] Saving collaboration network...")
    for author in authors.keys():
        recs = recommend_collaborators(author, authors, coauthorships)
        save_collaboration_network(recs, author)
    
    print("-" * 60)
    print(f"[COMPLETE] Generated {len(all_recommendations)} total recommendations")
    print("=" * 60)
    
    return all_recommendations

if __name__ == "__main__":
    build_network()
