# 30-scripts 重组计划 - 按项目分类

**创建日期:** 2026-03-11 18:50  
**问题:** 当前按类型分类导致跨项目查找困难  
**解决方案:** 按项目分类，每个项目独立文件夹

---

## 当前问题

```
30-scripts/
├── pdf-extractor/          ← 知识卡片项目
├── figure-enhancer/        ← 知识卡片项目
├── knowledge-card-generator/ ← 知识卡片项目
├── knowledge-card-webui.py   ← 知识卡片项目 (散落根目录)
├── daily-brief/            ← 日常简报项目
├── graph-optimizer/        ← LIG 知识图谱项目
├── multimodal-kg/          ← LIG 知识图谱项目
└── ... (其他散落文件)
```

**问题:**
1. 同一项目的文件分散在多个文件夹
2. 散落文件难以管理 (如 knowledge-card-webui.py)
3. 跨项目查找需要记住文件类型
4. 项目边界不清晰

---

## 新结构 - 按项目分类

```
30-scripts/
├── 00-UTILS/                    # 通用工具 (跨项目)
│   ├── cache/
│   ├── backups/
│   ├── utils/
│   └── tools/
│
├── 01-KNOWLEDGE-CARDS/          # 知识卡片生成器项目
│   ├── core/
│   │   ├── knowledge-card-generator.py
│   │   ├── knowledge-card-webui.py
│   │   └── README.md
│   ├── pdf/
│   │   └── pdf-extractor/
│   ├── figures/
│   │   └── figure-enhancer/
│   └── docs/
│
├── 02-DAILY-BRIEF/              # 日常简报项目
│   ├── daily-brief/
│   ├── weather/
│   ├── feishu-ui-sync.py
│   └── README.md
│
├── 03-LIG-KNOWLEDGE-GRAPH/      # LIG 知识图谱项目
│   ├── graph-optimizer/
│   ├── multimodal-kg/
│   ├── lig-worker.js
│   └── README.md
│
├── 04-COLLECTORS/               # 数据收集器
│   ├── collectors/
│   ├── arxiv-daily/
│   ├── medium-watcher/
│   └── README.md
│
├── 05-AI-RESEARCH/              # AI 研究工具
│   ├── ai-analysis/
│   ├── analysis/
│   ├── research/
│   └── README.md
│
├── 06-MONITORING/               # 监控工具
│   ├── monitoring/
│   ├── cpu-limiter.ps1
│   └── README.md
│
├── 07-DATA/                     # 数据处理
│   ├── data-lake/
│   ├── api/
│   ├── api-server/
│   └── README.md
│
├── 08-AUTOMATION/               # 自动化脚本
│   ├── auto-pnote/
│   ├── github-sync/
│   └── README.md
│
├── 09-TESTS/                    # 测试相关
│   ├── testing/
│   └── test-suite/
│
└── 99-ARCHIVE/                  # 归档
    ├── level-0/
    ├── early_exit_framework/
    └── feedback/
```

---

## 重组步骤

### 1. 创建新目录结构
```bash
mkdir 30-scripts/00-UTILS
mkdir 30-scripts/01-KNOWLEDGE-CARDS
mkdir 30-scripts/02-DAILY-BRIEF
mkdir 30-scripts/03-LIG-KNOWLEDGE-GRAPH
mkdir 30-scripts/04-COLLECTORS
mkdir 30-scripts/05-AI-RESEARCH
mkdir 30-scripts/06-MONITORING
mkdir 30-scripts/07-DATA
mkdir 30-scripts/08-AUTOMATION
mkdir 30-scripts/09-TESTS
mkdir 30-scripts/99-ARCHIVE
```

### 2. 移动文件

