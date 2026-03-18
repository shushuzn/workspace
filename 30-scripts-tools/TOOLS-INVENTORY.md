# 30-scripts-tools 工具清单

**统计日期:** 2026-03-18  
**总计:** **302 个 Python 脚本**

---

## 📊 按功能分类统计

| 类别 | 数量 | 占比 | 核心工具 |
|------|------|------|----------|
| **记忆系统** | 46 | 15.2% | `memory_engine_*`, `memory_distiller_*`, `memory_search_*` |
| **工作流** | 12 | 4.0% | `workflow_engine_*`, `workflow_optimizer_*`, `workflow_visualizer` |
| **仪表盘** | 4 | 1.3% | `dashboard_*`, `phase4_dashboard`, `unified_dashboard` |
| **监控** | 1 | 0.3% | `monitor_reports` |
| **CLI 工具** | 3 | 1.0% | `unified_cli_v3`, `context_cli`, `self_iter_cli` |
| **文件整理** | 4 | 1.3% | `file-organizer`, `folder-organizer`, `organize-root-*` |
| **备份恢复** | 1 | 0.3% | `backup-strategy-restructure` |
| **清理工具** | 4 | 1.3% | `cleanup_reports`, `clean-duplicates-safe`, `disaster-recovery-*` |
| **安全** | 7 | 2.3% | `security_*`, `batch_security_fixer`, `quick_security_fix` |
| **报告** | 12 | 4.0% | `report_*`, `smart_report_generator`, `advanced_report_gen` |
| **测试** | 15 | 5.0% | `test_*`, `core_system_test`, `auto_test_*` |
| **统一接口** | 6 | 2.0% | `unified_*`, `api_gateway`, `master_orchestrator` |
| **缓存** | 10 | 3.3% | `cache_*`, `semantic_cache`, `tiered_cache`, `adaptive_ttl_cache` |
| **知识图谱** | 3 | 1.0% | `knowledge_graph_*`, `kg_*` |
| **飞书集成** | 8 | 2.6% | `feishu_*` |
| **自动化** | 11 | 3.6% | `auto_*`, `automation_*`, `autonomous_*` |
| **智能工具** | 8 | 2.6% | `smart_*`, `ai_*` |
| **预测分析** | 3 | 1.0% | `predictive_*`, `error_predictor`, `query_predictor` |
| **自我迭代** | 4 | 1.3% | `self_*`, `evolution_engine` |
| **配置** | 3 | 1.0% | `config_*`, `config_center_*` |
| **Git Hook** | 4 | 1.3% | `*hook*`, `install-git-hooks`, `setup-git-hooks` |
| **Git 工具** | 2 | 0.7% | `git_*` |
| **arXiv** | 2 | 0.7% | `arxiv_*` |
| **压缩** | 1 | 0.3% | `compress-tiff-to-png` |
| **灾难恢复** | 1 | 0.3% | `disaster-recovery-cleanup` |
| **安装部署** | 3 | 1.0% | `setup-*`, `install-*`, `auto_deploy*` |
| **系统** | 2 | 0.7% | `system_*`, `workspace` |
| **性能** | 3 | 1.0% | `perf_*`, `performance_*` |
| **健康检查** | 2 | 0.7% | `health_*` |
| **异常检测** | 2 | 0.7% | `anomaly_*` |
| **错误处理** | 2 | 0.7% | `error_*` |
| **资源** | 1 | 0.3% | `resource_monitor` |
| **任务** | 1 | 0.3% | `task_priority_scorer` |
| **批处理** | 3 | 1.0% | `batch_*` |
| **通知** | 2 | 0.7% | `notification_*` |
| **其他工具** | ~100 | 33.1% | 各种专用工具 |

---

## 🎯 核心工具详解

### 1. 记忆系统 (46 个)

**引擎类:**
```
memory_engine_autonomous.py
memory_engine_evolution.py
memory_engine_maintenance.py
memory_engine_ops.py
memory_engine_orchestrator.py
```

**提炼类:**
```
memory_distiller_llm.py
memory_distiller_v1.py
memory_distiller_v2.py
memory_distillation_runner.py
auto_distill.py
```

**搜索类:**
```
memory_search_cached.py
memory_search_v2.py
ultimate_memory_search.py
ultimate_memory_search_v2.py
ultimate_memory_search_v3.py
ultra_fast_memory_search.py
memory_semantic_search.py
```

**质量类:**
```
memory_quality_assessor.py
memory_quality_scorer.py
memory_quality_scorer_v1.py
memory_conflict_detector.py
memory_conflict_resolver.py
```

