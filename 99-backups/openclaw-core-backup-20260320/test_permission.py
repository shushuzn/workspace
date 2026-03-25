import json
import sys
sys.path.insert(0, "30-scripts-tools")
from permission_validator import PermissionValidator

# 测试 Executor 角色
print("=" * 70)
print("测试 1: Executor 角色 - write_file (L2)")
print("=" * 70)
validator = PermissionValidator(role="Executor")
result = validator.verify_permission("write_file")
print(json.dumps(result, indent=2, ensure_ascii=False))
print()

print("=" * 70)
print("测试 2: Executor 角色 - safe_shell_executor (L4)")
print("=" * 70)
result = validator.verify_permission("safe_shell_executor")
print(json.dumps(result, indent=2, ensure_ascii=False))
print()

print("=" * 70)
print("测试 3: Admin 角色 - safe_shell_executor (L4)")
print("=" * 70)
validator_admin = PermissionValidator(role="Admin")
result = validator_admin.verify_permission("safe_shell_executor")
print(json.dumps(result, indent=2, ensure_ascii=False))
print()

print("=" * 70)
print("测试 4: Critic 角色 - write_file (L2)")
print("=" * 70)
validator_critic = PermissionValidator(role="Critic")
result = validator_critic.verify_permission("write_file")
print(json.dumps(result, indent=2, ensure_ascii=False))
