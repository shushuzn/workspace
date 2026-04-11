# 论文笔记：Witten 1989 — Quantum Field Theory and the Jones Polynomial

## 基本信息

- **标题**：Quantum field theory and the Jones polynomial
- **作者**：Edward Witten
- **发表**：Communications in Mathematical Physics, 1989
- **引用**：~5000次（Google Scholar）
- **获奖**：Witten因此工作获得1990年Fields奖

---

## 研究动机

### 核心问题

Jones多项式是纽结理论中的不变量，但**物理意义不明**。Witten问：

> 能否从物理（量子场论）的角度**导出** Jones 多项式，从而理解其深层几何含义？

### 背景

- Jones多项式（1984）来自Von Neumann代数的表示
- 量子场论（QFT）是物理学的通用框架
- 如果QFT可以给出拓扑不变量，说明**几何/拓扑与量子物理有深层联系**

---

## 核心方法

### Chern-Simons路径积分

Witten考虑了**纯 Chern-Simons 理论**的作用量：

$$S = \frac{k}{4\pi} \int_M \text{Tr}\left(A \wedge dA + \frac{2}{3} A \wedge A \wedge A\right)$$

对三维流形 $M$ 做**路径积分**：

$$Z_{CS}(M) = \int \mathcal{D}A \, e^{iS}$$

### 与Jones多项式的关系

Witten证明：

$$Z_{CS}(S^3) = V(L)(e^{2\pi i/k})$$

其中：
- $Z_{CS}(S^3)$：三维球面上的CS配分函数
- $V(L)$：纽结 $L$ 的Jones多项式
- $k$：CS理论的"level"（整数）

### 关键洞察

**物理 = 拓扑**：
- CS理论是**拓扑的**（不依赖于度规）
- Jones多项式是**拓扑不变量**
- 两者通过路径积分统一

---

## 关键结果

### 定理（Witten 1989）

对某个纽结 $L$ 和群 $G = SU(2)$：

$$\langle W_R(L) \rangle_{CS} = \text{Tr}_R \, q^{J_z}$$

其中 $W_R(L)$ 是**Wilson线算子**，$J_z$ 是某个Casimir算子。

###skein关系的推导

从CS理论可以**推导出**Jones多项式的skein关系：

$$t^{-1} V(L_+) - t V(L_-) = (t^{1/2} - t^{-1/2}) V(L_0)$$

这说明skein关系有物理起源（量子场的量子化）。

---

## 创新点

1. **物理方法处理拓扑问题**：首次用QFT路径积分方法系统研究拓扑不变量
2. **统一框架**：把Jones多项式、辫群表示、量子群放在同一物理框架下
3. **数学-物理桥接**：为数学家提供了新的计算工具，为物理学家提供了新的几何直觉
4. **范畴化先声**：为后来的Khovanov同调（范畴化Jones）埋下伏笔

---

## 后续影响

| 年份 | 工作 | 意义 |
|------|------|------|
| 1990 | Reshetikhin-Turaev | 用量子群严格构造CS TQFT |
| 1994 | Khovanov | 范畴化Jones多项式 |
| 1994 | Witten | 几何Langlands猜想 |
| 2004 | Kapustin-Witten | 几何Langlands与CS对偶 |

---

## 原文结论（摘录）

> "We have shown that the Jones polynomial can be derived from a three-dimensional quantum field theory... This suggests a deep connection between quantum field theory and the topology of manifolds."

---

## 相关知识点

- [[Chern-Simons理论]] — 本文的物理理论框架
- [[Jones多项式]] — 本文导出的数学对象
- [[辫群]] — Jones多项式的代数基础
- [[量子群]] — CS理论与纽结不变量的代数结构
- [[Khovanov同调]] — Jones的范畴化，是本文的数学延伸
- [[拓扑数学专题]] — 本文在拓扑数学中的位置

---

## 标签

#论文笔记 #量子场论 #纽结不变量 #Chern-Simons #Jones多项式 #Witten
