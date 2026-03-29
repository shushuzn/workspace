# 🤝 多 Agent 协作配置

**创建日期:** 2026-03-27

---

## 协作架构

```
用户 → Feishu (主 Agent)
         │
         ├──→ PR Reviewer (代码审查)
         ├──→ Test Writer (测试生成)
         ├──→ News Curator (资讯收集)
         ├──→ Vuln Scanner (安全扫描)
         └──→ 其他专用 Agent
```

---

## 协作场景

### 场景 1: PR 完整审查流程

```
用户提交 PR
    ↓
Feishu 调用 PR Reviewer (代码审查)
    ↓
Feishu 调用 Dep Scanner (依赖检查)
    ↓
Feishu 调用 Test Writer (补充测试)
    ↓
汇总报告 → 用户
```

**触发:** `"帮我审查这个 PR <url>"`

---

### 场景 2: 行业报告生成

```
用户请求报告
    ↓
Feishu 调用 News Curator (收集素材)
    ↓
Feishu 调用 SEO Writer (分析整理)
    ↓
Feishu 调用 Echo (生成多版本)
    ↓
输出报告 → 用户
```

**触发:** `"生成一份 AI 行业报告"`

---

### 场景 3: 安全事件响应

```
告警触发
    ↓
Feishu 调用 Vuln Scanner (确认漏洞)
    ↓
Feishu 调用 Incident Responder (分析影响)
    ↓
Feishu 调用 Personal CRM (通知相关人)
    ↓
生成事件报告 → 安全团队
```

**触发:** `"扫描项目漏洞并通知安全团队"`

---

## Agent 专业领域

| Agent | 专长 | 何时调用 |
|-------|------|----------|
| PR Reviewer | 代码审查、安全扫描 | 提 PR 时 |
| Test Writer | 单元测试、集成测试 | 代码覆盖率低 |
| Dep Scanner | 依赖管理、CVE 扫描 | 依赖更新时 |
| News Curator | 资讯收集、趋势分析 | 需要信息时 |
| Vuln Scanner | 漏洞检测、风险评估 | 安全审计 |
| Meeting Notes | 会议纪要、行动项 | 会议前后 |
| Personal CRM | 人脉管理、跟进 | 客户关系 |
| Churn Predictor | 数据分析、预警 | 客户流失风险 |

---

## 协作命令

```bash
# 查看可用 Agent
copaw agents list

# 与指定 Agent 协作
copaw agents chat <agent-id> --message "需要你帮忙..."

# 创建协作任务
copaw agents collaborate --agents "pr-reviewer,dep-scanner" --task "审查 PR #123"
```

---

## 协作规则

1. **Feishu 是主控** — 用户对话入口
2. **专用 Agent 按需调用** — 不要过度使用
3. **结果汇总给 Feishu** — 统一输出给用户
4. **上下文传递** — 必要时传递关键信息

---

## 当前 Agent 状态

| Agent | ID | 状态 | 可调用 |
|-------|-----|------|--------|
| Feishu (我) | nWyDpW | ✅ 在线 | ✅ 是 |
| Claw | ? | ❓ 未知 | ❓ 待确认 |

---

## 下一步

1. 确认其他 Agent 的 ID
2. 建立协作协议
3. 测试跨 Agent 通信

如需与特定 Agent 协作，告诉我需求，我来协调。
