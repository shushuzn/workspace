# Arxiv-Collector + Paper2MD 整合方案

**创建日期:** 2026-03-03  
**状态:** ✅ 测试完成 (2026-03-03 15:15)

**测试结果:**
- 测试论文：2602.23720 (Auton Framework)
- PDF 大小：0.39 MB
- 解析页数：19 页
- 输出 Markdown: 64,809 字符
- 输出路径：D:\obsidian\Vault\arxiv\deep\2602.23720-full.md
- 工具：PyMuDF (fitz) + 自定义脚本  

---

## 目标

将 `arxiv-collector-v2`（批量收集）与 `paper2md`（深度解析）整合，形成完整的论文处理流水线：

```
arXiv RSS → 批量收集 → 初步筛选 → 重点论文 → 深度解析 → 知识库
     ↓           ↓           ↓          ↓          ↓
  每日 100 篇   分类存储    人工/AI 筛选  10-20 篇   完整笔记
```

---

## 工具对比

| 维度 | Arxiv-Collector v2 | Paper2MD |
|------|-------------------|----------|
| **输入** | arXiv RSS Feed | 本地 PDF 文件 |
| **输出** | 基础 MD 笔记（标题/作者/摘要/链接） | 结构化 MD + JSON（页码/图表/表格/公式） |
| **处理速度** | ~100 篇/分钟 | ~1-2 篇/分钟 |
| **信息密度** | 低（元数据级别） | 高（全文解析级别） |
| **用途** | 每日追踪、初步筛选 | 深度阅读、知识沉淀 |

---

## 整合架构

### 方案 A: 两阶段流水线（推荐）

```
阶段 1: 批量收集 (每日 2am)
┌─────────────────────────────────────┐
│ arxiv-collector-v2.py               │
│  - 抓取 10 个领域 RSS                  │
│  - 保存基础 MD 笔记 (元数据)           │
│  - 生成当日汇总 (summary.md)         │
│  - 更新状态日志 (logs/status.md)    │
└─────────────────────────────────────┘
                  ↓
        arxiv/daily/YYYY/MM/DD/
        ├── csAI/ (13 篇基础笔记)
        ├── csLG/ (22 篇基础笔记)
        └── ...

阶段 2: 深度解析 (手动/定期)
┌─────────────────────────────────────┐
│ 1. 筛选重点论文                      │
│    - 人工浏览 summary.md            │
│    - 或 AI 自动评分 (相关性/新颖性)    │
│                                     │
│ 2. 下载 PDF                         │
│    - 批量下载脚本                    │
│    - 或手动下载                      │
│                                     │
│ 3. Paper2MD 解析                    │
│    - 提取全文结构                    │
│    - 解析图表/表格/公式              │
│    - 生成深度笔记 + JSON 索引          │
│                                     │
│ 4. 归档到知识库                      │
│    - 移动/链接到 topics/ 目录         │
│    - 更新知识图谱                    │
└─────────────────────────────────────┘
```

### 方案 B: 实时整合（复杂，不推荐）

```
arxiv-collector-v2 → 自动筛选 → 自动下载 PDF → Paper2MD → 深度笔记
                         ↓
                   置信度>阈值？
```

**问题:**
- PDF 下载不稳定（arXiv 反爬虫）
- Paper2MD 处理速度慢（1-2 篇/分钟）
- 误判风险高（可能解析低价值论文）

---

## 实施方案 A

### 步骤 1: 创建筛选脚本

```python
# arxiv-priority-scorer.py
# 对当日收集的论文进行优先级评分

import json
import re
from pathlib import Path

# 关键词权重（根据研究方向调整）
KEYWORDS = {
    'agent': 3, 'agentic': 3, 'autonomous': 2,
    'MCP': 3, 'tool': 2, 'function calling': 2,
    'reasoning': 3, 'planning': 2, 'reflection': 2,
    'efficient': 2, 'adaptive': 2, 'routing': 2,
    'causal': 2, 'interpretability': 2,
}

def score_paper(title, abstract):
    text = (title + ' ' + abstract).lower()
    score = 0
    matched = []
    
    for keyword, weight in KEYWORDS.items():
        if keyword in text:
            score += weight
            matched.append(keyword)
    
    return score, matched

def main():
    # 读取当日汇总
    today = datetime.now().strftime('%Y-%m-%d')
    summary_path = f"arxiv/daily/{today[:4]}/{today[5:7]}/{today}-summary.md"
    
    # 解析论文列表，计算评分
    # 输出 priority-YYYY-MM-DD.md
    pass
```

### 步骤 2: 创建 PDF 批量下载脚本

```powershell
# arxiv-download-pdfs.ps1
# 从优先级列表批量下载 PDF

param(
    [string]$PriorityList = "priority-2026-03-03.md",
    [string]$OutputDir = "D:\obsidian\Vault\arxiv\pdfs\2026-03-03"
)

# 解析优先级列表中的 arXiv ID
# 批量下载 PDF 到指定目录
# 生成下载日志
```

