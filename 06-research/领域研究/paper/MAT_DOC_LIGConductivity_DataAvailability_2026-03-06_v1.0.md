# Data Availability Statement

**Carbon 期刊要求:** 必须声明数据和代码的可用性

---

## 模板

### 方案 A（标准版）- 推荐

```
Data Availability Statement

The datasets generated and analyzed during this study, along with the 
source code and pre-trained models, are publicly available in the GitHub 
repository: https://github.com/shushuzn/lig-conductivity-prediction

The dataset is also archived on Zenodo with DOI: [待填写 DOI]
```

### 方案 B（简洁版）

```
Data Availability Statement

All data, code, and models are openly available at: 
https://github.com/shushuzn/lig-conductivity-prediction

Zenodo DOI: [待填写 DOI]
```

### 方案 C（详细版）

```
Data Availability Statement

The following datasets and materials are publicly available:

1. **Dataset:** LIG conductivity dataset with 200 samples extracted from 
   15 literature sources (lig_dataset_200.csv)
   
2. **Code:** Python scripts for data preprocessing, model training, and 
   prediction (https://github.com/shushuzn/lig-conductivity-prediction)
   
3. **Models:** Pre-trained Gaussian Process models with configuration files
   
4. **Figures:** All figures from this manuscript in high resolution (300 DPI)

The repository is archived on Zenodo with DOI: [待填写 DOI]
```

---

## 在论文中的位置

### 位置选项

1. **补充材料部分** (推荐)
   - 放在参考文献之后
   - 作为独立章节

2. **方法章节末尾**
   - 2.5 实现细节 最后一段

3. **脚注**
   - 首页脚注

### 推荐格式

在论文中作为独立章节：

```markdown
## Data Availability

The datasets, source code, and pre-trained models are publicly available 
at: https://github.com/shushuzn/lig-conductivity-prediction

Zenodo DOI: [待填写]
```

---

## 与其他部分的协调

| 位置 | 内容 | 状态 |
|------|------|------|
| 论文补充材料 | GitHub 链接 + Zenodo DOI | ✅ 已准备 |
| Cover Letter | 数据可用性声明 | ✅ 已包含 |
| 投稿系统 | Data Availability 字段 | ⏳ 投稿时填写 |
| README | 数据和代码说明 | ✅ 已完成 |

---

## Zenodo DOI 获取后更新

获取 DOI 后，需要更新以下位置：

1. **论文正文** - 补充材料部分
2. **本文件** - data_availability_statement.md
3. **Cover Letter** - 数据声明部分
4. **GitHub README** - Zenodo 徽章

---

*创建日期：2026-03-06*