**高级功能:**
```
memory_consciousness_emergence.py      # 意识涌现
memory_dark_matter.py                   # 暗记忆
memory_forgetting.py                    # 遗忘机制
memory_immune_system.py                 # 免疫系统
memory_neural_network.py                # 神经网络
memory_quantum_entanglement.py          # 量子纠缠 (概念性)
memory_time_crystal.py                  # 时间晶体 (概念性)
```

**仪表盘:**
```
memory_dashboard_v1.py
memory_dashboard_v2.py
```

---

### 2. 统一 CLI (3 个)

**unified_cli_v3.py** (382 行)
- ✅ 自然语言命令解析
- ✅ 工具发现和执行
- ✅ 工作流编排
- ✅ 交互模式
- ✅ 命令历史
- ⚠️ 部分工具路径可能已变更

**命令示例:**
```bash
py unified_cli_v3.py "scan tools"
py unified_cli_v3.py "analyze tools"
py unified_cli_v3.py "search memory query"
py unified_cli_v3.py --interactive
```

---

### 3. 文件整理 (4 个)

**file-organizer.py**
- ✅ 扫描空目录
- ✅ 扫描缓存文件
- ✅ 扫描大文件 (>50MB)
- ✅ 扫描旧文件 (>90 天)
- ✅ 扫描敏感信息
- ✅ 扫描重复文件 (SHA256)

**folder-organizer.py**
- ⚠️ 有重名处理缺陷，已禁用

**organize-root-files-v2.py**
- ✅ 整理根目录散落文件

**clean-duplicates-safe.py**
- ✅ 安全清理重复文件 (只删 _from_ 副本)

---

### 4. Git Hook (4 个)

**pre_commit_hook.py**
- ✅ 报告文件阻止
- ✅ 敏感文件检测
- ✅ 编码检查 (UTF-8, 无 BOM)
- ✅ 嵌套备份检测
- ✅ _from_ 重复文件检测
- ✅ 大文件检测 (>50MB)

**install-git-hooks.py**
- ✅ 安装 Hook 到 .git/hooks/

**setup-git-hooks.py**
- ✅ 配置 Hook

**git-firewall-proxy.py**
- 🔍 Git 防火墙代理

---

### 5. 备份恢复 (5 个)

**backup-strategy-restructure.py**
- ✅ auto/ (7 天)
- ✅ manual/ (永久)
- ✅ archive/ (压缩)
- ✅ temp/ (临时)

**disaster-recovery-cleanup.py**
- ✅ 清理嵌套备份
- ✅ 清理 _from_ 重复文件

**compress-tiff-to-png.py**
- ✅ 大文件压缩

**cleanup_reports.py**
- ✅ 清理报告文件

**monitor_reports.py**
- ✅ 监控报告生命周期

---

### 6. 安全工具 (7 个)

```
security_auditor.py
security_auto_fixer.py
security_reporter.py
security_validator.py
batch_security_fixer.py
quick_security_fix.py
sensitive_content_router.py
```

---

### 7. 监控和健康 (9 个)

**监控:**
```
monitor_reports.py
resource_monitor.py
anomaly_detector.py
anomaly_detector_pro.py
```

**健康:**
```
health_monitor_ai.py
health_predictor.py
system_health_checker.py
```

**性能:**
```
performance_analyzer.py
performance_profiler.py
perf_dashboard.py
```

**错误:**
```
error_analyzer.py
error_predictor.py
```

---

### 8. 工作流引擎 (12 个)

```
workflow_engine.py
workflow_engine_v2.py
workflow_optimizer_ai.py
workflow_visualizer_web.py
workflow_generator.py
workflow_template_gen.py
workflow_validator.py
workflow_tester_auto.py
workflow_analyzer.py
workflow_enhancer.py
workflow_manager.py
workflow_server.py
```

---

### 9. 人格系统

**注意:** 人格文件主要在 `30-AGENTS/personas/` 目录，不在 30-scripts-tools

**相关工具:**
```
memory_persona.py
meta_cognition_monitor.py
coordinator_balancer.py
```

---

### 10. 飞书集成 (8 个)

```
feishu-analytics-dashboard.py
feishu-chatbot.py
feishu_approval_workflow.py
feishu_card_templates.py
feishu_message_queue.py
feishu_notification.py
feishu_persona_notify.py
feishu_report_generator.py
```

---

## 🔍 工具状态评估

### ✅ 已验证可用 (最近使用)

| 工具 | 最后使用 | 状态 |
|------|----------|------|
| `backup-strategy-restructure.py` | 2026-03-18 | ✅ 正常 |
| `disaster-recovery-cleanup.py` | 2026-03-18 | ✅ 正常 |
| `compress-tiff-to-png.py` | 2026-03-18 | ✅ 正常 |
| `file-organizer.py` | 2026-03-18 | ✅ 正常 |
| `clean-duplicates-safe.py` | 2026-03-18 | ✅ 正常 |
| `organize-root-files-v2.py` | 2026-03-18 | ✅ 正常 |
| `install-git-hooks.py` | 2026-03-18 | ✅ 正常 |
| `setup-git-hooks.py` | 2026-03-18 | ✅ 正常 |

