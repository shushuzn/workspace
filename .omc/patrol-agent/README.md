# Patrol Agent

An autonomous workspace patrol agent that continuously巡逻 workspace:

- Execute pending plans from `docs/superpowers/plans/`
- Check and fix lint errors
- Run test suites
- Optimize code (dead code, duplicates, naming)
- Deep research → generate new plans
- Loop forever until stopped

## Quick Start

### Windows
```batch
patrol.bat
```

### Manual
```bash
cd D:/OpenClaw/workspace/.omc/patrol-agent
node src/index.js
```

## Patrol Rhythm

| Priority | Action | Frequency |
|----------|--------|-----------|
| High | Execute pending plans, lint check, test fix | Every loop (~5 min) |
| Medium | Code optimization scan | Every 10 loops |
| Low | Deep research → new plans | Every 50 loops |

## Adding Plans

Drop a `.md` file into `docs/superpowers/plans/` with frontmatter:

```markdown
---
status: pending
id: my-plan-id
hash: sha256:abc123
created_at: 2026-03-27T00:00:00Z
---

# Plan: My Plan

[content]
```

## Viewing State

Patrol state is stored at `~/.omc/patrol-state.json`:

```bash
cat ~/.omc/patrol-state.json | jq
```

## Stopping

Press `Ctrl+C` in the terminal running the agent.

## Logs

Patrol logs are in `~/.omc/patrol-state.json` under `patrol_log`. Recent activity:

```bash
cat ~/.omc/patrol-state.json | jq '.patrol_log[:3]'
```

## Architecture

```
src/
├── index.js      # Main patrol loop
├── state.js     # State load/save (~/.omc/patrol-state.json)
├── plans.js      # Plan discovery + status updates
├── git.js        # Git conflict detection + branching
├── lint.js       # ESLint check across projects
├── executor.js   # Execute plans via claude CLI
├── research.js   # GitHub + arXiv search
└── planWriter.js # Write new plans from research
```

## Projects Monitored

- `80-PROJECTS/agent-arena`
- `80-PROJECTS/ai-roundtable`
- `80-PROJECTS/star-forge-web`
