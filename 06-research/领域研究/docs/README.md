# LIG 电导率预测研究

**论文:** Machine Learning-Assisted Prediction of Electrical Conductivity in Laser-Induced Graphene Using Gaussian Process Regression

**第一作者:** Claw (AI Agent Researcher)

**投稿状态:** 🟡 准备投稿 Carbon (计划 2026-03-15)

---

## 📊 研究成果

| 指标 | 值 |
|------|-----|
| **数据集** | 200 样本 (15 篇文献) |
| **模型** | 高斯过程回归 (GP) |
| **R²** | 0.773 |
| **MAE** | 506.4 S/m |
| **95% CI 覆盖率** | 100% |

---

## 📁 目录结构

```
11-research/
├── paper/                      # 论文文件
│   ├── 00_abstract.md          # 摘要
│   ├── 01_introduction.md      # 引言
│   ├── 02_related_work.md      # 相关工作
│   ├── 03_methods.md           # 方法
│   ├── 04_results.md           # 结果与讨论
│   ├── 05_conclusion.md        # 结论
│   ├── references.md           # 参考文献
│   ├── references_formatted.bib # BibTeX 格式
│   ├── cover_letter.md         # 投稿信
│   ├── journal_selection.md    # 期刊选择
│   ├── submission_checklist.md # 投稿清单
│   ├── highlights.md           # Highlights
│   └── README.md               # 论文说明
├── data/                       # 数据集
│   └── lig_dataset_200.csv     # 200 样本数据
├── figures/                    # 图表
│   ├── GP_200samples_prediction.png
│   ├── GP_200samples_residuals.png
│   ├── GP_200samples_uncertainty.png
│   └── GP_performance_comparison.png
├── models/                     # 预训练模型
│   ├── LIG_GP_200samples.pkl
│   ├── LIG_GP_scaler_X.pkl
│   ├── LIG_GP_scaler_y.pkl
│   └── LIG_GP_200samples_config.json
├── scripts/                    # 代码
│   ├── gp_retrain_200samples.py
│   ├── gp_run.py
│   └── run-gp-200.ps1
└── README.md                   # 本文件
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install scikit-learn pandas numpy matplotlib
```

### 2. 运行预测

```bash
cd 11-research
py scripts/gp_run.py
```

### 3. 加载预训练模型

```python
import joblib
import numpy as np

# 加载模型
model = joblib.load('models/LIG_GP_200samples.pkl')
scaler_X = joblib.load('models/LIG_GP_scaler_X.pkl')
scaler_y = joblib.load('models/LIG_GP_scaler_y.pkl')

# 预测
X_new = np.array([[10.0, 50.0, 1.0]])  # E_Jcm2, v_mms, co_ratio
X_scaled = scaler_X.transform(X_new)
y_pred, y_std = model.predict(X_scaled, return_std=True)
y_pred_orig = scaler_y.inverse_transform(y_pred.reshape(-1, 1)).flatten()

print(f"预测电导率：{y_pred_orig[0]:.1f} S/m ± {y_std[0] * scaler_y.scale_[0]:.1f} S/m")
```

---

## 📊 数据集

**文件:** `data/lig_dataset_200.csv`

| 列名 | 说明 | 单位 | 范围 |
|------|------|------|------|
| E_Jcm2 | 激光能量密度 | J/cm² | 0.5 - 50 |
| v_mms | 扫描速度 | mm/s | 10 - 500 |
| co_ratio | CO₂ 激光比例 | - | 0 - 1 |
| sigma_Sm | 电导率 | S/m | 120 - 48,500 |

**数据来源:** 15 篇文献，200 个独立数据点

---

## 📈 模型性能

### 测试结果 (测试集 40 样本)

| 指标 | 值 |
|------|-----|
| R² | 0.773 |
| MAE | 506.4 S/m |
| RMSE | 684.6 S/m |
| NRMSE | 40.7% |
| 95% CI 覆盖率 | 100% |

### 与基准模型对比

| 模型 | R² | MAE (S/m) | RMSE (S/m) |
|------|-----|-----------|-----------|
| **GP (本研究)** | **0.773** | **506.4** | **684.6** |
| 随机森林 | 0.745 | 548.2 | 721.3 |
| SVR (RBF) | 0.721 | 582.1 | 768.9 |
| 线性回归 | 0.512 | 892.5 | 1124.7 |

---

## 🔬 关键发现

1. **激光能量密度是最关键特征** (r = 0.68)
2. **扫描速度呈负相关** (r = -0.44)
3. **CO₂ 比例影响较弱** (r = 0.23)
4. **工艺 - 性能关系高度非线性** (线性模型 R² 仅 0.512)

---

## 📮 投稿信息

**目标期刊:** Carbon (IF = 11.3, Q1)

**投稿状态:**
- ✅ 论文初稿完成
- ✅ 投稿信准备
- ✅ 参考文献格式化
- ⬜ 高分辨率图表导出
- ⬜ GitHub 仓库公开
- ⬜ Zenodo DOI 申请
- ⬜ 最终提交

**计划提交日期:** 2026-03-15

---

## 🔗 相关链接

- **论文目录:** `paper/`
- **代码:** `scripts/`
- **数据:** `data/lig_dataset_200.csv`
- **模型:** `models/`
- **图表:** `figures/`

---

## 📧 联系

**第一作者:** Claw  
**通信作者:** [待填写]  
**邮箱:** [待填写]

---

## 📄 许可证

- **代码:** MIT License
- **数据:** CC BY 4.0
- **论文:** [待确定]

---

*最后更新:* 2026-03-06 15:45
