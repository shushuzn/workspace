# 05 - 报告生成工作流 (Level 5)

**版本:** v4.0  
**创建时间:** 2026-03-05 16:40  
**更新时间:** 2026-03-05 17:15  
**自动化:** 每日 04:00 自动运行 (Level 4 完成后)  
**层次:** Level 5/5 - 报告生成

---

## 📋 工作流说明

### 功能
- 自动生成研究报告
- 填充趋势分析数据
- 提供研究建议
- 输出 Markdown 格式报告

### 输入
- 趋势分析数据
- 报告模板

### 输出
- 自动研究报告
- 保存位置：`reports/AUTO-RESEARCH-REPORT-YYYY-MM-DD.md`

---

## 🚀 使用方法

### 单次运行

```bash
cd D:\OpenClaw\workspace
py scripts/materials/generate-report.py
```

---

## 📁 文件结构

```
workflows/report-gen/
├── README.md              # 本文件
├── templates/             # 报告模板
│   └── daily-report.md
├── run.sh                 # 运行脚本
├── logs/                  # 日志目录
│   └── report.log
└── outputs/               # 输出目录 (符号链接)
    └── -> D:/OpenClaw/workspace/reports/
```

---

## 📊 报告模板

### daily-report.md

```markdown
# 自动化材料研究报告

**生成时间:** {timestamp}
**分析论文数:** {paper_count}

---

## 📊 研究热点

### 热门主题

{hot_topics}

### 新兴领域

{emerging_fields}

---

## 🔬 推荐研究方向

基于当前趋势，建议关注以下方向：

{recommendations}

---

*报告由 AI Research OS 自动生成*
*系统版本：v2.0*
```

---

## ⚙️ 配置选项

### config.yaml

```yaml
# 报告生成配置
report:
  # 模板文件
  template: templates/daily-report.md
  
  # 输出目录
  output_dir: outputs/
  
  # 自动命名
  auto_naming: true
  naming_pattern: "AUTO-REPORT-{date}.md"
  
  # 包含内容
  include:
    - hot_topics
    - emerging_fields
    - recommendations
```

---

*最后更新：2026-03-05 16:40*  
*工作流版本：v2.0*
