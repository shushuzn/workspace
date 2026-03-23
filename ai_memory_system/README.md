# AI Memory System

Local-first memory system for AI agents. 轻量、本地优先的 AI 记忆系统。

## Features

- **短期记忆** - 内存缓存，支持 LRU 淘汰和 TTL 过期
- **长期记忆** - 持久化存储，支持关键词检索
- **记忆检索** - 统一接口，支持跨短/长期记忆搜索
- **记忆蒸馏** - 使用本地 LLM 压缩和提炼记忆
- **RAG 支持** - 生成上下文字符串，方便注入 LLM prompt

## Quick Start

```python
from ai_memory_system import MemorySystem

# Initialize
ms = MemorySystem()

# Add memories
ms.add("user_name", "Alice", memory_type="short")
ms.add("last_project", "AI Memory System", memory_type="long")

# Search
results = ms.search("alice")
for r in results:
    print(f"[{r['source']}] {r['value']}")

# Get context for LLM
context = ms.get_context("user preferences")

# Distill memories
distilled = ms.distill()

# Persist
ms.save()
```

## Architecture

```
┌─────────────────────────────────────────┐
│           MemorySystem                   │
│  (Unified interface)                    │
└───────────┬──────────────┬──────────────┘
            │              │
    ┌───────▼──────┐  ┌───▼───────────┐
    │ ShortTerm    │  │ LongTerm      │
    │ (Memory)     │  │ (JSON file)   │
    └──────────────┘  └───────────────┘
            │              │
    ┌───────▼──────────────▼──────┐
    │      MemoryRetriever         │
    │  (Unified search)            │
    └───────────────────────────────┘
                    │
           ┌────────▼────────┐
           │   MemoryDistiller │
           │ (LLM compression) │
           └──────────────────┘
```

## Configuration

环境变量:

- `LOCAL_LLM_MODEL` - LLM 模型 (default: qwen2.5:1.5b)
- `LOCAL_LLM_BASE_URL` - LLM API 地址 (default: http://localhost:11434)

## Project Structure

```
ai-memory-system/
├── __init__.py          # Package exports
├── config.py            # Configuration
├── short_term.py        # Short-term memory (in-memory LRU cache)
├── long_term.py         # Long-term memory (JSON file storage)
├── retrieval.py         # Unified retrieval interface
├── distiller.py         # LLM-based memory distillation
├── memory_system.py     # Core MemorySystem class
├── main.py              # CLI entry point
└── README.md
```

## Requirements

- Python 3.10+
- requests (for LLM API calls)
- Local LLM server (Ollama recommended)

## License

MIT
