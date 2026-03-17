"""
Medium Watcher 路线图自动更新脚本
每小时运行一次，更新指标状态和任务优先级
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_DIR = Path("D:/obsidian/Vault/Medium")
ROADMAP_FILE = OUTPUT_DIR / "ROADMAP.md"
STATS_FILE = OUTPUT_DIR / ".watcher-stats.json"
LOG_FILE = OUTPUT_DIR / "watcher-log.md"


def load_stats():
    if STATS_FILE.exists():
        try:
            return json.load(open(STATS_FILE, "r", encoding="utf-8"))
        except:
            return {}
    return {}


def count_successful_runs():
    if not LOG_FILE.exists():
        return 0, 0
    content = LOG_FILE.read_text(encoding="utf-8")
    success_count = content.count("成功")
    total_count = content.count("### 2026-")
    return success_count, total_count


def calculate_north_star(stats: dict) -> tuple:
    total_articles = stats.get("total_articles", 0)
    total_notes = stats.get("total_notes", 0)
    total_runs = stats.get("total_runs", 0)
    
    if total_runs == 0:
        return 0, "stalled"
    
    success_rate = (total_notes / total_runs * 100) if total_runs > 0 else 0
    trend = "stalled" if total_notes == 0 else ("up" if total_notes > 0 else "down")
    
    return min(success_rate, 100), trend


def determine_mode(north_star: float, risk_level: str) -> str:
    if risk_level == "高":
        return "Recovery Mode"
    if north_star >= 85:
        return "Hardening Mode"
    if north_star >= 50:
        return "Optimization Mode"
    return "Acceleration Mode"


def determine_risk_level(stats: dict) -> str:
    total_runs = stats.get("total_runs", 0)
    total_notes = stats.get("total_notes", 0)
    errors = stats.get("errors", [])
    
    if len(errors) > 5 or (total_runs > 0 and total_notes == 0):
        return "高"
    if len(errors) > 0:
        return "中"
    return "低"


def update_roadmap():
    stats = load_stats()
    north_star, trend = calculate_north_star(stats)
    risk_level = determine_risk_level(stats)
    mode = determine_mode(north_star, risk_level)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    if not ROADMAP_FILE.exists():
        print("[WARN] Roadmap file not found")
        return None
    
    content = ROADMAP_FILE.read_text(encoding="utf-8")
    
    # 更新指标块
    error_rate = len(stats.get('errors', [])) / max(stats.get('total_runs', 1), 1) * 100
    stalled = "30+ 分钟" if stats.get('total_notes', 0) == 0 and stats.get('total_runs', 0) > 2 else "<30 分钟"
    
    metrics_block = f"""<!-- AUTO:METRICS-START -->
## 当前指标 ({timestamp})

| 指标 | 目标 | 当前 | 达成率 |
|------|------|------|--------|
| **North Star**: 搜集成功率 | ≥95% | {north_star:.1f}% | {north_star/95*100:.1f}% |
| **支持指标**: 文章抓取数 | ≥10/小时 | {stats.get('total_articles', 0)} | {stats.get('total_articles', 0)/10*100:.1f}% |
| **支持指标**: 笔记生成数 | ≥10/小时 | {stats.get('total_notes', 0)} | {stats.get('total_notes', 0)/10*100:.1f}% |
| **风险指标**: 错误率 | <5% | {error_rate:.1f}% | {"❌" if error_rate > 5 else "✅"} |
| **风险指标**: 停滞时间 | <30 分钟 | {stalled} | {"❌" if stalled == "30+ 分钟" else "✅"} |
<!-- AUTO:METRICS-END -->"""
    
    pattern = r"<!-- AUTO:METRICS-START -->.*?<!-- AUTO:METRICS-END -->"
    content = re.sub(pattern, metrics_block, content, flags=re.DOTALL)
    
    # 更新下次更新时间
    next_hour = (datetime.now().replace(minute=0, second=0, microsecond=0).timestamp() + 3600)
    next_update = datetime.fromtimestamp(next_hour).strftime("%Y-%m-%d %H:%M")
    
    content = re.sub(r"\*Last updated: .*\*", f"*Last updated: {timestamp}*", content)
    content = re.sub(r"\*Next auto-update: .*\*", f"*Next auto-update: {next_update}*", content)
    
    ROADMAP_FILE.write_text(content, encoding="utf-8")
    
    # 生成小时报告
    report_dir = OUTPUT_DIR / "Reports"
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / f"Hourly-{timestamp.replace(':', '-')}.md"
    
    report_content = f"""---
created: {timestamp}
type: hourly-report
tags: [medium-watcher, hourly-report]
---

# Medium Watcher 小时报告

## 指标摘要

- **North Star**: {north_star:.1f}% ({trend})
- **模式**: {mode}
- **风险等级**: {risk_level}

## 统计数据

| 指标 | 值 |
|------|-----|
| 总运行次数 | {stats.get('total_runs', 0)} |
| 总文章数 | {stats.get('total_articles', 0)} |
| 总笔记数 | {stats.get('total_notes', 0)} |
| 错误数 | {len(stats.get('errors', []))} |

---
*自动生成*
"""
    
    report_file.write_text(report_content, encoding="utf-8")
    
    return {
        "north_star": north_star,
        "trend": trend,
        "mode": mode,
        "risk_level": risk_level,
        "next_update": next_update
    }


if __name__ == "__main__":
    result = update_roadmap()
    if result:
        print(f"[OK] Roadmap updated | North Star: {result['north_star']:.1f}% | Mode: {result['mode']}")
    else:
        print("[WARN] Roadmap file not found")
