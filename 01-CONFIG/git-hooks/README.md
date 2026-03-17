# Git Hooks for OpenClaw Workspace

## Purpose

These hooks enforce workspace organization rules and coding standards.

## Available Hooks

### pre-commit
Validates file placement according to the 12-core directory structure:

- **Blocks report files** (`*report*.md`, `*summary*.md`, `*phase*.md`, etc.)
  - Important info → `00-CORE/SOUL.md` or `00-CORE/MEMORY.md`
  - Historical reports → `99-ARCHIVE/`

- **Warns about misplacement:**
  - Config files (`.json`, `.yaml`, `.env`) → `01-CONFIG/`
  - Python scripts → `40-TOOLS/`, `80-PROJECTS/`, or `30-AGENTS/`
  - Test files (`test_*.py`) → `90-TESTS/`
  - Web files (`.html`, `.css`, `.js`) → `50-DASHBOARD/web/`
  - Data files (`.csv`, `.xlsx`, `.pkl`) → `60-DATA/`
  - Log files (`.log`) → `logs/`

- **Enforces core files:**
  - `SOUL.md`, `MEMORY.md`, `AGENTS.md`, etc. must be in `00-CORE/`

## Installation

### Windows (PowerShell)
```powershell
cd D:\OpenClaw\workspace
.\01-CONFIG\git-hooks\install-hooks.ps1
```

### Linux/macOS
```bash
cd /path/to/workspace
cp 01-CONFIG/git-hooks/* .git/hooks/
chmod +x .git/hooks/*
```

## Bypass (Emergency Only)

If you need to commit something that fails the hook:

```bash
git commit --no-verify -m "Your message"
```

**Use sparingly** - the hooks exist to maintain workspace organization.

## Directory Structure Reference

```
00-CORE/       → Identity documents
01-CONFIG/     → Configuration files
10-RESEARCH/   → Research materials
20-MEMORY/     → Memory system
30-AGENTS/     → Agent system
40-TOOLS/      → Tool scripts
50-DASHBOARD/  → Dashboard (web/api)
60-DATA/       → Data files
70-DEPLOY/     → Deployment scripts
80-PROJECTS/   → Project-specific code
90-TESTS/      → Test files
99-ARCHIVE/    → Historical archives
```
