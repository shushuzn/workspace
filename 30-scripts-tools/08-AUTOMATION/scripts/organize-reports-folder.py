#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
21-reports 文件夹整理脚本
目标：根目录只保留 README.md，其他文件全部移入子文件夹
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

REPORTS_DIR = Path("D:/OpenClaw/workspace/21-reports")

def categorize_file(filename):
    """根据文件名分类"""
    name = filename.lower()

    # LIG 相关
    if 'lig' in name:
        if 'domain' in name or 'industry' in name or 'citation' in name:
            return 'lig-domain'
        elif 'author' in name or 'network' in name:
            return 'lig-authors'
        elif 'opportunity' in name:
            return 'lig-opportunities'
        elif 'risk' in name:
            return 'lig-risk'
        else:
            return 'lig-general'

    # 技能相关
    if 'skill' in name:
        return 'skills'

    # 自动化/任务相关
    if 'auto' in name or 'task' in name or 'batch' in name:
        return 'automation'

    # 学习资源
    if 'learning' in name or 'resource' in name:
        return 'learning-resources'

    # 文档/报告
    if name.startswith('doc_') or name.startswith('rep_'):
        return 'general-reports'

    # 默认
    return 'misc'

def main():
    print("📁 整理 21-reports 文件夹")
    print(f"📂 目录：{REPORTS_DIR}")
    print("-" * 60)

    # 创建子文件夹
    subdirs = {
        'lig-domain': 'LIG 领域数据',
        'lig-authors': 'LIG 作者分析',
        'lig-opportunities': 'LIG 机会分析',
        'lig-risk': 'LIG 风险预警',
        'lig-general': 'LIG 综合报告',
        'skills': '技能相关',
        'automation': '自动化任务',
        'learning-resources': '学习资源',
        'general-reports': '综合报告',
        'misc': '其他',
    }

    for subdir in subdirs.keys():
        (REPORTS_DIR / subdir).mkdir(exist_ok=True)

    # 移动文件
    moved_count = 0
    skipped = 0

    # 获取根目录所有文件
    files = [f for f in REPORTS_DIR.iterdir() if f.is_file()]

    for filepath in files:
        # 跳过 README 和 .gitignore
        if filepath.name.lower() in ['readme.md', '.gitignore']:
            print(f"⏭️  跳过：{filepath.name}")
            skipped += 1
            continue

        # 分类
        category = categorize_file(filepath.name)
        target_dir = REPORTS_DIR / category

        # 移动
        target_path = target_dir / filepath.name
        try:
            shutil.move(str(filepath), str(target_path))
            print(f"✅ {filepath.name} → {category}/")
            moved_count += 1
        except Exception as e:
            print(f"❌ 失败：{filepath.name} - {e}")

    print("-" * 60)
    print(f"✅ 移动：{moved_count} 个文件")
    print(f"⏭️  跳过：{skipped} 个文件")

    # 生成整理报告
    report_path = REPORTS_DIR / "organization-report.md"
    report = f"""# 21-reports 文件夹整理报告

**日期:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**整理前:** 根目录 {moved_count + skipped} 个文件  
**整理后:** 根目录 {skipped} 个文件 (README.md + .gitignore)

---

## 文件夹结构

```
21-reports/
├── README.md
├── lig-domain/          # LIG 领域数据 ({len(list((REPORTS_DIR / 'lig-domain').glob('*')))} 个文件)
├── lig-authors/         # LIG 作者分析 ({len(list((REPORTS_DIR / 'lig-authors').glob('*')))} 个文件)
├── lig-opportunities/   # LIG 机会分析 ({len(list((REPORTS_DIR / 'lig-opportunities').glob('*')))} 个文件)
├── lig-risk/            # LIG 风险预警 ({len(list((REPORTS_DIR / 'lig-risk').glob('*')))} 个文件)
├── lig-general/         # LIG 综合报告 ({len(list((REPORTS_DIR / 'lig-general').glob('*')))} 个文件)
├── skills/              # 技能相关
├── automation/          # 自动化任务
├── learning-resources/  # 学习资源
├── general-reports/     # 综合报告
└── misc/                # 其他
```

---

## 分类规则

| 关键词 | 目标文件夹 |
|--------|-----------|
| lig + domain/industry/citation | lig-domain/ |
| lig + author/network | lig-authors/ |
| lig + opportunity | lig-opportunities/ |
| lig + risk | lig-risk/ |
| lig (其他) | lig-general/ |
| skill | skills/ |
| auto/task/batch | automation/ |
| learning/resource | learning-resources/ |
| DOC_/REP_ 前缀 | general-reports/ |
| 其他 | misc/ |

---

**整理脚本:** `30-scripts/organize-reports-folder.py`
"""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n📄 报告：{report_path}")
    print("\n✅ 整理完成！")

if __name__ == "__main__":
    main()
