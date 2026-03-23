---
name: workflow
description: |
  Universal workflow for AI agent sessions. Provides unified session management,
  four-stage coding workflow, file operations, and safety rules. Use when:
  starting tasks, coding, saving progress, running tests, or ending sessions.
license: MIT
metadata:
  version: "1.0.0"
  category: workflow
  sources:
    - "AGENTS.md - Workspace rules"
    - "SOUL.md - Core identity"
    - "MEMORY.md - Long-term memory"
---

# Workflow Studio

Unified session management and coding workflow.

## Invocation

```bash
# Session commands
py workflow.py start <task>    # Start session
py workflow.py save <desc>     # Save progress
py workflow.py test            # Run tests
py workflow.py status          # View status
py workflow.py end <desc>      # End session
py workflow.py help            # Show help
```

## Skill Structure

```
workflow/
├── SKILL.md           # Core skill (this file)
├── scripts/
│   ├── run_tests.py   # Quick test runner
│   └── archive_old.py # Archive old files
└── templates/
    └── session_template.md  # Session template
```

## Compliance

**All rules in this skill are mandatory. Violating any rule is a blocking error.**

- [ ] Session started with `workflow.py start`
- [ ] Progress saved with `workflow.py save`
- [ ] Tests passed with `workflow.py test`
- [ ] Session ended with `workflow.py end`
- [ ] No forbidden operations used
- [ ] All file changes saved to disk

---

## Workflow

### Phase 1: Architect

Define the solution before coding:

1. **Purpose** — What problem does this solve?
2. **Data Flow** — Input → Process → Output
3. **File Structure** — What files need creation/modification?
4. **Edge Cases** — Error handling, validation

### Phase 2: Code

Implement following Architect decisions:

1. Write clean, documented code
2. Use DEBUG comments for complex logic
3. Follow naming conventions
4. Import modules correctly

### Phase 3: Ask

Self-review before testing:

1. **Edge Cases** — What unexpected inputs?
2. **Error Handling** — What can fail?
3. **Types** — Are parameters correct?
4. **Dependencies** — Are imports valid?

### Phase 4: Debug

Verify correctness:

1. **Unit Tests** — Individual functions
2. **Integration Tests** — Working together
3. **Edge Cases** — Boundary conditions

---

# 1. Session Management

## 1.1 Start Session

```bash
py workflow.py start "Task name"
```

Creates:
- `execution-state.json` — Session state
- `session_temp.json` — Decision history

## 1.2 Save Progress

```bash
py workflow.py save "Fixed cache bug"
```

Records:
- Current timestamp
- Decision/change description

## 1.3 Run Tests

```bash
py workflow.py test
```

Auto-detects and runs relevant tests:
- Stock PRO tests → `stock_pro/test_all.py`
- Workflow validation → State checks

## 1.4 End Session

```bash
py workflow.py end "Feature complete"
```

Performs:
- Duration calculation
- Memory file update
- State cleanup

---

# 2. File Operations

## 2.1 Read Before Write

```python
# ALWAYS read first
content = read_file("file.py")

# Then edit
edit_file(old_text, new_text)
```

## 2.2 Safe Patterns

| Operation | Method |
|-----------|--------|
| Read | `read_file()` |
| Edit | `edit_file()` |
| Write New | `write_file()` |
| Search | `grep_search()` |
| List | `glob_search()` |

## 2.3 Forbidden Patterns

| Category | Forbidden |
|----------|-----------|
| Shell | `bash`, `sh`, `cmd`, `powershell` |
| Execute | `os.system`, `subprocess`, `exec`, `eval` |
| Network | `curl\|bash`, `wget`, raw sockets |
| Paths | `../`, absolute paths (unless whitelisted) |

---

# 3. Four-Stage Coding

## 3.1 Stage 1: Architect

```
┌─────────────────────────────────────────┐
│  ARCHITECT                              │
│  ├─ Purpose: What problem?               │
│  ├─ Data Flow: Input → Process → Output  │
│  ├─ Files: What to create/modify?        │
│  └─ Edge Cases: Error handling           │
└─────────────────────────────────────────┘
```

