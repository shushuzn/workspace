#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Brainstorm - 工作流问题头脑风暴

审查维度:
1. 工作流步骤完整性
2. 工具集成和调用
3. 批判者和质量门禁
4. 会话压缩和记忆
5. Git 和版本控制
6. 性能和效率
"""

import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("D:\\OpenClaw\\workspace")
FLOW_FILE = WORKSPACE / "flow-archive" / "20260318-universal-workflow-001" / "workflow.json"
TOOLS_REGISTRY = WORKSPACE / "30-scripts-tools" / "tools_registry.json"

# ANSI 颜色代码
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"

def load_workflow():
    """加载工作流配置"""
    if not FLOW_FILE.exists():
        return None

    with open(FLOW_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_tools_registry():
    """加载工具注册表"""
    if not TOOLS_REGISTRY.exists():
        return None

    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        return json.load(f)

def brainstorm_workflow_steps(workflow):
    """维度 1: 工作流步骤完整性"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}维度 1: 工作流步骤完整性{Colors.RESET}")
    print("=" * 70)

    issues = []
    suggestions = []

    steps = workflow.get("steps", [])
    step_ids = [s.get("step_id") for s in steps]

    # 检查步骤连续性
    print(f"📊 当前步骤：{len(steps)}个")
    print(f"   步骤 ID: {step_ids}")

    # 检查 Step 6.5 是否合理
    if 6.5 in step_ids:
        print(f"   {Colors.GREEN}✅ Step 6.5 工具集成验证已添加{Colors.RESET}")
    else:
        issues.append({
            "dimension": 1,
            "severity": "high",
            "issue": "缺少工具集成验证步骤",
            "suggestion": "添加 Step 6.5 验证工具注册和集成"
        })

    # 检查是否有测试步骤
    has_test_step = any("test" in s.get("name", "").lower() for s in steps)
    if not has_test_step:
        issues.append({
            "dimension": 1,
            "severity": "medium",
            "issue": "缺少自动化测试步骤",
            "suggestion": "添加 Step 6.6 自动化测试验证"
        })
        suggestions.append("添加自动化测试步骤，确保代码质量")

    # 检查是否有文档步骤
    has_doc_step = any("doc" in s.get("name", "").lower() for s in steps)
    if not has_doc_step:
        issues.append({
            "dimension": 1,
            "severity": "low",
            "issue": "缺少文档生成步骤",
            "suggestion": "添加文档自动生成步骤"
        })
        suggestions.append("添加文档生成步骤，自动更新 README")

    # 检查步骤超时设置
    for step in steps:
        timeout = step.get("timeout_seconds")
        if timeout and timeout > 600:
            issues.append({
                "dimension": 1,
                "severity": "low",
                "issue": f"Step {step.get('step_id')} 超时设置过长 ({timeout}s)",
                "suggestion": "考虑优化步骤性能或拆分步骤"
            })

    # 检查是否有回滚机制
    has_rollback = any("rollback" in str(s).lower() for s in steps)
    if not has_rollback:
        issues.append({
            "dimension": 1,
            "severity": "medium",
            "issue": "缺少失败回滚机制",
            "suggestion": "添加失败自动回滚步骤"
        })
        suggestions.append("添加回滚机制，失败时自动恢复")

    print(f"\n{Colors.YELLOW}发现问题：{len(issues)}个{Colors.RESET}")
    for i, issue in enumerate(issues, 1):
        severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue["severity"])
        print(f"   {severity_icon} {i}. {issue['issue']}")

    return issues, suggestions

