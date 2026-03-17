# ⚡ Memory Retrieval Optimization Plan

**Date:** 2026-03-16 21:45  
**Priority:** **CRITICAL**  
**Goal:** Reduce memory retrieval time by 80%+

---

## 🔍 Root Cause Analysis

### Performance Profile Results

| Operation | Time | Status |
|-----------|------|--------|
| MEMORY.md read | 0.37 ms | ✅ Excellent |
| TODO.md read | 0.12 ms | ✅ Excellent |
| Search (keyword) | 3-5 ms | ✅ Excellent |
| **memory_search tool** | **500-2000 ms** | ❌ **SLOW** |

### Bottleneck Identified

**Not file I/O!** The slowdown comes from:

1. **memory_search tool overhead** - Semantic search initialization
2. **No caching** - Same queries repeated
3. **Full index scan** - Every search scans all memories
4. **LLM embedding generation** - If using vector search

---

## 🎯 Optimization Strategies

### Strategy 1: Aggressive Caching ⭐⭐⭐⭐⭐

**Problem:** Same queries repeated across conversations

**Solution:**
```python
# Before: Every call searches
result = memory_search(query="memory evolution")  # 500ms

# After: Cached result
cache_key = hash(query)
if cache_key in cache:
    result = cache[cache_key]  # <1ms
else:
    result = memory_search(query)
    cache[cache_key] = result
```

**Expected Impact:** 90% reduction for repeated queries

**Implementation:**
```python
from context_cache_manager import ContextCacheManager

cache = ContextCacheManager()

# Cache search results for 10 minutes
cache_key = f"search:{query}"
cached = cache.get(cache_key)
if cached:
    return cached
else:
    result = memory_search(query)
    cache.put(cache_key, result, ttl=600, priority='MEDIUM')
    return result
```

### Strategy 2: Pre-computed Index ⭐⭐⭐⭐

**Problem:** Full scan every search

**Solution:**
```python
# Build index once at startup
index = {
    'memory': [snippet1, snippet2, ...],
    'evolution': [snippet1, snippet3, ...],
    'engine': [snippet2, snippet4, ...],
}

# Search = dictionary lookup (not scan)
results = index.get(query_word, [])  # <1ms
```

**Expected Impact:** 95% reduction for keyword search

**Implementation:**
```python
# Pre-build index (run once daily)
python memory_indexer.py --build

# Search uses index (not full scan)
python memory_search.py --query "xxx" --use-index
```

### Strategy 3: Lazy Loading ⭐⭐⭐

**Problem:** Loading entire MEMORY.md when only need snippet

**Solution:**
```python
# Before: Load full file
content = MEMORY.md.read_text()  # 49KB, 0.37ms
results = search_in_content(content, query)

# After: Load only relevant sections
sections = get_section_index()  # Small metadata
relevant = [s for s in sections if query in s['keywords']]
results = [load_section(s['id']) for s in relevant]  # Load only what's needed
```

**Expected Impact:** 50% reduction for targeted queries

### Strategy 4: Query Deduplication ⭐⭐⭐⭐⭐

**Problem:** Same query multiple times in one conversation

**Solution:**
```python
# Track queries in conversation
conversation_queries = {}

def smart_search(query):
    if query in conversation_queries:
        return conversation_queries[query]  # Reuse
    
    result = memory_search(query)
    conversation_queries[query] = result
    return result
```

**Expected Impact:** 70% reduction in multi-query conversations

### Strategy 5: Asynchronous Pre-fetch ⭐⭐⭐

**Problem:** Waiting for search to complete

**Solution:**
```python
# Pre-fetch likely needed memories in background
import asyncio

async def pre_fetch_memories(topic):
    # Run in background while user types
    results = await memory_search(topic)
    cache.put(f"prefetch:{topic}", results)

# Start pre-fetch when conversation starts
asyncio.create_task(pre_fetch_memories("current_topic"))
```

**Expected Impact:** Perceived latency → 0ms (already cached)

---

## 🛠️ Immediate Actions (Next Session)

### Priority 1: Implement Caching Layer

