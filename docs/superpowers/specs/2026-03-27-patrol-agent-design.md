# Patrol Agent — 自主循环工作设计文档

## 概述

一个永不停歇的 AI agent 进程，持续巡逻 workspace：

1. 执行待办计划
2. 检查并修复错误
3. 优化代码
4. 深度研究，产生新 plan
5. 周而复始，直到被手动停止

---

## 核心架构

```
┌─────────────────────────────────────────────────┐
│           patrol-agent (Ralph 循环)              │
│                                                 │
│  ┌─────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Scanner │→ │ Planner  │→ │ Executor     │  │
│  │ 扫描现状 │  │ 决策做什么│  │ 自主执行      │  │
│  └─────────┘  └──────────┘  └──────────────┘  │
│       ↑                                    │    │
│       └─────────── State ────────────────┘    │
│                                                 │
│  ~/.omc/patrol-state.json                      │
│  docs/superpowers/plans/                       │
└─────────────────────────────────────────────────┘
```

**巡逻节奏（三层）**：

| 优先级 | 内容 | 频率 |
|--------|------|------|
| 高 | lint 检查、plan 执行、test 修复 | 每轮（~5分钟） |
| 中 | 代码优化扫描（dead code、重复、命名） | 每 10 轮 |
| 低 | 深度研究 → 产生新 plan | 每 50 轮 |

---

## 巡逻循环

每轮循环按顺序执行：

```
WHILE running:
  plan = get_next_pending_plan()
  IF plan:
    execute(plan)          # 自主决策执行到底
    mark_done(plan)
    log("✓ Executed: " + plan.name)
    CONTINUE

  IF has_lint_errors():
    fix_lint_errors()
    log("✓ Fixed lint errors")
    CONTINUE

  IF has_test_failures():
    fix_tests()
    log("✓ Fixed tests")
    CONTINUE

  IF loop_count % 10 == 0 AND has_optimization_opportunities():
    improve_code()
    log("✓ Improved: " + improvement)
    CONTINUE

  IF loop_count % 50 == 0:
    research_results = deep_research()
    FOR idea IN research_results:
      IF idea.confidence > 0.7:
        write_plan(idea)
        log("🆕 New plan from research: " + idea.title)

  sleep(interval)
  loop_count++
```

---

## 研究驱动的 Plan 生成

### 研究来源（可配置）

每 50 轮触发一次，按优先级依次搜索：

```
research_queries = [
  { q: "agent arena game implementation github trending", sources: ["github", "hackernews"] },
  { q: "LLM multi-agent roundtable discussion", sources: ["arxiv", "github"] },
  { q: "cross-project identity system patterns", sources: ["github", "arxiv"] },
  { q: "autonomous coding agent architecture", sources: ["arxiv", "github"] },
]
```

**数据来源**：
- GitHub Trending（按语言/Topic）
- arXiv cs.AI、cs.CL 最新论文
- Hacker News / lobste.rs

### 过滤与匹配

研究结果只有满足以下条件才生成 plan：

1. 与 workspace 已有项目直接相关（agent-arena、ai-roundtable、star-forge-web）
2. 不是重复已有 plan（hash 对比）
3. 置信度 > 0.7

### 研究输出格式

每个新 plan 附带研究元数据：

```markdown
## Plan: [标题]

**研究来源**: [URL]
**研究摘要**: [1-2 句话描述核心发现]
**为什么适合 workspace**: [与现有项目的关联]
**置信度**: 0.85
**实施建议**: [初步方案]
**generated_at**: 2026-03-27T08:00:00Z
```

---

## 错误恢复

```
TRY:
  execute(task)
CATCH error:
  IF retry_count < 2:
    retry_count++
    log("Retry #{retry_count} for: " + task.name)
    execute(task)   # 重试
  ELSE:
    log("⚠️ Skipped permanently: " + task.name + " | Error: " + error.message)
    mark_skipped(task, error)
    CONTINUE   # 不停机，继续下一个
```

- **最多 retry 2 次**，第 3 次失败则 skip 并记录
- **绝不 panic 停机**，循环继续运行
- 失败信息写入 `patrol-state.json` 供后续查看

---

## 防重复机制（Hash 追踪）

每次执行前计算内容 hash，已做过的跳过：

```json
// ~/.omc/patrol-state.json
{
  "last_patrol": "2026-03-27T08:00:00Z",
  "loop_count": 142,
  "completed_actions": [
    {
      "type": "plan",
      "id": "cross-project-identity-phase1",
      "hash": "sha256:abc123...",
      "executed_at": "2026-03-27T07:00:00Z"
    },
    {
      "type": "improvement",
      "file": "src/components/BattleResult.svelte",
      "hash": "sha256:def456...",
      "executed_at": "2026-03-27T07:05:00Z"
    }
  ],
  "skipped": [
    { "type": "plan", "id": "...", "reason": "failed 3x", "at": "..." }
  ],
  "research_topics": [
    { "topic": "agent arena game", "searched_at": "...", "ideas_generated": 2 }
  ]
}
```

