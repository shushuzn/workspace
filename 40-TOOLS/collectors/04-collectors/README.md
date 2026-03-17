# 04-collectors - Data Collectors

**Purpose:** Automated data collection from arXiv, Medium, Reddit, Twitter, HackerNews

**Last Updated:** 2026-03-13  
**Version:** v2.0

---

## 📁 Directory Structure

```
04-collectors/
├── arxiv/                              # arXiv collection
│   ├── arxiv-research-orchestrator.ps1
│   └── arxiv_ops_cli.py
├── arxiv-collector.py                  # v1 - Single category
├── arxiv-collector-v2.py               # v2 - Multi-category ⭐
├── arxiv-to-openclaw-integration.py    # Integration script
├── setup-scheduled-task.bat            # Auto-run setup
├── medium/                             # Medium monitoring
├── reddit/                             # Reddit tracking
├── x-twitter/                          # Twitter monitoring
├── hn/                                 # HackerNews
└── README.md                           # This file
```

---

## 🚀 Quick Start

### arXiv Collector v2 (Recommended)

```bash
# Navigate to directory
cd 30-scripts-tools\04-collectors

# Run collector
python arxiv-collector-v2.py

# Output:
# - Markdown notes: D:\obsidian\Vault\Arxiv\
# - JSON data: 40-collectors\arxiv\data\
```

### Setup Daily Auto-Run

```bash
# Run as Administrator
setup-scheduled-task.bat

# Task runs daily at 8:00 AM
```

### Integrate with OpenClaw

```bash
# Download PDFs and create analysis manifest
python arxiv-to-openclaw-integration.py
```

---

## ✨ Features

### arXiv Collector v2

| Feature | v1 | v2 |
|---------|----|----|
| Categories | 1 | 8 |
| Keywords | 0 | 6 |
| Output Format | Markdown | Markdown + JSON |
| Deduplication | ❌ | ✅ |
| Papers/Run | 15 | 400+ |
| Proxy Support | ✅ | ✅ |

### Supported Categories

- `cs.AI` - Artificial Intelligence
- `cs.LG` - Machine Learning
- `cs.CL` - Computation and Language
- `cs.CV` - Computer Vision
- `cs.NE` - Neural and Evolutionary Computing
- `physics.chem-ph` - Chemical Physics
- `cond-mat.mtrl-sci` - Materials Science
- `quant-ph` - Quantum Physics

### Supported Keywords

- Graph neural network molecular
- Transformer drug discovery
- Conductivity prediction
- Machine learning materials science
- Deep learning protein folding
- AI scientific discovery

---

## 📊 Configuration

### Edit `arxiv-collector-v2.py`

```python
# Categories to fetch
CATEGORIES = [
    'cs.AI',
    'cs.LG',
    'cs.CL',
    # Add more...
]

# Keywords to search
KEYWORDS = [
    'your keyword here',
    # Add more...
]

# Max papers per category/keyword
MAX_PAPERS = 50

# Enable deduplication
ENABLE_DEDUP = True
```

### Proxy Configuration

```python
# Clash proxy (default)
PROXY_ADDR = "http://127.0.0.1:7897"
```

---

## 📁 Output

### Markdown (Obsidian)

**Location:** `D:\obsidian\Vault\Arxiv\`

**Format:**
```markdown
# Paper Title

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/xxxx
- **Authors:** Author1, Author2
- **Categories:** cs.AI
- **Published:** 2026-03-13
- **Collected:** 2026-03-13 22:00:00

## Abstract

[Abstract text...]

## Tags

#AI #MachineLearning #Research #Arxiv
```

### JSON (Analysis)

**Location:** `40-collectors\arxiv\data\`

**Files:**
- `graph_neural_network_molecular_20260313.json`
- `transformer_drug_discovery_20260313.json`
- `conductivity_prediction_20260313.json`
- `seen_ids.json` (deduplication database)

**Format:**
```json
{
  "source": "graph neural network molecular",
  "collectedAt": "2026-03-13T22:00:00",
  "totalPapers": 50,
  "papers": [
    {
      "id": "https://arxiv.org/abs/2401.12345",
      "title": "Paper Title",
      "link": "https://arxiv.org/abs/2401.12345",
      "summary": "...",
      "authors": ["Author1", "Author2"],
      "categories": ["cs.AI"]
    }
  ]
}
```

---

## 🔄 Workflow

### Basic Collection

```
arxiv-collector-v2.py
    ↓
Fetch from arXiv API
    ↓
Deduplicate (seen_ids.json)
    ↓
Save Markdown + JSON
    ↓
Update deduplication database
```

### Full Integration

```
arxiv-collector-v2.py
    ↓
arxiv-to-openclaw-integration.py
    ↓
Download PDFs (top 10)
    ↓
