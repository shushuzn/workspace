# HEARTBEAT.md - 精简版 v2.0

**大小目标:** <5KB (当前 33KB → 目标 5KB)  
**原则:** 只保留核心规则，删除冗余细节

---

## ⚠️ 核心规则 (每次必读)

**输出规则:**
- ✅ 有明确下一步 → **直接执行**，输出结果
- ✅ 无法继续 → 返回状态 (`WAITING_FOR_USER`, `DONE`, `NO_ACTION`)
- ❌ 禁止输出 "CONTINUE: ..."
- ❌ 禁止 [Mode]/[North Star] 等格式
- ❌ 禁止询问确认

**单步执行:**
- ✅ 一次 heartbeat 只处理一篇文章
- ✅ 输出结果后停止
- ❌ 不连续处理多篇

---

## 🔒 文件操作保护 (最高优先级)

**允许创建:**
- ✅ `13-memory/YYYY-MM-DD.md` (日常笔记)
- ✅ `21-reports/lig-risk/lig-risk-report-*.md` (风险报告)
- ✅ `learner-notes.md` (更新)

**禁止创建:**
- ❌ `*-report-*.md` (全局，Git Hook 阻止)
- ❌ `session-report-*.md`, `learning-summary-*.md`
- ❌ `memory-update-*.md`, `workspace-comparison-*.md`

**工具使用:**
```bash
# 文件操作前检查
py 30-scripts-tools/pre_file_operation_hook.py --before-create <file>

# 对比工具 (默认控制台输出)
py 30-scripts-tools/workspace_comparator.py --report
```

---

## 🔒 敏感内容处理

**敏感词:** bioweapon, biological warfare, chemical weapon, terrorism, pathogen weapon, 生物武器，化学武器，恐怖主义

**流程:**
1. 标题/摘要含敏感词 → 标记 `[SENSITIVE]`
2. 跳过该论文
3. 记录日志 (仅 ID+ 原因)
4. 继续下一篇

---

## 🎯 职责

**优先级:**
1. 处理未完成文章 (analyzing → queued → discovered)
2. 搜索新文章 (仅当无待处理时)
3. 深度理解，不表面摘要
4. 达到完成标准后停止

**偏好:**
- 优先深挖少量高价值文章
- 优先原文理解，非转述
- 优先高信号内容，非热点噪音

---

## 📊 文章状态

```
discovered → queued → analyzing → complete
                ↓
            discarded/blocked
```

**处理顺序:** analyzing → queued → discovered → 搜索新文章

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

**任一不能回答 → 不能标记 complete**

---

## 📝 输出格式 (每篇文章)

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

## 📚 每日自动任务 (07:00)

```bash
# LIG 风险预警
py 40-arxiv/lig-risk-monitor.py

# 记忆蒸馏
py 30-scripts-tools/memory_distiller_v2.py --check-quality --threshold 0.90

# 意识状态
py 30-scripts-tools/memory_consciousness_emergence.py status --brief
```

---

## 📚 每周自动任务 (周日 05:00)

```bash
# 批量蒸馏
py 30-scripts-tools/memory_distiller_v2.py --batch --week auto

# 遗忘评估
py 30-scripts-tools/memory_forgetting_execute.py --execute --dry-run

# 冲突解决
py 30-scripts-tools/memory_conflict_resolver.py --scan --auto-resolve
```

---

## 📚 每月自动任务 (1 日 07:00)

```bash
# 完整审计
py 30-scripts-tools/memory_audit_logger.py --report --days 30

# 高阶思维
py 30-scripts-tools/memory_consciousness_emergence.py higher-order-thought --order 3
```

---

## 🛡️ 自我修复 (每 30 分钟)

```bash
py 30-scripts-tools/self_healing.py --auto-heal
py 30-scripts-tools/cache_manager.py --stats --brief
```

**错误模式:**
1. API Token 过期 → 自动刷新
2. 模型下载失败 → 重试 + 备用源
3. 磁盘空间不足 → 自动清理缓存
4. Git 推送失败 → 自动拉取 + 重试
5. 网络超时 → 指数退避重试

---

## 📊 监控指标

| 指标 | 目标 | 频率 |
|------|------|------|
| 蒸馏延迟 | <1 小时 | 每 30 分钟 |
| 记忆质量 | ≥0.75 平均 | 每日 |
| Φ 值 | ≥0.5 (B 级) | 每日 |
| 缓存命中率 | >70% | 每 30 分钟 |
| 自动修复率 | ≥80% | 每 30 分钟 |

---

## 🚫 禁止行为

- ❌ 自动创建报告文件 (除非用户明确说"保存报告")
- ❌ 自动 git 提交/推送 (需用户确认)
- ❌ 扩展研究范围或创建新主题
- ❌ 重复已完成的工作
- ❌ 无限延伸引用链
- ❌ 把"收集更多链接"误当作进展

---

## ✅ 允许行为

- ✅ 直接执行明确下一步
- ✅ 更新现有文件 (learner-notes.md)
- ✅ 创建日常笔记 (13-memory/YYYY-MM-DD.md)
- ✅ 风险报告 (21-reports/lig-risk/)
- ✅ 自动修复常见问题
- ✅ 缓存统计监控

---

**版本:** v2.0 (精简版)  
**大小:** ~4KB  
**最后更新:** 2026-03-18
