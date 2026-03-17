# 研究文档自动化工作流

**版本:** v1.0  
**创建时间:** 2026-03-05 16:55  
**自动化:** 每周一 09:00 自动运行

---

## 📋 工作流说明

### 功能
- 自动生成周报
- 更新研究进度
- 同步最新 arXiv 论文
- 导入实验数据
- 生成研究统计

### 输入
- 研究文档
- 实验数据
- arXiv 新论文

### 输出
- 周报
- 更新的研究文档
- 研究统计报告

---

## 🚀 使用方法

### 单次运行

```bash
cd D:\OpenClaw\workspace
py scripts/research/research-doc-generator.py
```

### 定时任务

**Windows:**
```powershell
$action = New-ScheduledTaskAction -Execute "py" `
  -Argument "D:\OpenClaw\workspace\scripts\research\research-doc-generator.py"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9am
Register-ScheduledTask -TaskName "Research-Docs-Auto" `
  -Action $action -Trigger $trigger
```

---

## 📁 文件结构

```
workflows/research-docs/
├── README.md              # 本文件
├── config.yaml            # 配置文件
├── run.sh                 # 运行脚本
├── templates/             # 模板目录
│   └── weekly-report.md
├── logs/                  # 日志目录
│   └── research.log
└── outputs/               # 输出目录
    ├── weekly-reports/
    └── stats/
```

---

## ⚙️ 配置选项

### config.yaml

```yaml
# 研究文档自动化配置
research:
  # 研究文件
  main_file: research/SOLID-STATE-BATTERY-RESEARCH.md
  
  # 输出目录
  output_dir: workflows/research-docs/outputs/
  
  # arXiv 同步
  arxiv_sync:
    enabled: true
    keywords:
      - solid-state battery
      - composite electrolyte
      - interface engineering
    max_papers: 10
  
  # 周报配置
  weekly_report:
    enabled: true
    auto_generate: true
    day: Monday
    time: "09:00"
  
  # 实验数据导入
  data_import:
    enabled: true
    source_dir: D:\\lab-data\\
    formats:
      - xrd
      - sem
      - electrochemical
  
  # 日志配置
  logging:
    level: INFO
    file: logs/research.log
    max_size: 10MB
    backup_count: 7
```

---

## 📊 自动化内容

### 1. 周报生成

**自动生成:**
- 本周完成工作
- 遇到的问题
- 下周计划
- 实验数据汇总
- 文献阅读列表

**输出:** `outputs/weekly-reports/week-N-report.md`

### 2. 进度更新

**自动更新:**
- 实验完成状态
- 测试数据填入
- 里程碑状态
- 经费使用统计

### 3. arXiv 同步

**自动同步:**
- 搜索关键词相关论文
- 添加到文献调研部分
- 标记为"新到文献"

### 4. 研究统计

**自动生成:**
- 实验次数统计
- 文献阅读统计
- 进度百分比
- 经费使用率

**输出:** `outputs/stats/research-stats.json`

---

## 📈 运行统计

### research-stats.json

```json
{
  "week": 1,
  "date": "2026-03-05",
  "experiments": {
    "total": 0,
    "completed": 0,
    "pending": 3
  },
  "literature": {
    "total_read": 0,
    "target": 20,
    "progress": 0
  },
  "milestones": {
    "total": 6,
    "completed": 0,
    "progress": 0
  },
  "budget": {
    "total": 32000,
    "used": 0,
    "remaining": 32000,
    "usage_rate": 0
  }
}
```

---

## 🔧 故障排除

### 常见问题

**1. 周报生成失败**

症状：`Weekly report generation failed`

解决：
```bash
# 检查研究文件
ls research/SOLID-STATE-BATTERY-RESEARCH.md

# 手动运行测试
py scripts/research/research-doc-generator.py --test
```

**2. arXiv 同步失败**

症状：`ArXiv sync failed`

解决：
```bash
# 检查网络连接
ping arxiv.org

# 检查关键词配置
cat workflows/research-docs/config.yaml
```

---

## 📞 相关文档

- [自动化系统文档](../../docs/AUTOMATED-RESEARCH-SYSTEM.md)
- [研究文档系统](../../research/README.md)
- [固态电池研究](../../research/SOLID-STATE-BATTERY-RESEARCH.md)

---

*最后更新：2026-03-05 16:55*  
*工作流版本：v1.0*
