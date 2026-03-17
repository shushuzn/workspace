# 科研文件命名规范 v4 (领域优先)

**创建日期:** 2026-03-07 00:36  
**来源:** 用户提供的专业科研规范  
**状态:** ✅ 强制执行  
**版本:** v4.0

---

## 🎯 核心设计原则

**领域 (Domain) 放在最前面** - 符合科研数据仓库标准

**原因:**
1. 第一层分类是学科领域
2. 然后才是文件类型
3. 再往后是项目与内容

**好处:**
- ✅ 同领域文件会自动聚在一起
- ✅ 数据库/文件系统更容易按学科管理
- ✅ 跨项目检索更方便

---

## 📋 总体结构 (7 字段)

```
DOMAIN_TYPE_PROJECT_SUBJECT_METHOD_DATE_VERSION.EXT
```

| 字段 | 含义 | 示例 |
|------|------|------|
| `DOMAIN` | 学科领域 | `CS`, `BIO`, `MED` |
| `TYPE` | 文件类型 | `DAT`, `EXP`, `ANA` |
| `PROJECT` | 项目 | `LLMAlignment`, `GeneExpression` |
| `SUBJECT` | 研究对象 | `RewardDataset`, `RNAseq` |
| `METHOD` | 方法 | `HumanPref`, `PCA` |
| `DATE` | 日期 | `2026-03-01` |
| `VERSION` | 版本 | `v1`, `v1.0` |

---

## 🔤 1. 学科领域 (DOMAIN)

**放在最前面**

| 代码 | 领域 | 英文 |
|------|------|------|
| `CS` | 计算机/AI | Computer Science |
| `BIO` | 生物 | Biology |
| `MED` | 医学 | Medicine |
| `CHEM` | 化学 | Chemistry |
| `PHY` | 物理 | Physics |
| `ENV` | 环境 | Environmental Science |
| `GEO` | 地理 | Geography |
| `ECO` | 经济 | Economics |
| `SOC` | 社会科学 | Social Science |
| `PSY` | 心理学 | Psychology |
| `LING` | 语言学 | Linguistics |
| `HIST` | 历史 | History |
| `MAT` | 材料科学 | Materials Science |
| `ENG` | 工程 | Engineering |
| `MATH` | 数学 | Mathematics |

---

## 📄 2. 文件类型 (TYPE)

| 代码 | 含义 | 示例 |
|------|------|------|
| `DAT` | 数据 | `CS_DAT_...` |
| `EXP` | 实验 | `BIO_EXP_...` |
| `ANA` | 分析 | `CS_ANA_...` |
| `RES` | 结果 | `MED_RES_...` |
| `FIG` | 图 | `BIO_FIG_...` |
| `TAB` | 表 | `ENV_TAB_...` |
| `MOD` | 模型 | `CS_MOD_...` |
| `DOC` | 文档 | `MAT_DOC_...` |
| `PAP` | 论文 | `SOC_PAP_...` |
| `PRE` | 演示 | `CS_PRE_...` |
| `MET` | 元数据 | `BIO_MET_...` |
| `SOP` | 标准操作 | `MED_SOP_...` |
| `NOTE` | 笔记 | `CS_NOTE_...` |
| `TEMPLATE` | 模板 | `TEMPLATE_...` |

---

## 📊 3. 命名示例

### AI / 计算机 (CS)

```
CS_DAT_LLMAlignment_RewardDataset_HumanPref_2026-03-01_v1.csv
CS_EXP_LLMAlignment_RewardModel_lr1e-5_2026-03-02_v1.md
CS_ANA_LLMAlignment_PCA_Embedding_2026-03-05_v1.py
CS_RES_LLMAlignment_BenchmarkResults_2026-03-10_v1.csv
CS_FIG_LLMAlignment_TrainingCurve_2026-03-12_v1.png
CS_MOD_LLMAlignment_RewardModel_v2_2026-03-15_v1.pkl
CS_PAP_LLMAlignment_Draft_2026-03-20_v0.5.docx
```

### 生物 (BIO)

```
BIO_DAT_GeneExpression_RNAseq_Raw_2026-02-01_v1.csv
BIO_EXP_GeneExpression_PCR_Temp37C_2026-02-05_v1.md
BIO_ANA_GeneExpression_PCA_RNAseq_2026-02-10_v1.R
BIO_FIG_GeneExpression_PCAPlot_2026-02-12_v1.png
BIO_TAB_GeneExpression_DEGList_2026-02-15_v1.xlsx
```

### 医学 (MED)

```
MED_DAT_CovidStudy_PatientData_Cleaned_2026-01-20_v2.csv
MED_ANA_CovidStudy_LogisticRegression_RiskFactors_2026-01-25_v1.R
MED_RES_CovidStudy_MortalityModel_Results_2026-01-28_v1.csv
MED_FIG_CovidStudy_RiskCurve_2026-01-30_v1.png
MED_SOP_CovidStudy_DataCollection_2026-02-01_v1.0.pdf
```

### 环境科学 (ENV)

```
ENV_DAT_ClimateChange_Temperature_Global_2025-01-01_v1.csv
ENV_ANA_ClimateChange_ARIMA_Temperature_2026-03-12_v1.R
ENV_FIG_ClimateChange_TemperatureTrend_Global_2026-03-15_v1.png
ENV_PAP_ClimateChange_ImpactAssessment_Draft_2026-03-20_v0.8.docx
```

### 社会科学 (SOC)

