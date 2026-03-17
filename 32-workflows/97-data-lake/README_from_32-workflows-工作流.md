# 数据湖工作流

**版本:** v1.0  
**创建时间:** 2026-03-05 17:40  
**自动化:** 每日 06:00 自动运行  
**层次:** 支撑系统

---

## 📋 工作流说明

### 功能
- 统一数据存储
- 分层数据管理 (Raw/Processed/Curated/Analytics)
- 数据血缘追踪
- 分析数据生成

### 数据湖分层

| 层级 | 用途 | 数据来源 |
|------|------|----------|
| Raw | 原始数据 | Level 1 |
| Processed | 处理数据 | Level 2-4 |
| Curated | 精选数据 | Level 5-6 |
| Analytics | 分析数据 | 自动生成 |

---

## 📁 目录结构

```
data-lake/
├── raw/                    # 原始数据
│   ├── 2026-03-05/
│   │   └── papers.json
│   └── ...
├── processed/              # 处理数据
│   ├── 2026-03-05/
│   │   ├── classified.json
│   │   ├── trends.json
│   │   └── clusters.json
│   └── ...
├── curated/                # 精选数据
│   ├── 2026-03-05/
│   │   ├── report.md
│   │   └── knowledge-graph.json
│   └── ...
└── analytics/              # 分析数据
    └── summary.json
```

---

## 🚀 使用方法

### 单次运行

```bash
cd D:\OpenClaw\workspace
python scripts/data-lake/data-lake-manager.py
```

### 定时任务 (Windows)

```powershell
# 创建每日 06:00 运行的定时任务
$action = New-ScheduledTaskAction -Execute "py" `
  -Argument "D:\OpenClaw\workspace\scripts\data-lake\data-lake-manager.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 6am
Register-ScheduledTask -TaskName "Data-Lake-Management" `
  -Action $action -Trigger $trigger
```

---

## 📊 数据血缘

### 血缘追踪
```
Level 1 (raw/papers.json)
    ↓
Level 2 (processed/classified.json)
    ↓
Level 3 (processed/trends.json)
    ↓
Level 4 (processed/clusters.json)
    ↓
Level 5 (curated/report.md)
    ↓
Level 6 (curated/knowledge-graph.json)
    ↓
Analytics (analytics/summary.json)
```

---

## 📈 分析指标

### summary.json
```json
{
  "generated_at": "2026-03-05T06:00:00",
  "total_dates": 30,
  "total_papers": 3810,
  "by_date": [
    {"date": "2026-03-05", "papers": 127},
    {"date": "2026-03-04", "papers": 125},
    ...
  ]
}
```

---

*最后更新：2026-03-05 17:40*
