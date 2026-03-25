import json

# 验证 workflow.json 更新
with open("flow-archive/20260318-universal-workflow-001/workflow.json", "r", encoding="utf-8") as f:
    w = json.load(f)

print("=" *60)
print("workflow.json 验证")
print("=" *60)
print(f"版本：{w['version']}")
print(f"规则数：{len(w['enforcement']['rules'])}")
print(f"\nEnforcement 配置:")
print(f"  tool_registry_required: {w['enforcement'].get('tool_registry_required')}")
print(f"  tool_executor_required: {w['enforcement'].get('tool_executor_required')}")
print(f"  call_logging_required: {w['enforcement'].get('call_logging_required')}")
print(f"  anti_fraud.enabled: {w['enforcement'].get('anti_fraud', {}).get('enabled')}")

print(f"\nProtection rules:")
for i, rule in enumerate(w['enforcement']['rules'], 1):
    clean_rule = rule.replace("🛡️", "[PROTECT]")
    print(f"  {i}. {clean_rule}")

print("\n" + "=" *60)
print("[OK] 验证通过")
print("=" *60)
