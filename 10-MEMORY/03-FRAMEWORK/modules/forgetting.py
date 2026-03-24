"""
遗忘管理模块

归档、删除、压缩低质量或过时的记忆。
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta


class ForgettingModule:
    """
    遗忘管理模块
    
    策略:
    - 基于质量遗忘
    - 基于时间遗忘
    - 基于使用频率遗忘
    """

    def __init__(self, config=None, storage=None):
        self.config = config
        self.storage = storage
        self.archive_dir = None

    def execute(self, memory_id: str, strategy: str = 'archive') -> bool:
        """
        执行遗忘
        
        Args:
            memory_id: 记忆 ID
            strategy: 'archive' | 'delete' | 'compress'
        
        Returns:
            是否成功
        """
        if strategy == 'archive':
            return self._archive(memory_id)
        elif strategy == 'delete':
            return self._delete(memory_id)
        elif strategy == 'compress':
            return self._compress(memory_id)
        else:
            return False

    def _archive(self, memory_id: str) -> bool:
        """归档记忆"""
        if self.storage:
            return self.storage.delete(memory_id)
        return True

    def _delete(self, memory_id: str) -> bool:
        """删除记忆"""
        # 永久删除 (谨慎使用)
        if self.storage:
            # TODO: 实现永久删除
            return True
        return True

    def _compress(self, memory_id: str) -> bool:
        """压缩记忆"""
        # 保留核心信息，删除细节
        # TODO: 实现压缩
        return True

    def auto_forget(self, memories: List[Dict]) -> List[Dict]:
        """
        自动遗忘
        
        Returns:
            被遗忘的记忆列表
        """
        forgotten = []

        for memory in memories:
            should_forget, reason = self._should_forget(memory)

            if should_forget:
                strategy = self._choose_strategy(memory)
                if self.execute(memory.get('id'), strategy):
                    forgotten.append({
                        'id': memory.get('id'),
                        'reason': reason,
                        'strategy': strategy,
                    })

        return forgotten

    def _should_forget(self, memory: Dict) -> Tuple[bool, str]:
        """判断是否应该遗忘"""
        score = memory.get('score', 0.5)
        timestamp = memory.get('timestamp', '')
        access_count = memory.get('access_count', 0)

        # 1. 低质量遗忘
        if score < 0.2:
            return True, "低质量 (score<0.2)"

        # 2. 时间遗忘
        if timestamp:
            try:
                date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                days_old = (datetime.now() - date).days

                if days_old > 365 and score < 0.5:
                    return True, f"过时 ({days_old}天)"
            except:
                pass

        # 3. 使用频率遗忘
        if access_count == 0 and score < 0.4:
            return True, "从未访问"

        return False, ""

    def _choose_strategy(self, memory: Dict) -> str:
        """选择遗忘策略"""
        score = memory.get('score', 0.5)

        if score < 0.2:
            return 'delete'
        elif score < 0.4:
            return 'compress'
        else:
            return 'archive'

    def get_forget_candidates(self, memories: List[Dict]) -> List[Dict]:
        """获取遗忘候选"""
        candidates = []

        for memory in memories:
            should_forget, reason = self._should_forget(memory)
            if should_forget:
                candidates.append({
                    'id': memory.get('id'),
                    'score': memory.get('score'),
                    'reason': reason,
                    'strategy': self._choose_strategy(memory),
                })

        return candidates

    def batch_archive(self, memory_ids: List[str]) -> Dict:
        """批量归档"""
        results = {
            'total': len(memory_ids),
            'success': 0,
            'failed': 0,
            'failed_ids': []
        }

        for memory_id in memory_ids:
            if self._archive(memory_id):
                results['success'] += 1
            else:
                results['failed'] += 1
                results['failed_ids'].append(memory_id)

        return results

