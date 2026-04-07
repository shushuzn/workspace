# File Operation Protocol - 文件操作规范

**Created:** 2026-03-14  
**Status:** ✅ MANDATORY (强制执行 - 最高优先级)  
**Version:** 3.0 (Strict Report Creation Limits)

---

## 🔒 核心原则（最高优先级）

### ⚠️ 禁止无对比的文件操作
- **禁止** 在没有对比现有文件的情况下创建文件
- **禁止** 在没有对比现有文件的情况下修改文件
- **禁止** 在没有对比现有文件的情况下删除文件
- **优先** 修改现有文件，而非创建新文件
- **保持** 工作台整洁，定期清理

### 🚫 严格限制报告文件创建（NEW - 最高优先级）
- **禁止** 创建 `session-report-*.md` 文件（使用单一 `learner-notes.md`）
- **禁止** 创建 `learning-summary-*.md` 文件（更新现有 summary）
- **禁止** 创建 `memory-update-*.md` 文件（直接更新 MEMORY.md）
- **禁止** 创建 `learner-memory-*.md` 文件（直接更新 MEMORY.md）
- **禁止** 创建 `learner-session-*.md` 文件（使用单一 `learner-notes.md`）
- **禁止** 创建 `workspace-comparison-*.md` 文件（默认只输出控制台）
- **禁止** 创建 `pre-op-check-*.json` 文件（默认只输出控制台）
- **优先** 更新现有文件，不创建新报告
- **默认** 工具只输出到控制台，不创建文件
- **例外** 明确指定 `--save` 参数才创建文件（谨慎使用）

### 强制检查流程
```
任何文件操作 → 运行 pre_file_operation_hook.py → 对比通过？ → 允许操作
                                          ↓
                                      不通过 → 阻止操作
```

### 2. 文件变动必定对比
- 使用 `workspace_comparator.py` 验证变更
- 对比报告必须保存
- 对比不通过不允许提交

### 3. 修改前必须备份
- 使用 `memory_auto_fix.py --strict` 自动备份
- 备份保留至少 7 天
- 关键文件保留 30 天

### 4. 审计日志完整
- 所有操作记录到 fix report
- Git 提交信息必须详细
- 包含对比结果和备份位置

### 5. 支持快速回滚
- 备份文件可随时恢复
- Git 历史保持清晰
- 回滚测试定期进行

---

## 🛠️ 工具使用规范

### workspace_comparator.py

**用途:** 文件对比验证（强制使用）

```bash
# 扫描工作区
python 30-scripts-tools/workspace_comparator.py --scan

# 对比配置区和工作区
python 30-scripts-tools/workspace_comparator.py --report

# 输出 JSON 报告
python 30-scripts-tools/workspace_comparator.py --json --output report.json
```

**强制使用时机:**
- ✅ **任何文件操作前**（创建/修改/删除）
- ✅ Git 提交前（pre-commit hook 自动运行）
- ✅ 批量文件操作前
- ✅ 每日健康检查

---

### pre_file_operation_hook.py（NEW - 强制使用）

**用途:** 文件操作前强制检查

```bash
# 创建文件前
python 30-scripts-tools/pre_file_operation_hook.py --before-create newfile.md

# 修改文件前
python 30-scripts-tools/pre_file_operation_hook.py --before-modify existing.md

# 删除文件前
python 30-scripts-tools/pre_file_operation_hook.py --before-delete oldfile.md

# 通用检查
python 30-scripts-tools/pre_file_operation_hook.py --check
```

**检查项目:**
1. ✅ 运行工作区对比（强制）
2. ✅ 扫描现有文件（优先修改现有文件）
3. ✅ 检查文件是否存在
4. ✅ 检查工作台整洁度
5. ✅ 保护关键文件（MEMORY.md 等）

**结果:**
- ✅ ALLOWED - 允许操作
- 🚫 BLOCKED - 阻止操作

---

### memory_auto_fix.py

