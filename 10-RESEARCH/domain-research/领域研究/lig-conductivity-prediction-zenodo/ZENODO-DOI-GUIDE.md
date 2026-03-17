# Zenodo DOI 申请指南

**创建日期:** 2026-03-10  
**目标:** 为 LIG 电导率预测模型获取学术 DOI（时间公证）

---

## 🚀 快速步骤

### 步骤 1: 创建 GitHub Release

1. 访问仓库：https://github.com/shushuzn/lig-conductivity-prediction
2. 点击 **Releases** → **Create a new release**
3. 填写信息:
   - **Tag version:** `v1.0.0`
   - **Release title:** `LIG Conductivity Prediction v1.0`
   - **Description:** 
     ```
     Initial release of LIG conductivity prediction model.
     
     - Dataset: 200 samples from 15 literature sources
     - Model: Gaussian Process Regression
     - R²: 0.801 (after active learning)
     - MAE: 459 S/m
     ```
4. 点击 **Publish release**

---

### 步骤 2: 连接 Zenodo

1. 访问：https://zenodo.org/account/settings/github/
2. 登录 Zenodo (可用 ORCID 登录)
3. 点击 **Connect to GitHub**
4. 授权 Zenodo 访问你的 GitHub 仓库
5. 在仓库列表中找到 `shushuzn/lig-conductivity-prediction`
6. 打开右侧的 **开关** (启用自动存档)

---

### 步骤 3: 获取 DOI

1. Zenodo 会自动检测新的 GitHub Release
2. 访问：https://zenodo.org/deposit
3. 找到你的仓库上传
4. 填写元数据:
   - **Title:** LIG Conductivity Prediction Model
   - **Creators:** shushuzn
   - **Publication Date:** 2026-03-10
   - **Description:** Machine learning model for predicting electrical conductivity in Laser-Induced Graphene
   - **Keywords:** LIG, conductivity, machine learning, Gaussian Process
5. 点击 **Save** → **Publish**
6. 获取 DOI (格式：`10.5281/zenodo.XXXXXX`)

---

### 步骤 4: 更新 README

将 DOI 徽章添加到 README:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXX)
```

---

## 📋 元数据模板

```yaml
title: LIG Conductivity Prediction Model
creators:
  - name: shushuzn
description: |
  Machine Learning-Assisted Prediction of Electrical Conductivity 
  in Laser-Induced Graphene Using Gaussian Process Regression
  
  - Dataset: 200 samples from 15 literature sources
  - Model: Gaussian Process Regression (GP)
  - R²: 0.801 (after active learning)
  - MAE: 459 S/m
  - 95% CI Coverage: 100%
publication_date: 2026-03-10
keywords:
  - Laser-Induced Graphene
  - Electrical Conductivity
  - Machine Learning
  - Gaussian Process Regression
  - Materials Informatics
license: CC-BY-4.0
```

---

## ⚠️ 注意事项

1. **DOI 一旦创建不可更改** - 确保版本正确
2. **开源协议** - 推荐使用 CC-BY-4.0 或 MIT
3. **数据完整性** - 确保所有文件已上传
4. **作者署名** - 确认作者列表正确

---

## 🔗 相关资源

- [Zenodo 官方文档](https://help.zenodo.org/)
- [GitHub 集成指南](https://developers.zenodo.org/#github)
- [DOI 最佳实践](https://www.doi.org/handbook_2000.html)

---

## 📊 时间线

| 步骤 | 预计时间 | 状态 |
|------|----------|------|
| GitHub Release | 5 分钟 | ⏸️ 待执行 |
| Zenodo 连接 | 3 分钟 | ⏸️ 待执行 |
| DOI 获取 | 5 分钟 | ⏸️ 待执行 |
| README 更新 | 2 分钟 | ⏸️ 待执行 |

**总计:** 约 15 分钟

---

*最后更新：2026-03-10*
