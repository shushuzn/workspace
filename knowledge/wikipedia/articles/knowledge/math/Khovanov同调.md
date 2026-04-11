# Khovanov同调

## 基本信息

- **原文**：Khovanov homology
- **发明者**：Mikhail Khovanov (2000)
- **类型**：联络目的范畴化不变量
- **本质**：Jones多项式的范畴化

---

## 与Jones多项式的关系

| Jones多项式 | Khovanov同调 |
|-------------|-------------|
| 数值不变量 | 范畴（带更多结构） |
| $V(L)(t)$ | $Kh(L) = \bigoplus_i H^i(L)$ |
| skein关系 | 范畴的映射 |

---

## 定义

### 构造

1. **立方体构造**：对每个交叉分配两种状态（0/1）
2. **陈类赋值**：对每个顶点赋值模2的交叉数
3. **同调群**：构造边界算子 $d$

### 范畴化

$$Kh(L) = \bigoplus_{i,j} H^{i,j}(L)$$

同调代数来自链复形的范畴。

---

## 与Chern-Simons理论的关系

### Witten 1994 猜想

$$Kh(L) = q\text{-graded Euler characteristic of } Z_{CS}(L)$$

Khovanov同调的欧拉示性数 = Jones多项式。

---

## 应用

1. **低维拓扑学**：辨别无法用Jones多项式区分的联络目
2. **四维流形**：与四维代数几何有关
3. **镜像对称**：与几何Langlands对偶有关

---

## 相关条目

- [[Jones多项式]] — Khovanov同调是Jones的范畴化
- [[Chern-Simons理论]] — CS理论产生Khovanov同调
- [[范畴化]] — Khovanov同调是范畴化的典型例子
- [[量子群]] — Khovanov同调的代数结构
- [[量子场论的数学物理]] — 山崎雅人演讲提到范畴化与同调

---

## 参考文献

- Khovanov 2000 — "A categorified Jones polynomial"
- Witten 2014 — "Khovanov homology and Jones polynomial" (未发表猜想)
