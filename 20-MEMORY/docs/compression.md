# Memory Compression - Best Practices

**Location:** `20-MEMORY/docs/compression.md`

**Last Updated:** 2026-03-18 00:40

---

## Core Principle

**Compression > Storage (压缩优于存储)**

Memory should be distilled wisdom, not raw data dumps.

---

## 4-Stage Hybrid Pipeline (Target: 150:1)

```
原始记忆 → 向量聚类 (5:1) → LLM 摘要 (3:1) → 知识图谱 (5:1) → 智能遗忘 (2:1)
                                                        ↓
                                                    总计 150:1
```

---

## Stage 1: Vector Clustering (向量聚类去重)

**Tool:** `40-TOOLS/scripts/memory_vector_dedup.py` (TBD)

**Technology:**
- sentence-transformers (`all-MiniLM-L6-v2`)
- ChromaDB for vector storage
- DBSCAN clustering (eps=0.05)

**Process:**
1. Embed all memory fragments
2. Cluster by similarity (>0.95)
3. Keep best representative per cluster
4. Merge similar content

**Compression:** ~5:1

**Implementation Priority:** ⭐⭐⭐⭐⭐ (Highest ROI, start immediately)

---

## Stage 2: LLM Abstraction (LLM 抽象摘要)

**Tool:** `40-TOOLS/scripts/memory_distiller_llm.py` ✅ Available

**Technology:**
- Ollama local models (qwen2.5:1.5b, qwen3.5:2b)
- Batch processing for cost reduction
- JSON output for integration

**Process:**
1. Read daily notes
2. Extract 3-5 core insights per note
3. Score quality (5 dimensions)
4. Output to `20-MEMORY/distilled/`

**Quality Dimensions:**
- Importance (0.0-1.0)
- Generality (0.0-1.0)
- Actionability (0.0-1.0)
- Novelty (0.0-1.0)
- Timeliness (0.0-1.0)

**Compression:** ~3:1

**Implementation Priority:** ⭐⭐⭐⭐ (This week)

---

## Stage 3: Knowledge Graph Integration (知识图谱整合)

**Tool:** `40-TOOLS/scripts/memory_fractal_compression.py` ✅ Available (experimental)

**Technology:**
- spaCy entity recognition
- RDF triple storage: (subject, relation, object)
- Graph compression via node merging

**Process:**
1. Extract entities from distilled memories
2. Identify relationships
3. Build knowledge graph
4. Compress by merging similar nodes

**Compression:** ~5:1

**Implementation Priority:** ⭐⭐⭐ (Next week)

---

## Stage 4: Ebbinghaus 2.0 (智能遗忘)

**Tool:** `40-TOOLS/scripts/memory_forgetting.py` ✅ Available

**Technology:**
- Ebbinghaus forgetting curve
- Retention formula: `retention(t) = base_curve(t) × importance × usage × links`
- Multi-factor weighting

**Factors:**
- **Time decay** - Base Ebbinghaus curve
- **Importance** - Manually assigned or LLM-scored
- **Usage frequency** - Access count tracking
- **Link strength** - Number of connections to other memories

**Process:**
1. Calculate retention score for each memory
2. Below threshold (0.2) → Archive to `20-MEMORY/archive/`
3. Medium (0.2-0.4) → Keep in distilled
4. High (>0.4) → Promote to `20-MEMORY/memory/`

**Compression:** ~2:1 (over time)

**Implementation Priority:** ⭐⭐ (This month)

---

## Innovative Techniques (Research)

### 1. Predictive Coding (预测编码)

**Tool:** `40-TOOLS/scripts/memory_predictive_coding.py` ✅ Available (experimental)

**Concept:** Store only "prediction errors" (unexpected information)

**Inspiration:** Neuroscience - brain stores surprises, not predictions

**Process:**
1. Train generative model on existing memories
2. Predict next memory state / user need
3. Store only residual (prediction - actual)
4. Update model to minimize future error

**Expected Compression:** Additional 2:1

---

### 2. Multi-Resolution Memory (多分辨率记忆)

**Concept:** Different resolutions for different time scales

