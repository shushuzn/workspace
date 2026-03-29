# 💾 备份配置

**创建日期:** 2026-03-27

---

## 备份策略

### 备份级别

| 级别 | 内容 | 频率 | 保留 |
|------|------|------|------|
| L1 | 核心配置 | 每日 | 30 天 |
| L2 | 工作文件 | 每周 | 90 天 |
| L3 | 完整快照 | 每月 | 1 年 |
| L4 | 归档 | 按需 | 按需 |

---

## 核心文件备份

```yaml
critical_files:
  - path: "agent.json"
    description: "Agent 配置"
  - path: "PROFILE.md"
    description: "Agent 身份"
  - path: "00-CORE/*.md"
    description: "核心文件"
  - path: "30-AGENTS/installed/"
    description: "Agent 模板"
  - path: ".env"
    description: "环境变量"
  - path: "memory/"
    description: "记忆文件"
```

---

## 备份位置

```
99-backups/
├── daily/
│   └── YYYY-MM-DD/
├── weekly/
│   └── YYYY-WXX/
├── monthly/
│   └── YYYY-MM/
└── archives/
```

---

## 备份命令

```bash
# 手动备份核心文件
backup.bat core

# 完整备份
backup.bat full

# 查看备份列表
backup.bat list

# 恢复备份
backup.bat restore 2026-03-27
```

---

## 恢复流程

1. 确认恢复点
2. 停止 Agent
3. 执行恢复
4. 验证完整性
5. 重启 Agent

---

## 自动备份规则

| 类型 | 时间 | 触发 |
|------|------|------|
| 核心文件 | 每日 03:00 | Cron 任务 |
| 记忆文件 | 每次会话结束 | 自动 |
| 重要决策 | 实时 | 触发时 |

---

## 灾难恢复

### 场景: 完全重置

1. 克隆仓库
2. 恢复 `.env`
3. 恢复 `agent.json`
4. 恢复 `memory/`
5. 恢复 `30-AGENTS/installed/`
6. 验证完整性

### 场景: 单文件恢复

```bash
# 查看备份
backup.bat list

# 恢复指定文件
backup.bat restore-file 30-AGENTS/installed/INDEX.md 2026-03-27
```

---

## 备份检查清单

- [ ] 备份核心文件
- [ ] 测试恢复流程
- [ ] 验证备份完整性
- [ ] 确认备份位置可用
- [ ] 设置自动备份 Cron

---

## 快捷命令

| 命令 | 执行 |
|------|------|
| `备份` | 执行核心文件备份 |
| `备份列表` | 查看可用备份 |
| `恢复` | 恢复最新备份 |
| `恢复 <日期>` | 恢复指定日期 |
