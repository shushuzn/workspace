# Feishu Communication System v2.0 - Quick Start Guide

**Version:** 2.0  
**Last Updated:** 2026-03-17  
**Status:** ✅ Production Ready

---

## 🚀 5 分钟快速启动

### 步骤 1: 配置环境变量 (2 分钟)

```bash
# 复制 .env 模板
cd D:\OpenClaw\workspace\30-scripts-tools
copy ..\.env.example .env

# 编辑 .env 文件
notepad .env
```

**必填配置:**
```ini
# Feishu 凭据
FEISHU_APP_ID=cli_a93a6936eff81bcd
FEISHU_APP_SECRET=your_secret_here
FEISHU_USER_ID=ou_72a847b95fc25870dcdd8ce56d929252

# 本地 LLM (可选)
LOCAL_LLM_ENABLED=true
LOCAL_LLM_MODEL=qwen2.5:1.5b
```

### 步骤 2: 测试消息队列 (1 分钟)

```bash
# 发送测试消息
python feishu_message_queue.py --send "Hello from v2.0!" --priority P1

# 处理队列
python feishu_message_queue.py --process

# 查看状态
python feishu_message_queue.py --status
```

### 步骤 3: 启动分析仪表板 (1 分钟)

```bash
# 启动仪表板
python feishu-analytics-dashboard.py

# 浏览器打开
http://localhost:8080
```

**看到实时图表 = 成功！** ✅

### 步骤 4: 测试聊天机器人 (1 分钟)

```bash
# 交互模式
python feishu-chatbot.py

# 输入测试命令
/status
/help
/faq 系统状态如何
```

### 步骤 5: 创建审批请求 (可选)

```bash
# 创建审批
python feishu_approval_workflow.py --create \
  --title "测试审批" \
  --description "这是测试" \
  --approver "ou_72a847b95fc25870dcdd8ce56d929252"

# 查看状态
python feishu_approval_workflow.py --status --request-id <request_id>
```

---

## 📋 常用命令速查

### 消息队列

```bash
# 发送消息
python feishu_message_queue.py --send "内容" --priority P1

# 发送卡片
python feishu_message_queue.py --card card-template.json

# 处理队列
python feishu_message_queue.py --process

# 查看状态
python feishu_message_queue.py --status

# 清理旧消息
python feishu_message_queue.py --cleanup --days 7
```

### 审批工作流

```bash
# 创建审批
python feishu_approval_workflow.py --create \
  --title "标题" \
  --description "描述" \
  --approver "user_id" \
  --priority normal \
  --timeout 30

# 批准
python feishu_approval_workflow.py --callback \
  --request-id 123 \
  --action approve

# 拒绝
python feishu_approval_workflow.py --callback \
  --request-id 123 \
  --action reject

# 查看状态
python feishu_approval_workflow.py --status --request-id 123

# 处理升级
python feishu_approval_workflow.py --escalate

# 统计数据
python feishu_approval_workflow.py --stats --days 7
```

### 分析仪表板

```bash
# 启动仪表板
python feishu-analytics-dashboard.py

# 访问
http://localhost:8080
```

### 聊天机器人

```bash
# 交互模式
python feishu-chatbot.py

# 可用命令
/help
/status
/queue
/persona
/approvals
/stats
/faq <问题>
```

---

## 🔧 故障排查

### 问题 1: "FeishuAPI not available"

**原因:** 缺少 `feishu_api.py` 或 `.env` 配置错误

**解决:**
```bash
# 检查文件存在
dir feishu_api.py

# 检查 .env
type .env

# 测试 API
python -c "from feishu_api import FeishuAPI; print('OK')"
```

### 问题 2: "ModuleNotFoundError"

**原因:** 模块名包含连字符

**解决:**
```bash
# 错误
import feishu-approval-workflow

# 正确
import feishu_approval_workflow
```

### 问题 3: 仪表板无法访问

**原因:** 端口被占用或防火墙阻止

**解决:**
```bash
# 检查端口
netstat -ano | findstr :8080

# 更换端口
python feishu-analytics-dashboard.py --port 8081

# 修改代码中的 PORT 配置
```

### 问题 4: 审批回调不工作

**原因:** 需要配置 webhook 服务器

**解决:**
```bash
# 开发环境：手动测试
python feishu_approval_workflow.py --callback \
  --request-id 123 \
  --action approve

# 生产环境：部署 webhook 服务器
# 参考：feishu_webhook_server.py (待实现)
```

---

