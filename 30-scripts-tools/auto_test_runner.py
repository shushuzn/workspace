#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto Test Runner - 自动化测试运行器

自动运行项目测试并生成报告
"""

import os
import sys
import json
import subprocess
import unittest
from datetime import datetime
from pathlib import Path

WORKSPACE = "D:\\OpenClaw\\workspace"
TESTS_DIR = "92-tests"
REPORTS_DIR = "21-reports\\tests"

class TestResult:
    """测试结果"""
    def __init__(self, name, status, duration=0, error=None):
        self.name = name
        self.status = status  # pass, fail, error, skip
        self.duration = duration
        self.error = error

def discover_tests(directory):
    """发现测试文件"""
    test_files = []
    
    try:
        for root, dirs, files in os.walk(directory):
            if '__pycache__' in root:
                continue
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    test_files.append(os.path.join(root, file))
    except Exception as e:
        print(f"发现测试失败：{e}")
    
    return test_files

def run_test_file(test_file):
    """运行单个测试文件"""
    results = []
    
    try:
        # 使用 unittest 运行测试
        cmd = [sys.executable, '-m', 'unittest', '-v', test_file.replace('.py', '')]
        
        start = datetime.now()
        result = subprocess.run(
            cmd,
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=60
        )
        end = datetime.now()
        
        duration = (end - start).total_seconds()
        
        # 解析结果
        if result.returncode == 0:
            status = 'pass'
        else:
            status = 'fail'
        
        results.append({
            'file': os.path.basename(test_file),
            'status': status,
            'duration': duration,
            'output': result.stdout[:500] if result.stdout else '',
            'error': result.stderr[:500] if result.stderr else ''
        })
        
    except subprocess.TimeoutExpired:
        results.append({
            'file': os.path.basename(test_file),
            'status': 'timeout',
            'duration': 60,
            'error': '测试超时 (60s)'
        })
    except Exception as e:
        results.append({
            'file': os.path.basename(test_file),
            'status': 'error',
            'duration': 0,
            'error': str(e)
        })
    
    return results

def run_syntax_check(file_path):
    """运行语法检查"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            compile(f.read(), file_path, 'exec')
        return {'status': 'pass', 'error': None}
    except SyntaxError as e:
        return {'status': 'fail', 'error': f'SyntaxError: {e}'}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def check_code_quality(file_path):
    """检查代码质量"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 检查项
        for i, line in enumerate(lines, 1):
            # 行长度检查
            if len(line.rstrip()) > 120:
                issues.append(f"Line {i}: 行过长 ({len(line.rstrip())} > 120)")
            
            # 尾随空格检查
            if line.rstrip() != line.rstrip('\n').rstrip():
                issues.append(f"Line {i}: 尾随空格")
        
        # 文件末尾空行检查
        if lines and not lines[-1].strip() == '':
            issues.append("文件末尾缺少空行")
        
    except Exception as e:
        issues.append(f"检查失败：{e}")
    
    return {
        'status': 'pass' if not issues else 'warning',
        'issues': issues,
        'issue_count': len(issues)
    }

def generate_report(all_results, syntax_results, quality_results):
    """生成测试报告"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 统计
    total_tests = len(all_results)
    passed = sum(1 for r in all_results if r['status'] == 'pass')
    failed = sum(1 for r in all_results if r['status'] in ['fail', 'error', 'timeout'])
    
    total_syntax = len(syntax_results)
    syntax_passed = sum(1 for r in syntax_results if r['status'] == 'pass')
    
    total_quality = len(quality_results)
    quality_passed = sum(1 for r in quality_results if r['status'] == 'pass')
    
    report = f"""# 🧪 自动化测试报告

**生成时间:** {timestamp}

## 测试概览

| 类别 | 总数 | 通过 | 失败 | 通过率 |
|------|------|------|------|--------|
| 功能测试 | {total_tests} | {passed} | {failed} | {passed/total_tests*100 if total_tests > 0 else 0:.1f}% |
| 语法检查 | {total_syntax} | {syntax_passed} | {total_syntax - syntax_passed} | {syntax_passed/total_syntax*100 if total_syntax > 0 else 0:.1f}% |
| 代码质量 | {total_quality} | {quality_passed} | {total_quality - quality_passed} | {quality_passed/total_quality*100 if total_quality > 0 else 0:.1f}% |

## 功能测试详情

"""
    
    if all_results:
        report += "| 测试文件 | 状态 | 耗时 | 错误 |\n"
        report += "|----------|------|------|------|\n"
        
        for result in all_results:
            status_icon = "✅" if result['status'] == 'pass' else "❌"
            error_msg = result.get('error', '')[:50] if result.get('error') else ''
            report += f"| {result['file']} | {status_icon} {result['status']} | {result['duration']:.2f}s | {error_msg} |\n"
        
        report += "\n"
    else:
        report += "没有发现测试文件。\n\n"
    
    report += f"""## 语法检查

"""
    
    failed_syntax = [r for r in syntax_results if r['status'] != 'pass']
    if failed_syntax:
        report += "### 失败的语法检查\n\n"
        for result in failed_syntax:
            report += f"- **{result['file']}**: {result.get('error', 'Unknown')}\n"
        report += "\n"
    else:
        report += "所有文件语法检查通过 ✅\n\n"
    
    report += f"""## 代码质量

"""
    
    quality_issues = [r for r in quality_results if r['status'] != 'pass']
    if quality_issues:
        report += "### 发现的问题\n\n"
        for result in quality_issues:
            report += f"- **{result['file']}** ({result['issue_count']} 个问题):\n"
            for issue in result.get('issues', [])[:5]:
                report += f"  - {issue}\n"
        report += "\n"
    else:
        report += "代码质量检查通过 ✅\n\n"
    
    report += f"""## 总结

- **总测试数:** {total_tests + total_syntax + total_quality}
- **总通过数:** {passed + syntax_passed + quality_passed}
- **总失败数:** {failed + (total_syntax - syntax_passed) + (total_quality - quality_passed)}
- **整体通过率:** {(passed + syntax_passed + quality_passed) / (total_tests + total_syntax + total_quality) * 100 if (total_tests + total_syntax + total_quality) > 0 else 0:.1f}%

## 建议

"""
    
    if failed > 0:
        report += "- ⚠️ 修复失败的测试\n"
    if (total_syntax - syntax_passed) > 0:
        report += "- ⚠️ 修复语法错误\n"
    if (total_quality - quality_passed) > 0:
        report += "- ⚠️ 改进代码质量\n"
    if total_tests == 0:
        report += "- 💡 建议添加单元测试\n"
    
    report += """
---

*本报告由 auto_test_runner.py 自动生成*
"""
    
    return report

