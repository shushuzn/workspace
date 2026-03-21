#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
合规率提升引擎 - 自动分析 + 智能提升
【防护 v8 核心】- 根因分析 + 自动训练 + 行为优化

功能:
  1. 分析合规率低的根因
  2. 生成针对性改进方案
  3. 自动训练 Agent 行为
  4. 实时监控合规趋势
  5. 智能推荐最佳实践
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

VIOLATION_LOG = Path("30-scripts-tools/violation_log.jsonl")
TOOL_CALL_LOG = Path("30-scripts-tools/tool_call_log.jsonl")
COMPLIANCE_REPORT = Path("30-scripts-tools/compliance_report.json")

class ComplianceBooster:
    """合规率提升引擎 - 防护 v8"""
    
    def __init__(self):
        self.session_id = self._get_session_id()
        self.violations = self._load_violations()
        self.tool_calls = self._load_tool_calls()
    
    def _get_session_id(self):
        state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
        if not state_file.exists():
            return None
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        return state.get("session_id")
    
    def _load_violations(self, limit=100):
        """加载违规记录"""
        if not VIOLATION_LOG.exists():
            return []
        
        with open(VIOLATION_LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        violations = []
        for line in lines[-limit:]:
            try:
                violations.append(json.loads(line))
            except (json.JSONDecodeError, IOError, OSError):
                pass
        
        return violations
    
    def _load_tool_calls(self, limit=1000):
        """加载工具调用记录"""
        if not TOOL_CALL_LOG.exists():
            return []
        
        with open(TOOL_CALL_LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        calls = []
        for line in lines[-limit:]:
            try:
                calls.append(json.loads(line))
            except (json.JSONDecodeError, IOError, OSError):
                pass
        
        return calls
    
    def analyze_root_causes(self) -> dict:
        """分析合规率低的根因"""
        if not self.violations:
            return {
                "total_violations": 0,
                "root_causes": [],
                "compliance_rate": 100.0
            }
        
        # 统计违规类型
        violation_types = {}
        for v in self.violations:
            v_type = v.get("violation_type", "unknown")
            violation_types[v_type] = violation_types.get(v_type, 0) + 1
        
        # 分析根因
        root_causes = []
        for v_type, count in sorted(violation_types.items(), key=lambda x: -x[1]):
            cause = self._identify_root_cause(v_type)
            root_causes.append({
                "type": v_type,
                "count": count,
                "percentage": count / len(self.violations) * 100,
                "root_cause": cause["root"],
                "solution": cause["solution"],
                "priority": cause["priority"]
            })
        
        # 计算合规率
        total_actions = len(self.violations) + len(self.tool_calls)
        compliance_rate = (len(self.tool_calls) / total_actions * 100) if total_actions > 0 else 0
        
        return {
            "total_violations": len(self.violations),
            "total_tool_calls": len(self.tool_calls),
            "compliance_rate": compliance_rate,
            "root_causes": root_causes
        }
    
    def _identify_root_cause(self, violation_type: str) -> dict:
        """识别根因"""
        cause_map = {
            "integrity_violation": {
                "root": "防护文件被篡改或会话伪造",
                "solution": "加强完整性检查，使用 blockchain_logger 记录所有操作",
                "priority": "critical"
            },
            "bypass_attempt": {
                "root": "尝试绕过防护层（如 --no-verify）",
                "solution": "强化 Git hook，使用 anti_bypass_engine 实时监控",
                "priority": "critical"
            },
            "protection_bypass": {
                "root": "直接使用 execute_shell_command 而非 safe_shell_executor",
                "solution": "所有 shell 命令必须通过 safe_shell_executor.py",
                "priority": "high"
            },
            "workflow_violation": {
                "root": "未遵循 20 步工作流",
                "solution": "使用 workflow_helper.py 逐步执行，Git hook 强制检查",
                "priority": "high"
            },
            "session_invalid": {
                "root": "未通过 copaw_entry.py 启动会话",
                "solution": "所有会话必须从 copaw_entry.py 开始",
                "priority": "critical"
            },
            "unknown": {
                "root": "未知违规类型",
                "solution": "检查 violation_log.jsonl 详情",
                "priority": "medium"
            }
        }
        
        return cause_map.get(violation_type, cause_map["unknown"])
    
    def generate_improvement_plan(self) -> list:
        """生成改进计划"""
        analysis = self.analyze_root_causes()
        
        plan = []
        for i, cause in enumerate(analysis["root_causes"], 1):
            plan.append({
                "step": i,
                "issue": cause["root_cause"],
                "action": cause["solution"],
                "priority": cause["priority"],
                "estimated_impact": f"+{cause['percentage']*0.8:.1f}% 合规率"
            })
        
        # 添加通用建议
        plan.append({
            "step": len(plan) + 1,
            "issue": "合规意识不足",
            "action": "每次操作前检查：是否通过防护层？",
            "priority": "medium",
            "estimated_impact": "+10% 合规率"
        })
        
        plan.append({
            "step": len(plan) + 1,
            "issue": "缺乏实时监控",
            "action": "使用 compliance_dashboard.py 实时监控",
            "priority": "medium",
            "estimated_impact": "+5% 合规率"
        })
        
        return plan
    
    def auto_train(self) -> dict:
        """自动训练（生成最佳实践）"""
        # 分析成功模式
        successful_patterns = []
        
        # 统计最常用的合规工具
        tool_usage = {}
        for call in self.tool_calls:
            tool = call.get("tool_id", "unknown")
            tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        # 找出 Top 5 合规工具
        top_tools = sorted(tool_usage.items(), key=lambda x: -x[1])[:5]
        
        training_result = {
            "top_compliant_tools": [
                {"tool": tool, "usage": count}
                for tool, count in top_tools
            ],
            "best_practices": [
                "所有 Python 脚本通过 protected_py.py 执行",
                "所有 Shell 命令通过 safe_shell_executor.py 执行",
                "所有会话从 copaw_entry.py 开始",
                "所有 Git 提交通过 git_commit_helper.py 执行",
                "使用 compliance_dashboard.py 实时监控"
            ],
            "anti_patterns": [
                "直接使用 execute_shell_command",
                "使用 git commit --no-verify",
                "手动修改 execution-state.json",
                "跳过 workflow 步骤",
                "直接删除防护文件"
            ]
        }
        
        return training_result
    
    def display(self):
        """显示分析报告"""
        analysis = self.analyze_root_causes()
        plan = self.generate_improvement_plan()
        training = self.auto_train()
        
        print("=" * 70)
        print("合规率提升引擎 v8.0 - 分析报告")
        print("=" * 70)
        print(f"会话：{self.session_id}")
        print(f"时间：{datetime.now().isoformat()}")
        print()
        
        print("核心指标:")
        print(f"  总违规数：{analysis['total_violations']}")
        print(f"  总工具调用：{analysis['total_tool_calls']}")
        print(f"  合规率：{analysis['compliance_rate']:.1f}%")
        print()
        
        if analysis["root_causes"]:
            print("根因分析 (Top 5):")
            for cause in analysis["root_causes"][:5]:
                priority_icon = "[CRITICAL]" if cause["priority"] == "critical" else "[HIGH]"
                print(f"  {priority_icon} {cause['type']}: {cause['count']} 次 ({cause['percentage']:.1f}%)")
                print(f"     根因：{cause['root_cause']}")
                print(f"     解决：{cause['solution']}")
        else:
            print("[OK] 无违规记录")
        print()
        
        print("改进计划:")
        for step in plan[:5]:
            print(f"  {step['step']}. [{step['priority'].upper()}] {step['issue']}")
            print(f"     行动：{step['action']}")
            print(f"     影响：{step['estimated_impact']}")
        print()
        
        print("最佳实践:")
        for practice in training["best_practices"]:
            print(f"  [OK] {practice}")
        print()
        
        print("避免行为:")
        for pattern in training["anti_patterns"]:
            print(f"  [FAIL] {pattern}")
        print("=" * 70)
    
    def save_report(self):
        """保存报告"""
        report = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "analysis": self.analyze_root_causes(),
            "improvement_plan": self.generate_improvement_plan(),
            "training": self.auto_train()
        }
        
        with open(COMPLIANCE_REPORT, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return str(COMPLIANCE_REPORT)


def main():
    import sys
    
    booster = ComplianceBooster()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--report":
            report_file = booster.save_report()
            print(f"报告已保存：{report_file}")
            return 0
        elif sys.argv[1] == "--train":
            training = booster.auto_train()
            print(json.dumps(training, indent=2, ensure_ascii=False))
            return 0
    
    # 默认：显示分析
    booster.display()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
