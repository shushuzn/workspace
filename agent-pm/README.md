# 🎯 Product Manager Agent

**版本:** v3.0-Full  
**定位:** 独立产品管理 Agent  
**核心理念:** 产品价值第一，整洁度是基础

---

## 📁 文件结构

```
agent-pm/                              # PM Agent 主程序和数据
├── agent-product-manager.py           # 主程序（唯一入口）
├── README.md                          # 项目说明
├── USAGE.md                           # 使用指南
├── config/
│   └── config.json                    # 配置文件
├── data/
│   ├── pm-state.json                  # 运行状态
│   └── pm-history.json                # 决策历史
└── reports/
    ├── product-analysis/
    ├── cleanliness-reports/
    └── roadmaps/

30-scripts-tools/                      # 工具脚本（可复用）
├── pm-duplicate-analyzer.py           # 重复文件夹分析工具
└── pm-merge-folders.py                # 文件夹合并工具
```

---

## 🚀 快速开始

### 运行 PM Agent（主程序）
```bash
cd D:\OpenClaw\workspace\agent-pm
python agent-product-manager.py --run
```

### 使用工具脚本
```bash
cd D:\OpenClaw\workspace
python 30-scripts-tools/pm-duplicate-analyzer.py
python 30-scripts-tools/pm-merge-folders.py
```

---

## 📊 功能

### 主程序 (`agent-product-manager.py`)
- 产品价值分析
- 整洁度检查
- 综合报告生成

### 工具脚本 (`30-scripts-tools/`)
- 重复文件夹分析
- 文件夹合并（P0/P1/P2）

---

**PM Agent v3.0** | 产品价值第一 | 整洁度基础