```python
# File: 30-scripts-tools/memory_search_cached.py

from context_cache_manager import ContextCacheManager

class CachedMemorySearcher:
    def __init__(self):
        self.cache = ContextCacheManager()
        self.query_history = {}  # Conversation-level cache
    
    def search(self, query: str, use_cache: bool = True):
        # Check conversation cache first
        if query in self.query_history:
            print(f"⚡ Cache hit (conversation): {query}")
            return self.query_history[query]
        
        # Check persistent cache (10 min TTL)
        cache_key = f"search:{query}"
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                print(f"⚡ Cache hit (persistent): {query}")
                self.query_history[query] = cached
                return cached
        
        # Fall back to full search
        print(f"🔍 Full search: {query}")
        result = memory_search(query)  # Original tool
        
        # Cache result
        if use_cache:
            self.cache.put(cache_key, result, ttl=600, priority='MEDIUM')
            self.query_history[query] = result
        
        return result
```

**Usage:**
```python
# Replace all memory_search calls with:
from memory_search_cached import CachedMemorySearcher
searcher = CachedMemorySearcher()
results = searcher.search("memory evolution")
```

### Priority 2: Add Query Statistics

```python
# Track which queries are most common
query_stats = {
    "memory evolution": 45,
    "security config": 32,
    "workflow engine": 28,
    ...
}

# Pre-compute top 20 queries daily
python memory_precompute.py --top 20
```

### Priority 3: Optimize memory_search Tool

**Current issues:**
- Loads full index every time
- No connection pooling
- No query optimization

**Fixes:**
```python
# 1. Singleton index (load once)
_index = None
def get_index():
    global _index
    if _index is None:
        _index = build_index()
    return _index

# 2. Limit results (default 5, not 50)
def memory_search(query, max_results=5):
    ...

# 3. Early exit (stop when found enough)
if len(results) >= max_results:
    break
```

---

## 📈 Expected Performance

### Before Optimization

| Scenario | Time |
|----------|------|
| First search | 500-2000 ms |
| Repeated search | 500-2000 ms |
| Multi-query conversation | 2000-8000 ms |

### After Optimization

| Scenario | Time | Reduction |
|----------|------|-----------|
| First search | 500-2000 ms | 0% (cold start) |
| Cached search | **<5 ms** | **99%** |
| Conversation cache | **<1 ms** | **99.9%** |
| Multi-query conversation | **100-500 ms** | **90%+** |

---

## 🔧 Configuration

### Cache Settings

```python
cache_config = {
    'ttl_seconds': 600,  # 10 minutes
    'max_entries': 100,
    'priority': 'MEDIUM',
    'eviction_policy': 'LRU',
}
```

### Query Optimization

```python
query_optimization = {
    'min_query_length': 2,  # Ignore single char
    'max_query_length': 100,  # Truncate long queries
    'stopwords': True,  # Remove common words
    'stemming': False,  # Keep original form
}
```

---

## 📝 Implementation Checklist

### Phase 1: Quick Wins (Next Session - 30 min)

- [ ] Create `memory_search_cached.py` wrapper
- [ ] Add conversation-level query deduplication
- [ ] Configure 10-minute TTL cache
- [ ] Test with real conversations
- [ ] Measure improvement

### Phase 2: Index Optimization (1 hour)

- [ ] Build pre-computed keyword index
- [ ] Implement lazy loading
- [ ] Add query statistics tracking
- [ ] Pre-compute top 20 queries daily

### Phase 3: Advanced (2 hours)

- [ ] Asynchronous pre-fetching
- [ ] Semantic caching (similar queries)
- [ ] Adaptive TTL (popular queries longer)
- [ ] Distributed cache (Redis)

---

## 🎯 Success Metrics

| Metric | Before | Target | After |
|--------|--------|--------|-------|
| Avg search time | 500ms | <50ms | ? |
| Cache hit rate | 0% | >80% | ? |
| Repeated query time | 500ms | <5ms | ? |
| User satisfaction | ? | >90% | ? |

---

## 💡 Pro Tips

1. **Cache warm-up**: Pre-load cache at conversation start
2. **Query normalization**: "memory" = "Memory" = "MEMORY"
3. **Partial matches**: Cache "memory evolution" and "memory" separately
4. **Expiration strategy**: Popular queries → longer TTL
5. **Monitor cache**: Track hit/miss ratio

---

**[MEM-OPT-001]** Caching is the #1 optimization for memory retrieval  
**[MEM-OPT-002]** Conversation-level cache fastest (no disk I/O)  
**[MEM-OPT-003]** 10-minute TTL balances freshness vs performance  
**[MEM-OPT-004]** Query deduplication eliminates redundant searches  

---

**Status:** 📋 Ready for implementation  
**Priority:** CRITICAL  
**ETA:** Next session (30 min for Phase 1)
