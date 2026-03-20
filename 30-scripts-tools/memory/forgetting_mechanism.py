# -*- coding: utf-8 -*-
"""
Forgetting Mechanism - 遗忘机制
模拟人类记忆曲线，自动衰减和清理低价值记忆
"""

import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from .archive_memory import ArchiveMemory


class ForgettingMechanism:
    """
    遗忘机制
    
    核心思想:
    - 信息随时间自然衰减
    - 低重要性信息优先遗忘
    - 高价值信息保护性增强
    """
    
    def __init__(self):
        # 遗忘曲线参数
        self.half_life_days = 7  # 半衰期（天）
        self.base_decay = 0.9    # 基础衰减率
        
        # 清理阈值
        self.delete_threshold = 0.1   # 直接删除的阈值
        self.archive_threshold = 0.3  # 归档阈值
        
        # 保护规则
        self.protected_types = ['preference', 'decision', 'critical']
    
    def calculate_decay(self, item_importance: float, 
                        days_old: float) -> float:
        """
        计算衰减后的重要性
        
        使用改进的遗忘曲线:
        decay = base_decay ^ (days / half_life) * importance
        
        高重要性信息衰减更慢
        """
        # 重要性越高，衰减越慢
        importance_factor = 1 + (item_importance - 0.5) * 0.5
        
        # 基础衰减
        decay = math.pow(self.base_decay, days_old / self.half_life_days)
        
        # 应用重要性保护
        effective_decay = decay * importance_factor
        
        return item_importance * effective_decay
    
    def apply(self, archive: ArchiveMemory, 
              dry_run: bool = True) -> int:
        """
        应用遗忘机制
        
        Args:
            archive: ArchiveMemory 实例
            dry_run: True=模拟, False=实际删除
            
        Returns:
            int: 删除/标记遗忘的数量
        """
        # 获取所有记忆
        all_items = archive.retrieve_recent(token_budget=100000)
        
        deleted_count = 0
        now = datetime.now()
        
        for item in all_items:
            # 计算年龄（天）
            try:
                created = datetime.fromisoformat(item.created_at)
                days_old = (now - created).total_seconds() / 86400
            except:
                days_old = 0
            
            # 跳过保护类型
            if item.type in self.protected_types:
                continue
            
            # 计算衰减后的重要性
            decayed_importance = self.calculate_decay(
                item.importance, 
                days_old
            )
            
            # 判断是否遗忘
            if decayed_importance < self.delete_threshold:
                if dry_run:
                    deleted_count += 1
                else:
                    # 实际删除
                    archive.delete_old(days=365, importance_threshold=0)
                    deleted_count += 1
        
        return deleted_count
    
    def should_forget(self, item_importance: float, 
                      item_type: str,
                      days_old: float) -> bool:
        """判断是否应该遗忘"""
        # 保护类型不遗忘
        if item_type in self.protected_types:
            return False
        
        # 计算衰减
        decayed = self.calculate_decay(item_importance, days_old)
        
        return decayed < self.delete_threshold
    
    def get_decay_preview(self, items: List, 
                          target_date: datetime = None) -> List[Dict]:
        """
        预览衰减效果
        
        Args:
            items: 记忆列表
            target_date: 目标日期（预览哪天的状态）
            
        Returns:
            List[Dict]: 每个item的衰减预览
        """
        target_date = target_date or datetime.now()
        
        previews = []
        for item in items:
            try:
                created = datetime.fromisoformat(item.created_at)
                days_old = (target_date - created).total_seconds() / 86400
            except:
                days_old = 0
            
            decayed = self.calculate_decay(item.importance, days_old)
            
            previews.append({
                'id': item.id,
                'original_importance': item.importance,
                'decayed_importance': round(decayed, 3),
                'days_old': round(days_old, 1),
                'should_forget': self.should_forget(
                    item.importance, 
                    item.type, 
                    days_old
                )
            })
        
        # 按衰减后重要性排序
        previews.sort(key=lambda x: x['decayed_importance'])
        return previews
    
    def suggest_retention(self, item_importance: float, 
                          item_type: str) -> Dict:
        """建议保留策略"""
        base_days = self.half_life_days * 2
        
        # 重要性加成
        if item_importance >= 0.8:
            multiplier = 4
        elif item_importance >= 0.6:
            multiplier = 2
        elif item_importance >= 0.4:
            multiplier = 1
        else:
            multiplier = 0.5
        
        # 类型加成
        if item_type in self.protected_types:
            multiplier *= 2
        
        retention_days = int(base_days * multiplier)
        
        return {
            'recommended_retention_days': retention_days,
            'will_decay_below_threshold': 
                item_importance * math.pow(self.base_decay, 
                                           retention_days / self.half_life_days) 
                < self.delete_threshold,
            'importance_protection': item_importance >= 0.6,
            'type_protection': item_type in self.protected_types
        }


class AdaptiveForgetting(ForgettingMechanism):
    """
    自适应遗忘机制
    
    根据用户行为动态调整遗忘参数
    """
    
    def __init__(self):
        super().__init__()
        self.usage_history: List[Dict] = []
        self.adapted_weights = {
            'frequency': 0.3,
            'feedback': 0.4,
            'uniqueness': 0.3
        }
    
    def record_access(self, item_id: str, access_type: str):
        """记录访问以调整遗忘"""
        self.usage_history.append({
            'item_id': item_id,
            'access_type': access_type,
            'timestamp': datetime.now().isoformat()
        })
    
    def adapt_parameters(self) -> Dict:
        """根据使用历史调整参数"""
        if len(self.usage_history) < 10:
            return self.weights
        
        # 统计访问类型
        access_types = {}
        for record in self.usage_history[-100:]:  # 最近100条
            at = record['access_type']
            access_types[at] = access_types.get(at, 0) + 1
        
        # 动态调整
        if access_types.get('frequent', 0) > 50:
            # 用户经常回顾 → 延长半衰期
            self.half_life_days = min(30, self.half_life_days * 1.2)
        
        if access_types.get('rare', 0) > 30:
            # 用户很少回顾 → 缩短半衰期
            self.half_life_days = max(3, self.half_life_days * 0.8)
        
        return {
            'half_life_days': self.half_life_days,
            'base_decay': self.base_decay
        }


# 导出
__all__ = ['ForgettingMechanism', 'AdaptiveForgetting']