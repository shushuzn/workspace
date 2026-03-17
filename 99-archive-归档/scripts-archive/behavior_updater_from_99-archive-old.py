#!/usr/bin/env python3
"""
行为更新器 - 根据学习信号实际更新 AI 行为

连接信号提取 → 行为配置 → 实际执行
"""

from typing import Dict, Optional
from datetime import datetime
import json
from pathlib import Path


class BehaviorUpdater:
    """行为更新器"""
    
    def __init__(self):
        self.config_file = Path('memory/behavior_config.json')
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载当前配置
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'confirm_before_execute': False,
            'report_progress': False,
            'keep_current': True,
            'updated_at': None
        }
    
    def _save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def update(self, signal: Dict):
        """
        根据信号更新行为
        
        逻辑:
        1. 负面信号 → 增加对应改进计数
        2. 计数达到阈值 → 更新行为配置
        3. 正面信号 → 保持当前方式
        """
        sentiment = signal.get('sentiment', 'neutral')
        improvement_type = signal.get('improvement_type', 'other')
        action = signal.get('action', '')
        
        # 初始化计数器
        if 'counts' not in self.config:
            self.config['counts'] = {
                'confirm_before_execute': 0,
                'report_progress': 0,
                'keep_current': 0
            }
        
        # 更新计数
        if action in self.config['counts']:
            self.config['counts'][action] += 1
        
        # 检查是否需要更新配置
        threshold = 3  # 3 次同样信号触发更新
        
        if action == 'confirm_before_execute' and self.config['counts'][action] >= threshold:
            self.config['confirm_before_execute'] = True
            self.config['report_progress'] = False
            self.config['keep_current'] = False
            self.config['updated_at'] = datetime.now().isoformat()
            self.config['update_reason'] = f'理解错误信号{self.config["counts"][action]}次'
        
        elif action == 'report_progress' and self.config['counts'][action] >= threshold:
            self.config['confirm_before_execute'] = False
            self.config['report_progress'] = True
            self.config['keep_current'] = False
            self.config['updated_at'] = datetime.now().isoformat()
            self.config['update_reason'] = f'速度慢信号{self.config["counts"][action]}次'
        
        elif action == 'keep_current' and self.config['counts'][action] >= threshold:
            self.config['confirm_before_execute'] = False
            self.config['report_progress'] = False
            self.config['keep_current'] = True
            self.config['updated_at'] = datetime.now().isoformat()
            self.config['update_reason'] = f'满意信号{self.config["counts"][action]}次'
        
        self._save_config()
    
    def should_confirm(self) -> bool:
        """是否应该先确认再执行"""
        return self.config.get('confirm_before_execute', False)
    
    def should_report_progress(self) -> bool:
        """是否应该报告进度"""
        return self.config.get('report_progress', False)
    
    def get_current_mode(self) -> str:
        """获取当前模式"""
        if self.config.get('confirm_before_execute'):
            return 'confirm_first'
        elif self.config.get('report_progress'):
            return 'report_progress'
        else:
            return 'normal'
    
    def reset_counts(self):
        """重置计数"""
        if 'counts' in self.config:
            self.config['counts'] = {
                'confirm_before_execute': 0,
                'report_progress': 0,
                'keep_current': 0
            }
            self._save_config()


# 全局更新器
global_updater = BehaviorUpdater()


def update_behavior(signal: Dict):
    """便捷函数：更新行为"""
    global_updater.update(signal)


def get_behavior_mode() -> str:
    """便捷函数：获取行为模式"""
    return global_updater.get_current_mode()


def should_confirm() -> bool:
    """便捷函数：是否应该确认"""
    return global_updater.should_confirm()


def should_report_progress() -> bool:
    """便捷函数：是否应该报告进度"""
    return global_updater.should_report_progress()


# 测试
if __name__ == '__main__':
    updater = BehaviorUpdater()
    
    print("测试行为更新器")
    print("=" * 50)
    
    # 重置配置
    updater.reset_counts()
    
    # 模拟 3 次理解错误信号
    print("\n模拟 3 次理解错误信号...")
    for i in range(3):
        signal = {
            'sentiment': 'negative',
            'improvement_type': 'understanding',
            'action': 'confirm_before_execute'
        }
        updater.update(signal)
        print(f"第{i+1}次更新后模式：{updater.get_current_mode()}")
    
    # 检查是否应该确认
    print(f"\n应该确认：{updater.should_confirm()}")
    print(f"应该报告进度：{updater.should_report_progress()}")
    
    # 查看配置
    print(f"\n当前配置：{updater.config}")
    
    print("\n测试完成！")
