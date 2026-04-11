# Yang-Baxter方程

## 基本信息

- **原文**：Yang-Baxter equation / braid equation
- **类型**：可积系统的核心方程
- **提出者**：Yang（1967），Baxter（1972）
- **数学结构**：辫群的基本关系

---

## 方程定义

### 经典Yang-Baxter方程

给定代数值 $R$（$R$ 矩阵），方程为：

$$R_{12} R_{13} R_{23} = R_{23} R_{13} R_{12}$$

其中 $R_{ij}$ 表示在空间 $i$ 和 $j$ 上作用的矩阵。

### 量子Yang-Baxter方程

$$R(u)_{12} R(u+v)_{13} R(v)_{23} = R(v)_{23} R(u+v)_{13} R(u)_{12}$$

---

## 与辫群的关系

### 辫群 $B_n$

$n$ 股辫子的代数结构，生成元 $\sigma_1, ..., \sigma_{n-1}$ 满足：

1. **相邻交换**：$\sigma_i \sigma_{i+1} \sigma_i = \sigma_{i+1} \sigma_i \sigma_{i+1}$
2. **不交叉**：$\sigma_i \sigma_j = \sigma_j \sigma_i$（$|i-j| > 1$）

### Yang-Baxter关系

$$\sigma_i = R(u_i) / \text{标量}$$

辫子的交叉动作 = Yang-Baxter $R$ 矩阵的普适化。

---

## 可积系统中的应用

### 可积条件

Yang-Baxter方程是**可积系统的基本条件**。

**transfer matrix** $T(u)$ 满足：

$$[ T(u), T(v) ] = 0, \quad \forall u,v$$

这要求 $R$ 矩阵满足Yang-Baxter方程。

### 例子：XXZ模型

$$
R(u) = \begin{pmatrix}
e^{u/2} & 0 & 0 & 0 \\
0 & e^{-u/2} \sinh \gamma & \sinh u & 0 \\
0 & \sinh u & e^{-u/2} \sinh \gamma & 0 \\
0 & 0 & 0 & e^{u/2}
\end{pmatrix}
$$

---

## 与拓扑的联系

### 统计力学 → 拓扑

**Kauffman bracket**：
- $R$ 矩阵的本征值决定辫子的拓扑不变量
- Yang-Baxter方程保证**编织的拓扑不变性**

### 量子场论

**2013年突破**（Costello-Witten-MY）：
- 四维Chern-Simons理论
- Wilson线（1维算符）
- "余剩维度"使得Wilson线自动满足Yang-Baxter方程
- **不需要额外的光谱参数**

---

## 应用领域

1. **可积量子场论**：精确求解二维系统
2. **冷原子物理**：一维玻色气体
3. **统计力学**：exactly solvable models
4. **拓扑量子计算**：braid anyons实现量子门
5. **拓扑量子场论**：Chern-Simons理论的代数结构

---

## 相关条目

- [[可积系统]] — Yang-Baxter方程是核心
- [[Chern-Simons理论]] — 物理实现Yang-Baxter关系
- [[联络目不变量]] — Yang-Baxter方程的拓扑应用
- [[量子场论的数学物理]] — 山崎雅人演讲，包含Yang-Baxter方程与可积系统的完整讨论

---

## 参考文献

- Yang 1967 — "S-Matrix for the One-Dimensional N-Body Problem"
- Baxter 1972 — "Partition function of the Eight-Vertex Lattice Model"
- Drinfeld 1985 — 量子群的引入
- Costello-Witten-MY 2013 — 4D场论与可积系统的连接
