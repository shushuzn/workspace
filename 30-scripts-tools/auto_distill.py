#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ENH-004: Memory Auto-Distill Trigger
学习者 - 自动蒸馏触发器

功能:
- 监控日常笔记累积数量
- 识别高价值洞察（用户打分≥90）
- 主题聚类（相似内容≥5 条）
- 自动触发蒸馏流程
- 通知用户审核

使用示例:
    python auto_distill.py --check
    python auto_distill.py --trigger --force
    python auto_distill.py --scan --days 7
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict
import hashlib
import subprocess
import re

# Windows 控制台编码修复
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        subprocess.run(['chcp', '65001'], capture_output=True, shell=True)


@dataclass
class MemorySnippet:
    id: str
    file_path: str
    content: str
    created_at: datetime
    tags: List[str] = field(default_factory=list)
    category: str = 'general'
    user_score: Optional[float] = None
    similarity_score: float = 0.0
    is_high_value: bool = False


@dataclass
class DistillTrigger:
    trigger_id: str
    trigger_type: str  # quantity/quality/clustering
    trigger_condition: str
    matched_items: List[str]
    confidence: float
    recommended_action: str
    estimated_time: str


class MemoryDistillTrigger:
    """记忆蒸馏触发器"""
    
    # 触发条件配置
    TRIGGER_CONFIG = {
        'quantity': {
            'min_notes': 10,
            'description': '日常笔记累积≥10 条'
        },
        'quality': {
            'min_score': 90,
            'min_items': 3,
            'description': '高价值洞察（≥90 分）≥3 条'
        },
        'clustering': {
            'min_similar': 5,
            'similarity_threshold': 0.7,
            'description': '相似内容≥5 条'
        }
    }
    
    def __init__(self, workspace_dir: str = str(Path(__file__).parent.parent)):
        self.workspace_dir = Path(workspace_dir)
        self.memory_dir = self.workspace_dir / '13-memory-记忆系统'
        self.daily_notes_dir = self.memory_dir
        self.distill_log_file = self.workspace_dir / '.distill_log.json'
        self.snippets: List[MemorySnippet] = []
        self.triggers: List[DistillTrigger] = []
    
    def scan_daily_notes(self, days: int = 7) -> List[MemorySnippet]:
        """扫描最近 N 天的日常笔记"""
        snippets = []
        today = datetime.now()
        
        # 扫描 memory/ 目录下的 Markdown 文件
        if not self.daily_notes_dir.exists():
            print(f"Warning: Memory directory not found: {self.daily_notes_dir}")
            return snippets
        
        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            # 查找匹配的文件
            patterns = [
                f"{date_str}.md",
                f"memory/{date_str}.md",
                f"2026-03-{date.day:02d}.md"
            ]
            
            for pattern in patterns:
                file_path = self.daily_notes_dir / pattern
                if file_path.exists():
                    snippet = self._parse_note_file(file_path, date)
                    if snippet:
                        snippets.append(snippet)
                    break
        
        # 也扫描 MEMORY.md 中的新条目
        memory_file = self.workspace_dir / 'MEMORY.md'
        if memory_file.exists():
            memory_snippets = self._parse_memory_file(memory_file, days)
            snippets.extend(memory_snippets)
        
        self.snippets = snippets
        return snippets
    
    def _parse_note_file(self, file_path: Path, date: datetime) -> Optional[MemorySnippet]:
        """解析单个笔记文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标签
            tags = re.findall(r'#(\w+)', content)
            
            # 提取分类
            category = 'general'
            if '教训' in content or 'LESSON' in content:
                category = 'lesson'
            elif '配置' in content or 'CONFIG' in content:
                category = 'config'
            elif '研究' in content or 'RESEARCH' in content:
                category = 'research'
            
            # 检查用户打分
            user_score = None
            score_match = re.search(r'评分 [::]\s*(\d+)', content)
            if score_match:
                user_score = float(score_match.group(1))
            
            snippet_id = hashlib.md5(f"{file_path}:{date}".encode()).hexdigest()[:8]
            
            return MemorySnippet(
                id=snippet_id,
                file_path=str(file_path),
                content=content[:500],  # 只取前 500 字符
                created_at=date,
                tags=tags,
                category=category,
                user_score=user_score,
                is_high_value=user_score is not None and user_score >= 90
            )
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def _parse_memory_file(self, file_path: Path, days: int) -> List[MemorySnippet]:
        """解析 MEMORY.md 文件"""
        snippets = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取最近添加的教训条目
            lesson_pattern = r'\[([A-Z]+-\d+)\]\s*([^\n]+)'
            matches = re.findall(lesson_pattern, content)
            
            for lesson_id, lesson_content in matches[-10:]:  # 最近 10 条
                snippet_id = hashlib.md5(f"{lesson_id}:{lesson_content}".encode()).hexdigest()[:8]
                
                snippets.append(MemorySnippet(
                    id=snippet_id,
                    file_path=str(file_path),
                    content=lesson_content,
                    created_at=datetime.now(),
                    tags=[lesson_id.split('-')[0]],
                    category='lesson',
                    is_high_value=True
                ))
        
        except Exception as e:
            print(f"Error parsing MEMORY.md: {e}")
        
        return snippets
    
    def check_quantity_trigger(self) -> Optional[DistillTrigger]:
        """检查数量触发条件"""
        config = self.TRIGGER_CONFIG['quantity']
        min_notes = config['min_notes']
        
        if len(self.snippets) >= min_notes:
            trigger = DistillTrigger(
                trigger_id=hashlib.md5(f"quantity_{len(self.snippets)}".encode()).hexdigest()[:8],
                trigger_type='quantity',
                trigger_condition=f"日常笔记累积≥{min_notes}条",
                matched_items=[s.id for s in self.snippets],
                confidence=min(1.0, len(self.snippets) / (min_notes * 2)),
                recommended_action=f"触发蒸馏：{len(self.snippets)}条笔记待处理",
                estimated_time=f"{len(self.snippets) * 2}分钟"
            )
            self.triggers.append(trigger)
            return trigger
        
        return None
    
    def check_quality_trigger(self) -> Optional[DistillTrigger]:
        """检查质量触发条件"""
        config = self.TRIGGER_CONFIG['quality']
        min_score = config['min_score']
        min_items = config['min_items']
        
        high_value_snippets = [s for s in self.snippets if s.is_high_value]
        
        if len(high_value_snippets) >= min_items:
            trigger = DistillTrigger(
                trigger_id=hashlib.md5(f"quality_{len(high_value_snippets)}".encode()).hexdigest()[:8],
                trigger_type='quality',
                trigger_condition=f"高价值洞察（≥{min_score}分）≥{min_items}条",
                matched_items=[s.id for s in high_value_snippets],
                confidence=min(1.0, len(high_value_snippets) / (min_items * 2)),
                recommended_action=f"优先蒸馏：{len(high_value_snippets)}条高价值内容",
                estimated_time=f"{len(high_value_snippets) * 3}分钟"
            )
            self.triggers.append(trigger)
            return trigger
        
        return None
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简化版）"""
        # 提取关键词
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        # Jaccard 相似度
        intersection = words1 & words2
        union = words1 | words2
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def check_clustering_trigger(self) -> List[DistillTrigger]:
        """检查聚类触发条件"""
        config = self.TRIGGER_CONFIG['clustering']
        min_similar = config['min_similar']
        threshold = config['similarity_threshold']
        
        triggers = []
        
        # 按类别分组
        category_groups = defaultdict(list)
        for snippet in self.snippets:
            category_groups[snippet.category].append(snippet)
        
        # 检查每个类别内的相似度
        for category, snippets in category_groups.items():
            if len(snippets) < min_similar:
                continue
            
            # 计算两两相似度
            similar_groups = []
            current_group = [snippets[0]]
            
            for i in range(1, len(snippets)):
                snippet = snippets[i]
                avg_similarity = sum(
                    self.calculate_similarity(snippet.content, s.content)
                    for s in current_group
                ) / len(current_group)
                
                if avg_similarity >= threshold:
                    current_group.append(snippet)
                else:
                    if len(current_group) >= min_similar:
                        similar_groups.append(current_group)
                    current_group = [snippet]
            
            # 检查最后一组
            if len(current_group) >= min_similar:
                similar_groups.append(current_group)
            
            # 为每个相似组创建触发器
            for group in similar_groups:
                trigger_id = hashlib.md5(
                    f"cluster_{category}_{'_'.join(s.id for s in group)}".encode()
                ).hexdigest()[:8]
                
                trigger = DistillTrigger(
                    trigger_id=trigger_id,
                    trigger_type='clustering',
                    trigger_condition=f"相似内容（{category}）≥{min_similar}条",
                    matched_items=[s.id for s in group],
                    confidence=min(1.0, len(group) / (min_similar * 2)),
                    recommended_action=f"聚类蒸馏：{len(group)}条相似{category}内容",
                    estimated_time=f"{len(group) * 2}分钟"
                )
                triggers.append(trigger)
                self.triggers.append(trigger)
        
        return triggers
    
    def check_all_triggers(self) -> List[DistillTrigger]:
        """检查所有触发条件"""
        self.triggers = []
        
        # 扫描笔记
        self.scan_daily_notes(days=7)
        
        # 检查各类型触发器
        self.check_quantity_trigger()
        self.check_quality_trigger()
        self.check_clustering_trigger()
        
        return self.triggers
    
    def should_distill(self) -> bool:
        """判断是否应该触发蒸馏"""
        if not self.triggers:
            self.check_all_triggers()
        
        # 有任何高置信度触发器就蒸馏
        high_confidence = [t for t in self.triggers if t.confidence >= 0.5]
        return len(high_confidence) > 0
    
    def trigger_distillation(self) -> Dict:
        """触发蒸馏流程"""
        if not self.triggers:
            self.check_all_triggers()
        
        if not self.triggers:
            return {
                'status': 'no_trigger',
                'message': '未达到蒸馏触发条件'
            }
        
        # 生成蒸馏任务
        distill_task = {
            'task_id': hashlib.md5(f"distill_{datetime.now()}".encode()).hexdigest()[:8],
            'created_at': datetime.now().isoformat(),
            'triggers': [
                {
                    'id': t.trigger_id,
                    'type': t.trigger_type,
                    'condition': t.trigger_condition,
                    'confidence': t.confidence,
                    'matched_items': t.matched_items
                }
                for t in self.triggers
            ],
            'total_items': len(set(item for t in self.triggers for item in t.matched_items)),
            'estimated_time': self._estimate_total_time(),
            'recommended_priority': self._calculate_priority(),
            'next_steps': [
                "1. 运行 memory-distiller.py --auto",
                "2. 审核蒸馏结果",
                "3. 更新 MEMORY.md",
                "4. 记录蒸馏日志"
            ]
        }
        
        # 记录到日志
        self._log_distill_task(distill_task)
        
        return distill_task
    
    def _estimate_total_time(self) -> str:
        """估算总时间"""
        total_minutes = sum(
            int(t.estimated_time.replace('分钟', '0') or '0')
            for t in self.triggers
        )
        return f"{total_minutes}分钟"
    
    def _calculate_priority(self) -> str:
        """计算优先级"""
        max_confidence = max(t.confidence for t in self.triggers) if self.triggers else 0
        
        if max_confidence >= 0.8:
            return 'P0'
        elif max_confidence >= 0.6:
            return 'P1'
        elif max_confidence >= 0.4:
            return 'P2'
        else:
            return 'P3'
    
    def _log_distill_task(self, task: Dict):
        """记录蒸馏任务到日志"""
        log_data = {
            'logged_at': datetime.now().isoformat(),
            'task': task
        }
        
        # 追加到日志文件
        log_entries = []
        if self.distill_log_file.exists():
            try:
                with open(self.distill_log_file, 'r', encoding='utf-8') as f:
                    log_entries = json.load(f)
            except:
                log_entries = []
        
        log_entries.append(log_data)
        
        with open(self.distill_log_file, 'w', encoding='utf-8') as f:
            json.dump(log_entries, f, indent=2, ensure_ascii=False)
    
    def notify_user(self, method: str = 'console') -> str:
        """通知用户"""
        if not self.triggers:
            return "无蒸馏触发"
        
        message = f"\n{'='*60}\n"
        message += "[MEMORY DISTILL] 蒸馏触发通知\n"
        message += f"{'='*60}\n"
        message += f"触发器数量：{len(self.triggers)}\n"
        message += f"待处理条目：{len(set(item for t in self.triggers for item in t.matched_items))}\n\n"
        
        for i, trigger in enumerate(self.triggers, 1):
            message += f"{i}. [{trigger.trigger_type.upper()}] {trigger.trigger_condition}\n"
            message += f"   置信度：{trigger.confidence*100:.1f}%\n"
            message += f"   建议：{trigger.recommended_action}\n"
            message += f"   估算时间：{trigger.estimated_time}\n\n"
        
        message += f"{'='*60}\n"
        message += "下一步：运行 python auto_distill.py --trigger\n"
        message += f"{'='*60}\n"
        
        if method == 'console':
            print(message)
        
        return message