**Output:** Written plan in response

## 3.2 Stage 2: Code

```
┌─────────────────────────────────────────┐
│  CODE                                   │
│  ├─ Implement per Architect plan         │
│  ├─ Use DEBUG comments for complexity    │
│  ├─ Follow naming conventions           │
│  └─ Keep functions focused              │
└─────────────────────────────────────────┘
```

**Output:** Working code files

## 3.3 Stage 3: Ask

```
┌─────────────────────────────────────────┐
│  ASK (Self-Review)                      │
│  ├─ Edge cases handled?                 │
│  ├─ Error handling complete?            │
│  ├─ Types correct?                      │
│  └─ Imports valid?                      │
└─────────────────────────────────────────┘
```

**Output:** Corrections if needed

## 3.4 Stage 4: Debug

```
┌─────────────────────────────────────────┐
│  DEBUG                                  │
│  ├─ Unit tests: Individual functions     │
│  ├─ Integration: Components work        │
│  └─ Edge cases: Boundaries tested        │
└─────────────────────────────────────────┘
```

**Output:** Pass/Fail status

---

# 4. State Files

## 4.1 Core Files

| File | Purpose | Persists |
|------|---------|----------|
| `execution-state.json` | Current session | ✅ |
| `session_temp.json` | Decision history | ❌ (temp) |
| `13-memory/YYYY-MM-DD.md` | Daily log | ✅ |
| `MEMORY.md` | Long-term memory | ✅ |

## 4.2 Session Template

```markdown
# Session Log

## Task
[Task name]

## Decisions
- [Time] Decision 1
- [Time] Decision 2

## Files Modified
- `file1.py` - Changed X
- `file2.py` - Added Y

## Tests
- [PASS/FAIL] Test name
```

---

# 5. Safety Rules

## 5.1 Forbidden Operations

| Category | Examples | Penalty |
|----------|----------|---------|
| Shell Direct | `bash`, `sh`, `cmd` | 50 pts |
| Execute Code | `os.system()`, `exec()` | 50 pts |
| Network Raw | `curl\|bash`, `wget` | 50 pts |
| Path Escape | `../`, absolute paths | 20 pts |

## 5.2 Allowed Operations

| Category | Functions |
|----------|-----------|
| Read | `read_file`, `view_image` |
| Write | `write_file`, `edit_file` |
| Browser | `browser_use`, `screenshot` |
| Utility | `memory_search`, `get_current_time` |
| Shell Safe | `safe_shell_executor.py` |

## 5.3 Protection Layer

All operations go through:
- `copaw_entry.py` — Session initialization
- `auto_protection_layer.py` — Risk checking
- `forced_protection_executor.py` — Blocking

---

# 6. Context Loading

## 6.1 Core Files (<100KB total)

```
SOUL.md, USER.md, AGENTS.md, TOOLS.md
HEARTBEAT.md, MEMORY.md
13-memory/YYYY-MM-DD.md (today)
```

## 6.2 Ignore Patterns

```
80-PROJECTS/, 40-arxiv/, 60-DATA/, 99-backups/
**/deep/*-full.md, node_modules/, venv/
```

## 6.3 Verification

```bash
py 30-scripts-tools/fast_load.py
# Should show: 49.6KB, 11562x speedup
```

---

# 7. Skills Index

## 7.1 Available Skills

| Skill | Category | Purpose |
|-------|----------|---------|
| workflow | workflow | Session management |
| coding | programming | Four-stage coding |
| stock-pro | finance | Stock analysis |
| pdf | document | PDF processing |
| xlsx | document | Spreadsheet |
| docx | document | Word document |
| pptx | document | PowerPoint |
| cron | automation | Scheduled tasks |
| browser_visible | browser | Visible browser |
| file_reader | utility | File reading |
| file-handling | utility | File operations |
| guidance | utility | Installation |
