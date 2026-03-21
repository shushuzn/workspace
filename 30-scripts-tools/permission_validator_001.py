import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf- utf-8 -*-
"""
权限验证器 - 最小权限原则核心
【防护 v10.1】- 基于角色和工具风险等级的权限控制

功能:
  1. 工具风险分级验证
  2. 角色权限矩阵检查
  3. 权限令牌生成和验证
  4. 越权检测告警
  5. 审计日志记录
"""
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timezone

MATRIX_FILE = Path("30-scripts-tools/permission_matrix.json")
STATE_FILE = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
PERMISSION_LOG = Path("30-scripts-tools/permission_log.jsonl")
TOKEN_FILE = Path("30-scripts-tools/permission_tokens.json")

class PermissionValidator:
    """权限验证器 - 最小权限原则"""
    
    def __init__(self, session_id: str = None, role: str = "Executor"):
        self.session_id = session_id or self._get_session_id()
        self.role = role
        self.matrix = self._load_matrix()
        self.token = self._get_or_create_token()
    
    def _get_session_id(self) -> str:
        if STATE_FILE.exists():
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            return state.get("session_id", "unknown")
        return "unknown"
    
    def _load_matrix(self) -> dict:
        if not MATRIX_FILE.exists():
            return self._create_default_matrix()
        with open(MATRIX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _create_default_matrix(self) -> dict:
        """创建默认权限矩阵（如果不存在）"""
        default = {
            "version": "1.0.0",
            "工具风险分级": {
                "L1_只读": {"risk_level": "低", "auto_approve": True},
                "L2_写入": {"risk_level": "中", "auto_approve": True},
                "L3_删除": {"risk_level": "高", "auto_approve": False},
                "L4_系统": {"risk_level": "极高", "auto_approve": False},
                "L5_防护": {"risk_level": "最高", "auto_approve": False}
            },
            "角色权限矩阵": {
                "Executor": {
                    "allowed_levels": ["L1_只读", "L2_写入", "L3_删除"],
                    "denied_levels": ["L4_系统", "L5_防护"]
                }
            }
        }
        return default
    
    def _get_or_create_token(self) -> dict:
        """获取或创建权限令牌"""
        if TOKEN_FILE.exists():
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                tokens = json.load(f)
            if self.session_id in tokens:
                return tokens[self.session_id]
        
        token = self._create_token()
        
        if TOKEN_FILE.exists():
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                tokens = json.load(f)
        else:
            tokens = {}
        
        tokens[self.session_id] = token
        
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(tokens, f, ensure_ascii=False, indent=2)
        
        return token
    
    def _create_token(self) -> dict:
        """创建权限令牌"""
        entropy = f"{self.session_id}|{self.role}|{os.urandom(16).hex()}|{datetime.now(timezone.utc).isoformat()}"
        token_hash = hashlib.sha256(entropy.encode()).hexdigest()
        
        return {
            "token": token_hash,
            "session_id": self.session_id,
            "role": self.role,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "permissions": self._get_role_permissions()
        }
    
    def _get_role_permissions(self) -> dict:
        """获取角色权限"""
        roles = self.matrix.get("角色权限矩阵", {})
        return roles.get(self.role, {
            "allowed_levels": ["L1_只读"],
            "denied_levels": ["L2_写入", "L3_删除", "L4_系统", "L5_防护"]
        })
    
    def get_tool_risk_level(self, tool_id: str) -> str:
        """获取工具风险等级"""
        mapping = self.matrix.get("工具分类映射", {})
        return mapping.get(tool_id, "L2_写入")  # 默认 L2
    
    def verify_permission(self, tool_id: str) -> dict:
        """验证工具调用权限"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "role": self.role,
            "tool_id": tool_id,
            "allowed": False,
            "checks": {}
        }
        
        # 检查 1: 工具风险等级
        risk_level = self.get_tool_risk_level(tool_id)
        result["risk_level"] = risk_level
        result["checks"]["risk_level_identified"] = True
        
        # 检查 2: 角色权限
        permissions = self._get_role_permissions()
        allowed_levels = permissions.get("allowed_levels", [])
        denied_levels = permissions.get("denied_levels", [])
        
        result["checks"]["role_exists"] = self.role in self.matrix.get("角色权限矩阵", {})
        
        # 检查 3: 权限匹配
        if risk_level in denied_levels:
            result["checks"]["permission_match"] = False
            result["denial_reason"] = f"角色 {self.role} 禁止使用 {risk_level} 工具"
            self._log_permission(result, False)
            return result
        
        if risk_level not in allowed_levels:
            result["checks"]["permission_match"] = False
            result["denial_reason"] = f"角色 {self.role} 未授权 {risk_level} 工具"
            self._log_permission(result, False)
            return result
        
        result["checks"]["permission_match"] = True
        
        # 检查 4: 是否需要确认
        requires_confirmation = False
        if "requires_confirmation_for" in permissions:
            requires_confirmation = risk_level in permissions["requires_confirmation_for"]
        result["requires_confirmation"] = requires_confirmation
        
        # 检查 5: 是否需要备份
        requires_backup = False
        if risk_level in ["L3_删除", "L4_系统", "L5_防护"]:
            requires_backup = True
        result["requires_backup"] = requires_backup
        
        # 综合判断
        result["allowed"] = True
        
        self._log_permission(result, True)
        return result
    
    def _log_permission(self, result: dict, allowed: bool):
        """记录权限审计日志"""
        log_entry = {
            "timestamp": result["timestamp"],
            "session_id": result["session_id"],
            "role": result["role"],
            "tool_id": result["tool_id"],
            "risk_level": result.get("risk_level", "unknown"),
            "allowed": allowed,
            "denial_reason": result.get("denial_reason")
        }
        
        with open(PERMISSION_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def escalate(self, tool_id: str, reason: str) -> dict:
        """权限升级请求"""
        escalation = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "role": self.role,
            "tool_id": tool_id,
            "reason": reason,
            "status": "pending_admin_approval"
        }
        
        # 记录升级请求
        escalation_file = Path("30-scripts-tools/permission_escalations.jsonl")
        with open(escalation_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(escalation, ensure_ascii=False) + "\n")
        
        return escalation
    
    def display(self):
        """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py permission_validator_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py permission_validator_001.py

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

显示权限状态"""
        print("=" * 70)
        print("权限验证器 v10.1 - 最小权限原则")
        print("=" * 70)
        print(f"会话：{self.session_id}")
        print(f"角色：{self.role}")
        print(f"令牌：{self.token['token'][:16]}...")
        print()
        
        permissions = self._get_role_permissions()
        print("允许的风险等级:")
        for level in permissions.get("allowed_levels", []):
            print(f"  - {level}")
        print()
        
        print("禁止的风险等级:")
        for level in permissions.get("denied_levels", []):
            print(f"  - {level}")
        print()
        
        print("工具分类示例:")
        examples = {
            "L1_只读": "read_file, memory_search",
            "L2_写入": "write_file, edit_file",
            "L3_删除": "trash, delete_file",
            "L4_系统": "safe_shell_executor",
            "L5_防护": "integrity_checker, emergency_stop"
        }
        for level, tools in examples.items():
            marker = "[OK]" if level in permissions.get("allowed_levels", []) else "[DENIED]"
            print(f"  {marker} {level}: {tools}")
        
        print("=" * 70)


logging.basicConfig(level=logging.INFO)
def main():
    import sys
    
    session_id = None
    role = "Executor"
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--role":
            role = sys.argv[2] if len(sys.argv) > 2 else "Executor"
        elif sys.argv[1] == "--verify":
            tool_id = sys.argv[2] if len(sys.argv) > 2 else "read_file"
            validator = PermissionValidator(session_id, role)
            result = validator.verify_permission(tool_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
        elif sys.argv[1] == "--escalate":
            tool_id = sys.argv[2] if len(sys.argv) > 2 else "unknown"
            reason = sys.argv[3] if len(sys.argv) > 3 else "No reason provided"
            validator = PermissionValidator(session_id, role)
            result = validator.escalate(tool_id, reason)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
    
    validator = PermissionValidator(session_id, role)
    validator.display()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
