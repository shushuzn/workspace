# 工作区快速查找指南

**版本:** v2.0 (2026-03-11 重组版)  
**用途:** 5 秒内找到需要的文件

---

## 🚀 快速查找表

### 按功能查找

| 我要... | 去这里 | 关键文件 |
|---------|--------|----------|
| 📖 查看身份配置 | `./` | `SOUL.md`, `USER.md`, `AGENTS.md` |
| ❤️  心跳任务 | `./` | `HEARTBEAT.md` |
| 📝 查看记忆 | `13-memory/` | `MEMORY.md`, `YYYY-MM-DD.md` |
| 📚 查看文档 | `15-docs/` | 各种规范文档 |
| 🔬 AI/领域研究 | `06-research/` | AI 论文 + LIG/CNT 研究 |
| 🕸️ 知识图谱 | `07-knowledge/knowledge-graph/` | 图谱数据 |
| 📰 数据收集 | `08-collectors/` | arXiv/Medium/Reddit 等 |
| ✍️ 小说创作 | `09-creation/novels/` | 小说章节 |
| 📊 查看报告 | `10-data/reports/` | 各类报告 |
| 🃏 知识卡片 | `07-knowledge/knowledge-cards/` | 教学卡片 |
| 🛠️ 脚本工具 | `30-scripts/` | Python/PS 脚本 |
| 🔌 技能插件 | `31-skills/` | OpenClaw 技能 |
| 📦 归档 | `99-archive/` | 旧文件 |

---

## 📂 重组后结构

```
workspace/
├── 00-05/     → OpenClaw 核心配置
│   ├── 00-clawhub/           # ClawHub 技能管理
│   ├── 01-obsidian/          # Obsidian 配置
│   ├── 02-openclaw/          # OpenClaw 配置
│   ├── 03-config/            # 配置文件
│   ├── 04-plugins/           # 插件
│   └── 05-templates/         # 模板
│
├── 06-research/              # 🔥 研究项目 (整并)
│   ├── ai-research/          # AI 论文分析
│   └── research/             # LIG/CNT 等领域研究
│
├── 07-knowledge/             # 🔥 知识管理 (整并)
│   ├── knowledge-graph/      # 知识图谱
│   └── knowledge-cards/      # 教学卡片
│
├── 08-collectors/            # 🔥 数据收集器 (整并)
│   ├── arxiv/                # arXiv 论文收集
│   ├── medium/               # Medium 文章
│   ├── hackernews/           # HackerNews
│   ├── reddit/               # Reddit
│   ├── twitter/              # Twitter
│   └── obsidian-sync/        # Obsidian 同步
│
├── 09-creation/              # 🔥 创作内容 (整并)
│   ├── novels/               # 小说创作 ✍️
│   └── awesome-finance/      # 金融精选
│
├── 10-data/                  # 🔥 数据与报告 (整并)
│   ├── data/                 # 原始数据
│   ├── reports/              # 报告输出
│   ├── distilled-viewpoints/ # 提炼观点
│   ├── topics/               # 主题
│   └── tags/                 # 标签
│
├── 13-15/     → 知识与文档
│   ├── 13-memory/            # 记忆系统 ❤️
│   ├── 14-notes/             # 笔记
│   └── 15-docs/              # 文档规范 📚
│
├── 30-33/     → 工具与技能
│   ├── 30-scripts/           # 脚本工具 🛠️
│   ├── 31-skills/            # OpenClaw 技能
│   ├── 32-workflows/         # 工作流
│   └── 33-dashboard/         # 仪表板
│
├── 51-web/      → 网页
│
├── 91-92/     → 日志与测试
│   ├── 91-logs/              # 日志
│   └── 92-tests/             # 测试
│
└── 99-archive/  → 归档 (整并)
    ├── archive/              # 旧文件
    └── workspace/            # 工作区旧文件
```

---

## 📊 重组对比

### 重组前
- **目录数:** 35+ 个分散目录
- **编号:** 00-99 不连续
- **查找:** 需要记住具体编号
- **关联:** 相关项目分散多处

