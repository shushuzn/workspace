# WORKSPACE.md - Directory Structure

**Location:** `D:\OpenClaw\workspace/`

**Migration Complete:** 2026-03-18 (50+ dirs → 12 core dirs → standardized subdirs, ~59K files)

---

## 12 Core Directories (MECE Principle)

```
D:\OpenClaw\workspace/
├── 00-CORE/              → Identity: SOUL.md, MEMORY.md, AGENTS.md, USER.md, TOOLS.md, IDENTITY.md (8 files)
├── 01-CONFIG/            → Config: .openclaw/, git-hooks/, i18n/, obsidian/, templates/ (5 subdirs, 11 files)
├── 10-RESEARCH/          → Research: arxiv/, automation/, domain-research/, innovation/, papers/, reports/ (6 subdirs)
├── 20-MEMORY/            → Memory: archive/, cache/, daily/, distilled/, docs/, knowledge-graph/, logs/, memory/, P-Notes/, tests/ (10 subdirs, 277 files)
├── 30-AGENTS/            → Agents: critic/, docs/, execution/, personas/, planning/, pm/, scripts/ (7 subdirs)
├── 40-TOOLS/             → Tools: scripts/, utils/, automation/, collectors/, knowledge-cards/, setup/, templates/, tests/, archive/ (9 subdirs, ~300 scripts)
├── 50-DASHBOARD/         → Dashboard: api/, data/, web/ (3 subdirs)
├── 60-DATA/              → Data: raw/, processed/, external/, collectors/, cache/, experiments/, metrics/, backups/, context/ (9 subdirs)
├── 70-DEPLOY/            → Deploy: .github/, cloud/, configs/, dashboard/, installers/, monitoring/, scripts/ (7 subdirs)
├── 80-PROJECTS/          → Projects: stock-analyzer/, innovator/, rl-trading/, active/, 50-ton-hackathon-2026/ (5 subdirs)
├── 90-TESTS/             → Tests: unit/, integration/, fixtures/, dashboard/, 92-tests/ (5 subdirs)
├── 99-ARCHIVE/           → Archive: by-year/, by-project/, deprecated/, legacy-docs/, old-systems/, ... (34 subdirs)
├── logs/                 → System logs (14 files)
└── venv/                 → Python virtual environment (36,981 files)
```

---

## Key Principles

| Directory | Purpose | Rules |
|-----------|---------|-------|
| **00-CORE/** | Identity & principles | Only core identity files |
| **01-CONFIG/** | Session configuration | Preserved across migrations |
| **10-RESEARCH/** | Research materials | Papers, notes, automation |
| **20-MEMORY/** | Memory system | Only memory data (no scripts) |
| **30-AGENTS/** | Agent system | Personas, planning, critic |
| **40-TOOLS/** | **All executable scripts** | Scripts centralized here |
| **50-DASHBOARD/** | Dashboard | Web UI, API, data |
| **60-DATA/** | Data storage | raw/ → processed/ → external/ |
| **70-DEPLOY/** | Deployment | Cloud, monitoring, CI/CD |
| **80-PROJECTS/** | Active projects | stock-analyzer, innovator, etc. |
| **90-TESTS/** | Testing | Unit, integration, fixtures |
| **99-ARCHIVE/** | Historical archive | by-year/, by-project/, deprecated/ |

---

## File Placement Rules

**Scripts → 40-TOOLS/scripts/**
- All Python scripts (.py)
- All executable tools
- Memory tools included (e.g., `memory_distiller_llm.py`)

**Data → 60-DATA/**
- `raw/` — Original, unprocessed data
- `processed/` — Cleaned, transformed data
- `external/` — Imported from external sources
- `cache/` — Temporary cached data
- `experiments/` — Experimental datasets
- `metrics/` — Performance metrics
- `backups/` — Data backups

**Memory → 20-MEMORY/**
- `daily/` — Daily notes (YYYY-MM-DD.md)
- `memory/` — Raw memory files
- `distilled/` — Distilled insights
- `knowledge-graph/` — KG data
- **NO scripts here** (moved to 40-TOOLS/scripts/)

**Config → 01-CONFIG/**
- Session-specific configs (.env, config.json)
- Git hooks
- Templates
- Obsidian configs

---

## Git Hooks

**Location:** `01-CONFIG/git-hooks/`

**Pre-commit Hook** blocks:
- ❌ Report files: `*report*.md`, `*summary*.md`, `*phase*.md`, `*complete*.md`
  - Important info → `00-CORE/SOUL.md` or `00-CORE/MEMORY.md`
  - Historical reports → `99-ARCHIVE/`

**Warnings** for misplacement:
| File Type | Should Be In |
|-----------|--------------|
| `.json`, `.yaml`, `.env` | `01-CONFIG/` |
| `.py` scripts | `40-TOOLS/scripts/`, `80-PROJECTS/`, `30-AGENTS/` |
| `test_*.py` | `90-TESTS/` |
| `.html`, `.css`, `.js` | `50-DASHBOARD/web/` |
| `.csv`, `.xlsx`, `.pkl` | `60-DATA/` |
| `.log` files | `logs/` |

**Install:**
```powershell
.\01-CONFIG\git-hooks\install-hooks.ps1
```

---

## Git Commits (Migration)

| Commit | Description |
|--------|-------------|
| `58a2167a` | Memory system cleanup (10 duplicates removed, 14 scripts merged) |
| `5f54f09e` | Secondary directory standardization (~3,119 files) |
| `eed1b734` | SOUL.md update (secondary dirs documented) |
| `d5d5196f` | SOUL.md update (memory cleanup documented) |
| `f0648f41` | SOUL.md simplified (remove technical details) |

---

## Old Structure Reference

See `99-ARCHIVE/old-structure-map.md` for historical structure.

---

**Last Updated:** 2026-03-18 00:35
