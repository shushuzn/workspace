# 详细数据提取指南

**创建日期:** 2026-03-06  
**目标:** 从 3 篇 Sci-Hub PDF 提取数据

---

## 📁 PDF 文件列表

### 1. Lin et al. Nature Communications 2014

**下载:**
```
https://sci-hub.ru/download/moscow/3336/b91ee6bb47244647d48391ff031506ad/lin2014.pdf
```

**查找位置:**
- **Page 2-3:** Experimental Section (实验方法)
- **Page 4-5:** Results and Discussion (结果与讨论)
- **Figure 1:** LIG 形貌图
- **Figure 2:** 电导率数据

**预期数据:**
- 激光功率：~10.6 W
- 扫描速度：~50 mm/s
- 光斑直径：~100 μm
- 电导率：~1e5 S/m

**提取步骤:**
1. 打开 PDF
2. 搜索 "conductivity" 或 "resistance"
3. 查找数字和单位
4. 告诉我数值

---

### 2. Karimi et al. Int J Energy Res 2021

**下载:**
```
https://sci-hub.ru/download/2024/8531/1bdfa8d1f69f5200f1d87e8ec054c08f/karimi2021.pdf
```

**查找位置:**
- **Table 1:** 电阻/电导率数据表 ⭐⭐⭐
- **Page 3-4:** Experimental details
- **Figure 2-3:** 参数研究图

**预期数据:**
- 多组 P, v 参数
- 电阻或电导率值
- 预计 10-15 数据点

**提取步骤:**
1. 打开 PDF
2. 找到 Table 1
3. 抄录所有 P, v, R 或 σ 值
4. 告诉我

---

### 3. Murray et al. ACS Omega 2021

**下载:**
```
https://sci-hub.ru/download/zero/downloads/2021-08-10/04f5/murray2021.pdf
```

**查找位置:**
- **Page 2-3:** Experimental Section
- **Results:** Sheet resistance 数据
- **Figure 3-4:** 参数优化图

**预期数据:**
- Sheet resistance (Ω/sq)
- 激光参数
- 预计 5-10 数据点

**提取步骤:**
1. 打开 PDF
2. 搜索 "sheet resistance"
3. 查找数字
4. 告诉我

---

## 📊 数据格式模板

### 找到数据后，按以下格式告诉我：

**示例:**

```
论文 1 (Lin 2014):
- P = 10.6 W
- v = 50 mm/s
- d = 100 μm
- σ = 1.2e5 S/m

论文 2 (Karimi 2021) Table 1:
- P=8W, v=40mm/s, R=500 Ω → σ=?
- P=8W, v=60mm/s, R=600 Ω → σ=?
- P=12W, v=40mm/s, R=300 Ω → σ=?
...

论文 3 (Murray 2021):
- P=9.5W, v=45mm/s, Rs=? Ω/sq
...
```

---

## 🔢 单位转换

### 电阻 → 电导率

如果找到的是电阻 (R) 或薄层电阻 (Rs):

```
σ = 1 / (Rs × t)
```

其中 t 是薄膜厚度 (通常 ~10-50 μm)

**或者简单处理:**
- 告诉我 R 或 Rs 值
- 我来计算 σ

---

### 单位统一

| 原始单位 | 目标单位 | 转换 |
|----------|----------|------|
| W | W | 不变 |
| mW | W | ÷ 1000 |
| mm/s | mm/s | 不变 |
| cm/s | mm/s | × 10 |
| μm | μm | 不变 |
| nm | μm | ÷ 1000 |
| S/cm | S/m | × 100 |
| S/m | S/m | 不变 |
| Ω | S/m | 需要转换 |
| Ω/sq | S/m | 需要厚度 |

---

## 📝 快速提取清单

### 每篇论文查找

- [ ] 激光功率 (P)
- [ ] 扫描速度 (v)
- [ ] 光斑直径/线宽 (d)
- [ ] 电导率/电阻 (σ 或 R)
- [ ] 气氛 (Air/Ar/N₂)
- [ ] 基底材料 (PI/其他)

---

## 💡 提示

### 搜索关键词

在 PDF 中搜索以下关键词：

**英文:**
- "conductivity"
- "resistance"
- "sheet resistance"
- "electrical"
- "laser power"
- "scan speed"
- "spot size"

**符号:**
- "σ" (电导率)
- "R" (电阻)
- "P" (功率)
- "v" (速度)

---

## 🎯 目标

**从 3 篇论文提取:**
- 最少：20 数据点
- 目标：40-50 数据点
- 理想：50+ 数据点

**预期 R² 提升:**
- 当前：0.356
- 预期：0.6-0.8

---

## 📞 找到数据后

**告诉我:**
```
"论文 1 数据：P=XX, v=XX, d=XX, σ=XX
论文 2 数据：...
论文 3 数据：..."
```

**我来做:**
1. 填入 CSV
2. 运行验证
3. 生成图表
4. 撰写报告

**预计时间:** 15 分钟

---

*指南创建日期：2026-03-06*  
*下一步：下载 PDF 并提取数据*
