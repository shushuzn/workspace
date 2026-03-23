---
name: abc-contracts
description: |
  ABC Contracts: Behavioral Contracts for reliable agent execution.
  Use when: adding preconditions/postconditions to agent actions, ensuring reliability.
metadata:
  version: "1.0.0"
  category: reliability
---

# ABC Contracts Skill

Behavioral Contracts for reliable agent execution based on arXiv:2602.22302.

## Usage

```bash
py .opencode/skills/abc-contracts/run_abc.py check "<contract_name>"
py .opencode/skills/abc-contracts/run_abc.py list
```

## Actions

| Action | Description |
|--------|-------------|
| check | Verify contract conditions |
| list | List available contracts |
