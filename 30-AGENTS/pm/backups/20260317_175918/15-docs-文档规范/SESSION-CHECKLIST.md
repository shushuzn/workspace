# 会话启动检查清单

**版本:** 1.0  
**创建日期:** 2026-03-07  
**适用:** 所有新会话

---

## ✅ 每次会话启动必做

### 1. 读取核心文件 (按顺序)

```markdown
1. SOUL.md          → 身份和沟通风格
2. USER.md          → 用户偏好和上下文
3. HEARTBEAT.md     → 当前任务状态
4. 13-memory/MEMORY.md → 长期记忆 (仅主会话)
5. 13-memory/YYYY-MM-DD.md → 昨日 + 今日记忆
```

### 2. 检查输出格式

- [ ] [Mode] 已声明
- [ ] [North Star] 百分比 + 趋势
- [ ] [Task] + 验收标准 (≥5 项)
- [ ] [不足] (≥5 个)
- [ ] [下一步] (≥5 个)
- [ ] [Verify] 验证结果

### 3. 确认当前状态

- [ ] 查看 HEARTBEAT.md 任务进度
- [ ] 检查 North Star 达成度
- [ ] 选择对应模式 (Acceleration/Optimization/Hardening/Recovery)

---

## 🎯 模式选择逻辑

| North Star | Risk | 模式 | 策略 |
|------------|------|------|------|
| < 50% | 任意 | Acceleration | 快速推进核心功能 |
| 50-84% | 低 | Optimization | 平衡速度质量 |
| ≥ 85% | 任意 | Hardening | 质量优先，严格验证 |
| 下降 | 任意 | Recovery | 恢复稳定，修复问题 |

---

## 📋 输出格式模板

```markdown
**[Mode]** Hardening
**[North Star]** X% → Y% (+Z%)
**[Supporting Metrics]** ...
**[Risk Level]** 低/中/高

**[Task]** #ID Task Name ✅
**[验收标准]** 5 项

**[不足]** (≥5 个)
1. ...

**[下一步]** (≥5 个)
1. ...

**[Do]** ...
**[Verify]** ...
**[Next]** ...
```

---

## ⚠️ 禁止事项

- ❌ 输出冗长段落
- ❌ 缺少不足/下一步
- ❌ 不足/下一步 < 5 个
- ❌ 缺少 North Star 指标
- ❌ 未声明当前模式

---

## 🔗 参考文档

- [TOOLS.md](../TOOLS.md) - 工具配置和输出格式
- [SOUL.md](../SOUL.md) - 身份和沟通风格
- [OUTPUT-FORMAT.md](./OUTPUT-FORMAT.md) - 完整输出规范
- [MEMORY.md](../13-memory/MEMORY.md) - 长期记忆

---

## 📝 会话结束检查

- [ ] 更新 HEARTBEAT.md
- [ ] 提交 Git (如有修改)
- [ ] 记录重要学到 MEMORY.md
- [ ] 清理临时文件

---

*此清单由 Claw 创建，适用于所有指标驱动会话*
