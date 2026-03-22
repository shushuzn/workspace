# Active Skills Index

| Skill | Version | Category | Description |
|-------|---------|----------|-------------|
| [workflow](workflow/) | v1.0.0 | workflow | Session management |
| [coding](coding/) | v1.0.0 | programming | Universal coding workflow |
| [stock-pro](stock-pro/) | v12.7 | finance | Stock analysis toolkit |
| [pdf](pdf/) | - | document | PDF manipulation |
| [xlsx](xlsx/) | - | document | Spreadsheet operations |
| [docx](docx/) | - | document | Word document operations |
| [pptx](pptx/) | - | document | PowerPoint operations |
| [cron](cron/) | - | automation | Scheduled tasks |
| [browser_visible](browser_visible/) | - | browser | Visible browser control |
| [file_reader](file_reader/) | - | utility | File content reading |
| [file-handling](file-handling/) | - | utility | File operations |
| [guidance](guidance/) | - | utility | Installation guidance |
| [himalaya](himalaya/) | - | communication | Email management |
| [news](news/) | - | information | News lookup |
| [agent-spectrum](agent-spectrum/) | - | analysis | Agent scoring framework |
| [dingtalk_channel](dingtalk_channel/) | - | integration | DingTalk integration |

---

## Quick Reference

### Invoke a Skill

Skills are automatically loaded when relevant. Key phrases:

| Skill | Trigger Phrases |
|-------|-----------------|
| coding | "write code", "debug", "refactor" |
| stock-pro | "stock", "analyze", "portfolio" |
| pdf | "pdf", "merge", "split" |
| xlsx | "spreadsheet", "excel", "xlsx" |
| docx | "word", "docx", "document" |
| pptx | "powerpoint", "presentation", "slides" |
| cron | "schedule", "cron", "automate" |
| browser | "browser", "open page" |
| news | "news", "latest" |
| email | "email", "himalaya" |

---

## Skill Development

### MiniMax Skill Format

Skills follow the MiniMax format with:

```
skill-name/
├── SKILL.md           # Core skill document
├── scripts/           # Utility scripts
├── templates/         # File templates
├── references/        # Reference docs
└── assets/            # Images, fonts, etc.
```

### SKILL.md Structure

```yaml
---
name: skill-name
description: |
  Brief description. Use when: scenarios.
license: MIT
metadata:
  version: "1.0.0"
  category: category
  sources:
    - "source1"
    - "source2"
---

# Skill Name

## Invocation
## Skill Structure
## Compliance (mandatory)
## Workflow
## 1-10: Detailed sections
```

### Create New Skill

1. Create directory: `active_skills/<skill-name>/`
2. Create `SKILL.md` with frontmatter + compliance
3. Add `scripts/` and `templates/` as needed
4. Add to this index

### References

- [MiniMax Skills](https://github.com/MiniMax-AI/skills)
- [workflow/SKILL.md](workflow/) - Session management
- [coding/SKILL.md](coding/) - Programming workflow

---

## Updates

| Date | Skill | Change |
|------|-------|--------|
| 2026-03-22 | coding | Created |
| 2026-03-22 | stock-pro | v12.7 - 20 fixes |
