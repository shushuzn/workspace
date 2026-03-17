"""
冲突检测与解决模块

检测记忆之间的矛盾和冲突。
"""

from typing import Dict, List, Tuple, Optional
from pathlib import Path


class ConflictModule:
    """
    冲突检测与解决模块
    
    冲突类型:
    - 信息矛盾
    - 时间冲突
    - 来源冲突
    - 逻辑冲突
    """
    
    def __init__(self, config=None):
        self.config = config
        self.conflict_threshold = 0.7
    
    def detect(self, memory: Dict, memories: List[Dict]) -> List[Dict]:
        """检测与给定记忆的冲突"""
        conflicts = []
        
        for other in memories:
            if other.get('id') == memory.get('id'):
                continue
            
            conflict = self._check_conflict(memory, other)
            
            if conflict:
                conflicts.append(conflict)
        
        return conflicts
    
    def detect_all(self, memories: List[Dict]) -> List[Dict]:
        """检测所有记忆之间的冲突"""
        conflicts = []
        
        for i, mem1 in enumerate(memories):
            for mem2 in memories[i+1:]:
                conflict = self._check_conflict(mem1, mem2)
                
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts
    
    def _check_conflict(self, mem1: Dict, mem2: Dict) -> Optional[Dict]:
        """检查两个记忆之间是否有冲突"""
        conflict_types = []
        
        # 1. 检查时间冲突
        time_conflict = self._check_time_conflict(mem1, mem2)
        if time_conflict:
            conflict_types.append(time_conflict)
        
        # 2. 检查信息矛盾
        info_conflict = self._check_info_conflict(mem1, mem2)
        if info_conflict:
            conflict_types.append(info_conflict)
        
        # 3. 检查来源冲突
        source_conflict = self._check_source_conflict(mem1, mem2)
        if source_conflict:
            conflict_types.append(source_conflict)
        
        if conflict_types:
            return {
                'memory1_id': mem1.get('id'),
                'memory2_id': mem2.get('id'),
                'conflicts': conflict_types,
                'severity': self._calculate_severity(conflict_types),
            }
        
        return None
    
    def _check_time_conflict(self, mem1: Dict, mem2: Dict) -> Optional[Dict]:
        """检查时间冲突"""
        # TODO: 实现时间冲突检测
        return None
    
    def _check_info_conflict(self, mem1: Dict, mem2: Dict) -> Optional[Dict]:
        """检查信息矛盾"""
        content1 = mem1.get('content', '').lower()
        content2 = mem2.get('content', '').lower()
        
        # 矛盾词汇
        contradiction_pairs = [
            ('是', '不是'),
            ('有', '没有'),
            ('正确', '错误'),
            ('对', '错'),
            ('支持', '反对'),
        ]
        
        for word1, word2 in contradiction_pairs:
            if word1 in content1 and word2 in content2:
                return {
                    'type': 'information_contradiction',
                    'description': f"矛盾词汇：'{word1}' vs '{word2}'",
                    'severity': 0.8,
                }
        
        return None
    
    def _check_source_conflict(self, mem1: Dict, mem2: Dict) -> Optional[Dict]:
        """检查来源冲突"""
        source1 = mem1.get('source', '')
        source2 = mem2.get('source', '')
        
        # 如果来源不同但内容相似，可能有冲突
        if source1 and source2 and source1 != source2:
            # TODO: 检查内容相似性
            pass
        
        return None
    
    def _calculate_severity(self, conflicts: List[Dict]) -> float:
        """计算冲突严重程度"""
        if not conflicts:
            return 0.0
        
        severities = [c.get('severity', 0.5) for c in conflicts]
        return sum(severities) / len(severities)
    
    def resolve(self, conflict: Dict, memories: List[Dict]) -> Dict:
        """解决冲突"""
        mem1_id = conflict.get('memory1_id')
        mem2_id = conflict.get('memory2_id')
        
        mem1 = next((m for m in memories if m.get('id') == mem1_id), None)
        mem2 = next((m for m in memories if m.get('id') == mem2_id), None)
        
        if not mem1 or not mem2:
            return {'status': 'failed', 'reason': 'Memory not found'}
        
        # 解决策略
        strategy = self._choose_resolution_strategy(mem1, mem2, conflict)
        
        if strategy == 'keep_higher_score':
            # 保留分数高的
            winner = mem1 if mem1.get('score', 0) > mem2.get('score', 0) else mem2
            loser = mem2 if winner == mem1 else mem1
            
            return {
                'status': 'resolved',
                'strategy': strategy,
                'keep': winner.get('id'),
                'archive': loser.get('id'),
            }
        
        elif strategy == 'merge':
            # 合并两个记忆
            return {
                'status': 'resolved',
                'strategy': strategy,
                'merge_ids': [mem1_id, mem2_id],
            }
        
        else:
            return {
                'status': 'unresolved',
                'reason': 'No suitable strategy',
            }
    
    def _choose_resolution_strategy(self, mem1: Dict, mem2: Dict, conflict: Dict) -> str:
        """选择解决策略"""
        score1 = mem1.get('score', 0.5)
        score2 = mem2.get('score', 0.5)
        
        # 如果分数差异大，保留高的
        if abs(score1 - score2) > 0.2:
            return 'keep_higher_score'
        
        # 否则尝试合并
        return 'merge'
    
    def get_conflict_stats(self, conflicts: List[Dict]) -> Dict:
        """获取冲突统计"""
        if not conflicts:
            return {'total': 0}
        
        by_type = {}
        by_severity = {'low': 0, 'medium': 0, 'high': 0}
        
        for conflict in conflicts:
            # 按类型统计
            for c in conflict.get('conflicts', []):
                ctype = c.get('type', 'unknown')
                by_type[ctype] = by_type.get(ctype, 0) + 1
            
            # 按严重程度统计
            severity = conflict.get('severity', 0.5)
            if severity < 0.4:
                by_severity['low'] += 1
            elif severity < 0.7:
                by_severity['medium'] += 1
            else:
                by_severity['high'] += 1
        
        return {
            'total': len(conflicts),
            'by_type': by_type,
            'by_severity': by_severity,
            'avg_severity': sum(c.get('severity', 0) for c in conflicts) / len(conflicts),
        }
