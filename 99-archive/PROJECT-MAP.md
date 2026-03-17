# 🗺️ Project Map - 项目地图

**Quick visual guide to find all projects**

---

## 🎯 Find Projects Fast

### Method 1: Interactive Menu (EASIEST!)
```bash
find-project.bat
```
→ Shows menu, pick number, opens folder!

### Method 2: Direct Access
```bash
# TON Hackathon (Most Important!)
cd 50-projects\50-ton-hackathon-2026

# Knowledge Card Generator
cd knowledge-card-generator

# OpenClaw-RL
cd OpenClaw-RL
```

### Method 3: View Index
```bash
start PROJECTS-INDEX.md
```

---

## 📊 Project Locations Map

```
D:\OpenClaw\workspace/
│
├── 🟢 ACTIVE PROJECTS (活跃项目)
│   │
│   ├── 50-projects/
│   │   └── 50-ton-hackathon-2026/    ← ⭐ SUBMIT NOW!
│   │
│   ├── knowledge-card-generator/      ← Deployed on Render
│   └── OpenClaw-RL/                   ← Planning
│
├── ✅ COMPLETED PROJECTS (已完成)
│   │
│   ├── knowledge-card-package/        ← Package complete
│   └── knowledge-card-android/        ← Android app
│
└── 📄 TEMPLATES (模板)
    └── projects/
        └── PROJECT_TEMPLATE.md        ← New project template
```

---

## 🎨 Visual Project Board

| Priority | Project | Location | Status | Action |
|----------|---------|----------|--------|--------|
| 🔴 URGENT | TON Hackathon | `50-projects/50-ton-hackathon-2026/` | 95% | Submit! |
| 🟡 MEDIUM | Knowledge Card Generator | `knowledge-card-generator/` | Deployed | Monitor |
| 🟡 MEDIUM | OpenClaw-RL | `OpenClaw-RL/` | Planning | Define |
| 🟢 LOW | Knowledge Card Package | `knowledge-card-package/` | Done | Archive |
| 🟢 LOW | Knowledge Card Android | `knowledge-card-android/` | Done | Archive |

---

## 🔍 Project Search Commands

### Find by Name
```bash
# Search all project folders
dir /b | findstr /i project
```

### Find by File
```bash
# Find all READMEs (projects)
dir /s /b README.md

# Find all package.json (Node.js projects)
dir /s /b package.json

# Find all requirements.txt (Python projects)
dir /s /b requirements.txt
```

### Find by Status
```bash
# Active projects
dir 50-projects /b

# Completed projects
dir /b | findstr /i "package android"
```

---

## 📋 Project Directory Tree

```
workspace/
│
├── 50-projects/                          [MAIN PROJECTS FOLDER]
│   └── 50-ton-hackathon-2026/            [⭐ ACTIVE - SUBMIT NOW]
│       ├── README.md
│       ├── bot.js
│       ├── package.json
│       └── demo-mode.js
│
├── knowledge-card-generator/             [✅ DEPLOYED]
│   ├── README.md
│   ├── server.js
│   ├── package.json
│   └── .env.example
│
├── OpenClaw-RL/                          [🟡 PLANNING]
│   ├── README.md
│   └── (planning docs)
│
├── knowledge-card-package/               [✅ COMPLETE]
│   ├── README.md
│   └── package files
│
├── knowledge-card-android/               [✅ COMPLETE]
│   ├── README.md
│   └── Android app files
│
└── projects/                             [TEMPLATES ONLY]
    └── PROJECT_TEMPLATE.md               [Use for new projects]
```

---

## 🎯 Quick Decision Tree

```
Want to work on a project?
    │
    ├─→ Submit hackathon? 
    │   └─→ 50-projects/50-ton-hackathon-2026/
    │
    ├─→ Check deployed app?
    │   └─→ knowledge-card-generator/
    │
    ├─→ Start new project?
    │   └─→ projects/PROJECT_TEMPLATE.md
    │
    └─→ Not sure?
        └─→ Run: find-project.bat
```

---

## 💡 Pro Tips

### 1. Use the Finder Script
```bash
find-project.bat
# Interactive menu - easiest!
```

### 2. Bookmark Important Paths
```
TON Hackathon: 50-projects/50-ton-hackathon-2026/
Knowledge Card: knowledge-card-generator/
New Projects: 50-projects/[name]/
```

### 3. Keep Projects Organized
- New projects → `50-projects/`
- Web projects → `51-web/`
- Templates → `projects/`
- Archive → `99-archive/`

### 4. Update Index
When creating new project, update `PROJECTS-INDEX.md`

---

## 📞 Quick Reference

| I want to... | Command |
|--------------|---------|
| Open TON project | `find-project.bat` → [1] |
| See all projects | `start PROJECTS-INDEX.md` |
| Create new project | `find-project.bat` → [7] |
| Find project files | `dir /s /b README.md` |
| Quick open folder | `explorer 50-projects\50-ton-hackathon-2026` |

---

*Projects organized and easy to find!* ✅

**Last Updated:** 2026-03-13
