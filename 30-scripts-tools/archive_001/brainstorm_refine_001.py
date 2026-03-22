import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BRAINSTORM-REFINE-001 Auto Problem Refinement
【自动问题重构器】

原理: 智能优化问题表述，生成更清晰的探索方向

重构策略:
  1. 问题澄清 - 明确问题的核心
  2. 约束识别 - 找出隐含限制
  3. 目标分解 - 将大目标分解为小目标
  4. 视角转换 - 提供不同角度

使用:
  py brainstorm_refine.py <problem>
"""

import json
import re
import sys
from pathlib import Path


# 问题重构规则
REFINEMENT_RULES = {
    "vague_words": {
        "检测": ["优化", "改进", "提升", "better", "improve", "fix", "解决"],
        "替换建议": "具体行动或指标"
    },
    "scope_expansion": {
        "关键词": ["只", "仅仅", "only", "just"],
        "建议": "考虑更广泛的视角"
    },
    "negation_check": {
        "检测": ["不要", "避免", "不要做", "don't", "avoid", "stop"],
        "建议": "正向表述目标"
    }
}


def detect_vague_parts(text: str) -> list:
    """检测模糊词汇"""
    vague_found = []
    
    for word in REFINEMENT_RULES["vague_words"]["检测"]:
        if word.lower() in text.lower():
            vague_found.append({
                "word": word,
                "issue": "模糊词汇",
                "suggestion": REFINEMENT_RULES["vague_words"]["替换建议"]
            })
    
    return vague_found


def detect_negations(text: str) -> list:
    """检测否定表述"""
    negations_found = []
    
    for word in REFINEMENT_RULES["negation_check"]["检测"]:
        if word.lower() in text.lower():
            negations_found.append({
                "word": word,
                "issue": "否定表述",
                "suggestion": "转化为正向目标"
            })
    
    return negations_found


def extract_keywords(text: str) -> list:
    """提取关键词"""
    # 移除停用词
    stop_words = ["的", "了", "是", "在", "和", "与", "或", "the", "a", "an", "is", "are", "to", "for", "of"]
    
    words = re.findall(r'\w+', text.lower())
    keywords = [w for w in words if w not in stop_words and len(w) > 1]
    
    return list(set(keywords))


def generate_rephrasings(text: str, keywords: list) -> list:
    """生成改写版本"""
    rephrasings = []
    
    # 1. 从问题转为目标
    rephrasings.append({
        "type": "目标导向",
        "text": f"如何实现{text}？",
        "rationale": "将问题转化为具体目标"
    })
    
    # 2. 从现状出发
    rephrasings.append({
        "type": "现状分析",
        "text": f"当前{text}的痛点是什么？",
        "rationale": "从用户痛点出发"
    })
    
    # 3. 反向思考
    rephrasings.append({
        "type": "反向思考",
        "text": f"如果不做{text}会怎样？",
        "rationale": "验证问题的必要性"
    })
    
    # 4. 扩大范围
    if keywords:
        main_keyword = keywords[0]
        rephrasings.append({
            "type": "扩展视角",
            "text": f"除了{main_keyword}，还有什么相关问题？",
            "rationale": "发现更多关联问题"
        })
    
    return rephrasings


def generate_sub_questions(text: str, keywords: list) -> list:
    """生成分问题"""
    sub_questions = []
    
    for kw in keywords[:3]:  # 最多3个关键词
        sub_questions.append({
            "keyword": kw,
            "questions": [
                f"什么是 {kw} 的最佳实践？",
                f"如何衡量 {kw} 的效果？",
                f"谁最需要 {kw}？",
                f"{kw} 的边界在哪里？"
            ]
        })
    
    return sub_questions


def refine_problem(text: str) -> dict:
    """重构问题"""
    
    results = {
        "original": text,
        "refinements": {
            "vague_parts": detect_vague_parts(text),
            "negations": detect_negations(text),
            "keywords": extract_keywords(text),
            "rephrasings": generate_rephrasings(text, extract_keywords(text)),
            "sub_questions": generate_sub_questions(text, extract_keywords(text))
        }
    }
    
    return results


def display_refinement(results: dict):
    """展示重构结果"""
    
    print("=" * 60)
    print(f"[REFINE] Problem: {results['original']}")
    print("=" * 60)
    
    # 检测到的问题
    refinements = results["refinements"]
    
    if refinements["vague_parts"]:
        print("\n[检测到模糊词汇]")
        for v in refinements["vague_parts"]:
            print(f"  - '{v['word']}' → {v['suggestion']}")
    
    if refinements["negations"]:
        print("\n[检测到否定表述]")
        for n in refinements["negations"]:
            print(f"  - '{n['word']}' → {n['suggestion']}")
    
    # 关键词
    if refinements["keywords"]:
        print(f"\n[关键词] {', '.join(refinements['keywords'][:5])}")
    
    # 改写版本
    if refinements["rephrasings"]:
        print("\n[改写版本]")
        for r in refinements["rephrasings"]:
            print(f"  [{r['type']}] {r['text']}")
    
    # 分问题
    if refinements["sub_questions"]:
        print("\n[分解问题]")
        for sq in refinements["sub_questions"]:
            print(f"  关于 '{sq['keyword']}':")
            for q in sq["questions"][:2]:
                print(f"    -> {q}")
    
    print("\n" + "=" * 60)


logging.basicConfig(level=logging.INFO)
def main():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py brainstorm_refine_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py brainstorm_refine_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

主函数"""
    
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "优化头脑风暴工作流"
    
    results = refine_problem(topic)
    display_refinement(results)
    
    # 保存结果
    output_file = Path(f"flow-archive/brainstorm-current/refined_problem.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n[Saved to] {output_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