**用途:** 自动修复 + 备份 + 审计（默认严格模式）

```bash
# 检查问题（默认严格模式）
python 30-scripts-tools/memory_auto_fix.py --check

# 自动修复（带对比 + 备份）
python 30-scripts-tools/memory_auto_fix.py --fix

# 模拟运行（不实际修改）
python 30-scripts-tools/memory_auto_fix.py --dry-run

# 禁用严格模式（不推荐）
python 30-scripts-tools/memory_auto_fix.py --no-strict
```

**默认行为:**
- ⚠️ **STRICT MODE ENABLED BY DEFAULT**
- 所有修改前自动运行对比
- 所有修改前自动创建备份
- 生成完整审计日志

---

### memory_health_monitor.py

**用途:** 健康监控

```bash
# 健康检查
python 30-scripts-tools/memory_health_monitor.py --check --report

# 每小时自动运行（cron）
0 * * * * cd /d D:\OpenClaw\workspace && python 30-scripts-tools\memory_health_monitor.py --check --report
```

**监控指标:**
- 文件存在性
- 文件大小（Workspace >40KB, Config >10KB）
- 交叉引用完整性

---

## 📋 文件操作流程

### 标准流程（修改文件）

```
1. 运行预操作检查（强制）
   python 30-scripts-tools/pre_file_operation_hook.py --before-modify filename.md
   ↓
2. 检查结果
   - ALLOWED → 继续
   - BLOCKED → 停止，解决问题
   ↓
3. 执行修改
   - 使用 edit_file 或 write_file
   - 小步修改，多次提交
   ↓
4. Git 提交（自动触发 pre-commit hook）
   git add filename.md
   git commit -m "Detailed message"
   ↓
5. Pre-commit hook 自动运行对比
   - 对比通过 → 允许提交
   - 对比失败 → 阻止提交
   ↓
6. Git 推送
   git push
```

### 创建文件流程（优先修改现有文件）

```
1. 扫描现有文件
   python 30-scripts-tools/pre_file_operation_hook.py --check
   ↓
2. 检查是否有现有文件可修改
   - 有类似文件 → 修改现有文件（不创建新的）
   - 无类似文件 → 继续创建流程
   ↓
3. 运行预操作检查（强制）
   python 30-scripts-tools/pre_file_operation_hook.py --before-create newfile.md
   ↓
4. 检查结果
   - ALLOWED → 允许创建
   - BLOCKED → 停止（理由：应修改现有文件）
   ↓
5. 创建文件
   ↓
6. Git 提交（自动对比）
```

### 删除文件流程（优先移动到 archive）

```
1. 运行预操作检查（强制）
   python 30-scripts-tools/pre_file_operation_hook.py --before-delete oldfile.md
   ↓
2. 检查是否受保护
   - MEMORY.md, PROFILE.md 等 → BLOCKED（禁止删除）
   - 普通文件 → 继续
   ↓
3. 建议移动到 archive
   - 移动到 90-99-archive/ 而非删除
   ↓
4. Git 提交
```

---

## 📊 对比报告解读

### 对比结果字段

| 字段 | 含义 | 安全阈值 |
|------|------|----------|
| **Identical** | 完全相同文件 | - |
| **Modified** | 已修改文件 | <10 个/次 |
| **Unique (Workspace)** | 仅工作区有 | 正常 |
| **Unique (Config)** | 仅配置区有 | <5 个 |
| **High Priority** | 高优先级审查 | 0 个 |
| **Review Needed** | 需要审查 | <20 个 |

### 危险信号

🚨 **立即停止操作，如果:**
- Modified > 10 个（未预期）
- High Priority > 0 个
- MEMORY.md 出现在 Modified 中（未备份）
- 配置文件出现在 Unique 中（意外）

---

## 💾 备份策略

### 备份位置
```
D:\OpenClaw\workspace\00-persona-system\memory-backups\
├── MEMORY-backup-20260314-220000.md
├── MEMORY-backup-20260314-230000.md
└── ...
```

