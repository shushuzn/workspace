# 🧠 Memory System Migration Guide

**Version:** 1.0  
**Date:** 2026-03-17  
**Status:** Production Ready  

---

## 📋 Overview

**Old System:** Multiple independent tools (memory_distiller_v2, memory_orchestrator, etc.)  
**New System:** Memory Core v2.0 (unified API)

**Why Migrate:**
- ✅ Single unified API
- ✅ Modular architecture
- ✅ Better maintainability
- ✅ Easier to extend
- ✅ Improved testability

---

## 🚀 Quick Start

### Before (Old System)
```python
# Multiple imports for different functions
from memory_distiller_v2 import MemoryDistiller
from memory_quality_scorer import MemoryQualityScorer
from memory_forgetting import MemoryForgetting

# Different APIs for each tool
distiller = MemoryDistiller()
distiller.distill('file.md')

scorer = MemoryQualityScorer()
score = scorer.assess('file.md')
```

### After (Memory Core v2.0)
```python
# Single import
from memory_core import MemoryCore

# Unified API
core = MemoryCore()
core.distill('file.md')
core.assess_quality('file.md')
core.process('text content')
```

---

## 📚 API Mapping

### Core Functions

| Old Tool | Old Command | New MemoryCore API |
|----------|-------------|-------------------|
| **memory_distiller_v2.py** | `--distill file.md` | `core.distill('file.md')` |
| | `--batch --week 2026-W12` | `core.distill_batch(week='2026-W12')` |
| | `--check-quality --threshold 0.90` | `core.check_quality(threshold=0.90)` |
| **memory_quality_scorer.py** | `--memory file.md` | `core.assess_quality('file.md')` |
| | `--batch` | `core.assess_batch(['file1.md', 'file2.md'])` |
| **memory_orchestrator.py** | `run-pipeline quick` | `core.process('file.md', pipeline='quick')` |
| | `run-full MEMORY.md` | `core.process('MEMORY.md', pipeline='full')` |
| | `status --all` | `core.status()` |
| **memory_forgetting.py** | `--evaluate` | `core.evaluate_forgetting('file.md')` |
| | `--execute` | `core.execute_forgetting('file.md')` |
| **memory_conflict_resolver.py** | `--scan` | `core.scan_conflicts('file.md')` |
| | `--auto-resolve` | `core.resolve_conflicts('file.md', auto=True)` |
| **memory_search_v2.py** | `--search "query"` | `core.search('query')` |
| | `--cached` | `core.search('query', use_cache=True)` |

### Advanced Functions

| Function | Old Way | New Way |
|----------|---------|---------|
| **Process Text** | N/A | `core.process("text content")` |
| **Get Memory** | N/A | `memory = core.get(id)` |
| **Optimize** | N/A | `core.optimize('file.md')` |
| **Export** | N/A | `core.export('file.md', format='json')` |

---

## 🔧 Migration Steps

### Step 1: Update Imports

**Before:**
```python
import sys
sys.path.insert(0, '30-scripts-tools')
from memory_distiller_v2 import MemoryDistiller
```

**After:**
```python
from memory_core import MemoryCore
```

### Step 2: Update Function Calls

**Before:**
```python
distiller = MemoryDistiller(threshold=0.90)
result = distiller.distill('13-memory/2026-03-17.md')
```

**After:**
```python
core = MemoryCore(quality_threshold=0.90)
result = core.distill('13-memory/2026-03-17.md')
```

### Step 3: Update Error Handling

**Before:**
```python
try:
    result = distiller.distill('file.md')
except DistillationError as e:
    print(f"Distillation failed: {e}")
```

**After:**
```python
try:
    result = core.distill('file.md')
except MemoryCoreError as e:
    print(f"Memory processing failed: {e}")
```

---

## 📖 Usage Examples

### Example 1: Simple Distillation

**Old:**
```bash
python memory_distiller_v2.py --distill "13-memory/2026-03-17.md"
```

