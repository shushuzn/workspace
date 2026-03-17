# 📚 知识卡片生成器 (Knowledge Card Generator)

**版本:** v2.5  
**创建日期:** 2026-03-11  
**状态:** ✅ 可用 - Web UI/API 监控/公式渲染

---

## 📖 概述

从学术论文 PDF 自动生成结构化 HTML 知识卡片。支持元数据提取、章节解析、参考文献识别和学术诚信检查。

---

## ✨ 功能

### 核心功能
- ✅ **元数据提取** - 标题、作者、年份、arXiv ID
- ✅ **章节解析** - 自动识别论文结构
- ✅ **参考文献提取** - 识别引用并标记验证状态
- ✅ **参考文献自动验证** - CrossRef API + arXiv API
- ✅ **智能重试机制** - 失败自动重试 3 次 (指数退避) (v2.1) 🔥
- ✅ **验证结果缓存** - 24 小时缓存，避免重复请求 (v2.1) 🔥
- ✅ **BibTeX 导出** - 已验证文献自动导出 (v2.1) 🔥
- ✅ **错误日志记录** - 详细验证日志 (v2.1)
- ✅ **并发验证** - 5 线程并行，速度提升 3-5 倍 (v2.2) 🔥🔥
- ✅ **缓存管理** - LRU 淘汰，自动清理过期/超限缓存 (v2.2) 🔥🔥
- ✅ **验证统计报告** - 成功/失败/缓存命中率 (v2.3) 🔥🔥🔥
- ✅ **缓存查看/清理** - 命令行管理缓存 (v2.3) 🔥🔥🔥
- ✅ **批量汇总报告** - HTML+JSON 汇总报告 (v2.4) 🔥🔥🔥🔥
- ✅ **可视化图表** - Chart.js 饼图/柱状图 (v2.4) 🔥🔥🔥🔥
- ✅ **缓存导出/导入** - 备份和迁移缓存 (v2.4) 🔥🔥🔥🔥
- ✅ **Web UI 界面** - Flask Web 应用 (v2.5 新增) 🔥🔥🔥🔥🔥
- ✅ **API 配额监控** - CrossRef/arXiv 限速跟踪 (v2.5 新增) 🔥🔥🔥🔥🔥
- ✅ **公式 LaTeX 渲染** - MathJax 支持 (v2.5 新增) 🔥🔥🔥🔥🔥
- ✅ **图表检测** - 提取图片并编号
- ✅ **HTML 卡片生成** - 美观的响应式布局
- ✅ **学术诚信检查** - 自动标记验证状态

### 输出特性
- 📱 响应式设计 (桌面/平板/手机)
- 🎨 现代 UI 风格
- ⚠️ 学术诚信提醒
- 🔍 参考文献验证状态标记

---

## 🚀 安装

```bash
# 依赖
pip install PyMuPDF

# 验证安装
py knowledge-card-generator.py --help
```

---

## 📖 用法

### 单文件处理

```bash
# 基本用法 (输出到同目录)
py knowledge-card-generator.py paper.pdf

# 指定输出目录
py knowledge-card-generator.py paper.pdf -o output/

# 预览 HTML (不保存)
py knowledge-card-generator.py paper.pdf --preview

# 验证参考文献 (v2.0 新功能)
py knowledge-card-generator.py paper.pdf --validate

# 验证 + 输出到指定目录
py knowledge-card-generator.py paper.pdf --validate -o cards/

# 验证 + 导出 BibTeX (v2.1 新功能)
py knowledge-card-generator.py paper.pdf --validate --export-bibtex

# 使用自定义缓存文件 (v2.1 新功能)
py knowledge-card-generator.py paper.pdf --validate --cache my-cache.json

# 并发验证 (v2.2 新功能，默认启用)
py knowledge-card-generator.py paper.pdf --validate  # 默认 5 线程

# 自定义并发线程数 (v2.2 新功能)
py knowledge-card-generator.py paper.pdf --validate --workers 10

# 禁用并发 (串行模式) (v2.2 新功能)
py knowledge-card-generator.py paper.pdf --validate --no-concurrent

# 自定义缓存大小限制 (v2.2 新功能)
py knowledge-card-generator.py paper.pdf --validate --max-cache-size 2000

# 查看缓存统计 (v2.3 新功能)
py knowledge-card-generator.py --view-cache

# 清理过期缓存 (v2.3 新功能)
py knowledge-card-generator.py --cleanup-cache

# 导出缓存 (v2.4 新功能)
py knowledge-card-generator.py --export-cache backup.json

# 导入缓存 (v2.4 新功能)
py knowledge-card-generator.py --import-cache backup.json

# 批量处理 + 生成汇总报告 (v2.4 新功能)
py knowledge-card-generator.py --batch papers/ --validate --batch-report -o cards/

# 启动 Web UI (v2.5 新功能)
py 30-scripts/knowledge-card-webui.py --port 5000

# Web UI 访问地址
# http://127.0.0.1:5000
```

