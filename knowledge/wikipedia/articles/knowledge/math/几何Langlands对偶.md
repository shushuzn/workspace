# 几何Langlands对偶

## 基本信息

- **原文**：Geometric Langlands correspondence
- **本质**：数论的 Langlands 对偶在几何化语境下的对应
- **核心思想**：域上的表示论 ↔ 黎曼面上的层（sheaf）
- **提出者**：Drinfeld, Laumon, Beilinson, Bernstein

---

## 核心概念

### 经典 Langlands 对偶（数论）

在数域上，Langlands 对偶建立了：

$$Gal(K/k) \longleftrightarrow GL_n(\mathbb{A}_k)$$

- **左侧**：数域的 Galois 群表示
- **右侧**： Adele 环上的一般线性群自守形式

### 几何化 Langlands

把域替换为黎曼面 $X$：

| 数论 Langlands | 几何 Langlands |
|----------------|----------------|
| $Gal(K/k)$ 的表示 | 局部系统的层（Local system） |
| $GL_n(\mathbb{A}_k)$ 的自守形式 | $GL_n$ 的主丛上的 Higgs 层 |
| Hecke 本征形式 | Hecke 特征层（Hecke eigensheaf） |
| 保形表示 | 可构造层（perverse sheaf） |

### 关键定理

**Laumon (1989)**：证明了光滑 Langlands 对偶的存在性。

**Beilinson & Bernstein (1992)**：建立了 $\mathcal{D}$-模框架下的几何 Langlands 对偶。

---

## 与物理的关系

### Witten 的物理诠释

**Witten (1994)**：几何 Langlands 对偶可以用 Chern-Simons 理论在三维流形上解释：

$$Z_{CS} \longleftrightarrow \text{几何 Langlands 对偶}$$

- $G$ 的 CS 理论 ↔ $^L G$ 的 Langlands 对偶
- 其中 $^L G$ 是 Langlands 对偶群（如 $SL_2$ ↔ $PGL_2$）

### 量子场论视角

| 物理构造 | 数学对象 |
|----------|----------|
| CS 配分函数 | 黎曼面上的线丛截面 |
| Wilson 线算子 | Hecke 特征层的代数 |
| 边界态 | 可构造层的奇异支撑 |

---

## 与 Khovanov 同调的关系

**Witten 2014 猜想**（未完全证明）：

$$Kh(L) = q\text{-graded Euler characteristic of } Z_{CS}(L)$$

这建立了：
- **Khovanov 同调**（范畴化 Jones 多项式）
- **几何 Langlands 对偶**（量子场论与数论的桥梁）

两者通过 CS 理论在三维拓扑量子场论的框架下统一。

---

## 数学结构

### 关键对象

- **Higgs 层**（Higgs bundle）：黎曼面上的主丛 + Higgs 场
- **$\mathcal{D}$-模**：代数 $\mathcal{D}$-模与可构造层
- **perverse sheaf**：介于代数层与constructible层之间的范畴
- **拟反射函数**：Langlands 对偶的核函数

### 对偶的范畴化

几何 Langlands 不仅是数值对应，而是**范畴化**的：
- 左侧：$G$ 的表示范畴
- 右侧：${}^L G$ 的凝块层范畴（derived category of ${}^L G$-bundles）

---

## 相关条目

- [[Chern-Simons理论]] — Witten 用 CS 理论解释几何 Langlands 对偶
- [[Khovanov同调]] — Witten 猜想连接 Khovanov 同调与 CS 理论
- [[量子群]] — Langlands 对偶与量子群的表示论有关
- [[范畴化]] — 几何 Langlands 是范畴化的经典例子
- [[可积系统]] — 几何 Langlands 与可积系统的深层联系

---

## 参考文献

- Laumon 1989 — "Transformation de Fourier, constante d функции elliptique et интервал"
- Beilinson & Bernstein 1992 — "A proof of Jantzen conjectures"
- Witten 1989 — "Quantum field theory and the Jones polynomial"
- Witten 2014 — "Khovanov homology and Jones polynomial" (unpublished conjecture)
