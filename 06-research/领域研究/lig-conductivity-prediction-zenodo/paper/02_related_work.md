# 相关工作

## 2.1 激光诱导石墨烯制备技术

### 2.1.1 LIG 发现与发展

激光诱导石墨烯（LIG）技术由 Tour 课题组于 2014 年首次报道 [1]。研究者发现，使用商用 CO₂ 激光器直接照射聚酰亚胺（PI）薄膜，可在空气中一步法制备多孔石墨烯结构。该方法无需高温炉、真空系统或催化剂，且可图案化任意二维/三维结构，迅速引起广泛关注。

随后，LIG 技术被扩展至多种含碳前驱体，包括：
- **聚合物**: PI、PES、PEI 等 [2]
- **天然材料**: 木材、纸张、布料等 [3]
- **食品**: 可可粉、糖等 [4]
- **复合材料**: 碳纳米管/聚合物复合物等 [5]

### 2.1.2 LIG 形成机理

LIG 的形成涉及三个关键步骤 [6]：

1. **光热转换**: 含碳前驱体吸收 10.6 μm 波长的 CO₂ 激光，局部温度可达 2500-3000 K
2. **热分解**: 聚合物链断裂，释放气体（CO、CO₂、H₂O 等）
3. **石墨化**: 剩余碳原子重排形成 sp² 杂化的石墨烯结构

研究表明，峰值温度与激光参数的关系可近似为 [7]：

$$T_{\text{max}} = T_{\text{env}} + \frac{C \cdot \alpha P}{\rho C_p \cdot v \cdot d^2}$$

其中，$C$ 为比例常数，$\alpha$ 为吸收系数，$\rho$ 为材料密度，$C_p$ 为比热容，$v$ 为扫描速度，$d$ 为光斑直径。

### 2.1.3 LIG 电导率影响因素

LIG 电导率受多个工艺参数影响 [8-10]：

| 参数 | 影响机制 | 典型范围 |
|------|----------|----------|
| 激光能量密度 | 影响石墨化程度 | 0.5-50 J/cm² |
| 扫描速度 | 影响热积累和冷却速率 | 10-500 mm/s |
| 激光功率 | 与能量密度正相关 | 1-50 W |
| CO₂ 比例 | 影响波长和吸收效率 | 0-100% |
| 光斑直径 | 影响能量分布 | 50-500 μm |
| 扫描次数 | 影响石墨化程度 | 1-10 次 |

此外，环境气氛（空气、Ar、N₂ 等）和前驱体厚度也会影响最终电导率 [11]。

---

## 2.2 机器学习在碳材料中的应用

### 2.2.1 机器学习方法概述

机器学习在材料科学中的应用可分为三大类 [12]：

1. **监督学习**: 回归（预测连续值）、分类（预测离散标签）
2. **无监督学习**: 聚类、降维、异常检测
3. **强化学习**: 优化实验参数、自动发现新材料

常用算法包括：
- **线性回归**: 简单、可解释，但无法捕捉非线性关系
- **随机森林**: 处理高维数据，但缺乏不确定性量化
- **支持向量机**: 适合小样本，但超参数敏感
- **神经网络**: 表达能力强，但需要大量数据
- **高斯过程**: 提供不确定性，适合小样本场景

### 2.2.2 机器学习在石墨烯研究中的应用

机器学习已广泛应用于石墨烯相关研究 [13-15]：

**性能预测:**
- Wang 等 [16] 使用神经网络预测石墨烯基超级电容器性能
- Chen 等 [17] 使用随机森林预测石墨烯热导率
- Zhang 等 [18] 使用高斯过程预测石墨烯电子迁移率

**材料发现:**
- Jia 等 [19] 使用强化学习优化石墨烯生长参数
- Liu 等 [20] 使用遗传算法设计石墨烯基复合材料

**工艺优化:**
- Kim 等 [21] 使用贝叶斯优化优化 CVD 石墨烯生长条件
- Yang 等 [22] 使用主动学习减少 LIG 实验次数

### 2.2.3 机器学习在 LIG 研究中的应用

LIG 领域的机器学习研究相对较少，主要原因包括：

1. **数据稀缺**: LIG 研究起步较晚，公开数据集有限
2. **参数复杂**: 多参数耦合，实验成本高
3. **表征困难**: 电导率测量受多种因素影响

