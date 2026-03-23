---
name: memory-assistant
description: |
  AI Memory System 的 OpenClaw Agent 接口。用于存储、检索和蒸馏记忆。
  Use when: 用户需要记忆跨会话信息、搜索过往记忆、获取上下文。
metadata:
  version: "0.1.0"
  category: memory
---

# Memory Assistant Skill

记忆助手 - AI Memory System 的 OpenClaw Agent 接口。

## Capabilities

- 存储和检索记忆
- 语义搜索相关记忆
- 生成 LLM 上下文
- 记忆蒸馏压缩
- 持久化存储

## Usage

```bash
# 查看状态
py active_skills/memory-assistant/run_memory.py status

# 添加记忆
py active_skills/memory-assistant/run_memory.py memorize '{"key": "key_name", "value": "value", "memory_type": "short"}'

# 召回记忆
py active_skills/memory-assistant/run_memory.py recall '{"key": "key_name"}'

# 搜索记忆
py active_skills/memory-assistant/run_memory.py search '{"query": "关键词", "top_k": 3}'

# 语义搜索 (需要 sentence-transformers)
py active_skills/memory-assistant/run_memory.py semantic_search '{"query": "自然语言查询", "top_k": 3}'

# 获取上下文 (RAG)
py active_skills/memory-assistant/run_memory.py context '{"query": "query", "max_items": 5}'

# 蒸馏记忆
py active_skills/memory-assistant/run_memory.py distill

# 清理短期记忆
py active_skills/memory-assistant/run_memory.py clear

# 获取状态
py active_skills/memory-assistant/run_memory.py status
```

## Memory Types

| Type | 说明 | 持久化 |
|------|------|--------|
| short | 短期记忆 (内存, LRU+TTL) | 否 |
| long | 长期记忆 (JSON 文件) | 是 |

## Examples

### 记住用户偏好
```
py active_skills/memory-assistant/run_memory.py memorize '{"key": "user_language", "value": "Chinese", "memory_type": "long"}'
```

### 记住当前项目
```
py active_skills/memory-assistant/run_memory.py memorize '{"key": "current_project", "value": "OpenClaw optimization", "memory_type": "short"}'
```

### 搜索相关记忆
```
py active_skills/memory-assistant/run_memory.py search '{"query": "project"}'
```

### 获取 RAG 上下文
```
py active_skills/memory-assistant/run_memory.py context '{"query": "user preferences"}'
```

## Implementation

- Python runner: `active_skills/memory-assistant/run_memory.py`
- Memory library: `D:\ai_memory_system\`
- 数据存储: `D:\ai_memory_system\data\`

## Config

环境变量：
- `LOCAL_LLM_MODEL` - LLM 模型 (default: qwen2.5:1.5b)
- `LOCAL_LLM_BASE_URL` - LLM API (default: http://localhost:11434)

## Dependencies

```bash
pip install sentence-transformers numpy
```

## Search Types

| Type | 说明 | 示例 |
|------|------|------|
| search | 关键词匹配 | "python" → 包含 python 的记忆 |
| semantic_search | 语义理解 | "programming" → 找到 coding 相关记忆 |
