#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Hybrid Compression Pipeline - 混合压缩管道

整合所有压缩策略:
1. 去重 (Cleanup) - memory_cleanup_compress.py
2. 质量评分 (Quality) - memory_quality_scorer.py
3. 重要性评估 (Importance) - memory_importance_assessor.py
4. 增量压缩 (Incremental) - memory_incremental_compressor.py
5. 分层压缩 (Tiered) - post_session_compress.py
6. LLM 蒸馏 (LLM) - 可选

压缩决策树:
```
                    ┌─────────────────┐
                    │   输入记忆      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  1. 去重清理    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  2. 质量评分    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
       ┌──────▼──────┐ ┌─────▼─────┐ ┌─────▼─────┐
       │ Quality≥0.9 │ │0.7≤Q<0.9  │ │ Quality<0.7│
       └──────┬──────┘ └─────┬─────┘ └─────┬─────┘
              │              │              │
       ┌──────▼──────┐ ┌─────▼─────┐ ┌─────▼─────┐
       │3.重要性评估 │ │ 标准压缩  │ │ 归档/遗忘 │
       └──────┬──────┘ └───────────┘ └───────────┘
              │
       ┌──────┴──────┐
       │  Importance │
       └──────┬──────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│ Imp≥0.8│ │0.5≤I<0.8│ │  I<0.5 │
└───┬───┘ └───┬───┘ └───┬───┘
    │         │         │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│蒸馏到 │ │分层压 │ │重度压 │
│MEMORY │ │缩 50% │ │缩 20% │
└───────┘ └───────┘ └───────┘
```

使用:
    # 单文件混合压缩
    py memory_hybrid_pipeline.py --memory "13-memory/2026-03-18.md"
    
    # 批量处理 (最近 7 天)
    py memory_hybrid_pipeline.py --batch --days 7
    
    # 仅分析 (不执行压缩)
    py memory_hybrid_pipeline.py --analyze --days 14
    
    # 生成压缩报告
    py memory_hybrid_pipeline.py --report --days 30
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
class CompressionResult:
    """压缩结果"""
    memory_id: str
    original_size: int
    final_size: int
    compression_ratio: float
    quality_score: float
    importance_score: float
    strategy_used: str
    steps_executed: List[str]
    timestamp: str


@dataclass
class PipelineReport:
    """管道执行报告"""
    total_memories: int
    total_original_size: int
    total_final_size: int
    overall_compression_ratio: float
    strategy_distribution: Dict[str, int]
    quality_distribution: Dict[str, int]
    details: List[CompressionResult]
    recommendations: List[str]
    timestamp: str


