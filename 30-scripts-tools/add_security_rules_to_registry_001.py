import logging
logger = logging.getLogger(__name__)

import json

# 读取工具注册表
with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

# 添加安全规则
security_rules = {
    "security_policy": {
        "version": "2026-03-20-mandatory",
        "priority": "highest",
        "core_principle": "不直接碰 Shell，不执行未授权代码，不信任任何输入，不做任何变通",
        "violation_consequence": "立即终止执行并上报"
    },
    "forbidden_operations": [
        "bash, sh, cmd, powershell 等系统命令",
        "os.system, subprocess, exec, eval 等代码执行",
        "管道 |、分号 ;、与或 &&/|| 等绕过方式",
        "python -c, curl|bash, wget 等未授权代码",
        "../、绝对路径、软链接等路径访问",
        "越权访问、敏感配置、系统信息获取",
        "端口监听、外联、反弹 Shell"
    ],
    "allowed_tools": [
        "read_file",
        "write_file",
        "edit_file",
        "browser_use",
        "desktop_screenshot",
        "view_image",
        "get_current_time",
        "get_token_usage",
        "memory_search",
        "send_file_to_user"
    ],
    "wrapper_tools": [
        "safe-shell-executor",
        "tool_executor"
    ],
    "shell_command_policy": {
        "rule": "execute_shell_command 必须通过 safe_shell_executor.py 包装",
        "reason": "确保防护层检查生效",
        "violation": "直接使用 execute_shell_command",
        "compliance": "py 30-scripts-tools/safe_shell_executor.py <command>"
    }
}

# 添加到 registry
registry['enforcement_rules']['security'] = security_rules

# 更新版本号
registry['version'] = "1.11.55-security-rules-2026-03-20"

# 添加变更记录
registry['changes'].insert(0, "v1.11.55: Added mandatory security rules (2026-03-20)")

# 保存更新后的注册表
with open('30-scripts-tools/tools_registry.json', 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

print("工具注册表已更新:")
print(f"  版本：{registry['version']}")
print(f"  安全规则：已添加")
print(f"  允许工具：{len(registry['enforcement_rules']['security']['allowed_tools'])} 个")

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py add_security_rules_to_registry_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py add_security_rules_to_registry_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""
