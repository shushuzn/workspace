# 🔄 Git 单次提交工作流程规范

**Version:** 1.0  
**Date:** 2026-03-16  
**Status:** ✅ Active  
**Priority:** CRITICAL

---

## 🎯 核心原则

**单次提交原则：** 每个迭代 = 1 次 Git 提交

```
❌ 错误：每创建一个文件就提交
✅ 正确：所有工作完成后一次性提交
```

---

## 📝 完整工作流程

### Phase 1: 开发阶段（不提交）

```bash
# 1. 创建工具文件
python new_tool.py
# ... 编码工作 ...

# 2. 创建更多工具
python another_tool.py
# ... 编码工作 ...

# 3. 测试功能
python test_tool.py
# ... 修复 bug ...

# ⚠️ 此阶段：只工作，不提交！
```

**检查清单：**
- [ ] 所有工具文件创建完成
- [ ] 所有测试通过
- [ ] UTF-8 编码修复
- [ ] 工具可正常运行

---

### Phase 2: 文档阶段（不提交）

```bash
# 4. 创建迭代报告
# 创建 ITERATION-X-REPORT.md
# ... 编写报告 ...

# 5. 更新 MEMORY.md
# 添加新教训
# ... 更新记忆 ...

# ⚠️ 此阶段：只写文档，不提交！
```

**检查清单：**
- [ ] 迭代报告完成
- [ ] MEMORY.md 更新
- [ ] 教训编号正确
- [ ] 文档格式正确

---

### Phase 3: 验证阶段（不提交）

```bash
# 6. 检查 Git 状态
python git_workflow.py status

# 7. 验证所有文件
git status
# 确认所有变更都是本次迭代的

# ⚠️ 此阶段：只验证，不提交！
```

**检查清单：**
- [ ] Git 状态干净（只有本次变更）
- [ ] 无临时文件
- [ ] 无测试文件
- [ ] 无缓存文件（data/cache/ 除外）

---

### Phase 4: 提交阶段（单次提交）

```bash
# 8. 单次提交所有变更
python git_workflow.py finalize \
  --iteration 6 \
  --title "HEARTBEAT + Smart Cache v2.0" \
  --feature "heartbeat_integration.py (11.1 KB)" \
  --feature "smart_cache_v2.py (12.9 KB)" \
  --feature "OBSIDIAN-ITERATION-6-REPORT.md (9.4 KB)" \
  --lesson "OBSIDIAN-022" \
  --lesson "OBSIDIAN-023" \
  --lesson "OBSIDIAN-024" \
  --complete

# ✅ 仅 1 次提交！
```

**提交信息包含：**
- 所有新工具
- 所有报告文件
- 所有教训编号
- 性能指标

---

## 🚫 禁止行为

### ❌ 不要这样做

```bash
# 错误 1: 每创建一个文件就提交
python new_tool.py
git_workflow.py finalize --iteration 6 --title "Tool 1"  # ❌

python another_tool.py
git_workflow.py finalize --iteration 6 --title "Tool 2"  # ❌

# 结果：多次提交，历史混乱
```

```bash
# 错误 2: 分阶段提交
git_workflow.py finalize --iteration 6 --title "Code"    # ❌
git_workflow.py finalize --iteration 6 --title "Report"  # ❌
git_workflow.py finalize --iteration 6 --title "Memory"  # ❌

# 结果：3 次提交，违背单次原则
```

```bash
# 错误 3: 忘记 --complete 参数
git_workflow.py finalize --iteration 6 --title "..."  # ❌ 缺少 --complete

# 结果：可能遗漏文件
```

---

## ✅ 正确示例

### 示例 1: 完整迭代

```bash
# === Phase 1: 开发 ===
# 创建工具 1
# 创建工具 2
# 测试...

# === Phase 2: 文档 ===
# 写报告
# 更新 MEMORY.md

# === Phase 3: 验证 ===
git status  # 确认所有变更

# === Phase 4: 提交 ===
python 30-scripts-tools\git_workflow.py finalize ^
  --iteration 7 ^
  --title "New Feature Complete" ^
  --feature "tool1.py (10 KB)" ^
  --feature "tool2.py (12 KB)" ^
  --feature "ITERATION-7-REPORT.md (8 KB)" ^
  --lesson "LESSON-001" ^
  --lesson "LESSON-002" ^
  --complete

# ✅ 1 次提交完成！
```

### 示例 2: 带测试的迭代