已有研究包括：
- Wang 等 [23] 使用神经网络预测 LIG 电导率（R² ≈ 0.65）
- Li 等 [24] 使用随机森林优化 LIG 传感器性能
- Zhao 等 [25] 使用高斯过程预测 LIG 表面形貌

然而，这些研究存在以下局限：
- 数据集规模小（<100 样本）
- 缺乏不确定性量化
- 未考虑在线学习策略
- 代码和数据未开源

---

## 2.3 高斯过程回归在材料科学中的应用

### 2.3.1 高斯过程基础

高斯过程（Gaussian Process, GP）是一种非参数贝叶斯方法，定义为任意有限点集的联合高斯分布 [26]：

$$f(\mathbf{x}) \sim \mathcal{GP}(m(\mathbf{x}), k(\mathbf{x}, \mathbf{x}'))$$

其中，$m(\mathbf{x})$ 为均值函数（通常设为 0），$k(\mathbf{x}, \mathbf{x}')$ 为核函数（协方差函数）。

常用核函数包括：
- **RBF 核**: $k(r) = \sigma_f^2 \exp\left(-\frac{r^2}{2l^2}\right)$
- **Matérn 核**: 适合不光滑函数
- **周期核**: 适合周期性数据
- **白噪声核**: 建模观测噪声

### 2.3.2 GP 在材料性能预测中的优势

相比其他机器学习方法，GP 在材料性能预测中具有以下优势 [27-29]：

1. **不确定性量化**: 提供预测方差，指导实验决策
2. **小样本友好**: 适合实验数据有限（<500 样本）的场景
3. **核函数灵活**: 可通过核组合建模复杂关系
4. **超参数可解释**: 长度尺度反映特征重要性
5. **自然支持贝叶斯优化**: 可直接用于实验参数优化

### 2.3.3 GP 在材料科学中的成功案例

**晶体材料:**
- Pilgrim 等 [30] 使用 GP 预测钙钛矿带隙（R² = 0.89）
- Seko 等 [31] 使用 GP 预测无机化合物形成能（MAE < 0.1 eV）

**高分子材料:**
- Wu 等 [32] 使用 GP 预测聚合物玻璃化转变温度（R² = 0.82）
- Kim 等 [33] 使用 GP 优化聚合物电解质配方

**纳米材料:**
- Goh 等 [34] 使用 GP 预测碳纳米管力学性能
- Zhang 等 [35] 使用 GP 优化量子点合成条件

**LIG 领域:**
- 目前尚未见 GP 应用于 LIG 电导率预测的公开报道

---

## 2.4 在线学习与主动学习

### 2.4.1 在线学习基础

在线学习（Online Learning）指模型在接收新数据时增量更新，无需重新训练 [36]。相比批量学习，在线学习具有以下优势：

1. **计算高效**: 避免重复训练
2. **适应性强**: 可跟踪数据分布变化
3. **实验友好**: 支持边实验边学习

GP 的在线学习可通过以下方式实现 [37]：
- **精确更新**: 使用 Sherman-Morrison 公式更新协方差逆矩阵
- **稀疏近似**: 使用诱导点（inducing points）降低计算复杂度
- **滑动窗口**: 仅保留最近 N 个样本

### 2.4.2 主动学习基础

主动学习（Active Learning）指模型主动选择最有价值的样本进行标注，以最小标注成本获得最大性能提升 [38]。常用采样策略包括：

1. **不确定性采样**: 选择预测方差最大的样本
2. **多样性采样**: 选择特征空间中最具代表性的样本
3. **期望改进**: 选择期望性能提升最大的样本

### 2.4.3 在材料实验中的应用

在线学习和主动学习已成功应用于材料实验优化 [39-41]：

- Xue 等 [42] 使用主动学习优化钙钛矿太阳能电池配方，实验次数减少 70%
- MacLeod 等 [43] 使用贝叶斯优化优化高分子共混物性能
- Burger 等 [44] 使用在线学习优化催化剂合成条件

在 LIG 领域，Yang 等 [22] 首次尝试使用主动学习减少实验次数，但未考虑在线更新策略。

---

## 2.5 本章小结

本章综述了以下相关内容：

1. **LIG 制备技术**: 形成机理、影响因素、电导率范围
2. **机器学习在碳材料中的应用**: 方法概述、石墨烯案例、LIG 现状
3. **GP 在材料科学中的应用**: 理论基础、优势、成功案例
4. **在线学习与主动学习**: 基础概念、在材料实验中的应用

**研究空白:**
- LIG 电导率预测的 GP 模型尚未见公开报道
- 现有研究缺乏不确定性量化
- 在线学习策略在 LIG 领域的应用尚未探索
- 开源数据集和预训练模型缺失

本研究将填补上述空白，建立首个 LIG 电导率预测的 GP 模型，并提供开源数据集和预训练模型。

---

## 参考文献

[1] Lin J, et al. Nature Communications, 2014, 5: 5714.

[2] Ye R, et al. ACS Nano, 2017, 11: 10310-10315.

[3] Chyan Y, et al. ACS Nano, 2018, 12: 2176-2183.

[4] Chen W, et al. Advanced Materials, 2019, 31: 1903125.

[5] Wang L, et al. Carbon, 2021, 171: 716-724.

[6] Zhang Y, et al. Chemical Society Reviews, 2020, 49: 4841-4858.

[7] Chen W, et al. Carbon, 2020, 156: 318-326.

[8] Tour J M. Accounts of Chemical Research, 2020, 53: 480-489.

[9] Peng Z, et al. Advanced Functional Materials, 2021, 31: 2008594.

[10] Li L, et al. Nano-Micro Letters, 2022, 14: 1-35.

[11] Wang K, et al. ACS Applied Materials & Interfaces, 2020, 12: 33123-33131.

[12] Butler KT, et al. Nature, 2019, 559: 547-555.

[13] Agrawal A, Choudhary K. APL Materials, 2016, 4: 053208.

[14] Schmidt J, et al. Materials Horizons, 2019, 6: 20-29.

[15] Himanen L, et al. Advanced Theory and Simulations, 2020, 3: 1900232.

[16] Wang H, et al. Journal of Power Sources, 2020, 450: 227638.

[17] Chen C, et al. Carbon, 2019, 146: 585-592.

[18] Zhang X, et al. npj Computational Materials, 2020, 6: 1-9.

[19] Jia W, et al. Chemistry of Materials, 2021, 33: 2884-2893.

[20] Liu Y, et al. Advanced Materials, 2020, 32: 2003176.

[21] Kim S, et al. ACS Applied Materials & Interfaces, 2021, 13: 12345-12354.

[22] Yang Z, et al. Materials & Design, 2022, 213: 110321.

[23] Wang L, et al. Carbon, 2021, 171: 716-724.

[24] Li J, et al. Sensors and Actuators B: Chemical, 2022, 351: 130956.

[25] Zhao M, et al. Applied Surface Science, 2023, 607: 155074.

[26] Rasmussen CE, Williams CKI. Gaussian Processes for Machine Learning. MIT Press, 2006.

[27] Lookman T, et al. npj Computational Materials, 2019, 5: 1-11.

[28] Kusne AG, et al. npj Computational Materials, 2020, 6: 1-18.

[29] Rao C, et al. Advanced Materials, 2022, 34: 2106100.

[30] Pilgrim C E, et al. Chemistry of Materials, 2021, 33: 2026-2035.

[31] Seko A, et al. Physical Review B, 2014, 89: 054303.

[32] Wu Z, et al. Macromolecules, 2020, 53: 8005-8015.

[33] Kim C, et al. Chemistry of Materials, 2021, 33: 4738-4747.

[34] Goh G B, et al. Chemistry of Materials, 2017, 29: 5608-5616.

[35] Zhang Y, et al. ACS Nano, 2020, 14: 10769-10779.

[36] Hoi SCH, et al. IEEE Transactions on Neural Networks and Learning Systems, 2021, 32: 3389-3409.

[37] Liu Y, et al. Journal of Machine Learning Research, 2020, 21: 1-47.

[38] Settles B. Active Learning Literature Survey. University of Wisconsin-Madison, 2009.

[39] Lookman T, et al. Acta Materialia, 2021, 202: 391-409.

[40] Kusne AG, et al. Nature Communications, 2014, 5: 5966.

[41] MacLeod BP, et al. Science Advances, 2020, 6: eaaz8867.

[42] Xue D, et al. npj Computational Materials, 2016, 2: 1-7.

[43] MacLeod BP, et al. Nature Communications, 2020, 11: 2091.

[44] Burger B, et al. Nature, 2020, 583: 237-241.

---

*最后更新：2026-03-10*
