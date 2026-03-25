# 🔗 高级技能集成报告 (Batch 2)

**集成时间:** 2026-03-04 04:26  
**技能:** gh-issues, coding-agent, model-usage  
**状态:** ✅ 配置完成

---

## ✅ 已集成技能

### 1. gh-issues (GitHub 问题自动修复)

**状态:** ✅ 配置完成  
**配置:** `.openclaw/gh-issues-config.yaml`

**核心功能:**
- ✅ 自动获取 GitHub issues
- ✅ 派生子代理实现修复
- ✅ 自动创建 PR
- ✅ 监控 PR 评论并修复
- ✅ 支持 watch 模式持续监控

**使用示例:**
```bash
# 获取并修复 bug
/gh-issues owner/repo --label bug --limit 5

# 持续监控模式
/gh-issues owner/repo --watch --interval 5

# 仅处理 PR 评论
/gh-issues owner/repo --reviews-only

# 测试运行 (不执行)
/gh-issues owner/repo --dry-run
```

**依赖:**
- gh CLI (GitHub CLI)
- Git
- GH_TOKEN 环境变量

**安装:**
```bash
# Windows (winget)
winget install GitHub.cli

# macOS (brew)
brew install gh

# 认证
gh auth login
```

---

### 2. coding-agent (编码代理)

**状态:** ✅ 配置完成  
**配置:** `.openclaw/coding-agent-config.yaml`

**核心功能:**
- ✅ 委托编码任务给 Codex/Claude Code/Pi
- ✅ 支持 PTY 模式 (交互式 CLI)
- ✅ 自动创建临时 git 仓库
- ✅ 子代理并行处理
- ✅ 自动清理临时文件

**使用示例:**
```bash
# 使用 Codex 构建功能
codex exec "Build a REST API with FastAPI"

# 使用 Claude Code 审查代码
claude code "Review this PR for security issues"

# 后台运行
codex exec "Your prompt" &
```

**依赖:**
- Codex CLI 或 Claude Code CLI 或 Pi CLI
- Git
- bash (支持 PTY)

**安装:**
```bash
# Codex
npm install -g codex

# Claude Code
npm install -g @anthropic-ai/claude-code

# 或参考各自官方文档
```

---

### 3. model-usage (模型使用统计)

**状态:** ✅ 配置完成  
**配置:** `.openclaw/model-usage-config.yaml`

**核心功能:**
- ✅ 查看各模型使用成本
- ✅ 分析 token 消耗
- ✅ 按日/周/月统计
- ✅ 成本阈值告警
- ✅ 支持 CodexBar/ClaudeBar

**使用示例:**
```bash
# 查看当前模型
model-usage --mode current

# 查看所有模型统计
model-usage --mode all

# JSON 格式输出
model-usage --mode all --format json --pretty

# 按周统计
model-usage --mode all --group-by week
```

**依赖:**
- codexbar CLI (macOS) 或
- claudebar CLI (macOS)

**安装:**
```bash
# macOS (brew)
brew install steipete/tap/codexbar
brew install steipete/tap/claudebar

# Windows/Linux
# 需要手动配置数据源或使用 API
```

---

## 📊 完整技能清单 (18 个)

### 核心研究流 (4 个)
1. ✅ knowledge-graph
2. ✅ ai-research-os
3. ✅ knowledge-graph-builder
4. ✅ research-stats

### 数据收集与蒸馏 (3 个)
5. ✅ arxiv-daily
6. ✅ medium-watcher
7. ✅ memory-distiller

### 高级处理 (3 个)
8. ✅ citation-tracker
9. ✅ batch-processor
10. ✅ pdf-extractor

### 系统维护 (3 个)
11. ✅ github-sync
12. ✅ healthcheck
13. ✅ session-logs

### 信息增强 (2 个)
14. ✅ summarize
15. ✅ blogwatcher

### 开发与运维 (3 个) ← 新增
16. ✅ **gh-issues**
17. ✅ **coding-agent**
18. ✅ **model-usage**