## 📊 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                Feishu Communication v2.0                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Message    │  │  Approval    │  │   Chatbot    │ │
│  │    Queue     │  │   Workflow   │  │   + FAQ      │ │
│  │              │  │              │  │              │ │
│  │  - Priority  │  │  - Create    │  │  - Commands  │ │
│  │  - Retry     │  │  - Approve   │  │  - FAQ Match │ │
│  │  - Dedup     │  │  - Escalate  │  │  - LLM       │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                 │                 │          │
│         └─────────────────┼─────────────────┘          │
│                           │                            │
│                  ┌────────▼────────┐                   │
│                  │  SQLite DBs     │                   │
│                  │  - queue.db     │                   │
│                  │  - approvals.db │                   │
│                  │  - chatbot.db   │                   │
│                  └────────┬────────┘                   │
│                           │                            │
│         ┌─────────────────┼─────────────────┐         │
│         │                 │                 │         │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐ │
│  │   Card       │  │  Analytics   │  │   Feishu     │ │
│  │  Templates   │  │  Dashboard   │  │    API       │ │
│  │              │  │              │  │              │ │
│  │  - 6 Types   │  │  - Charts    │  │  - Send      │ │
│  │  - Custom    │  │  - Real-time │  │  - Receive   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 最佳实践

### 1. 消息优先级

| 优先级 | 使用场景 | 示例 |
|--------|---------|------|
| **P0** | 紧急告警 | 安全漏洞、系统宕机 |
| **P1** | 重要通知 | 审批请求、任务完成 |
| **P2** | 普通消息 | 日常通知、日志 |

### 2. 审批超时设置

| 类型 | 超时时间 | 升级次数 |
|------|---------|---------|
| **普通** | 30 分钟 | 2 次 |
| **重要** | 1 小时 | 3 次 |
| **紧急** | 15 分钟 | 1 次 |

### 3. FAQ 维护

- 每周更新 FAQ 数据库
- 记录未匹配问题
- 根据使用情况优化答案

### 4. 仪表板监控

- 每日检查送达率 (>95%)
- 监控失败率 (<5%)
- 跟踪平均响应时间 (<2 秒)

---

## 📚 进阶使用

### 集成到现有系统

```python
# 1. 导入模块
from feishu_message_queue import FeishuMessageQueue
from feishu_approval_workflow import ApprovalWorkflowManager

# 2. 初始化
queue = FeishuMessageQueue()
approvals = ApprovalWorkflowManager()

# 3. 发送通知
queue.enqueue("任务完成！", priority='P1')

# 4. 创建审批
request_id = approvals.create_approval_request(
    title="部署审批",
    description="请批准部署",
    approver_id="user_id"
)
```

### 自定义卡片模板

```python
from feishu_card_templates import CardTemplateLibrary

lib = CardTemplateLibrary()

# 创建自定义卡片
card = {
    "config": {
        "wide_screen_mode": True
    },
    "elements": [
        {
            "tag": "markdown",
            "content": "**自定义通知**\n\n内容在这里"
        }
    ]
}

# 发送
api.send_card(card, user_id)
```

### 扩展聊天机器人命令

```python
# 在 feishu_chatbot.py 中添加新命令

class CommandHandler:
    def __init__(self):
        self.commands = {
            # ... existing commands
            'custom': self.cmd_custom,
        }
    
    def cmd_custom(self, args):
        return "自定义命令响应"
```

---

## 🔗 相关文档

- **v1.0 文档:** `README-FEISHU-COMMUNICATION.md`
- **v2.0 报告:** `FEISHU-ITERATION-V2-REPORT.md`
- **API 参考:** 各模块 docstrings
- **MEMORY.md:** [FEISHU-001~042]

---

## 🆘 获取帮助

### 内置帮助

```bash
# 工具帮助
python feishu_message_queue.py --help
python feishu_approval_workflow.py --help
python feishu-chatbot.py --help

# 聊天机器人帮助
python feishu-chatbot.py
# 输入：/help
```

### 在线资源

- **GitHub Issues:** 提交 bug 报告
- **MEMORY.md:** 查看已知问题和解决方案
- **飞书开放平台:** https://open.feishu.cn/

---

## ✅ 检查清单

部署前确认：

- [ ] `.env` 文件已配置
- [ ] Feishu API 可访问
- [ ] 消息队列测试通过
- [ ] 仪表板可访问 (localhost:8080)
- [ ] 聊天机器人响应正常
- [ ] 审批流程测试通过
- [ ] 所有测试通过 (`python test_feishu_tools_v2.py`)

---

**🎉 恭喜！飞书通讯系统 v2.0 已就绪！**

**开始使用吧！** 🚀
