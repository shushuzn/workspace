#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Materials Property Predictor v1 - 设计文档
材料性能预测 (ML 模型集成)
"""

# 技术方案

## 1. 材料描述符计算

### 库选择
- **matminer:** 材料特征工程库
- **pymatgen:** 材料分析基础库

### 描述符类型
1. **成分描述符**
   - 原子百分比
   - 元素属性统计 (均值、方差等)
   - 电负性、原子半径等

2. **结构描述符**
   - 晶体系统
   - 空间群
   - 配位数
   - 键长/键角统计

3. **电子结构描述符**
   - 带隙
   - 费米能级
   - 态密度特征

### 示例代码
```python
from matminer.featurizers.composition import ElementProperty
from matminer.featurizers.structure import SiteStatsFingerprint

# 成分描述符
featurizer = ElementProperty.from_preset('magpie')
features = featurizer.featurize_dataframe(df, 'composition')

# 结构描述符
struct_featurizer = SiteStatsFingerprint.from_preset('CrystalNN')
struct_features = struct_featurizer.featurize_dataframe(df, 'structure')
```

## 2. 性能预测模型

### 预测目标
| 性能 | 单位 | 典型范围 |
|------|------|----------|
| 带隙 | eV | 0-10 |
| 形成能 | eV/atom | -10-10 |
| 体积模量 | GPa | 0-500 |
| 剪切模量 | GPa | 0-300 |
| 热导率 | W/mK | 0-1000 |

### 模型选择
1. **Random Forest**
   - 优点：可解释性好，不易过拟合
   - 适用：中小数据集

2. **Gradient Boosting (XGBoost/LightGBM)**
   - 优点：精度高
   - 适用：中等数据集

3. **Neural Networks**
   - 优点：拟合能力强
   - 适用：大数据集

4. **Graph Neural Networks**
   - 优点：直接处理晶体结构
   - 适用：结构 - 性能关系

### 示例代码
```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# 准备数据
X = features.drop('target', axis=1)
y = features['target']

# 训练测试分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 训练模型
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

# 评估
from sklearn.metrics import mean_absolute_error
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
```

## 3. 预训练模型集成

### 可用模型
1. **MPNN (Materials Property Neural Network)**
   - 来源：PyTorch Geometric
   - 支持：带隙、形成能等

2. **CGCNN (Crystal Graph Convolutional Neural Network)**
   - 来源：GitHub 开源
   - 支持：多种性能预测

3. **MEGNet (MatErials Graph Network)**
   - 来源：matbench
   - 支持：12 种性能预测

### 集成方式
```python
from megnet.models import MEGNetModel

# 加载预训练模型
model = MEGNetModel.load_model("pretrained_model")

# 预测
prediction = model.predict_structure(structure)
```

## 4. 预计工作量

| 任务 | 用时 |
|------|------|
| 材料描述符计算 | 2 小时 |
| 性能预测模型集成 | 3 小时 |
| 带隙预测 | 2 小时 |
| 弹性模量预测 | 2 小时 |
| 稳定性预测 | 1 小时 |
| **总计** | **10 小时** |

## 5. 实施计划

**时间:** 2026-03-17 ~ 03-21  
**优先级:** 🔴 高

---

*创建时间：2026-03-05 13:25*