---

## 🔄 工作流更新

### GitHub 开发工作流

```
GitHub Issues
    ↓
gh-issues (自动获取)
    ↓
coding-agent (子代理修复)
    ↓
自动创建 PR
    ↓
监控评论并修复
    ↓
合并 PR
```

### 成本监控工作流

```
Codex/Claude 使用
    ↓
model-usage (统计)
    ↓
成本分析
    ↓
阈值告警 (可选)
    ↓
优化模型选择
```

---

## ⚙️ 依赖安装

### gh-issues

```bash
# Windows (winget)
winget install GitHub.cli

# macOS (brew)
brew install gh

# 认证
gh auth login
```

### coding-agent

```bash
# Codex
npm install -g codex

# Claude Code
npm install -g @anthropic-ai/claude-code

# 或使用其他支持的代理
```

### model-usage

```bash
# macOS (brew)
brew install steipete/tap/codexbar
brew install steipete/tap/claudebar

# Windows/Linux
# 使用 API 或手动配置数据源
```

---

## 🚀 测试运行

### 测试 gh-issues

```bash
# 1. 检测当前仓库
gh repo view

# 2. 获取 issues (dry-run)
/gh-issues --label bug --limit 3 --dry-run

# 3. 实际运行 (需要确认)
/gh-issues --label bug --limit 3
```

### 测试 coding-agent

```bash
# 1. 创建临时目录
SCRATCH=$(mktemp -d) && cd $SCRATCH && git init

# 2. 测试 Codex
codex exec "Create a simple Python calculator"

# 3. 测试 Claude Code
claude code "Explain this code" < file.py
```

### 测试 model-usage

```bash
# 1. 查看当前模型
model-usage --mode current

# 2. 查看所有模型
model-usage --mode all --format json --pretty
```

---

## 📁 文件结构

```
D:\OpenClaw\workspace\
├── .openclaw/
│   ├── gh-issues-config.yaml      ← 新增
│   ├── coding-agent-config.yaml   ← 新增
│   ├── model-usage-config.yaml    ← 新增
│   └── ...
│
├── reports/
│   └── ADVANCED-SKILLS-BATCH2.md  ← 本文件
│
└── logs/
    └── coding-agent/              ← 日志目录
```

---

## ⚠️ 注意事项

### gh-issues

1. **GH_TOKEN:** 需要配置 GitHub Token
2. **Fork 模式:** 如果没有写权限，使用 fork
3. **Dry-run:** 首次运行建议使用 --dry-run

### coding-agent

1. **PTY 模式:** 必须使用 pty:true
2. **临时目录:** 自动创建和清理
3. **超时:** 设置合理的 timeout

### model-usage

1. **数据源:** 需要 codexbar/claudebar 或手动配置
2. **成本:** 基于 API 定价计算
3. **缓存:** 可选包含缓存成本

---

## 🎯 下一步

### 立即执行

1. **安装 gh CLI:**
   ```bash
   winget install GitHub.cli
   gh auth login
   ```

2. **安装 coding agent:**
   ```bash
   npm install -g codex
   # 或
   npm install -g @anthropic-ai/claude-code
   ```

3. **测试运行:**
   ```bash
   # gh-issues
   /gh-issues --dry-run
   
   # coding-agent
   codex exec "Hello"
   
   # model-usage
   model-usage --mode current
   ```

### 配置环境变量

```bash
# GitHub Token (可选，gh auth login 会自动配置)
$env:GH_TOKEN="ghp_..."

# Codex/Claude API Keys
$env:OPENAI_API_KEY="sk-..."
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

---

## 📝 参考文档

1. **gh-issues:** `skills/gh-issues/SKILL.md`
2. **coding-agent:** `skills/coding-agent/SKILL.md`
3. **model-usage:** `skills/model-usage/SKILL.md`
4. **集成报告:** `reports/ADVANCED-SKILLS-BATCH2.md`

---

*✅ 3 个高级技能集成完成！总计 18 个技能！* 🎉
