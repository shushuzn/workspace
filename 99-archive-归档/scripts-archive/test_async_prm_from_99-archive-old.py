#!/usr/bin/env python3
"""测试异步执行器 + PRM 集成"""

import sys
sys.path.insert(0, '.')

from async_executor import AsyncExecutor
import time

def test_task(duration=2, success=True, task=None):
    """测试任务"""
    if task:
        task.progress = 50
        time.sleep(duration / 2)
        task.progress = 100
        time.sleep(duration / 2)
    
    if success:
        return {'status': 'success', 'result': 'test', 'duration': duration}
    else:
        return {'status': 'failed', 'error': 'test error', 'duration': duration}

# 测试
executor = AsyncExecutor(max_workers=2)

print("测试 1: 成功任务")
task_id_1 = executor.submit('test-1', test_task, duration=2, success=True)
time.sleep(3)
status_1 = executor.get_status(task_id_1)
print(f"状态：{status_1['status']}")
print(f"PRM 评分：{status_1.get('prm_score', {})}")
print()

print("测试 2: 失败任务")
task_id_2 = executor.submit('test-2', test_task, duration=2, success=False)
time.sleep(3)
status_2 = executor.get_status(task_id_2)
print(f"状态：{status_2['status']}")
print(f"PRM 评分：{status_2.get('prm_score', {})}")
print()

print("测试 3: 带用户反馈")
task_id_3 = executor.submit('test-3', test_task, duration=2, success=True)
time.sleep(3)
task_3 = executor.tasks.get(task_id_3)
task_3.user_feedback = "很好，很满意"
task_3.prm_score = executor.prm.evaluate(task_3.result, task_3.user_feedback)
status_3 = executor.get_status(task_id_3)
print(f"状态：{status_3['status']}")
print(f"用户反馈：很好，很满意")
print(f"PRM 评分：{status_3.get('prm_score', {})}")
print()

print("所有测试完成！")
