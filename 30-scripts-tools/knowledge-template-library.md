# Knowledge Template Library / 知识沉淀模板库

**Created:** 2026-03-13 (Critic v5.0 fix-012)  
**Purpose:** Reusable templates for knowledge capture and reuse  
**Version:** v1.0

---

## 📚 Template Categories / 模板分类

### 1. Research Templates / 研究模板

#### Paper Analysis Template / 论文分析模板
```markdown
# Paper Analysis: [Title]

## Basic Info
- **Authors:** [Names]
- **Journal/Conference:** [Venue]
- **Year:** [Year]
- **DOI/PMID:** [ID]

## Core Question
[What problem does this paper solve?]

## Key Contributions
1. [Contribution 1]
2. [Contribution 2]
3. [Contribution 3]

## Methodology
[Describe the method/approach]

## Results
- [Result 1]
- [Result 2]

## Limitations
1. [Limitation 1]
2. [Limitation 2]

## Relevance to Our Work
[How does this relate to our research?]

## Action Items
- [ ] [Action 1]
- [ ] [Action 2]
```

#### Experiment Record Template / 实验记录模板
```markdown
# Experiment: [Name]

## Objective
[What are we testing?]

## Hypothesis
[What do we expect?]

## Setup
- **Date:** YYYY-MM-DD
- **Environment:** [Details]
- **Data:** [Dataset info]

## Procedure
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Results
| Metric | Value | Notes |
|--------|-------|-------|
| [Metric 1] | X | |
| [Metric 2] | Y | |

## Analysis
[What do the results mean?]

## Conclusion
- [ ] Hypothesis supported
- [ ] Hypothesis rejected
- [ ] Inconclusive

## Next Steps
- [ ] [Next 1]
- [ ] [Next 2]
```

---

### 2. Code Templates / 代码模板

#### Script Template / 脚本模板
```python
#!/usr/bin/env python3
"""
[Script Name]

Description: [What does this script do?]
Author: [Name]
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
Version: 1.0.0
"""

import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description='[Description]')
    parser.add_argument('--input', type=str, required=True, help='Input file')
    parser.add_argument('--output', type=str, default='output.json', help='Output file')
    parser.add_argument('--verbose', action='store_true', help='Verbose mode')
    return parser.parse_args()

def main():
    args = parse_args()
    logger.info(f"Starting processing: {args.input}")
    
    # Your code here
    
    logger.info(f"Completed. Output: {args.output}")

if __name__ == '__main__':
    main()
```

#### README Template / README 模板
```markdown
# [Project Name]

**Description:** [One-line description]  
**Version:** 1.0.0  
**Author:** [Name]  
**License:** MIT

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python script.py --input data.json --output result.json
```

## API Reference

[API documentation]

## Examples

[Usage examples]

## Testing

```bash
python -m pytest tests/
```

## Contributing

[Contribution guidelines]

## License

MIT License - see LICENSE file
```

---

### 3. Documentation Templates / 文档模板

#### Meeting Notes Template / 会议笔记模板
```markdown
# Meeting: [Topic]

**Date:** YYYY-MM-DD  
**Attendees:** [Names]  
**Absent:** [Names]

## Agenda
1. [Topic 1]
2. [Topic 2]
3. [Topic 3]

## Discussion

### Topic 1
[Summary of discussion]

### Topic 2
[Summary of discussion]

## Decisions Made
1. [Decision 1]
2. [Decision 2]

## Action Items
| Item | Owner | Due Date | Status |
|------|-------|----------|--------|
| [Item 1] | [Name] | YYYY-MM-DD | ⏳ |
| [Item 2] | [Name] | YYYY-MM-DD | ⏳ |

## Next Meeting
**Date:** YYYY-MM-DD  
**Time:** HH:MM  
**Location:** [Location/Link]
```

#### Project Status Template / 项目状态模板
```markdown
# Project Status: [Project Name]

**Week:** [Week Number]  
**Date Range:** YYYY-MM-DD to YYYY-MM-DD

## Summary
[Brief status summary]

## Completed This Week
- ✅ [Task 1]
- ✅ [Task 2]

## In Progress
- 🔄 [Task 1] (XX% complete)
- 🔄 [Task 2] (XX% complete)

## Blocked
- ⛔ [Task 1] - [Reason]

## Next Week
- [ ] [Task 1]
- [ ] [Task 2]

## Metrics
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| [Metric 1] | X | Y | 🟢 |
| [Metric 2] | X | Y | 🟡 |

## Risks
1. [Risk 1] - [Mitigation]
2. [Risk 2] - [Mitigation]
```

---

### 4. Workflow Templates / 工作流模板

#### Task Execution Workflow / 任务执行工作流
```
1. Task Received
   ↓
2. Understand Requirements
   ↓
3. Plan Approach
   ↓
4. Execute (with checkpoints)
   ↓
5. Quality Check (Critic v5.0)
   ↓
6. Document Results
   ↓
7. User Feedback
   ↓
8. Knowledge Capture
   ↓
9. Git Commit & Push
   ↓
10. Celebration & Next Task
```

#### Code Review Workflow / 代码审查工作流
```
1. Developer completes code
   ↓
2. Self-review checklist
   ↓
3. Create PR/MR
   ↓
4. Automated tests run
   ↓
5. Peer review (use checklist)
   ↓
6. Address feedback
   ↓
7. Approve & Merge
   ↓
8. Deploy
   ↓
9. Monitor
```

---

## 📈 Usage Statistics / 使用统计

| Template | Times Used | Last Used | Effectiveness |
|----------|------------|-----------|---------------|
| Paper Analysis | N | YYYY-MM-DD | X.X / 5 |
| Experiment Record | N | YYYY-MM-DD | X.X / 5 |
| Script Template | N | YYYY-MM-DD | X.X / 5 |
| README Template | N | YYYY-MM-DD | X.X / 5 |
| Meeting Notes | N | YYYY-MM-DD | X.X / 5 |

---

## 🔄 Maintenance / 维护

**Owner:** [Name]  
**Review Frequency:** Monthly  
**Last Review:** YYYY-MM-DD  
**Next Review:** YYYY-MM-DD

### Template Updates
| Date | Template | Change | Author |
|------|----------|--------|--------|
| YYYY-MM-DD | [Template] | [Description] | [Name] |

---

*Template Version:* v1.0  
*Last Updated:* 2026-03-13  
*Usage:* Copy and adapt for each use case