def brainstorm_tool_integration(workflow, registry):
    """维度 2: 工具集成和调用"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}维度 2: 工具集成和调用{Colors.RESET}")
    print("=" * 70)

    issues = []
    suggestions = []

    # 检查工具注册率
    steps = workflow.get("steps", [])
    workflow_tool_ids = set()
    for step in steps:
        tool_id = step.get("tool_id")
        if tool_id:
            workflow_tool_ids.add(tool_id)

    print(f"📊 工作流使用工具：{len(workflow_tool_ids)}个")

    # 检查工具是否都注册了
    if registry:
        registered_tools = set(registry.get("tools", {}).keys())
        unregistered = workflow_tool_ids - registered_tools

        if unregistered:
            issues.append({
                "dimension": 2,
                "severity": "high",
                "issue": f"{len(unregistered)}个工具未注册：{unregistered}",
                "suggestion": "立即注册所有使用的工具"
            })
        else:
            print(f"   {Colors.GREEN}✅ 所有工具已注册{Colors.RESET}")

    # 检查 tool_executor 集成
    tool_executor_file = WORKSPACE / "30-scripts-tools" / "tool_executor.py"
    if tool_executor_file.exists():
        with open(tool_executor_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否有工具映射
        if "tool_mapping" not in content and "TOOLS" not in content:
            issues.append({
                "dimension": 2,
                "severity": "medium",
                "issue": "tool_executor.py 缺少工具映射",
                "suggestion": "添加完整的工具映射字典"
            })
            suggestions.append("完善 tool_executor.py 的工具映射")

    # 检查是否有工具版本控制
    if registry:
        version = registry.get("version")
        if not version:
            issues.append({
                "dimension": 2,
                "severity": "low",
                "issue": "tools_registry.json 缺少版本号",
                "suggestion": "添加版本管理和变更日志"
            })

    # 检查工具调用日志
    has_logging = any("log" in str(s).lower() for s in steps)
    if not has_logging:
        issues.append({
            "dimension": 2,
            "severity": "medium",
            "issue": "缺少工具调用日志",
            "suggestion": "添加详细的工具调用日志记录"
        })
        suggestions.append("记录所有工具调用，便于调试")

    print(f"\n{Colors.YELLOW}发现问题：{len(issues)}个{Colors.RESET}")
    for i, issue in enumerate(issues, 1):
        severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue["severity"])
        print(f"   {severity_icon} {i}. {issue['issue']}")

    return issues, suggestions

def brainstorm_critic_quality(workflow):
    """维度 3: 批判者和质量门禁"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}维度 3: 批判者和质量门禁{Colors.RESET}")
    print("=" * 70)

    issues = []
    suggestions = []

    steps = workflow.get("steps", [])

    # 检查批判者步骤
    critic_step = next((s for s in steps if "critic" in s.get("tool_id", "").lower()), None)
    if critic_step:
        print(f"   {Colors.GREEN}✅ 批判者步骤已存在{Colors.RESET}")

        # 检查批判者参数
        params = critic_step.get("parameters", {})
        if "check_integration" not in params:
            issues.append({
                "dimension": 3,
                "severity": "medium",
                "issue": "批判者缺少集成度检查",
                "suggestion": "添加 check_integration 参数"
            })
    else:
        issues.append({
            "dimension": 3,
            "severity": "high",
            "issue": "缺少批判者审查步骤",
            "suggestion": "添加 Auto-Critic v7.0 审查"
        })

    # 检查质量门禁
    quality_step = next((s for s in steps if "quality" in s.get("name", "").lower()), None)
    if quality_step:
        print(f"   {Colors.GREEN}✅ 质量门禁步骤已存在{Colors.RESET}")

        # 检查质量门禁参数
        params = quality_step.get("parameters", {})
        if "integration_check" not in params:
            issues.append({
                "dimension": 3,
                "severity": "medium",
                "issue": "质量门禁缺少集成检查",
                "suggestion": "添加 integration_check 参数"
            })
    else:
        issues.append({
            "dimension": 3,
            "severity": "high",
            "issue": "缺少质量门禁步骤",
            "suggestion": "添加质量门禁检查"
        })

    # 检查是否有性能基准测试
    has_benchmark = any("benchmark" in str(s).lower() for s in steps)
    if not has_benchmark:
        issues.append({
            "dimension": 3,
            "severity": "low",
            "issue": "缺少性能基准测试",
            "suggestion": "添加性能基准测试步骤"
        })
        suggestions.append("建立性能基准，持续监控")

    # 检查是否有安全审计
    has_security = any("security" in str(s).lower() for s in steps)
    if not has_security:
        issues.append({
            "dimension": 3,
            "severity": "medium",
            "issue": "缺少安全审计步骤",
            "suggestion": "添加代码安全审计"
        })
        suggestions.append("定期进行安全审计")

    print(f"\n{Colors.YELLOW}发现问题：{len(issues)}个{Colors.RESET}")
    for i, issue in enumerate(issues, 1):
        severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue["severity"])
        print(f"   {severity_icon} {i}. {issue['issue']}")

    return issues, suggestions