### 步骤 3: 创建 Paper2MD 批量处理脚本

```python
# paper2md-batch.py
# 批量调用 paper2md 解析 PDF

import subprocess
from pathlib import Path

PDF_DIR = Path("D:/obsidian/Vault/arxiv/pdfs/2026-03-03")
OUTPUT_DIR = Path("D:/obsidian/Vault/arxiv/deep/2026-03-03")

for pdf in PDF_DIR.glob("*.pdf"):
    # 调用 paper2md
    subprocess.run([
        "python", "paper2md.py",
        "--input", str(pdf),
        "--output", str(OUTPUT_DIR)
    ])
```

### 步骤 4: 创建整合工作流脚本

```powershell
# arxiv-workflow.ps1
# 一键执行完整工作流

param(
    [ValidateSet("collect", "score", "download", "parse", "all")]
    [string]$Mode = "all",
    [string]$Date = (Get-Date -Format "yyyy-MM-dd")
)

switch ($Mode) {
    "collect" { python arxiv-collector-v2.py }
    "score" { python arxiv-priority-scorer.py -Date $Date }
    "download" { .\arxiv-download-pdfs.ps1 -Date $Date }
    "parse" { python paper2md-batch.py -Date $Date }
    "all" {
        Write-Host "[1/4] 收集论文..."
        python arxiv-collector-v2.py
        
        Write-Host "[2/4] 评分筛选..."
        python arxiv-priority-scorer.py -Date $Date
        
        Write-Host "[3/4] 下载 PDF (需人工确认)..."
        .\arxiv-download-pdfs.ps1 -Date $Date
        
        Write-Host "[4/4] 深度解析 (手动触发)..."
        Write-Host "  运行：python paper2md-batch.py -Date $Date"
    }
}
```

---

## 目录结构（整合后）

```
arxiv/
├── daily/                      # 每日收集（基础笔记）
│   └── YYYY/MM/DD/
│       ├── csAI/ csLG/ ...    # 按领域分类
│       ├── logs/              # 状态日志
│       ├── YYYY-MM-DD-summary.md
│       └── priority-YYYY-MM-DD.md  # 优先级评分
│
├── pdfs/                       # PDF 临时存储
│   └── YYYY-MM-DD/
│       ├── 2401.12345.pdf
│       └── ...
│
├── deep/                       # 深度解析笔记
│   └── YYYY-MM-DD/
│       ├── 2401.12345-full.md  # 完整解析
│       ├── 2401.12345.json     # 结构化数据
│       └── ...
│
└── archive/                    # 归档（月度汇总）
    └── YYYY-MM/
```

---

## 使用流程

### 日常流程（每日 5 分钟）

```powershell
# 1. 自动收集（定时任务，2am）
#    无需手动操作

# 2. 早晨查看汇总
cd D:\obsidian\Vault\arxiv\daily\2026\03\
code 2026-03-03-summary.md

# 3. 标记重点论文
#    在 summary.md 中标记 ⭐ 或移动到 priority 列表

# 4. 下载 + 解析（每周 1-2 次）
.\arxiv-workflow.ps1 -Mode download -Date 2026-03-03
python paper2md-batch.py -Date 2026-03-03
```

### 周流程（每周 30 分钟）

```powershell
# 1. 回顾本周收集
Get-ChildItem arxiv\daily\2026\03\*-summary.md

# 2. 批量下载重点论文 PDF
.\arxiv-download-pdfs.ps1 -Week 10

# 3. 批量解析
python paper2md-batch.py -Week 10

# 4. 归档到知识库
#    手动移动到 topics/ 目录并添加链接
```

---

## 待开发脚本清单

| 脚本 | 状态 | 优先级 |
|------|------|--------|
| arxiv-tasksched-config.ps1 | ✅ 已完成 | ⭐⭐⭐ |
| arxiv-priority-scorer.py | ⬜ 待开发 | ⭐⭐⭐ |
| arxiv-download-pdfs.ps1 | ⬜ 待开发 | ⭐⭐ |
| paper2md-batch.py | ⬜ 待开发 | ⭐⭐ |
| arxiv-workflow.ps1 | ⬜ 待开发 | ⭐⭐⭐ |

---

## 下一步

1. **部署定时任务**
   ```powershell
   cd C:\Users\华为\.openclaw\workspace
   .\arxiv-tasksched-config.ps1
   ```

2. **开发优先级评分器** (arxiv-priority-scorer.py)
   - 基于关键词匹配
   - 支持自定义权重
   - 输出优先级列表

3. **测试完整流程**
   - 手动运行收集 → 评分 → 下载 → 解析
   - 验证输出质量
   - 调整参数

---

*整合目标：自动化收集 + 人工筛选 + 深度解析*
