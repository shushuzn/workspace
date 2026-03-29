# 已安装技能清单

> 最后更新：2026-03-28

## 总计

- **已安装**: 45 个技能
- **已启用**: 41 个技能
- **安全审查技能**: ✅ 已安装

---

## 安全审查流程技能（新）

| 技能 | 状态 | 用途 |
|------|------|------|
| skill-security-review | ✅ 启用 | 每次安装新技能前的安全审查流程 |

**触发条件：**
- 用户提到"安装 skill" / "审查技能" / "这个技能安全吗"
- 从社区发现新技能时

**审查流程：**
1. clawskills.sh 初筛（VirusTotal + OpenClaw 状态）
2. Agent Trust Hub 深度扫描
3. 人工审查（SKILL.md + 代码）
4. 风险评级与安装决策

---

## 内置技能（Builtin）

| 技能 | 状态 | 类别 |
|------|------|------|
| news | ✅ 启用 | 资讯 |
| pdf | ✅ 启用 | 文档 |
| pptx | ✅ 启用 | 文档 |
| docx | ✅ 启用 | 文档 |
| xlsx | ✅ 启用 | 文档 |
| browser_use | ✅ 启用 | 浏览器 |
| execute_shell_command | ✅ 启用 | 系统 |
| read_file | ✅ 启用 | 文件 |
| write_file | ✅ 启用 | 文件 |
| edit_file | ✅ 启用 | 文件 |
| grep_search | ✅ 启用 | 文件 |
| glob_search | ✅ 启用 | 文件 |
| get_current_time | ✅ 启用 | 工具 |
| memory_search | ✅ 启用 | 记忆 |
| ... | ... | ... |

---

## 社区技能（已审查）

### 工作流与协作

| 技能 | 状态 | 风险 | 说明 |
|------|------|------|------|
| superpowers | ✅ 启用 | 🟢 低 | 系统化项目迭代 |
| langgraph_workflow | ✅ 启用 | 🟢 低 | LangGraph 工作流 |
| agnt-os | ✅ 启用 | 🟢 低 | Agent 操作系统层 |
| multi_agent_collaboration | ✅ 启用 | 🟢 低 | 多智能体协作 |

### 成本与配置

| 技能 | 状态 | 风险 | 说明 |
|------|------|------|------|
| agent-cost-strategy | ✅ 启用 | 🟢 低 | 模型成本优化 |
| agent-create-config | ✅ 启用 | 🟢 低 | Agent 配置创建 |
| agent-config | ✅ 启用 | 🟢 极低 | Agent 配置修改指南 |
| agent-benchmark | ✅ 启用 | 🟢 低 | Agent 基准测试 |

### 记忆与知识

| 技能 | 状态 | 风险 | 说明 |
|------|------|------|------|
| chroma_memory | ✅ 启用 | 🟢 低 | Chroma 向量记忆 |
| brain (2nd-brain) | ✅ 启用 | 🟢 低 | 个人知识库 |

### 工具与效率

| 技能 | 状态 | 风险 | 说明 |
|------|------|------|------|
| file_reader | ✅ 启用 | 🟢 低 | 文件读取 |
| cron | ✅ 启用 | 🟢 低 | 定时任务 |
| himalaya | ✅ 启用 | 🟢 低 | 邮件管理 |
| academic-research | ✅ 启用 | 🟢 低 | 学术研究 |
| guidance | ✅ 启用 | 🟢 低 | CoPaw 安装配置指南 |
| copaw_source_index | ✅ 启用 | 🟢 低 | CoPaw 文档索引 |
| channel_message | ✅ 启用 | 🟢 低 | 频道消息推送 |
| browser_visible | ✅ 启用 | 🟢 低 | 可见浏览器模式 |
| imraxy (auto-context-manager) | ✅ 启用 | 🟢 低 | 自动上下文管理 |

---

## 已拒绝技能（安全原因）

| 技能 | 风险 | 拒绝原因 |
|------|------|----------|
| 0g-compute | 🟡 中 | 金融/钱包操作 |
| aade-api-monitor | 🟡 中 | 凭证处理 |
| active-maintenance | 🟡 中 | 文件删除操作 |
| adblock-dns | 🟡 中 | 需要 root 权限 |
| autogen_collaboration | 🟡 中 | 代码执行 |
| zerone0x (book-fetch) | 🔴 高 | VirusTotal Suspicious + 版权问题 |
| shawnpana | 🟡 中 | 无 SKILL.md 文档 |

---

## 安全参考文档

| 文档 | 路径 |
|------|------|
| Snyk Agent Scan | `docs/snyk-agent-scan.md` |
| Agent Trust Hub | `docs/agent-trust-hub.md` |
| 安全审查清单 | `active_skills/skill-security-review/references/checklist.md` |
| 快速审查指南 | `active_skills/skill-security-review/references/quick-guide.md` |

---

## 安全原则

1. **双重 Benign 原则** — VirusTotal 和 OpenClaw 都必须是 Benign
2. **代码审查必要** — 即使扫描通过也要人工检查
3. **最小权限原则** — 只安装必要权限的技能
4. **定期复审** — 已安装技能也应定期复查
5. **有疑问 = 不安装**

---

## 下次审查时使用

```
# 触发安全审查技能
"帮我审查这个技能：{skill-name}"
"准备安装 {skill-name}，执行安全审查"
"这个技能安全吗：{skill-name}"
```
