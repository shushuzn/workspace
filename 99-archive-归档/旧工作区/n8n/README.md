# OpenClaw + n8n 自动化工作流

**创建时间:** 2026-03-04 21:32  
**更新时间:** 2026-03-04 21:38 (统一主工作流)  
**n8n 版本:** 2.9.4  
**工作流数量:** 1 个主工作流 + 2 个独立工作流

---

## 📋 工作流列表

### 🎯 1. OpenClaw 主工作流 (统一调度中心) ⭐NEW

**文件:** `workflows/openclaw-master-workflow.json`

**功能:** 统一调度所有定时任务

**触发器:**
| 时间 | 任务 | 说明 |
|------|------|------|
| **每小时** | Hourly Sync | Obsidian 自动同步 |
| **每日 2:00 AM** | arXiv Collect | 收集论文 + 智能解析 |
| **每日 3:00 AM** | Security Audit | 夜间安全审计 |
| **每日 4:00 AM** | Medium Watcher | 文章收集 + 分析 |
| **每日 9:00 AM** | Morning Sync | 早晨同步 |
| **每周日 5:00 AM** | Memory Distiller | 知识蒸馏 + 图谱 |
| **每周一 10:00 AM** | Weekly Report | 生成周报 |

**流程图:**
```
┌─────────────────┐
│  7 个触发器     │
│  (Cron/Schedule)│
└────────┬────────┘
         │
    ┌────┴────┐
    │ 主工作流 │
    │ 调度中心 │
    └────┬────┘
         │
    ┌────┴────────────────────────┐
    │                             │
┌───┴───┐  ┌───────────┐  ┌──────┴──────┐
│arXiv  │  │  Security │  │   Medium    │
│Collect│  │   Audit   │  │   Collect   │
└───┬───┘  └─────┬─────┘  └──────┬──────┘
    │            │               │
    │        ┌───┴───────────────┴───┐
    │        │   Obsidian Sync      │ (每小时)
    │        └───────────────────────┘
    │
┌───┴──────────┐
│Batch Parse   │ (≥3 篇高优先级)
└──────────────┘
```

---

### 2. OpenClaw 自动化工作流 (独立)

**文件:** `workflows/openclaw-automation.json`

**功能:** 独立的 Obsidian 同步 + Git 提交

**用途:** 备用方案或测试使用

---

### 3. arXiv 每日收集工作流 (独立)

**文件:** `workflows/arxiv-daily-workflow.json`

**功能:** 独立的 arXiv 收集流程

**用途:** 备用方案或测试使用

---

## 🚀 部署步骤

### 1. 启动 n8n

```bash
# 启动 n8n
n8n start

# 或使用隧道模式 (公开访问)
n8n start --tunnel
```

**访问地址:** http://localhost:5678

---

### 2. 导入工作流

1. 打开 n8n 界面
2. 点击 "Workflows" → "Add Workflow"
3. 点击右上角 "⋯" → "Import from File"
4. 选择 `workflows/openclaw-automation.json`
5. 同样导入 `arxiv-daily-workflow.json`

---

### 3. 激活工作流

1. 点击工作流右上角的 "Active" 开关
2. 确认激活

---

### 4. 配置凭据 (可选)

**OpenClaw API 凭据:**
1. 点击 "Credentials" → "Add Credential"
2. 选择 "HTTP Header Auth"
3. 填写:
   - Name: `OpenClaw API`
   - Header Name: `Authorization`
   - Header Value: `Bearer YOUR_API_KEY`

---

## 📊 工作流对比

| 特性 | Windows 定时任务 | n8n 工作流 |
|------|------------------|------------|
| **触发方式** | 固定时间 | 灵活 (时间/事件/Webhook) |
| **条件逻辑** | ❌ 无 | ✅ 支持 (if/switch) |
| **错误处理** | ❌ 基础 | ✅ 高级 (重试/通知) |
| **可视化** | ❌ 无 | ✅ 流程图 |
| **日志记录** | ❌ 事件查看器 | ✅ 执行历史 |
| **集成能力** | ❌ 本地脚本 | ✅ 200+ 应用 |
| **监控仪表板** | ❌ 无 | ✅ 实时状态 |

---

## 🎯 优化建议

### 当前配置

**Windows 定时任务 (保留):**
- ✅ OpenClaw-Arxiv-Collector (2:00 AM)
- ✅ OpenClaw-Nightly-Security-Audit (3:00 AM)
- ✅ OpenClaw-Medium-Watcher (4:00 AM)

**n8n 工作流 (新增):**
- ✅ Obsidian 自动同步 (每小时)
- ✅ arXiv 每日收集 (智能触发)

### 推荐配置

**迁移到 n8n:**
1. 保留 Windows 定时任务作为备份
2. 使用 n8n 处理复杂逻辑
3. 利用 n8n 的通知功能 (邮件/Slack/Discord)

---

## 🔧 高级用法

### 1. Webhook 触发

```json
{
  "node": "Webhook Trigger",
  "parameters": {
    "httpMethod": "POST",
    "path": "openclaw/collect"
  }
}
```

**用途:** 外部系统触发收集任务

---

### 2. 错误通知

```json
{
  "node": "Error Trigger",
  "parameters": {
    "method": "POST",
    "url": "https://hooks.slack.com/xxx"
  }
}
```

**用途:** 任务失败时发送 Slack 通知

---

### 3. 数据聚合

```json
{
  "node": "Merge",
  "parameters": {
    "mode": "append"
  }
}
```

**用途:** 合并多个数据源结果

---

## 📈 监控与日志

### n8n 执行历史

1. 点击 "Executions" 查看所有执行记录
2. 筛选成功/失败执行
3. 查看详细输入/输出

### 性能指标

- **平均执行时间:** ~30 秒
- **成功率:** 目标 >95%
- **每日执行:** ~24 次 (每小时同步)

---

## 🛡️ 安全建议

1. **不要暴露 n8n 公网访问** (除非必要)
2. **使用 HTTPS** (生产环境)
3. **配置认证** (Basic Auth / OAuth)
4. **限制 Webhook IP** (如果可能)

---

## 📚 相关资源

- [n8n 官方文档](https://docs.n8n.io)
- [n8n 工作流模板](https://n8n.io/workflows)
- [OpenClaw 技能文档](D:\npm-global\node_modules\openclaw\docs)

---

*工作流配置完成 · 2026-03-04*
