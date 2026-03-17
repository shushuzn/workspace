# 理论验证数据收集指南

**创建日期:** 2026-03-06  
**目标:** 收集 20-30 个数据点验证标度律  
**用途:** 验证 sigma ∝ (P/(v*d))^alpha

---

## 📊 必需数据字段

| 字段 | 符号 | 单位 | 必填 | 说明 |
|------|------|------|------|------|
| 论文 ID | paper_id | - | ✅ | LIG_001, LIG_002... |
| DOI | doi | - | ✅ | 永久标识符 |
| 激光功率 | P | W | ✅ | 通常 5-30 W |
| 扫描速度 | v | mm/s | ✅ | 通常 10-100 mm/s |
| 光斑直径 | d | μm | ✅ | 通常 80-150 μm |
| 电导率 | sigma | S/m | ✅ | 通常 1e5 - 1e7 S/m |
| 备注 | notes | - | ⏳ | 特殊条件说明 |

---

## 🔍 数据来源

### 优先级 1: 电导率优化论文 (15 篇)

**检索关键词:**
```
"laser-induced graphene" electrical conductivity optimization
"laser-induced graphene" laser parameters conductivity
LIG electrical properties process parameters
```

**使用:** `../literature/50_PAPER_TARGET_LIST.md`

**目标:** 每篇提取 5-10 个数据点

---

### 优先级 2: 工艺参数研究 (10 篇)

**检索关键词:**
```
"laser-induced graphene" power speed conductivity
LIG laser power density electrical
```

**目标:** 每篇提取 3-5 个数据点

---

### 优先级 3: 综述论文 (5 篇)

**检索关键词:**
```
"laser-induced graphene" review electrical properties
```

**目标:** 提取汇总数据表

---

## 📝 提取流程

### 步骤 1: 获取论文 (Day 1-2)

1. 点击检索链接
2. 下载 PDF
3. 保存到 `theory/data/pdfs/`
4. 记录到追踪表

---

### 步骤 2: 数据提取 (Day 3-7)

**使用工具:** `theory/data/data_collection_template.csv`

**提取位置:**
- 实验部分 (Experimental Section)
- 结果与讨论 (Results and Discussion)
- 表格 (Tables)
- 图表坐标轴 (Figures)

**示例:**
```
论文：Lin et al. Nature Comm 2014

从 Table 1 提取:
P = 10.6 W
v = 50 mm/s
d = 100 μm
sigma = 1.2e5 S/m
```

---

### 步骤 3: 数据验证 (Day 8-10)

**检查:**
- 单位是否正确？
- 数值范围是否合理？
- 是否有异常值？

**合理范围:**
- P: 5-30 W
- v: 10-100 mm/s
- d: 80-150 μm
- sigma: 1e4 - 1e7 S/m

---

## 📈 验证方法

### 运行验证脚本

```bash
cd theory
py scripts/scaling_law_validation.py
```

**输出:**
- 拟合的 alpha 值
- R² 拟合优度
- 验证图表

---

### 成功标准

| 指标 | 目标值 | 状态 |
|------|--------|------|
| 数据点数量 | 20-30 | ⏳ |
| alpha 范围 | 1.0-2.0 | ⏳ |
| R² | > 0.75 | ⏳ |

---

## 💡 提取技巧

### 技巧 1: 优先提取表格数据

- 表格数据最准确
- 通常包含完整参数
- 无需从图表读取

---

### 技巧 2: 图表数据提取

使用 WebPlotDigitizer:
```
https://automeris.io/WebPlotDigitizer/
```

**步骤:**
1. 截图图表
2. 上传到工具
3. 校准坐标轴
4. 提取数据点
5. 导出 CSV

---

### 技巧 3: 注意单位转换

| 原始单位 | 目标单位 | 转换 |
|----------|----------|------|
| mW | W | ÷ 1000 |
| cm/s | mm/s | × 10 |
| S/cm | S/m | × 100 |
| μm | μm | 不变 |

---

## ⚠️ 常见问题

### Q: 论文没有明确给出光斑直径？

**A:** 
- 查找 Experimental 部分
- 通常 CO2 激光器 d ≈ 100-120 μm
- 或标注为"estimated"

---

### Q: 电导率单位是 S/cm？

**A:** 
- 转换为 S/m: sigma_Sm = sigma_Scm × 100

---

### Q: 只有电阻率数据？

**A:** 
- 电导率 = 1/电阻率
- sigma = 1/rho

---

## 📋 进度追踪

| 日期 | 论文数 | 数据点数 | 累计 | 状态 |
|------|--------|----------|------|------|
| Day 1 | 5 | 25 | 25 | ⏳ |
| Day 2 | 10 | 50 | 75 | ⏳ |
| Day 3 | 15 | 75 | 150 | ⏳ |
| Day 4 | 20 | 100 | 250 | ⏳ |
| Day 5 | 25 | 125 | 375 | ⏳ |
| Day 6-7 | 30 | 150 | 525 | ⏳ |

**目标:** 30 篇论文，提取 20-30 个独立数据点 (去重后)

---

## 📁 文件结构

```
theory/
├── data/
│   ├── data_collection_template.csv
│   ├── lig_data_collected.csv (待创建)
│   └── pdfs/ (待创建)
├── scripts/
│   └── scaling_law_validation.py
├── figures/
│   └── scaling_law_*.png (待创建)
└── DATA_COLLECTION_GUIDE.md (本文件)
```

---

*创建日期：2026-03-06*  
*状态：准备就绪，开始收集*
