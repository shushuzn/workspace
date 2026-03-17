# Zenodo DOI 申请指南

**创建日期:** 2026-03-06  
**用途:** 为 LIG 电导率预测研究代码和数据获取永久 DOI

---

## 📦 上传内容

| 文件/文件夹 | 大小 | 说明 |
|-------------|------|------|
| `data/lig_dataset_200.csv` | 19.45 KB | 200 样本数据集 |
| `data/README.md` | 1.18 KB | 数据说明 |
| `models/*.pkl` | 214 KB | 预训练 GP 模型 (4 个文件) |
| `models/model_card.md` | 3.6 KB | 模型说明 |
| `scripts/*.py` | ~50 KB | 核心代码 (3 个文件) |
| `figures/*.png` | ~5 MB | 图表文件 (17 个) |
| `README.md` | ~5 KB | 项目说明 |
| `LICENSE` | ~1 KB | 许可证 |
| `requirements.txt` | <1 KB | 依赖列表 |

**总计:** ~110 MB

---

## 🔗 Zenodo 上传步骤

### 步骤 1: 登录 Zenodo

1. 访问：https://zenodo.org
2. 点击 "Log in" (右上角)
3. 使用 ORCID 或 GitHub 账号登录

### 步骤 2: 创建新上传

1. 点击 "New upload" (顶部菜单)
2. 填写基本信息

### 步骤 3: 填写元数据

#### 基本信息
| 字段 | 填写内容 |
|------|----------|
| **Upload type** | Dataset |
| **Title** | Machine Learning-Assisted Prediction of Electrical Conductivity in Laser-Induced Graphene Using Gaussian Process Regression |
| **Creators** | Claw (AI Agent Researcher). [你的单位]. ORCID: [你的 ORCID] |
| **Description** | 见下方模板 |
| **Publication date** | 2026-03-06 |
| **Language** | English |

#### 描述模板
```
This dataset contains the data, code, and models for the paper "Machine Learning-Assisted Prediction of Electrical Conductivity in Laser-Induced Graphene Using Gaussian Process Regression".

## Contents

- **data/**: LIG dataset with 200 samples extracted from 15 literature sources
- **models/**: Pre-trained Gaussian Process regression models
- **scripts/**: Python scripts for model training and prediction
- **figures/**: All figures from the paper

## Model Performance

- R² = 0.801 (after online learning with 3 experimental data points)
- MAE = 459 S/m
- 95% CI coverage = 100%

## Usage

See README.md for detailed usage instructions.

## License

- Code: MIT License
- Data: CC BY 4.0
- Models: MIT License
```

#### 学科分类
- **Primary:** Engineering → Materials Science
- **Secondary:** Computer Science → Machine Learning

#### 关键词
```
laser-induced graphene, LIG, electrical conductivity, machine learning, Gaussian process, materials science, prediction model, online learning
```

#### 相关标识符
- **GitHub:** https://github.com/shushuzn/lig-conductivity-prediction
- **ORCID:** [你的 ORCID]

### 步骤 4: 上传文件

**推荐方式:** 打包上传

```bash
# 在 github_repo 目录执行
cd D:\OpenClaw\workspace\11-research\github_repo

# 创建压缩包 (排除大文件和临时文件)
Compress-Archive -Path * -DestinationPath ../lig-conductivity-prediction-zenodo.zip -Force
```

**上传:**
1. 点击 "Choose files" 或拖拽文件
2. 上传 `lig-conductivity-prediction-zenodo.zip`
3. 等待上传完成 (~110 MB)

### 步骤 5: 选择许可证

| 组件 | 推荐许可证 |
|------|------------|
| **代码** | MIT License |
| **数据** | Creative Commons Attribution 4.0 (CC BY 4.0) |
| **模型** | MIT License |

### 步骤 6: 保存并获取 DOI

1. 点击 "Save" 保存元数据
2. 点击 "Submit" 提交上传
3. Zenodo 会分配 DOI (格式：`10.5281/zenodo.XXXXXXX`)
4. 记录 DOI 用于论文引用

---

## 📝 论文中引用格式

### 代码/数据引用

```
[34] Claw. Machine Learning-Assisted Prediction of Electrical Conductivity 
in Laser-Induced Graphene Using Gaussian Process Regression [Dataset and 
Code]. Zenodo. 2026. DOI: 10.5281/zenodo.XXXXXXX
```

### GitHub + Zenodo 联合引用

```
Code and data available at: 
https://github.com/shushuzn/lig-conductivity-prediction
DOI: 10.5281/zenodo.XXXXXXX
```

---

## ✅ 上传后检查清单

- [ ] DOI 已获取并记录
- [ ] 论文中添加 DOI 引用
- [ ] GitHub README 中添加 Zenodo 徽章
- [ ] 确认所有文件可下载
- [ ] 测试 DOI 链接有效性

---

## 🎯 Zenodo 徽章 (添加到 GitHub README)

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

---

## 💡 提示

1. **Zenodo 与 GitHub 集成:** 可以在 GitHub release 时自动同步到 Zenodo
2. **版本管理:** 每次论文修改后更新 Zenodo 版本
3. **DOI 不变:** 同一上传的 DOI 永久不变
4. **公开时间:** 可以设置 embargo (延迟公开)

---

*指南创建时间：2026-03-06 19:20*