### 批量处理

```bash
# 处理整个文件夹
py knowledge-card-generator.py --batch papers/

# 批量处理 + 指定输出
py knowledge-card-generator.py --batch papers/ -o cards/

# 批量处理 + 验证参考文献 (注意速率限制)
py knowledge-card-generator.py --batch papers/ --validate -o cards/
```

### 批量处理

```bash
# 处理整个文件夹
py knowledge-card-generator.py --batch papers/

# 批量处理 + 指定输出
py knowledge-card-generator.py --batch papers/ -o cards/
```

### 输出文件

```
paper.pdf → paper.card.html (单文件模式)
papers/ → cards/ (批量模式)
├── paper1.html
├── paper2.html
└── batch-stats.json (处理统计)
```

---

## 📋 输出示例

### HTML 卡片结构

```html
<!DOCTYPE html>
<html>
<head>
    <title>论文标题</title>
    <style>...</style>
</head>
<body>
    <div class="card">
        <div class="header">
            <h1>论文标题</h1>
            <div class="meta">作者：张三，李四</div>
            <div class="meta">年份：2024</div>
            <div class="meta">arXiv: <span class="badge">2401.00001</span></div>
        </div>
        
        <div class="abstract">
            <strong>📖 摘要</strong>
            <p>摘要内容...</p>
        </div>
        
        <div class="integrity-notice">
            <strong>🔒 学术诚信声明：</strong>
            本卡片内容由 AI 辅助生成，所有参考文献需人工核实真实性。
        </div>
        
        <h2>📑 核心章节</h2>
        <div class="section">...</div>
        
        <h2>📚 参考文献</h2>
        <div class="reference unverified">
            <span class="ref-id">[1]</span>
            <span class="ref-content">Author. Title. Journal, 2024.</span>
            <span class="ref-status">⚠️ 待验证</span>
        </div>
    </div>
</body>
</html>
```

---

## ⚠️ 学术诚信规范

### 重要声明

**v2.0 支持自动验证，但仍需人工复核！**

- ✅ 自动验证 DOI (CrossRef API)
- ✅ 自动验证 arXiv ID (arXiv API)
- ✅ 显示验证详情 (期刊名、年份、引用数)
- ⚠️ 无 DOI/arXiv 的文献仍需人工核实
- ❌ 禁止直接使用未验证的文献信息

### 验证流程 (v2.0)

```
1. 生成卡片 → AI 提取参考文献
2. 自动验证 → CrossRef/arXiv API (可选 --validate)
3. 结果显示 → ✅已验证 / 🔍需人工 / ⚠️待验证
4. 人工复核 → 检查无 DOI/arXiv 的文献
5. 发布使用 → 仅使用已验证文献
```

### 验证资源

| 类型 | 验证渠道 | 自动验证 |
|------|----------|----------|
| DOI 文献 | CrossRef API | ✅ 自动 |
| arXiv 论文 | arXiv API | ✅ 自动 |
| 期刊论文 | 期刊官网 / Web of Science | 🔍 人工 |
| 会议论文 | IEEE Xplore / ACM DL | 🔍 人工 |
| 书籍 | 出版社官网 / Google Books | 🔍 人工 |

