# 20260318-universal-workflow-001 优化方案

**创建日期:** 2026-03-20  
**当前版本:** 1.6.0  
**目标版本:** 2.0.0

---

## 📊 现状诊断

### 1. 步骤编号问题

**当前状态:**
```
步骤编号: 1, 2, 3, 4, 5, 6, 6.5, 6.6, 6.7, 7, 8, 8.5, 8.6, 8.7, 9.1, 10.1, 10.5, 11.2, 12.2, 13.2
```

**问题:**
- 12 个步骤使用非整数编号 (60%)
- 步骤不连续，难以追踪
- 必要步骤标记为 0/20

### 2. 工具映射问题

**当前状态:**
```
工具存在性: 0/20 (0%)
```

| 步骤 | 工具名 | 状态 | 替代工具 |
|------|--------|------|---------|
| 1 | context_search | ❌ | context_verify.py ✅ |
| 2 | flow_manager | ❌ | workflow_scheduler.py ✅ |
| 3 | task_analyzer | ❌ | task_analyzer.py ✅ |
| 4 | tool_suggester | ❌ | tool_selector.py ✅ |
| 5 | workflow_scheduler | ✅ | - |
| 6 | tool_executor | ✅ | - |
| 6.5 | integration_validator | ❌ | content_validator.py ✅ |
| 6.6 | auto-test-runner | ❌ | (合并到步骤 7) |
| 6.7 | config-backup | ❌ | auto_backup.py ✅ |
| 7 | execution_logger | ❌ | (使用 session_temp.json) |
| 8 | checkpoint_saver | ❌ | state_snapshot.py ✅ |
| 8.5 | memory-persistence | ❌ | memory_distiller.py ✅ |
| 8.6 | rollback-manager | ❌ | (合并到步骤 8) |
| 8.7 | metacognition-monitor | ❌ | metacognition_monitor.py ✅ |
| 9.1 | auto_critic_v7 | ❌ | embedded_critic.py ✅ |
| 10.1 | quality-gate-check | ❌ | (合并到步骤 9) |
| 10.5 | aai-scorer | ✅ | - |
| 11.2 | post-session-compress | ❌ | post_session_compress.py ✅ |
| 12.2 | git-commit | ❌ | git_commit_helper.py ✅ |
| 13.2 | auto-doc-generator | ✅ | - |

**实际可用工具:** 6/20 (30%)

### 3. 新工具未集成

**刚创建的工具:**
- ✅ pre-session-hook.py (会话前检查)
- ✅ core_files_compressor.py (核心文件压缩)
- ✅ post_session_compress.py (会话后压缩)
- ✅ session_end.py (会话结束)

**缺失的工具:**
- ❌ 快速工具选择器
- ❌ 集成测试器
- ❌ 回滚管理器

---

## 🎯 优化目标

### 短期目标 (v1.7.0)

1. **修复工具映射** - 将所有工具映射到实际存在的文件
2. **统一步骤编号** - 使用连续整数编号
3. **集成新工具** - 加入 pre-session-hook, core_files_compressor 等

### 中期目标 (v1.8.0)

1. **合并冗余步骤** - 减少步骤数量
2. **添加必要标记** - 标记关键步骤为 mandatory
3. **添加时间估算** - 为每个步骤添加预计时间

### 长期目标 (v2.0.0)

1. **工作流分层** - 区分核心步骤和扩展步骤
2. **动态执行** - 根据任务类型跳过可选步骤
3. **自动化执行** - 支持无人值守执行

---

## 📋 优化方案

### Phase 1: 紧急修复 (立即执行)

#### 1.1 重新编号步骤

**当前:**
```
1, 2, 3, 4, 5, 6, 6.5, 6.6, 6.7, 7, 8, 8.5, 8.6, 8.7, 9.1, 10.1, 10.5, 11.2, 12.2, 13.2
```

**优化后:**
```
1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20
```

#### 1.2 修复工具映射