```
SOC_DAT_UrbanMobility_SurveyRaw_SG_2025-12-01_v1.csv
SOC_ANA_UrbanMobility_Regression_CommuteTime_2026-02-10_v1.R
SOC_FIG_UrbanMobility_CommutePattern_2026-02-15_v1.png
SOC_PAP_UrbanMobility_CommutePattern_Draft_2026-03-20_v1.docx
```

### 材料科学 (MAT) - 我们的领域

```
MAT_DAT_LIGConductivity_Dataset_200Samples_2026-03-01_v1.csv
MAT_EXP_LIGConductivity_GPModel_R2_0.773_2026-03-06_v1.md
MAT_ANA_LIGConductivity_FeatureImportance_2026-03-06_v1.py
MAT_FIG_LIGConductivity_PredictionPlot_2026-03-06_v1.png
MAT_MOD_LIGConductivity_GPModel_Optimized_2026-03-06_v1.pkl
MAT_PAP_LIGConductivity_Carbon_Draft_2026-03-06_v2.0.docx
MAT_SOP_LIGConductivity_DataExtraction_2026-03-07_v1.0.md
```

---

## 🔄 排序效果

**按领域自动分组:**

```
BIO_ANA_...
BIO_DAT_...
BIO_EXP_...
BIO_FIG_...
CS_ANA_...
CS_DAT_...
CS_EXP_...
ENV_ANA_...
ENV_DAT_...
MAT_ANA_...
MAT_DAT_...
MAT_FIG_...
MED_ANA_...
MED_DAT_...
```

**非常适合:**
- ✅ 实验室数据仓库
- ✅ 机构科研档案
- ✅ 数据平台
- ✅ 长期科研项目

---

## 📁 我们的工作空间应用

### LIG 导电率预测项目

```
MAT_DAT_LIGConductivity_Dataset_200Samples_2026-03-01_v1.csv
MAT_EXP_LIGConductivity_GPModel_R2_0.773_2026-03-06_v1.md
MAT_ANA_LIGConductivity_FeatureImportance_2026-03-06_v1.py
MAT_FIG_LIGConductivity_PredictionPlot_2026-03-06_v1.png
MAT_MOD_LIGConductivity_GPModel_Optimized_2026-03-06_v1.pkl
MAT_PAP_LIGConductivity_Carbon_Submitted_2026-03-15_v1.0.docx
```

### CNT 碳纳米管项目

```
MAT_DAT_CNTConductivity_Dataset_300Samples_2026-03-07_v1.csv
MAT_EXP_CNTConductivity_GPModel_Training_2026-03-10_v1.md
MAT_ANA_CNTConductivity_SHAP_Analysis_2026-03-15_v1.py
MAT_FIG_CNTConductivity_FeatureImportance_2026-03-15_v1.png
MAT_PAP_CNTConductivity_Draft_2026-04-01_v0.5.docx
```

### 理论工作

```
MAT_DOC_LIGTheory_2DModel_Derivation_2026-03-06_v1.0.md
MAT_ANA_LIGTheory_TemperatureDependent_kCp_2026-03-06_v1.py
MAT_FIG_LIGTheory_TemperatureProfile_2D_2026-03-06_v1.png
```

### 模板文件

```
TEMPLATE_MAT_DAT_v1.0.md
TEMPLATE_MAT_EXP_v1.0.md
TEMPLATE_MAT_ANA_v1.0.md
TEMPLATE_MAT_FIG_v1.0.md
TEMPLATE_MAT_PAP_v1.0.md
```

---

## ✅ 核心结构总结

```
DOMAIN → TYPE → PROJECT → SUBJECT → METHOD → DATE → VERSION
```

**示例:**
```
MAT_DAT_LIGConductivity_Dataset_200Samples_2026-03-01_v1.csv
  ↓    ↓      ↓            ↓           ↓         ↓      ↓
 领域  类型   项目         对象        方法      日期   版本
```

---

## 📋 命名字典

### 我们的领域代码

| 代码 | 领域 | 使用场景 |
|------|------|----------|
| `MAT` | 材料科学 | LIG, CNT 研究 |
| `CS` | 计算机/AI | ML 模型，算法 |
| `CHEM` | 化学 | 化学反应，材料合成 |

### 我们的文件类型

| 代码 | 含义 | 示例 |
|------|------|------|
| `DAT` | 数据集 | `MAT_DAT_...` |
| `EXP` | 实验记录 | `MAT_EXP_...` |
| `ANA` | 分析脚本 | `MAT_ANA_...` |
| `RES` | 结果数据 | `MAT_RES_...` |
| `FIG` | 图表 | `MAT_FIG_...` |
| `MOD` | 模型文件 | `MAT_MOD_...` |
| `PAP` | 论文 | `MAT_PAP_...` |
| `DOC` | 文档 | `MAT_DOC_...` |
| `SOP` | 标准操作 | `MAT_SOP_...` |
| `NOTE` | 笔记 | `MAT_NOTE_...` |
| `TEMPLATE` | 模板 | `TEMPLATE_...` |

---

## 🚫 禁止的命名

```
❌ 新建文档.docx
❌ 最终版 2.docx
❌ LIG 数据.csv
❌ GP 模型结果.xlsx
❌ 论文草稿_v1_改过.docx
❌ 2026.3.6_数据.csv
```

---

## 📊 与之前版本对比

| 版本 | 结构 | 优点 | 缺点 |
|------|------|------|------|
| v1 | 全小写 | 简单 | 无分类 |
| v2 | 描述前缀 | 可读 | 无领域 |
| v3 | 企业级 | 完整 | 不适合科研 |
| **v4** | **领域优先** | **科研标准** | **字段较多** |

---

*科研文件命名规范由用户提供，Claw 记录并执行*  
*版本:* v4.0  
*最后更新:* 2026-03-07 00:36
