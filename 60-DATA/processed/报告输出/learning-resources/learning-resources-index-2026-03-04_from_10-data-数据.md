# 📚 学习资料索引

**更新时间:** 2026-03-04 23:33  
**工作区:** D:\OpenClaw\workspace

---

## 📖 目录结构

```
D:\OpenClaw\workspace/
├── AI-Research/           # AI 研究资料
│   ├── Papers/           # 论文 PDF
│   ├── Notes/            # 研究笔记
│   └── Templates/        # 笔记模板
├── Medium/               # Medium 文章
│   ├── P-Note/          # 论文深度解析
│   ├── M-Note/          # 跨论文对比
│   ├── C-Note/          # 概念主题研究
│   └── Raw/             # 原始收集
├── Arxiv/               # arXiv 元数据
├── memory/              # 每日笔记
├── knowledge-graph/     # 知识图谱
└── reports/             # 报告文档
```

---

## 📊 资料统计

| 类别 | 文件数 | 大小 | 说明 |
|------|--------|------|------|
| **AI-Research** | 12 | 5.89 MB | 研究资料 + PDF |
| **Medium** | 972 | 1.35 MB | 文章收集 |
| **Arxiv** | 236 | 0.82 MB | 论文元数据 |
| **memory** | 31 | 0.21 MB | 每日笔记 |
| **knowledge-graph** | 20 | 0.24 MB | 知识图谱 |
| **reports** | 48 | 0.22 MB | 报告文档 |

---

## 🎓 核心学习资料

### 1. AI-Research 目录

**位置:** `D:\OpenClaw\workspace\AI-Research\`

**内容:**
- 📄 README.md - 研究指南
- 📄 Timeline.md - 研究时间线
- 📄 Radar.md - 研究雷达图
- 📄 C - Audio.md - 音频概念笔记
- 📄 C - FAD.md - FAD 概念笔记
- 📄 P-Note 模板 - 论文解析模板

**PDF 论文:**
| 文件 | 大小 | 主题 |
|------|------|------|
| 2401.00001.pdf | 5.54 MB | 基础论文 |
| 2602.23958.pdf | 0.30 MB | 最新研究 |

---

### 2. Medium P-Note (论文深度解析)

**位置:** `D:\OpenClaw\workspace\Medium\P-Note\`

**最新解析 (2026-03-03):**

| 论文 | 大小 | 主题 |
|------|------|------|
| P-2026-03-03-The-Auton-Agentic-AI-Framework | 20.4 KB | Agentic AI 架构 |
| P-2026-03-03-PseudoAct | 19.1 KB | 伪代码规划 |
| P-2026-03-03-ProductResearch | 20.4 KB | 电商深度研究 |
| P-2026-03-03-ODAR | 19.5 KB | 自适应路由 |
| P-2026-03-03-From-Flat-Logs | 13.4 KB | 层次化归因 |

**历史解析:**
- P-20260302-* 系列 (5 篇)

---

### 3. Medium M-Note (跨论文对比)

**位置:** `D:\OpenClaw\workspace\Medium\M-Note\`

**最新对比:**

| 笔记 | 大小 | 主题 |
|------|------|------|
| M-20260303-Efficiency-Optimization | 6.8 KB | 效率优化技术对比 |

**内容:**
- 3 篇论文横向对比
- 技术演进路径
- 设计原则提炼

---

### 4. Medium C-Note (概念主题研究)

**位置:** `D:\OpenClaw\workspace\Medium\C-Note\`

**最新概念:**

| 笔记 | 主题 |
|------|------|
| C-2026-03-04-Medium-HighQuality-Articles | Medium 高质文章分析 |

---

### 5. Arxiv 元数据

**位置:** `D:\OpenClaw\workspace\Arxiv\`

**内容:**
- 236 篇论文元数据
- 按日期组织
- 包含标题/作者/摘要/链接

**使用:**
```powershell
# 查看最新收集
Get-ChildItem -Path "Arxiv" -Filter "*.md" | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

---

### 6. 知识图谱

