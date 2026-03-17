#!/usr/bin/env python3
"""
Workspace 文件整合脚本
整合 D:\OpenClaw\workspace 下所有重要文件

执行流程:
1. 扫描 workspace 目录
2. 分类重要文件
3. 创建归档目录
4. 复制文件
5. 生成总索引

作者：AI Research OS
创建时间：2026-03-06 12:43
"""

import shutil
from pathlib import Path
from datetime import datetime

print("=" * 70)
print("Workspace 文件整合")
print("=" * 70)
print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Workspace 根目录
workspace_dir = Path("D:/OpenClaw/workspace")
archive_dir = workspace_dir / "WORKSPACE_ARCHIVE"

# ============================================================================
# 任务 1: 扫描目录
# ============================================================================
print("\n[任务 1/5] 扫描 Workspace 目录...")

# 重要目录
important_dirs = [
    "research",
    "memory",
    "docs",
    "scripts",
    "data",
    "models",
    "figures"
]

# 扫描结果
scan_results = {}
for dir_name in important_dirs:
    dir_path = workspace_dir / dir_name
    if dir_path.exists():
        files = list(dir_path.rglob("*"))
        file_count = len([f for f in files if f.is_file()])
        scan_results[dir_name] = file_count
        print(f"  - {dir_name}/: {file_count} 个文件")

print(f"\n总计：{sum(scan_results.values())} 个文件")

# ============================================================================
# 任务 2: 创建归档目录
# ============================================================================
print("\n[任务 2/5] 创建归档目录...")

archive_dir.mkdir(exist_ok=True)

# 创建分类目录
categories = {
    "01_Research": ["research"],
    "02_Memory": ["memory"],
    "03_Docs": ["docs"],
    "04_Scripts": ["scripts"],
    "05_Data": ["data"],
    "06_Models": ["models"],
    "07_Figures": ["figures"]
}

for category, sources in categories.items():
    (archive_dir / category).mkdir(exist_ok=True)

print(f"  [OK] 归档目录已创建：{archive_dir}")

# ============================================================================
# 任务 3: 复制关键文件
# ============================================================================
print("\n[任务 3/5] 复制关键文件...")

# 文件映射规则
copy_rules = {
    "01_Research": ["research/docs/*.md", "research/data/*.csv", "research/scripts/*.py", "research/models/*.pkl", "research/figures/*.png"],
    "02_Memory": ["memory/*.md"],
    "03_Docs": ["docs/*.md"],
    "04_Scripts": ["scripts/**/*.py"],
    "05_Data": ["data/*.csv", "data/*.json"],
    "06_Models": ["models/*.pkl", "models/*.json"],
    "07_Figures": ["figures/*.png"]
}

copied_count = 0
for category, patterns in copy_rules.items():
    target_dir = archive_dir / category
    for pattern in patterns:
        for src_file in workspace_dir.glob(pattern):
            if src_file.is_file():
                # 保持目录结构
                rel_path = src_file.relative_to(workspace_dir)
                dst_file = archive_dir / rel_path
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
                copied_count += 1

print(f"  [OK] 已复制 {copied_count} 个文件")

# ============================================================================
# 任务 4: 生成总索引
# ============================================================================
print("\n[任务 4/5] 生成总索引...")

index_content = f"""# Workspace 文件总索引

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**归档目录:** {archive_dir}
**总文件数:** {copied_count}

## 目录结构

```
WORKSPACE_ARCHIVE/
├── 01_Research/    # 研究项目
├── 02_Memory/      # 记忆文件
├── 03_Docs/        # 文档资料
├── 04_Scripts/     # 脚本文件
├── 05_Data/        # 数据文件
├── 06_Models/      # 模型文件
└── 07_Figures/     # 图表文件
```

## 文件统计

"""

for category, count in scan_results.items():
    index_content += f"- **{category}/:** {count} 个文件\n"

index_content += f"\n**总计:** {sum(scan_results.values())} 个文件\n\n"

