#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
ENH-003: Critic Auto-Fix Generator
批判者 AI 辅助修复建议生成器

功能:
- 根据问题描述自动生成具体修复步骤
- 估算修复时间
- 提供修复优先级建议
- 支持批量问题处理

使用示例:
    python critic_auto_fix.py --issue "Memory update failed" --category "memory" --severity high
    python critic_auto_fix.py --batch issues.json
"""

import argparse
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

# Windows 控制台编码修复
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        os.system('chcp 65001 >nul')


@dataclass
class Issue:
    description: str
    category: str  # memory/file/git/quality/security/performance
    severity: str  # low/medium/high/critical
    context: Optional[str] = None
    error_code: Optional[str] = None


class CriticAutoFixGenerator:
    """批判者自动修复建议生成器"""
    
    # 问题类别到修复模板的映射
    FIX_TEMPLATES = {
        'memory': {
            'high': {
                'steps': [
                    "1. 检查 MEMORY.md 文件锁定状态",
                    "2. 验证文件编码 (UTF-8)",
                    "3. 运行 memory_auto_fix.py --strict 进行诊断",
                    "4. 从最近备份恢复 (memory/backups/)",
                    "5. 手动验证关键章节完整性"
                ],
                'estimated_time': '15-30 分钟',
                'tools': ['memory_auto_fix.py', 'workspace_comparator.py']
            },
            'medium': {
                'steps': [
                    "1. 检查 memory/ 目录结构",
                    "2. 验证今日笔记文件存在",
                    "3. 运行 memory_search 测试检索功能",
                    "4. 更新 MEMORY.md 索引"
                ],
                'estimated_time': '5-10 分钟',
                'tools': ['memory_search.py']
            }
        },
        'file': {
            'high': {
                'steps': [
                    "1. 立即停止当前文件操作",
                    "2. 运行 pre_file_operation_hook.py 诊断",
                    "3. 使用 workspace_comparator.py 对比差异",
                    "4. 从 Git 恢复或从备份还原",
                    "5. 验证文件完整性后重新操作"
                ],
                'estimated_time': '20-40 分钟',
                'tools': ['pre_file_operation_hook.py', 'workspace_comparator.py', 'git']
            },
            'critical': {
                'steps': [
                    "🚨 紧急：文件操作错误",
                    "1. 立即执行 git stash 保存当前状态",
                    "2. 运行 memory_auto_fix.py --strict --backup",
                    "3. 检查 .git/hooks/pre-commit 日志",
                    "4. 联系用户确认操作意图",
                    "5. 在测试环境验证后重试"
                ],
                'estimated_time': '30-60 分钟',
                'tools': ['git', 'memory_auto_fix.py'],
                'requires_user_confirmation': True
            }
        },
        'git': {
            'medium': {
                'steps': [
                    "1. 运行 git status 检查状态",
                    "2. 查看 git log --oneline -5 最近提交",
                    "3. 如有冲突：git mergetool",
                    "4. 验证后 git push"
                ],
                'estimated_time': '5-15 分钟',
                'tools': ['git']
            },
            'high': {
                'steps': [
                    "1. git fetch origin 获取远程状态",
                    "2. git diff HEAD origin/master 对比差异",
                    "3. 决定 rebase 或 merge",
                    "4. 解决冲突后 git push --force-with-lease"
                ],
                'estimated_time': '15-30 分钟',
                'tools': ['git']
            }
        },
        'quality': {
            'medium': {
                'steps': [
                    "1. 运行相关测试套件",
                    "2. 检查批判者评分 (<85 分需修复)",
                    "3. 根据评分报告逐项修复",
                    "4. 重新运行测试验证"
                ],
                'estimated_time': '20-40 分钟',
                'tools': ['pytest', 'critic_review.py']
            }
        },
        'security': {
            'critical': {
                'steps': [
                    "🔒 安全漏洞 - 立即处理",
                    "1. 隔离受影响组件",
                    "2. 审查安全日志",
                    "3. 应用安全补丁",
                    "4. 运行安全扫描验证",
                    "5. 记录安全事件报告"
                ],
                'estimated_time': '1-2 小时',
                'tools': ['security_scanner.py'],
                'requires_user_confirmation': True
            }
        },
        'performance': {
            'medium': {
                'steps': [
                    "1. 运行性能分析 (cProfile)",
                    "2. 识别瓶颈 (>80% 耗时)",
                    "3. 优化热点代码",
                    "4. 基准测试对比"
                ],
                'estimated_time': '30-60 分钟',
                'tools': ['cProfile', 'line_profiler']
            }
        }
    }
    
    # 通用修复建议 (当无特定模板时)
    GENERIC_FIX = {
        'steps': [
            "1. 详细记录问题现象和复现步骤",
            "2. 搜索类似问题 (GitHub Issues/StackOverflow)",
            "3. 查看相关文档和日志",
            "4. 尝试最小化复现",
            "5. 制定修复方案并测试"
        ],
        'estimated_time': '30-90 分钟',
        'tools': ['日志文件', '文档']
    }
    
    def generate_fix(self, issue: Issue) -> Dict:
        """生成修复建议"""
        category = issue.category.lower()
        severity = issue.severity.lower()
        
        # 查找特定模板
        if category in self.FIX_TEMPLATES:
            if severity in self.FIX_TEMPLATES[category]:
                template = self.FIX_TEMPLATES[category][severity]
            else:
                # 使用最接近的严重程度
                severities = ['critical', 'high', 'medium', 'low']
                for sev in severities:
                    if sev in self.FIX_TEMPLATES[category]:
                        template = self.FIX_TEMPLATES[category][sev]
                        break
                else:
                    template = self.GENERIC_FIX
        else:
            template = self.GENERIC_FIX
        
        # 构建完整修复建议
        fix_suggestion = {
            'issue_summary': issue.description[:100] + ('...' if len(issue.description) > 100 else ''),
            'category': category,
            'severity': severity,
            'fix_steps': template['steps'],
            'estimated_time': template['estimated_time'],
            'required_tools': template.get('tools', []),
            'priority_score': self._calc_priority_score(severity, category),
            'requires_user_confirmation': template.get('requires_user_confirmation', False),
            'auto_fixable': self._is_auto_fixable(category, severity),
            'generated_at': datetime.now().isoformat()
        }
        
        # 添加上下文相关建议
        if issue.context:
            fix_suggestion['context_specific_advice'] = self._generate_context_advice(issue)
        
        # 添加错误码相关建议
        if issue.error_code:
            fix_suggestion['error_code_lookup'] = self._lookup_error_code(issue.error_code)
        
        return fix_suggestion
    
    def _calc_priority_score(self, severity: str, category: str) -> int:
        """计算修复优先级分数 (0-100)"""
        severity_scores = {
            'critical': 40,
            'high': 30,
            'medium': 20,
            'low': 10
        }
        
        category_multipliers = {
            'security': 1.5,
            'file': 1.3,
            'memory': 1.2,
            'git': 1.1,
            'quality': 1.0,
            'performance': 0.9
        }
        
        base_score = severity_scores.get(severity, 20)
        multiplier = category_multipliers.get(category, 1.0)
        
        return min(100, int(base_score * multiplier))
    
    def _is_auto_fixable(self, category: str, severity: str) -> bool:
        """判断是否可自动修复"""
        auto_fixable_categories = ['memory', 'git', 'file']
        non_auto_severities = ['critical']
        
        return (category in auto_fixable_categories and 
                severity not in non_auto_severities)
    
    def _generate_context_advice(self, issue: Issue) -> str:
        """根据上下文生成特定建议"""
        context = issue.context.lower()
        
        if 'backup' in context:
            return "检测到备份相关上下文 - 优先检查备份完整性"
        elif 'git' in context or 'commit' in context:
            return "检测到 Git 相关上下文 - 建议先 git stash 保存状态"
        elif 'memory' in context or 'learn' in context:
            return "检测到记忆系统相关 - 验证 MEMORY.md 完整性"
        elif 'file' in context or 'write' in context:
            return "检测到文件操作相关 - 启用严格模式验证"
        
        return "无特定上下文建议"
    
    def _lookup_error_code(self, error_code: str) -> Dict:
        """查找错误码相关信息"""
        # 简单错误码映射 (可扩展)
        error_database = {
            'Errno 22': {
                'meaning': 'Invalid argument - 无效参数',
                'common_causes': ['文件路径包含非法字符', '参数格式错误', '编码问题'],
                'fix': '检查参数格式和文件路径编码'
            },
            'Errno 13': {
                'meaning': 'Permission denied - 权限拒绝',
                'common_causes': ['文件被占用', '权限不足', '只读文件系统'],
                'fix': '以管理员身份运行或关闭占用程序'
            },
            'Errno 2': {
                'meaning': 'No such file or directory - 文件不存在',
                'common_causes': ['路径错误', '文件被删除', '相对路径问题'],
                'fix': '验证文件路径和工作目录'
            }
        }
        
        # 模糊匹配
        for code, info in error_database.items():
            if code in error_code:
                return info
        
        return {
            'meaning': '未知错误码',
            'common_causes': ['需进一步调查'],
            'fix': '搜索错误码 + 查看完整堆栈跟踪'
        }
    
    def batch_generate(self, issues: List[Issue]) -> List[Dict]:
        """批量生成修复建议"""
        return [self.generate_fix(issue) for issue in issues]


def main():
    parser = argparse.ArgumentParser(description='Critic Auto-Fix Generator - ENH-003')
    parser.add_argument('--issue', type=str, help='问题描述')
    parser.add_argument('--category', type=str, required=False,
                        choices=['memory', 'file', 'git', 'quality', 'security', 'performance'],
                        help='问题类别')
    parser.add_argument('--severity', type=str, default='medium',
                        choices=['low', 'medium', 'high', 'critical'],
                        help='严重程度')
    parser.add_argument('--context', type=str, help='额外上下文信息')
    parser.add_argument('--error-code', type=str, help='错误码 (如 Errno 22)')
    parser.add_argument('--batch', type=str, help='批量问题 JSON 文件')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    generator = CriticAutoFixGenerator()
    
    # 批量模式
    if args.batch:
        with open(args.batch, 'r', encoding='utf-8') as f:
            issues_data = json.load(f)
        
        issues = []
        for data in issues_data:
            issue = Issue(
                description=data.get('description', 'Unknown issue'),
                category=data.get('category', 'memory'),
                severity=data.get('severity', 'medium'),
                context=data.get('context'),
                error_code=data.get('error_code')
            )
            issues.append(issue)
        
        results = generator.batch_generate(issues)
        
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(f"\n{'='*60}")
            print(f"[FIX] 批量修复建议生成 (共 {len(results)} 个问题)")
            print(f"{'='*60}\n")
            
            for i, result in enumerate(results, 1):
                print(f"{i}. [{result['severity'].upper()}] {result['issue_summary']}")
                print(f"   优先级分数：{result['priority_score']}/100")
                print(f"   预估时间：{result['estimated_time']}")
                print(f"   可自动修复：{'[OK] 是' if result['auto_fixable'] else '[FAIL] 否'}")
                print(f"   修复步骤:")
                for step in result['fix_steps']:
                    print(f"     {step}")
                print()
        
        return
    
    # 单问题模式
    if not args.issue:
        parser.print_help()
        return
    
    issue = Issue(
        description=args.issue,
        category=args.category or 'memory',
        severity=args.severity,
        context=args.context,
        error_code=args.error_code
    )
    
    result = generator.generate_fix(issue)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*60}")
        print(f"[FIX] 自动修复建议")
        print(f"{'='*60}")
        print(f"问题：{result['issue_summary']}")
        print(f"类别：{result['category']} | 严重程度：{result['severity'].upper()}")
        print(f"优先级分数：{result['priority_score']}/100")
        print(f"预估修复时间：{result['estimated_time']}")
        print(f"可自动修复：{'[OK] 是' if result['auto_fixable'] else '[FAIL] 否'}")
        print(f"需用户确认：{'[WARN] 是' if result['requires_user_confirmation'] else '[OK] 否'}")
        
        print(f"\n[LIST] 修复步骤:")
        for i, step in enumerate(result['fix_steps'], 1):
            print(f"   {step}")
        
        print(f"\n[TOOL]  所需工具：{', '.join(result['required_tools'])}")
        
        if 'context_specific_advice' in result:
            print(f"\n[IDEA] 上下文建议：{result['context_specific_advice']}")
        
        if 'error_code_lookup' in result:
            ec = result['error_code_lookup']
            print(f"\n[SEARCH] 错误码解析:")
            print(f"   含义：{ec['meaning']}")
            print(f"   常见原因：{', '.join(ec['common_causes'])}")
            print(f"   修复建议：{ec['fix']}")
        
        print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
