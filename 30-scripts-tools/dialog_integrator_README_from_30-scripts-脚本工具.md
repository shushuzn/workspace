# dialog_integrator.py - 对话集成器

**功能:** 集成多轮对话管理、上下文追踪、响应生成  
**作者:** OpenClaw Team  
**创建:** 2026-02-22  
**更新:** 2026-03-13 (文档创建)  
**版本:** v1.0.0

---

## 📖 功能描述

`dialog_integrator.py` 提供完整的对话管理功能:

- **多轮对话:** 维护对话历史和上下文
- **意图识别:** 识别用户意图和槽位
- **响应生成:** 基于模板和规则生成响应
- **上下文追踪:** 追踪对话状态和实体
- **会话管理:** 开始、继续、结束会话

**适用场景:**
- 聊天机器人
- 客服对话系统
- 任务型对话
- 问答系统

---

## 🔧 依赖

```bash
pip install nltk spacy
```

---

## 🚀 使用方法

### Python API

```python
from dialog_integrator import DialogManager

# 创建对话管理器
dm = DialogManager(
    context_window=5,
    language='zh'
)

# 开始对话
dm.start_session(user_id='user_001')

# 处理用户输入
response = dm.process(
    user_id='user_001',
    message='我想查询今天的天气'
)

print(response['text'])

# 结束会话
dm.end_session(user_id='user_001')
```

---

## 📋 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `context_window` | int | 5 | 上下文窗口大小 |
| `language` | str | 'zh' | 语言 (zh/en) |
| `intent_model` | str | None | 意图识别模型路径 |

---

## 📊 输出格式

```json
{
  "session_id": "sess_001",
  "user_id": "user_001",
  "intent": "query_weather",
  "entities": [{"type": "date", "value": "today"}],
  "text": "正在查询今天的天气...",
  "context_updated": true
}
```

---

## ❓ 常见问题

### Q: 如何添加自定义意图？

A: 创建意图配置文件 `intents.json`:

```json
{
  "intents": [
    {
      "name": "custom_intent",
      "patterns": ["pattern1", "pattern2"],
      "responses": ["response1", "response2"]
    }
  ]
}
```

---

*最后更新:* 2026-03-13 11:40  
*文档状态:* ✅ 完整
