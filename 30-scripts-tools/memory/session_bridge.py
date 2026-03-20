# -*- coding: utf-8 -*-
"""
Session Bridge - 跨 Session 桥接
允许新Session继承关键信息
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from .working_memory import WorkingMemory
from .archive_memory import ArchiveMemory
from .models import MemoryItem


class SessionBridge:
    """
    跨Session桥接器
    
    功能:
    1. 偏好继承 - 用户的明确偏好
    2. 关键决策继承 - 重要决策记录
    3. 项目状态继承 - 进行中的任务状态
    4. 上下文桥接 - 最近对话摘要
    """
    
    def __init__(self):
        # 继承优先级
        self.priority_order = [
            'preference',    # 最高: 用户偏好
            'decision',      # 高: 关键决策
            'project',       # 中: 项目状态
            'context'        # 低: 对话上下文
        ]
        
        # 最小重要性阈值
        self.min_importance = {
            'preference': 0.3,
            'decision': 0.5,
            'project': 0.4,
            'context': 0.6
        }
    
    def export_essential(self, working: WorkingMemory, 
                         archive: ArchiveMemory,
                         new_session_id: str,
                         max_items: int = 20) -> Dict:
        """
        导出 essential 信息到新Session
        
        Args:
            working: 当前 WorkingMemory
            archive: 当前 ArchiveMemory
            new_session_id: 新Session ID
            max_items: 最大导出项数
            
        Returns:
            Dict: 导出的essential信息
        """
        essential = {
            'session_id': new_session_id,
            'exported_at': datetime.now().isoformat(),
            'preferences': [],
            'decisions': [],
            'project_state': [],
            'context_summary': None,
            'stats': {}
        }
        
        # 1. 导出偏好（从Working + Archive）
        preferences = self._extract_by_type(working, archive, 'preference')
        essential['preferences'] = [
            self._serialize_item(p) for p in preferences
        ][:10]
        
        # 2. 导出决策
        decisions = self._extract_by_type(working, archive, 'decision')
        essential['decisions'] = [
            self._serialize_item(d) for d in decisions
        ][:10]
        
        # 3. 导出项目状态
        project_items = self._extract_by_type(working, archive, 'project')
        essential['project_state'] = [
            self._serialize_item(p) for p in project_items
        ][:5]
        
        # 4. 生成上下文摘要
        essential['context_summary'] = self._generate_summary(working)
        
        # 5. 统计
        essential['stats'] = {
            'total_exported': (
                len(essential['preferences']) + 
                len(essential['decisions']) + 
                len(essential['project_state'])
            ),
            'preference_count': len(essential['preferences']),
            'decision_count': len(essential['decisions']),
            'project_count': len(essential['project_state'])
        }
        
        return essential
    
    def import_essential(self, essential: Dict) -> List[MemoryItem]:
        """
        从导出的essential恢复记忆
        
        Args:
            essential: 导出的信息
            
        Returns:
            List[MemoryItem]: 可直接加载的MemoryItem列表
        """
        items = []
        
        # 恢复偏好
        for pref in essential.get('preferences', []):
            item = MemoryItem(
                id=f"inherited_{pref['id']}",
                content=pref['content'],
                type='preference',
                importance=max(pref['importance'], 0.7),  # 提升重要性
                created_at=pref['created_at'],
                metadata={'inherited': True, 'origin': essential['session_id']}
            )
            items.append(item)
        
        # 恢复决策
        for decision in essential.get('decisions', []):
            item = MemoryItem(
                id=f"inherited_{decision['id']}",
                content=decision['content'],
                type='decision',
                importance=max(decision['importance'], 0.8),
                created_at=decision['created_at'],
                metadata={'inherited': True, 'origin': essential['session_id']}
            )
            items.append(item)
        
        return items
    
    def save_essential(self, essential: Dict, 
                       path: str = None) -> str:
        """保存essential到文件"""
        path = path or f"13-memory/essential_{essential['session_id']}.json"
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(essential, f, ensure_ascii=False, indent=2)
        
        return path
    
    def load_essential(self, path: str) -> Dict:
        """从文件加载essential"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _extract_by_type(self, working: WorkingMemory,
                         archive: ArchiveMemory,
                         memory_type: str) -> List[MemoryItem]:
        """按类型提取记忆"""
        threshold = self.min_importance.get(memory_type, 0.3)
        
        results = []
        
        # 从Working Memory提取
        for item in working.get_all():
            if item.type == memory_type and item.importance >= threshold:
                results.append(item)
        
        # 从Archive补充
        recent = archive.retrieve_recent(token_budget=2000)
        for item in recent:
            if item.type == memory_type and item.importance >= threshold:
                if item.id not in [r.id for r in results]:
                    results.append(item)
        
        # 按重要性排序
        results.sort(key=lambda x: x.importance, reverse=True)
        
        return results
    
    def _serialize_item(self, item: MemoryItem) -> Dict:
        """序列化MemoryItem"""
        return {
            'id': item.id,
            'content': item.content,
            'type': item.type,
            'importance': item.importance,
            'created_at': item.created_at,
            'metadata': item.metadata
        }
    
    def _generate_summary(self, working: WorkingMemory) -> Optional[str]:
        """生成上下文摘要"""
        items = working.get_recent(n=10)
        
        if not items:
            return None
        
        # 提取关键信息
        topics = []
        for item in items:
            if item.type in ['decision', 'preference']:
                topics.append(item.content[:100])
        
        if topics:
            summary = "Recent priorities: " + "; ".join(topics[:3])
            return summary
        
        return None
    
    def auto_bridge(self, old_session_id: str, 
                    new_session_id: str,
                    archive_path: str = "13-memory/memory.db") -> Dict:
        """
        自动桥接两个Session
        
        读取旧session的essential，生成新的导入数据
        """
        # 查找旧session的essential文件
        essential_path = f"13-memory/essential_{old_session_id}.json"
        
        if Path(essential_path).exists():
            old_essential = self.load_essential(essential_path)
            new_items = self.import_essential(old_essential)
            
            return {
                'status': 'success',
                'items': [self._serialize_item(i) for i in new_items],
                'count': len(new_items)
            }
        else:
            # 尝试从archive直接提取
            return {
                'status': 'no_essential_file',
                'suggestion': 'Run export before new session'
            }


# 导出
__all__ = ['SessionBridge']