---
name: himac-executor
description: |
  HiMAC: Hierarchical Macro-Micro Learning Executor for complex task decomposition.
  Use when: breaking down complex tasks, hierarchical planning, multi-step execution.
metadata:
  version: "1.0.0"
  category: execution
---

# HiMAC Executor Skill

Hierarchical Macro-Micro Learning Executor based on arXiv:2603.00977.

## Architecture

```
HiMACExecutor
├── MacroPlanner (blueprint generation)
└── MicroExecutor (goal-conditioned action execution)
```

## Usage

```bash
py .opencode/skills/himac-executor/run_himac.py plan "Research AI agents"
py .opencode/skills/himac-executor/run_himac.py execute "<blueprint_id>"
py .opencode/skills/himac-executor/run_himac.py status
```

## Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| plan | Generate hierarchical blueprint | task (str) |
| execute | Execute blueprint | blueprint_id (str) |
| status | View execution status | - |