### 重组后
- **目录数:** 22 个 (减少 37%)
- **编号:** 按功能分组连续
- **查找:** 按功能分类，直观
- **关联:** 相关项目在同一组

---

## 🎯 快速入口

### 研究人员
```bash
06-research/          # 研究项目
├── ai-research/      # AI 论文
└── research/         # 领域研究 (LIG/CNT)

08-collectors/        # 数据收集
├── arxiv/            # 论文收集
└── medium/           # 文章收集
```

### 创作者
```bash
09-creation/          # 创作内容
└── novels/           # 小说创作
```

### 开发者
```bash
30-scripts/           # 脚本工具
├── maintain.ps1      # 维护脚本
└── QUICK-FIND-GUIDE.md

31-skills/            # OpenClaw 技能
```

### 数据分析师
```bash
10-data/              # 数据与报告
├── data/             # 原始数据
└── reports/          # 报告输出
```

---

## 📋 核心文件清单

### 根目录文件
| 文件 | 用途 | 大小 |
|------|------|------|
| `SOUL.md` | AI 身份配置 | 6 KB |
| `USER.md` | 用户信息 | 11 KB |
| `AGENTS.md` | 工作区规范 | 9 KB |
| `HEARTBEAT.md` | 心跳任务 | 12 KB |
| `TOOLS.md` | 工具配置 | 6 KB |
| `README.md` | 工作区说明 | 7 KB |
| `WORKSPACE-GUIDE.md` | 快速查找 | 4 KB |
| `WORKSPACE-INDEX.md` | 项目索引 | 5 KB |

### 关键目录统计
| 目录 | 文件数 | 大小 | 用途 |
|------|--------|------|------|
| `06-research/` | 1147 | 167 MB | 研究项目 |
| `08-collectors/` | 882 | 3 MB | 数据收集 |
| `30-scripts/` | 2885 | 31 MB | 脚本工具 |
| `13-memory/` | 64 | 0.4 MB | 记忆系统 |
| `99-archive/` | 438 | 37 MB | 归档 |

---

## 🔍 常用命令

### 工作区维护
```powershell
# 清理缓存
py 30-scripts/maintain.ps1 -CleanCache

# 健康检查
py 30-scripts/maintain.ps1 -HealthCheck

# 生成统计
py 30-scripts/maintain.ps1 -GenerateStats
```

### Git 操作
```bash
# 查看状态
git status

# 提交变更
git add -A
git commit -m "描述"
git push
```

### 快速搜索
```powershell
# 搜索文件
Get-ChildItem -Recurse -Filter "*.md" | Select-String "关键词"

# 查找大文件
Get-ChildItem -Recurse -File | Where-Object { $_.Length -gt 10MB }
```

---

## 📊 工作区统计

| 类别 | 目录数 | 文件数 | 总大小 |
|------|--------|--------|--------|
| OpenClaw 配置 (00-05) | 6 | ~50 | ~3 MB |
| 研究项目 (06) | 2 | 1147 | 167 MB |
| 知识管理 (07) | 2 | 49 | 0.4 MB |
| 数据收集 (08) | 6 | 882 | 3 MB |
| 创作内容 (09) | 2 | 228 | 1.3 MB |
| 数据报告 (10) | 5 | 130 | 2.5 MB |
| 记忆文档 (13-15) | 3 | 166 | 0.9 MB |
| 工具技能 (30-33) | 4 | 3012 | 32 MB |
| 日志测试 (91-92) | 2 | 24 | 0.3 MB |
| 归档 (99) | 2 | 438 | 37 MB |
| **总计** | **28** | **5900+** | **~247 MB** |

---

## 🔗 相关文档

- **30-scripts 导航:** `30-scripts/QUICK-FIND-GUIDE.md`
- **30-scripts 索引:** `30-scripts/PROJECT-INDEX.md`
- **工作区索引:** `WORKSPACE-INDEX.md`
- **工作区规范:** `AGENTS.md`
- **记忆系统:** `13-memory/MEMORY.md`

---

*最后更新：2026-03-11 v2.0 (重组版)*
