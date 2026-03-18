#!/usr/bin/env python3
"""
效果追踪器 - 验证改进是否有效

记录改进前后的用户反馈，分析效果
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path


class EffectTracker:
    """效果追踪器"""
    
    def __init__(self):
        self.tracker_file = Path('memory/effect_tracker.json')
        self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载追踪记录
        self.records = self._load_records()
    
    def _load_records(self) -> list:
        """加载记录"""
        if self.tracker_file.exists():
            with open(self.tracker_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_records(self):
        """保存记录"""
        with open(self.tracker_file, 'w', encoding='utf-8') as f:
            json.dump(self.records[-200:], f, ensure_ascii=False, indent=2)
    
    def record_improvement(self, improvement_type: str, before_config: Dict):
        """记录改进实施"""
        record = {
            'type': 'improvement',
            'improvement_type': improvement_type,
            'before_config': before_config,
            'timestamp': datetime.now().isoformat(),
            'before_signals': [],  # 改进前的负面信号
            'after_signals': []    # 改进后的负面信号
        }
        
        self.records.append(record)
        self._save_records()
        
        return len(self.records) - 1  # 返回记录索引
    
    def record_signal_after_improvement(self, record_index: int, signal: Dict):
        """记录改进后的信号"""
        if record_index < len(self.records):
            self.records[record_index]['after_signals'].append(signal)
            self._save_records()
    
    def analyze_effect(self, record_index: int) -> Dict:
        """分析改进效果"""
        if record_index >= len(self.records):
            return {'error': '记录不存在'}
        
        record = self.records[record_index]
        
        # 统计改进前后的负面信号数量
        before_count = len(record.get('before_signals', []))
        after_count = len(record.get('after_signals', []))
        
        # 计算效果
        if before_count == 0:
            effect = 'no_data'
        elif after_count < before_count:
            effect = 'improved'
        elif after_count == before_count:
            effect = 'no_change'
        else:
            effect = 'worse'
        
        # 计算改进百分比
        if before_count > 0:
            improvement_rate = (before_count - after_count) / before_count * 100
        else:
            improvement_rate = 0
        
        return {
            'effect': effect,
            'before_count': before_count,
            'after_count': after_count,
            'improvement_rate': improvement_rate,
            'record': record
        }
    
    def get_effective_improvements(self) -> List[Dict]:
        """获取有效的改进"""
        effective = []
        
        for i, record in enumerate(self.records):
            if record['type'] == 'improvement':
                analysis = self.analyze_effect(i)
                if analysis.get('effect') == 'improved':
                    effective.append({
                        'index': i,
                        'type': record['improvement_type'],
                        'improvement_rate': analysis['improvement_rate'],
                        'timestamp': record['timestamp']
                    })
        
        return effective
    
    def get_ineffective_improvements(self) -> List[Dict]:
        """获取无效的改进"""
        ineffective = []
        
        for i, record in enumerate(self.records):
            if record['type'] == 'improvement':
                analysis = self.analyze_effect(i)
                if analysis.get('effect') == 'worse':
                    ineffective.append({
                        'index': i,
                        'type': record['improvement_type'],
                        'worse_rate': -analysis['improvement_rate'],
                        'timestamp': record['timestamp']
                    })
        
        return ineffective


# 全局追踪器
global_tracker = EffectTracker()


def track_improvement(improvement_type: str, config: Dict) -> int:
    """便捷函数：记录改进"""
    return global_tracker.record_improvement(improvement_type, config)


def track_signal_after(index: int, signal: Dict):
    """便捷函数：记录改进后信号"""
    global_tracker.record_signal_after_improvement(index, signal)


def analyze(index: int) -> Dict:
    """便捷函数：分析效果"""
    return global_tracker.analyze_effect(index)


# 测试
if __name__ == '__main__':
    tracker = EffectTracker()
    
    print("测试效果追踪器")
    print("=" * 50)
    
    # 重置记录
    tracker.records = []
    tracker._save_records()
    
    # 测试 1: 记录改进
    print("\n测试 1: 记录改进 (确认优先模式)")
    config = {'confirm_before_execute': True}
    index = tracker.record_improvement('confirm_first', config)
    print(f"记录索引：{index}")
    
    # 添加改进前的信号
    tracker.records[index]['before_signals'] = [{'sentiment': 'negative'} for _ in range(3)]
    tracker._save_records()
    
    # 测试 2: 记录改进后的信号
    print("\n测试 2: 记录改进后的信号")
    for i in range(5):
        signal = {
            'sentiment': 'negative' if i < 2 else 'positive',
            'type': 'understanding' if i < 2 else 'satisfied'
        }
        tracker.record_signal_after_improvement(index, signal)
        print(f"记录信号{i+1}: {signal['sentiment']}")
    
    # 测试 3: 分析效果
    print("\n测试 3: 分析效果")
    analysis = tracker.analyze_effect(index)
    print(f"效果：{analysis['effect']}")
    print(f"改进前负面信号：{analysis['before_count']}")
    print(f"改进后负面信号：{analysis['after_count']}")
    print(f"改进率：{analysis['improvement_rate']:.1f}%")
    
    # 测试 4: 获取有效改进
    print("\n测试 4: 获取有效改进")
    effective = tracker.get_effective_improvements()
    print(f"有效改进数：{len(effective)}")
    
    print("\n测试完成！")
