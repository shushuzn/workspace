#!/usr/bin/env python3
"""
技能集成脚本 - arxiv-daily + medium-watcher + memory-distiller

功能:
- 配置 arxiv-daily 每日论文收集
- 配置 medium-watcher 文章监听
- 配置 memory-distiller 知识蒸馏
- 创建定时任务

使用:
    python integrate-collectors.py --workspace D:\OpenClaw\workspace
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
import yaml


def check_dependencies():
    """检查依赖"""
    missing = []
    
    try:
        import feedparser
    except ImportError:
        missing.append("feedparser")
    
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    try:
        import bs4
    except ImportError:
        missing.append("beautifulsoup4")
    
    try:
        import yaml
    except ImportError:
        missing.append("pyyaml")
    
    if missing:
        print(f"⚠️ 缺少依赖：{', '.join(missing)}")
        print(f"安装命令：py -m pip install {' '.join(missing)}")
        return False
    
    return True


def create_cron_tasks(workspace: str):
    """创建定时任务配置"""
    workspace_path = Path(workspace)
    
    cron_config = {
        "tasks": [
            {
                "name": "arxiv-daily",
                "description": "每日 arXiv 论文收集",
                "schedule": "0 2 * * *",  # 每天 2am
                "command": f"py {workspace_path}\\Arxiv\\arxiv-daily.py --config {workspace_path}\\Arxiv\\config.yaml",
                "enabled": True
            },
            {
                "name": "medium-watcher",
                "description": "每日 Medium 文章收集",
                "schedule": "0 8 * * *",  # 每天 8am
                "command": f"py {workspace_path}\\Medium\\medium-watcher.py --config {workspace_path}\\Medium\\config.yaml",
                "enabled": True
            },
            {
                "name": "memory-distiller",
                "description": "每周知识蒸馏",
                "schedule": "0 23 * * 0",  # 每周日 11pm
                "command": f"py {workspace_path}\\memory\\distiller.py --config {workspace_path}\\memory\\distiller-config.yaml",
                "enabled": True
            }
        ]
    }
    
    output_path = workspace_path / ".openclaw" / "cron-tasks.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cron_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 已创建定时任务配置：{output_path}")
    return output_path


def create_integration_guide(workspace: str):
    """创建集成指南"""
    workspace_path = Path(workspace)
    
    guide = f"""# 🔗 技能集成指南

**集成日期:** {datetime.now().strftime('%Y-%m-%d')}  
**工作空间:** {workspace}

---

## ✅ 已集成技能

### 1. arxiv-daily (每日论文收集)

**配置:** `{workspace_path}\\Arxiv\\config.yaml`  
**输出:** `{workspace_path}\\Arxiv\\collected\\`  
**定时:** 每天 2:00 AM

**手动执行:**
```bash
py {workspace_path}\\Arxiv\\arxiv-daily.py --categories cs.AI,cs.LG --output {workspace_path}\\Arxiv\\collected\\
```

**功能:**
- ✅ 多类别监听 (cs.AI, cs.LG, cs.CL, etc.)
- ✅ 优先级评分 (1-5 分)
- ✅ 去重处理 (基于 arXiv ID)
- ✅ JSON/Markdown 输出

---

### 2. medium-watcher (文章监听)

**配置:** `{workspace_path}\\Medium\\config.yaml`  
**输出:** `{workspace_path}\\Medium\\Raw\\`  
**定时:** 每天 8:00 AM

**手动执行:**
```bash
py {workspace_path}\\Medium\\medium-watcher.py --tags ai,llm --output {workspace_path}\\Medium\\Raw\\
```

**功能:**
- ✅ 按标签/作者/出版物订阅
- ✅ 内容提取 (正文/图片/代码)
- ✅ 质量评分 (阅读数/点赞/评论)
- ✅ 自动归档 (30 天)

---

### 3. memory-distiller (知识蒸馏)

**配置:** `{workspace_path}\\memory\\distiller-config.yaml`  
**输出:** `{workspace_path}\\MEMORY.md`  
**定时:** 每周日 11:00 PM

**手动执行:**
```bash
py {workspace_path}\\memory\\distiller.py --input {workspace_path}\\memory\\ --output {workspace_path}\\MEMORY.md
```

**功能:**
- ✅ 观点提取 (从每日笔记)
- ✅ 去重合并 (语义相似度)
- ✅ 置信度评估 (高/中/低)
- ✅ 增量更新 MEMORY.md

