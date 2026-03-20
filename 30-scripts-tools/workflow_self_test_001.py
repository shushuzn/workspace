#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工作流自测系统 v1.0

功能：
1. 测试工作流中每个步骤的工具可用性
2. 测试步骤之间的依赖关系
3. 测试关键路径执行
4. 生成测试报告和健康度评分

使用：
  py workflow_self_test.py --all
  py workflow_self_test.py --step 7
  py workflow_self_test.py --critical-path
  py workflow_self_test.py --report
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class WorkflowSelfTest:
    """工作流自测系统"""

    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.workflow_path = self.workspace / "flow-archive/20260318-universal-workflow-001/workflow.json"
        self.test_log = self.workspace / "flow-archive/20260318-universal-workflow-001/test-log.jsonl"

    def load_workflow(self) -> Dict:
        """加载工作流"""
        with open(self.workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_tool_availability(self, workflow: Dict) -> Dict:
        """测试工具可用性"""
        steps = workflow.get('steps', [])
        results = {
            'total': len(steps),
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }

        for step in steps:
            tool_id = step.get('tool_id')

            if tool_id is None:
                results['skipped'] += 1
                results['details'].append({
                    'step_id': step.get('step_id'),
                    'name': step.get('name'),
                    'tool': 'N/A (built-in)',
                    'status': 'skipped',
                    'reason': '内置功能'
                })
                continue

            # 检查工具是否存在
            tool_path = self.workspace / "30-scripts-tools" / tool_id
            if tool_path.exists():
                results['passed'] += 1
                results['details'].append({
                    'step_id': step.get('step_id'),
                    'name': step.get('name'),
                    'tool': tool_id,
                    'status': 'pass',
                    'size_kb': round(tool_path.stat().st_size / 1024, 2)
                })
            else:
                results['failed'] += 1
                results['details'].append({
                    'step_id': step.get('step_id'),
                    'name': step.get('name'),
                    'tool': tool_id,
                    'status': 'fail',
                    'reason': '工具文件不存在'
                })

        results['pass_rate'] = round(results['passed'] / results['total'] * 100, 1) if results['total'] > 0 else 0

        return results

    def test_step_dependencies(self, workflow: Dict) -> Dict:
        """测试步骤依赖关系"""
        steps = workflow.get('steps', [])
        step_ids = [s.get('step_id') for s in steps]

        results = {
            'total': len(steps),
            'passed': 0,
            'warnings': 0,
            'details': []
        }

        # 检查步骤编号连续性
        expected_id = 1
        for step in sorted(steps, key=lambda x: x.get('step_id', 0)):
            step_id = step.get('step_id')
            if step_id == expected_id:
                results['passed'] += 1
            else:
                results['warnings'] += 1
                results['details'].append({
                    'type': 'sequence',
                    'expected': expected_id,
                    'actual': step_id,
                    'message': f'步骤编号不连续'
                })
            expected_id += 1

        # 检查必要步骤
        mandatory_steps = [s for s in steps if s.get('mandatory', False)]
        results['mandatory_count'] = len(mandatory_steps)

        # 检查并行组
        parallel_groups = workflow.get('parallel_groups', [])
        results['parallel_groups'] = len(parallel_groups)

        return results

    def test_critical_path(self, workflow: Dict) -> Dict:
        """测试关键路径"""
        # 获取必要步骤
        steps = workflow.get('steps', [])
        mandatory_steps = [s for s in steps if s.get('mandatory', False)]

        results = {
            'mandatory_steps': [s.get('step_id') for s in mandatory_steps],
            'count': len(mandatory_steps),
            'estimated_time': sum(s.get('estimated_time_seconds', 0) for s in mandatory_steps),
            'health': 'good' if len(mandatory_steps) >= 5 else 'needs_review'
        }

        # 检查关键步骤是否有工具
        for step in mandatory_steps:
            if not step.get('tool_id'):
                results['health'] = 'warning'

        return results

    def test_output_requirements(self, workflow: Dict) -> Dict:
        """测试输出要求"""
        output_req = workflow.get('output_requirements', {})

        results = {
            'required_outputs': list(output_req.keys()),
            'checked': [],
            'missing': []
        }

        # 检查必需文件
        for key in output_req.keys():
            if 'output' in key.lower():
                continue

            path_str = output_req.get(key, '')
            if path_str:
                path = self.workspace / path_str.replace('YYYY-MM-DD', datetime.now().strftime('%Y-%m-%d'))
                if path.exists():
                    results['checked'].append(key)
                else:
                    results['missing'].append(key)

        return results

    def run_all_tests(self) -> Dict:
        """运行所有测试"""
        workflow = self.load_workflow()

        results = {
            'timestamp': datetime.now().isoformat(),
            'workflow_version': workflow.get('version', 'unknown'),
            'tests': {}
        }

        # 1. 工具可用性测试
        results['tests']['tool_availability'] = self.test_tool_availability(workflow)

        # 2. 步骤依赖测试
        results['tests']['step_dependencies'] = self.test_step_dependencies(workflow)

        # 3. 关键路径测试
        results['tests']['critical_path'] = self.test_critical_path(workflow)

        # 4. 输出要求测试
        results['tests']['output_requirements'] = self.test_output_requirements(workflow)

        # 计算总体健康度
        health_score = 100

        # 工具可用性扣分
        tool_test = results['tests']['tool_availability']
        if tool_test['failed'] > 0:
            health_score -= tool_test['failed'] * 10

        # 依赖问题扣分
        dep_test = results['tests']['step_dependencies']
        health_score -= dep_test['warnings'] * 5

        # 关键路径扣分
        cp_test = results['tests']['critical_path']
        if cp_test['health'] == 'warning':
            health_score -= 15
        elif cp_test['health'] == 'needs_review':
            health_score -= 10

        results['health_score'] = max(0, health_score)
        results['health_level'] = (
            'excellent' if health_score >= 95 else
            'good' if health_score >= 85 else
            'fair' if health_score >= 70 else
            'poor'
        )

        # 保存测试日志
        self._save_test_log(results)

        return results

    def test_single_step(self, step_id: int) -> Dict:
        """测试单个步骤"""
        workflow = self.load_workflow()
        steps = workflow.get('steps', [])

        step = next((s for s in steps if s.get('step_id') == step_id), None)

        if not step:
            return {'status': 'not_found', 'step_id': step_id}

        tool_id = step.get('tool_id')
        if tool_id:
            tool_path = self.workspace / "30-scripts-tools" / tool_id
            exists = tool_path.exists()
            size = tool_path.stat().st_size if exists else 0

            return {
                'status': 'pass' if exists else 'fail',
                'step': step,
                'tool_exists': exists,
                'tool_size_kb': round(size / 1024, 2) if exists else 0
            }

        return {
            'status': 'skipped',
            'step': step,
            'reason': '内置功能'
        }

    def _save_test_log(self, results: Dict):
        """保存测试日志"""
        log_entry = {
            'timestamp': results['timestamp'],
            'health_score': results['health_score'],
            'health_level': results['health_level']
        }

        with open(self.test_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    def generate_report(self) -> str:
        """生成测试报告"""
        results = self.run_all_tests()

        report = []
        report.append("=" * 70)
        report.append("工作流自测报告")
        report.append(f"时间: {results['timestamp']}")
        report.append(f"版本: {results['workflow_version']}")
        report.append("=" * 70)
        report.append("")

        # 总体健康度
        health = results['health_level']
        health_display = {
            'excellent': '[优秀]',
            'good': '[良好]',
            'fair': '[一般]',
            'poor': '[需改进]'
        }.get(health, '[未知]')

        report.append(f"总体健康度: {health_display} {results['health_score']}分")
        report.append("")

        # 工具可用性
        tool_test = results['tests']['tool_availability']
        report.append(f"工具可用性: {tool_test['passed']}/{tool_test['total']} 通过 ({tool_test['pass_rate']}%)")

        if tool_test['failed'] > 0:
            for detail in tool_test['details']:
                if detail['status'] == 'fail':
                    report.append(f"  [FAIL] 步骤 {detail['step_id']}: {detail['tool']} 不存在")

        # 步骤依赖
        dep_test = results['tests']['step_dependencies']
        report.append(f"步骤依赖: {dep_test['passed']}/{dep_test['total']} 正常")

        if dep_test['warnings'] > 0:
            report.append(f"  [WARN] {dep_test['warnings']} 个警告")

        # 关键路径
        cp_test = results['tests']['critical_path']
        report.append(f"关键路径: {cp_test['count']} 个必要步骤, 预计时间 {cp_test['estimated_time']}s")
        report.append(f"  必要步骤: {cp_test['mandatory_steps']}")

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)


def main():
    """主函数"""
    tester = WorkflowSelfTest()

    if len(sys.argv) < 2:
        print(tester.generate_report())
        return

    command = sys.argv[1]

    if command == '--all':
        result = tester.run_all_tests()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == '--step':
        if len(sys.argv) > 2:
            step_id = int(sys.argv[2])
            result = tester.test_single_step(step_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("用法: --step <step_id>")

    elif command == '--critical-path':
        workflow = tester.load_workflow()
        result = tester.test_critical_path(workflow)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == '--report':
        print(tester.generate_report())

    else:
        print(f"未知命令: {command}")
        print("用法:")
        print("  py workflow_self_test.py --all           运行所有测试")
        print("  py workflow_self_test.py --step <id>    测试单个步骤")
        print("  py workflow_self_test.py --critical-path 测试关键路径")
        print("  py workflow_self_test.py --report       生成报告")


if __name__ == "__main__":
    main()