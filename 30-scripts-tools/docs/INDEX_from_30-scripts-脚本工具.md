# 30-scripts 文档索引

**版本:** v1.0  
**创建日期:** 2026-03-12  
**最后更新:** 2026-03-12  
**文档总数:** 10+

---

## 📁 目录结构

```
30-scripts-脚本工具/
├── docs/                          # 文档框架
│   ├── README-TEMPLATE.md         # 文档模板
│   ├── CONTRIBUTING-DOCS.md       # 文档更新指南
│   ├── TEMPLATE-VALIDATION-REPORT.md
│   └── INDEX.md                   # 本文档
│
├── 01-KNOWLEDGE-CARDS/            # 知识卡片系统
│   ├── core/
│   │   ├── knowledge-card-generator.py
│   │   ├── knowledge-card-webui.py
│   │   └── README.md              # ✅ 100/100
│   └── README.md
│
├── 02-DAILY-BRIEF/                # 日常简报系统
│   ├── core/
│   │   └── daily-brief.py
│   └── README.md                  # ✅ 95/100
│
├── pdf-extractor/                 # PDF 提取器
│   ├── layoutlm_pdf_extractor.py
│   └── README.md                  # ✅ 98/100
│
├── figure-enhancer/               # 图表增强器
│   ├── figure_enhancer.py
│   ├── quality_filter.py
│   ├── super_resolution.py
│   └── README.md                  # ✅ 98/100
│
├── graph-optimizer/               # 图谱优化器
│   ├── graph_renderer_canvas.html
│   ├── BENCHMARK-REPORT.md        # 性能基准
│   └── README.md                  # ✅ 100/100
│
├── multimodal-kg/                 # 多模态图谱
│   ├── multimodal_kg.py
│   ├── tests/
│   │   ├── test_multimodal_kg.py  # 21 个单元测试
│   │   └── TEST-REPORT.md         # 测试报告
│   └── README.md                  # ✅ 100/100
│
└── [更多模块...]
```

---

## 📊 文档质量总览

| 模块 | 文档评分 | 测试覆盖 | 状态 |
|------|----------|----------|------|
| knowledge-card-webui | 100/100 | ⚠️ 待补充 | ✅ |
| daily-brief | 95/100 | ⚠️ 待补充 | ✅ |
| pdf-extractor | 98/100 | ✅ 有测试 | ✅ |
| figure-enhancer | 98/100 | ✅ 有测试 | ✅ |
| graph-optimizer | 100/100 | ✅ 有基准 | ✅ |
| multimodal-kg | 100/100 | ✅ 21 个测试 | ✅ |

**平均评分：98.5/100**

---

## 📖 快速导航

### 按功能分类

#### 知识管理
- [知识卡片生成器](01-KNOWLEDGE-CARDS/core/README.md) - PDF→HTML 知识卡片
- [多模态图谱](multimodal-kg/README.md) - 图表/公式/数据管理

#### 数据处理
- [PDF 提取器](pdf-extractor/README.md) - LayoutLM 布局分析
- [图表增强器](figure-enhancer/README.md) - 质量过滤 + 超分辨率

#### 可视化
- [图谱优化器](graph-optimizer/README.md) - 高性能图谱渲染

#### 自动化
- [日常简报](02-DAILY-BRIEF/README.md) - arXiv/Medium/HN 聚合

---

### 按使用场景分类

#### 快速开始
1. [安装指南](#安装指南)
2. [快速入门](#快速入门)
3. [常见问题](#常见问题)

#### 进阶使用
1. [批量处理](#批量处理)
2. [自定义配置](#自定义配置)
3. [集成开发](#集成开发)

#### 开发贡献
1. [文档模板](docs/README-TEMPLATE.md)
2. [更新指南](docs/CONTRIBUTING-DOCS.md)
3. [测试规范](#测试规范)

---

## 🔧 安装指南

### 统一依赖安装

```bash
# 进入目录
cd 30-scripts-脚本工具

# 安装所有依赖
pip install -r requirements-all.txt

# 或按模块安装
pip install -r 01-KNOWLEDGE-CARDS/requirements.txt
pip install -r pdf-extractor/requirements.txt
```

### 可选依赖

```bash
# Real-ESRGAN (图表超分辨率)
pip install realesrgan basicsr

# CLIP (图像语义搜索)
pip install clip-by-openai

# LayoutLM (PDF 布局分析)
pip install transformers
```

---

## 🚀 快速入门

### 示例 1: 生成知识卡片

```bash
# 处理单篇 PDF
py 01-KNOWLEDGE-CARDS/core/knowledge-card-generator.py paper.pdf --validate

# Web UI 界面
py 01-KNOWLEDGE-CARDS/core/knowledge-card-webui.py --port 5000
```

### 示例 2: 提取 PDF 内容

```bash
# 提取为 Markdown
py pdf-extractor/layoutlm_pdf_extractor.py paper.pdf

# 提取为 JSON
py pdf-extractor/layoutlm_pdf_extractor.py paper.pdf --format json
```

### 示例 3: 增强图表质量

```bash
# 自动增强
py figure-enhancer/figure_enhancer.py figure.png -o enhanced.png

# 批量增强
py figure-enhancer/figure_enhancer.py --batch figures/ --output-dir enhanced/
```

### 示例 4: 生成日常简报

```bash
# 生成今日简报
py 02-DAILY-BRIEF/core/daily-brief.py --date today

# 发送到 Feishu
py 02-DAILY-BRIEF/core/daily-brief.py --date today --send-feishu
```

---

## ❓ 常见问题

### Q1: 如何选择合适的工具？

**A:** 根据需求选择：
- **PDF→知识卡片:** knowledge-card-generator
- **PDF→Markdown/JSON:** pdf-extractor
- **图表质量提升:** figure-enhancer
- **图谱可视化:** graph-optimizer
- **多模态管理:** multimodal-kg

---

### Q2: 所有工具都支持批量处理吗？

**A:** 大部分支持：
- ✅ knowledge-card-generator (--batch)
- ✅ pdf-extractor (脚本循环)
- ✅ figure-enhancer (--batch)
- ✅ daily-brief (自动生成)

---

### Q3: 如何集成到自己的项目？

**A:** 三种方式：
1. **命令行调用:** `subprocess.run()`
2. **Python 导入:** `from module import Class`
3. **API 调用:** (部分工具提供 REST API)

---

### Q4: 测试如何运行？

**A:** 各模块独立测试：
```bash
# multimodal-kg
py multimodal-kg/tests/test_multimodal_kg.py -v

# pdf-extractor
py pdf-extractor/test_pdf_extractor.py

# figure-enhancer
py figure-enhancer/test_suite.py
```

---

### Q5: 文档如何更新？

**A:** 遵循 [CONTRIBUTING-DOCS.md](docs/CONTRIBUTING-DOCS.md)

---

## 📚 相关资源

- [AI Research OS](../../README.md) - 项目总览
- [SOUL.md](../../SOUL.md) - 项目理念
- [AGENTS.md](../../AGENTS.md) - 开发规范
- [GitHub](https://github.com/openclaw/openclaw) - 代码仓库

---

## 📝 更新日志

### v1.0 (2026-03-12)
- ✨ 初始文档框架
- ✨ 10+ 模块文档 (平均 98.5 分)
- ✨ 统一模板和指南
- ✨ 测试报告集成

---

**维护者:** Claw (AI Agent)  
**最后更新:** 2026-03-12  
**下次审查:** 2026-04-12 (月度审查)
