# 开始数据收集！

**创建日期:** 2026-03-06 20:59  
**状态:** 准备就绪

---

## 🎯 任务

**收集 20-30 篇 LIG 论文，提取 20-50 个数据点**

---

## 📋 快速开始

### 1. 打开数据文件

**文件:** `literature_data.csv`

**位置:** `D:\OpenClaw\workspace\11-research\theory\data\literature_data.csv`

### 2. 开始检索

**Google Scholar:**
```
https://scholar.google.com
```

**检索式:**
```
"laser-induced graphene" electrical conductivity
```

### 3. 下载论文

**目标:** 20-30 篇

**保存到:** `theory/data/pdfs/`

### 4. 提取数据

**从每篇论文提取:**
- P (W)
- v (mm/s)
- d (μm)
- σ (S/m)

**填入 CSV**

---

## 📊 数据模板

```csv
paper_id,P_W,v_mms,d_um,sigma_Sm,atmosphere,substrate,notes,status
LIG_001,10.6,50,100,1.2e5,Air,PI,Example data,To Extract
LIG_002,12.0,40,120,2.5e5,Air,PI,Example data,To Extract
...
```

---

## 📁 相关文件

- `README_data_collection.md` - 详细指南
- `literature_data.csv` - 数据文件
- `scripts/scaling_law_validation.py` - 验证脚本

---

## ⏱️ 预计时间

| 任务 | 时间 |
|------|------|
| 下载论文 | 1-2 小时 |
| 提取数据 | 2-3 小时 |
| 数据整理 | 1 小时 |
| 模型验证 | 1 小时 |
| **总计** | **5-7 小时** |

---

## 🎯 目标

**验证成功标准:**
- 数据点 ≥ 20
- R² > 0.75
- 参数物理意义合理

---

*准备就绪，开始收集！*
