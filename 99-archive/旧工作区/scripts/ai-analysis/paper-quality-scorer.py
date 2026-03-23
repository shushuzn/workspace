#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paper Quality Scorer v1
论文质量 AI 评分系统
"""

import json
from datetime import datetime
from pathlib import Path

# 配置
OUTPUT_DIR = Path(r"D:\obsidian\Vault\AI-Research\Paper-Scores")

# 评分标准
SCORING_CRITERIA = {
    'innovation': {
        'name': '创新性',
        'weight': 0.35,
        'indicators': [
            '提出新方法/框架',
            '解决开放性问题',
            '跨领域融合',
            '理论突破'
        ]
    },
    'impact': {
        'name': '影响力',
        'weight': 0.30,
        'indicators': [
            '引用潜力',
            '实用价值',
            '社区关注度',
            '可复现性'
        ]
    },
    'methodology': {
        'name': '方法严谨性',
        'weight': 0.25,
        'indicators': [
            '实验设计',
            '对比基线',
            '统计分析',
            '局限性讨论'
        ]
    },
    'clarity': {
        'name': '表达清晰度',
        'weight': 0.10,
        'indicators': [
            '结构清晰',
            '图表质量',
            '写作流畅',
            '可理解性'
        ]
    }
}

def calculate_score(paper_metadata):
    """计算论文综合评分"""
    scores = {}
    total_score = 0

    for criterion_id, criterion in SCORING_CRITERIA.items():
        # 简化版：基于关键词匹配评分
        score = 0.7  # 默认分
        title = paper_metadata.get('title', '').lower()
        abstract = paper_metadata.get('abstract', '').lower()

        # 检查指标关键词
        for indicator in criterion['indicators']:
            if indicator.lower() in title or indicator.lower() in abstract:
                score += 0.1

        score = min(1.0, score)  # 上限 1.0
        scores[criterion_id] = round(score, 2)
        total_score += score * criterion['weight']

    return {
        'overall': round(total_score, 2),
        'breakdown': scores,
        'level': get_score_level(total_score)
    }

def get_score_level(score):
    """评分等级"""
    if score >= 0.85:
        return 'S'  # 顶级
    elif score >= 0.70:
        return 'A'  # 优秀
    elif score >= 0.55:
        return 'B'  # 良好
    elif score >= 0.40:
        return 'C'  # 一般
    else:
        return 'D'  # 较低

def score_papers(papers):
    """批量评分"""
    results = []

    for paper in papers:
        score_result = calculate_score(paper)
        results.append({
            'arxiv_id': paper.get('arxiv_id', 'unknown'),
            'title': paper.get('title', '')[:100],
            'score': score_result['overall'],
            'level': score_result['level'],
            'breakdown': score_result['breakdown']
        })

    # 按评分排序
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

def save_scores(results):
    """保存评分结果"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 保存为 JSON
    json_file = OUTPUT_DIR / f"paper-scores-{date_str}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'date': date_str,
            'total_papers': len(results),
            'score_distribution': {
                'S': len([r for r in results if r['level'] == 'S']),
                'A': len([r for r in results if r['level'] == 'A']),
                'B': len([r for r in results if r['level'] == 'B']),
                'C': len([r for r in results if r['level'] == 'C']),
                'D': len([r for r in results if r['level'] == 'D']),
            },
            'papers': results
        }, f, ensure_ascii=False, indent=2)

    # 保存为 Markdown 报告
    md_file = OUTPUT_DIR / f"paper-scores-{date_str}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# 论文质量评分报告 - {date_str}\n\n")
        f.write(f"**评分时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**论文总数:** {len(results)}\n\n")
        f.write("---\n\n")

        f.write("## 📊 评分分布\n\n")
        dist = {
            'S': len([r for r in results if r['level'] == 'S']),
            'A': len([r for r in results if r['level'] == 'A']),
            'B': len([r for r in results if r['level'] == 'B']),
            'C': len([r for r in results if r['level'] == 'C']),
            'D': len([r for r in results if r['level'] == 'D']),
        }
        for level, count in dist.items():
            f.write(f"- **{level}级:** {count} 篇\n")
        f.write("\n---\n\n")

        f.write("## 🏆 高评分论文 (S 级)\n\n")
        s_papers = [r for r in results if r['level'] == 'S']
        for i, paper in enumerate(s_papers[:10], 1):
            f.write(f"### {i}. {paper['title']}\n\n")
            f.write(f"**arXiv:** {paper['arxiv_id']}  \n")
            f.write(f"**评分:** {paper['score']:.2f} (S 级)  \n\n")
            f.write("---\n\n")

    print(f"[OK] Saved scores to {json_file}")
    print(f"       S 级：{dist['S']}, A 级：{dist['A']}, B 级：{dist['B']}")
    return md_file

def test_scorer():
    """测试评分系统"""
    print("=" * 60)
    print("Paper Quality Scorer v1 - Test")
    print("=" * 60)

    # 模拟论文数据
    test_papers = [
        {
            'arxiv_id': '2603.00267',
            'title': 'Novel Framework for Agentic AI Planning',
            'abstract': 'We propose a novel framework that introduces innovative methods for multi-agent planning...'
        },
        {
            'arxiv_id': '2603.00285',
            'title': 'Efficient Training of Large Language Models',
            'abstract': 'This paper presents an efficient training method with rigorous experiments and baselines...'
        },
        {
            'arxiv_id': '2603.00309',
            'title': 'A Survey on Deep Learning',
            'abstract': 'This survey covers recent advances in deep learning...'
        },
    ]

    print("\n[1/3] Loading scoring criteria...")
    print(f"  Criteria: {len(SCORING_CRITERIA)}")

    print("\n[2/3] Scoring papers...")
    results = score_papers(test_papers)

    print("\n[3/3] Saving results...")
    save_scores(results)

    print("-" * 60)
    print("[COMPLETE] Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_scorer()