### API 速率限制

| API | 限制 | 自动延迟 |
|-----|------|----------|
| CrossRef | 10 请求/分钟 | 6 秒/请求 |
| arXiv | 10 请求/分钟 | 6 秒/请求 |

**注意:** 批量验证 10 篇参考文献约需 1 分钟。

### v2.3 优化特性

#### 验证统计报告 🔥
- **详细统计** (总数/成功/失败/需人工)
- **缓存命中率** (显示缓存节省的 API 调用)
- **性能估算** (理论耗时计算)
- **百分比显示** (直观了解验证质量)

**输出示例:**
```
📊 验证统计报告
   总参考文献：17 篇
   ✅ 已验证：12 篇 (70.6%)
   🔍 需人工：3 篇 (17.6%)
   ❌ 验证失败：2 篇 (11.8%)

   性能统计:
   📦 缓存命中：5 篇 (29.4%)
   🌐 API 调用：12 篇
   ⏱️  平均耗时：72.0 秒 (理论值)
```

#### 缓存管理命令 🔥
- **查看缓存** (`--view-cache`)
- **清理过期** (`--cleanup-cache`)
- **统计信息** (大小/验证状态/最近缓存)

**使用示例:**
```bash
# 查看缓存统计
py knowledge-card-generator.py --view-cache

# 输出:
📊 缓存统计
   缓存文件：.ref-cache.json
   缓存大小：50 条
   文件大小：125.34 KB

   验证状态:
   ✅ 已验证：42 条
   ❌ 验证失败：8 条

   最近缓存 (前 5 条):
   ✅ [2026-03-11] Attention Is All You Need...
   ✅ [2026-03-11] BERT: Pre-training of Deep...
   ❌ [2026-03-10] Unknown DOI...

# 清理过期缓存
py knowledge-card-generator.py --cleanup-cache

# 输出:
✅ 清理完成：删除 12 条过期记录
   剩余缓存：38 条
```

### v2.2 优化特性

#### 并发验证 🔥
- **5 线程并行** (默认，可配置 1-20)
- **速度提升 3-5 倍** (批量验证场景)
- **实时进度显示** (tqdm 进度条)
- **线程安全** (锁保护缓存)
- **自动降级** (tqdm 未安装时切换串行)

**使用示例:**
```bash
# 默认 5 线程
py knowledge-card-generator.py paper.pdf --validate

# 10 线程 (更快的验证)
py knowledge-card-generator.py paper.pdf --validate --workers 10

# 串行模式 (调试用)
py knowledge-card-generator.py paper.pdf --validate --no-concurrent
```

#### 缓存管理 🔥
- **LRU 淘汰策略** (保留最近使用的缓存)
- **大小限制** (默认 1000 条，可配置)
- **自动清理** (启动时检查并清理)
- **过期清理** (>24 小时自动删除)

**使用示例:**
```bash
# 默认缓存限制 1000 条
py knowledge-card-generator.py paper.pdf --validate

# 自定义缓存大小
py knowledge-card-generator.py paper.pdf --validate --max-cache-size 2000
```

### v2.1 优化特性

#### 智能重试机制
- 失败自动重试 3 次
- 指数退避策略 (6s → 12s → 24s)
- 提高验证成功率

#### 验证结果缓存
- 缓存文件：`.ref-cache.json` (默认)
- 缓存有效期：24 小时
- 自定义缓存：`--cache my-cache.json`
- 避免重复 API 请求

#### BibTeX 导出
- 仅导出已验证文献
- 自动生成 BibTeX key
- 支持 article/book/misc 类型
- 输出：`paper.bib`

#### 错误日志
- 日志文件：`knowledge-card-validator.log`
- 记录验证成功/失败/重试
- 便于调试和审计

---

## 📊 处理统计

批量处理会生成 `batch-stats.json`:

