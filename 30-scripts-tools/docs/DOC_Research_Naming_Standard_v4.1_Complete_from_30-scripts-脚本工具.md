# 科研文件命名标准 (完整版)

**创建日期:** 2026-03-07 00:43  
**版本:** v4.1 Complete  
**状态:** 🚧 完善中  
**来源:** 用户专业指导 + Claw 记录

---

## 🎯 标准目标

建立一套**真正可以长期使用的科研命名体系**，适用于：

- ✅ 实验室数据仓库
- ✅ 机构科研档案
- ✅ 跨机构合作项目
- ✅ 长期科研项目
- ✅ 数据平台归档

---

## 📋 核心结构

```
DOMAIN_TYPE_PROJECT_SUBJECT_METHOD_DATE_VERSION
```

**7 个字段，领域优先**

---

## 🔤 1. 学科领域代码表 (DOMAIN)

### 自然科学

| 代码 | 领域 | 英文 |
|------|------|------|
| `MAT` | 材料科学 | Materials Science |
| `CHEM` | 化学 | Chemistry |
| `PHY` | 物理 | Physics |
| `BIO` | 生物学 | Biology |
| `MED` | 医学 | Medicine |
| `ENV` | 环境科学 | Environmental Science |
| `GEO` | 地球科学 | Geoscience |
| `ASTRO` | 天文学 | Astronomy |

### 工程与技术

| 代码 | 领域 | 英文 |
|------|------|------|
| `CS` | 计算机科学 | Computer Science |
| `AI` | 人工智能 | Artificial Intelligence |
| `EE` | 电气工程 | Electrical Engineering |
| `ME` | 机械工程 | Mechanical Engineering |
| `CE` | 土木工程 | Civil Engineering |
| `CHE` | 化学工程 | Chemical Engineering |
| `IE` | 工业工程 | Industrial Engineering |
| `NE` | 核工程 | Nuclear Engineering |

### 数学与统计

| 代码 | 领域 | 英文 |
|------|------|------|
| `MATH` | 数学 | Mathematics |
| `STAT` | 统计学 | Statistics |
| `OR` | 运筹学 | Operations Research |

### 社会科学

| 代码 | 领域 | 英文 |
|------|------|------|
| `ECO` | 经济学 | Economics |
| `SOC` | 社会学 | Sociology |
| `PSY` | 心理学 | Psychology |
| `POL` | 政治学 | Political Science |
| `LAW` | 法学 | Law |
| `EDU` | 教育学 | Education |
| `MGMT` | 管理学 | Management |

### 人文科学

| 代码 | 领域 | 英文 |
|------|------|------|
| `HIST` | 历史学 | History |
| `PHIL` | 哲学 | Philosophy |
| `LING` | 语言学 | Linguistics |
| `LIT` | 文学 | Literature |
| `ART` | 艺术学 | Art Studies |

### 交叉学科

| 代码 | 领域 | 英文 |
|------|------|------|
| `BME` | 生物医学工程 | Biomedical Engineering |
| `NANO` | 纳米科学 | Nanoscience |
| `ENERGY` | 能源科学 | Energy Science |
| `DATA` | 数据科学 | Data Science |
| `NEURO` | 神经科学 | Neuroscience |

---

## 📄 2. 文件类型代码表 (TYPE)

### 数据类

| 代码 | 含义 | 说明 |
|------|------|------|
| `DAT` | 原始数据 | Raw data |
| `PROCDAT` | 处理数据 | Processed data |
| `CLEANDAT` | 清洗数据 | Cleaned data |
| `MET` | 元数据 | Metadata |
| `DICT` | 数据字典 | Data dictionary |

### 实验类

| 代码 | 含义 | 说明 |
|------|------|------|
| `EXP` | 实验记录 | Experiment log |
| `PROTOCOL` | 实验方案 | Protocol |
| `SOP` | 标准操作 | Standard Operating Procedure |

### 分析类

| 代码 | 含义 | 说明 |
|------|------|------|
| `ANA` | 分析脚本 | Analysis script |
| `CODE` | 代码 | Code |
| `NOTEBOOK` | 计算笔记本 | Jupyter notebook |