**防重规则**：

| 操作 | 检查方式 |
|------|---------|
| Plan 执行 | 查 `completed_actions` 中是否有相同 `id` + `hash` |
| 文件修改 | 对比 git HEAD hash，已一致则跳过 |
| 新 plan 生成 | 对比 `research_topics` 中相同 topic 下已生成的 ideas |
| Loop 重启 | 从 `loop_count` 断点继续，不从头开始 |

---

## 冲突检测

改文件前检查 git 状态：

```
FOR file IN files_to_modify:
  status = git status --short {file}

  IF status starts with "M ":    # Working tree modified
    log("⚠️  External change detected for: " + file)
    git checkout -b patrol/auto-{timestamp}
    write changes to branch
    log("⚠️  Created branch for conflicting changes, manual merge needed")
    BREAK   # 本轮跳过，等你 merge

  ELSE IF status starts with "M":  # Staged change (ours)
    write changes   # 安全，直接写

  ELSE:
    write changes   # 干净文件，直接写
```

**核心原则**：如果文件在你手动改过（未 commit），agent 自动开分支写自己的改动，**不覆盖你的东西**，等你手动 merge。

---

## 状态管理

### 状态文件

`~/.omc/patrol-state.json`

- **loop_count**：当前轮次（重启后从断点继续）
- **completed_actions**：已完成的动作 hash 记录
- **skipped**：跳过的任务及原因
- **research_topics**：研究历史（避免重复研究）
- **patrol_log**：最近 N 条巡逻记录

### Plans 目录

`docs/superpowers/plans/`

每个 plan 文件包含状态字段：

```markdown
---
status: pending | in_progress | done | skipped
retry_count: 0
hash: sha256:...
generated_from: research | manual
source_url: (如果是研究来源)
created_at: 2026-03-27T...
updated_at: 2026-03-27T...
---

# Plan: [标题]

[内容]
```

### Loop 重启恢复

启动时读取 `patrol-state.json`：

1. 从 `loop_count` 继续（不从头开始）
2. 检查 `completed_actions`，跳过已做过的
3. 对 `plans/` 目录按 `updated_at` 排序，最旧的先做

---

## 自主边界（Guardrails）

### 可以自主决定

- 读/写/修改 workspace 任何文件
- 在 `docs/superpowers/plans/` 创建新 plan
- 执行 lint/stylelint 检查并修复
- 执行测试并修复失败用例
- 代码优化（dead code 删除、重复合并、命名改进）
- Git commit + push（message 格式：`patrol: {action} — {detail}`）
- Web research（搜索 GitHub、arXiv、Hacker News）

### 不能自主决定

- **删除文件**（只能 retire/log，向你报告）
- **调用外部 API**（除已有的 minimax API）
- **修改 `~/.omc/` 之外的系统文件**

### 外部冲突处理

```
IF external_change_detected:
  create_branch("patrol/auto-{timestamp}")
  log("⚠️  Branched for conflicting changes, waiting for manual merge")
  NOTIFY you via patrol_log
  CONTINUE (skip this task, do next one)
```

---

## 输出报告

每轮循环结束后，通过 **patrol log** 记录：

```
[2026-03-27 08:05:00] Loop #143
  ✓ Executed: cross-project-identity-phase1
  ✓ Fixed 2 lint errors in agent-arena/src/
  ✓ Improved: removed dead code in Gacha.svelte
  🆕 New plan from research: "LLM Memory System for Agents" (source: arxiv.org/abs/...)
  ──
  Next: Loop #144 in ~5min
  Pending plans: 3
  Research cooldown: 47 loops
```

**有事做才报告**，无事发生时静默（不打扰你）。

---

## 启动与停止

### 启动

```bash
cd D:/OpenClaw/workspace
claude --riot "patrol"
# 或者用 OMC
/ralph --patrol
```

### 停止

```bash
# 在 agent 运行时输入
stop
# 或者
Ctrl+C
```

### 后台运行

```bash
nohup claude --patrol > ~/.omc/patrol.log 2>&1 &
```

---

## 实施计划

### Phase 1: 核心循环（1天）
- Ralph 循环 + 三层巡逻节奏
- 状态读写（patrol-state.json）
- Plan 执行 + done 标记
- lint 检查 + 修复

### Phase 2: 研究能力（1天）
- Web research 集成（GitHub、arXiv 搜索）
- Plan 生成 + 置信度过滤
- 研究去重

### Phase 3: 防错机制（半天）
- Hash 追踪 + 重复防护
- 冲突检测 + 自动分支
- 错误恢复 + retry 逻辑

### Phase 4: 调优（半天）
- 日志输出格式优化
- 巡逻节奏调参
- 与飞书/telegram 日志集成（可选）