```json
{
  "total": 10,
  "success": 9,
  "failed": 1,
  "cards": [
    {
      "file": "paper1.pdf",
      "output": "paper1.html",
      "status": "success"
    },
    {
      "file": "paper2.pdf",
      "error": "PDF 损坏",
      "status": "failed"
    }
  ]
}
```

---

## 🔧 配置选项

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `pdf_file` | PDF 文件路径 | 必填 |
| `--output, -o` | 输出目录 | 同目录 |
| `--batch, -b` | 批量处理文件夹 | - |
| `--preview, -p` | 预览 HTML | false |

### 提取限制

| 项目 | 限制 | 说明 |
|------|------|------|
| 章节数量 | 前 5 章 | 避免卡片过长 |
| 章节内容 | 500 字/章 | 摘要展示 |
| 参考文献 | 前 10 篇 | 避免列表过长 |

---

## 🧪 测试

### 测试用例

```bash
# 测试单文件
py knowledge-card-generator.py test-paper.pdf -o test-output/

# 测试批量
py knowledge-card-generator.py --batch test-papers/ -o test-cards/

# 验证输出
ls test-output/*.html
```

### 验收标准 (v2.3)

| 标准 | 状态 | 说明 |
|------|------|------|
| 元数据提取 | ✅ | 标题/作者/年份/arXiv |
| 章节解析 | ✅ | 识别 Introduction/Methods 等 |
| 参考文献提取 | ✅ | 识别引用格式 |
| DOI 自动验证 | ✅ | CrossRef API 集成 |
| arXiv 自动验证 | ✅ | arXiv API 集成 |
| 验证状态显示 | ✅ | ✅已验证/🔍需人工/⚠️待验证 |
| 验证详情展示 | ✅ | 期刊名/年份/引用数 |
| **智能重试** | ✅ | 3 次重试 + 指数退避 |
| **结果缓存** | ✅ | 24 小时缓存 |
| **BibTeX 导出** | ✅ | 已验证文献导出 |
| **错误日志** | ✅ | 详细验证日志 |
| **并发验证** | ✅ | 5 线程并行，3-5 倍提速 |
| **缓存管理** | ✅ | LRU 淘汰 + 自动清理 |
| **验证统计** | ✅ | 成功/失败/缓存命中率 |
| **缓存查看** | ✅ | --view-cache 命令 |
| **缓存清理** | ✅ | --cleanup-cache 命令 |
| HTML 生成 | ✅ | 有效 HTML5 |
| 响应式 | ✅ | 适配手机/平板/桌面 |
| 学术诚信 | ✅ | 包含验证提醒 |

---

## 📁 文件结构

```
30-scripts/
├── knowledge-card-generator.py      # 主脚本
├── knowledge-card-generator/
│   └── README.md                     # 本文档
└── knowledge-cards/                  # 输出目录 (可选)
    ├── paper1.html
    ├── paper2.html
    └── batch-stats.json
```

---

## 🔮 未来改进

- [ ] 公式 LaTeX 渲染 (MathJax)
- [ ] 图表自动裁剪 + 增强
- [ ] 参考文献自动验证 (CrossRef API)
- [ ] 支持中文论文
- [ ] 导出 Markdown 格式
- [ ] 知识图谱关联

---

## 📝 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.5 | 2026-03-11 | Web UI/API 配额监控/公式 LaTeX 渲染 |
| v2.4 | 2026-03-11 | 批量汇总报告/可视化图表/缓存导入导出 |
| v2.3 | 2026-03-11 | 验证统计报告/缓存查看清理命令 |
| v2.2 | 2026-03-11 | 并发验证 (5 线程)/缓存管理 (LRU+ 自动清理) |
| v2.1 | 2026-03-11 | 智能重试/缓存/BibTeX 导出/错误日志 |
| v2.0 | 2026-03-11 | 参考文献自动验证 (CrossRef + arXiv API) |
| v1.0 | 2026-03-11 | 初始版本 - 基础提取 + HTML 生成 |

---

## 📄 许可证

MIT License - AI Research OS 项目

---

*知识卡片生成器 v1.0 | 2026-03-11*
