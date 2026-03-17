# 文献数据收集指南

**创建日期:** 2026-03-06  
**目标:** 收集 20-30 篇 LIG 论文，提取 20-50 个数据点

---

## 🎯 数据需求

### 必需字段

| 字段 | 符号 | 单位 | 必填 |
|------|------|------|------|
| 论文 ID | paper_id | - | ✅ |
| 激光功率 | P | W | ✅ |
| 扫描速度 | v | mm/s | ✅ |
| 光斑直径 | d | μm | ✅ |
| 电导率 | σ | S/m | ✅ |

### 可选字段

| 字段 | 说明 |
|------|------|
| atmosphere | 气氛 (Air/Ar/H₂等) |
| substrate | 基底类型 |
| notes | 备注 |

---

## 🔍 数据来源

### 优先级 1: LIG 电导率优化论文

**检索式:**
```
"laser-induced graphene" electrical conductivity optimization
```

**目标期刊:**
- Carbon
- ACS Nano
- Advanced Materials
- Nano Letters

### 优先级 2: 工艺参数研究

**检索式:**
```
"laser-induced graphene" laser parameters conductivity
```

### 优先级 3: 综述论文

**检索式:**
```
"laser-induced graphene" review electrical properties
```

---

## 📋 提取流程

### 步骤 1: 下载论文 (1-2 小时)

1. 使用 Google Scholar
2. 搜索上述关键词
3. 下载 20-30 篇 PDF
4. 保存到 `theory/data/pdfs/`

### 步骤 2: 阅读并提取 (2-3 小时)

**从每篇论文查找:**
- Experimental Section (实验参数)
- Results and Discussion (电导率数据)
- Tables (数据表)
- Figures (图表数据)

**提取示例:**
```
论文：Lin et al. Nature Comm 2014

从 Experimental 部分:
- P = 10.6 W
- v = 50 mm/s
- d = 100 μm

从 Results 部分:
- σ = 1.2e5 S/m

填入 CSV:
LIG_001,10.6,50,100,1.2e5,Air,PI,Example
```

### 步骤 3: 数据整理 (1 小时)

**检查:**
- 单位是否统一？
- 数值范围是否合理？
- 是否有异常值？

**合理范围:**
- P: 5-30 W
- v: 10-100 mm/s
- d: 80-150 μm
- σ: 1e4 - 1e7 S/m

---

## 📊 验证标准

### 数据量

| 指标 | 最小 | 目标 |
|------|------|------|
| 论文数 | 15 | 20-30 |
| 数据点 | 20 | 50+ |

### 数据质量

- [ ] 单位统一
- [ ] 无明显异常值
- [ ] 参数范围覆盖合理

---

## 📁 文件位置

**数据文件:**
- `literature_data.csv` - 数据收集文件

**PDF 存储:**
- `theory/data/pdfs/` - 论文 PDF

**验证脚本:**
- `scripts/scaling_law_validation.py` - 验证拟合

---

## 💡 提取技巧

### 技巧 1: 优先提取表格数据

- 表格数据最准确
- 通常包含完整参数

### 技巧 2: 图表数据提取

使用 WebPlotDigitizer:
```
https://automeris.io/WebPlotDigitizer/
```

### 技巧 3: 注意单位转换

| 原始单位 | 目标单位 | 转换 |
|----------|----------|------|
| mW | W | ÷ 1000 |
| cm/s | mm/s | × 10 |
| S/cm | S/m | × 100 |
| μm | μm | 不变 |

---

## 🎯 下一步

**收集完成后:**

1. 运行验证脚本:
   ```bash
   cd theory
   py scripts/scaling_law_validation.py
   ```

2. 检查结果:
   - R² > 0.75? ✅
   - 参数合理？✅

3. 撰写验证报告

---

*创建日期：2026-03-06*  
*下一步：开始收集数据*
