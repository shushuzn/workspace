"""
记忆验证器
"""

from typing import Dict, List, Tuple


class MemoryValidator:
    """记忆验证器"""
    
    @staticmethod
    def validate(memory: Dict) -> Tuple[bool, List[str]]:
        """
        验证记忆
        
        Returns:
            (是否有效，错误列表)
        """
        errors = []
        
        # 检查必需字段
        if not memory.get('content'):
            errors.append("Missing 'content' field")
        
        # 检查内容长度
        content = memory.get('content', '')
        if len(content) < 10:
            errors.append("Content too short (< 10 chars)")
        
        if len(content) > 100000:
            errors.append("Content too long (> 100k chars)")
        
        # 检查标签
        tags = memory.get('tags', [])
        if not isinstance(tags, list):
            errors.append("'tags' must be a list")
        elif len(tags) > 20:
            errors.append("Too many tags (> 20)")
        
        # 检查分数
        score = memory.get('score', 0.0)
        if not isinstance(score, (int, float)):
            errors.append("'score' must be a number")
        elif not (0.0 <= score <= 1.0):
            errors.append("'score' must be between 0.0 and 1.0")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @staticmethod
    def validate_batch(memories: List[Dict]) -> Dict:
        """批量验证"""
        results = {
            'total': len(memories),
            'valid': 0,
            'invalid': 0,
            'errors': []
        }
        
        for i, memory in enumerate(memories):
            is_valid, errors = MemoryValidator.validate(memory)
            
            if is_valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
                results['errors'].append({
                    'index': i,
                    'errors': errors
                })
        
        return results
    
    @staticmethod
    def sanitize(memory: Dict) -> Dict:
        """清理记忆数据"""
        sanitized = {}
        
        # 复制有效字段
        if memory.get('content'):
            sanitized['content'] = str(memory['content']).strip()
        
        if memory.get('tags') and isinstance(memory['tags'], list):
            sanitized['tags'] = [str(t).strip() for t in memory['tags'][:20]]
        
        if memory.get('score'):
            try:
                score = float(memory['score'])
                sanitized['score'] = max(0.0, min(1.0, score))
            except:
                sanitized['score'] = 0.5
        
        # 添加元数据
        sanitized['sanitized'] = True
        
        return sanitized
