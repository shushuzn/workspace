#!/usr/bin/env python3
"""
高级技能集成脚本 - citation-tracker + batch-processor + pdf-extractor
"""

import json
from datetime import datetime
from pathlib import Path


def update_cron_tasks(workspace: str):
    """更新定时任务配置"""
    workspace_path = Path(workspace)
    cron_file = workspace_path / ".openclaw" / "cron-tasks.json"

    if cron_file.exists():
        with open(cron_file, "r", encoding="utf-8") as f:
            cron_config = json.load(f)
    else:
        cron_config = {"tasks": []}

    new_tasks = [
        {
            "name": "citation-tracker",
            "description": "每周引用关系追踪",
            "schedule": "0 4 * * 1",
            "command": f"py {workspace_path}\\skills\\citation-tracker\\scripts\\citation-tracker.py --input {workspace_path}\\Medium --output {workspace_path}\\knowledge-graph\\citations",
            "enabled": True
        },
        {
            "name": "batch-processor",
            "description": "批量论文解析",
            "schedule": "30 2 * * *",
            "command": f"py {workspace_path}\\skills\\batch-processor\\scripts\\batch-processor.py --config {workspace_path}\\Arxiv\\batch-config.yaml",
            "enabled": True
        },
        {
            "name": "pdf-extractor",
            "description": "PDF 批量解析",
            "schedule": "0 5 * * *",
            "command": f"py {workspace_path}\\skills\\pdf-extractor\\scripts\\pdf-extractor.py --config {workspace_path}\\Arxiv\\pdf-extractor-config.yaml",
            "enabled": True
        }
    ]

    existing_names = {t["name"] for t in cron_config["tasks"]}
    for task in new_tasks:
        if task["name"] not in existing_names:
            cron_config["tasks"].append(task)

    with open(cron_file, "w", encoding="utf-8") as f:
        json.dump(cron_config, f, indent=2, ensure_ascii=False)

    print(f"✅ 已更新定时任务：{cron_file}")


if __name__ == "__main__":
    workspace = "D:\\OpenClaw\\workspace"
    print(f"\n=== 高级技能集成 ===\n")
    update_cron_tasks(workspace)
    print(f"\n✅ 集成完成！查看报告：reports\\ADVANCED-SKILLS-INTEGRATION.md")
