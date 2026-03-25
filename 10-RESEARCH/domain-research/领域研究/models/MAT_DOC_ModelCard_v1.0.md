# Model Card: LIG GP 200 Samples

**版本:** 1.0  
**创建日期:** 2026-03-06  
**作者:** Claw (OpenClaw Research Lab)

---

## 📋 模型详情

| 属性 | 值 |
|------|-----|
| **模型类型** | 高斯过程回归 (Gaussian Process Regression) |
| **训练数据** | 200 样本 (15 篇文献) |
| **特征** | 能量密度 (E_Jcm²), 扫描速度 (v_mms), CO₂比例 (co_ratio) |
| **目标** | 电导率 (σ_Sm, S/m) |
| **核函数** | RBF + WhiteKernel |
| **性能** | R² = 0.773, MAE = 506.4 S/m |
| **不确定性** | 95% CI 覆盖率 100% |

---

## 🎯 预期用途

预测激光诱导石墨烯 (LIG) 的电导率，基于以下工艺参数：
- 激光能量密度 (J/cm²)
- 扫描速度 (mm/s)
- CO₂ 激光比例 (0-1)

**适用场景:**
- LIG 工艺参数优化
- 实验设计指导
- 性能预测与风险评估

---

## 📊 训练数据

**数据来源:** 15 篇已发表的 LIG 研究论文

**数据分布:**
- 能量密度: 0.5 - 50 J/cm²
- 扫描速度: 10 - 500 mm/s
- CO₂ 比例: 0 - 1
- 电导率: 120 - 48,500 S/m

**数据集划分:**
- 训练集: 160 样本 (80%)
- 测试集: 40 样本 (20%)

---

## ⚙️ 使用方法

### Python 示例

```python
import joblib
import numpy as np

# 加载模型
model = joblib.load('LIG_GP_200samples.pkl')
scaler_X = joblib.load('LIG_GP_scaler_X.pkl')
scaler_y = joblib.load('LIG_GP_scaler_y.pkl')

# 准备输入
X_new = np.array([[10.0, 50.0, 1.0]])  # E, v, co
X_scaled = scaler_X.transform(X_new)

# 预测
y_pred, y_std = model.predict(X_scaled, return_std=True)
y_pred_orig = scaler_y.inverse_transform(y_pred.reshape(-1, 1)).flatten()

print(f"预测电导率：{y_pred_orig[0]:.1f} S/m")
print(f"不确定性 (1σ): ±{y_std[0] * scaler_y.scale_[0]:.1f} S/m")
```

### 命令行

```bash
python predict.py --E 10.0 --v 50.0 --co 1.0
```

---

## ⚠️ 局限性

1. **数据限制**
   - 仅 200 个样本，来自文献
   - 无实验验证数据
   - 数据分布不均 (中等能量密度区域集中)

2. **特征限制**
   - 仅 3 个特征
   - 未考虑基底类型、环境因素、后处理工艺

3. **模型限制**
   - GP 计算复杂度 O(n³)，难以扩展到>1000 样本
   - R² = 0.773，未达 0.80 目标
   - 高能量密度区域不确定性较高

---

## 📈 性能指标

| 指标 | 值 | 说明 |
|------|-----|------|
| R² | 0.773 | 测试集 |
| MAE | 506.4 S/m | 平均绝对误差 |
| RMSE | 684.6 S/m | 均方根误差 |
| NRMSE | 40.7% | 归一化 RMSE |
| 95% CI 覆盖率 | 100% | 不确定性可靠性 |

---

## 🔬 超参数

优化后的核函数：

```
k(x, x') = 1.48² × RBF(length_scale=[3.78, 5.96, 2.31]) + WhiteKernel(noise_level=0.328)
```

**长度尺度解释:**
- E_Jcm2: 3.78 (中等敏感)
- v_mms: 5.96 (较不敏感)
- co_ratio: 2.31 (最敏感)

---

## 📚 引用

如使用本模型，请引用：

```bibtex
@misc{claw2026lig,
  author = {Claw},
  title = {LIG Conductivity Prediction Model - Gaussian Process Regression},
  year = {2026},
  howpublished = {Zenodo},
  doi = {10.5281/zenodo.xxxxxxx},
  note = {R² = 0.773, 200 samples, 95\% CI coverage = 100\%}
}
```

**相关论文:**
```
Claw. (2026). Machine Learning-Assisted Prediction of Electrical Conductivity 
in Laser-Induced Graphene Using Gaussian Process Regression. [Submitted to Carbon].
```

---

## 📄 许可证

- **模型:** MIT License
- **数据:** CC BY 4.0
- **代码:** MIT License

---

## 🔗 相关链接

- **GitHub 仓库:** [待填写]
- **Zenodo DOI:** [待填写]
- **论文预印本:** [待填写]

---

## 📧 联系

**作者:** Claw  
**所属机构:** OpenClaw Research Lab  
**邮箱:** [待填写]

---

*最后更新:* 2026-03-06 16:10
