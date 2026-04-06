# Wikipedia Style Knowledge Base

维基百科风格知识库，支持 `[[wiki-link]]` 、分类、标签、前向/反向链接追踪。**用 Obsidian 作为编辑器**。

## 目录结构

```
wikipedia/
├── wiki.mjs          # 主CLI工具
├── index.json        # 条目索引（自动生成）
├── index.html        # 百科首页（自动生成）
├── articles/         # 条目Markdown文件（按知识点文件夹组织）
│   ├── math/
│   │   ├── braid-group/           # 辫群
│   │   │   ├── braid-group.md         # 原始笔记
│   │   │   ├── [name]-20260406.md    # 知识点版本化快照
│   │   │   ├── 01-辫群.md             # 视频文案
│   │   │   ├── 01-辫群.mp3            # 语音
│   │   │   ├── 01-辫群.mp4            # 视频
│   │   │   └── fig-01-braid-group.png # 配图
│   │   └── burau-lyapunov/        # Burau-Lyapunov指数
│   │       ├── burau-lyapunov.md
│   │       ├── [name]-20260406.md
│   │       ├── 02-Burau-Lyapunov指数.md
│   │       ├── 02-Burau-Lyapunov指数.mp3
│   │       ├── 02-Burau-Lyapunov指数.mp4
│   │       └── fig-04-le-flow.png
│   ├── security/
│   │   ├── iam-cloud/
│   │   │   ├── iam-cloud.md
│   │   │   ├── [name]-20260406.md
│   │   │   ├── 04-IAM云身份与访问管理.md
│   │   │   ├── 04-IAM云身份与访问管理.mp3
│   │   │   ├── 04-IAM云身份与访问管理.mp4
│   │   │   └── fig-02-iam-model.png
│   │   └── iam-privilege-escalation/
│   │       ├── iam-privilege-escalation.md
│   │       ├── [name]-20260406.md
│   │       ├── 03-IAM特权升级.md
│   │       ├── 03-IAM特权升级.mp3
│   │       ├── 03-IAM特权升级.mp4
│   │       └── fig-03-attack-path.png
│   └── ai/
│       └── outofdomain-stress-test/
│           ├── outofdomain-stress-test.md
│           ├── [name]-20260406.md
│           ├── 05-Out-of-Domain-Stress-Test论文解读.md
│           ├── 05-Out-of-Domain-Stress-Test论文解读.mp3
│           └── 05-Out-of-Domain-Stress-Test论文解读.mp4
├── video/                # 视频生产流水线源码
│   ├── draw_braid.py     # 配图生成
│   ├── make_script.py    # 阅读文案提取
│   ├── generate_speech.py # 语音合成
│   └── make_video.py     # 视频合成
└── categories/           # 分类目录（预留）
```

## 快速开始

```bash
# 创建条目
node wiki.mjs create "人工智能" --category AI --tags 大模型,机器学习

# 搜索（wiki原生）
node wiki.mjs search AI

# 用 Obsidian 编辑条目
node wiki.mjs edit 人工智能

# 通过 Obsidian CLI 搜索
node wiki.mjs obsidian search query=AI

# 启动 HTTP API
node wiki.mjs server --port 3000
```

## 命令参考

| 命令 | 说明 |
|------|------|
| `create` | 创建条目，支持 `--category` `--tags` |
| `ingest <url\|path>` | 抓取网页或PDF创建条目，`--analyze` 用LLM分析 |
| `view <title\|id>` | 格式化阅读条目内容（CLI预览） |
| `search <query>` | 搜索标题/标签/分类 |
| `list [category]` | 列出条目，按分类统计 |
| `link <id1> <id2>` | 创建两条目间的关联 |
| `backlinks <title>` | 查询引用某条目的所有条目 |
| `orphan` | 列出无其他条目引用的孤立条目 |
| `delete <id>` | 删除条目 |
| `edit <title-or-id>` | 用 Obsidian 编辑条目 |
| `sync` | 从磁盘扫描重建索引，检测断链 |
| `linkcheck [--fix]` | 检测断链，`--fix` 自动修复 |
| `category-rename <old> <new>` | 批量重命名分类 |
| `import <dir>` | 批量导入 `.md` 文件，`--category` 指定默认分类 |
| `server [--port N]` | 启动 HTTP REST API |
| `obsidian <cmd> [args...]` | 直接调用 Obsidian CLI |

## Obsidian CLI 封装

所有 Obsidian CLI 命令均可通过 `wiki.mjs obsidian` 调用，自动绑定 vault：

```bash
# 搜索
node wiki.mjs obsidian search query=AI

# 查看标签
node wiki.mjs obsidian tags sort=count counts

# 反向链接
node wiki.mjs obsidian backlinks file="AI大模型"

# 阅读文件内容
node wiki.mjs obsidian read file="AI大模型"

# 孤立文件
node wiki.mjs obsidian orphans total

# 属性查询
node wiki.mjs obsidian properties file="AI大模型"

# 任务
node wiki.mjs obsidian tasks todo

# 每日笔记
node wiki.mjs obsidian daily:read
```

完整命令列表：`obsidian vault="3cb50ee5e304a7ea" --help`

## HTTP API

启动服务后可用以下接口：

```
GET  /articles           列出所有条目
GET  /articles/:id      阅读单个条目
GET  /search?q=<query>  搜索
POST /articles           创建条目（JSON body: title, content, category, tags）
```

## 标签格式

条目内使用 `[[wiki-link]]` 创建条目间链接，自动追踪反向链接。

```markdown
这是一段关于[[人工智能]]的内容。
```

## 条目结构

```yaml
---
id:人工智能-1234567890
title:人工智能
category:AI
tags:[大模型, 机器学习]
references:[]
---

# 人工智能

正文内容...
```

## 维护命令

```bash
# 重建索引+断链检测
node wiki.mjs sync

# 清理孤立条目
node wiki.mjs orphan
```