### 结果类

| 代码 | 含义 | 说明 |
|------|------|------|
| `RES` | 结果数据 | Results |
| `OUT` | 输出文件 | Output |
| `LOG` | 日志文件 | Log file |

### 可视化类

| 代码 | 含义 | 说明 |
|------|------|------|
| `FIG` | 图表 | Figure |
| `PLOT` | 绘图 | Plot |
| `IMG` | 图片 | Image |
| `TAB` | 表格 | Table |

### 模型类

| 代码 | 含义 | 说明 |
|------|------|------|
| `MOD` | 模型文件 | Model |
| `CHKPT` | 检查点 | Checkpoint |
| `CONFIG` | 配置文件 | Configuration |

### 文档类

| 代码 | 含义 | 说明 |
|------|------|------|
| `DOC` | 文档 | Document |
| `PAP` | 论文 | Paper |
| `PRE` | 演示文稿 | Presentation |
| `REP` | 报告 | Report |
| `PROP` | 项目提案 | Proposal |
| `THESIS` | 学位论文 | Thesis |

### 笔记类

| 代码 | 含义 | 说明 |
|------|------|------|
| `NOTE` | 笔记 | Note |
| `MIN` | 会议纪要 | Minutes |
| `IDEA` | 想法记录 | Idea |

### 模板类

| 代码 | 含义 | 说明 |
|------|------|------|
| `TMPL` | 模板 | Template |

---

## 🔢 3. 项目编号规则

### 内部项目

```
[领域缩写][年份][序号]
```

**示例:**
```
MAT2026001  # 材料科学 2026 年第 1 个项目
CS2026015   # 计算机科学 2026 年第 15 个项目
```

### 外部项目

```
[资助机构][项目编号]
```

**示例:**
```
NSF2026-12345  # 国家自然科学基金
NIH-R01-12345  # 美国国立卫生研究院
EU-H2020-123   # 欧盟地平线 2020
```

---

## 📊 4. 实验编号规则

### 格式

```
E[领域][年份][序号]
```

**示例:**
```
EMAT2026001  # 材料科学 2026 年第 1 个实验
EBIO2026042  # 生物学 2026 年第 42 个实验
```

### 完整示例

```
MAT_EXP_EMAT2026001_LIGSynthesis_2026-03-07_v1.md
BIO_EXP_EBIO2026042_PCRCycle_2026-03-08_v1.md
```

---

## 📁 5. 数据集编号规则

### 格式

```
D[领域][年份][序号]
```

**示例:**
```
DMAT2026001  # 材料科学 2026 年第 1 个数据集
DCS2026015   # 计算机科学 2026 年第 15 个数据集
```

### 完整示例

```
MAT_DAT_DMAT2026001_LIGConductivity_200Samples_2026-03-01_v1.csv
CS_DAT_DCS2026015_LLMAlignment_HumanPref_2026-03-01_v1.csv
```

---

## 🏛️ 6. 跨机构项目编号规则

### 格式

```
[机构代码]-[领域]-[年份]-[序号]
```

### 机构代码示例

| 代码 | 机构 |
|------|------|
| `MIT` | 麻省理工学院 |
| `STAN` | 斯坦福大学 |
| `TSING` | 清华大学 |
| `PKU` | 北京大学 |
| `CAS` | 中国科学院 |

### 完整示例

```
CAS-MAT-2026-001  # 中科院材料科学 2026 年第 1 个项目
MIT-CS-2026-015   # MIT 计算机科学 2026 年第 15 个项目
```

---

## 📋 7. 完整命名示例

### 材料科学 (我们的领域)

```
MAT_DAT_DMAT2026001_LIGConductivity_Raw_2026-03-01_v1.csv
MAT_DAT_DMAT2026001_LIGConductivity_Cleaned_2026-03-02_v1.csv
MAT_EXP_EMAT2026001_GPModel_Training_2026-03-06_v1.md
MAT_ANA_DMAT2026001_FeatureImportance_2026-03-06_v1.py
MAT_FIG_DMAT2026001_PredictionPlot_2026-03-06_v1.png
MAT_MOD_DMAT2026001_GPModel_Optimized_2026-03-06_v1.pkl
MAT_PAP_DMAT2026001_Carbon_Submitted_2026-03-15_v1.0.docx
MAT_SOP_DMAT2026001_DataExtraction_2026-03-07_v1.0.md
MAT_TMPL_DMAT2026_DataNote_2026-03-07_v1.0.md
```