```
时间维度:
├── Raw (0-7 天)      → 100% retention, full detail
├── Embedding (7-30 天)  → 1% storage, vector only
├── Summary (30-90 天)   → 10% storage, LLM abstract
└── Principle (>90 天)   → 5% storage, core insights only
```

**Reconstruction:** On-demand retrieval rebuilds full context

**Average Compression:** ~150:1

---

### 3. Attention-Based Compression (注意力压缩)

**Concept:** Use Transformer attention mechanisms to decide what to keep

**Process:**
1. Run memory through attention model
2. High attention weights → Keep
3. Low attention weights → Compress or delete
4. Learn from retrieval patterns

**Inspiration:** How human brain consolidates memories during sleep

---

## Current Tools Inventory

| Tool | Status | Stage |
|------|--------|-------|
| `memory_cleanup_compress.py` | ✅ Ready | Pre-processing |
| `memory_distiller_llm.py` | ✅ Ready | Stage 2 |
| `memory_distiller_v1/v2.py` | ✅ Ready | Stage 2 |
| `memory_fractal_compression.py` | ⚠️ Experimental | Stage 3 |
| `memory_forgetting.py` | ✅ Ready | Stage 4 |
| `memory_predictive_coding.py` | ⚠️ Experimental | Research |
| `memory_quality_scorer.py` | ❌ Deprecated | - |
| `memory_semantic_search.py` | ✅ Ready | Retrieval |
| `memory_util_indexer.py` | ✅ Ready | Retrieval |

---

## Implementation Roadmap

### Phase 1: Foundation (Today)
- [ ] Run `memory_cleanup_compress.py` - Remove duplicates
- [ ] Run `memory_distiller_llm.py` - Distill daily notes
- [ ] Run `memory_forgetting.py` - Archive old memories
- **Target:** 2.14MB → 500KB (4:1)

### Phase 2: Vector Deduplication (Tomorrow, 2h)
- [ ] Create `memory_vector_dedup.py`
- [ ] Embed all memories
- [ ] Cluster and merge
- **Target:** 500KB → 100KB (5:1)

### Phase 3: Knowledge Graph (This week, 1 day)
- [ ] Enhance `memory_fractal_compression.py`
- [ ] Extract entity triples
- [ ] Build and compress graph
- **Target:** 100KB → 20KB (5:1)

### Phase 4: Predictive Coding (Next week, 2 days)
- [ ] Enhance `memory_predictive_coding.py`
- [ ] Train generative model
- [ ] Store prediction errors only
- **Target:** 20KB → 10KB (2:1)

---

## Expected Results

| Stage | Compression | Cumulative | Storage | Retrieval Speed |
|-------|-------------|------------|---------|-----------------|
| Original | 1:1 | 1:1 | 2.14MB | O(n) |
| Phase 1 | 4:1 | 4:1 | 500KB | O(n) |
| Phase 2 | 5:1 | 20:1 | 100KB | O(log n) |
| Phase 3 | 5:1 | 100:1 | 20KB | O(log n) |
| Phase 4 | 2:1 | 200:1 | 10KB | O(1) |

**Final Goals:**
- Compression: 10:1 → **150:1** (15x improvement)
- Retrieval: O(n) → **O(log n)**
- Semantic integrity: 60% → **90%**
- Storage: 50MB → **5MB** (-90%)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Semantic loss | Keep originals in `99-ARCHIVE/` (reversible) |
| Retrieval quality drop | A/B test before/after compression |
| LLM hallucination | Local models (Ollama) + human review |
| Over-compression | Tiered compression (reversible/irreversible) |

---

## Testing Protocol

1. **Before compression:**
   - Record baseline retrieval accuracy
   - Sample 10 random queries
   - Measure precision/recall

2. **After each stage:**
   - Run same 10 queries
   - Compare results
   - If quality drops >10%, adjust parameters

3. **Final validation:**
   - User feedback on retrieval quality
   - Measure storage savings
   - Document lessons learned

---

**Source:** Memory compression brainstorming session (2026-03-17) - Analysis of 12 compression techniques