def main():
    """主函数"""
    print("=" * 60)
    print("Auto Test Runner v1.0 - 自动化测试运行器")
    print("=" * 60)
    
    # 创建报告目录
    report_dir = os.path.join(WORKSPACE, REPORTS_DIR)
    os.makedirs(report_dir, exist_ok=True)
    
    # 发现测试
    print(f"\n[1/4] 发现测试文件...")
    tests_dir = os.path.join(WORKSPACE, TESTS_DIR)
    test_files = discover_tests(tests_dir)
    print(f"✅ 找到 {len(test_files)} 个测试文件")
    
    # 运行功能测试
    print(f"\n[2/4] 运行功能测试...")
    all_results = []
    for test_file in test_files[:10]:  # 限制数量用于演示
        print(f"  运行：{os.path.basename(test_file)}")
        results = run_test_file(test_file)
        all_results.extend(results)
    
    # 语法检查
    print(f"\n[3/4] 语法检查...")
    syntax_results = []
    quality_results = []
    
    tools_dir = os.path.join(WORKSPACE, "30-scripts-tools")
    py_files = [f for f in os.listdir(tools_dir) if f.endswith('.py') and not f.startswith('_')][:20]
    
    for py_file in py_files:
        file_path = os.path.join(tools_dir, py_file)
        
        # 语法检查
        syntax_result = run_syntax_check(file_path)
        syntax_result['file'] = py_file
        syntax_results.append(syntax_result)
        
        # 代码质量检查
        quality_result = check_code_quality(file_path)
        quality_result['file'] = py_file
        quality_results.append(quality_result)
    
    syntax_passed = sum(1 for r in syntax_results if r['status'] == 'pass')
    print(f"✅ 语法检查：{syntax_passed}/{len(syntax_results)} 通过")
    
    quality_passed = sum(1 for r in quality_results if r['status'] == 'pass')
    print(f"✅ 代码质量：{quality_passed}/{len(quality_results)} 通过")
    
    # 生成报告
    print(f"\n[4/4] 生成报告...")
    report = generate_report(all_results, syntax_results, quality_results)
    
    # 保存报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(report_dir, f"test_report_{timestamp}.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 保存 JSON 结果
    json_path = os.path.join(report_dir, f"test_report_{timestamp}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "test_results": all_results,
            "syntax_results": syntax_results,
            "quality_results": quality_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 报告已保存：{report_path}")
    print(f"✅ JSON 已保存：{json_path}")
    
    print("\n" + "=" * 60)
    print("✅ 自动化测试完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()
