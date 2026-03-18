#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
ENH-006: Innovation Pattern Matcher
创新者模式库自动匹配系统

功能:
- 识别重复/低效模式
- 自动匹配创新方案
- 提供具体实施建议
- 支持自定义模式库

使用示例:
    python innovation_pattern_matcher.py --task "Daily backup manual"
    python innovation_pattern_matcher.py --task "Running same query 5 times"
    python innovation_pattern_matcher.py --scan --dir D:\OpenClaw\workspace
"""

import argparse
import json
import sys
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Windows 控制台编码修复
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        os.system('chcp 65001 >nul')


@dataclass
class Task:
    name: str
    description: str = ""
    frequency: str = "once"  # once/daily/weekly/hourly
    manual_steps: int = 1
    time_cost: float = 1.0  # hours
    tools_used: List[str] = None
    
    def __post_init__(self):
        if self.tools_used is None:
            self.tools_used = []


@dataclass
class InnovationPattern:
    id: str
    name: str
    trigger_condition: str
    solution_template: str
    expected_improvement: str
    implementation_steps: List[str]
    tools_required: List[str]
    difficulty: str  # easy/medium/hard
    roi_multiplier: float  # ROI 倍数


class InnovationPatternMatcher:
    """创新者模式匹配器"""
    
    # 核心创新模式库
    PATTERNS = [
        InnovationPattern(
            id='AUTOMATE-001',
            name='自动化脚本',
            trigger_condition='重复操作≥3 次 或 每日执行',
            solution_template='创建 Python 脚本自动执行',
            expected_improvement='时间减少 90%+',
            implementation_steps=[
                "1. 记录手动操作步骤",
                "2. 识别可自动化环节",
                "3. 编写 Python 脚本",
                "4. 添加错误处理",
                "5. 设置定时触发 (cron/Task Scheduler)",
                "6. 测试并部署"
            ],
            tools_required=['Python', 'schedule/cron'],
            difficulty='medium',
            roi_multiplier=10.0
        ),
        
        InnovationPattern(
            id='BATCH-001',
            name='批量处理',
            trigger_condition='相似任务≥5 个 或 同类型操作',
            solution_template='合并为批量处理任务',
            expected_improvement='效率提升 5-10 倍',
            implementation_steps=[
                "1. 收集所有相似任务",
                "2. 提取共同参数",
                "3. 设计批量接口",
                "4. 实现并行/串行处理",
                "5. 添加进度追踪",
                "6. 生成汇总报告"
            ],
            tools_required=['Python', 'concurrent.futures'],
            difficulty='easy',
            roi_multiplier=5.0
        ),
        
        InnovationPattern(
            id='CACHE-001',
            name='智能缓存',
            trigger_condition='重复查询≥2 次 或 API 调用频繁',
            solution_template='实现多层缓存策略',
            expected_improvement='API 调用减少 70%+',
            implementation_steps=[
                "1. 识别重复查询模式",
                "2. 设计缓存键 (hash)",
                "3. 设置 TTL (过期时间)",
                "4. 实现缓存失效策略",
                "5. 添加缓存命中率监控",
                "6. 预热常用数据"
            ],
            tools_required=['Redis/内存缓存', 'hashlib'],
            difficulty='medium',
            roi_multiplier=7.0
        ),
        
        InnovationPattern(
            id='PARALLEL-001',
            name='并行执行',
            trigger_condition='独立任务≥3 个 或 串行耗时>30 分钟',
            solution_template='使用线程池/进程池并行化',
            expected_improvement='执行时间减少 60-80%',
            implementation_steps=[
                "1. 识别任务依赖关系",
                "2. 分组可并行任务",
                "3. 选择并发模型 (ThreadPool/ProcessPool)",
                "4. 实现并行执行器",
                "5. 添加结果聚合",
                "6. 处理异常和超时"
            ],
            tools_required=['concurrent.futures', 'asyncio'],
            difficulty='medium',
            roi_multiplier=4.0
        ),
        
        InnovationPattern(
            id='EXTERNALIZE-001',
            name='外部化存储',
            trigger_condition='大文件>1GB 或 依赖文件>1000 个',
            solution_template='移到外部存储 + 符号链接',
            expected_improvement='工作区文件减少 80%+',
            implementation_steps=[
                "1. 识别大文件/目录",
                "2. 选择存储方案 (云/外部硬盘)",
                "3. 迁移数据",
                "4. 创建符号链接",
                "5. 更新引用路径",
                "6. 验证功能正常"
            ],
            tools_required=['mklink', '云存储 API'],
            difficulty='easy',
            roi_multiplier=3.0
        ),
        
        InnovationPattern(
            id='TEMPLATE-001',
            name='模板化',
            trigger_condition='相似文档≥5 个 或 重复结构',
            solution_template='创建可复用模板',
            expected_improvement='创建时间减少 75%',
            implementation_steps=[
                "1. 分析文档共同结构",
                "2. 提取可变部分",
                "3. 设计模板语法",
                "4. 实现模板引擎",
                "5. 创建示例模板",
                "6. 文档化使用方法"
            ],
            tools_required=['Jinja2/string.Template'],
            difficulty='easy',
            roi_multiplier=6.0
        ),
        
        InnovationPattern(
            id='MONITOR-001',
            name='自动监控',
            trigger_condition='需人工检查≥2 次/天 或 关键指标',
            solution_template='部署自动监控 + 告警',
            expected_improvement='人工检查减少 95%',
            implementation_steps=[
                "1. 定义监控指标",
                "2. 设置采集频率",
                "3. 实现监控脚本",
                "4. 配置告警阈值",
                "5. 集成通知渠道 (飞书/邮件)",
                "6. 添加仪表盘可视化"
            ],
            tools_required=['prometheus/自定义', '飞书 API'],
            difficulty='medium',
            roi_multiplier=8.0
        ),
        
        InnovationPattern(
            id='VALIDATE-001',
            name='预操作验证',
            trigger_condition='破坏性操作 或 关键文件修改',
            solution_template='实现预操作钩子强制检查',
            expected_improvement='错误减少 100%',
            implementation_steps=[
                "1. 识别关键操作点",
                "2. 设计验证规则",
                "3. 实现 pre-hook 脚本",
                "4. 集成到工作流",
                "5. 设置强制阻止机制",
                "6. 添加审计日志"
            ],
            tools_required=['Git hooks/自定义拦截器'],
            difficulty='medium',
            roi_multiplier=15.0  # 防止灾难性错误
        ),
        
        InnovationPattern(
            id='DISTILL-001',
            name='自动蒸馏',
            trigger_condition='信息累积>10 条 或 知识碎片化',
            solution_template='定期自动提炼核心观点',
            expected_improvement='知识整理时间减少 85%',
            implementation_steps=[
                "1. 定义蒸馏触发条件",
                "2. 实现聚类算法",
                "3. 训练/配置摘要模型",
                "4. 设置定时任务",
                "5. 人工审核流程",
                "6. 自动更新知识库"
            ],
            tools_required=['LLM API', '聚类算法'],
            difficulty='hard',
            roi_multiplier=12.0
        ),
        
        InnovationPattern(
            id='MERGE-001',
            name='工具整合',
            trigger_condition='相似工具≥3 个 或 功能重叠',
            solution_template='合并为统一工具',
            expected_improvement='维护成本减少 60%',
            implementation_steps=[
                "1. 列出所有相似工具",
                "2. 分析功能重叠",
                "3. 设计统一接口",
                "4. 重构核心逻辑",
                "5. 迁移用户",
                "6. 废弃旧工具"
            ],
            tools_required=['重构工具', 'API 设计'],
            difficulty='hard',
            roi_multiplier=5.0
        )
    ]
    
    # 触发条件关键词映射
    TRIGGER_KEYWORDS = {
        'AUTOMATE-001': ['重复', 'manual', 'daily', '每天', '自动', 'automate'],
        'BATCH-001': ['批量', 'batch', '多个', 'similar', '同类型', '≥5'],
        'CACHE-001': ['重复查询', 'cache', 'API', '调用', 'query', '缓存'],
        'PARALLEL-001': ['并行', 'parallel', '独立', 'independent', '串行', 'slow'],
        'EXTERNALIZE-001': ['大文件', 'large', 'GB', '文件数', 'node_modules'],
        'TEMPLATE-001': ['模板', 'template', '文档', 'document', '结构', 'similar'],
        'MONITOR-001': ['监控', 'monitor', '检查', 'check', '告警', 'alert'],
        'VALIDATE-001': ['验证', 'validate', '检查', 'critical', '关键', 'hook'],
        'DISTILL-001': ['蒸馏', 'distill', '提炼', '总结', '累积', '碎片'],
        'MERGE-001': ['整合', 'merge', '多个工具', '重叠', 'duplicate', 'unify']
    }
    
    def match(self, task: Task) -> List[Dict]:
        """匹配最佳创新方案"""
        matched_patterns = []
        
        # 文本匹配
        text_to_analyze = f"{task.name} {task.description}".lower()
        
        for pattern in self.PATTERNS:
            score = self._calculate_match_score(text_to_analyze, pattern)
            
            # 频率匹配
            frequency_bonus = self._check_frequency_match(task.frequency, pattern.id)
            
            # 工作量匹配
            effort_bonus = self._check_effort_match(task.manual_steps, task.time_cost, pattern.id)
            
            total_score = score + frequency_bonus + effort_bonus
            
            if total_score >= 0.3:  # 阈值 30%
                matched_patterns.append({
                    'pattern': pattern,
                    'match_score': round(total_score * 100, 2),
                    'confidence': 'high' if total_score >= 0.7 else 'medium' if total_score >= 0.5 else 'low'
                })
        
        # 按分数排序
        matched_patterns.sort(key=lambda x: x['match_score'], reverse=True)
        
        return matched_patterns
    
    def _calculate_match_score(self, text: str, pattern: InnovationPattern) -> float:
        """计算文本匹配分数"""
        keywords = self.TRIGGER_KEYWORDS.get(pattern.id, [])
        
        matches = sum(1 for kw in keywords if kw.lower() in text)
        return min(1.0, matches / max(len(keywords), 1))
    
    def _check_frequency_match(self, frequency: str, pattern_id: str) -> float:
        """检查频率匹配加分"""
        high_frequency = ['daily', 'hourly', 'weekly']
        
        if frequency in high_frequency and 'AUTOMATE' in pattern_id:
            return 0.2  # 高频任务 + 自动化 = 强匹配
        elif frequency == 'once' and 'TEMPLATE' in pattern_id:
            return 0.1
        
        return 0.0
    
    def _check_effort_match(self, manual_steps: int, time_cost: float, pattern_id: str) -> float:
        """检查工作量匹配加分"""
        if manual_steps >= 5 and 'AUTOMATE' in pattern_id:
            return 0.15
        elif time_cost >= 2.0 and 'AUTOMATE' in pattern_id:
            return 0.1
        elif manual_steps >= 3 and 'BATCH' in pattern_id:
            return 0.1
        
        return 0.0
    
    def scan_directory(self, directory: Path) -> List[Dict]:
        """扫描目录识别优化机会"""
        opportunities = []
        
        # 扫描 Python 脚本
        py_files = list(directory.rglob('*.py'))
        
        # 检查重复代码模式
        # (简化版 - 实际应使用 AST 分析)
        script_names = [f.stem for f in py_files]
        
        # 查找相似命名的脚本
        for i, name1 in enumerate(script_names):
            for name2 in script_names[i+1:]:
                similarity = self._string_similarity(name1, name2)
                if similarity > 0.6:
                    opportunities.append({
                        'type': 'MERGE-001',
                        'files': [str(py_files[i]), str(py_files[script_names.index(name2)])],
                        'reason': f'相似命名：{name1} vs {name2} (相似度 {similarity:.0%})',
                        'suggestion': '考虑合并为统一工具'
                    })
        
        # 查找大文件
        for file in directory.rglob('*'):
            if file.is_file():
                try:
                    size_mb = file.stat().st_size / 1024 / 1024
                    if size_mb > 100:  # >100MB
                        opportunities.append({
                            'type': 'EXTERNALIZE-001',
                            'file': str(file),
                            'size_mb': round(size_mb, 2),
                            'suggestion': '考虑移到外部存储'
                        })
                except:
                    pass
        
        return opportunities
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """计算字符串相似度 (简化版)"""
        s1, s2 = s1.lower(), s2.lower()
        common = sum(1 for c in s1 if c in s2)
        return common / max(len(s1), len(s2), 1)
    
    def generate_implementation_plan(self, pattern_id: str, context: Dict) -> Dict:
        """生成详细实施计划"""
        pattern = next((p for p in self.PATTERNS if p.id == pattern_id), None)
        
        if not pattern:
            return {'error': 'Pattern not found'}
        
        # 估算 ROI
        estimated_hours_saved = context.get('current_time_cost', 1) * pattern.roi_multiplier
        implementation_cost = {'easy': 2, 'medium': 5, 'hard': 10}.get(pattern.difficulty, 5)
        payback_days = implementation_cost / max(estimated_hours_saved, 0.1)
        
        return {
            'pattern': pattern.name,
            'id': pattern.id,
            'difficulty': pattern.difficulty,
            'implementation_steps': pattern.implementation_steps,
            'tools_required': pattern.tools_required,
            'expected_improvement': pattern.expected_improvement,
            'roi_analysis': {
                'roi_multiplier': pattern.roi_multiplier,
                'estimated_hours_saved': round(estimated_hours_saved, 2),
                'implementation_cost_hours': implementation_cost,
                'payback_days': round(payback_days, 1)
            },
            'next_action': pattern.implementation_steps[0]
        }


def main():
    parser = argparse.ArgumentParser(description='Innovation Pattern Matcher - ENH-006')
    parser.add_argument('--task', type=str, help='任务描述')
    parser.add_argument('--desc', type=str, default='', help='详细描述')
    parser.add_argument('--freq', type=str, default='once',
                        choices=['once', 'daily', 'weekly', 'hourly'],
                        help='执行频率')
    parser.add_argument('--steps', type=int, default=1, help='手动步骤数')
    parser.add_argument('--time', type=float, default=1.0, help='耗时 (小时)')
    parser.add_argument('--scan', action='store_true', help='扫描目录模式')
    parser.add_argument('--dir', type=str, default=str(Path(__file__).parent.parent), help='扫描目录')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    matcher = InnovationPatternMatcher()
    
    # 扫描模式
    if args.scan:
        directory = Path(args.dir)
        opportunities = matcher.scan_directory(directory)
        
        if args.json:
            print(json.dumps(opportunities, indent=2, ensure_ascii=False))
        else:
            print(f"\n{'='*60}")
            print(f"[SEARCH] 目录扫描结果 (共 {len(opportunities)} 个优化机会)")
            print(f"{'='*60}\n")
            
            for i, opp in enumerate(opportunities, 1):
                print(f"{i}. [{opp['type']}] {opp.get('reason', opp.get('file', 'Unknown'))}")
                print(f"   建议：{opp['suggestion']}")
                print()
        
        return
    
    # 任务匹配模式
    if not args.task:
        parser.print_help()
        return
    
    task = Task(
        name=args.task,
        description=args.desc,
        frequency=args.freq,
        manual_steps=args.steps,
        time_cost=args.time
    )
    
    matches = matcher.match(task)
    
    if args.json:
        output = []
        for m in matches:
            output.append({
                'pattern_id': m['pattern'].id,
                'pattern_name': m['pattern'].name,
                'match_score': m['match_score'],
                'confidence': m['confidence'],
                'trigger_condition': m['pattern'].trigger_condition,
                'solution': m['pattern'].solution_template,
                'expected_improvement': m['pattern'].expected_improvement,
                'roi_multiplier': m['pattern'].roi_multiplier
            })
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*60}")
        print(f"[IDEA] 创新方案匹配结果 (共 {len(matches)} 个)")
        print(f"{'='*60}\n")
        
        if not matches:
            print("未找到匹配的创新方案 - 可能需要人工分析")
        else:
            for i, m in enumerate(matches, 1):
                p = m['pattern']
                print(f"{i}. [TARGET] [{m['confidence'].upper()}] {p.name} ({p.id})")
                print(f"   匹配度：{m['match_score']}%")
                print(f"   触发条件：{p.trigger_condition}")
                print(f"   解决方案：{p.solution_template}")
                print(f"   预期提升：{p.expected_improvement}")
                print(f"   ROI 倍数：{p.roi_multiplier}x")
                print(f"   难度：{p.difficulty.upper()}")
                
                # 显示前 3 步实施步骤
                print(f"   实施步骤 (前 3 步):")
                for step in p.implementation_steps[:3]:
                    print(f"     - {step}")
                print()
        
        # 推荐最佳方案
        if matches:
            best = matches[0]
            print(f"{'='*60}")
            print(f"🏆 推荐方案：{best['pattern'].name}")
            print(f"   下一步：{best['pattern'].implementation_steps[0]}")
            print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
