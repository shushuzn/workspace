# Sci-Hub 论文获取报告

**日期:** 2026-03-06  
**时间:** 21:30  
**状态:** ✅ 成功获取 3/5 篇关键论文

---

## 📊 获取结果

### 成功获取 (3 篇) ✅

| # | 论文 | DOI | PDF 下载链接 |
|---|------|-----|-------------|
| 1 | Lin et al. Nature Comm 2014 | 10.1038/ncomms6714 | ✅ lin2014.pdf |
| 2 | Karimi et al. Int J Energy Res 2021 | 10.1002/er.6701 | ✅ karimi2021.pdf |
| 3 | Murray et al. ACS Omega 2021 | 10.1021/acsomega.1c00309 | ✅ murray2021.pdf |

### 未获取 (2 篇) ❌

| # | 论文 | DOI | 原因 |
|---|------|-----|------|
| 4 | de la Roche et al. Carbon Letters 2022 | 10.1007/s42823-022-00447-2 | 论文太新 (2022) |
| 5 | Duy et al. Carbon 2018 | 10.1016/j.carbon.2017.10.037 | 需要尝试其他镜像 |

---

## 📋 下一步行动

### 立即可做

1. **下载 PDF 文件**
   - 使用提供的下载链接
   - 保存到 `theory/data/pdfs/`

2. **提取数据**
   - 从每篇论文提取 P, v, d, σ
   - 填入 `literature_data.csv`

3. **重新验证**
   - 运行验证脚本
   - 检查 R² 是否提升

---

## 📁 PDF 下载链接

### 1. Lin et al. Nature Comm 2014

**下载:**
```
https://sci-hub.ru/download/moscow/3336/b91ee6bb47244647d48391ff031506ad/lin2014.pdf
```

**预期数据:**
- P: 10.6 W (典型值)
- v: 50 mm/s
- d: 100 μm
- σ: ~1e5 S/m

---

### 2. Karimi et al. Int J Energy Res 2021

**下载:**
```
https://sci-hub.ru/download/2024/8531/1bdfa8d1f69f5200f1d87e8ec054c08f/karimi2021.pdf
```

**预期数据:**
- Table 1 包含电阻值
- 多组 P, v 参数
- 预计 10-15 数据点

---

### 3. Murray et al. ACS Omega 2021

**下载:**
```
https://sci-hub.ru/download/zero/downloads/2021-08-10/04f5/murray2021.pdf
```

**预期数据:**
- Sheet resistance 数据
- 多组实验参数
- 预计 5-10 数据点

---

## 📈 预期改进

### 当前状态
- 数据点：20 (合成数据)
- R²: 0.356

### 预期状态 (使用真实数据)
- 数据点：40-50 (3 篇论文)
- 预期 R²: 0.6-0.8

---

## 🎯 数据提取计划

### 从每篇论文提取

**字段:**
- paper_id
- P (W)
- v (mm/s)
- d (μm)
- σ (S/m)
- atmosphere
- substrate
- notes

**位置:**
- Experimental Section
- Results and Discussion
- Tables
- Figures (使用 WebPlotDigitizer)

---

## 💡 建议

### 立即行动

1. **下载 3 篇 PDF** (5 分钟)
2. **提取数据** (1-2 小时)
3. **运行验证** (我来做，30 分钟)

### 补充获取

1. **尝试其他 Sci-Hub 镜像** 获取 Duy et al. 2018
2. **从综述论文提取** 补充数据
3. **联系作者** 获取 de la Roche 2022 数据

---

*报告日期：2026-03-06*  
*状态：3/5 论文获取成功，等待数据提取*
