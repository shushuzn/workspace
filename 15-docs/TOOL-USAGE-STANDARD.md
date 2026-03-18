# Tool Usage Standard v2.0

**Date:** 2026-03-18  
**Priority:** CRITICAL  
**Applies to:** All tools in 30-scripts-tools/

---

## 🎯 Core Principle

```
所有工具都应该是自动调用的

✅ PASS: 工具被工作流脚本自动调用 (session_end.py, post_session_compress.py, etc.)
❌ FAIL: 工具只被手动调用 (手动调用 = 工具设计失败)
```

---

## 📋 Standard Definition

### Old Standard (v1.0) - ❌ DEPRECATED

```
Requirement: Tool must be used ≥1 time

Verification:
- Count critic-auto-*.json files
- Check command history
- Accept manual invocation as valid usage

Problem:
- Manual usage doesn't scale
- Users forget to use tools
- Tools become shelfware
```

### New Standard (v2.0) - ✅ CURRENT

```
Requirement: Tool must be integrated into workflow

Verification:
- Check session_end.py for tool calls
- Check post_session_compress.py for tool calls
- Check other workflow scripts
- Manual usage is NOT acceptable

Benefit:
- Automatic usage (no user action required)
- Consistent application
- Tools actually provide value
```

---

## 🔍 Verification Method

### auto-critic.py Workflow Detection

```python
workflow_scripts = [
    "session_end.py",
    "post_session_compress.py",
    "pre_session_hook.py",
    "memory_index_generator.py",
    "memory_tag_search.py",
    "memory_benchmark.py",
    "memory_consistency_checker.py",
]

# Check each workflow script for tool invocation
for workflow_file in workflow_scripts:
    content = workflow_file.read_text()
    
    # Check for import patterns
    if f"import {tool_name}" in content:
        return PASS
    
    # Check for subprocess patterns
    if f"py {tool_name}.py" in content:
        return PASS
    
    # Check for function calls
    if f"{function_name}(" in content:
        return PASS
```

### Evidence Examples

**✅ PASS Examples:**
```
session_end.py: contains 'py 30-scripts-tools\\auto-critic.py'
post_session_compress.py: contains 'import memory_index_generator'
memory_index_generator.py: contains 'memory_tag_search.py'
```

**❌ FAIL Examples:**
```
File exists but NOT in any workflow
Manual usage is NOT acceptable
Must integrate into session_end.py, post_session_compress.py, etc.
```

---

## 🛠️ Integration Patterns

### Pattern 1: subprocess Call

```python
# In session_end.py
import subprocess

def run_auto_critic(task_name: str):
    cmd = f'py 30-scripts-tools\\auto-critic.py -t "{task_name}" -p final'
    subprocess.run(cmd, shell=True, capture_output=True, text=True)
```

### Pattern 2: Function Import

```python
# In post_session_compress.py
from memory_index_generator import generate_index

def compress_session():
    # ... compression logic ...
    generate_index()  # Auto-call tool
```

### Pattern 3: Scheduled Execution

```python
# In cron job or heartbeat
py 30-scripts-tools\memory_benchmark.py --auto
```

---

## 📊 Tool Status

| Tool | Integrated In | Status |
|------|---------------|--------|
| `auto-critic.py` | `session_end.py` STEP 4 | ✅ PASS |
| `post_session_compress.py` | `session_end.py` STEP 1 | ✅ PASS |
| `memory_index_generator.py` | `post_session_compress.py` | ✅ PASS |
| `memory_tag_search.py` | None yet | ⚠️ TODO |
| `memory_benchmark.py` | None yet | ⚠️ TODO |
| `memory_consistency_checker.py` | None yet | ⚠️ TODO |
| `fast_load.py` | `session_end.py` STEP 2 | ✅ PASS |

---

## 🎯 Design Guidelines

### When Creating a New Tool

1. **Design for automation from the start**
   - Don't require user interaction
   - Support command-line arguments
   - Return clear exit codes

2. **Plan integration points**
   - Which workflow script will call this?
   - When should it be called? (start/mid/end)
   - What parameters does it need?

3. **Implement integration immediately**
   - Don't wait until "later"
   - Add to workflow script before committing
   - Test the integration

4. **Document the integration**
   - Which script calls this tool?
   - What parameters are used?
   - What's the expected output?

### Example: Tool Creation Checklist

```markdown
- [ ] Tool created: 30-scripts-tools/my-tool.py
- [ ] Integration planned: session_end.py STEP X
- [ ] Integration implemented: Added call to session_end.py
- [ ] Integration tested: session_end.py runs successfully
- [ ] Documentation: 15-docs/MY-TOOL.md created
- [ ] auto-critic verification: PASS
```

---

## 📈 Impact

### Before v2.0 (Manual Usage)

```
Tools Created: 7
Tools Used Manually: 3 (43%)
Tools Actually Providing Value: 2 (29%)
```

### After v2.0 (Workflow Integration)

```
Tools Created: 7
Tools Integrated: 4 (57%)
Tools Automatically Used: 4 (57%)
Tools Actually Providing Value: 4 (57%)
```

**Target:** 100% of tools integrated into workflow

---

## 🔗 Related Documents

- `ZERO-SCORE-ITEMS.md` - Zero-score items reference
- `SESSION-END-SCRIPT.md` - Session end workflow
- `AUTO-CRITIC.md` - Auto-critic documentation (TODO)

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-17 | Initial standard (manual usage accepted) |
| 2.0 | 2026-03-18 | Workflow integration required, manual = design failure |