**New:**
```python
from memory_core import MemoryCore

core = MemoryCore()
memory = core.distill('13-memory/2026-03-17.md')
print(f"Distilled: {memory.content}")
```

### Example 2: Quality Assessment

**Old:**
```bash
python memory_quality_scorer.py --memory "MEMORY.md"
```

**New:**
```python
from memory_core import MemoryCore

core = MemoryCore()
quality = core.assess_quality('MEMORY.md')
print(f"Quality Score: {quality.score:.2f}")
print(f"Density: {quality.density:.2f}")
```

### Example 3: Batch Processing

**Old:**
```bash
python memory_distiller_v2.py --batch --week 2026-W12
```

**New:**
```python
from memory_core import MemoryCore

core = MemoryCore()
results = core.distill_batch(week='2026-W12')
print(f"Distilled {len(results)} memories")
```

### Example 4: Pipeline Execution

**Old:**
```bash
python memory_orchestrator.py run-pipeline quick "MEMORY.md"
```

**New:**
```python
from memory_core import MemoryCore

core = MemoryCore()
result = core.process('MEMORY.md', pipeline='quick')
print(f"Processed: {result}")
```

---

## ⚠️ Deprecation Timeline

| Date | Event |
|------|-------|
| **2026-03-17** | Deprecation warnings added to old tools |
| **2026-03-24** | HEARTBEAT.md updated to use MemoryCore |
| **2026-04-01** | Old tools marked as deprecated in documentation |
| **2026-04-15** | Old tools removed from default imports |
| **2026-05-01** | Old tools scheduled for removal |

---

## 🔍 Verification

### Check if Using New System

```bash
# Test MemoryCore import
python -c "from memory_core import MemoryCore; print('✅ Using Memory Core v2.0')"

# Check for old tool usage
findstr /s /i "memory_distiller_v2" *.py 30-scripts-tools\*.py
findstr /s /i "memory_orchestrator" *.py 30-scripts-tools\*.py
```

### Run Tests

```bash
# Memory Core tests
cd 30-scripts-tools
python test_memory_core.py

# Verify no old tool usage in critical paths
python verify_deployment.py
```

---

## 🆘 Troubleshooting

### Issue 1: Import Error

**Error:**
```
ModuleNotFoundError: No module named 'memory_core'
```

**Solution:**
```bash
# Ensure you're in the correct directory
cd D:\OpenClaw\workspace\30-scripts-tools

# Or add to PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;D:\OpenClaw\workspace\30-scripts-tools
```

### Issue 2: Missing Function

**Error:**
```
AttributeError: 'MemoryCore' object has no attribute 'old_function'
```

**Solution:**
Check the API mapping table above. The function may have been renamed:
- `old_function` → `new_method`

### Issue 3: Configuration Error

**Error:**
```
MemoryCoreError: Configuration not found
```

**Solution:**
```python
from memory_core import MemoryCore, MemoryConfig

config = MemoryConfig(
    workspace='D:\\OpenClaw\\workspace',
    quality_threshold=0.7
)
core = MemoryCore(config=config)
```

---

## 📚 Additional Resources

- **Memory Core Documentation:** `30-scripts-tools/memory_core/README.md`
- **API Reference:** `30-scripts-tools/memory_core/core.py`
- **Test Examples:** `30-scripts-tools/test_memory_core.py`
- **Migration Check Report:** `30-scripts-tools/MEMORY-MIGRATION-CHECK-REPORT.md`

---

## ✅ Migration Checklist

- [ ] Read this migration guide
- [ ] Update imports in your scripts
- [ ] Replace old API calls with MemoryCore API
- [ ] Run tests to verify functionality
- [ ] Update HEARTBEAT.md (if applicable)
- [ ] Remove old tool imports from your code
- [ ] Report any issues or missing features

---

**Need Help?** Check `30-scripts-tools/memory_core/README.md` for detailed documentation.

**Status:** ⚠️ **Migration in Progress - Old tools deprecated but still functional**

---

*Generated:* 2026-03-17  
*Version:* 1.0  
*Next Review:* 2026-04-01