### 备份保留策略
| 文件类型 | 保留期限 | 保留数量 |
|----------|----------|----------|
| **MEMORY.md** | 30 天 | 所有 |
| **配置文件** | 7 天 | 最近 10 个 |
| **系统文件** | 7 天 | 最近 5 个 |
| **临时文件** | 1 天 | 不保留 |

### 备份命名规范
```
{filename}-backup-{YYYYMMDD-HHMMSS}{extension}
```

---

## 📝 审计日志

### Git 提交规范

```bash
# 格式
git commit -m "[TYPE]: Description [TAG-XXX]

DETAILS:
- What changed
- Why changed
- Comparison result
- Backup location

FILES:
- file1.py (modified)
- file2.md (created)
"
```

### 提交类型

| TYPE | 用途 | 示例 |
|------|------|------|
| **Fix** | 修复问题 | Fix: Memory split issue [MEMORY-001] |
| **Add** | 新增文件 | Add: Health monitor tool [TOOL-001] |
| **Update** | 更新内容 | Update: User preferences [CONFIG-001] |
| **Refactor** | 重构代码 | Refactor: Comparator logic [CODE-001] |
| **Innovator** | 创新工具 | Innovator: Auto-fix module [INNOVATOR-011] |

---

## ↩️ 回滚流程

### 从备份恢复

```bash
# 1. 查找备份
dir D:\OpenClaw\workspace\00-persona-system\memory-backups\MEMORY-backup-*

# 2. 运行自动修复（会自动从最新备份恢复）
python 30-scripts-tools/memory_auto_fix.py --fix

# 3. 验证健康
python 30-scripts-tools/memory_health_monitor.py --check --report
```

### Git 回滚

```bash
# 查看历史
git log --oneline -10

# 回滚到特定提交
git revert <commit-hash>

# 强制回滚（危险！）
git reset --hard <commit-hash>
```

---

## 🎯 检查清单

### 文件操作前

- [ ] 已运行 workspace_comparator.py --report
- [ ] 已确认对比结果无危险信号
- [ ] 已创建备份（memory_auto_fix.py --check）
- [ ] 已记录修改原因
- [ ] 已准备 Git 提交信息

### 文件操作后

- [ ] 再次运行对比验证
- [ ] 确认修改符合预期
- [ ] Git 提交（详细信息）
- [ ] Git push
- [ ] 运行健康检查

### 定期维护

- [ ] 每小时：memory_health_monitor.py 自动运行
- [ ] 每天：检查备份文件大小
- [ ] 每周：清理过期备份（>30 天）
- [ ] 每月：回滚测试

---

## 🚨 违规处理

### 违规等级

| 等级 | 行为 | 后果 |
|------|------|------|
| **轻微** | 未运行对比但无损失 | 警告 + 补运行 |
| **中等** | 未备份但可恢复 | 警告 + 备份策略审查 |
| **严重** | 数据丢失 | 全面审查 + 流程改进 |
| **critical** | 重复违规 | 暂停文件操作权限 |

### 违规报告流程

1. 立即停止所有文件操作
2. 运行 health monitor 评估损失
3. 尝试从备份恢复
4. 记录违规详情到 memory-fix-report.json
5. 更新流程防止再次发生

---

## 📚 相关文档

- [Innovator Tools Inventory](innovator-tools-inventory.md)
- [Memory System Architecture](../13-memory-记忆系统/MEMORY.md)
- [Workspace Comparator Report](workspace-comparison-*.md)

---

## 🎓 教训编号

| 编号 | 教训 | 日期 |
|------|------|------|
| [INNOVATOR-016] | 严格模式防止意外变更 | 2026-03-14 |
| [INNOVATOR-017] | 修改前对比是强制性的 | 2026-03-14 |
| [FILE-001] | 文件操作零容忍错误 | 2026-03-14 |

---

*Last Updated: 2026-03-14 22:20*  
*Version: 1.0*  
*Status: ✅ Mandatory*
