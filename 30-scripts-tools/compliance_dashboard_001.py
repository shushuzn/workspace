#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
合规仪表板 - 实时显示防护系统状态
【防护 v5 核心】- 可视化监控 + 自动修复建议

功能:
  1. 实时合规率显示
  2. 违规趋势分析
  3. 惩罚状态监控
  4. 自动修复建议
  5. HTML 报告生成
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

STATE_FILE = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
VIOLATION_LOG = Path("30-scripts-tools/violation_log.jsonl")
COMPLIANCE_LOG = Path("30-scripts-tools/shell_compliance_log.jsonl")
PENALTY_FILE = Path("30-scripts-tools/penalty_state.json")
REWARD_FILE = Path("30-scripts-tools/reward_state.json")
STOP_FLAG = Path("30-scripts-tools/.STOP_FLAG")
LOCKDOWN_FILE = Path("30-scripts-tools/.lockdown_active")

class ComplianceDashboard:
    """合规仪表板 - 防护 v5"""
    
    def __init__(self):
        self.session_id = self._get_session_id()
    
    def _get_session_id(self):
        if not STATE_FILE.exists():
            return None
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        return state.get("session_id")
    
    def get_metrics(self) -> dict:
        """获取所有指标"""
        metrics = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "compliance": self._get_compliance_stats(),
            "violations": self._get_violation_stats(),
            "penalty": self._get_penalty_stats(),
            "reward": self._get_reward_stats(),
            "system_status": self._get_system_status(),
            "trend": self._get_trend_analysis(),
            "auto_fix_suggestions": self._get_auto_fix_suggestions()
        }
        return metrics
    
    def _get_compliance_stats(self) -> dict:
        """获取合规统计"""
        compliance_count = 0
        violation_count = 0
        
        if COMPLIANCE_LOG.exists():
            with open(COMPLIANCE_LOG, "r", encoding="utf-8") as f:
                compliance_count = sum(1 for _ in f)
        
        if VIOLATION_LOG.exists():
            with open(VIOLATION_LOG, "r", encoding="utf-8") as f:
                violation_count = sum(1 for _ in f)
        
        total = compliance_count + violation_count
        rate = (compliance_count / total * 100) if total > 0 else 100
        
        return {
            "compliant_calls": compliance_count,
            "violation_calls": violation_count,
            "total_calls": total,
            "compliance_rate": round(rate, 2),
            "status": "excellent" if rate >= 95 else "good" if rate >= 90 else "warning" if rate >= 80 else "critical"
        }
    
    def _get_violation_stats(self) -> dict:
        """获取违规统计"""
        violations = []
        by_type = defaultdict(int)
        by_hour = defaultdict(int)
        
        if VIOLATION_LOG.exists():
            with open(VIOLATION_LOG, "r", encoding="utf-8") as f:
                for line in f:
                    v = json.loads(line)
                    violations.append(v)
                    by_type[v.get("violation_type", "unknown")] += 1
                    
                    # 按小时统计
                    ts = v.get("timestamp", "")
                    if ts:
                        hour = ts[:13]  # YYYY-MM-DDTHH
                        by_hour[hour] += 1
        
        # 最近 10 条违规
        recent = violations[-10:] if violations else []
        
        return {
            "total_violations": len(violations),
            "by_type": dict(by_type),
            "by_hour": dict(by_hour),
            "recent_violations": recent,
            "total_penalty_points": sum(v.get("penalty_points", 0) for v in violations)
        }
    
    def _get_penalty_stats(self) -> dict:
        """获取惩罚统计"""
        if not PENALTY_FILE.exists():
            return {"level": 0, "points": 0, "status": "clean"}
        
        with open(PENALTY_FILE, "r", encoding="utf-8") as f:
            penalty = json.load(f)
        
        level = penalty.get("current_level", 0)
        points = penalty.get("total_points", 0)
        
        status_map = {
            0: "clean",
            1: "warning",
            2: "serious",
            3: "read_only",
            4: "locked"
        }
        
        return {
            "level": level,
            "points": points,
            "status": status_map.get(level, "unknown"),
            "violations_count": len(penalty.get("violations", []))
        }
    
    def _get_reward_stats(self) -> dict:
        """获取奖励统计"""
        if not REWARD_FILE.exists():
            return {"level": 0, "points": 0, "status": "none"}
        
        with open(REWARD_FILE, "r", encoding="utf-8") as f:
            reward = json.load(f)
        
        return {
            "level": reward.get("current_level", 0),
            "points": reward.get("total_points", 0),
            "status": reward.get("status", "none")
        }
    
    def _get_system_status(self) -> dict:
        """获取系统状态"""
        return {
            "stop_flag": STOP_FLAG.exists(),
            "lockdown": LOCKDOWN_FILE.exists(),
            "session_active": self.session_id is not None,
            "protection_tools": self._count_protection_tools()
        }
    
    def _count_protection_tools(self) -> int:
        """统计防护工具数量"""
        registry_file = Path("30-scripts-tools/tools_registry.json")
        if not registry_file.exists():
            return 0
        
        with open(registry_file, "r", encoding="utf-8") as f:
            registry = json.load(f)
        
        tools = registry.get("tools", {})
        return sum(1 for t in tools.values() if t.get("category") == "protection")
    
    def _get_trend_analysis(self) -> dict:
        """趋势分析"""
        # 简单实现：比较最近 1 小时 vs 前 1 小时
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        recent_violations = 0
        previous_violations = 0
        
        if VIOLATION_LOG.exists():
            with open(VIOLATION_LOG, "r", encoding="utf-8") as f:
                for line in f:
                    v = json.loads(line)
                    ts_str = v.get("timestamp", "")
                    try:
                        ts = datetime.fromisoformat(ts_str)
                        if ts > hour_ago:
                            recent_violations += 1
                        elif ts > hour_ago - timedelta(hours=1):
                            previous_violations += 1
                    except (Exception,):
                        pass
        
        trend = "improving" if recent_violations < previous_violations else "worsening" if recent_violations > previous_violations else "stable"
        
        return {
            "recent_violations": recent_violations,
            "previous_violations": previous_violations,
            "trend": trend,
            "change_rate": round((recent_violations - previous_violations) / max(previous_violations, 1) * 100, 1)
        }
    
    def _get_auto_fix_suggestions(self) -> list:
        """自动生成修复建议"""
        suggestions = []
        
        # 避免递归：直接获取必要数据
        compliance_count = 0
        violation_count = 0
        
        if COMPLIANCE_LOG.exists():
            with open(COMPLIANCE_LOG, "r", encoding="utf-8") as f:
                compliance_count = sum(1 for _ in f)
        
        if VIOLATION_LOG.exists():
            with open(VIOLATION_LOG, "r", encoding="utf-8") as f:
                violation_count = sum(1 for _ in f)
        
        total = compliance_count + violation_count
        compliance_rate = (compliance_count / total * 100) if total > 0 else 100
        
        # 获取惩罚等级
        penalty_level = 0
        if PENALTY_FILE.exists():
            with open(PENALTY_FILE, "r", encoding="utf-8") as f:
                penalty = json.load(f)
                penalty_level = penalty.get("current_level", 0)
        
        # 合规率低于 90%
        if compliance_rate < 90:
            suggestions.append({
                "priority": "high",
                "issue": f"合规率过低 ({compliance_rate}%)",
                "action": "检查所有脚本是否通过防护层执行",
                "auto_fix": "py 30-scripts-tools/safe_shell_executor.py <command>"
            })
        
        # 惩罚等级 >= 2
        if penalty_level >= 2:
            suggestions.append({
                "priority": "critical",
                "issue": f"惩罚等级过高 (Level {penalty_level})",
                "action": "立即停止所有操作，检查违规原因",
                "auto_fix": "检查 violation_log.jsonl"
            })
        
        # 系统停止
        if STOP_FLAG.exists():
            suggestions.append({
                "priority": "critical",
                "issue": "系统处于停止状态",
                "action": "需要管理员恢复",
                "auto_fix": "删除 .STOP_FLAG 文件（管理员）"
            })
        
        # 无活跃会话
        if not self.session_id:
            suggestions.append({
                "priority": "high",
                "issue": "没有活跃会话",
                "action": "通过 copaw_entry.py 启动新会话",
                "auto_fix": "py 30-scripts-tools/copaw_entry.py \"Task Name\""
            })
        
        return suggestions
    
    def generate_html_report(self, output_path: str = "30-scripts-tools/compliance_report.html"):
        """生成 HTML 报告"""
        metrics = self.get_metrics()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>防护系统合规报告 - {metrics['session_id']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 20px; border: 1px solid #ccc; border-radius: 5px; }}
        .excellent {{ background-color: #d4edda; }}
        .good {{ background-color: #d1ecf1; }}
        .warning {{ background-color: #fff3cd; }}
        .critical {{ background-color: #f8d7da; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>防护系统合规报告</h1>
    <p>会话：{metrics['session_id']}</p>
    <p>时间：{metrics['timestamp']}</p>
    
    <h2>核心指标</h2>
    <div class="metric {metrics['compliance']['status']}">
        <h3>合规率</h3>
        <p style="font-size: 2em;">{metrics['compliance']['compliance_rate']}%</p>
        <p>状态：{metrics['compliance']['status']}</p>
    </div>
    
    <div class="metric">
        <h3>违规总数</h3>
        <p style="font-size: 2em;">{metrics['violations']['total_violations']}</p>
        <p>惩罚分：{metrics['violations']['total_penalty_points']}</p>
    </div>
    
    <div class="metric">
        <h3>惩罚等级</h3>
        <p style="font-size: 2em;">Level {metrics['penalty']['level']}</p>
        <p>状态：{metrics['penalty']['status']}</p>
    </div>
    
    <div class="metric">
        <h3>防护工具</h3>
        <p style="font-size: 2em;">{metrics['system_status']['protection_tools']}</p>
    </div>
    
    <h2>趋势分析</h2>
    <p>趋势：{metrics['trend']['trend']}</p>
    <p>变化率：{metrics['trend']['change_rate']}%</p>
    
    <h2>自动修复建议</h2>
    <table>
        <tr><th>优先级</th><th>问题</th><th>操作</th><th>自动修复命令</th></tr>
"""
        
        for s in metrics["auto_fix_suggestions"]:
            html += f"""<tr>
                <td>{s['priority']}</td>
                <td>{s['issue']}</td>
                <td>{s['action']}</td>
                <td><code>{s['auto_fix']}</code></td>
            </tr>"""
        
        html += """
    </table>
</body>
</html>"""
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        return output_path
    
    def display(self):
        """在终端显示仪表板"""
        metrics = self.get_metrics()
        
        print("=" * 70)
        print("防护系统合规仪表板 v5.0")
        print("=" * 70)
        print(f"会话：{metrics['session_id']}")
        print(f"时间：{metrics['timestamp']}")
        print()
        
        print("核心指标:")
        print(f"  合规率：{metrics['compliance']['compliance_rate']}% ({metrics['compliance']['status']})")
        print(f"  合规调用：{metrics['compliance']['compliant_calls']}")
        print(f"  违规调用：{metrics['compliance']['violation_calls']}")
        print()
        
        print("惩罚状态:")
        print(f"  等级：Level {metrics['penalty']['level']} ({metrics['penalty']['status']})")
        print(f"  总分：{metrics['penalty']['points']}")
        print()
        
        print("系统状态:")
        print(f"  停止标志：{'是' if metrics['system_status']['stop_flag'] else '否'}")
        print(f"  系统封锁：{'是' if metrics['system_status']['lockdown'] else '否'}")
        print(f"  防护工具：{metrics['system_status']['protection_tools']}")
        print()
        
        print("趋势分析:")
        print(f"  趋势：{metrics['trend']['trend']}")
        print(f"  变化率：{metrics['trend']['change_rate']}%")
        print()
        
        if metrics["auto_fix_suggestions"]:
            print("自动修复建议:")
            for i, s in enumerate(metrics["auto_fix_suggestions"], 1):
                print(f"  {i}. [{s['priority']}] {s['issue']}")
                print(f"     操作：{s['action']}")
                print(f"     命令：{s['auto_fix']}")
        else:
            print("自动修复建议：无（系统运行正常）")
        
        print("=" * 70)


def main():
    dashboard = ComplianceDashboard()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--html":
        output = dashboard.generate_html_report()
        print(f"HTML 报告已生成：{output}")
        return 0
    
    dashboard.display()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
