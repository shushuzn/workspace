# HOMFLY-PT多项式

## 基本信息

- **原文**：HOMFLY-PT polynomial
- **发现者**：Hoste, Ocneanu, Freyd, Lickorish, Hoste, Yetter (1985)
- **类型**：联络目不变量（双变量多项式）

---

## 定义

### 双变量skein关系

$$l P(L_+) + l^{-1} P(L_-) + m P(L_0) = 0$$

其中 $l, m$ 是两个变量。

### 与其他多项式的关系

| 特殊化 | 结果 |
|--------|------|
| $l = t^{-1}, m = (t^{1/2} - t^{-1/2})$ | Jones多项式 |
| $l = 1, m = (q^{1/2} - q^{-1/2})$ | Alexander多项式 |

---

## Jones多项式的关系

$$V(L)(t) = P(L)(t^{-1}, t^{1/2} - t^{-1/2})$$

HOMFLY-PT 包含的信息比 Jones 多项式更多。

---

## 物理意义

### 统计力学

HOMFLY-PT多项式来自六顶点模型（six-vertex model）的可积系统。

### 与Chern-Simons理论

$$P(L)(l,m) = Z_{CS}(L)$$

三维Chern-Simons路径积分给出HOMFLY-PT多项式（$l = e^{2\pi i / k}$）。

---

## 与Khovanov同调的关系

### HOMFLY-PT 的范畴化

| 数值多项式 | 范畴化版本 |
|------------|------------|
| Jones多项式 | Khovanov同调 |
| HOMFLY-PT | **Khovanov-Rozansky同调** |

**Khovanov-Rozansky (2000s)**：构造了 HOMFLY-PT 的范畴化版本——KR同调，是双变量版本的范畴化。

### 范畴化层次

$$V(L) \xrightarrow{\text{范畴化}} Kh(L) \xrightarrow{\text{特殊化}} P(L)$$

- Jones → Khovanov（同调）
- HOMFLY-PT → KR同调（高阶同调）

---

## 与辫群的关系

### Hecke 代数

HOMFLY-PT 多项式来自 **Hecke 代数** $H_n(q)$：

$$\sigma_i^2 = (q-1)\sigma_i + q$$

- 当 $q \to 1$，Hecke 代数退化为辫群代数 $B_n$
- Hecke 代数是辫群的**量子化**

###辫群表示

$$P(L) = \text{Tr}(\mathcal{R} \cdot \mathcal{R}^*)$$

- $\mathcal{R}$：辫群表示的 R-矩阵
- 来自量子群 $U_q(sl_N)$ 的表示

---

## 与量子群的关系

### $U_q(sl_N)$ 表示

| 量子群 | 对应不变量 |
|--------|-----------|
| $U_q(sl_2)$ | Jones多项式 |
| $U_q(sl_N)$ | HOMFLY-PT（$N$ 变量） |

HOMFLY-PT 的两个变量：
- $l = q^{N/2}$
- $m = q^{1/2} - q^{-1/2}$

---

## Skein关系详解

### 基础skein

$$l P(L_+) + l^{-1} P(L_-) + m P(L_0) = 0$$

三个构型：
- $L_+$：标准交叉
- $L_-$：反向交叉
- $L_0$：消除交叉

### 标准化

规范化的 HOMFLY-PT 满足：

$$P(\text{平凡纽结}) = 1$$
$$P(\text{平凡链环}) = \frac{l - l^{-1}}{m}$$

---

## 相关条目

- [[Jones多项式]] — HOMFLY-PT的特殊化（$l=t^{-1}, m=t^{1/2}-t^{-1/2}$）
- [[Chern-Simons理论]] — 物理上产生HOMFLY-PT（$l=e^{2\pi i/k}$）
- [[辫群]] — Hecke代数是辫群的量子化
- [[量子群]] — $U_q(sl_N)$ 表示产生HOMFLY-PT
- [[Khovanov同调]] — Jones的范畴化；HOMFLY-PT对应Khovanov-Rozansky同调
- [[可积系统]] — 六顶点模型与可积结构
- [[量子场论的数学物理]] — 山崎雅人演讲提到HOMFLY-PT多项式

---

## 参考文献

- HOMFLY, Ocneanu, Freyd, Lickorish, Hoste, Yetter 1985 — "A new polynomial invariant of knots and links"
- Khovanov & Rozansky 1998 — "Matrix factorizations and link homology"
- Webester 2017 — "Khovanov homology and the security of braid group representations"
