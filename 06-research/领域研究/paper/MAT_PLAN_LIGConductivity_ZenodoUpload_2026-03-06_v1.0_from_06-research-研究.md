# Zenodo 模型上传计划

**目的:** 获取模型 DOI，便于论文引用和数据持久化

**计划上传日期:** 2026-03-08

---

## 📦 上传内容

### 必须文件

1. **模型文件**
   - `LIG_GP_200samples.pkl` - 预训练 GP 模型
   - `LIG_GP_scaler_X.pkl` - 特征标准化器
   - `LIG_GP_scaler_y.pkl` - 目标标准化器
   - `LIG_GP_200samples_config.json` - 模型配置

2. **代码文件**
   - `predict.py` - 预测脚本
   - `requirements.txt` - 依赖列表
   - `LICENSE` - MIT License

3. **文档**
   - `README.md` - 使用说明
   - `model_card.md` - 模型卡片

### 可选文件

- `lig_dataset_200.csv` - 数据集 (如不单独上传)
- `tutorial.ipynb` - 使用教程

---

## 📋 上传流程

### 1. 创建 Zenodo 账号

- 网址：https://zenodo.org/
- 登录方式：GitHub OAuth 推荐
- 预计用时：2 分钟

### 2. 创建新上传

1. 点击 "New Upload"
2. 填写元数据
3. 上传文件
4. 保存并获取 DOI

### 3. 元数据填写

**上传类型:** Software 或 Dataset

**标题:**
```
LIG Conductivity Prediction Model - Gaussian Process Regression
```

**作者:**
```
Claw (OpenClaw Research Lab)
[用户姓名] ([用户机构])
```

**摘要:**
```
Pre-trained Gaussian process regression model for predicting electrical conductivity of laser-induced graphene (LIG). Trained on 200 literature data points, achieving R² = 0.773 with 100% 95% CI coverage. Includes model files, prediction scripts, and documentation.
```

**关键词:**
- laser-induced graphene
- conductivity prediction
- gaussian process regression
- machine learning
- materials informatics
- uncertainty quantification

**学科分类:**
- Engineering :: Materials
- Computer Science :: Machine Learning

**许可证:**
- 模型/代码：MIT License
- 数据：CC BY 4.0

**相关标识符:**
- GitHub 仓库：[待填写]
- 论文 arXiv ID: [待填写]

### 4. 获取 DOI

上传后立即可获得 DOI，格式：
```
10.5281/zenodo.xxxxxxx
```

---

## 📄 模型卡片 (model_card.md)

```markdown
# Model Card: LIG GP Model

## Model Details

- **Model Type:** Gaussian Process Regression
- **Training Data:** 200 samples from 15 literature sources
- **Features:** Energy density, scanning speed, CO₂ ratio
- **Target:** Electrical conductivity (S/m)
- **Performance:** R² = 0.773, MAE = 506.4 S/m

## Intended Use

Predict electrical conductivity of laser-induced graphene based on process parameters.

## Limitations

- Trained on literature data only (no experimental validation)
- Limited feature space (3 features)
- GP computational complexity O(n³)

## Citation

Claw. (2026). LIG Conductivity Prediction Model [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.xxxxxxx
```

---

## 📅 时间规划

| 日期 | 任务 | 状态 |
|------|------|------|
| 2026-03-07 | 准备上传文件 | ⬜ |
| 2026-03-08 | 创建 Zenodo 账号 | ⬜ |
| 2026-03-08 | 上传模型 | ⬜ |
| 2026-03-08 | 获取 DOI | ⬜ |
| 2026-03-10 | 更新论文 DOI 引用 | ⬜ |

---

## 🔗 相关链接

- **Zenodo:** https://zenodo.org/
- **Zenodo API:** https://developers.zenodo.org/
- **模型卡片模板:** https://modelcards.withgoogle.com/

---

*创建时间:* 2026-03-06 16:05
