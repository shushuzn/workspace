# 01-KNOWLEDGE-CARDS - 知识卡片生成器 🔥

**用途:** 从学术论文 PDF 自动生成结构化 HTML 知识卡片

**版本:** v2.5 (2026-03-11)

---

## 📁 目录结构

```
01-KNOWLEDGE-CARDS/
├── core/                      # 核心脚本
│   ├── knowledge-card-generator.py   (52KB, 主脚本)
│   ├── knowledge-card-webui.py       (21KB, Web 界面)
│   └── README.md
├── pdf/                       # PDF 处理
│   └── pdf-extractor/
│       ├── layoutlm_pdf_extractor.py
│       ├── simple_pdf_extractor.py
│       └── README.md
├── figures/                   # 图表处理
│   └── figure-enhancer/
│       ├── figure_enhancer.py
│       ├── super_resolution.py
│       └── README.md
├── formula/                   # 公式处理
│   ├── prepare-formula-dataset.py
│   ├── generate_formula_dataset.py
│   └── finetune-formula-model.py
├── docs/                      # 文档
│   └── knowledge-card-generator/
│       └── README.md          (18KB, 详细文档)
├── test-output/               # 测试输出
│   └── *.html
└── README.md                  # 本文档
```

---

## 🚀 快速开始

### 单文件处理
```bash
# 基本用法
py 01-KNOWLEDGE-CARDS/core/knowledge-card-generator.py paper.pdf

# 验证参考文献
py 01-KNOWLEDGE-CARDS/core/knowledge-card-generator.py paper.pdf --validate

# 导出 BibTeX
py 01-KNOWLEDGE-CARDS/core/knowledge-card-generator.py paper.pdf --validate --export-bibtex
```

### 批量处理
```bash
# 处理整个文件夹
py 01-KNOWLEDGE-CARDS/core/knowledge-card-generator.py --batch papers/ -o cards/

# 批量处理 + 生成汇总报告
py 01-KNOWLEDGE-CARDS/core/knowledge-card-generator.py --batch papers/ --validate --batch-report -o cards/
```

### Web UI
```bash
# 启动 Web 界面
py 01-KNOWLEDGE-CARDS/core/knowledge-card-webui.py --port 5000

# 访问地址
http://127.0.0.1:5000
```

---

## ✨ 核心功能

### v2.5 新功能
- ✅ **Web UI 界面** - Flask + Tailwind CSS
- ✅ **API 配额监控** - CrossRef/arXiv 限速跟踪
- ✅ **公式 LaTeX 渲染** - MathJax 支持
- ✅ **批量汇总报告** - HTML+JSON 可视化
- ✅ **缓存导入/导出** - 备份和迁移

### 完整功能列表
| 功能 | 说明 | 版本 |
|------|------|------|
| PDF 解析 | 支持单栏/双栏/混合布局 | v1.0 |
| 元数据提取 | 标题/作者/年份/arXiv ID | v1.0 |
| 章节解析 | 自动识别论文结构 | v1.0 |
| 参考文献验证 | CrossRef/arXiv API | v2.0 |
| 智能重试 | 3 次重试 + 指数退避 | v2.1 |
| 结果缓存 | 24 小时缓存 | v2.1 |
| BibTeX 导出 | 已验证文献导出 | v2.1 |
| 并发验证 | 5 线程并行 (5x 提速) | v2.2 |
| 缓存管理 | LRU 淘汰 + 自动清理 | v2.2 |
| 统计报告 | 成功/失败/缓存命中 | v2.3 |
| 批量报告 | HTML+JSON 汇总 | v2.4 |
| 可视化图表 | Chart.js 饼图 | v2.4 |
| Web UI | Flask Web 应用 | v2.5 |
| API 监控 | 配额跟踪 | v2.5 |
| 公式渲染 | MathJax 支持 | v2.5 |

---

## 📊 性能指标

### 处理速度
| 文献数 | 串行时间 | 并发时间 (5 线程) | 提速 |
|--------|----------|------------------|------|
| 10 篇 | 60 秒 | 12 秒 | 5.0x |
| 20 篇 | 120 秒 | 24 秒 | 5.0x |
| 50 篇 | 300 秒 | 60 秒 | 5.0x |

### 验证成功率
- DOI 验证：~85%
- arXiv 验证：~90%
- 缓存命中率：~30% (重复验证场景)

---

## 🔧 配置选项

### 命令行参数
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--output, -o` | 输出目录 | 同目录 |
| `--validate, -v` | 验证参考文献 | false |
| `--export-bibtex` | 导出 BibTeX | false |
| `--workers` | 并发线程数 | 5 |
| `--max-cache-size` | 缓存最大条目数 | 1000 |
| `--view-cache` | 查看缓存统计 | false |
| `--cleanup-cache` | 清理过期缓存 | false |
| `--export-cache` | 导出缓存到文件 | - |
| `--import-cache` | 从文件导入缓存 | - |
| `--batch-report` | 生成批量汇总报告 | false |

---

## 📦 依赖项

### Python 包
```bash
pip install PyMuPDF Flask tqdm Pillow
```

### 可选依赖
```bash
# Web UI 支持
pip install flask

# 进度条显示
pip install tqdm

# 图像处理
pip install Pillow
```

---

## 🧪 测试

### 运行测试
```bash
# PDF 提取器测试
py 01-KNOWLEDGE-CARDS/pdf/pdf-extractor/test_pdf_extractor.py

# 图表增强器测试
py 01-KNOWLEDGE-CARDS/figures/figure-enhancer/test_suite.py
```

### 验证安装
```bash
# 验证主脚本
py 01-KNOWLEDGE-CARDS/core/knowledge-card-generator.py --help

# 验证 Web UI
py 01-KNOWLEDGE-CARDS/core/knowledge-card-webui.py --help
```

---

## 📊 统计信息

| 类别 | 数量 | 大小 |
|------|------|------|
| 核心脚本 | 2 | 73KB |
| PDF 处理 | 12 | 67KB |
| 图表处理 | 11 | 43KB |
| 公式处理 | 5 | 23KB |
| HTML 文档 | 3 | 36KB |
| **总计** | **33** | **~242KB** |

---

## 🔗 相关项目

- **02-DAILY-BRIEF** - 日常简报系统 (可能使用知识卡片)
- **03-LIG-KNOWLEDGE-GRAPH** - LIG 知识图谱 (类似功能)
- **05-AI-RESEARCH** - AI 研究工具 (论文分析)

---

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📄 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.5 | 2026-03-11 | Web UI/API 监控/公式渲染 |
| v2.4 | 2026-03-11 | 批量报告/可视化/缓存导入导出 |
| v2.3 | 2026-03-11 | 验证统计/缓存命令 |
| v2.2 | 2026-03-11 | 并发验证/缓存管理 |
| v2.1 | 2026-03-11 | 智能重试/BibTeX 导出 |
| v2.0 | 2026-03-11 | 参考文献自动验证 |
| v1.0 | 2026-03-11 | 初始版本 |

---

## 📄 许可证

MIT License

---

## 📞 联系方式

- **项目主页:** GitHub
- **问题反馈:** Issues
- **文档:** `docs/knowledge-card-generator/README.md`

---

*最后更新：2026-03-11 | 版本 v2.5*