#### 知识卡片项目 (01-KNOWLEDGE-CARDS)
```bash
mv 30-scripts/knowledge-card-generator.py 30-scripts/01-KNOWLEDGE-CARDS/core/
mv 30-scripts/knowledge-card-webui.py 30-scripts/01-KNOWLEDGE-CARDS/core/
mv 30-scripts/knowledge-card-generator/ 30-scripts/01-KNOWLEDGE-CARDS/core/
mv 30-scripts/pdf-extractor/ 30-scripts/01-KNOWLEDGE-CARDS/pdf/
mv 30-scripts/figure-enhancer/ 30-scripts/01-KNOWLEDGE-CARDS/figures/
```

#### 日常简报项目 (02-DAILY-BRIEF)
```bash
mv 30-scripts/daily-brief/ 30-scripts/02-DAILY-BRIEF/
mv 30-scripts/weather/ 30-scripts/02-DAILY-BRIEF/
mv 30-scripts/feishu-ui-sync.py 30-scripts/02-DAILY-BRIEF/
mv 30-scripts/feishu-queue-process.py 30-scripts/02-DAILY-BRIEF/
```

#### LIG 知识图谱项目 (03-LIG-KNOWLEDGE-GRAPH)
```bash
mv 30-scripts/graph-optimizer/ 30-scripts/03-LIG-KNOWLEDGE-GRAPH/
mv 30-scripts/multimodal-kg/ 30-scripts/03-LIG-KNOWLEDGE-GRAPH/
mv 30-scripts/lig-*.js 30-scripts/03-LIG-KNOWLEDGE-GRAPH/
mv 30-scripts/lig-*.html 30-scripts/03-LIG-KNOWLEDGE-GRAPH/
```

#### 通用工具 (00-UTILS)
```bash
mv 30-scripts/cache/ 30-scripts/00-UTILS/
mv 30-scripts/backups/ 30-scripts/00-UTILS/
mv 30-scripts/utils/ 30-scripts/00-UTILS/
mv 30-scripts/tools/ 30-scripts/00-UTILS/
```

### 3. 创建项目 README
每个项目文件夹创建 README.md，包含：
- 项目概述
- 文件结构
- 使用方法
- 依赖项
- 相关脚本

### 4. 更新路径引用
- 更新定时任务配置
- 更新文档中的路径
- 更新导入语句

### 5. 验证
- 测试所有脚本仍能正常运行
- 验证定时任务正常执行
- 确认文档链接有效

---

## 优势

### 查找效率提升
| 场景 | 旧方式 | 新方式 |
|------|--------|--------|
| 找知识卡片相关 | 记住在 pdf-extractor/figure-enhancer/ | 直接去 01-KNOWLEDGE-CARDS/ |
| 找日常简报 | 记住在 daily-brief/weather/ | 直接去 02-DAILY-BRIEF/ |
| 找 LIG 图谱 | 记住在 graph-optimizer/multimodal-kg/ | 直接去 03-LIG-KNOWLEDGE-GRAPH/ |

### 项目管理清晰
- 每个项目独立文件夹
- 项目边界清晰
- 易于删除/归档整个项目
- 易于权限管理

### 扩展性好
- 新增项目只需创建新文件夹
- 不影响现有结构
- 易于理解

---

## 执行时间估算

| 步骤 | 时间 |
|------|------|
| 创建目录结构 | 2 分钟 |
| 移动文件 | 5 分钟 |
| 创建项目 README | 15 分钟 |
| 更新路径引用 | 10 分钟 |
| 验证测试 | 10 分钟 |
| **总计** | **42 分钟** |

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 路径引用遗漏 | 脚本运行失败 | 全面搜索旧路径，逐一替换 |
| 定时任务失效 | 自动化中断 | 更新任务配置后验证执行 |
| 文档链接断裂 | 用户困惑 | 更新所有文档中的路径 |
| 导入语句错误 | Python 脚本失败 | 更新 sys.path 配置 |

---

## 验收标准

- [ ] 所有文件移动完成
- [ ] 所有脚本正常运行
- [ ] 定时任务正常执行
- [ ] 文档路径更新完成
- [ ] 项目 README 创建完成
- [ ] Git 提交并推送

---

*由 Claw 创建 | 2026-03-11 18:50*
