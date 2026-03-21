import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUDIT-001 Audit Log Analyzer
【通用审计日志分析器】

功能:
  - 解析日志文件
  - 统计操作频率
  - 检测异常
  - 生成报告

通用性: 适用于任何日志文件分析
"""
import json
import sys
import re
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import statistics

# 配置
AUDIT_DIR = Path("60-DATA/audit_001")


class AuditAnalyzer:
    """审计日志分析器"""
    
    def __init__(self):
        self.audit_dir = AUDIT_DIR
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.audit_dir / "audit_log.json"
        self.report_file = self.audit_dir / "audit_report.json"
    
    def log_event(self, event_type: str, details: dict):
        """记录事件"""
        events = []
        if self.log_file.exists():
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    events = json.load(f)
            except (Exception,):
                pass
        
        event = {
            "type": event_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        events.append(event)
        
        # 保留最近10000条
        events = events[-10000:]
        
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
    
    def parse_log_file(self, file_path: str, pattern: str = None) -> dict:
        """解析日志文件"""
        p = Path(file_path)
        
        if not p.exists():
            return {"status": "error", "message": "File not found"}
        
        events = []
        regex = re.compile(pattern) if pattern else None
        
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if regex:
                    match = regex.search(line)
                    if match:
                        events.append({
                            "raw": line.strip(),
                            "matched": match.group(0)
                        })
                else:
                    events.append({"raw": line.strip()})
        
        return {
            "status": "success",
            "total_lines": len(events),
            "events": events[:100]  # 限制返回数量
        }
    
    def analyze(self, event_type: str = None, limit: int = 100) -> dict:
        """分析日志"""
        if not self.log_file.exists():
            return {"status": "error", "message": "No log file"}
        
        with open(self.log_file, "r", encoding="utf-8") as f:
            events = json.load(f)
        
        if event_type:
            events = [e for e in events if e.get("type") == event_type]
        
        if not events:
            return {"status": "success", "count": 0, "events": []}
        
        # 统计
        type_counts = Counter(e.get("type") for e in events)
        
        # 时间分析
        timestamps = [e.get("timestamp") for e in events if e.get("timestamp")]
        
        # 分析详情
        analysis = {
            "total_events": len(events),
            "event_types": dict(type_counts),
            "first_event": timestamps[0] if timestamps else None,
            "last_event": timestamps[-1] if timestamps else None,
            "events": events[-limit:]
        }
        
        return analysis
    
    def detect_anomalies(self, threshold: int = 10) -> dict:
        """检测异常 - 高频事件"""
        if not self.log_file.exists():
            return {"status": "error", "message": "No log file"}
        
        with open(self.log_file, "r", encoding="utf-8") as f:
            events = json.load(f)
        
        # 按时间窗口分组（每分钟）
        time_windows = defaultdict(int)
        
        for e in events:
            ts = e.get("timestamp", "")
            if ts:
                # 取到分钟
                minute = ts[:16]
                time_windows[minute] += 1
        
        # 找异常窗口
        anomalies = []
        for minute, count in time_windows.items():
            if count >= threshold:
                anomalies.append({
                    "timestamp": minute,
                    "count": count,
                    "severity": "HIGH" if count >= threshold * 2 else "MEDIUM"
                })
        
        anomalies.sort(key=lambda x: x["count"], reverse=True)
        
        return {
            "status": "success",
            "threshold": threshold,
            "anomalies": anomalies[:20],
            "total_anomalies": len(anomalies)
        }
    
    def get_summary(self) -> dict:
        """获取摘要"""
        if not self.log_file.exists():
            return {"status": "error", "message": "No log file"}
        
        with open(self.log_file, "r", encoding="utf-8") as f:
            events = json.load(f)
        
        if not events:
            return {"status": "success", "total": 0}
        
        type_counts = Counter(e.get("type") for e in events)
        
        return {
            "status": "success",
            "total": len(events),
            "event_types": dict(type_counts.most_common(10)),
            "latest": events[-1].get("timestamp") if events else None
        }
    
    def generate_report(self) -> dict:
        """生成完整报告"""
        analysis = self.analyze()
        summary = self.get_summary()
        anomalies = self.detect_anomalies()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "analysis": analysis,
            "anomalies": anomalies
        }
        
        # 保存
        with open(self.report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
    
    def clear_log(self):
        """清空日志"""
        if self.log_file.exists():
            self.log_file.unlink()
        return {"status": "success", "message": "Log cleared"}


logging.basicConfig(level=logging.INFO)
def main():
    analyzer = AuditAnalyzer()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--log":
            # 记录事件: --log TYPE JSON_DETAILS
            event_type = sys.argv[2] if len(sys.argv) > 2 else "test"
            details = {"message": " ".join(sys.argv[3:]) if len(sys.argv) > 3 else {}}
            analyzer.log_event(event_type, details)
            print(json.dumps({"status": "success", "logged": event_type}, ensure_ascii=False))
            return 0
        
        if sys.argv[1] == "--analyze":
            event_type = sys.argv[2] if len(sys.argv) > 2 else None
            result = analyzer.analyze(event_type)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--anomalies":
            threshold = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            result = analyzer.detect_anomalies(threshold)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--summary":
            result = analyzer.get_summary()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--report":
            result = analyzer.generate_report()
            print(json.dumps(result.get("summary", {}), ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--clear":
            result = analyzer.clear_log()
            print(json.dumps(result, ensure_ascii=False))
            return 0
        
        if sys.argv[1] == "--parse":
            file_path = sys.argv[2] if len(sys.argv) > 2 else "app.log"
            pattern = sys.argv[3] if len(sys.argv) > 3 else None
            result = analyzer.parse_log_file(file_path, pattern)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("AUDIT-001 Audit Log Analyzer")
    print("Usage:")
    print("  py audit_001_analyzer.py --log <type> <details>    # Log event")
    print("  py audit_001_analyzer.py --analyze [type]         # Analyze log")
    print("  py audit_001_analyzer.py --anomalies [threshold]  # Detect anomalies")
    print("  py audit_001_analyzer.py --summary                # Get summary")
    print("  py audit_001_analyzer.py --report                  # Generate report")
    print("  py audit_001_analyzer.py --parse <file> [pattern] # Parse log file")
    print("  py audit_001_analyzer.py --clear                    # Clear log")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())