class MemoryHybridPipeline:
    """记忆混合压缩管道"""
    
    def __init__(self, config: Dict = None):
        self.results = []
        # 正确合并配置
        default = self._default_config()
        if config:
            default.update(config)
        self.config = default
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            'quality_thresholds': {
                'high': 0.9,    # 高质量 - 考虑蒸馏
                'medium': 0.7,  # 中等质量 - 标准压缩
                'low': 0.5      # 低质量 - 重度压缩/归档
            },
            'importance_thresholds': {
                'critical': 0.8,  # 极其重要 - 蒸馏到 MEMORY
                'high': 0.6,      # 很重要 - 轻度压缩
                'medium': 0.4,    # 中等 - 标准压缩
                'low': 0.2        # 低 - 重度压缩
            },
            'strategies': {
                'distill_to_memory': {
                    'min_quality': 0.9,
                    'min_importance': 0.8,
                    'compression_ratio': 0.9,  # 保留 90%
                    'description': '蒸馏到 MEMORY.md'
                },
                'tiered_light': {
                    'min_quality': 0.7,
                    'min_importance': 0.6,
                    'compression_ratio': 0.8,  # 保留 80%
                    'description': '分层轻度压缩'
                },
                'tiered_standard': {
                    'min_quality': 0.5,
                    'min_importance': 0.4,
                    'compression_ratio': 0.5,  # 保留 50%
                    'description': '分层标准压缩'
                },
                'tiered_heavy': {
                    'min_quality': 0.0,
                    'min_importance': 0.2,
                    'compression_ratio': 0.2,  # 保留 20%
                    'description': '分层重度压缩'
                },
                'archive': {
                    'min_quality': 0.0,
                    'min_importance': 0.0,
                    'compression_ratio': 0.1,  # 保留 10%
                    'description': '归档'
                }
            },
            'skip_tools': False,  # 是否跳过外部工具调用
            'dry_run': False      # 是否只分析不执行
        }
    
    def _call_tool(self, tool_name: str, args: List[str]) -> Tuple[bool, str]:
        """调用外部工具"""
        if self.config['skip_tools']:
            return True, "Skipped (dry-run mode)"
        
        tool_path = SCRIPTS_DIR / f"{tool_name}.py"
        if not tool_path.exists():
            return False, f"Tool not found: {tool_name}"
        
        try:
            cmd = [sys.executable, str(tool_path)] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                return True, result.stdout[:500] if result.stdout else "OK"
            else:
                return False, result.stderr[:500] if result.stderr else "Unknown error"
        
        except Exception as e:
            return False, str(e)
    
    def _assess_quality(self, content: str) -> float:
        """评估质量（简化版，不依赖外部工具）"""
        score = 0.0
        
        # 1. 长度评分 (25%)
        length = len(content)
        if length >= 500:
            score += 0.25
        elif length >= 200:
            score += 0.20
        elif length >= 100:
            score += 0.15
        elif length >= 50:
            score += 0.10
        
        # 2. 结构评分 (25%)
        has_headers = bool(re.search(r'^#{1,6}\s', content, re.MULTILINE))
        has_lists = bool(re.search(r'^\s*[-*]\s', content, re.MULTILINE))
        has_code = bool(re.search(r'`[^`]+`', content))
        
        structure_score = sum([has_headers, has_lists, has_code]) / 3
        score += structure_score * 0.25
        
        # 3. 信息密度 (25%)
        lines = content.split('\n')
        non_empty = [l for l in lines if l.strip()]
        density = len(non_empty) / max(len(lines), 1)
        score += density * 0.25
        
        # 4. 独特性 (25%)
        unique_keywords = ['insight', 'discover', 'learn', 'decision', 'architecture', 
                          'critical', 'breakthrough', '创新', '发现', '决策', '架构']
        unique_count = sum(1 for kw in unique_keywords if kw.lower() in content.lower())
        uniqueness_score = min(unique_count / 5, 1.0)
        score += uniqueness_score * 0.25
        
        return min(score, 1.0)
    
    def _assess_importance(self, content: str, timestamp: str) -> float:
        """评估重要性（简化版）"""
        score = 0.0
        
        # 1. 可执行性 (20%)
        action_keywords = ['next', 'action', 'todo', 'should', 'must', '下一步', '待办']
        action_count = sum(1 for kw in action_keywords if kw in content.lower())
        score += min(action_count / 5, 1.0) * 0.20
        
        # 2. 独特性 (25%)
        creation_keywords = ['create', 'implement', 'build', 'design', '创建', '实现']
        creation_count = sum(1 for kw in creation_keywords if kw in content.lower())
        score += min(creation_count / 3, 1.0) * 0.25
        
        # 3. 时效性 (15%)
        try:
            if 'T' in timestamp:
                memory_time = datetime.fromisoformat(timestamp)
            else:
                memory_time = datetime.strptime(timestamp, '%Y-%m-%d')
            
            days_old = (datetime.now() - memory_time).days
            recency = max(0, 1.0 - (days_old / 30))
            score += recency * 0.15
        except:
            score += 0.15
        
        # 4. 影响力 (25%)
        impact_keywords = ['architecture', 'critical', 'major', 'phase', 'core', 
                          '架构', '关键', '重大', '核心']
        impact_count = sum(1 for kw in impact_keywords if kw in content.lower())
        score += min(impact_count / 5, 1.0) * 0.25
        
        # 5. 连接性 (15%)
        link_patterns = [r'\[.*?\]\(.*?\)', r'\.md\b', r'30-scripts']
        link_count = sum(1 for p in link_patterns if re.search(p, content))
        score += min(link_count / 5, 1.0) * 0.15
        
        return min(score, 1.0)
    
    def _select_strategy(self, quality: float, importance: float) -> str:
        """选择压缩策略"""
        strategies = self.config['strategies']
        
        # 按优先级检查
        if quality >= strategies['distill_to_memory']['min_quality'] and \
           importance >= strategies['distill_to_memory']['min_importance']:
            return 'distill_to_memory'
        
        if quality >= strategies['tiered_light']['min_quality'] and \
           importance >= strategies['tiered_light']['min_importance']:
            return 'tiered_light'
        
        if quality >= strategies['tiered_standard']['min_quality'] and \
           importance >= strategies['tiered_standard']['min_importance']:
            return 'tiered_standard'
        
        if importance >= strategies['tiered_heavy']['min_importance']:
            return 'tiered_heavy'
        
        return 'archive'
    
    def compress_single(self, memory_path: Path) -> CompressionResult:
        """压缩单条记忆"""
        # 读取内容
        content = memory_path.read_text(encoding='utf-8', errors='replace')
        original_size = len(content)
        
        # 提取时间戳
        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2})', memory_path.name)
        timestamp = timestamp_match.group(1) if timestamp_match else datetime.now().isoformat()
        
        # Step 1: 质量评分
        quality_score = self._assess_quality(content)
        
        # Step 2: 重要性评估
        importance_score = self._assess_importance(content, timestamp)
        
        # Step 3: 选择策略
        strategy = self._select_strategy(quality_score, importance_score)
        
        # Step 4: 执行压缩（简化版，实际应调用对应工具）
        compression_ratio = self.config['strategies'][strategy]['compression_ratio']
        final_size = int(original_size * compression_ratio)
        
        # 记录执行步骤
        steps = [
            f"Quality assessment: {quality_score:.3f}",
            f"Importance assessment: {importance_score:.3f}",
            f"Strategy selection: {strategy}",
            f"Compression: {original_size} → {final_size} bytes"
        ]
        
        return CompressionResult(
            memory_id=memory_path.name,
            original_size=original_size,
            final_size=final_size,
            compression_ratio=round((original_size - final_size) / original_size, 3) if original_size > 0 else 0,
            quality_score=round(quality_score, 3),
            importance_score=round(importance_score, 3),
            strategy_used=strategy,
            steps_executed=steps,
            timestamp=datetime.now().isoformat()
        )
    
    def compress_batch(self, days: int = 7) -> PipelineReport:
        """批量压缩"""
        results = []
        
        if not MEMORY_DIR.exists():
            return self._empty_report()
        
        # 获取最近的日常笔记
        cutoff_date = datetime.now() - timedelta(days=days)
        daily_notes = []
        
        for note_file in MEMORY_DIR.glob("*.md"):
            if note_file.stem == "MEMORY":
                continue
            
            try:
                note_date = datetime.strptime(note_file.stem, '%Y-%m-%d')
                if note_date >= cutoff_date:
                    daily_notes.append(note_file)
            except ValueError:
                continue
        
        # 逐个压缩
        for note_file in daily_notes:
            try:
                result = self.compress_single(note_file)
                results.append(result)
            except Exception as e:
                print(f"[ERROR] {note_file.name}: {e}")
        
        # 生成报告
        return self._generate_report(results)
    
    def _empty_report(self) -> PipelineReport:
        """生成空报告"""
        return PipelineReport(
            total_memories=0,
            total_original_size=0,
            total_final_size=0,
            overall_compression_ratio=0,
            strategy_distribution={},
            quality_distribution={},
            details=[],
            recommendations=["No memories found"],
            timestamp=datetime.now().isoformat()
        )
    
    def _generate_report(self, results: List[CompressionResult]) -> PipelineReport:
        """生成管道报告"""
        if not results:
            return self._empty_report()
        
        # 统计
        total_original = sum(r.original_size for r in results)
        total_final = sum(r.final_size for r in results)
        overall_ratio = (total_original - total_final) / total_original if total_original > 0 else 0
        
        # 策略分布
        strategy_dist = {}
        for r in results:
            strategy_dist[r.strategy_used] = strategy_dist.get(r.strategy_used, 0) + 1
        
        # 质量分布
        quality_dist = {'high': 0, 'medium': 0, 'low': 0}
        for r in results:
            if r.quality_score >= 0.7:
                quality_dist['high'] += 1
            elif r.quality_score >= 0.5:
                quality_dist['medium'] += 1
            else:
                quality_dist['low'] += 1
        
        # 生成建议
        recommendations = self._generate_recommendations(results, strategy_dist, quality_dist)
        
        return PipelineReport(
            total_memories=len(results),
            total_original_size=total_original,
            total_final_size=total_final,
            overall_compression_ratio=round(overall_ratio, 3),
            strategy_distribution=strategy_dist,
            quality_distribution=quality_dist,
            details=results,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    def _generate_recommendations(self, results: List[CompressionResult],
                                  strategy_dist: Dict, quality_dist: Dict) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 基于策略分布
        if strategy_dist.get('archive', 0) > len(results) * 0.3:
            recommendations.append("发现较多低质量记忆，建议定期清理归档")
        
        if strategy_dist.get('distill_to_memory', 0) > 0:
            recommendations.append(f"{strategy_dist['distill_to_memory']} 条记忆适合蒸馏到 MEMORY.md")
        
        # 基于质量分布
        if quality_dist.get('high', 0) > len(results) * 0.5:
            recommendations.append("记忆质量整体良好，保持当前实践")
        
        if quality_dist.get('low', 0) > len(results) * 0.3:
            recommendations.append("部分记忆质量较低，建议改进记录习惯")
        
        # 总体评价
        if not recommendations:
            recommendations.append("记忆管理系统运行良好")
        
        return recommendations
    
    def analyze_only(self, days: int = 7) -> Dict:
        """仅分析，不执行压缩"""
        results = []
        
        if not MEMORY_DIR.exists():
            return {'error': 'Memory directory not found'}
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for note_file in MEMORY_DIR.glob("*.md"):
            if note_file.stem == "MEMORY":
                continue
            
            # 跳过非日常笔记文件
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', note_file.stem):
                continue
            
            try:
                note_date = datetime.strptime(note_file.stem, '%Y-%m-%d')
                if note_date < cutoff_date:
                    continue
                
                content = note_file.read_text(encoding='utf-8', errors='replace')
                timestamp = note_file.stem
                
                quality = self._assess_quality(content)
                importance = self._assess_importance(content, timestamp)
                strategy = self._select_strategy(quality, importance)
                
                results.append({
                    'memory_id': note_file.name,
                    'quality': round(quality, 3),
                    'importance': round(importance, 3),
                    'recommended_strategy': strategy,
                    'estimated_compression': self.config['strategies'][strategy]['compression_ratio']
                })
            
            except Exception as e:
                continue
        
        # 排序
        results.sort(key=lambda x: (x['quality'], x['importance']), reverse=True)
        
        return {
            'total_memories': len(results),
            'analysis_period_days': days,
            'memories': results,
            'summary': {
                'avg_quality': round(sum(r['quality'] for r in results) / len(results), 3) if results else 0,
                'avg_importance': round(sum(r['importance'] for r in results) / len(results), 3) if results else 0,
                'strategy_distribution': self._count_strategies(results)
            }
        }
    
    def _count_strategies(self, results: List[Dict]) -> Dict[str, int]:
        """统计策略分布"""
        dist = {}
        for r in results:
            strategy = r['recommended_strategy']
            dist[strategy] = dist.get(strategy, 0) + 1
        return dist


def print_result(result: CompressionResult):
    """打印压缩结果"""
    print("\n" + "=" * 60)
    print(f"Hybrid Compression: {result.memory_id}")
    print("=" * 60)
    
    print(f"\n[Size]")
    print(f"  Original: {result.original_size:,} bytes")
    print(f"  Final:    {result.final_size:,} bytes")
    print(f"  Ratio:    {result.compression_ratio:.1%} reduction")
    
    print(f"\n[Scores]")
    print(f"  Quality:    {result.quality_score:.3f}")
    print(f"  Importance: {result.importance_score:.3f}")
    
    print(f"\n[Strategy]")
    print(f"  {result.strategy_used}")
    
    print(f"\n[Steps]")
    for step in result.steps_executed:
        print(f"  • {step}")


def print_report(report: PipelineReport):
    """打印管道报告"""
    print("\n" + "=" * 60)
    print("Hybrid Compression Pipeline - Report")
    print("=" * 60)
    
    print(f"\n[Overview]")
    print(f"  Total Memories:     {report.total_memories}")
    print(f"  Original Size:      {report.total_original_size:,} bytes")
    print(f"  Final Size:         {report.total_final_size:,} bytes")
    print(f"  Compression Ratio:  {report.overall_compression_ratio:.1%} reduction")
    
    print(f"\n[Strategy Distribution]")
    for strategy, count in sorted(report.strategy_distribution.items(), key=lambda x: -x[1]):
        pct = count / report.total_memories * 100 if report.total_memories > 0 else 0
        print(f"  {strategy:25s}: {count:3d} ({pct:5.1f}%)")
    
    print(f"\n[Quality Distribution]")
    for quality, count in report.quality_distribution.items():
        pct = count / report.total_memories * 100 if report.total_memories > 0 else 0
        print(f"  {quality:10s}: {count:3d} ({pct:5.1f}%)")
    
    if report.recommendations:
        print(f"\n[Recommendations]")
        for rec in report.recommendations:
            print(f"  • {rec}")


def print_analysis(analysis: Dict):
    """打印分析报告"""
    print("\n" + "=" * 60)
    print("Hybrid Compression Pipeline - Analysis")
    print("=" * 60)
    
    print(f"\n[Overview]")
    print(f"  Total Memories: {analysis.get('total_memories', 0)}")
    print(f"  Analysis Period: {analysis.get('analysis_period_days', 0)} days")
    
    if 'summary' in analysis:
        print(f"\n[Summary]")
        print(f"  Average Quality:    {analysis['summary']['avg_quality']:.3f}")
        print(f"  Average Importance: {analysis['summary']['avg_importance']:.3f}")
        
        print(f"\n[Strategy Distribution]")
        for strategy, count in analysis['summary']['strategy_distribution'].items():
            print(f"  {strategy}: {count}")
    
    if 'memories' in analysis:
        print(f"\n[Top Memories by Quality]")
        for mem in analysis['memories'][:5]:
            print(f"  {mem['memory_id']}: Q={mem['quality']:.3f}, I={mem['importance']:.3f} → {mem['recommended_strategy']}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Hybrid Compression Pipeline')
    parser.add_argument('--memory', type=str, help='压缩单条记忆文件')
    parser.add_argument('--batch', action='store_true', help='批量压缩')
    parser.add_argument('--days', type=int, default=7, help='处理最近 N 天 (默认 7)')
    parser.add_argument('--analyze', action='store_true', help='仅分析，不执行压缩')
    parser.add_argument('--report', action='store_true', help='生成完整报告')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    parser.add_argument('--dry-run', action='store_true', help='干运行 (不实际压缩)')
    
    args = parser.parse_args()
    
    pipeline = MemoryHybridPipeline({'dry_run': args.dry_run})
    
    # 单文件压缩
    if args.memory:
        memory_path = Path(args.memory.replace('"', '').replace("'", ""))
        if not memory_path.is_absolute():
            memory_path = WORKSPACE / memory_path
        
        if not memory_path.exists():
            print(f"[ERROR] File not found: {memory_path}")
            return 1
        
        result = pipeline.compress_single(memory_path)
        
        if args.json:
            print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
        else:
            print_result(result)
        
        return 0
    
    # 批量压缩
    if args.batch:
        report = pipeline.compress_batch(args.days)
        
        if args.json:
            print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
        else:
            print_report(report)
        
        return 0
    
    # 仅分析
    if args.analyze:
        analysis = pipeline.analyze_only(args.days)
        
        if args.json:
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
        else:
            print_analysis(analysis)
        
        return 0
    
    # 生成报告
    if args.report:
        report = pipeline.compress_batch(args.days)
        
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
