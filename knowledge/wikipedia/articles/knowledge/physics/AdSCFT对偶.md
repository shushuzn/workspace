# AdS/CFT对偶

## 基本信息

- **原文**：Anti-de Sitter / Conformal Field Theory correspondence
- **提出者**：Maldacena (1997)
- **本质**：引力理论与共形场论之间的全息对偶
- **意义**：量子引力理解的重大突破，桥接弦论与量子场论

---

## 核心表述

### AdS₄/CFT₃（Maldacena conjecture）

$$N \gg 1:\quad \mathcal{N}=4 \text{ SYM } \leftrightarrow \text{Type IIB string on } AdS_5 \times S^5$$

| 边界（ conformal field theory） | 体内（anti-de Sitter space） |
|--------------------------------|------------------------------|
| $d$ 维 CFT | $d+1$ 维 AdS |
| 耦合常数 $g_{YM}^2 N$ | 弦耦合 $g_s$ |
| 't Hooft 耦合 $\lambda = g_{YM}^2 N$ | 弦张力 $\sqrt{\lambda}$ |

---

## 维度对应表

| CFT（边界） | AdS（体内） | 物理应用 |
|-------------|-------------|---------|
| d=2 | AdS₃ | BTZ黑洞，2D共形场论 |
| d=3 | AdS₄ | 纳米流体，BCS超导 |
| d=4 | AdS₅ | $\mathcal{N}=4$ SYM，量子色动力学 |

---

## 与Chern-Simons理论的关系

### AdS₃/CFT₂ 中的 CS 理论

**Witten (1999)**：三维AdS空间的引力等价于边界上的CS理论：

$$S_{GR}[AdS_3] = \Gamma[z_{CFT_2}]$$

- 体内：$SL(2,\mathbb{R})$ CS理论
- 边界：2D共形场论（Viraroso代数）

### CS路径积分 = CFT correlator

$$Z_{CS} = \langle e^{iS_{CS}} \rangle = Z_{CFT_2}$$

CS配分函数 = CFT₂的关联函数。

---

## 在量子引力中的地位

### 为什么重要

1. **量子引力的非微扰定义**：引力在AdS空间中有明确的非微扰定义
2. **黑洞信息悖论的解**：视界面编码在边界CFT中，信息不丢失
3. **计算工具**：强耦合场论可映射到弱耦合引力（经典计算）

### 局限性

| 限制 | 说明 |
|------|------|
| AdS边界条件 | 宇宙学常数必须为负（AdS） |
| 紫外完备性 | 边界CFT是紫外完备的 |
| 真实宇宙 | 不适用于 de Sitter 宇宙 |

---

## 与拓扑数学的联系

### 全息对偶中的拓扑结构

| 拓扑概念 | 在AdS/CFT中的角色 |
|----------|-----------------|
| 陈数 | 拓扑不变量保护边缘态 |
| Chern-Simons | 3D引力的有效理论 |
| 拓扑序 | 边界CFT中的拓扑相位 |
| Khovanov同调 | 边界上的纽结不变量 |

### 边界态与体内对应

**RT公式**（Ryu-Takayanagi, 2006）：

$$S_{entanglement} = \frac{\text{Area}(\gamma)}{4G_N}$$

- $\gamma$：体内极小曲面
- 对应边界子区域的纠缠熵

---

## 应用

### 凝聚态物理

| 系统 | AdS/CFT应用 |
|------|-------------|
| 纳米流体 | 输运系数的计算 |
| 高温超导 | 有机金属中的相变 |
| 量子相变 | AdS/CMT |

### 量子信息

- **纠缠熵**：RT公式给出严格计算
- **量子误差纠正**：AdS空间中的误差纠正码
- **tensor network**：MERA（多尺度纠缠重整化Ansatz）

---

## 相关条目

- [[BTZ黑洞]] — AdS₃中的黑洞，CFT₂的引力对偶
- [[Chern-Simons理论]] — 3D引力的CS formulation
- [[拓扑量子计算]] — AdS/CFT启发了拓扑量子计算的某些思想
- [[量子场论的数学物理]] — 山崎雅人演讲涉及AdS₃/CFT₂
- [[分数量子霍尔效应]] — 与AdS/CFT共享某些数学结构

---

## 参考文献

- Maldacena 1997 — "The large N limit of superconformal field theories and anti-de Sitter spacetime"
- Witten 1998 — "Anti de Sitter space and holography"
- Ryu & Takayanagi 2006 — "Holographic derivation of entanglement entropy"
- Gubser, Klebanov, Polyakov 1998 — "Gauge theory correlators from non-critical string theory"
