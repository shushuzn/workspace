# BTZ黑洞

## 基本信息

- **原文**：BTZ black hole (Banados-Teitelboim-Zanelli black hole)
- **发现者**：Banados, Teitelboim, Zanelli (1992)
- **类型**：三维黑洞解（AdS₃空间中的黑洞）
- **重要意义**：唯一已知有熵的二维/三维量子引力模型

---

## 核心概念

### 度规

BTZ黑洞的线元（质量 $M$ 和角动量 $J$）：

$$ds^2 = -N^2 dt^2 + \frac{dr^2}{N^2} + r^2(N^\phi dt - d\phi)^2$$

其中：

$$N^2 = -M + \frac{r^2}{\ell^2} + \frac{J^2}{4r^2}$$

- $\ell$：AdS半径（cosmological constant $\Lambda = -1/\ell^2$）
- 事件视界由 $N^2 = 0$ 决定

### 分类

| 类型 | 条件 |
|------|------|
| 极端黑洞 | $M^2\ell^2 = J^2$ |
| 施瓦西解 | $J = 0$ |
| 裸奇点 | $M^2\ell^2 < J^2$ |

---

## 与Chern-Simons理论的关系

### CS formulation of 3D gravity

三维爱因斯坦-希尔伯特作用量等价于两个CS项：

$$S_{GR} = \frac{1}{16\pi G}\int d^3x \sqrt{-g}(R - 2\Lambda) = S_{CS}[A] - S_{CS}[\tilde{A}]$$

其中：
- $A$：$SL(2,\mathbb{R})$ 主丛联络
- $\tilde{A}$：对偶联络

### 配分函数

$$Z_{BTZ} = \int \mathcal{D}A \mathcal{D}\tilde{A} e^{i(S_{CS}[A] - S_{CS}[\tilde{A}])}$$

**Witten (1989)**：这个路径积分给出BTZ黑洞的熵！

---

## 与AdS/CFT对偶的关系

### AdS₃/CFT₂

| 空间 | 维度 | 对偶 |
|------|------|------|
| AdS₃ | 3维 | CFT₂（2维共形场论） |
| BTZ黑洞 | 边界 | CFT₂上的热力学 |

### 霍金辐射与CFT

BTZ黑洞的霍金温度：

$$T_H = \frac{\sqrt{M}}{2\pi\ell}$$

对应边界CFT₂的共形温度。

---

## 黑洞熵的拓扑解释

### Cardy公式

BTZ黑洞的微观熵（通过CFT₂计算）：

$$S = 2\pi\sqrt{\frac{cL_0}{24}} + 2\pi\sqrt{\frac{c\bar{L}_0}{24}}$$

- $c$：共形荷（central charge）
- $L_0, \bar{L}_0$：Virasoro算子

### 拓扑熵

**Witten的洞见**：在CS formulation中，黑洞熵来自**拓扑项**：

$$S_{CS} \sim \frac{k}{4\pi} \int_{\partial M} \text{Tr}(A \wedge dA + \frac{2}{3}A \wedge A \wedge A)$$

- 熵正比于 level $k$（与陈数有关）
- 这是熵的**纯拓扑起源**解释

---

## 与拓扑数学的联系

### 陈数与黑洞熵

| 量 | 表达式 | 拓扑含义 |
|----|--------|----------|
| 质量 $M$ | $\frac{r_+^2 + r_-^2}{2\ell^2}$ | 视界面积相关 |
| 角动量 $J$ | $\frac{r_+ r_-}{\ell}$ | Penrose不等式 |
| 熵 | $\frac{\pi r_+}{2G}$ | 贝肯斯坦-霍金熵 |

### CS理论中的黑洞

$$S_{BTZ} = \frac{\pi r_+}{2G} = 2\pi \sqrt{\frac{cL_0}{24}}$$

两种描述完全等价——说明黑洞熵有深层的几何/拓扑起源。

---

## 在量子引力中的地位

### 为什么BTZ是特殊的

1. **唯一可解**：三维中引力完全可积
2. **有熵**：是已知唯一能计算微观熵的黑洞
3. **有全息对偶**：明确的AdS₃/CFT₂描述
4. **通用性**：所有三维黑洞都是BTZ的特例

### 与其他黑洞的关系

```
BTZ (3D)
    ↓ 维数提升
Schwarzschild (4D) ← 不可积
Kerr (4D) ← 有解析解但复杂
```

---

## 相关条目

- [[Chern-Simons理论]] — 3D引力的CS formulation
- [[拓扑量子计算]] — CS理论在拓扑量子计算中的应用
- [[分数量子霍尔效应]] — 与BTZ共享CS路径积分框架
- [[AdS/CFT对偶]] — BTZ是AdS₃/CFT₂的核心
- [[量子场论的数学物理]] — 山崎雅人演讲涉及AdS₃/CFT₂

---

## 参考文献

- Banados, Teitelboim, Zanelli 1992 — "The black hole in three-dimensional spacetime"
- Witten 1988/1989 — "3D gravity and CS theory"
- Strominger 1997 — "Black hole entropy from near-horizon microstates"
