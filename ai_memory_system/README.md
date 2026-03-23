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
├── ai_research_tool.py  # AI Research Tool (FLARE + MEMORA + AutoTool)
├── main.py              # CLI entry point
└── README.md
```

## AI Research Tool (v3.0)

Integrated research system combining FLARE + MEMORA + AutoTool:

```python
from ai_memory_system.ai_research_tool import ResearchTool, get_research_tool

# Get singleton instance
tool = get_research_tool()

# Run research task
result = tool.research("Research AI agent planning")

# Add to memory
tool.add_research_memory("FLARE planner solves myopic commitment", entities=["FLARE"])

# Search memories
results = tool.search_research_memory("FLARE")

# Get next tool via AutoTool inertia
next_tool = tool.get_next_tool("research_scan")
# Returns: {"next": "research_analyze", "method": "graph", "efficiency": 1.0}
```

### CLI Usage

```bash
py ai_research_tool.py research --task "Research AI agents"
py ai_research_tool.py add --content "FLARE saves 30% cost"
py ai_research_tool.py search --query "FLARE"
py ai_research_tool.py next --current research_scan
```

## Requirements

- Python 3.10+
- requests (for LLM API calls)
- Local LLM server (Ollama recommended)

## License

MIT