---

## 🔄 工作流集成

```
arxiv-daily (2am)
    ↓
Arxiv/collected/*.json
    ↓
ai-research-os (深度解析)
    ↓
P-Note/C-Note/M-Note

medium-watcher (8am)
    ↓
Medium/Raw/*.md
    ↓
筛选高质内容
    ↓
深度分析/归档

memory/*.md (每日笔记)
    ↓
memory-distiller (周日 11pm)
    ↓
MEMORY.md (长期记忆)
```

---

## 📊 依赖安装

```bash
py -m pip install feedparser requests beautifulsoup4 pyyaml
```

---

## ⚙️ 配置说明

### arxiv-daily

编辑 `{workspace_path}\\Arxiv\\config.yaml`:
- `categories`: 添加/删除监听类别
- `keywords.include`: 核心关键词 (加分)
- `keywords.exclude`: 排除关键词 (减分)
- `min_score`: 最低分数阈值 (默认 3.0)

### medium-watcher

编辑 `{workspace_path}\\Medium\\config.yaml`:
- `tags`: 订阅标签
- `authors`: 订阅作者
- `publications`: 订阅出版物
- `min_score`: 最低质量分数 (默认 3.0)

### memory-distiller

编辑 `{workspace_path}\\memory\\distiller-config.yaml`:
- `categories`: 观点分类
- `distillation.min_confidence`: 最小置信度
- `schedule.frequency`: 执行频率

---

## 🚀 下一步

1. **安装依赖:**
   ```bash
   py -m pip install feedparser requests beautifulsoup4 pyyaml
   ```

2. **测试运行:**
   ```bash
   # 测试 arxiv-daily
   py {workspace_path}\\skills\\arxiv-daily\\scripts\\arxiv-daily.py --categories cs.AI --output {workspace_path}\\Arxiv\\collected\\
   
   # 测试 medium-watcher
   py {workspace_path}\\skills\\medium-watcher\\scripts\\medium-watcher.py --tags ai --output {workspace_path}\\Medium\\Raw\\
   ```

3. **配置定时任务:**
   - OpenClaw 心跳检查已集成
   - 或使用 Windows 定时任务

4. **监控运行:**
   - 查看输出目录
   - 检查日志文件
   - 验证 MEMORY.md 更新

---

## 📝 文件结构

```
{workspace}\\
├── Arxiv/
│   ├── config.yaml              # arxiv-daily 配置
│   ├── papers/                  # 原始 PDF 存储
│   └── collected/               # 收集的论文元数据
│
├── Medium/
│   ├── config.yaml              # medium-watcher 配置
│   ├── Raw/                     # 原始文章
│   └── Archive/                 # 归档 (30 天+)
│
├── memory/
│   ├── distiller-config.yaml    # memory-distiller 配置
│   ├── YYYY-MM-DD.md            # 每日笔记
│   └── MEMORY.md                # 长期记忆
│
└── scripts/
    ├── integrate-collectors.py  # 集成脚本
    └── research-stats.py        # 统计看板
```

---

*集成完成，系统已就绪！* 🎉
"""
    
    output_path = workspace_path / "reports" / "SKILL-INTEGRATION-GUIDE.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(guide)
    
    print(f"✅ 已创建集成指南：{output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="技能集成脚本")
    parser.add_argument("--workspace", type=str, default="D:\\OpenClaw\\workspace",
                        help="工作空间路径")
    args = parser.parse_args()
    
    print(f"\n=== Skill Integration ===")
    print(f"工作空间：{args.workspace}\n")
    
    # 检查依赖
    print("🔍 检查依赖...")
    if check_dependencies():
        print("✅ 依赖检查通过")
    else:
        print("⚠️ 请先安装缺少的依赖")
        return 1
    
    # 创建定时任务配置
    print("\n📅 创建定时任务配置...")
    create_cron_tasks(args.workspace)
    
    # 创建集成指南
    print("\n📖 创建集成指南...")
    create_integration_guide(args.workspace)
    
    print("\n✅ 技能集成完成！")
    print("\n下一步:")
    print("1. 安装依赖：py -m pip install feedparser requests beautifulsoup4 pyyaml")
    print("2. 测试运行：查看集成指南中的测试命令")
    print("3. 配置定时任务：OpenClaw 心跳检查已集成")
    
    return 0


if __name__ == "__main__":
    exit(main())
