# Critic v5.0 - Universal Checklist Template

**Version:** 5.0-Universal  
**Date:** 2026-03-18  
**Auto-Critic:** `30-scripts-tools/auto-critic.py`

---

## Overview

Critic v5.0 now uses **universal checklists** that work for all task types, not just research.

### Key Changes

| Before (v5.0-Research) | After (v5.0-Universal) |
|------------------------|------------------------|
| Research-only checklists | 5 task types supported |
| Fixed 14 items | 6-12 items (type-dependent) |
| Statistical focus | Quality + usage focus |
| Manual invocation | Auto-invocation |

---

## Task Types

Auto-Critic automatically detects task type based on keywords:

| Type | Keywords | Post-Task Items |
|------|----------|-----------------|
| **tool** | tool, generator, search, auto-, script, utility, critic | 12 items |
| **research** | research, analysis, study, experiment, model, prediction, cnt- | 12 items |
| **documentation** | doc, readme, guide, manual, note, memory, summary, index | 12 items |
| **code** | optimize, refactor, fix, bug, performance, cleanup, hook | 12 items |
| **general** | (default) | 6 items |

---

## Checklist Templates

### Pre-Task (All Types - 6 Items)

1. 任务目标清晰可衡量 (有明确验收标准)
2. 任务必要性已论证 (为什么做这个)
3. 已有方案调研 (≥3 个参考/竞品/文献)
4. 风险评估完成 (技术/时间/依赖)
5. 资源需求明确 (时间/工具/权限)
6. 成功标准定义 (如何算完成)

### Mid-Task (All Types - 4 Items)

1. 进度正常 (每 30% 检查一次)
2. 无致命问题阻塞
3. 偏离目标已记录并调整
4. 关键决策已文档化

### Post-Task Common (All Types - 6 Items)

1. 致命问题 0 个
2. 严重问题≤2 个
3. 一般问题≤10 个
4. 验收标准 100% 满足
5. 代码/文档已提交 Git
6. 关键决策已记录到 MEMORY.md

### Post-Task: Tool Development (6 Additional Items)

7. 工具已创建并在实际工作流中使用
8. 使用次数≥1 次 (有证据证明)
9. 价值已量化 (时间节省/效率提升)
10. 使用案例已文档化
11. 工具文档完整 (README/使用说明)
12. 错误处理完善 (边界情况测试)

### Post-Task: Research Analysis (6 Additional Items)

7. 置信区间报告 (所有指标 95% CI)
8. 效应量报告 (Cohen's f² 或等价指标)
9. 统计功效分析 (Power≥0.8)
10. 多重共线性检验 (VIF<5)
11. 外部验证 (独立样本或交叉验证)
12. 可复现性 (代码 + 数据公开)

### Post-Task: Documentation (6 Additional Items)

7. 文档结构清晰 (目录/标题层级)
8. 关键信息前置 (执行摘要)
9. 示例/代码片段完整
10. 引用来源可验证
11. 格式统一 (命名/术语一致)
12. 长度适中 (<100 行或分页)

### Post-Task: Code Optimization (6 Additional Items)

7. 代码通过测试 (单元测试/集成测试)
8. 无安全漏洞 (敏感信息/注入风险)
9. 性能优化已验证 (基准测试)
10. 代码注释完整 (复杂逻辑说明)
11. 遵循代码规范 (PEP8/项目规范)
12. 无冗余代码 (DRY 原则)

---

## Usage

### Basic Usage

```bash
# Start phase
py 30-scripts-tools\auto-critic.py -t "Task-Name" -p start

# Mid phase
py 30-scripts-tools\auto-critic.py -t "Task-Name" -p mid

# Final phase
py 30-scripts-tools\auto-critic.py -t "Task-Name" -p final
```

### With Auto-Update

```bash
# Auto-update daily note
py 30-scripts-tools\auto-critic.py -t "Task-Name" -p final --auto-update-daily
```

### Examples

```bash
# Tool development
py 30-scripts-tools\auto-critic.py -t "Memory-Index-Generator" -p final

# Research analysis
py 30-scripts-tools\auto-critic.py -t "CNT-Conductivity-Analysis" -p final

# Documentation
py 30-scripts-tools\auto-critic.py -t "README-Update" -p final

# Code optimization
py 30-scripts-tools\auto-critic.py -t "Performance-Refactor" -p final

# General task
py 30-scripts-tools\auto-critic.py -t "Workspace-Cleanup" -p final
```

---

## Scoring

### Score Calculation

| Category | Weight | Description |
|----------|--------|-------------|
| Critical Issues | 40% | 0 fatal problems |
| Severe Issues | 20% | ≤2 severe problems |
| Minor Issues | 15% | ≤10 minor problems |
| Type-Specific | 15% | Varies by task type |
| Documentation | 10% | Git + MEMORY.md |

### Pass Thresholds

| Score | Status | Action |
|-------|--------|--------|
| ≥95 | ✅ Excellent | No action needed |
| 85-94 | ✅ Pass | Minor improvements optional |
| 70-84 | ⚠️ Borderline | Recommended improvements |
| <70 | ❌ Fail | Required rework |

---

## Output Files

### Review JSON

Location: `30-scripts-tools/critic-auto-{task-name}.json`

Structure:
```json
{
  "task": "Task-Name",
  "phase": "final",
  "task_type": "tool",
  "timestamp": "2026-03-18T17:00:00",
  "checklist": [
    {"item": "...", "checked": true, "notes": "..."}
  ],
  "score": 92,
  "status": "PASS"
}
```

### Daily Note Update

Auto-Critic appends review section to daily note when `--auto-update-daily` is used.

---

## Integration

### Workflow Integration

1. **Task Start** → Run `auto-critic.py -p start`
2. **Complete Checklist** → Mark items as checked
3. **Task Progress** → Run `auto-critic.py -p mid` at 30%, 60%, 90%
4. **Task Complete** → Run `auto-critic.py -p final`
5. **Save Review** → JSON saved to `30-scripts-tools/`
6. **Git Commit** → Include review file in commit
7. **Session Compress** → Run `post_session_compress.py --auto`

### Git Hook Integration

Future: Auto-invoke critic in git pre-commit hook for all commits.

---

## Migration Guide

### From v5.0-Research to v5.0-Universal

**Old (Research-Only):**
```bash
# Fixed 14-item checklist
# All items always shown
```

**New (Universal):**
```bash
# 6-12 items based on task type
# Automatic type detection
# Type-specific checklists
```

**No Breaking Changes:**
- Existing review files remain valid
- Command-line interface unchanged
- Output format compatible

---

## Best Practices

1. **Invoke Early** - Run at task start, not just end
2. **Be Honest** - Don't check items without evidence
3. **Document Everything** - Use notes field for context
4. **Quantify Value** - Time savings, efficiency gains
5. **Learn from Reviews** - Track patterns over time

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 5.0-Universal | 2026-03-18 | Universal checklists, 5 task types |
| 5.0-Research | 2026-03-11 | Research-focused checklists |
| 4.0 | 2026-03-10 | Auto-invocation |
| 3.0 | 2026-03-09 | Mid-task reviews |
| 2.0 | 2026-03-08 | Pre-task reviews |
| 1.0 | 2026-03-07 | Initial release |

---

**See Also:**
- `USER-004` - Critic requirement
- `AGENTS.md` - Workflow conventions
- `30-scripts-tools/auto-critic.py` - Implementation
