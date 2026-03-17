# CNT 性能预测研究计划

**启动日期:** 2026-03-06  
**方向:** B1. 碳纳米管 (CNT) 性能预测  
**并行任务:** C3. 可解释 AI (SHAP 分析)

---

## 📊 研究目标

### 主要目标

1. **数据集:** 收集 300+ CNT 电导率/力学性能数据
2. **模型:** GP 回归，目标 R² > 0.75
3. **可解释性:** SHAP 分析识别关键特征
4. **产出:** 2 篇论文 (应用 + 方法)

---

## 📋 任务分解

### 阶段 1: 文献调研与数据收集 (2-3 周)

#### 任务 1.1: 文献检索

**数据库:**
- Web of Science
- Scopus
- Google Scholar
- arXiv

**检索词:**
```
("carbon nanotube" OR CNT OR "carbon nanotubes")
AND ("electrical conductivity" OR "electronic properties" OR "mechanical properties")
AND ("machine learning" OR "prediction" OR "model*" OR "regression")
```

**纳入标准:**
- 明确报告电导率或力学性能
- 提供完整制备参数
- 同行评议论文或预印本

**目标:** 40-50 篇核心论文

---

#### 任务 1.2: 数据提取

**提取字段:**

| 类别 | 字段 | 单位 |
|------|------|------|
| 结构参数 | 直径 (d) | nm |
| | 长度 (l) | μm |
| | 层数 (n) | - |
| | 手性 (n,m) | - |
| 制备参数 | CVD 温度 | °C |
| | 催化剂类型 | - |
| | 生长时间 | min |
| | 碳源气体 | - |
| 性能指标 | 电导率 | S/m |
| | 拉伸强度 | GPa |
| | 杨氏模量 | GPa |

**目标:** 300+ 数据点

---

#### 任务 1.3: 数据整理

- 单位统一
- 异常值检测
- 缺失值处理
- 特征工程

**输出:** `cnt_dataset_v1.csv`

---

### 阶段 2: 模型开发 (2-3 周)

#### 任务 2.1: 基线模型

复用 LIG 研究的 GP 框架:
- 相同核函数 (RBF + WhiteKernel)
- 相同评估指标 (R², MAE, RMSE)
- 相同不确定性量化

**代码复用率:** ~80%

---

#### 任务 2.2: 特征选择

**候选特征:**
1. 直径 (d)
2. 长径比 (l/d)
3. 层数 (n)
4. CVD 温度
5. 生长时间
6. 催化剂类型 (编码)

**方法:**
- 相关性分析
- 递归特征消除 (RFE)
- 基于 GP 长度尺度

---

#### 任务 2.3: 模型优化

- 核函数调优
- 超参数优化
- 集成学习 (可选)

**目标:** R² > 0.75

---

### 阶段 3: 可解释性分析 (1-2 周)

#### 任务 3.1: SHAP 分析

**方法:** KernelSHAP (模型无关)

**分析内容:**
- 特征重要性排序
- SHAP 依赖图
- 特征交互效应

**工具:** `shap` Python 库

---

#### 任务 3.2: 物理洞见

从 SHAP 分析中提取:
- 哪些结构参数最关键？
- 是否存在阈值效应？
- 特征之间是否有交互？

**预期发现:**
- 直径 vs 电导率关系
- 长径比的影响
- 最优制备条件

---

### 阶段 4: 论文撰写 (2-3 周)

#### 论文 1: 应用导向

**标题:** Machine Learning-Assisted Prediction of Carbon Nanotube Electrical Conductivity Using Gaussian Process Regression

**目标期刊:** Carbon (IF=11.3) 或 ACS Nano (IF=18.1)

**结构:**
- 引言：CNT 应用 + ML 需求
- 方法：数据收集 + GP 模型
- 结果：预测性能 + 对比
- 讨论：SHAP 分析 + 物理洞见
- 结论

---

#### 论文 2: 方法/数据导向

**标题:** A Curated Dataset and Benchmark for Machine Learning Prediction of Carbon Nanotube Properties

**目标期刊:** Scientific Data (IF=9.8) 或 Journal of Chemical Information and Modeling (IF=5.6)

**内容:**
- 数据集详细描述
- 基准测试结果
- 数据质量分析
- 使用指南

---

## 📅 时间线

| 阶段 | 任务 | 开始 | 结束 | 里程碑 |
|------|------|------|------|--------|
| 1 | 文献调研 | W1 | W2 | 50 篇论文 |
| 1 | 数据收集 | W2 | W3 | 300+ 数据点 |
| 2 | 基线模型 | W4 | W4 | GP 运行 |
| 2 | 特征选择 | W5 | W5 | 最终特征 |
| 2 | 模型优化 | W6 | W6 | R² > 0.75 |
| 3 | SHAP 分析 | W7 | W7 | 特征重要性 |
| 3 | 物理解释 | W8 | W8 | 关键发现 |
| 4 | 论文 1 撰写 | W9 | W11 | 初稿完成 |
| 4 | 论文 2 撰写 | W11 | W13 | 初稿完成 |

**总计:** 13 周 (~3 个月)

---

## 📁 文件结构

```
11-research/
├── cnt-research/
│   ├── data/
│   │   ├── cnt_dataset_v1.csv
│   │   └── data_description.md
│   ├── scripts/
│   │   ├── cnt_gp_run.py
│   │   ├── cnt_feature_selection.py
│   │   └── cnt_shap_analysis.py
│   ├── figures/
│   │   └── (CNT 相关图表)
│   ├── models/
│   │   └── (CNT GP 模型)
│   └── paper/
│       ├── cnt_paper_draft.md
│       └── cnt_dataset_paper.md
└── docs/
    ├── CNT_RESEARCH_PLAN.md (本文件)
    └── NEXT_RESEARCH_DIRECTIONS.md
```

---

## 🔧 技术栈

| 用途 | 工具 | 备注 |
|------|------|------|
| 数据处理 | pandas, numpy | 复用 LIG 研究 |
| 模型 | scikit-learn GP | 复用 LIG 研究 |
| 可视化 | matplotlib | 复用 LIG 研究 |
| SHAP 分析 | shap | 新安装 |
| 文献管理 | Zotero/EndNote | 用户选择 |

---

## 📊 与 LIG 研究的对比

| 维度 | LIG 研究 | CNT 研究 (计划) |
|------|----------|----------------|
| 数据量 | 200 样本 | 300+ 样本 |
| 特征数 | 3 个 | 6 个 |
| 模型 | GP | GP (复用) |
| 目标 R² | 0.80 | 0.75 |
| 可解释性 | 长度尺度 | SHAP + 长度尺度 |
| 论文数 | 1 篇 | 2 篇 |

---

## ✅ 立即可做的任务

### 今天 (2026-03-06)

- [x] 研究规划 (已完成)
- [ ] 安装 `shap` 库
- [ ] 开始文献检索

### 本周

- [ ] 收集 20 篇核心论文
- [ ] 设计数据提取模板
- [ ] 创建项目文件夹

### 下周

- [ ] 完成 50 篇论文筛选
- [ ] 提取 100+ 数据点
- [ ] 初步数据分析

---

## 🎯 成功标准

| 指标 | 目标值 | 状态 |
|------|--------|------|
| 数据点 | 300+ | ⏳ |
| R² | > 0.75 | ⏳ |
| SHAP 发现 | 3+ 关键洞见 | ⏳ |
| 论文 | 2 篇 | ⏳ |

---

*创建日期：2026-03-06*  
*状态：启动准备中*
