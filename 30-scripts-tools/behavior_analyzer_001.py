#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI 行为分析器 - 异常检测 + 模式识别
【防护 v8 核心】- 行为建模 + 异常检测 + 预测预警

功能:
  1. 建立 Agent 行为模型
  2. 检测异常行为模式
  3. 预测潜在违规
  4. 生成行为报告
  5. 实时预警
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

TOOL_CALL_LOG = Path("30-scripts-tools/tool_call_log.jsonl")
VIOLATION_LOG = Path("30-scripts-tools/violation_log.jsonl")
BEHAVIOR_REPORT = Path("30-scripts-tools/behavior_analysis.json")

class BehaviorAnalyzer:
    """AI 行为分析器 - 防护 v8"""
    
    def __init__(self):
        self.tool_calls = self._load_tool_calls()
        self.violations = self._load_violations()
        self.behavior_model = self._build_behavior_model()
    
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
            except:
                pass
        
        return calls
    
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
            except:
                pass
        
        return violations
    
    def _build_behavior_model(self) -> dict:
        """建立行为模型"""
        model = {
            "tool_usage": defaultdict(int),
            "hourly_pattern": defaultdict(int),
            "session_patterns": defaultdict(list),
            "violation_correlation": defaultdict(list)
        }
        
        # 统计工具使用
        for call in self.tool_calls:
            tool = call.get("tool_id", "unknown")
            model["tool_usage"][tool] += 1
            
            # 小时模式
            ts = call.get("timestamp", "")
            if ts:
                try:
                    hour = datetime.fromisoformat(ts).hour
                    model["hourly_pattern"][hour] += 1
                except:
                    pass
            
            # Session 模式
            session = call.get("session_id", "unknown")
            model["session_patterns"][session].append(call)
        
        # 违规关联
        for v in self.violations:
            session = v.get("session_id", "unknown")
            model["violation_correlation"][session].append(v)
        
        return model
    
    def detect_anomalies(self) -> list:
        """检测异常行为"""
        anomalies = []
        
        # 异常 1: 工具使用频率异常
        avg_usage = sum(self.behavior_model["tool_usage"].values()) / max(len(self.behavior_model["tool_usage"]), 1)
        for tool, count in self.behavior_model["tool_usage"].items():
            if count > avg_usage * 5:  # 超过平均 5 倍
                anomalies.append({
                    "type": "tool_overuse",
                    "tool": tool,
                    "count": count,
                    "severity": "medium",
                    "description": f"工具 {tool} 使用频率异常 ({count} 次)"
                })
        
        # 异常 2: 时间模式异常（深夜高频操作）
        for hour, count in self.behavior_model["hourly_pattern"].items():
            if hour in [0, 1, 2, 3, 4, 5] and count > 50:  # 凌晨 0-5 点高频
                anomalies.append({
                    "type": "abnormal_time_pattern",
                    "hour": hour,
                    "count": count,
                    "severity": "low",
                    "description": f"凌晨 {hour} 点有 {count} 次操作"
                })
        
        # 异常 3: Session 违规率高
        for session, violations in self.behavior_model["violation_correlation"].items():
            if len(violations) >= 3:
                anomalies.append({
                    "type": "high_violation_session",
                    "session": session,
                    "violation_count": len(violations),
                    "severity": "high",
                    "description": f"会话 {session} 有 {len(violations)} 次违规"
                })
        
        # 异常 4: 违规时间聚集
        if self.violations:
            violation_times = []
            for v in self.violations:
                ts = v.get("timestamp", "")
                if ts:
                    try:
                        violation_times.append(datetime.fromisoformat(ts))
                    except:
                        pass
            
            if len(violation_times) >= 2:
                violation_times.sort()
                for i in range(1, len(violation_times)):
                    diff = (violation_times[i] - violation_times[i-1]).total_seconds()
                    if diff < 60:  # 1 分钟内多次违规
                        anomalies.append({
                            "type": "violation_cluster",
                            "time_diff": diff,
                            "severity": "high",
                            "description": f"{diff:.0f} 秒内发生多次违规"
                        })
        
        return anomalies
    
    def predict_risks(self) -> list:
        """预测潜在风险"""
        risks = []
        
        # 风险 1: 违规趋势上升
        if len(self.violations) >= 5:
            recent = self.violations[-5:]
            timestamps = []
            for v in recent:
                ts = v.get("timestamp", "")
                if ts:
                    try:
                        timestamps.append(datetime.fromisoformat(ts))
                    except:
                        pass
            
            if len(timestamps) >= 2:
                time_diffs = [(timestamps[i] - timestamps[i-1]).total_seconds() 
                             for i in range(1, len(timestamps))]
                avg_diff = sum(time_diffs) / len(time_diffs)
                
                if avg_diff < 300:  # 平均 5 分钟内违规
                    risks.append({
                        "type": "escalating_violations",
                        "severity": "critical",
                        "description": f"违规频率上升（平均 {avg_diff:.0f} 秒/次）",
                        "recommendation": "立即停止操作，检查违规原因"
                    })
        
        # 风险 2: 惩罚等级接近阈值
        penalty_file = Path("30-scripts-tools/penalty_state.json")
        if penalty_file.exists():
            with open(penalty_file, "r", encoding="utf-8") as f:
                penalty = json.load(f)
            
            current_level = penalty.get("current_level", 0)
            total_points = penalty.get("total_points", 0)
            
            if current_level >= 3:
                risks.append({
                    "type": "near_lockdown",
                    "severity": "critical",
                    "description": f"惩罚等级 {current_level}，接近封锁（Level 4）",
                    "recommendation": "使用 auto_fix_engine.py 重置惩罚状态"
                })
            elif total_points >= 40:
                risks.append({
                    "type": "approaching_level_3",
                    "severity": "high",
                    "description": f"惩罚分 {total_points}，接近 Level 3",
                    "recommendation": "减少违规操作"
                })
        
        # 风险 3: 关键工具未使用
        critical_tools = [
            "copaw-entry",
            "tool-executor",
            "safe-shell-executor",
            "workflow-helper"
        ]
        
        used_tools = set(self.behavior_model["tool_usage"].keys())
        missing_tools = [t for t in critical_tools if t not in used_tools]
        
        if missing_tools:
            risks.append({
                "type": "missing_critical_tools",
                "severity": "high",
                "description": f"关键工具未使用：{', '.join(missing_tools)}",
                "recommendation": "确保所有操作通过关键防护工具"
            })
        
        return risks
    
    def generate_behavior_report(self) -> dict:
        """生成行为报告"""
        anomalies = self.detect_anomalies()
        risks = self.predict_risks()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tool_calls": len(self.tool_calls),
                "total_violations": len(self.violations),
                "unique_tools": len(self.behavior_model["tool_usage"]),
                "unique_sessions": len(self.behavior_model["session_patterns"])
            },
            "top_tools": sorted(
                [{"tool": k, "count": v} for k, v in self.behavior_model["tool_usage"].items()],
                key=lambda x: -x["count"]
            )[:10],
            "anomalies": anomalies,
            "risks": risks,
            "health_score": self._calculate_health_score()
        }
        
        return report
    
    def _calculate_health_score(self) -> float:
        """计算健康分数（0-100）"""
        score = 100.0
        
        # 违规扣分
        score -= len(self.violations) * 5
        
        # 异常扣分
        anomalies = self.detect_anomalies()
        for a in anomalies:
            if a["severity"] == "critical":
                score -= 20
            elif a["severity"] == "high":
                score -= 10
            elif a["severity"] == "medium":
                score -= 5
            else:
                score -= 2
        
        # 风险扣分
        risks = self.predict_risks()
        for r in risks:
            if r["severity"] == "critical":
                score -= 30
            elif r["severity"] == "high":
                score -= 15
            else:
                score -= 5
        
        return max(0, min(100, score))
    
    def display(self):
        """显示行为分析"""
        report = self.generate_behavior_report()
        
        print("=" * 70)
        print("AI 行为分析器 v8.0")
        print("=" * 70)
        print(f"时间：{report['timestamp']}")
        print()
        
        print("行为摘要:")
        print(f"  工具调用：{report['summary']['total_tool_calls']} 次")
        print(f"  违规记录：{report['summary']['total_violations']} 次")
        print(f"  使用工具：{report['summary']['unique_tools']} 种")
        print(f"  会话数：{report['summary']['unique_sessions']} 个")
        print()
        
        print("Top 工具:")
        for tool in report["top_tools"][:5]:
            print(f"  {tool['tool']}: {tool['count']} 次")
        print()
        
        print("异常检测:")
        if report["anomalies"]:
            for a in report["anomalies"][:5]:
                icon = "[HIGH]" if a["severity"] == "high" else "[MEDIUM]"
                print(f"  {icon} {a['type']}: {a['description']}")
        else:
            print("  [OK] 无异常")
        print()
        
        print("风险预测:")
        if report["risks"]:
            for r in report["risks"][:5]:
                icon = "[CRITICAL]" if r["severity"] == "critical" else "[HIGH]"
                print(f"  {icon} {r['type']}: {r['description']}")
                print(f"      建议：{r['recommendation']}")
        else:
            print("  [OK] 无风险")
        print()
        
        print(f"健康分数：{report['health_score']:.1f}/100")
        if report["health_score"] >= 80:
            print("状态：[OK] 良好")
        elif report["health_score"] >= 60:
            print("状态：[WARN] 需改进")
        else:
            print("状态：[CRITICAL] 危险")
        print("=" * 70)
    
    def save_report(self):
        """保存报告"""
        report = self.generate_behavior_report()
        
        with open(BEHAVIOR_REPORT, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return str(BEHAVIOR_REPORT)


def main():
    import sys
    
    analyzer = BehaviorAnalyzer()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--report":
            report_file = analyzer.save_report()
            print(f"报告已保存：{report_file}")
            return 0
        elif sys.argv[1] == "--predict":
            risks = analyzer.predict_risks()
            print(json.dumps(risks, indent=2, ensure_ascii=False))
            return 0
    
    # 默认：显示分析
    analyzer.display()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