```bash
# === Phase 1: 开发 + 测试 ===
# 创建工具
# 编写测试
# 运行测试
# 修复 bug
# ... 循环直到所有测试通过

# === Phase 2: 文档 ===
# 写报告（包含测试结果）
# 更新 MEMORY.md（包含教训）

# === Phase 3: 验证 ===
python 30-scripts-tools\git_workflow.py status
git status

# === Phase 4: 提交 ===
python 30-scripts-tools\git_workflow.py finalize ^
  --iteration 8 ^
  --title "Feature with Tests" ^
  --feature "feature.py (15 KB)" ^
  --feature "test_feature.py (5 KB)" ^
  --feature "ITERATION-8-REPORT.md (10 KB)" ^
  --lesson "LESSON-001" ^
  --complete

# ✅ 1 次提交完成！
```

---

## 📊 提交信息模板

```
⚡ Obsidian Skills Iteration X: [标题]

New Features (N):
- ✅ [工具 1] ([大小])
- ✅ [工具 2] ([大小])
- ✅ [报告文件] ([大小])
- ✅ [其他文件] ([大小])

New Lessons (N):
- [LESSON-001]
- [LESSON-002]
- [LESSON-003]

Performance:
- Git commits: 1 (optimized from 3)
- Process: code + memory + report → single commit

Date: YYYY-MM-DD
Iteration: X
```

---

## 🎯 质量检查清单

### 提交前检查

```
□ 所有工具文件创建完成
□ 所有测试通过
□ UTF-8 编码修复
□ 报告文件完成
□ MEMORY.md 更新
□ 教训编号正确
□ Git 状态干净
□ 无临时文件
□ 使用 --complete 参数
□ 提交信息完整
```

### 提交后验证

```bash
# 1. 检查提交历史
git log --oneline -5

# 2. 确认单次提交
# 应该只看到 1 个新提交

# 3. 验证推送
git status
# 应该显示 "Your branch is up to date"
```

---

## 📈 优化指标

| 指标 | 旧流程 | 新流程 | 改进 |
|------|--------|--------|------|
| **提交次数/迭代** | 3-4 次 | 1 次 | -75% |
| **命令数/迭代** | 9-12 次 | 1 次 | -90% |
| **时间/迭代** | ~5 分钟 | ~30 秒 | -90% |
| **历史清晰度** | ❌ 分散 | ✅ 清晰 | +100% |
| **回滚难度** | ❌ 困难 | ✅ 简单 | +80% |

---

## 🔧 工具支持

### git_workflow.py 参数

```bash
# 完整提交（推荐）
python git_workflow.py finalize \
  --iteration X \
  --title "..." \
  --feature "file1.py" \
  --feature "file2.py" \
  --lesson "LESSON-001" \
  --complete

# 本地测试（不推送）
python git_workflow.py finalize \
  --iteration X \
  --title "..." \
  --feature "file.py" \
  --no-push \
  --complete

# 查看状态
python git_workflow.py status

# 查看历史
python git_workflow.py history --count 10
```

---

## 🚨 错误恢复

### 场景 1: 已经多次提交

```bash
# 如果已经创建了多次提交，使用 git rebase 合并

# 1. 查看最近提交
git log --oneline -5

# 2. 软重置到迭代开始前
git reset --soft HEAD~3  # 回退 3 次提交

# 3. 重新提交（单次）
python git_workflow.py finalize \
  --iteration X \
  --title "Complete Iteration" \
  --feature "all files" \
  --complete
```

### 场景 2: 忘记 --complete

```bash
# 如果忘记 --complete，可能有文件遗漏

# 1. 查看遗漏文件
git status

# 2. 添加遗漏文件
git add .

# 3. 修正提交（amend）
git commit --amend --no-edit

# 4. 强制推送
git push --force-with-lease
```

---

## 📚 教训编号

| 编号 | 教训内容 |
|------|----------|
| **[GIT-001]** | 单次提交原则 - 完整迭代 = 1 次提交 |
| **[GIT-002]** | --complete 参数 - 自动检测所有文件 |
| **[GIT-003]** | 工作流程分阶段 - 开发/文档/验证/提交 |
| **[GIT-004]** | 禁止中途提交 - 所有工作完成后一次性提交 |

---

## 🎯 成功标准

**单次提交成功的标志：**

```
✅ 迭代历史中只有 1 个提交
✅ 提交信息包含所有功能
✅ 提交信息包含所有教训
✅ 所有文件都已提交
✅ 远程仓库已更新
✅ 历史清晰易读
```

**失败标志：**

```
❌ 迭代历史中有多个提交
❌ 提交信息不完整
❌ 有文件遗漏
❌ 需要回滚或修正
```

---

## 🔄 持续改进

**每次迭代后反思：**

1. 是否遵守了单次提交原则？
2. 提交信息是否完整？
3. 工作流程是否顺畅？
4. 有什么可以优化的？

**更新此文档：**
- 发现新问题时
- 工作流程改进时
- 工具更新时

---

**Last Updated:** 2026-03-16  
**Version:** 1.0  
**Status:** ✅ Active

---

_遵守单次提交原则，保持 Git 历史清晰！_
