# LIG 理论 - 学习指南

**创建日期:** 2026-03-06  
**目标:** 系统掌握 LIG 电导率理论  
**预计时间:** 4-6 小时

---

## 📚 学习路线

### 阶段 1: 基础理解 (1-2 小时)

**阅读:** `01_theoretical_framework.md`

**学习目标:**
- [ ] 理解物理过程分解
- [ ] 掌握热传导方程
- [ ] 理解石墨化动力学
- [ ] 理解 Percolation 理论

**关键问题:**
1. 激光如何产生温度场？
2. 温度如何影响石墨化？
3. 石墨化如何影响电导率？

---

### 阶段 2: 深入推导 (2-3 小时)

**阅读:** `03_deep_derivation.md`

**学习目标:**
- [ ] 理解量纲分析
- [ ] 掌握 Arrhenius 方程推导
- [ ] 理解渗流理论
- [ ] 掌握标度律分析

**练习:**
1. 自己推导 T_max 公式
2. 推导 χ(t) 的解析解
3. 分析高/低功率极限

---

### 阶段 3: 代码实践 (1 小时)

**运行:** `scripts/symbolic_derivation.py`

**学习目标:**
- [ ] 理解符号推导
- [ ] 验证公式正确性
- [ ] 探索参数影响

**修改练习:**
1. 改变参数值
2. 添加新的物理效应
3. 尝试不同的核函数

---

### 阶段 4: 验证分析 (1 小时)

**运行:** `scripts/scaling_law_validation.py`

**学习目标:**
- [ ] 理解数据拟合
- [ ] 掌握 R² 的意义
- [ ] 理解 alpha 的物理意义

---

## 📖 核心公式清单

### 必须记住的公式

1. **峰值温度:**
   $$T_{max} = T_{env} + \frac{C \alpha P}{\rho C_p v d^2}$$

2. **石墨化程度:**
   $$\chi = 1 - \exp\left[-\frac{A d}{v} \exp\left(-\frac{B v d^2}{P}\right)\right]$$

3. **电导率:**
   $$\sigma = \sigma_0 \chi^t$$

4. **标度律:**
   $$\sigma \propto \left(\frac{P}{v d^2}\right)^\alpha$$

---

## 🧠 概念理解检查

### 热传导

**Q1:** 为什么 T_max 与 P 成正比？

**A:** 功率越大，输入能量越多，温升越高。

**Q2:** 为什么 T_max 与 v 成反比？

**A:** 速度越快，激光在某点停留时间越短，加热越少。

**Q3:** 为什么 T_max 与 d² 成反比？

**A:** 光斑越大，能量越分散，功率密度越低。

---

### 石墨化动力学

**Q4:** 为什么使用 Arrhenius 方程？

**A:** 石墨化是热激活过程，需要克服活化能势垒。

**Q5:** 双重指数的物理意义？

**A:** 温度本身由指数决定 (Boltzmann)，石墨化速率又指数依赖温度。

---

### 电导率模型

**Q6:** 什么是渗流阈值？

**A:** 导电路径开始连通时的临界石墨化程度。

**Q7:** 临界指数 t 的意义？

**A:** 描述电导率在阈值附近的增长速度。

---

## 💻 实践练习

### 练习 1: 参数敏感性

修改 `symbolic_derivation.py`:
- 改变 A, B, t 的值
- 观察 σ 的变化
- 哪个参数最敏感？

### 练习 2: 极限分析

验证:
- 高功率极限公式
- 低功率极限公式
- 与完整公式对比

### 练习 3: 数据拟合

使用 `scaling_law_validation.py`:
- 修改 sample_data
- 拟合新的 alpha 值
- 分析 R² 变化

---

## 📝 学习笔记模板

```markdown
# 学习笔记 - [日期]

## 今天学到的

1. [概念 1]
   - 关键点
   - 疑问

2. [概念 2]
   - 关键点
   - 疑问

## 推导练习

[自己的推导过程]

## 问题清单

1. [问题 1]
2. [问题 2]

## 下一步

- [ ] [任务 1]
- [ ] [任务 2]
```

---

## 🔗 进阶阅读

### 热传导

- Incropera & DeWitt, "Fundamentals of Heat and Mass Transfer"
- Carslaw & Jaeger, "Conduction of Heat in Solids"

### 化学动力学

- Laidler, "Chemical Kinetics"

### 渗流理论

- Stauffer & Aharony, "Introduction to Percolation Theory"

### LIG 技术

- Tour JM, "Laser-induced graphene: from discovery to translation" (2019)
- Lin J et al., "Laser-induced porous graphene films" (2014)

---

## 💡 学习建议

1. **循序渐进**: 不要跳过基础直接看公式
2. **动手推导**: 纸上推导比阅读更有效
3. **代码验证**: 用代码验证推导结果
4. **讨论问题**: 有疑问随时提问

---

*创建日期：2026-03-06*  
*祝你学习愉快！*
