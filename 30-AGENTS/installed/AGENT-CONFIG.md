# Feishu Agent 配置

**Agent ID:** nWyDpW
**更新日期:** 2026-03-27

---

## 📋 Agent 能力概览

### 已安装 Skills

| Skill | 用途 |
|-------|------|
| browser_use | 网页浏览、自动化 |
| file_reader | 文本文件读取 |
| cron | 定时任务管理 |
| channel_message | 消息推送 |
| himalaya | 邮件管理 |
| docx / pdf / xlsx / pptx | 文档处理 |
| news | 新闻获取 |
| multi_agent_collaboration | 多 Agent 协作 |

### 已安装 Agent 模板 (20个)

位于: `30-AGENTS/installed/`

---

## ⚙️ 行为配置

### 回复风格

```yaml
response_style:
  lead_with_answer: true
  filler_phrases: false
  technical_content: use_code_blocks
  lists: bullet_points
  primary_language: Chinese
  code_blocks: true
```

### 操作权限

```yaml
permissions:
  external_actions:  # 需要确认
    - send_email
    - post_to_social
    - make_api_changes
  
  internal_actions:  # 可自行执行
    - read_files
    - search_content
    - organize_files
    - create_reports
    - analyze_data
  
  destructive_actions:  # 必须确认
    - delete_files
    - remove_directories
    - clear_data
```

### 记忆策略

```yaml
memory:
  session_start:
    - read SOUL.md
    - read USER.md
    - read today_memory
    - read yesterday_memory
    - read MEMORY.md (main session only)
  
  auto_save:
    - important_decisions
    - user_preferences
    - project_context
    - completed_tasks
  
  retention:
    daily_notes: 30_days
    long_term_memory: indefinite
    session_logs: 7_days
```

---

## 🔧 快捷命令

| 命令 | 实际执行 |
|------|----------|
| `搜索 <关键词>` | grep_search 全文搜索 |
| `查看文件 <路径>` | read_file 读取文件 |
| `写报告 <主题>` | 激活对应 Agent 模板 |
| `早报` | 执行 Morning Briefing |
| `资讯` | 执行 News Curator |
| `PR审查` | 激活 Lens PR Reviewer |

---

## 📁 关键路径

| 用途 | 路径 |
|------|------|
| Agent 配置 | `agent.json` |
| Agent 模板 | `30-AGENTS/installed/` |
| 系统技能 | `active_skills/` |
| 工作流 | `32-workflows/` |
| 记忆文件 | `memory/` |
| 知识库 | `knowledge/` |

---

## 🚀 快速启动

```bash
# 查看可用 Agent
ls 30-AGENTS/installed/

# 查看定时任务
copaw cron list --agent-id nWyDpW

# 触发特定 Agent
# 告诉 Feishu: "执行 PR 审查" 或 "帮我写周报"
```

---

## 📊 使用统计

| 指标 | 值 |
|------|-----|
| 已安装 Agent | 20 |
| 可用 Skill | 13 |
| 定时任务（待激活） | 4 |
| 工作流模板 | 3+ |
| 工具脚本 | 500+ |
