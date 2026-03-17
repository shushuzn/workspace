# LIG 稳定性预测模型训练脚本

**机器学习模型训练** - 预测激光诱导石墨烯 (LIG) 材料稳定性

---

## 📖 简介

`train_lig_stability_model.py` 用于训练 LIG 材料稳定性预测模型，基于激光参数、环境条件等特征预测材料性能变化率。

### 核心功能

- **数据加载**: 支持 CSV 格式稳定性数据集
- **特征工程**: 自动计算能量密度、总曝光量等衍生特征
- **双模型训练**: 回归模型 (预测变化率) + 分类模型 (稳定性评级)
- **模型评估**: 交叉验证、MAE、准确率等指标
- **特征重要性**: 分析关键影响因素
- **模型导出**: 保存为 pickle 格式供推理使用

---

## 🚀 快速使用

### 基本命令

```bash
# 训练模型
py 30-scripts/train_lig_stability_model.py --data data/lig_stability.csv --output models/

# 指定模型类型
py 30-scripts/train_lig_stability_model.py --data data/lig_stability.csv --model-type regression --output models/

# 查看特征重要性
py 30-scripts/train_lig_stability_model.py --data data/lig_stability.csv --feature-importance --output models/
```

### 输出示例

```
[OK] Loaded 150 samples from data/lig_stability.csv
[OK] Preprocessed 150 samples
[OK] Features: ['laser_power', 'scan_speed', 'scan_passes', 'environment', 'energy_density', 'total_exposure']

=== 回归模型 (RandomForest) ===
CV MAE: 3.45 ± 0.82 %
Test MAE: 3.12 %
R² Score: 0.87

=== 分类模型 (稳定性评级) ===
CV Accuracy: 0.89 ± 0.05
Test Accuracy: 0.91
Classification Report:
              precision    recall  f1-score   support
           A       0.95      0.92      0.93        48
           B       0.88      0.90      0.89        52
           C       0.85      0.83      0.84        30
           D       0.92      0.95      0.93        20

[OK] Model saved to models/lig_stability_model_20260310_042600.pkl
[OK] Training log saved to models/training_log_20260310_042600.json
```

---

## 📊 数据格式

### 输入数据 (CSV)

| 列名 | 类型 | 说明 | 必填 |
|------|------|------|------|
| `laser_power` | float | 激光功率 (mW) | ✅ |
| `scan_speed` | float | 扫描速度 (mm/s) | ✅ |
| `scan_passes` | int | 扫描次数 | ✅ |
| `environment` | string | 环境条件 (air/nitrogen/argon) | ✅ |
| `humidity` | float | 湿度 (%) | ❌ |
| `temperature` | float | 温度 (°C) | ❌ |
| `change_percent` | float | 性能变化率 (%) | ✅ (标签) |
| `cycles` | int | 测试循环次数 | ❌ |

### 示例数据

```csv
laser_power,scan_speed,scan_passes,environment,humidity,temperature,change_percent,cycles
200,50,3,air,45,25,4.2,100
250,40,5,nitrogen,30,22,2.1,100
180,60,2,air,50,26,8.5,100
```

---

## 🎯 稳定性评级标准

模型自动将连续的变化率转换为离散评级：

| 评级 | 变化率范围 | 稳定性描述 |
|------|------------|------------|
| **A** | < 5% | 优秀 - 高度稳定 |
| **B** | 5-15% | 良好 - 可接受 |
| **C** | 15-30% | 中等 - 需改进 |
| **D** | > 30% | 差 - 不稳定 |

---

## ⚙️ 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--data` | string | 必填 | 输入数据 CSV 路径 |
| `--output` | string | `models/` | 模型输出目录 |
| `--model-type` | string | `both` | 模型类型：`regression`/`classification`/`both` |
| `--feature-importance` | flag | False | 输出特征重要性分析 |
| `--test-size` | float | 0.2 | 测试集比例 |
| `--cv-folds` | int | 5 | 交叉验证折数 |
| `--random-state` | int | 42 | 随机种子 |

---

## 📁 输出文件

### 模型文件

- `lig_stability_model_YYYYMMDD_HHMMSS.pkl` - 训练好的模型 (pickle 格式)

### 日志文件

- `training_log_YYYYMMDD_HHMMSS.json` - 训练日志 (指标、参数、特征重要性)

### 日志内容示例

```json
{
  "timestamp": "2026-03-10T04:26:00",
  "data_file": "data/lig_stability.csv",
  "num_samples": 150,
  "num_features": 6,
  "model_type": "both",
  "regression_metrics": {
    "cv_mae_mean": 3.45,
    "cv_mae_std": 0.82,
    "test_mae": 3.12,
    "r2_score": 0.87
  },
  "classification_metrics": {
    "cv_accuracy_mean": 0.89,
    "cv_accuracy_std": 0.05,
    "test_accuracy": 0.91
  },
  "feature_importance": {
    "energy_density": 0.32,
    "laser_power": 0.25,
    "scan_speed": 0.18,
    "environment": 0.12,
    "total_exposure": 0.08,
    "scan_passes": 0.05
  }
}
```

---

## 🔬 特征工程

### 自动衍生特征

脚本自动计算以下衍生特征：

1. **能量密度** (`energy_density`):
   ```
   energy_density = laser_power / scan_speed
   ```
   单位面积接收的激光能量，影响石墨烯化程度。

2. **总曝光量** (`total_exposure`):
   ```
   total_exposure = laser_power × scan_passes
   ```
   材料接收的总激光能量。

### 特征重要性分析

使用 `--feature-importance` 参数输出各特征对预测的贡献度：

```
特征重要性排序:
  1. energy_density: 0.32 (能量密度最关键)
  2. laser_power: 0.25
  3. scan_speed: 0.18
  4. environment: 0.12 (环境影响显著)
  5. total_exposure: 0.08
  6. scan_passes: 0.05
```

---

## 🔧 依赖

```
pandas>=1.5.0
numpy>=1.23.0
scikit-learn>=1.2.0
matplotlib>=3.6.0
```

### 安装依赖

```bash
pip install pandas numpy scikit-learn matplotlib
```

---

## 📝 使用场景

1. **工艺优化**: 识别最优激光参数组合
2. **质量控制**: 预测批次稳定性
3. **实验设计**: 指导后续实验方向
4. **生产监控**: 实时评估工艺稳定性

---

## 🐛 常见问题

### Q: 数据量多少才够训练？
A: 建议至少 100 个样本。少于 50 个样本时模型容易过拟合。

### Q: 如何提高模型准确率？
A: 
- 增加训练数据量
- 添加更多特征 (如前驱体类型、激光波长等)
- 尝试其他模型 (XGBoost、LightGBM)

### Q: 模型可以用于其他材料吗？
A: 需要重新训练。不同材料的稳定性机制不同。

---

## 📄 相关文档

- `11-research/LIG-Stability-Data-Collection.md` - 稳定性数据收集
- `11-research/LIG-Stability-ML-Framework.md` - ML 框架设计文档

---

**维护者**: Claw (AI Research OS)  
**最后更新**: 2026-03-10