def main():
    parser = argparse.ArgumentParser(description='Memory Auto-Distill Trigger - ENH-004')
    parser.add_argument('--check', action='store_true', help='检查触发条件')
    parser.add_argument('--trigger', action='store_true', help='触发蒸馏流程')
    parser.add_argument('--force', action='store_true', help='强制触发（忽略条件）')
    parser.add_argument('--scan', action='store_true', help='扫描模式')
    parser.add_argument('--days', type=int, default=7, help='扫描天数')
    parser.add_argument('--workspace', type=str, default=str(Path(__file__).parent.parent),
                        help='工作区目录')
    parser.add_argument('--json', action='store_true', help='JSON 输出')
    
    args = parser.parse_args()
    
    trigger_system = MemoryDistillTrigger(args.workspace)
    
    # 扫描模式
    if args.scan:
        snippets = trigger_system.scan_daily_notes(days=args.days)
        
        if args.json:
            output = {
                'scanned_days': args.days,
                'total_snippets': len(snippets),
                'by_category': {},
                'high_value_count': sum(1 for s in snippets if s.is_high_value),
                'snippets': [
                    {
                        'id': s.id,
                        'category': s.category,
                        'tags': s.tags,
                        'user_score': s.user_score,
                        'is_high_value': s.is_high_value
                    }
                    for s in snippets
                ]
            }
            # 按类别统计
            for snippet in snippets:
                cat = snippet.category
                output['by_category'][cat] = output['by_category'].get(cat, 0) + 1
            
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print(f"\n{'='*60}")
            print(f"[SCAN] 扫描结果（最近{args.days}天）")
            print(f"{'='*60}")
            print(f"总笔记数：{len(snippets)}")
            print(f"高价值内容：{sum(1 for s in snippets if s.is_high_value)}")
            print(f"\n按类别:")
            by_cat = defaultdict(int)
            for s in snippets:
                by_cat[s.category] += 1
            for cat, count in by_cat.items():
                print(f"  - {cat}: {count}")
            print(f"{'='*60}\n")
        return
    
    # 检查模式
    if args.check:
        triggers = trigger_system.check_all_triggers()
        should_distill = trigger_system.should_distill()
        
        if args.json:
            output = {
                'should_distill': should_distill,
                'trigger_count': len(triggers),
                'triggers': [
                    {
                        'id': t.trigger_id,
                        'type': t.trigger_type,
                        'condition': t.trigger_condition,
                        'confidence': t.confidence,
                        'recommended_action': t.recommended_action
                    }
                    for t in triggers
                ]
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            trigger_system.notify_user('console')
        return
    
    # 触发模式
    if args.trigger:
        if args.force:
            # 强制触发
            result = trigger_system.trigger_distillation()
        else:
            # 先检查
            trigger_system.check_all_triggers()
            if not trigger_system.should_distill():
                print("\n[INFO] 未达到蒸馏触发条件，使用 --force 强制触发\n")
                return
            result = trigger_system.trigger_distillation()
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\n{'='*60}")
            print(f"[TRIGGER] 蒸馏任务已创建")
            print(f"{'='*60}")
            print(f"任务 ID: {result.get('task_id', 'N/A')}")
            print(f"触发器：{result.get('triggers', []) and len(result['triggers'])} 个")
            print(f"待处理：{result.get('total_items', 0)} 条目")
            print(f"估算时间：{result.get('estimated_time', 'N/A')}")
            print(f"优先级：{result.get('recommended_priority', 'N/A')}")
            print(f"\n下一步:")
            for step in result.get('next_steps', []):
                print(f"  {step}")
            print(f"{'='*60}\n")
        return
    
    # 默认：显示帮助
    parser.print_help()


if __name__ == '__main__':
    main()
