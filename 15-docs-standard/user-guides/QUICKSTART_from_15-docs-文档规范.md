# AI Research OS - 快速开始指南

**版本:** v1.0  
**创建时间:** 2026-03-05 12:38  
**适用:** 新用户快速上手

---

## 🚀 5 分钟快速开始

### 步骤 1: 查看系统状态 (1 分钟)

```powershell
# 查看今日收集的论文
Get-ChildItem "D:\obsidian\Vault\Arxiv\daily\2026\03\2026-03-05" -Recurse -Filter "*.md" | Measure-Object

# 查看系统监控报告
Get-ChildItem "D:\obsidian\Vault\AI-Research\System-Monitor" -Filter "*.md" | Select-Object -Last 1 | Code
```

### 步骤 2: 运行一次收集 (2 分钟)

```powershell
cd D:\OpenClaw\workspace\scripts

# 收集 arXiv 论文
py arxiv-collector-v2.py

# 查看收集结果
Get-ChildItem "D:\obsidian\Vault\Arxiv\daily\2026\03\2026-03-05" -Recurse -Filter "*.md" | Measure-Object
```

### 步骤 3: 查看知识观点 (1 分钟)

```powershell
# 查看 MEMORY.md
Code "D:\OpenClaw\workspace\MEMORY.md"

# 查看今日报告
Code "D:\obsidian\Vault\AI-Research\Auto-Reports\daily-report-2026-03-05.md"
```

### 步骤 4: 系统检查 (1 分钟)

```powershell
# 运行系统监控
py task-monitor.py

# 运行数据质量检查
py data-quality-checker.py
```

---

## 📚 常用命令

### 信息收集
```powershell
py arxiv-collector-v2.py      # arXiv 论文
py twitter-watcher.py          # Twitter 监听
py hn-watcher.py               # HackerNews
py reddit-watcher-mock.py      # Reddit (模拟)
```

### 数据处理
```powershell
py pdf-downloader.py           # PDF 下载
py pnote-auto-fill.py          # P-Note 填充
```

### AI 分析
```powershell
py paper-quality-scorer.py     # 论文评分
py tech-trend-predictor.py     # 趋势预测
py collaboration-recommender.py # 合作者推荐
```

### 系统工具
```powershell
py task-monitor.py             # 任务监控
py data-quality-checker.py     # 质量检查
py performance-optimizer.py    # 性能优化
py auto-report-generator.py    # 报告生成
```

---

## 📖 更多文档

- [[USAGE-GUIDE.md]] - 完整使用文档
- [[FAQ.md]] - 常见问题解答
- [[FINAL-SUMMARY.md]] - 全阶段总结

---

## 🆘 获取帮助

```powershell
# 查看脚本帮助
py arxiv-collector-v2.py --help

# 查看 FAQ
Code "D:\OpenClaw\workspace\docs\FAQ.md"
```

---

*最后更新：2026-03-05 12:38*
