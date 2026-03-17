# 7-Persona 人格系统

**整理日期:** 2026-03-18  
**版本:** v4.1  
**状态:** ✅ 已整理

---

## 📂 目录结构

```
personas/
├── 00-core/           # 核心代码 (7 人格 + 指挥者)
│   ├── planner.py          # 规划者
│   ├── executor.py         # 执行者
│   ├── critic.py           # 批判者
│   ├── learner.py          # 学习者
│   ├── coordinator.py      # 协调者
│   ├── innovator.py        # 创新者
│   ├── metacognitive.py    # 元认知
│   └── orchestrator.py     # 指挥者
├── 01-config/         # 配置文件
│   └── multi-agent-config.yaml
├── 02-docs/           # 文档
│   ├── 7-PERSONA-OPTIMIZATION-COMPLETE.md
│   ├── PERSONA-V4-INTEGRATION-COMPLETE.md
│   └── CRITIC-REVIEW-7-PERSONA.md
├── 03-scripts/        # 启动脚本
│   ├── start-dashboard-v4-persona.bat
│   ├── activate-personas.bat
│   └── persona-system.bat
├── 04-data/           # 运行时数据
│   ├── persona-state.json
│   ├── persona-health-history.json
│   └── persona-history.json
└── 99-archive/        # 历史版本
    └── v2-backup-20260317/   # v2 版本备份
```

---

## 🚀 快速启动

```bash
# 启动 Dashboard (默认 v4.1-Persona)
start-dashboard-v4-persona.bat

# 激活人格系统
activate-personas.bat

# 完整人格系统
persona-system.bat
```

---

## 📊 7 人格职责

| 人格 | 职责 | 触发条件 |
|------|------|---------|
| **Planner** | 任务规划、分解 | 新任务到达 |
| **Executor** | 任务执行 | 规划完成后 |
| **Critic** | 质量审查、找问题 | 任务完成前后 |
| **Learner** | 经验总结、记忆 | 任务完成后 |
| **Coordinator** | 健康监控、调度 | 持续监控 |
| **Innovator** | 创新提案、优化 | 定期/触发 |
| **Metacognitive** | 系统进化、反思 | 定期/触发 |
| **Orchestrator** | 总指挥、协调 | 全程 |

---

## 📝 整理记录

**整理前问题:**
- 文件分散在 5+ 位置 (04-plugins, 30-AGENTS, 60-DATA, 80-PROJECTS, 99-archive)
- 重复文件多 (文档 3 份 + 代码 2 份)
- 命名不统一 (persona-agent-*.py vs *-PERSONA-v2.md)
- 备份混乱

**整理后改进:**
- ✅ 统一到 `30-AGENTS/personas/`
- ✅ 标准化命名 (简短名称)
- ✅ 分类清晰 (core/config/docs/scripts/data/archive)
- ✅ 历史版本集中归档

---

## 🔗 原始位置保留

以下位置保留原始文件 (向后兼容):
- `04-plugins/persona-agent-*.py` - 插件系统调用
- `60-DATA/persona-*.json` - 运行时数据 (主存储)
- 根目录 `*.bat` - 快捷启动

**注意:** 新开发请使用 `30-AGENTS/personas/` 目录

---

*Last Updated: 2026-03-18*