| 新编号 | 步骤名 | 工具 | 状态 |
|--------|--------|------|------|
| 1 | 会话前检查 | pre-session-hook.py | ✅ 新增 |
| 2 | 上下文加载验证 | context_verify.py | ✅ 替换 |
| 3 | Flow ID 绑定 | workflow_scheduler.py | ✅ 替换 |
| 4 | 任务解析 | task_analyzer.py | ✅ 替换 |
| 5 | 工具选择 | tool_selector.py | ✅ 替换 |
| 6 | 子工作流调度 | workflow_scheduler.py | ✅ 保留 |
| 7 | 工具执行 | tool_executor.py | ✅ 保留 |
| 8 | 内容验证 | content_validator.py | ✅ 替换 |
| 9 | 自动备份 | auto_backup.py | ✅ 替换 |
| 10 | 检查点保存 | state_snapshot.py | ✅ 替换 |
| 11 | 记忆持久化 | memory_distiller.py | ✅ 替换 |
| 12 | 元认知评估 | metacognition_monitor.py | ✅ 替换 |
| 13 | 批判者审查 | embedded_critic.py | ✅ 替换 |
| 14 | 质量评分 | aai_scorer.py | ✅ 保留 |
| 15 | 核心文件压缩 | core_files_compressor.py | ✅ 新增 |
| 16 | 会话压缩 | post_session_compress.py | ✅ 替换 |
| 17 | 会话结束 | session_end.py | ✅ 新增 |
| 18 | Git 提交 | git_commit_helper.py | ✅ 替换 |
| 19 | 文档生成 | auto_doc_generator.py | ✅ 保留 |
| 20 | 清理临时文件 | (内置功能) | ✅ 新增 |

#### 1.3 标记必要步骤

```json
"mandatory_steps": [1, 2, 7, 13, 15, 16, 17]
```

### Phase 2: 结构优化 (一周内)

#### 2.1 步骤分组

```json
"step_groups": {
  "init": [1, 2, 3, 4, 5],
  "execution": [6, 7, 8, 9, 10],
  "memory": [11, 12],
  "quality": [13, 14],
  "cleanup": [15, 16, 17, 18, 19, 20]
}
```

#### 2.2 时间估算

| 步骤 | 预计时间 | 说明 |
|------|---------|------|
| 1 | 5s | 检查文件 |
| 2 | 10s | 加载上下文 |
| 3 | 5s | 绑定 Flow ID |
| 4 | 15s | 解析任务 |
| 5 | 10s | 选择工具 |
| 6 | 5s | 调度工作流 |
| 7 | 可变 | 执行任务 |
| 8 | 10s | 验证内容 |
| 9 | 5s | 自动备份 |
| 10 | 5s | 保存检查点 |
| 11 | 30s | 蒸馏记忆 |
| 12 | 10s | 元认知评估 |
| 13 | 20s | 批判者审查 |
| 14 | 10s | 质量评分 |
| 15 | 15s | 压缩核心文件 |
| 16 | 30s | 压缩会话 |
| 17 | 10s | 结束会话 |
| 18 | 15s | Git 提交 |
| 19 | 20s | 生成文档 |
| 20 | 5s | 清理文件 |

**总计:** 约 4 分钟 + 执行时间

### Phase 3: 功能增强 (两周内)

#### 3.1 动态跳过

```json
"skip_conditions": {
  "11": "if MEMORY.md < 20KB",
  "15": "if core_files < 100KB",
  "19": "if not user_requested"
}
```

#### 3.2 并行执行

```json
"parallel_groups": [
  [8, 9],  // 验证和备份可并行
  [13, 14] // 批判和评分可并行
]
```

#### 3.3 错误恢复

```json
"error_recovery": {
  "max_retries": 3,
  "fallback_steps": {
    "7": "manual_execution",
    "16": "skip_compression"
  }
}
```

---

## 🚀 实施计划

### Step 1: 创建工具映射表 (已完成)

**文件:** `tool_mapping.json`

### Step 2: 更新 workflow.json (立即执行)

**修改内容:**
1. 重新编号所有步骤
2. 更新 tool_id 为实际存在的文件
3. 标记 mandatory 步骤
4. 添加 estimated_time_seconds

### Step 3: 创建缺失工具 (一周内)

**需要创建:**
- quick_tool_selector.py (步骤 5)
- state_snapshot.py (步骤 10)

### Step 4: 测试验证 (一周内)

**测试场景:**
1. 完整工作流执行
2. 部分步骤跳过
3. 错误恢复
4. 并行执行

### Step 5: 文档更新 (一周内)

**更新文件:**
- AGENTS.md
- TOOLS.md
- MEMORY.md

---

## 📊 预期效果

| 指标 | 当前 | 优化后 | 提升 |
|------|------|--------|------|
| 工具可用性 | 30% | 100% | +233% |
| 步骤编号规范 | 40% | 100% | +150% |
| 必要步骤标记 | 0% | 35% | +100% |
| 时间估算 | 0% | 100% | +100% |
| 错误恢复 | 0% | 100% | +100% |

---

## ⚠️ 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 工具名称不匹配 | 高 | 创建工具映射表 |
| 步骤顺序改变 | 中 | 保持功能逻辑不变 |
| 新工具不稳定 | 中 | 充分测试后再上线 |
| 文档不同步 | 低 | 自动更新机制 |

---

**批准:** [待批准]  
**执行时间:** [待确定]  
**负责人:** Claw