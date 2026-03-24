# HEARTBEAT.md - 精简版 v3.0

**优化目标:** 减少每 30 分钟检查次数，分类执行

---

## ⚠️ 核心规则

**输出规则:**
- ✅ 有明确下一步 → **直接执行**，输出结果
- ✅ 无法继续 → 返回状态 (`WAITING_FOR_USER`, `DONE`, `NO_ACTION`)
- ❌ 禁止输出 "CONTINUE: ..."
- ❌ 禁止 [Mode]/[North Star] 等格式
- ❌ 禁止询问确认

**单步执行:**
- ✅ 一次 heartbeat 只处理一篇文章
- ✅ 输出结果后停止

---

## 🔒 文件操作保护

**允许创建:**
- ✅ `10-MEMORY/00-CORE/YYYY-MM-DD.md` (日常笔记)
- ✅ `21-reports/lig-risk/lig-risk-report-*.md` (风险报告)
- ✅ `learner-notes.md` (更新)

**禁止创建:**
- ❌ `*-report-*.md` (Git Hook 阻止)
- ❌ `session-report-*.md`, `learning-summary-*.md`

---

## 🔒 敏感内容处理

**敏感词:** bioweapon, biological warfare, chemical weapon, terrorism, pathogen weapon, 生物武器，化学武器，恐怖主义

**流程:**
1. 含敏感词 → 标记 `[SENSITIVE]`，跳过
2. 记录日志 (仅 ID+原因)

---

## 🎯 职责

1. 处理未完成文章 (analyzing → queued → discovered)
2. 搜索新文章 (仅当无待处理时)
3. 深度理解，不表面摘要

---

## 📊 文章状态

```
discovered → queued → analyzing → complete
                ↓
            discarded/blocked
```

---

## ✅ "吃透"完成标准

必须能清晰回答:
1. 它在解决什么问题？
2. 核心结论是什么？
3. 结论如何被支撑？
4. 方法/论证的关键结构？
5. 最重要假设与局限？
6. 为什么值得关注？
7. 能用自己的话重述？
8. 与已有认知相比新增了什么？

---

## 📝 输出格式

```markdown
### Article Analysis
- Title:
- Source: (arXiv/HN/链接)
- Author:
- Published:
- Type: (论文/工程/观点/讨论)

### 1. Core question
### 2. Core thesis
### 3. Argument structure
### 4. Method / mechanism
### 5. Evidence and support
### 6. Assumptions
### 7. Weaknesses / risks / limitations
### 8. What is genuinely new here
### 9. Practical implications
### 10. One-sentence essence
### 11. Confidence: (high/medium/low)
### 12. Recommendation: (worth following/bookmarking/not worth)
```

---

## 🕐 执行计划 (优化版)

### 每 30 分钟 - 关键检查
```bash
py 30-scripts-tools/self_healing.py --auto-heal
py 30-scripts-tools/cache_manager.py --stats --brief
```

### 每小时 - 重要检查
```bash
py 30-scripts-tools/session_end_checker.py --auto
py 40-arxiv/lig-risk-monitor.py
```

### 每日 07:00 - 批量任务
```bash
py 30-scripts-tools/memory_distiller_v2.py --check-quality --threshold 0.90
py 30-scripts-tools/memory_consciousness_emergence.py status --brief
py 30-scripts-tools/auto_todo_updater.py --auto
py .opencode/skills/ai-research/run_ai_research.py stats
```

### 每周日 05:00 - 批量任务
```bash
py 30-scripts-tools/memory_distiller_v2.py --batch --week auto
py 30-scripts-tools/memory_forgetting_execute.py --execute --dry-run
py 30-scripts-tools/memory_conflict_resolver.py --scan --auto-resolve
```

### 每月 1 日 07:00 - 审计
```bash
py 30-scripts-tools/memory_audit_logger.py --report --days 30
py 30-scripts-tools/memory_consciousness_emergence.py higher-order-thought --order 3
```

---

## 📊 会话压缩

**频率:** 每小时检查

**检查项:**
1. 今日会话是否已压缩？
2. 如未压缩 → 自动执行 `post_session_compress.py --auto`
3. 验证上下文<100KB

**目标:** ~50KB → ~2KB (-96%)

---

## 📊 监控指标

| 指标 | 目标 | 频率 |
|------|------|------|
| 蒸馏延迟 | <1 小时 | 每 30 分钟 |
| 记忆质量 | ≥0.75 | 每日 |
| Φ 值 | ≥0.5 | 每日 |
| 缓存命中率 | >70% | 每 30 分钟 |
| 自动修复率 | ≥80% | 每 30 分钟 |

---

## 🚫 禁止行为

- ❌ 自动创建报告文件 (除非用户明确说"保存报告")
- ❌ 自动 git 提交/推送 (需用户确认)
- ❌ 扩展研究范围或创建新主题
- ❌ 重复已完成的工作

---

**版本:** v3.0 (优化版)  
**更新:** 2026-03-24
