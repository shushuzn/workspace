#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Importance Assessor - 记忆重要性评估工具

功能:
- 评估单条记忆/会话的重要性 (0-1)
- 多维度评分（可执行性/独特性/时效性/影响力）
- 推荐压缩策略
- 批量评估支持

使用:
    # 评估单条记忆
    py memory_importance_assessor.py --memory "13-memory/2026-03-18.md"
    
    # 批量评估
    py memory_importance_assessor.py --batch --days 30
    
    # 查看评分分布
    py memory_importance_assessor.py --distribution
    
    # 推荐压缩策略
    py memory_importance_assessor.py --memory "13-memory/2026-03-18.md" --recommend
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory'
SCRIPTS_DIR = WORKSPACE / '30-scripts-tools'


@dataclass
class ImportanceReport:
    """重要性评估报告"""
    memory_id: str
    overall_score: float
    dimensions: Dict[str, float]
    grade: str  # S/A/B/C/D
    compression_strategy: str
    recommendations: List[str]
    timestamp: str


class MemoryImportanceAssessor:
    """记忆重要性评估器"""
    
    def __init__(self):
        # 权重配置
        self.weights = {
            'actionability': 0.20,    # 可执行性
            'uniqueness': 0.25,       # 独特性
            'recency': 0.15,          # 时效性
            'impact': 0.25,           # 影响力
            'connectivity': 0.15      # 连接性
        }
        
        # 评分阈值
        self.grade_thresholds = {
            'S': 0.90,  # 极其重要 - 完整保留
            'A': 0.75,  # 很重要 - 轻度压缩
            'B': 0.60,  # 中等重要 - 标准压缩
            'C': 0.40,  # 较低重要 - 重度压缩
            'D': 0.00   # 不重要 - 归档/遗忘
        }
        
        # 压缩策略映射
        self.strategy_map = {
            'S': 'retain_full',      # 完整保留
            'A': 'compress_light',   # 轻度压缩 (保留 80%)
            'B': 'compress_standard', # 标准压缩 (保留 50%)
            'C': 'compress_heavy',   # 重度压缩 (保留 20%)
            'D': 'archive_only'      # 仅归档
        }
    
    def score_actionability(self, content: str) -> float:
        """
        可执行性评分 (0-1)
        
        检查项:
        - 有 next_actions / TODO / 下一步
        - 有明确的责任人/时间点
        - 有可衡量的目标
        """
        score = 0.0
        
        # 1. 检查行动项关键词
        action_keywords = [
            'next action', 'todo', 'to-do', '下一步', '待办',
            'should', 'must', 'need to', 'will', 'plan to'
        ]
        
        content_lower = content.lower()
        action_count = sum(1 for kw in action_keywords if kw in content_lower)
        
        if action_count >= 5:
            score += 0.5
        elif action_count >= 3:
            score += 0.3
        elif action_count >= 1:
            score += 0.1
        
        # 2. 检查时间承诺
        time_patterns = [
            r'\d+[dhm]',  # 1h, 30m, 2d
            r'tomorrow', 'next week', 'by ', 'before ',
            '明天', '下周', '之前'
        ]
        
        time_count = sum(1 for pattern in time_patterns if re.search(pattern, content_lower))
        if time_count >= 2:
            score += 0.3
        elif time_count >= 1:
            score += 0.15
        
        # 3. 检查量化指标
        metric_patterns = [
            r'\d+%', r'\d+x', r'\d+ seconds?', r'\d+ minutes?',
            r'increase', 'decrease', 'improve', 'reduce',
            '提升', '降低', '减少', '增加'
        ]
        
        metric_count = sum(1 for pattern in metric_patterns if re.search(pattern, content_lower))
        if metric_count >= 3:
            score += 0.2
        elif metric_count >= 1:
            score += 0.1
        
        return min(score, 1.0)
    
    def score_uniqueness(self, content: str) -> float:
        """
        独特性评分 (0-1)
        
        检查项:
        - 有新工具/文件创建
        - 有新概念/洞察
        - 与已有记忆重复度低
        """
        score = 0.0
        
        # 1. 检查创建内容
        creation_patterns = [
            r'create', r'created', r'implement', r'implemented',
            r'build', r'built', r'design', r'designed',
            '创建', '实现', '设计', '开发'
        ]
        
        content_lower = content.lower()
        creation_count = sum(1 for pattern in creation_patterns if re.search(pattern, content_lower))
        
        if creation_count >= 3:
            score += 0.4
        elif creation_count >= 1:
            score += 0.2
        
        # 2. 检查工具/文件提及
        tool_patterns = [
            r'tool', r'script', r'module', r'system',
            r'engine', r'framework', r'pipeline',
            '工具', '脚本', '系统', '引擎'
        ]
        
        tool_count = sum(1 for pattern in tool_patterns if re.search(pattern, content_lower))
        if tool_count >= 5:
            score += 0.3
        elif tool_count >= 2:
            score += 0.15
        
        # 3. 检查新概念/洞察
        insight_patterns = [
            r'insight', r'discover', r'learn', r'realize',
            r'principle', r'pattern', r'strategy',
            '洞察', '发现', '学习', '原则', '模式'
        ]
        
        insight_count = sum(1 for pattern in insight_patterns if re.search(pattern, content_lower))
        if insight_count >= 3:
            score += 0.3
        elif insight_count >= 1:
            score += 0.15
        
        return min(score, 1.0)
    
    def score_recency(self, timestamp: str) -> float:
        """
        时效性评分 (0-1)
        
        使用指数衰减:
        - 0-7 天：1.0 → 0.8
        - 7-30 天：0.8 → 0.4
        - 30+ 天：0.4 → 0.0
        """
        try:
            # 解析时间戳
            if 'T' in timestamp:
                memory_time = datetime.fromisoformat(timestamp)
            else:
                memory_time = datetime.strptime(timestamp, '%Y-%m-%d')
            
            days_old = (datetime.now() - memory_time).days
            
            if days_old < 0:
                return 1.0
            
            # 指数衰减
            import math
            if days_old <= 7:
                # 0-7 天：快速衰减
                score = 1.0 - (days_old / 7) * 0.2
            elif days_old <= 30:
                # 7-30 天：中速衰减
                score = 0.8 - ((days_old - 7) / 23) * 0.4
            else:
                # 30+ 天：慢速衰减
                score = max(0, 0.4 * math.exp(-(days_old - 30) / 60))
            
            return score
        
        except Exception as e:
            return 0.5  # 默认中等分数
    
    def score_impact(self, content: str) -> float:
        """
        影响力评分 (0-1)
        
        检查项:
        - 有重大决策/架构变更
        - 影响范围广（多个模块/系统）
        - 长期价值
        """
        score = 0.0
        
        content_lower = content.lower()
        
        # 1. 检查重大决策关键词
        impact_keywords = [
            'architecture', 'critical', 'major', 'phase', 'milestone',
            'breakthrough', 'significant', 'core', 'foundation',
            '架构', '关键', '重大', '阶段', '里程碑', '核心'
        ]
        
        impact_count = sum(1 for kw in impact_keywords if kw in content_lower)
        if impact_count >= 5:
            score += 0.4
        elif impact_count >= 2:
            score += 0.2
        elif impact_count >= 1:
            score += 0.1
        
        # 2. 检查影响范围
        scope_patterns = [
            r'system', r'module', r'component', r'layer',
            r'pipeline', r'workflow', r'framework',
            '系统', '模块', '组件', '流程'
        ]
        
        scope_count = sum(1 for pattern in scope_patterns if re.search(pattern, content_lower))
        if scope_count >= 5:
            score += 0.3
        elif scope_count >= 2:
            score += 0.15
        
        # 3. 检查长期价值
        value_patterns = [
            r'long.?term', r'sustainable', r'scalable', r'reusable',
            r'principle', r'guideline', r'best practice',
            '长期', '可持续', '可扩展', '可复用', '原则'
        ]
        
        value_count = sum(1 for pattern in value_patterns if re.search(pattern, content_lower))
        if value_count >= 3:
            score += 0.3
        elif value_count >= 1:
            score += 0.15
        
        return min(score, 1.0)
    
    def score_connectivity(self, content: str) -> float:
        """
        连接性评分 (0-1)
        
        检查项:
        - 引用其他记忆/文档
        - 被其他记忆引用
        - 跨领域连接
        """
        score = 0.0
        
        content_lower = content.lower()
        
        # 1. 检查引用
        reference_patterns = [
            r'see also', r'related to', r'references', r'based on',
            r'continuation', r'follow.?up',
            '参见', '相关', '参考', '基于', '后续'
        ]
        
        ref_count = sum(1 for pattern in reference_patterns if re.search(pattern, content_lower))
        if ref_count >= 3:
            score += 0.4
        elif ref_count >= 1:
            score += 0.2
        
        # 2. 检查跨领域
        domain_patterns = [
            r'memory', r'compression', r'architecture', r'workflow',
            r'tool', r'system', r'research',
            '记忆', '压缩', '架构', '工作流', '工具', '系统', '研究'
        ]
        
        domain_count = sum(1 for pattern in domain_patterns if re.search(pattern, content_lower))
        if domain_count >= 5:
            score += 0.3
        elif domain_count >= 2:
            score += 0.15
        
        # 3. 检查链接/文件引用
        link_patterns = [
            r'\[.*?\]\(.*?\)',  # Markdown 链接
            r'`.*?`',           # 代码引用
            r'\.md\b',          # .md 文件
            r'30-scripts',      # 脚本目录
        ]
        
        link_count = sum(1 for pattern in link_patterns if re.search(pattern, content))
        if link_count >= 5:
            score += 0.3
        elif link_count >= 2:
            score += 0.15
        
        return min(score, 1.0)
    
    def assess(self, memory_path: Path) -> ImportanceReport:
        """评估单条记忆"""
        # 读取内容
        content = memory_path.read_text(encoding='utf-8', errors='replace')
        
        # 提取时间戳
        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2})', memory_path.name)
        timestamp = timestamp_match.group(1) if timestamp_match else datetime.now().isoformat()
        
        # 多维度评分
        dimensions = {
            'actionability': self.score_actionability(content),
            'uniqueness': self.score_uniqueness(content),
            'recency': self.score_recency(timestamp),
            'impact': self.score_impact(content),
            'connectivity': self.score_connectivity(content)
        }
        
        # 计算总分
        overall_score = sum(
            dimensions[dim] * self.weights[dim]
            for dim in dimensions
        )
        
        # 确定等级
        grade = 'D'
        for g, threshold in self.grade_thresholds.items():
            if overall_score >= threshold:
                grade = g
                break
        
        # 推荐压缩策略
        compression_strategy = self.strategy_map[grade]
        
        # 生成建议
        recommendations = self._generate_recommendations(dimensions, grade)
        
        return ImportanceReport(
            memory_id=memory_path.name,
            overall_score=round(overall_score, 3),
            dimensions={k: round(v, 3) for k, v in dimensions.items()},
            grade=grade,
            compression_strategy=compression_strategy,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    def _generate_recommendations(self, dimensions: Dict[str, float], grade: str) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 找出最弱维度
        min_dim = min(dimensions, key=dimensions.get)
        min_score = dimensions[min_dim]
        
        if min_score < 0.3:
            if min_dim == 'actionability':
                recommendations.append("添加明确的下一步行动 (Next Actions)")
                recommendations.append("量化目标和时间承诺")
            elif min_dim == 'uniqueness':
                recommendations.append("记录独特洞察和新发现")
                recommendations.append("标注创建的工具/文件")
            elif min_dim == 'recency':
                recommendations.append("考虑归档或蒸馏到 MEMORY.md")
            elif min_dim == 'impact':
                recommendations.append("说明决策的长期影响")
                recommendations.append("记录架构变更的原因")
            elif min_dim == 'connectivity':
                recommendations.append("添加相关记忆的引用链接")
                recommendations.append("建立跨领域连接")
        
        # 根据等级给出建议
        if grade in ['C', 'D']:
            recommendations.append("考虑重度压缩或归档")
        elif grade == 'B':
            recommendations.append("标准压缩即可")
        elif grade == 'A':
            recommendations.append("轻度压缩，保留关键细节")
        elif grade == 'S':
            recommendations.append("完整保留，标记为关键记忆")
        
        return recommendations
    
    def assess_batch(self, days: int = 30) -> List[ImportanceReport]:
        """批量评估最近 N 天的记忆"""
        reports = []
        
        if not MEMORY_DIR.exists():
            return reports
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for note_file in MEMORY_DIR.glob("*.md"):
            if note_file.stem == "MEMORY":
                continue
            
            try:
                # 解析日期
                note_date = datetime.strptime(note_file.stem, '%Y-%m-%d')
                if note_date < cutoff_date:
                    continue
                
                # 评估
                report = self.assess(note_file)
                reports.append(report)
            
            except Exception as e:
                print(f"[ERROR] {note_file.name}: {e}")
        
        # 按分数排序
        reports.sort(key=lambda r: r.overall_score, reverse=True)
        
        return reports


def print_report(report: ImportanceReport):
    """打印评估报告"""
    print("\n" + "=" * 60)
    print(f"Memory Importance Assessment: {report.memory_id}")
    print("=" * 60)
    
    print(f"\n[Overall Score] {report.overall_score:.3f} / 1.000")
    print(f"[Grade] {report.grade}")
    print(f"[Compression Strategy] {report.compression_strategy}")
    
    print(f"\n[Dimensions]")
    for dim, score in report.dimensions.items():
        bar = '█' * int(score * 10) + '░' * (10 - int(score * 10))
        print(f"  {dim:15s}: [{bar}] {score:.3f}")
    
    if report.recommendations:
        print(f"\n[Recommendations]")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"  {i}. {rec}")
    
    print(f"\n[Timestamp] {report.timestamp}")


