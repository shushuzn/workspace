# Memory Assistant Skill

记忆助手 - AI Memory System 的 OpenClaw Agent 接口。

## Capabilities

- 存储和检索记忆
- 语义搜索相关记忆
- 生成 LLM 上下文
- 记忆蒸馏压缩

## Usage

### memorize
添加记忆到系统。

```
Key: user_name
Value: Alice
Type: short|long
```

### recall
根据 Key 召回记忆。

```
Key: user_name
```

### search
语义搜索记忆。

```
Query: alice login
TopK: 3
```

### context
获取 RAG 上下文字符串。

```
Query: user preferences
MaxItems: 5
```

### distill
蒸馏压缩所有记忆。

### clear
清理短期记忆。

### status
查看记忆系统状态。

## Integration

```python
from ai_memory_system.agent_tool import MemoryAgentTool

tool = MemoryAgentTool()
tool.memorize("key", "value")
tool.search_memories("query")
tool.get_context("query")
tool.distill_memories()
tool.get_status()
```

## Config

环境变量：
- `LOCAL_LLM_MODEL` - LLM 模型 (default: qwen2.5:1.5b)
- `LOCAL_LLM_BASE_URL` - LLM API (default: http://localhost:11434)