index_content += """## 重要文件

### LIG 研究项目

- **论文:** 01_Research/docs/PAPER_DRAFT_V2.md
- **数据:** 01_Research/data/lig_dataset_200.csv
- **代码:** 01_Research/scripts/autonomous_paper_prep_v*.py
- **模型:** 01_Research/models/LIG_GP_online.pkl
- **图表:** 01_Research/figures/GP_*.png

### 记忆文件

- **今日记忆:** 02_Memory/2026-03-06.md
- **任务清单:** 02_Memory/task-list-phase12.md

### 文档资料

- **最终报告:** 03_Docs/FINAL_REPORT.md
- **部署指南:** 03_Docs/DEPLOYMENT.md

### 脚本文件

- **自治脚本:** 04_Scripts/autonomous_paper_prep_v*.py
- **数据处理:** 04_Scripts/data_augmentation.py
- **模型训练:** 04_Scripts/gp_*.py

## GitHub 仓库

所有文件已推送至 GitHub:
https://github.com/shushuzn/obsidian-sync

## 使用说明

1. 查看归档目录：cd WORKSPACE_ARCHIVE
2. 查看总索引：cat FILE_INDEX.md
3. 使用文件：直接访问对应目录

---

*Workspace 文件整合完成！*
"""

index_path = archive_dir / "FILE_INDEX.md"
with open(index_path, 'w', encoding='utf-8') as f:
    f.write(index_content)

print(f"  [OK] 总索引已生成：{index_path}")

# ============================================================================
# 任务 5: 生成 README
# ============================================================================
print("\n[任务 5/5] 生成 README...")

readme_content = f"""# Workspace 归档目录

**归档时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**总文件数:** {copied_count}
**归档位置:** {archive_dir}

## 项目概述

本归档目录包含 D:\\OpenClaw\\workspace 下的所有重要文件，按类别整理。

## 目录结构

- **01_Research:** LIG 材料机器学习研究项目
- **02_Memory:** 记忆文件 (每日记忆、任务清单)
- **03_Docs:** 文档资料 (报告、指南)
- **04_Scripts:** 脚本文件 (Python 脚本)
- **05_Data:** 数据文件 (CSV, JSON)
- **06_Models:** 模型文件 (PKL, JSON)
- **07_Figures:** 图表文件 (PNG)

## 快速开始

### 查看 LIG 研究

```bash
cd 01_Research
cat docs/PAPER_DRAFT_V2.md
```

### 使用数据

```python
import pandas as pd
df = pd.read_csv('05_Data/lig_dataset_200.csv')
```

### 运行脚本

```bash
python 04_Scripts/online_learning.py
```

### 加载模型

```python
import joblib
model = joblib.load('06_Models/LIG_GP_online.pkl')
```

## 文件统计

| 类别 | 文件数 |
|------|--------|
| Research | {scan_results.get('research', 0)} |
| Memory | {scan_results.get('memory', 0)} |
| Docs | {scan_results.get('docs', 0)} |
| Scripts | {scan_results.get('scripts', 0)} |
| Data | {scan_results.get('data', 0)} |
| Models | {scan_results.get('models', 0)} |
| Figures | {scan_results.get('figures', 0)} |
| **总计** | **{sum(scan_results.values())}** |

## GitHub 仓库

所有文件已推送至 GitHub:
https://github.com/shushuzn/obsidian-sync

## 原始位置

所有文件的原始位置:
D:\\OpenClaw\\workspace

---

*Workspace 归档完成！*
"""

readme_path = archive_dir / "README.md"
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(readme_content)

print(f"  [OK] README 已生成：{readme_path}")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 70)
print("Workspace 文件整合完成！")
print("=" * 70)

print(f"\n执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\n归档目录：{archive_dir}")
print(f"\n总文件数：{copied_count} 个")
print(f"\n目录结构:")
for category in categories.keys():
    cat_dir = archive_dir / category
    file_count = len(list(cat_dir.rglob("*")))
    print(f"  - {category}/: {file_count} 个文件")

print(f"\n生成的文件:")
print(f"  - {archive_dir}/README.md")
print(f"  - {archive_dir}/FILE_INDEX.md")

print(f"\n下一步:")
print(f"  1. 查看归档目录：cd {archive_dir}")
print(f"  2. 阅读 README: cat README.md")
print(f"  3. 查看文件索引：cat FILE_INDEX.md")

print("=" * 70)
print("\n[OK] Workspace 文件整合完成！")
print("=" * 70)