def print_distribution(reports: List[ImportanceReport]):
    """打印分数分布"""
    print("\n" + "=" * 60)
    print("Score Distribution")
    print("=" * 60)
    
    # 按等级分组
    grades = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}
    for report in reports:
        grades[report.grade] += 1
    
    total = len(reports)
    
    print(f"\n[Total Memories] {total}")
    print(f"\n[Grade Distribution]")
    
    for grade, count in sorted(grades.items(), reverse=True):
        pct = (count / total * 100) if total > 0 else 0
        bar = '█' * int(pct / 5)
        print(f"  {grade}: {count:3d} ({pct:5.1f}%) {bar}")
    
    # 平均分
    if reports:
        avg_score = sum(r.overall_score for r in reports) / len(reports)
        print(f"\n[Average Score] {avg_score:.3f}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Importance Assessor')
    parser.add_argument('--memory', type=str, help='评估单条记忆文件')
    parser.add_argument('--batch', action='store_true', help='批量评估')
    parser.add_argument('--days', type=int, default=30, help='评估最近 N 天 (默认 30)')
    parser.add_argument('--distribution', action='store_true', help='显示分数分布')
    parser.add_argument('--recommend', action='store_true', help='推荐压缩策略')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    assessor = MemoryImportanceAssessor()
    
    # 单条评估
    if args.memory:
        # 处理路径（支持多种格式）
        memory_path = Path(args.memory.replace('"', '').replace("'", ""))
        if not memory_path.is_absolute():
            memory_path = WORKSPACE / memory_path
        
        if not memory_path.exists():
            print(f"[ERROR] File not found: {memory_path}")
            print(f"[CWD] {Path.cwd()}")
            print(f"[WORKSPACE] {WORKSPACE}")
            return 1
        
        report = assessor.assess(memory_path)
        
        if args.json:
            print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
        else:
            print_report(report)
            
            if args.recommend:
                print(f"\n[Recommended Action]")
                print(f"  Strategy: {report.compression_strategy}")
                print(f"  - Retain: {report.grade in ['S', 'A']}")
                print(f"  - Compress: {report.grade in ['B', 'C']}")
                print(f"  - Archive: {report.grade == 'D'}")
        
        return 0
    
    # 批量评估
    if args.batch:
        reports = assessor.assess_batch(args.days)
        
        if args.json:
            print(json.dumps([asdict(r) for r in reports], indent=2, ensure_ascii=False))
        else:
            print(f"\n[Batch Assessment] Last {args.days} days")
            print(f"Total memories: {len(reports)}")
            
            # 显示 Top 5
            if reports:
                print(f"\n[Top 5 Most Important]")
                for i, report in enumerate(reports[:5], 1):
                    print(f"  {i}. {report.memory_id} - {report.overall_score:.3f} ({report.grade})")
                
                # 显示 Bottom 5
                if len(reports) > 5:
                    print(f"\n[Bottom 5 Least Important]")
                    for i, report in enumerate(reports[-5:], 1):
                        print(f"  {i}. {report.memory_id} - {report.overall_score:.3f} ({report.grade})")
        
        # 分布统计
        if args.distribution or args.batch:
            print_distribution(reports)
        
        return 0
    
    # 默认显示帮助
    parser.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