def brainstorm_memory_session(workflow):
    """维度 4: 会话压缩和记忆"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}维度 4: 会话压缩和记忆{Colors.RESET}")
    print("=" * 70)

    issues = []
    suggestions = []

    steps = workflow.get("steps", [])

    # 检查会话压缩步骤
    compress_step = next((s for s in steps if "compress" in s.get("name", "").lower()), None)
    if compress_step:
        print(f"   {Colors.GREEN}✅ 会话压缩步骤已存在{Colors.RESET}")

        # 检查压缩参数
        params = compress_step.get("parameters", {})
        if "importance_score" not in params:
            issues.append({
                "dimension": 4,
                "severity": "low",
                "issue": "会话压缩缺少重要性评分",
                "suggestion": "添加重要性评估参数"
            })
    else:
        issues.append({
            "dimension": 4,
            "severity": "high",
            "issue": "缺少会话压缩步骤",
            "suggestion": "添加 post_session_compress.py"
        })

    # 检查记忆持久化
    memory_step = next((s for s in steps if "memory" in s.get("name", "").lower()), None)
    if not memory_step:
        issues.append({
            "dimension": 4,
            "severity": "medium",
            "issue": "缺少长期记忆持久化步骤",
            "suggestion": "添加记忆保存到 memory-db.json"
        })
        suggestions.append("持久化重要记忆到长期记忆")

    # 检查是否有记忆压缩
    has_memory_compress = any("memory" in str(s).lower() and "compress" in str(s).lower() for s in steps)
    if not has_memory_compress:
        issues.append({
            "dimension": 4,
            "severity": "low",
            "issue": "缺少记忆自动压缩",
            "suggestion": "定期压缩长期记忆"
        })
        suggestions.append("每周压缩长期记忆，保持精简")

    # 检查上下文大小限制
    has_context_limit = any("context" in str(s).lower() for s in steps)
    if not has_context_limit:
        issues.append({
            "dimension": 4,
            "severity": "medium",
            "issue": "缺少上下文大小监控",
            "suggestion": "监控上下文大小，防止超限"
        })
        suggestions.append("设置上下文大小警报 (<100KB)")

    print(f"\n{Colors.YELLOW}发现问题：{len(issues)}个{Colors.RESET}")
    for i, issue in enumerate(issues, 1):
        severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue["severity"])
        print(f"   {severity_icon} {i}. {issue['issue']}")

    return issues, suggestions

def brainstorm_git_version(workflow):
    """维度 5: Git 和版本控制"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}维度 5: Git 和版本控制{Colors.RESET}")
    print("=" * 70)

    issues = []
    suggestions = []

    steps = workflow.get("steps", [])

    # 检查 Git 提交步骤
    git_step = next((s for s in steps if "git" in s.get("name", "").lower()), None)
    if git_step:
        print(f"   {Colors.GREEN}✅ Git 提交步骤已存在{Colors.RESET}")

        # 检查是否有推送
        if "push" not in str(git_step).lower():
            issues.append({
                "dimension": 5,
                "severity": "medium",
                "issue": "Git 步骤缺少推送操作",
                "suggestion": "添加 git push origin master"
            })
    else:
        issues.append({
            "dimension": 5,
            "severity": "high",
            "issue": "缺少 Git 提交步骤",
            "suggestion": "添加 git commit + push 步骤"
        })

    # 检查版本备份
    has_version_backup = any("version" in str(s).lower() and "backup" in str(s).lower() for s in steps)
    if not has_version_backup:
        issues.append({
            "dimension": 5,
            "severity": "medium",
            "issue": "缺少配置版本备份",
            "suggestion": "备份 workflow.json 和 tools_registry.json"
        })
        suggestions.append("每次变更前备份配置文件")

    # 检查 Git Hook
    git_hook_file = WORKSPACE / ".git" / "hooks" / "pre-commit"
    if not git_hook_file.exists():
        issues.append({
            "dimension": 5,
            "severity": "low",
            "issue": "缺少 Git Pre-Commit Hook",
            "suggestion": "添加工作流验证 Hook"
        })
        suggestions.append("创建 pre-commit hook 验证工作流")

    # 检查变更日志
    has_changelog = any("changelog" in str(s).lower() for s in steps)
    if not has_changelog:
        issues.append({
            "dimension": 5,
            "severity": "low",
            "issue": "缺少变更日志生成",
            "suggestion": "自动生成 CHANGELOG.md"
        })
        suggestions.append("维护变更日志")

    print(f"\n{Colors.YELLOW}发现问题：{len(issues)}个{Colors.RESET}")
    for i, issue in enumerate(issues, 1):
        severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue["severity"])
        print(f"   {severity_icon} {i}. {issue['issue']}")

    return issues, suggestions

