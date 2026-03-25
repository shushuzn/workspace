# HEARTBEAT.md - 精简版 v2.0

--- [200 lines compressed] ---


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
- ✅ 一次 heartbeat 只处理一篇文章
- ✅ 输出结果后停止
- ❌ 不连续处理多篇
## 🔒 文件操作保护 (最高优先级)
- ✅ `13-memory/YYYY-MM-DD.md` (日常笔记)
- ✅ `21-reports/lig-risk/lig-risk-report-*.md` (风险报告)
- ✅ `learner-notes.md` (更新)
- ❌ `*-report-*.md` (全局，Git Hook 阻止)
- ❌ `session-report-*.md`, `learning-summary-*.md`
- ❌ `memory-update-*.md`, `workspace-comparison-*.md`
# 文件操作前检查
py 30-scripts-tools/pre_file_operation_hook.py --before-create <file>
# 对比工具 (默认控制台输出)
py 30-scripts-tools/workspace_comparator.py --report
## 🔒 敏感内容处理
**敏感词:** bioweapon, biological warfare, chemical weapon, terrorism, pathogen weapon, 生物武器，化学武器，恐怖主义
1. 标题/摘要含敏感词 → 标记 `[SENSITIVE]`
2. 跳过该论文
3. 记录日志 (仅 ID+ 原因)
4. 继续下一篇
## 🎯 职责
1. 处理未完成文章 (analyzing → queued → discovered)
2. 搜索新文章 (仅当无待处理时)
3. 深度理解，不表面摘要
4. 达到完成标准后停止
- 优先深挖少量高价值文章
- 优先原文理解，非转述
- 优先高信号内容，非热点噪音
## 📊 文章状态
discovered → queued → analyzing → complete
            discarded/blocked
## ✅ "吃透"完成标准
1. 它在解决什么问题？
2. 核心结论是什么？
3. 结论如何被支撑？
4. 方法/论证的关键结构？
5. 最重要假设与局限？
6. 为什么值得关注？
7. 能用自己的话重述？
8. 与已有认知相比新增了什么？
**任一不能回答 → 不能标记 complete**
## 📝 输出格式 (每篇文章)
### Article Analysis
- Title:
- Source: (arXiv/HN/链接)
- Author:
- Published:
- Type: (论文/工程/观点/讨论)
### 1. Core question
### 2. Core thesis
### 3. Argument structure