Create analysis manifest
    ↓
OpenClaw PDF Parser
    ↓
OpenAI Analysis
    ↓
Memory System
```

---

## ⏰ Scheduled Task

### Setup

```bash
# Run as Administrator
setup-scheduled-task.bat
```

### Task Details

| Property | Value |
|----------|-------|
| Name | arXiv-Daily-Collector |
| Trigger | Daily at 8:00 AM |
| Action | python arxiv-collector-v2.py |
| Working Directory | 30-scripts-tools\04-collectors |

### Management Commands

```bash
# Check status
schtasks /Query /TN "arXiv-Daily-Collector"

# Run manually
schtasks /Run /TN "arXiv-Daily-Collector"

# Delete task
schtasks /Delete /TN "arXiv-Daily-Collector" /F
```

---

## 📈 Performance

### Typical Run

| Metric | Value |
|--------|-------|
| Categories | 8 |
| Keywords | 6 |
| Total Papers | 400-500 |
| New Papers | 200-300 |
| Duplicates | 100-200 |
| Run Time | 60-90 seconds |
| Network Requests | 14 |
| Output Size | ~5MB |

### Resource Usage

- **CPU:** Low (<10%)
- **Memory:** Low (<200MB)
- **Network:** Moderate (~50MB)
- **Disk:** Low (~5MB/run)

---

## 🛠️ Troubleshooting

### Connection Timeout

**Issue:** `Read timed out`

**Solution:**
1. Check proxy is running (Clash)
2. Increase timeout in code
3. Reduce MAX_PAPERS

### Module Not Found

**Issue:** `ModuleNotFoundError: No module named 'feedparser'`

**Solution:**
```bash
pip install feedparser requests
```

### Unicode Error

**Issue:** `UnicodeEncodeError`

**Solution:** Already fixed with UTF-8 encoding wrapper

### Permission Denied (Scheduled Task)

**Issue:** Task fails to run

**Solution:**
1. Run `setup-scheduled-task.bat` as Administrator
2. Check Task Scheduler permissions

---

## 🔗 Integration

### With Obsidian

- Markdown files auto-save to Obsidian vault
- Tags enable easy searching
- Metadata supports linking

### With OpenClaw

```bash
# 1. Collect papers
python arxiv-collector-v2.py

# 2. Download PDFs + Create manifest
python arxiv-to-openclaw-integration.py

# 3. Analyze with OpenClaw
# (Use OpenClaw PDF parser and analysis tools)
```

### With Knowledge Cards

```bash
# 1. Collect papers → JSON
# 2. Send to Knowledge Card Generator
# 3. Get HTML cards for sharing
```

---

## 📊 Statistics

### First Run (2026-03-13)

```
Categories:
  cs.AI: 50 papers ✅
  cs.LG: Timeout ⚠️
  cs.CL: 50 papers ✅
  cs.CV: 50 papers ✅
  cs.NE: 50 papers ✅
  physics.chem-ph: 50 papers ✅
  cond-mat.mtrl-sci: 50 papers ✅
  quant-ph: 50 papers ✅

Keywords:
  graph neural network molecular: 50 papers ✅
  transformer drug discovery: 50 papers ✅
  conductivity prediction: 50 papers ✅
  machine learning materials science: 50 papers ✅
  deep learning protein folding: 50 papers ✅
  AI scientific discovery: 50 papers ✅

Total: 550 papers
New: 250 papers
Duplicates: 300 papers
```

---

## 🎯 Best Practices

### 1. Run Frequency
- **Daily:** Recommended for active research
- **Weekly:** Minimum for staying updated
- **On-demand:** For specific topics

### 2. Deduplication
- Keep `seen_ids.json` for continuity
- Reset periodically for comprehensive reviews
- Backup before major changes

### 3. Storage Management
- Archive old JSON files monthly
- Keep recent Markdown notes
- Compress PDFs if needed

### 4. Category Selection
- Start with 3-5 core categories
- Expand based on research needs
- Remove unused categories

---

## 📝 Changelog

### v2.0 (2026-03-13)
- ✅ Multi-category support (8 categories)
- ✅ Multi-keyword search (6 keywords)
- ✅ JSON + Markdown dual output
- ✅ Auto-deduplication
- ✅ OpenClaw integration
- ✅ Scheduled task support
- ✅ All documentation in English

### v1.0 (Previous)
- Single category (cs.AI)
- Markdown output only
- No deduplication
- 15 papers/run

---

## 📞 Support

### Issues
- Check proxy configuration
- Verify Python dependencies
- Review error logs

### Enhancement Ideas
- Add more categories
- PDF auto-download
- Summary generation
- Research trend analysis

---

*Last Updated:* 2026-03-13  
*Version:* v2.0  
*Maintainer:* OpenClaw Team