---

### ⚠️ 需要验证 (可能路径变更)

| 工具 | 问题 | 建议 |
|------|------|------|
| `unified_cli_v3.py` | 部分工具路径可能已变更 | 更新 COMMAND_ALIASES |
| `memory_dashboard_v*.py` | 依赖可能缺失 | 测试运行 |
| `workflow_visualizer_web.py` | Web 服务依赖 | 测试运行 |
| `knowledge_graph_*.py` | 路径可能变更 | 检查导入 |

---

### ❌ 已知问题

| 工具 | 问题 | 状态 |
|------|------|------|
| `folder-organizer.py` | 重名处理缺陷 | 已禁用 |

---

## 📈 工具密度分析

**平均每类别:** 8.4 个工具  
**最高密度:** 记忆系统 (46 个，15.2%)  
**最低密度:** 压缩/灾难恢复 (各 1 个)

**工具分布:**
```
记忆系统    ███████████████ 15.2%
其他工具    ██████████ 33.1%
测试        ███ 5.0%
报告        ███ 4.0%
工作流      ██ 4.0%
自动化      ██ 3.6%
缓存        ██ 3.3%
安全        ██ 2.3%
飞书        ██ 2.6%
智能        ██ 2.6%
统一接口    ██ 2.0%
...
```

---

## 🎯 工具整合机会

### 1. 统一 CLI 增强 (优先级：高)

**当前:** `unified_cli_v3.py` (382 行)

**增强方向:**
```
[更新命令别名]
- 修复路径变更
- 添加新工具 (backup, disaster-recovery, etc.)
- 添加 Git Hook 测试命令

[新增功能]
- 工具健康检查
- 自动依赖安装
- 工具推荐 (基于任务)
```

**预估用时:** 2-3 小时

---

### 2. 记忆工具精简 (优先级：中)

**当前:** 46 个记忆工具

**精简方向:**
```
[合并相似工具]
- memory_search_v1/v2/v3 → memory_search.py
- memory_distiller_v1/v2 → memory_distiller.py
- memory_quality_scorer_v1 → memory_quality_scorer.py

[归档概念性工具]
- memory_quantum_entanglement.py (概念性)
- memory_time_crystal.py (概念性)
- memory_thermodynamics.py (概念性)
```

**预估节省:** 10-15 个文件

---

### 3. 报告工具整合 (优先级：中)

**当前:** 12 个报告工具

**整合方向:**
```
[统一报告生成器]
- smart_report_generator.py
- advanced_report_gen.py
- doc_generator.py
- unified_doc_generator.py

→ 合并为 report_generator.py
```

---

### 4. 监控工具统一 (优先级：低)

**当前:** 9 个监控/健康工具

**统一方向:**
```
[统一监控平台]
- health_monitor_ai.py
- system_health_checker.py
- resource_monitor.py
- anomaly_detector_pro.py

→ 合并为 monitor_platform.py
```

---

## 🚀 推荐行动

### P0: 立即可做 (今天)

1. **测试 unified_cli_v3.py**
   ```bash
   py 30-scripts-tools/unified_cli_v3.py --interactive
   ```
   验证核心命令是否正常工作

2. **更新 CLI 别名**
   修复路径变更的工具引用

3. **创建工具索引文档**
   本文档即为开始

---

### P1: 本周完成

4. **验证核心工具**
   - 记忆搜索
   - 仪表盘
   - 工作流引擎

5. **精简记忆工具**
   合并 v1/v2/v3 版本

6. **创建工具健康检查**
   自动检测不可用工具

---

### P2: 本月完成

7. **统一 CLI v4**
   基于 v3 增强，添加所有新工具

8. **工具文档化**
   为每个工具创建 README

9. **工具测试套件**
   自动化测试所有工具

---

## 📝 结论

**工具总数:** 302 个  
**核心工具:** ~50 个 (16.5%)  
**重复/相似:** ~100 个 (33.1%)  
**概念性/实验性:** ~50 个 (16.5%)  
**专用工具:** ~100 个 (33.1%)

**整合潜力:** 可减少 30-40% (约 90-120 个文件)

**建议策略:**
1. ✅ 保留核心工具 (已验证可用)
2. 🔧 整合相似工具 (v1/v2/v3 合并)
3. 📦 归档概念性工具 (移动到 90-archive/)
4. 📝 文档化所有工具

---

*文档版本：v1.0*  
*最后更新：2026-03-18*