### 计算机科学 (AI)

```
CS_DAT_DCS2026015_LLMAlignment_Raw_2026-03-01_v1.csv
CS_EXP_ECS2026015_RewardModel_Training_2026-03-02_v1.md
CS_ANA_DCS2026015_PCA_Embedding_2026-03-05_v1.py
CS_RES_DCS2026015_Benchmark_2026-03-10_v1.csv
CS_FIG_DCS2026015_TrainingCurve_2026-03-12_v1.png
CS_MOD_DCS2026015_RewardModel_v2_2026-03-15_v1.pkl
CS_PAP_DCS2026015_NeurIPS_Submitted_2026-05-01_v1.0.pdf
```

### 生物学

```
BIO_DAT_DBIO2026001_GeneExpression_RNAseq_2026-02-01_v1.csv
BIO_EXP_EBIO2026001_PCR_Temp37C_2026-02-05_v1.md
BIO_ANA_DBIO2026001_PCA_RNAseq_2026-02-10_v1.R
BIO_FIG_DBIO2026001_PCAPlot_2026-02-12_v1.png
BIO_TAB_DBIO2026001_DEGList_2026-02-15_v1.xlsx
BIO_PAP_DBIO2026001_Nature_Submitted_2026-04-01_v1.0.docx
```

---

## 🗂️ 8. 目录结构建议

```
/workspace/
├── MAT/                    # 材料科学领域
│   ├── DATA/               # 数据集
│   │   ├── DMAT2026001_LIGConductivity/
│   │   └── DMAT2026002_CNTConductivity/
│   ├── EXP/                # 实验记录
│   │   ├── EMAT2026001/
│   │   └── EMAT2026002/
│   ├── ANA/                # 分析脚本
│   ├── FIG/                # 图表
│   ├── MOD/                # 模型
│   ├── PAP/                # 论文
│   └── SOP/                # 标准操作
├── CS/                     # 计算机科学领域
│   └── ...
├── BIO/                    # 生物学领域
│   └── ...
└── COMMON/                 # 通用资源
    ├── TMPL/               # 模板
    └── DOC/                # 通用文档
```

---

## ✅ 9. 快速参考卡片

### 核心结构

```
DOMAIN_TYPE_PROJECT_SUBJECT_METHOD_DATE_VERSION
```

### 常用领域代码

```
MAT 材料科学    CS 计算机    BIO 生物
CHEM 化学       AI 人工智能  MED 医学
PHY 物理        ENV 环境     ENG 工程
```

### 常用类型代码

```
DAT 数据    EXP 实验    ANA 分析
RES 结果    FIG 图表    MOD 模型
PAP 论文    DOC 文档    SOP 标准
TMPL 模板   NOTE 笔记
```

### 日期格式

```
YYYY-MM-DD  (2026-03-07)
```

### 版本格式

```
v1.0  首次发布
v1.1  小改动
v2.0  重大更新
```

---

## 📝 10. 实施检查清单

### 新项目启动

- [ ] 分配项目编号
- [ ] 创建目录结构
- [ ] 设置模板文件
- [ ] 记录元数据

### 文件创建

- [ ] 使用正确领域代码
- [ ] 使用正确类型代码
- [ ] 日期格式正确
- [ ] 版本号正确

### 文件归档

- [ ] 最终版本转 PDF
- [ ] 元数据完整
- [ ] 移至归档目录
- [ ] 更新索引

---

## 🔄 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v4.0 | 2026-03-07 00:36 | 初始版本 (领域优先) |
| v4.1 | 2026-03-07 00:43 | 完整版 (添加编号规则) |

---

*科研文件命名标准由用户提供框架，Claw 记录并完善*  
*版本:* v4.1 Complete  
*最后更新:* 2026-03-07 00:43
