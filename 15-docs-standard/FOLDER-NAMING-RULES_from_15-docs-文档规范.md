# 工作空间文件夹命名规范 v2.0

**版本:** v2.0  
**更新日期:** 2026-03-11  
**适用范围:** `D:\OpenClaw\workspace` 所有文件夹

---

## 📁 一级文件夹命名规则

### ✅ 数字前缀规范

所有业务文件夹必须使用数字前缀，按功能分类：

| 前缀范围 | 类别 | 示例 |
|----------|------|------|
| `00-09` | 核心配置 | `00-clawhub/`, `03-config/`, `04-plugins/` |
| `10-19` | 知识库 | `11-research/`, `13-memory/`, `15-docs/` |
| `20-29` | 数据与报告 | `21-reports/`, `22-distilled-viewpoints/` |
| `30-39` | 工具与脚本 | `30-scripts/`, `31-skills/`, `32-workflows/` |
| `40-49` | 数据采集器 | `40-arxiv/`, `41-medium/`, `42-hackernews/` |
| `50-59` | 专题项目 | `50-novels/`, `51-web/` |
| `60-69` | 知识卡片 | `60-knowledge-cards/` |
| `90-99` | 归档与测试 | `90-archive/`, `92-tests/`, `99-workspace-archive/` |

### ❌ 禁止的命名

- ❌ 无数字前缀（如 `config/`, `docs/`, `skills/`）
- ❌ 中文字符
- ❌ 大写字母开头（如 `Medium/` → `41-medium/`）
- ❌ 下划线分隔（使用连字符 `-`）

### ✅ 允许的例外

| 文件夹 | 原因 |
|--------|------|
| `.clawhub/` | 隐藏配置文件夹 |
| `.obsidian/` | Obsidian 系统文件夹 |
| `.openclaw/` | OpenClaw 系统文件夹 |
| `.pytest_cache/` | Python 测试缓存 |

---

## 📁 二级文件夹规范

### 40-arxiv/ 结构

```
40-arxiv/
├── Archive/              # 归档（按月）
├── config/               # 配置文件
├── data/                 # 数据文件 (JSON)
├── daily/                # 每日论文 (YYYY-MM-DD)
├── lig/                  # LIG 领域特定
│   └── risk/             # LIG 风险预警
├── lig-outreach/         # LIG 科普笔记
└── scripts/              # 脚本文件
```

### 30-scripts/ 结构

```
30-scripts/
├── arxiv-daily/          # arXiv 收集器
├── domain_ranker_v2.py   # 段位评估
├── lig-*.py              # LIG 相关脚本
├── medium-watcher/       # Medium 监控
└── tools/                # 工具脚本
```

### 13-memory/ 结构

```
13-memory/
├── MEMORY.md             # 长期记忆
├── heartbeat-state.json  # Heartbeat 状态
├── YYYY-MM-DD.md         # 每日笔记
└── intentkit-*.md        # 意图工程研究
```

---

## 🔄 迁移规则

### 无主文件夹处理

| 原名称 | 目标文件夹 | 说明 |
|--------|-----------|------|
| `config/` | `03-config/` | 合并 |
| `docs/` | `15-docs/` | 合并 |
| `skills/` | `31-skills/` | 合并 |
| `tools/` | `30-scripts/` | 合并 |
| `memory/` | `13-memory/` | 合并 |
| `n8n/` | `99-workspace-archive/` | 已弃用 (CPU 过热) |
| `output/` | `21-reports/` | 报告输出 |
| `Medium/` | `41-medium/` | 统一小写 |
| `formula_dataset/` | `92-tests/` | 测试数据 |
| `handwritten_formula_dataset/` | `92-tests/` | 测试数据 |

### 命名冲突处理

1. **内容合并:** 如果目标文件夹已存在，合并内容
2. **文件去重:** 相同文件保留最新版本
3. **Git 追踪:** 使用 `git mv` 保持历史记录

---

## 🧹 清理规则

### 定期清理

| 类型 | 频率 | 操作 |
|------|------|------|
| `__pycache__/` | 每次 Git 前 | 删除 |
| `*.pyc` | 每次 Git 前 | 删除 |
| `.pytest_cache/` | 每月 | 清理 |
| `99-workspace-archive/` | 每季度 | 压缩归档 |

### Git 前检查

```bash
# 检查不规范命名
ls | grep -P '^[a-z]' | grep -v '^\.'

# 检查临时文件夹
ls | grep -E '(temp|migr|backup|old)'

# 清理 Python 缓存
find . -name "__pycache__" -type d -exec rm -rf {} +
```

---

## ✅ 当前状态 (2026-03-11)

### 一级文件夹清单

```
.clawhub/                  ✅ 隐藏配置
.obsidian/                 ✅ Obsidian 系统
.openclaw/                 ✅ OpenClaw 系统
.pytest_cache/             ✅ Python 测试缓存
00-clawhub/                ✅ 核心配置
01-obsidian/               ✅ Obsidian 配置
02-openclaw/               ✅ OpenClaw 配置
03-config/                 ✅ 系统配置
04-plugins/                ✅ 插件配置
05-templates/              ✅ 模板
10-ai-research/            ✅ AI 研究
11-research/               ✅ 研究笔记
12-knowledge-graph/        ✅ 知识图谱
13-memory/                 ✅ 记忆系统
14-notes/                  ✅ 临时笔记
15-docs/                   ✅ 文档
20-data/                   ✅ 数据
21-reports/                ✅ 报告
22-distilled-viewpoints/   ✅ 蒸馏观点
23-topics/                 ✅ 主题
24-tags/                   ✅ 标签
30-scripts/                ✅ 脚本工具
31-skills/                 ✅ 技能
32-workflows/              ✅ 工作流
33-dashboard/              ✅ 仪表板
40-arxiv/                  ✅ arXiv 收集器
41-medium/                 ✅ Medium 监控
42-hackernews/             ✅ HackerNews
43-reddit/                 ✅ Reddit
44-twitter/                ✅ Twitter
45-obsidian-sync/          ✅ Obsidian 同步
50-awesome-finance/        ✅ 金融项目
50-novels/                 ✅ 小说创作
51-web/                    ✅ Web 项目
60-knowledge-cards/        ✅ 知识卡片
90-archive/                ✅ 归档
91-logs/                   ✅ 日志
92-tests/                  ✅ 测试数据
99-workspace-archive/      ✅ 废弃项目
```

**已迁移文件夹:**
- ✅ `config/` → `03-config/`
- ✅ `docs/` → `15-docs/`
- ✅ `skills/` → `31-skills/`
- ✅ `tools/` → `30-scripts/`
- ✅ `memory/` → `13-memory/`
- ✅ `n8n/` → `99-workspace-archive/`
- ✅ `output/` → `21-reports/`
- ✅ `Medium/` → `41-medium/`
- ✅ `formula_dataset/` → `92-tests/`
- ✅ `handwritten_formula_dataset/` → `92-tests/`

---

## 🔧 维护脚本

### 检查脚本

```bash
# 检查不规范命名
py 30-scripts/check-workspace-naming.py

# 自动修复
py 30-scripts/fix-folder-naming.py --dry-run
```

### 自动化清理

```bash
# 每周清理 (Windows Task Scheduler)
py 30-scripts/weekly-cleanup.py
```

---

**违规处理:** 发现不规范命名立即整改，Git 提交前必须检查。

**更新日志:**
- v2.0 (2026-03-11): 添加完整一级文件夹清单 + 迁移规则
- v1.0 (2026-03-11): 初始版本 (40-arxiv 规范)