**位置:** `D:\OpenClaw\workspace\knowledge-graph\`

**内容:**
- 38 个实体 (概念/论文/作者/机构)
- 139 个关系
- GraphML/JSON/Mermaid 格式

**可视化:**
- `knowledge-graph/visualization/index.html` - D3.js 交互式可视化
- `knowledge-graph/graph.mmd` - Mermaid 图表

---

### 7. 每日笔记

**位置:** `D:\OpenClaw\workspace\memory\`

**最新笔记:**

| 文件 | 主题 |
|------|------|
| 2026-03-04.md | 每日记录 |
| learning-notes-2026-03-04-youtube-pokemon-firered-leafgreen.md | YouTube 学习 |
| learning-notes-2026-03-04.md | Claude Skills 学习 |
| COLLECTION-SUMMARY-2026-03-04-FINAL.md | 晚间整理报告 |

---

## 🔍 快速查找

### 按主题查找

**Agentic AI:**
```powershell
Get-ChildItem -Recurse -Filter "*Agentic*" -Include *.md
```

**效率优化:**
```powershell
Get-ChildItem -Recurse -Filter "*Efficiency*" -Include *.md
```

**路由/规划:**
```powershell
Get-ChildItem -Recurse -Filter "*Routing*","*Planning*" -Include *.md
```

---

### 按日期查找

**今日资料:**
```powershell
Get-ChildItem -Recurse | Where-Object { $_.LastWriteTime.Date -eq (Get-Date).Date }
```

**本周资料:**
```powershell
Get-ChildItem -Recurse | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) }
```

---

## 📚 学习路径建议

### 入门路径

1. **阅读模板**
   - `AI-Research/Templates/P-Note-Template.md`
   - `AI-Research/Templates/M-Note-Template.md`
   - `AI-Research/Templates/C-Note-Template.md`

2. **查看示例**
   - `Medium/P-Note/P-2026-03-03-The-Auton-Agentic-AI-Framework.md`
   - `Medium/M-Note/M-20260303-Efficiency-Optimization.md`

3. **理解概念**
   - `memory/learning-notes-2026-03-04.md` (Claude Skills)
   - `AI-Research/C-*.md` (概念笔记)

---

### 进阶路径

1. **深度阅读论文解析**
   - 5 篇 P-Note (2026-03-03)
   - 5 篇 P-Note (2026-03-02)

2. **对比分析**
   - M-Note 跨论文对比
   - 技术演进路径

3. **知识图谱**
   - 查看实体关系
   - 理解知识网络

---

### 研究路径

1. **选择研究方向**
   - 查看 `AI-Research/Radar.md`
   - 查看 `AI-Research/Timeline.md`

2. **收集相关资料**
   - Arxiv 每日收集 (2AM 自动)
   - Medium 文章收集 (4AM 自动)

3. **深度解析**
   - 使用 P-Note 模板
   - 使用 batch-processor 批量解析

4. **知识沉淀**
   - 更新 MEMORY.md
   - 构建知识图谱

---

## 🎯 推荐学习顺序

### 第 1 天：了解系统

- [ ] 阅读 README.md
- [ ] 查看目录结构
- [ ] 理解 P/M/C-Note 格式

### 第 2-3 天：学习核心概念

- [ ] 阅读 P-2026-03-03-The-Auton-Agentic-AI-Framework
- [ ] 阅读 P-2026-03-03-PseudoAct
- [ ] 阅读 P-2026-03-03-ODAR

### 第 4-5 天：对比分析

- [ ] 阅读 M-20260303-Efficiency-Optimization
- [ ] 理解技术演进
- [ ] 提炼设计原则

### 第 6-7 天：实践应用

- [ ] 选择一篇新论文
- [ ] 使用 P-Note 模板解析
- [ ] 添加到知识图谱

---

## 📄 相关报告

- `reports/storage-optimization-report-2026-03-04.md` - 存储优化报告
- `reports/optimization-complete-2026-03-04.md` - 优化完成报告
- `reports/learning-resources-index-2026-03-04.md` - 本索引

---

## 🔗 外部资源

- **arXiv:** https://arxiv.org
- **Medium:** https://medium.com
- **Semantic Scholar:** https://www.semanticscholar.org
- **Connected Papers:** https://www.connectedpapers.com

---

*学习资料索引 · 2026-03-04 23:33*
