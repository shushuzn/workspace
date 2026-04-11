# 论文笔记：Jones 1985 — A Polynomial Invariant of Knots and Links

## 基本信息

- **标题**：A polynomial invariant of knots and links via braids
- **作者**：Vaughan Jones
- **发表**：Bulletin of the American Mathematical Society, 1985
- **引用**：~3000次（Google Scholar）
- **获奖**：Jones因此工作获得1990年Fields奖（与Witten并列）

---

## 研究动机

### 核心问题

纽结理论中已有 Alexander多项式（1923），但：
- Alexander多项式**不能区分所有纽结**
- 例如，无法区分某些手性（orientation）问题
- 是否有**更强的**不变量？

### 发现过程

Jones在研究**Von Neumann代数**时意外发现了这个不变量——这完全是数学的意外发现，而非从物理出发。

---

## 核心方法

### 从辫群表示出发

Jones的关键构造：

1. 取**Hecke代数** $H_n(q)$：

$$\sigma_i^2 = (q-1)\sigma_i + q$$

2. 取**特殊表示**（Boltzmann权重）

3. 对任意辫群 $B_n$ 的表示，计算**迹**（trace）：

$$V(L) = \text{Tr}(\pi(\beta))$$

其中 $\beta \in B_n$ 是纽结对应的辫。

### Skein关系

得到的 Jones 多项式满足：

$$t^{-1} V(L_+) - t V(L_-) = (t^{1/2} - t^{-1/2}) V(L_0)$$

其中 $L_+, L_-, L_0$ 是同一交叉点的三种构型。

---

## 关键结果

### 定理（Jones, 1985）

对任意纽结或链环 $L$：

$$V(L)(t) \in \mathbb{Z}[t^{-1}, t]$$

- 是**Laurent多项式**
- 在**手性翻转**下对称：$V(L^*)(t) = V(L)(t^{-1})$
- 对**平凡纽结**：$V(\text{unknot}) = 1$

### Jones多项式的例子

| 纽结 | Jones多项式 |
|------|-------------|
| 平凡纽结 | $1$ |
| 三叶结 | $t^{-1} + t^{-3} - t^{-4}$ |
| 八字结 | $t^{-2} - t^{-1} + 1 - t + t^2$ |

---

## 创新点

1. **全新构造方法**：从Von Neumann代数（算子代数）导出拓扑不变量——跨领域的意外联系
2. **强于Alexander**：能区分Alexander无法区分的纽结（如Kinoshita–Terasaka结）
3. **skein关系**：简洁的递推关系使计算可行
4. **物理预兆**：后来Witten (1989)发现Jones多项式有物理（QFT）起源

---

## 历史地位

```
1984  Jones在算子代数研究中意外发现
  ↓
1985  正式发表
  ↓
1989  Witten用CS路径积分给出物理解释
  ↓
1990  Jones获Fields奖（与Witten并列）
  ↓
2000  Khovanov给出范畴化（Khovanov同调）
```

---

## 后续影响

| 年份 | 工作 | 意义 |
|------|------|------|
| 1985 | Jones多项式 | 新不变量 |
| 1989 | HOMFLY-PT | Jones的推广（双变量） |
| 1989 | Witten | 物理解释（CS理论） |
| 1990 | Jones获Fields奖 | 算子代数→拓扑 |
| 2000 | Khovanov同调 | 范畴化 |

---

## 与物理的联系

虽然Jones的出发点是纯数学（算子代数），但：
- **Witten (1989)**：Jones多项式来自**Chern-Simons路径积分**
- 这说明**存在物理机制**产生像Jones这样的拓扑不变量
- 物理和拓扑之间有**深层几何联系**

---

## 原文结论（摘录）

> "The polynomial invariant introduced here is perhaps the first genuinely new knot invariant since Alexander's work in 1923."

---

## 相关知识点

- [[Jones多项式]] — 本文的主题
- [[辫群]] — Jones多项式的代数基础
- [[Chern-Simons理论]] — Witten (1989)给出的物理解释
- [[HOMFLY-PT多项式]] — Jones的推广
- [[Khovanov同调]] — Jones的范畴化
- [[量子群]] — Jones多项式的代数结构

---

## 标签

#论文笔记 #纽结理论 #算子代数 #Jones多项式 #辫群
