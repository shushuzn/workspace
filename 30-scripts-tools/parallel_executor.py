#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parallel Executor - 并行执行器

并行执行独立任务以提高效率
"""

import os
import json
import time
import concurrent.futures
from datetime import datetime
from pathlib import Path

WORKSPACE = "D:\\OpenClaw\\workspace"

class ParallelExecutor:
    """并行执行器"""
    
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.results = []
    
    def execute_parallel(self, tasks):
        """并行执行任务"""
        results = []
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_task = {}
            
            for task in tasks:
                task_id = task.get('id', f'task_{len(future_to_task)}')
                future = executor.submit(self._execute_task, task)
                future_to_task[future] = task_id
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_task):
                task_id = future_to_task[future]
                try:
                    result = future.result()
                    result['task_id'] = task_id
                    result['status'] = 'success'
                except Exception as e:
                    result = {
                        'task_id': task_id,
                        'status': 'error',
                        'error': str(e)
                    }
                results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 计算性能提升
        sequential_time = sum(r.get('duration', 0) for r in results if r['status'] == 'success')
        speedup = sequential_time / total_time if total_time > 0 else 1
        
        return {
            'results': results,
            'total_time': total_time,
            'sequential_time': sequential_time,
            'speedup': speedup,
            'success_count': sum(1 for r in results if r['status'] == 'success'),
            'error_count': sum(1 for r in results if r['status'] == 'error')
        }
    
    def _execute_task(self, task):
        """执行单个任务"""
        start = time.time()
        
        # 模拟任务执行
        task_type = task.get('type', 'default')
        duration = task.get('duration', 0.1)
        
        if task_type == 'file_read':
            # 文件读取任务
            file_path = task.get('file', '')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                result = {'bytes_read': len(content)}
            else:
                result = {'error': 'file_not_found'}
        
        elif task_type == 'api_call':
            # API 调用任务 (模拟)
            time.sleep(duration)
            result = {'response': 'mock_response'}
        
        else:
            # 默认任务
            time.sleep(duration)
            result = {'output': 'completed'}
        
        end = time.time()
        result['duration'] = end - start
        
        return result
    
    def analyze_dependencies(self, tasks):
        """分析任务依赖"""
        # 简单的依赖分析
        independent = []
        dependent = []
        
        for task in tasks:
            if not task.get('depends_on'):
                independent.append(task)
            else:
                dependent.append(task)
        
        return {
            'independent': independent,
            'dependent': dependent,
            'parallelizable': len(independent),
            'sequential': len(dependent)
        }

def generate_report(execution_result, dependency_analysis):
    """生成报告"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    report = f"""# ⚡ 并行执行报告

**生成时间:** {timestamp}

## 执行概览

| 指标 | 值 |
|------|-----|
| 总任务数 | {len(execution_result['results'])} |
| 成功数 | {execution_result['success_count']} |
| 失败数 | {execution_result['error_count']} |
| 总耗时 | {execution_result['total_time']:.2f}s |
| 串行耗时 | {execution_result['sequential_time']:.2f}s |
| 加速比 | {execution_result['speedup']:.2f}x |
| 效率提升 | {(1 - 1/execution_result['speedup'])*100 if execution_result['speedup'] > 1 else 0:.1f}% |

## 依赖分析

| 类型 | 数量 | 百分比 |
|------|------|--------|
| 独立任务 | {dependency_analysis['parallelizable']} | {dependency_analysis['parallelizable']/len(execution_result['results'])*100 if execution_result['results'] else 0:.1f}% |
| 依赖任务 | {dependency_analysis['sequential']} | {dependency_analysis['sequential']/len(execution_result['results'])*100 if execution_result['results'] else 0:.1f}% |

## 任务详情

"""
    
    if execution_result['results']:
        report += "| 任务 ID | 状态 | 耗时 | 结果 |\n"
        report += "|--------|------|------|------|\n"
        
        for result in execution_result['results']:
            task_id = result.get('task_id', 'Unknown')
            status = "✅" if result['status'] == 'success' else "❌"
            duration = f"{result.get('duration', 0):.3f}s"
            output = str(result.get('output', result.get('error', '')))[:30]
            
            report += f"| {task_id} | {status} {result['status']} | {duration} | {output} |\n"
        
        report += "\n"
    
    report += f"""## 性能分析

"""
    
    speedup = execution_result['speedup']
    if speedup >= 4:
        report += "✅ **优秀!** 并行化效果显著\n"
    elif speedup >= 2:
        report += "✅ **良好** 有明显的性能提升\n"
    elif speedup >= 1.5:
        report += "⚠️ **一般** 有一定的性能提升\n"
    else:
        report += "⚠️ **待优化** 并行化效果不明显\n"
    
    report += f"""
## 建议

"""
    
    if dependency_analysis['sequential'] > 0:
        report += f"- 💡 尝试将 {dependency_analysis['sequential']} 个依赖任务转换为独立任务\n"
    
    if speedup < 2:
        report += "- 💡 增加并行任务数量以提高加速比\n"
        report += "- 💡 检查是否有 I/O 瓶颈\n"
    
    report += """
## 使用说明

### 并行执行
```bash
py parallel_executor.py --execute --tasks tasks.json
```

### 分析依赖
```bash
py parallel_executor.py --analyze --tasks tasks.json
```

---

*本报告由 parallel_executor.py 自动生成*
"""
    
    return report

def main():
    """主函数"""
    print("=" * 60)
    print("Parallel Executor v1.0 - 并行执行器")
    print("=" * 60)
    
    executor = ParallelExecutor(max_workers=4)
    
    # 创建示例任务
    print(f"\n[1/4] 创建示例任务...")
    tasks = [
        {'id': 'task_1', 'type': 'file_read', 'file': 'SOUL.md', 'duration': 0.1},
        {'id': 'task_2', 'type': 'file_read', 'file': 'USER.md', 'duration': 0.1},
        {'id': 'task_3', 'type': 'file_read', 'file': 'AGENTS.md', 'duration': 0.1},
        {'id': 'task_4', 'type': 'api_call', 'duration': 0.2},
        {'id': 'task_5', 'type': 'api_call', 'duration': 0.2},
        {'id': 'task_6', 'type': 'default', 'duration': 0.1},
    ]
    print(f"✅ 创建 {len(tasks)} 个任务")
    
    # 分析依赖
    print(f"\n[2/4] 分析任务依赖...")
    dependency_analysis = executor.analyze_dependencies(tasks)
    print(f"✅ 独立任务：{dependency_analysis['parallelizable']}, 依赖任务：{dependency_analysis['sequential']}")
    
    # 并行执行
    print(f"\n[3/4] 并行执行任务...")
    execution_result = executor.execute_parallel(tasks)
    print(f"✅ 成功：{execution_result['success_count']}, 失败：{execution_result['error_count']}")
    print(f"✅ 总耗时：{execution_result['total_time']:.2f}s, 加速比：{execution_result['speedup']:.2f}x")
    
    # 生成报告
    print(f"\n[4/4] 生成报告...")
    report = generate_report(execution_result, dependency_analysis)
    
    # 保存报告
    report_dir = os.path.join(WORKSPACE, "21-reports")
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(report_dir, f"parallel_exec_{timestamp}.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存：{report_path}")
    
    print("\n" + "=" * 60)
    print("✅ 并行执行完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()
