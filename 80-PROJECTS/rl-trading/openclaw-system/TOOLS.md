# TOOLS.md - Local Notes

**Last Updated:** 2026-03-06

Skills define _how_ tools work. This file is for _your_ specifics.

---

## 馃洜锔?Local Setup

### Runtime
- **Platform:** OpenClaw on Windows NT 10.0.26200
- **Node:** v24.14.0
- **Shell:** PowerShell
- **Workspace:** `D:\OpenClaw\workspace`

### 鈿狅笍 Performance Constraints
- **馃毇 NO n8n** - Causes severe CPU heating
- **Preferred:** Lightweight PowerShell scripts, scheduled tasks
- **Monitor:** CPU usage, temperature (keep it cool!)

### Model Configuration
- **Default Model:** `bailian/qwen3.5-plus`
- **Context Tokens:** 550k (auto-session rotation)

### Channel
- **Provider:** Feishu webchat
- **Chat Type:** Direct message

---

## 📁 Folder Structure

Workspace uses numeric prefix organization:

| Prefix | Category | Example |
|--------|----------|---------|
| `00-09` | Core Config | `03-config/` |
| `10-19` | Knowledge | `13-memory/` |
| `20-29` | Data | `21-reports/` |
| `30-39` | Tools | `30-scripts/` |
| `40-49` | Collectors | `40-arxiv/`, `41-medium/` |
| `60-69` | Knowledge Cards | `60-knowledge-cards/` |
| `90-99` | Archive | `90-archive/` |

See `15-docs/FOLDER-INDEX.md` for full details.

---

## 📖 Academic Integrity Rules (2026-03-10)

**Knowledge Card System v3.1 - Reference Authenticity Requirements**

### Core Principles
- ✅ All references must be real and verifiable
- ✅ No fabrication of any literature information
- ✅ Prioritize textbooks and curriculum standards

### Verification Checklist
Must verify when creating knowledge cards:
- [ ] Does the textbook really exist?
- [ ] Is the author real?
- [ ] Is the publisher real?
- [ ] Is the publication year accurate?
- [ ] Is the curriculum standard officially published?
- [ ] Can the journal paper be found?
- [ ] Are volume and issue numbers accurate?
- [ ] Are page numbers accurate?

**If any item cannot be verified, delete the reference!**

### Recommended Sources
1. **PEP Textbooks:** High school textbooks published by People's Education Press
2. **Curriculum Standards:** 2017 edition standards issued by Ministry of Education of China
3. **Classic Works:** Zhao Kaihua's "New Concept Physics", Zhang Daozhen's "English Grammar", etc.

### Related Files
- `60-knowledge-cards/README.md` - Knowledge card system specifications
- `60-knowledge-cards/` - Knowledge cards directory

---

## 馃敡 Tool Preferences

### TTS
- No ElevenLabs sag configured yet

### Browser
- Default target: `host`
- Profile: `openclaw` (isolated)

### Memory
- **Location:** `13-memory/MEMORY.md`
- **Daily Notes:** `13-memory/YYYY-MM-DD.md`
- **Distiller:** Weekly auto-distill (Sunday 5 AM)

---

## 馃搵 Active Skills

### Core Skills
| Skill | Function |
|-------|----------|
| `proactive-agent-lite` | **Proactive behavior** (memory arch, reverse prompting, self-healing) |
| `task-manager` | Task planning & execution (10-min rule, priority-driven) |
| `ai-research-os` | Paper analysis |
| `arxiv-daily` | Daily paper collection (38 fields) |
| `medium-watcher` | Medium article monitoring |
| `memory-distiller` | Knowledge distillation (weekly) |
| `knowledge-graph` | Graph building |
| `github-sync` | Auto Git sync |
| `domain_ranker_v2` | **学科学术段位评价** (11 维度，8 段位×1000 级) |
| `knowledge-card-generator` | **PDF→HTML 知识卡片** (元数据/章节/参考文献提取) |

### Disabled Skills
| Skill | Reason |
|-------|--------|
| `n8n` | 馃毇 CPU overheating - replaced with lightweight scripts |

---

## 馃攼 Security Notes

- No external actions without confirmation
- Private data stays local
- Destructive commands require explicit approval

---

## 🏆 学科学术段位系统

**文档:** `15-docs/Domain-Ranking-System-v2.md`  
**脚本:** `30-scripts/domain_ranker_v2.py`

### 快速使用

```bash
# 评估 LIG 领域
py domain_ranker_v2.py --evaluate LIG

# 比较所有领域
py domain_ranker_v2.py --compare

# 评估自定义领域
py domain_ranker_v2.py --evaluate MyDomain
```

### 11 个评价维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 理论基础 | 15% | 理论体系完整性 |
| 技术成熟度 | 15% | TRL 等级 |
| 学术影响力 | 12% | 论文引用 |
| 应用广度 | 10% | 跨领域应用 |
| 人才储备 | 8% | 研究组数量 |
| 资金投入 | 5% | 年度经费 |
| 创新能力 | 10% | 原创性/突破性 |
| 国际合作 | 8% | 跨国研究合作 |
| 教育普及 | 8% | 教材/课程收录 |
| 开源贡献 | 7% | 开源工具/数据 |
| 产业转化 | 7% | 商业化应用 |

### 当前排名

| 排名 | 领域 | 段位 | 等级 | 进度 |
|------|------|------|------|------|
| 1 | DeepLearning | 黑铁 | 717 级 | 71.7% |
| 2 | Graphene | 黑铁 | 647 级 | 64.7% |
| 3 | LIG | 黑铁 | 473 级 | 47.3% |

---

## 📊 Output Format (指标驱动)

**All task responses must include:**

```markdown
**[Mode]** Hardening/Optimization/Acceleration/Recovery
**[North Star]** X% → Y% (+Z%)
**[Supporting Metrics]** ...
**[Risk Level]** 低/中/高

**[Task]** #ID Task Name ✅/⏸️/❌
**[验收标准]** 5 项 (≥5 个要求)

**[不足]** (≥5 个)
1. ...
2. ...

**[下一步]** (≥5 个)
1. ...
2. ...

**[Do]** ...
**[Verify]** ...
**[Next]** ...
```

**Rules:**
- 不足 ≥5 个
- 下一步 ≥5 个
- 简洁、结构化、指标驱动
- 避免冗长输出

---

*Update this file when you add new tools or change configurations.*

---

## 馃敊 Backlinks

**Documents linking here:**
- [[README]] - README
- [[SOUL]] - SOUL
- [[15-docs\LINK_INDEX]] - LINK_INDEX
- [[90-archive\知识库索引]] - 知识库索引

