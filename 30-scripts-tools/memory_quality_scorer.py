#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Quality Scorer - 记忆质量评分工具

评估记忆质量，识别低质量内容，提供改进建议。

评分维度 (总分 100 分):
1. 完整性 (25 分) - 是否有清晰的上下文、决策、结果
2. 结构化 (20 分) - 是否有标题、列表、代码块等结构
3. 信息密度 (20 分) - 非空行比例、有效信息量
4. 可执行性 (20 分) - 是否有 Next Actions、待办事项
5. 独特性 (15 分) - 是否有新洞察、新决策、新概念

质量等级:
- A (≥90): 优秀 - 直接蒸馏到 MEMORY.md
- B (80-89): 良好 - 轻度压缩保留
- C (70-79): 中等 - 标准压缩
- D (60-69): 及格 - 重度压缩
- F (<60): 不合格 - 归档或删除

使用:
    # 评分单条记忆
    py memory_quality_scorer.py --memory "13-memory/2026-03-18.md"
    
    # 批量评分 (最近 7 天)
    py memory_quality_scorer.py --batch --days 7
    
    # 识别低质量记忆
    py memory_quality_scorer.py --low-quality --days 30
    
    # 生成质量报告
    py memory_quality_scorer.py --report --days 30
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import subprocess

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory'
SCRIPTS_DIR = WORKSPACE / '30-scripts-tools'


@dataclass
class QualityScore:
    """质量评分结果"""
    memory_id: str
    total_score: float
    grade: str
    dimensions: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    timestamp: str


@dataclass
class QualityReport:
    """质量报告"""
    total_memories: int
    average_score: float
    grade_distribution: Dict[str, int]
    low_quality_memories: List[str]
    high_quality_memories: List[str]
    details: List[QualityScore]
    recommendations: List[str]
    timestamp: str


