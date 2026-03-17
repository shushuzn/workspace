# LIG 材料机器学习研究项目

**项目名称:** 文献数据挖掘与在线学习结合的 LIG 电导率预测  
**完成时间:** 2026-03-06  
**项目状态:** ✅ 投稿准备完成 (95%)  
**目标期刊:** npj Computational Materials (IF: 12.8)  
**投稿日期:** 2026-03-17 (计划)

## 核心成果

- **R² = 0.801** (超越目标 0.80) ✅
- **从 0.50 到 0.801** (+60.2% 提升) ✅
- **203 样本数据集** (200 文献 + 3 实验) ✅
- **完整在线学习系统** ✅
- **12.5 小时完成研究** ✅

## 目录结构

```
ORGANIZED_PROJECT/
├── 01_Paper_Draft/     # 论文稿件 (V2, 6000 字，6 图表)
├── 02_Data/            # 数据集 (203 样本)
├── 03_Code/            # 代码 (55+ Python 脚本)
├── 04_Models/          # 模型 (30+ 模型文件)
├── 05_Figures/         # 图表 (15+ PNG 文件)
├── 06_Submission/      # 投稿材料 (Cover Letter 等)
└── 07_Documentation/   # 文档资料 (报告、指南等)
```

## 快速开始

### 查看论文

```bash
cd 01_Paper_Draft
cat PAPER_DRAFT_V2.md
```

### 使用数据

```python
import pandas as pd
df = pd.read_csv('02_Data/lig_dataset_200.csv')
```

### 运行在线学习

```bash
python 03_Code/online_learning.py
```

### 加载模型

```python
import joblib
model = joblib.load('04_Models/LIG_GP_online.pkl')
```

## 方法创新

1. **文献数据挖掘:** 80 个数据点自动提取
2. **特征工程优化:** 共线性识别与处理
3. **集成学习框架:** GP+RF+GBT Stacking
4. **在线学习系统:** 实时模型更新

## 性能指标

| 阶段 | 样本数 | R² | MAE (S/m) |
|------|--------|-----|-----------|
| 基线 | 120 | 0.50 | 850 |
| 文献挖掘 | 200 | 0.795 | 485 |
| 集成学习 | 200 | 0.795 | 485 |
| **在线学习** | **203** | **0.801** | **459** |

## 投稿信息

**期刊:** npj Computational Materials  
**影响因子:** 12.8  
**投稿系统:** https://www.editorialmanager.com/npjcompumats/  
**计划投稿日期:** 2026-03-17

## 文件清单

- **论文稿件:** 01_Paper_Draft/PAPER_DRAFT_V2.md
- **数据集:** 02_Data/lig_dataset_200.csv
- **代码:** 03_Code/ (6 个核心脚本)
- **模型:** 04_Models/ (3 个核心模型)
- **图表:** 05_Figures/ (6 个核心图表)
- **投稿材料:** 06_Submission/ (5 个文件)
- **文档:** 07_Documentation/ (3 个报告)

## GitHub 仓库

完整项目已开源:
https://github.com/shushuzn/obsidian-sync/tree/master/research

**许可:**
- 代码：MIT License
- 数据：CC BY 4.0
- 模型：MIT License

## 时间线

- **03-06 00:00:** 项目启动 (R²=0.50)
- **03-06 02:40:** 文献挖掘完成 (R²=0.795)
- **03-06 11:25:** 在线学习突破 (R²=0.801)
- **03-06 12:38:** 文件整合完成
- **03-06 12:40:** 项目完成 (95%)
- **03-07:** 填写 Cover Letter + 核实审稿人
- **03-17:** 投稿日 🎯

## 联系方式

**GitHub:** https://github.com/shushuzn/obsidian-sync  
**问题反馈:** 请在 GitHub 提交 Issue

---

*项目从启动到文件整合完成，总用时约 12.5 小时。*
*所有数据、代码、模型已开源，确保可复现性。*
