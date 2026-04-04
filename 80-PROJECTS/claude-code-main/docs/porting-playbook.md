# Porting Playbook

A step-by-step guide for porting a TypeScript command or tool from the archived snapshot to a runnable Python module.

---

## Stages

```
snapshot metadata → stub __init__.py → partial port → complete port
```

---

## Stage 1: Snapshot Metadata

**Goal:** Identify the archived source files.

1. Find the command/tool in `src/reference_data/commands_snapshot.json` or `tools_snapshot.json`
2. Note `name`, `source_hint` (e.g. `commands/review.ts`), and `responsibility`
3. If porting a subsystem, check `src/reference_data/subsystems/<name>.json` for `sample_files`

**Checklist:**
- [ ] Command/tool exists in snapshot
- [ ] `source_hint` points to a real archived file path
- [ ] Responsibility description is noted

---

## Stage 2: Stub __init__.py

**Goal:** Create a metadata-only package that loads snapshot data.

1. Run `python scripts/scaffold_subsystem.py <name>` to generate the stub
2. Or create manually:
   ```python
   """Python package placeholder for the archived `<name>` subsystem."""

   from __future__ import annotations
   import json
   from pathlib import Path

   SNAPSHOT_PATH = Path(__file__).resolve().parent.parent / 'reference_data' / 'subsystems' / '<name>.json'
   _SNAPSHOT = json.loads(SNAPSHOT_PATH.read_text())

   ARCHIVE_NAME = _SNAPSHOT.get('archive_name', '<name>')
   MODULE_COUNT = _SNAPSHOT.get('module_count', 0)
   SAMPLE_FILES = tuple(_SNAPSHOT.get('sample_files', []))
   PORTING_NOTE = f"Python placeholder package for '{ARCHIVE_NAME}' with {MODULE_COUNT} archived module references."

   __all__ = ['ARCHIVE_NAME', 'MODULE_COUNT', 'PORTING_NOTE', 'SAMPLE_FILES']
   ```

**Checklist:**
- [ ] `src/<name>/__init__.py` created
- [ ] Snapshot path resolves correctly
- [ ] `porting_status.json` updated to `status: stub`

---

## Stage 3: Partial Port

**Goal:** Implement the core logic, even if incomplete.

1. Read the archived TypeScript source to understand the interface
2. Create Python module file(s) under `src/<name>/`
3. Define function/class signatures matching the original
4. Use `# TODO: port` comments for unconverted logic
5. Keep the `__init__.py` as the public surface

**Checklist:**
- [ ] Core function/class signatures match original
- [ ] Type hints added where possible
- [ ] `# TODO` comments for unported sections
- [ ] `porting_status.json` updated to `status: partial`
- [ ] `python -m src.main subsystems` shows the module

---

## Stage 4: Complete Port

**Goal:** Fully functional Python replacement.

1. Replace all `# TODO` comments with real implementations
2. Add tests under `tests/`
3. Remove snapshot dependency from `__init__.py` if no longer needed
4. Run full test suite: `python -m unittest discover -s tests -v`
5. Update `porting_status.json` to `status: complete`

**Checklist:**
- [ ] All `# TODO` comments resolved
- [ ] Unit tests added
- [ ] `python -m unittest discover -s tests -v` passes
- [ ] `porting_status.json` → `status: complete`
- [ ] CLI commands (if any) work via `python -m src.main <command>`

---

## Workflow Commands

```bash
# Scan and update all subsystem status
python scripts/porting_tracker.py

# Scaffold a new subsystem
python scripts/scaffold_subsystem.py <name> --dry-run

# Render CLI reference
python -m src.main docs --surface commands --query <term>

# Run tests
python -m unittest discover -s tests -v

# Parity audit
python -m src.main parity-audit
```

---

## Reference

- Snapshot files: `src/reference_data/commands_snapshot.json`, `tools_snapshot.json`
- Subsystem metadata: `src/reference_data/subsystems/<name>.json`
- Status files: `src/<name>/porting_status.json`
- CLI entrypoint: `python -m src.main`
