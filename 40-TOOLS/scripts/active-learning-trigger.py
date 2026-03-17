#!/usr/bin/env python3

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
主动学习触发器 - Active Learning Trigger
功能：监控任务完成，自动触发学习流程
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class ActiveLearningTrigger:
    """主动学习触发器"""
    
    def __init__(self):
        self.trigger_file = Path(__file__).parent / 'learning-triggers.json'
        self.learned_patterns = Path(__file__).parent / 'learned-patterns.json'
    
    def detect_task_completion(self, task_description: str, result: str) -> Dict:
        """检测任务完成并提取学习点"""
        
        # 分析任务结果
        learning_points = []
        
        # 检测成功
        if '成功' in result or '完成' in result or 'success' in result.lower() or 'pass' in result.lower():
            learning_points.append({
                'type': 'success_pattern',
                'description': '成功模式',
                'extracted': self._extract_success_pattern(task_description, result)
            })
        
        # 检测问题/错误
        if '问题' in result or '错误' in result or 'error' in result.lower() or 'fail' in result.lower():
            learning_points.append({
                'type': 'lesson_learned',
                'description': '经验教训',
                'extracted': self._extract_lesson(task_description, result)
            })
        
        # 检测优化
        if '优化' in result or '提升' in result or 'optimize' in result.lower() or 'improve' in result.lower():
            learning_points.append({
                'type': 'optimization',
                'description': '优化经验',
                'extracted': self._extract_optimization(task_description, result)
            })
        
        return {
            'task': task_description,
            'result': result,
            'learning_points': learning_points,
            'should_learn': len(learning_points) > 0,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _extract_success_pattern(self, task: str, result: str) -> Dict:
        """提取成功模式"""
        return {
            'task_type': self._classify_task(task),
            'success_factors': self._identify_success_factors(result),
            'reusable': True
        }
    
    def _extract_lesson(self, task: str, result: str) -> Dict:
        """提取经验教训"""
        return {
            'problem': self._extract_problem(result),
            'solution': self._extract_solution(result),
            'lesson_category': self._categorize_lesson(result)
        }
    
    def _extract_optimization(self, task: str, result: str) -> Dict:
        """提取优化经验"""
        return {
            'optimization_target': task,
            'improvement': self._extract_improvement(result),
            'method': self._extract_method(result)
        }
    
    def _classify_task(self, task: str) -> str:
        """分类任务"""
        if '优化' in task or 'optimize' in task.lower():
            return 'optimization'
        elif '创建' in task or 'create' in task.lower():
            return 'creation'
        elif '检测' in task or 'test' in task.lower():
            return 'testing'
        elif '修复' in task or 'fix' in task.lower():
            return 'bugfix'
        else:
            return 'general'
    
    def _identify_success_factors(self, result: str) -> List[str]:
        """识别成功因素"""
        factors = []
        
        if '自动化' in result or 'automated' in result.lower():
            factors.append('自动化')
        if '测试' in result or 'test' in result.lower():
            factors.append('充分测试')
        if '规划' in result or 'plan' in result.lower():
            factors.append('详细规划')
        if '7 人格' in result:
            factors.append('7 人格流程')
        
        return factors if factors else ['标准流程']
    
    def _extract_problem(self, result: str) -> str:
        """提取问题"""
        lines = result.split('\n')
        for line in lines:
            if '问题' in line or 'error' in line.lower():
                return line.strip()
        return "未明确"
    
    def _extract_solution(self, result: str) -> str:
        """提取解决方案"""
        lines = result.split('\n')
        for line in lines:
            if '解决' in line or '方案' in line or 'fix' in line.lower():
                return line.strip()
        return "未明确"
    
    def _categorize_lesson(self, result: str) -> str:
        """分类教训"""
        if '防护' in result or '路径' in result:
            return 'SYS'
        elif '人格' in result or '规划' in result:
            return 'MULTI'
        elif '记忆' in result:
            return 'MEM'
        else:
            return 'GENERAL'
    
    def _extract_improvement(self, result: str) -> str:
        """提取改进效果"""
        # 查找百分比或数字
        import re
        matches = re.findall(r'(\d+(?:\.\d+)?%?)', result)
        if matches:
            return f"提升 {matches[0]}"
        return "显著提升"
    
    def _extract_method(self, result: str) -> str:
        """提取方法"""
        if '工具' in result:
            return "工具优化"
        elif '流程' in result:
            return "流程优化"
        elif '算法' in result:
            return "算法优化"
        else:
            return "综合优化"
    
    def should_trigger_learning(self, detection_result: Dict) -> bool:
        """判断是否应触发学习"""
        # 有学习点
        if not detection_result.get('learning_points'):
            return False
        
        # 重要任务
        task = detection_result.get('task', '').lower()
        important_keywords = ['系统', '核心', '关键', 'critical', 'core']
        for kw in important_keywords:
            if kw in task:
                return True
        
        # 有错误/教训
        for point in detection_result['learning_points']:
            if point['type'] == 'lesson_learned':
                return True
        
        return False
    
    def generate_learning_task(self, detection_result: Dict) -> Dict:
        """生成学习任务"""
        learning_points = detection_result['learning_points']
        
        # 提取关键信息
        problem = ""
        solution = ""
        for point in learning_points:
            if point['type'] == 'lesson_learned':
                problem = point['extracted'].get('problem', '')
                solution = point['extracted'].get('solution', '')
        
        return {
            'task_type': 'extract_lesson',
            'input': detection_result['task'],
            'context': detection_result['result'],
            'problem': problem,
            'solution': solution,
            'priority': 'high' if '错误' in detection_result['result'] else 'medium',
            'auto_extract': True
        }
    
    def print_detection(self, detection_result: Dict):
        """打印检测结果"""
        print("=" * 60)
        print("主动学习检测")
        print("=" * 60)
        
        print(f"\n任务：{detection_result['task']}")
        print(f"结果：{detection_result['result'][:100]}...")
        print(f"时间：{detection_result['timestamp']}")
        
        print(f"\n【学习点】")
        if detection_result['learning_points']:
            for i, point in enumerate(detection_result['learning_points'], 1):
                print(f"  {i}. {point['type']}: {point['description']}")
        else:
            print("  无显著学习点")
        
        print(f"\n【触发学习】{'是 [OK]' if detection_result['should_learn'] else '否 [FAIL]'}")
        
        if detection_result['should_learn']:
            learning_task = self.generate_learning_task(detection_result)
            print(f"\n【学习任务】")
            print(f"  类型：{learning_task['task_type']}")
            print(f"  优先级：{learning_task['priority']}")
            print(f"  自动提取：{learning_task['auto_extract']}")
        
        print("\n" + "=" * 60)


def demo_active_learning():
    """演示主动学习"""
    print("=" * 60)
    print("主动学习触发器")
    print("=" * 60)
    
    trigger = ActiveLearningTrigger()
    
    # 示例任务结果
    test_cases = [
        (
            "优化规划者系统",
            "成功完成规划者优化，实施 5 个工具，质量提升 75%，批判者评分 95/100"
        ),
        (
            "修复路径防护问题",
            "问题：文件创建在 C 盘。解决方案：实施 5 层防护系统。验证：5/5 测试通过。"
        ),
        (
            "创建记忆检索工具",
            "成功创建 memory-search-v2.py，检索速度提升 60%，准确率提升 40%"
        )
    ]
    
    for task, result in test_cases:
        print(f"\n{'='*60}")
        detection = trigger.detect_task_completion(task, result)
        trigger.print_detection(detection)


if __name__ == "__main__":
    demo_active_learning()