class MemoryQualityScorer:
    """记忆质量评分器"""
    
    def __init__(self):
        self.weights = {
            'completeness': 25.0,    # 完整性
            'structure': 20.0,       # 结构化
            'density': 20.0,         # 信息密度
            'actionability': 20.0,   # 可执行性
            'uniqueness': 15.0       # 独特性
        }
    
    def _score_completeness(self, content: str) -> float:
        """评分完整性 (25 分)"""
        score = 0.0
        
        # 1. 有清晰的标题/主题 (5 分)
        has_title = bool(re.search(r'^#{1,3}\s+\S+', content, re.MULTILINE))
        score += 5 if has_title else 0
        
        # 2. 有上下文/背景 (5 分)
        context_keywords = ['context', 'background', 'goal', 'objective', '目标', '背景', '上下文']
        has_context = any(kw in content.lower() for kw in context_keywords)
        score += 5 if has_context else 0
        
        # 3. 有决策/结论 (5 分)
        decision_keywords = ['decided', 'decision', 'conclusion', 'result', '决定', '结论', '结果']
        has_decision = any(kw in content.lower() for kw in decision_keywords)
        score += 5 if has_decision else 0
        
        # 4. 有理由/依据 (5 分)
        reason_keywords = ['because', 'reason', 'therefore', 'since', '因为', '所以', '原因']
        has_reason = any(kw in content.lower() for kw in reason_keywords)
        score += 5 if has_reason else 0
        
        # 5. 有后续行动 (5 分)
        action_keywords = ['next', 'action', 'todo', 'should', 'will', '下一步', '待办']
        has_action = any(kw in content.lower() for kw in action_keywords)
        score += 5 if has_action else 0
        
        return score
    
    def _score_structure(self, content: str) -> float:
        """评分结构化 (20 分)"""
        score = 0.0
        
        # 1. 使用标题层级 (5 分)
        headers = re.findall(r'^#{1,6}\s+', content, re.MULTILINE)
        if len(headers) >= 3:
            score += 5
        elif len(headers) >= 1:
            score += 3
        
        # 2. 使用列表 (5 分)
        lists = re.findall(r'^\s*[-*+]\s', content, re.MULTILINE)
        if len(lists) >= 5:
            score += 5
        elif len(lists) >= 1:
            score += 3
        
        # 3. 使用代码块 (5 分)
        code_blocks = re.findall(r'```', content)
        if len(code_blocks) >= 2:
            score += 5
        elif len(code_blocks) >= 1:
            score += 3
        
        # 4. 使用表格 (5 分)
        tables = re.findall(r'\|.*?\|', content)
        if len(tables) >= 2:
            score += 5
        elif len(tables) >= 1:
            score += 3
        
        return min(score, 20.0)
    
    def _score_density(self, content: str) -> float:
        """评分信息密度 (20 分)"""
        score = 0.0
        
        lines = content.split('\n')
        non_empty = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        
        # 1. 非空行比例 (10 分)
        if len(lines) > 0:
            density = len(non_empty) / len(lines)
            score += density * 10
        
        # 2. 平均行长度 (10 分)
        if non_empty:
            avg_length = sum(len(l) for l in non_empty) / len(non_empty)
            if avg_length >= 50:
                score += 10
            elif avg_length >= 30:
                score += 7
            elif avg_length >= 15:
                score += 5
        
        return min(score, 20.0)
    
    def _score_actionability(self, content: str) -> float:
        """评分可执行性 (20 分)"""
        score = 0.0
        
        # 1. 有明确的 Next Actions (10 分)
        next_action_patterns = [
            r'next\s*(action|step|task)',
            r'todo\s*\d*',
            r'待办\s*\d*',
            r'下一步\s*[:：]',
            r'TODO\s*[:：]',
        ]
        has_next_action = any(re.search(p, content, re.IGNORECASE) for p in next_action_patterns)
        score += 10 if has_next_action else 0
        
        # 2. 有量化指标 (5 分)
        metrics = re.findall(r'\d+\s*(%|ms|KB|MB|GB|seconds|minutes|hours)', content, re.IGNORECASE)
        if len(metrics) >= 3:
            score += 5
        elif len(metrics) >= 1:
            score += 3
        
        # 3. 有时间承诺 (5 分)
        time_patterns = [
            r'(today|tomorrow|this\s+week|next\s+week)',
            r'(今天 | 明天 | 本周 | 下周)',
            r'\d{4}-\d{2}-\d{2}',
        ]
        has_time = any(re.search(p, content, re.IGNORECASE) for p in time_patterns)
        score += 5 if has_time else 0
        
        return score
    
    def _score_uniqueness(self, content: str) -> float:
        """评分独特性 (15 分)"""
        score = 0.0
        
        # 1. 有新概念/新工具 (5 分)
        creation_keywords = ['create', 'implement', 'build', 'design', 'new', 'first', 
                            '创建', '实现', '构建', '设计', '新', '首次']
        creation_count = sum(1 for kw in creation_keywords if kw in content.lower())
        if creation_count >= 5:
            score += 5
        elif creation_count >= 2:
            score += 3
        
        # 2. 有洞察/发现 (5 分)
        insight_keywords = ['insight', 'discover', 'learn', 'realize', 'found', 
                           '洞察', '发现', '学到', '意识到']
        insight_count = sum(1 for kw in insight_keywords if kw in content.lower())
        if insight_count >= 3:
            score += 5
        elif insight_count >= 1:
            score += 3
        
        # 3. 有架构变更/重大决策 (5 分)
        architecture_keywords = ['architecture', 'refactor', 'migration', 'phase', 'major',
                                '架构', '重构', '迁移', '阶段', '重大']
        arch_count = sum(1 for kw in architecture_keywords if kw in content.lower())
        if arch_count >= 3:
            score += 5
        elif arch_count >= 1:
            score += 3
        
        return min(score, 15.0)
    
    def _determine_grade(self, total_score: float) -> str:
        """确定等级"""
        if total_score >= 90:
            return 'A'
        elif total_score >= 80:
            return 'B'
        elif total_score >= 70:
            return 'C'
        elif total_score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_feedback(self, content: str, dimensions: Dict[str, float]) -> Tuple[List[str], List[str], List[str]]:
        """生成反馈"""
        strengths = []
        weaknesses = []
        recommendations = []
        
        # 完整性
        if dimensions['completeness'] >= 20:
            strengths.append("内容完整性良好，包含清晰的上下文和决策")
        else:
            weaknesses.append("缺少清晰的上下文或决策")
            recommendations.append("添加背景说明、决策理由和后续行动")
        
        # 结构化
        if dimensions['structure'] >= 15:
            strengths.append("结构化良好，使用了标题、列表等格式")
        else:
            weaknesses.append("结构化不足")
            recommendations.append("使用标题层级、列表、代码块来组织内容")
        
        # 信息密度
        if dimensions['density'] >= 15:
            strengths.append("信息密度高，内容充实")
        else:
            weaknesses.append("信息密度较低")
            recommendations.append("减少空行，增加实质性内容")
        
        # 可执行性
        if dimensions['actionability'] >= 15:
            strengths.append("可执行性强，有明确的后续行动")
        else:
            weaknesses.append("缺少可执行的行动项")
            recommendations.append("添加具体的 Next Actions 和时间承诺")
        
        # 独特性
        if dimensions['uniqueness'] >= 10:
            strengths.append("包含独特洞察或新概念")
        else:
            weaknesses.append("内容较为常规")
            recommendations.append("记录更多个人洞察、决策理由和教训")
        
        return strengths, weaknesses, recommendations
    
    def score_single(self, memory_path: Path) -> QualityScore:
        """评分单条记忆"""
        content = memory_path.read_text(encoding='utf-8', errors='replace')
        
        # 各维度评分
        dimensions = {
            'completeness': self._score_completeness(content),
            'structure': self._score_structure(content),
            'density': self._score_density(content),
            'actionability': self._score_actionability(content),
            'uniqueness': self._score_uniqueness(content)
        }
        
        # 总分
        total_score = sum(dimensions.values())
        
        # 等级
        grade = self._determine_grade(total_score)
        
        # 反馈
        strengths, weaknesses, recommendations = self._generate_feedback(content, dimensions)
        
        return QualityScore(
            memory_id=memory_path.name,
            total_score=round(total_score, 2),
            grade=grade,
            dimensions={k: round(v, 2) for k, v in dimensions.items()},
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    def score_batch(self, days: int = 7) -> List[QualityScore]:
        """批量评分"""
        scores = []
        
        if not MEMORY_DIR.exists():
            return scores
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for note_file in MEMORY_DIR.glob("*.md"):
            if note_file.stem == "MEMORY":
                continue
            
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', note_file.stem):
                continue
            
            try:
                note_date = datetime.strptime(note_file.stem, '%Y-%m-%d')
                if note_date < cutoff_date:
                    continue
                
                score = self.score_single(note_file)
                scores.append(score)
            
            except Exception as e:
                print(f"[ERROR] {note_file.name}: {e}")
        
        return sorted(scores, key=lambda x: x.total_score, reverse=True)
    
    def generate_report(self, days: int = 7) -> QualityReport:
        """生成质量报告"""
        scores = self.score_batch(days)
        
        if not scores:
            return QualityReport(
                total_memories=0,
                average_score=0,
                grade_distribution={},
                low_quality_memories=[],
                high_quality_memories=[],
                details=[],
                recommendations=["No memories found"],
                timestamp=datetime.now().isoformat()
            )
        
        # 统计
        avg_score = sum(s.total_score for s in scores) / len(scores)
        
        # 等级分布
        grade_dist = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        for s in scores:
            grade_dist[s.grade] = grade_dist.get(s.grade, 0) + 1
        
        # 高质量和低质量
        high_quality = [s.memory_id for s in scores if s.grade in ['A', 'B']]
        low_quality = [s.memory_id for s in scores if s.grade in ['D', 'F']]
        
        # 总体建议
        recommendations = []
        if grade_dist['F'] > 0:
            recommendations.append(f"发现 {grade_dist['F']} 条低质量记忆 (F 级)，建议归档或删除")
        
        if grade_dist['A'] > 0:
            recommendations.append(f"发现 {grade_dist['A']} 条高质量记忆 (A 级)，建议蒸馏到 MEMORY.md")
        
        if avg_score < 70:
            recommendations.append("整体质量偏低，建议改进记录习惯")
        elif avg_score >= 85:
            recommendations.append("整体质量优秀，保持当前实践")
        
        if not recommendations:
            recommendations.append("记忆质量良好")
        
        return QualityReport(
            total_memories=len(scores),
            average_score=round(avg_score, 2),
            grade_distribution=grade_dist,
            low_quality_memories=low_quality,
            high_quality_memories=high_quality,
            details=scores,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )


def print_score(score: QualityScore):
    """打印评分结果"""
    print("\n" + "=" * 60)
    print(f"Quality Score: {score.memory_id}")
    print("=" * 60)
    
    print(f"\n[Overall]")
    print(f"  Total Score: {score.total_score}/100")
    print(f"  Grade: {score.grade}")
    
    print(f"\n[Dimensions]")
    for dim, val in score.dimensions.items():
        max_score = {'completeness': 25, 'structure': 20, 'density': 20, 
                    'actionability': 20, 'uniqueness': 15}[dim]
        bar = '█' * int(val / max_score * 20)
        print(f"  {dim:15s}: {val:5.1f}/{max_score:2d} {bar}")
    
    if score.strengths:
        print(f"\n[Strengths]")
        for s in score.strengths:
            print(f"  ✓ {s}")
    
    if score.weaknesses:
        print(f"\n[Weaknesses]")
        for w in score.weaknesses:
            print(f"  ✗ {w}")
    
    if score.recommendations:
        print(f"\n[Recommendations]")
        for r in score.recommendations:
            print(f"  • {r}")


def print_report(report: QualityReport):
    """打印质量报告"""
    print("\n" + "=" * 60)
    print("Memory Quality Report")
    print("=" * 60)
    
    print(f"\n[Overview]")
    print(f"  Total Memories: {report.total_memories}")
    print(f"  Average Score:  {report.average_score}/100")
    
    print(f"\n[Grade Distribution]")
    for grade in ['A', 'B', 'C', 'D', 'F']:
        count = report.grade_distribution.get(grade, 0)
        pct = count / report.total_memories * 100 if report.total_memories > 0 else 0
        bar = '█' * int(pct / 5)
        print(f"  {grade}: {count:3d} ({pct:5.1f}%) {bar}")
    
    if report.high_quality_memories:
        print(f"\n[High Quality ({len(report.high_quality_memories)})]")
        for mem in report.high_quality_memories[:5]:
            print(f"  • {mem}")
    
    if report.low_quality_memories:
        print(f"\n[Low Quality ({len(report.low_quality_memories)})]")
        for mem in report.low_quality_memories[:5]:
            print(f"  • {mem}")
    
    print(f"\n[Recommendations]")
    for rec in report.recommendations:
        print(f"  • {rec}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Quality Scorer')
    parser.add_argument('--memory', type=str, help='评分单条记忆文件')
    parser.add_argument('--batch', action='store_true', help='批量评分')
    parser.add_argument('--days', type=int, default=7, help='处理最近 N 天 (默认 7)')
    parser.add_argument('--low-quality', action='store_true', help='仅显示低质量记忆')
    parser.add_argument('--report', action='store_true', help='生成完整报告')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    scorer = MemoryQualityScorer()
    
    # 单文件评分
    if args.memory:
        memory_path = Path(args.memory.replace('"', '').replace("'", ""))
        if not memory_path.is_absolute():
            memory_path = WORKSPACE / memory_path
        
        if not memory_path.exists():
            print(f"[ERROR] File not found: {memory_path}")
            return 1
        
        score = scorer.score_single(memory_path)
        
        if args.json:
            print(json.dumps(asdict(score), indent=2, ensure_ascii=False))
        else:
            print_score(score)
        
        return 0
    
    # 批量评分
    if args.batch:
        scores = scorer.score_batch(args.days)
        
        if args.json:
            print(json.dumps([asdict(s) for s in scores], indent=2, ensure_ascii=False))
        else:
            for score in scores:
                print_score(score)
        
        return 0
    
    # 低质量记忆
    if args.low_quality:
        scores = scorer.score_batch(args.days)
        low_quality = [s for s in scores if s.grade in ['D', 'F']]
        
        if args.json:
            print(json.dumps([asdict(s) for s in low_quality], indent=2, ensure_ascii=False))
        else:
            print(f"\n[Low Quality Memories ({len(low_quality)})]")
            for score in low_quality:
                print(f"\n{score.memory_id}: {score.total_score}/100 (Grade {score.grade})")
                for w in score.weaknesses:
                    print(f"  ✗ {w}")
        
        return 0
    
    # 生成报告
    if args.report:
        report = scorer.generate_report(args.days)
        
        if args.json:
            print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
        else:
            print_report(report)
        
        return 0
    
    # 默认显示帮助
    parser.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
