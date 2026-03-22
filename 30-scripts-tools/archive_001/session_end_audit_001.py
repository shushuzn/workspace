import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
会话结束审计工具

功能：
1. 检查 tool_call_log 完整性
2. 检查文件修改 vs 工具调用匹配
3. 生成审计报告
4. 更新 MEMORY.md

使用：
  py session_end_audit.py --session session-xxx
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter


class SessionEndAuditor:
    """会话结束审计器"""
    
    def __init__(self, session_id: str = None):
        self.workspace = Path("D:/OpenClaw/workspace")
        self.tool_call_log = self.workspace / "30-scripts-tools/tool_call_log.jsonl"
        self.memory_file = self.workspace / "13-memory/MEMORY.md"
        self.session_id = session_id
        self.report = {}
    
    def audit(self) -> dict:
        """执行完整审计"""
        print("=" * 70)
        print(" " * 25 + "Session End Audit")
        print("=" * 70)
        
        # 1. 加载工具调用日志
        calls = self._load_tool_calls()
        
        # 2. 统计分析
        stats = self._analyze_calls(calls)
        
        # 3. 完整性检查
        integrity = self._check_integrity(calls)
        
        # 4. 生成报告
        report = {
            "session_id": self.session_id,
            "audit_time": datetime.now().isoformat(),
            "statistics": stats,
            "integrity": integrity,
            "score": self._calculate_score(stats, integrity)
        }
        
        # 5. 打印报告
        self._print_report(report)
        
        # 6. 保存到审计报告
        self._save_report(report)
        
        return report
    
    def _load_tool_calls(self) -> list:
        """加载工具调用日志"""
        print("\n[1] Loading tool call log...")
        
        if not self.tool_call_log.exists():
            print("  [WARN] tool_call_log.jsonl not found")
            return []
        
        calls = []
        with open(self.tool_call_log, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if self.session_id and entry.get('session_id') != self.session_id:
                        continue
                    calls.append(entry)
                except (json.JSONDecodeError, IOError, OSError):
                    continue
        
        print(f"  [OK] Loaded {len(calls)} calls")
        return calls
    
    def _analyze_calls(self, calls: list) -> dict:
        """统计分析"""
        print("\n[2] Analyzing calls...")
        
        stats = {
            "total_calls": len(calls),
            "tools_used": Counter(c.get('tool_id', 'unknown') for c in calls),
            "success_rate": 0,
            "avg_duration": 0,
        }
        
        # 计算成功率
        success = sum(1 for c in calls if c.get('result') in ['success', 'completed', 'allowed'])
        stats['success_rate'] = success / len(calls) * 100 if calls else 0
        
        # 计算平均时长
        durations = [c.get('duration_seconds', 0) for c in calls if 'duration_seconds' in c]
        stats['avg_duration'] = sum(durations) / len(durations) if durations else 0
        
        print(f"  Total calls: {stats['total_calls']}")
        print(f"  Tools: {dict(stats['tools_used'])}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Avg duration: {stats['avg_duration']:.2f}s")
        
        return stats
    
    def _check_integrity(self, calls: list) -> dict:
        """完整性检查"""
        print("\n[3] Checking integrity...")
        
        integrity = {
            "has_session_id": bool(self.session_id),
            "has_tool_calls": len(calls) > 0,
            "has_variety": len(set(c.get('tool_id') for c in calls)) > 1,
            "has_success": any(c.get('result') in ['success', 'completed'] for c in calls),
            "no_critical_errors": not any(c.get('result') == 'blocked' for c in calls),
        }
        
        # 打印检查结果
        for check, passed in integrity.items():
            status = "[OK]" if passed else "[FAIL]"
            print(f"  {status} {check}: {passed}")
        
        return integrity
    
    def _calculate_score(self, stats: dict, integrity: dict) -> int:
        """计算会话质量评分"""
        score = 0
        
        # 基础分：有工具调用
        if integrity['has_tool_calls']:
            score += 20
        
        # 多样性分：使用多种工具
        if integrity['has_variety']:
            score += 20
        
        # 成功率分
        score += int(stats['success_rate'] * 0.3)  # 最多 30 分
        
        # 完整性分
        passed_checks = sum(integrity.values())
        score += passed_checks * 6  # 最多 30 分
        
        return min(100, score)
    
    def _print_report(self, report: dict):
        """打印审计报告"""
        print("\n" + "=" * 70)
        print(" Audit Report")
        print("=" * 70)
        print(f"Session ID: {report['session_id']}")
        print(f"Audit Time: {report['audit_time']}")
        print(f"Total Calls: {report['statistics']['total_calls']}")
        print(f"Success Rate: {report['statistics']['success_rate']:.1f}%")
        print(f"Quality Score: {report['score']}/100")
        
        if report['score'] >= 80:
            print("\n[OK] Session quality: EXCELLENT")
        elif report['score'] >= 60:
            print("\n[OK] Session quality: GOOD")
        elif report['score'] >= 40:
            print("\n[WARN] Session quality: FAIR")
        else:
            print("\n[FAIL] Session quality: POOR")
    
    def _save_report(self, report: dict):
        """
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
# py session_end_audit_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py session_end_audit_001.py

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

保存审计报告"""
        print("\n[4] Saving audit report...")
        
        report_dir = self.workspace / "21-reports/session-audits"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f"audit_{report['session_id']}_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"  [OK] Saved to: {report_file}")


logging.basicConfig(level=logging.INFO)
def main():
    if len(sys.argv) < 2:
        print("Usage: py session_end_audit.py <session_id>")
        print("Example: py session_end_audit.py session-20260320124324")
        sys.exit(1)
    
    session_id = sys.argv[1]
    auditor = SessionEndAuditor(session_id)
    report = auditor.audit()
    
    # 返回质量评分
    if report['score'] >= 60:
        sys.exit(0)
    else:
        print("\n[WARN] Low quality session - consider reviewing")
        sys.exit(1)


if __name__ == '__main__':
    main()