def brainstorm_performance_efficiency(workflow):
    """维度 6: 性能和效率"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}维度 6: 性能和效率{Colors.RESET}")
    print("=" * 70)

    issues = []
    suggestions = []

    steps = workflow.get("steps", [])

    # 计算总超时时间
    total_timeout = sum(s.get("timeout_seconds", 0) for s in steps)
    print(f"📊 总超时设置：{total_timeout}秒 ({total_timeout/60:.1f}分钟)")

    if total_timeout > 3600:
        issues.append({
            "dimension": 6,
            "severity": "low",
            "issue": "总超时时间过长",
            "suggestion": "优化步骤性能，减少超时时间"
        })

    # 检查并行执行
    has_parallel = any("parallel" in str(s).lower() for s in steps)
    if not has_parallel:
        issues.append({
            "dimension": 6,
            "severity": "medium",
            "issue": "缺少并行执行优化",
            "suggestion": "独立步骤可并行执行"
        })
        suggestions.append("并行执行独立步骤，提升效率")

    # 检查缓存机制
    has_cache = any("cache" in str(s).lower() for s in steps)
    if not has_cache:
        issues.append({
            "dimension": 6,
            "severity": "medium",
            "issue": "缺少结果缓存",
            "suggestion": "缓存重复计算结果"
        })
        suggestions.append("实现结果缓存，避免重复计算")

    # 检查增量执行
    has_incremental = any("incremental" in str(s).lower() for s in steps)
    if not has_incremental:
        issues.append({
            "dimension": 6,
            "severity": "low",
            "issue": "缺少增量执行",
            "suggestion": "支持增量执行，跳过未变更部分"
        })
        suggestions.append("增量执行，只处理变更部分")

    # 检查资源监控
    has_resource_monitor = any("resource" in str(s).lower() or "memory" in str(s).lower() for s in steps)
    if not has_resource_monitor:
        issues.append({
            "dimension": 6,
            "severity": "low",
            "issue": "缺少资源监控",
            "suggestion": "监控 CPU/内存使用"
        })
        suggestions.append("监控资源使用，防止超限")

    print(f"\n{Colors.YELLOW}发现问题：{len(issues)}个{Colors.RESET}")
    for i, issue in enumerate(issues, 1):
        severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue["severity"])
        print(f"   {severity_icon} {i}. {issue['issue']}")

    return issues, suggestions

def generate_priority_matrix(all_issues):
    """生成优先级矩阵"""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}优先级矩阵{Colors.RESET}")
    print("=" * 70)

    # 按严重程度分组
    high = [i for i in all_issues if i["severity"] == "high"]
    medium = [i for i in all_issues if i["severity"] == "medium"]
    low = [i for i in all_issues if i["severity"] == "low"]

    print(f"\n🔴 高优先级 ({len(high)}个):")
    for i, issue in enumerate(high, 1):
        print(f"   {i}. [{issue['dimension']}维度] {issue['issue']}")

    print(f"\n🟡 中优先级 ({len(medium)}个):")
    for i, issue in enumerate(medium, 1):
        print(f"   {i}. [{issue['dimension']}维度] {issue['issue']}")

    print(f"\n🟢 低优先级 ({len(low)}个):")
    for i, issue in enumerate(low, 1):
        print(f"   {i}. [{issue['dimension']}维度] {issue['issue']}")

    return {
        "high": high,
        "medium": medium,
        "low": low
    }

def main():
    print(f"\n{Colors.BOLD}{Colors.CYAN}工作流问题头脑风暴{Colors.RESET}")
    print("=" * 70)
    print(f"时间：{datetime.now().isoformat()}")
    print(f"工作流：20260318-universal-workflow-001")

    # 加载配置
    workflow = load_workflow()
    registry = load_tools_registry()

    if not workflow:
        print(f"{Colors.RED}❌ 工作流配置文件不存在{Colors.RESET}")
        return

    all_issues = []
    all_suggestions = []

    # 6 个维度头脑风暴
    issues, suggestions = brainstorm_workflow_steps(workflow)
    all_issues.extend(issues)
    all_suggestions.extend(suggestions)

    issues, suggestions = brainstorm_tool_integration(workflow, registry)
    all_issues.extend(issues)
    all_suggestions.extend(suggestions)

    issues, suggestions = brainstorm_critic_quality(workflow)
    all_issues.extend(issues)
    all_suggestions.extend(suggestions)

    issues, suggestions = brainstorm_memory_session(workflow)
    all_issues.extend(issues)
    all_suggestions.extend(suggestions)

    issues, suggestions = brainstorm_git_version(workflow)
    all_issues.extend(issues)
    all_suggestions.extend(suggestions)

    issues, suggestions = brainstorm_performance_efficiency(workflow)
    all_issues.extend(issues)
    all_suggestions.extend(suggestions)

    # 生成优先级矩阵
    priority_matrix = generate_priority_matrix(all_issues)

    # 保存结果
    result = {
        "timestamp": datetime.now().isoformat(),
        "workflow": "20260318-universal-workflow-001",
        "total_issues": len(all_issues),
        "by_severity": {
            "high": len(priority_matrix["high"]),
            "medium": len(priority_matrix["medium"]),
            "low": len(priority_matrix["low"])
        },
        "issues": all_issues,
        "suggestions": all_suggestions,
        "priority_matrix": priority_matrix
    }

    result_file = WORKSPACE / "flow-archive" / "20260318-universal-workflow-001" / "brainstorm-workflow-issues.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n{Colors.GREEN}✅ 结果已保存到：{result_file}{Colors.RESET}")
    print(f"\n{Colors.BOLD}总结:{Colors.RESET}")
    print(f"   总问题数：{len(all_issues)}个")
    print(f"   高优先级：{len(priority_matrix['high'])}个")
    print(f"   中优先级：{len(priority_matrix['medium'])}个")
    print(f"   低优先级：{len(priority_matrix['low'])}个")
    print(f"   建议数：{len(all_suggestions)}条")

    print("=" * 70)

if __name__ == '__main__':
    main()
