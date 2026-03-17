# 07 - Git 提交工作流

**版本:** v4.0  
**创建时间:** 2026-03-05 16:40  
**更新时间:** 2026-03-05 17:15  
**自动化:** 每日 05:00 自动运行  
**层次:** 支持工作流

---

## 📋 工作流说明

### 功能
- 自动添加新文件
- 自动提交更改
- 自动推送到 GitHub
- 带 Emoji 的提交信息

### 输入
- 当日生成的所有文件

### 输出
- Git 提交
- GitHub 推送

---

## 🚀 使用方法

### 单次运行

```bash
cd D:\OpenClaw\workspace
py scripts/materials/auto-git-commit.py
```

---

## 📁 文件结构

```
workflows/git-commit/
├── README.md              # 本文件
├── config.yaml            # Git 配置
├── run.sh                 # 运行脚本
└── logs/                  # 日志目录
    └── git.log
```

---

## ⚙️ 配置选项

### config.yaml

```yaml
# Git 配置
git:
  # 仓库路径
  repo_path: D:\\OpenClaw\\workspace
  
  # 提交信息前缀
  commit_prefix: "🤖 Automated"
  
  # 自动推送
  auto_push: true
  
  # 远程仓库
  remote: origin
  branch: master
```

---

## 📊 提交信息格式

### 标准格式

```
🤖 Automated research update YYYY-MM-DD

- Collected {N} papers
- Generated report: AUTO-REPORT-YYYY-MM-DD.md
- Updated knowledge graph: {N} entities, {N} relations
```

### 示例

```
🤖 Automated research update 2026-03-05

- Collected 127 papers
- Generated report: AUTO-RESEARCH-REPORT-2026-03-05.md
- Updated knowledge graph: 100 entities, 250 relations
```

---

## 🔧 故障排除

### 常见问题

**1. Git 提交失败**

症状：`git commit failed`

解决：
```bash
# 检查 Git 配置
git config --list

# 检查仓库状态
git status

# 手动提交
git add -A
git commit -m "Manual commit"
```

**2. Git 推送失败**

症状：`git push failed`

解决：
```bash
# 检查网络连接
ping github.com

# 检查远程仓库
git remote -v

# 手动推送
git push origin master
```

---

*最后更新：2026-03-05 16:40*  
*工作流版本：v2.0*
