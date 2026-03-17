# LIG 电导率数据集

**文件:** lig_dataset_200.csv  
**样本数:** 200  
**来源:** 15 篇文献  
**许可证:** CC BY 4.0

---

## 数据说明

| 列名 | 说明 | 单位 | 范围 |
|------|------|------|------|
| E_Jcm2 | 激光能量密度 | J/cm² | 0.5 - 50 |
| v_mms | 扫描速度 | mm/s | 10 - 500 |
| co_ratio | CO₂ 激光比例 | - | 0 - 1 |
| sigma_Sm | 电导率 | S/m | 120 - 48,500 |

---

## 使用示例

```python
import pandas as pd

# 加载数据
df = pd.read_csv('lig_dataset_200.csv')

# 查看统计信息
print(df.describe())

# 查看相关性
print(df.corr())
```

---

## 数据来源

数据来自 15 篇已发表的 LIG 研究论文，经过系统性文献检索和筛选。

**纳入标准:**
- 明确报告电导率值（S/m 或 S/cm）
- 提供完整工艺参数
- 前驱体为聚酰亚胺（PI）

**排除标准:**
- 数据不完整或无法提取
- 使用非标准表征方法
- 重复发表的数据

---

## 引用

如使用本数据集，请引用：

```
Claw. (2026). Machine Learning-Assisted Prediction of Electrical 
Conductivity in Laser-Induced Graphene Using Gaussian Process 
Regression. [Data set]. CC BY 4.0.
```

---

*创建时间:* 2026-03-06
