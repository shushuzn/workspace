#!/usr/bin/env python3
"""
Research Statistics Dashboard - 研究统计看板

功能:
- 论文收集统计
- 笔记生成统计
- 知识图谱统计
- 趋势分析

使用:
    python research-stats.py --workspace D:\OpenClaw\workspace
    python research-stats.py --output reports\weekly-stats.md
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import re


def count_pnotes(workspace: str) -> dict:
    """统计 P-Note 数量"""
    medium_path = Path(workspace) / ".." / ".." / "obsidian" / "Vault" / "Medium"
    if not medium_path.exists():
        medium_path = Path(workspace) / "Medium"

    pnotes = list(medium_path.glob("P-*.md")) if medium_path.exists() else []

    # 按年份统计
    by_year = defaultdict(int)
    for p in pnotes:
        match = re.search(r"P-(\d{4})", p.name)
        if match:
            by_year[match.group(1)] += 1

    # 按标签统计 (需要读取文件)
    by_tag = defaultdict(int)
    for p in pnotes[:10]:  # 限制读取数量
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
            tags_match = re.search(r"tags:\s*\[(.*?)\]", content)
            if tags_match:
                tags = [t.strip() for t in tags_match.group(1).split(",")]
                for tag in tags:
                    by_tag[tag] += 1
        except Exception:
            pass

    return {
        "total": len(pnotes),
        "by_year": dict(by_year),
        "by_tag": dict(sorted(by_tag.items(), key=lambda x: x[1], reverse=True)[:10])
    }


def count_cnotes(workspace: str) -> dict:
    """统计 C-Note 数量"""
    foundations_path = Path(workspace) / ".." / ".." / "obsidian" / "Vault" / "AI-Research" / "01-Foundations"
    if not foundations_path.exists():
        foundations_path = Path(workspace) / "AI-Research" / "01-Foundations"

    cnotes = list(foundations_path.glob("C-*.md")) if foundations_path.exists() else []

    return {
        "total": len(cnotes),
        "files": [c.name for c in cnotes[:10]]
    }


def count_mnotes(workspace: str) -> dict:
    """统计 M-Note 数量"""
    radar_path = Path(workspace) / ".." / ".." / "obsidian" / "Vault" / "AI-Research" / "00-Radar"
    if not radar_path.exists():
        radar_path = Path(workspace) / "AI-Research" / "00-Radar"

    mnotes = list(radar_path.glob("M-*.md")) if radar_path.exists() else []

    return {
        "total": len(mnotes),
        "files": [m.name for m in mnotes[:10]]
    }


def count_knowledge_graph(workspace: str) -> dict:
    """统计知识图谱"""
    kg_path = Path(workspace) / "knowledge-graph"

    stats = {
        "exists": kg_path.exists(),
        "files": [],
        "entities": 0,
        "relations": 0
    }

    if kg_path.exists():
        stats["files"] = [f.name for f in kg_path.glob("*")]

        # 读取 JSON 统计
        json_path = kg_path / "graph.json"
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                stats["entities"] = len(data.get("entities", []))
                stats["relations"] = len(data.get("relations", []))
                stats["entity_types"] = data.get("stats", {}).get("entity_types", {})
            except Exception:
                pass

    return stats


def count_memory_files(workspace: str) -> dict:
    """统计记忆文件"""
    memory_path = Path(workspace) / "memory"

    if not memory_path.exists():
        return {"total": 0, "recent": []}

    files = list(memory_path.glob("*.md"))

    # 最近 7 天
    recent = []
    seven_days_ago = datetime.now() - timedelta(days=7)
    for f in files:
        if datetime.fromtimestamp(f.stat().st_mtime) > seven_days_ago:
            recent.append(f.name)

    return {
        "total": len(files),
        "recent_7days": len(recent),
        "recent_files": recent[:10]
    }


def generate_markdown_report(stats: dict, output_path: str):
    """生成 Markdown 报告"""
    report = f"""# 📊 研究系统统计看板

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📄 论文笔记 (P-Note)

| 指标 | 数值 |
|------|------|
| 总数 | {stats['pnotes']['total']} |

### 按年份分布

"""

    for year, count in sorted(stats['pnotes']['by_year'].items(), reverse=True):
        report += f"- **{year}**: {count} 篇\n"

    report += f"""
### 热门标签

"""
    for tag, count in stats['pnotes']['by_tag'].items():
        report += f"- `{tag}`: {count} 篇\n"

    report += f"""
---

## 🧠 概念笔记 (C-Note)

| 指标 | 数值 |
|------|------|
| 总数 | {stats['cnotes']['total']} |

---

## 📊 对比笔记 (M-Note)

| 指标 | 数值 |
|------|------|
| 总数 | {stats['mnotes']['total']} |

---

## 🕸️ 知识图谱

| 指标 | 数值 |
|------|------|
| 状态 | {'✅ 已构建' if stats['knowledge_graph']['exists'] else '❌ 未构建'} |
| 实体数 | {stats['knowledge_graph']['entities']} |
| 关系数 | {stats['knowledge_graph']['relations']} |

### 实体类型分布

"""

    for etype, count in stats['knowledge_graph'].get('entity_types', {}).items():
        report += f"- **{etype}**: {count}\n"

    report += f"""
### 输出文件

"""
    for f in stats['knowledge_graph']['files']:
        report += f"- `{f}`\n"

    report += f"""
---

## 📝 记忆文件

| 指标 | 数值 |
|------|------|
| 总数 | {stats['memory']['total']} |
| 最近 7 天 | {stats['memory']['recent_7days']} |

---

## 📈 系统健康度

| 组件 | 状态 |
|------|------|
| P-Note 收集 | {'✅' if stats['pnotes']['total'] > 0 else '⚠️'} |
| C-Note 管理 | {'✅' if stats['cnotes']['total'] > 0 else '⚠️'} |
| M-Note 触发 | {'✅' if stats['mnotes']['total'] > 0 else '⚠️'} |
| 知识图谱 | {'✅' if stats['knowledge_graph']['exists'] else '⚠️'} |
| 记忆系统 | {'✅' if stats['memory']['total'] > 0 else '⚠️'} |

---

*报告由 research-stats.py 自动生成*
"""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ 已生成统计报告：{output}")


def main():
    parser = argparse.ArgumentParser(description="研究统计看板")
    parser.add_argument("--workspace", type=str, default="D:\\OpenClaw\\workspace",
                        help="工作空间路径")
    parser.add_argument("--output", type=str, default="reports\\research-stats.md",
                        help="输出报告路径")
    args = parser.parse_args()

    print(f"\n=== Research Statistics Dashboard ===")
    print(f"工作空间：{args.workspace}\n")

    # 收集统计
    stats = {
        "pnotes": count_pnotes(args.workspace),
        "cnotes": count_cnotes(args.workspace),
        "mnotes": count_mnotes(args.workspace),
        "knowledge_graph": count_knowledge_graph(args.workspace),
        "memory": count_memory_files(args.workspace)
    }

    # 打印摘要
    print(f"📊 统计摘要:")
    print(f"  P-Note: {stats['pnotes']['total']} 篇")
    print(f"  C-Note: {stats['cnotes']['total']} 篇")
    print(f"  M-Note: {stats['mnotes']['total']} 篇")
    print(f"  知识图谱：{stats['knowledge_graph']['entities']} 实体，{stats['knowledge_graph']['relations']} 关系")
    print(f"  记忆文件：{stats['memory']['total']} 篇 (最近 7 天：{stats['memory']['recent_7days']})")

    # 生成报告
    generate_markdown_report(stats, args.output)


if __name__ == "__main__":
    main()
