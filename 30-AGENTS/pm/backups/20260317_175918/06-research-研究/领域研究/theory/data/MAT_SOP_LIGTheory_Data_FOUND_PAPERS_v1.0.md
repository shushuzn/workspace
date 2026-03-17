# 找到的 LIG 数据相关论文

**搜索日期:** 2026-03-06  
**来源:** Google Scholar  
**搜索结果:** 约 10,800 条

---

## 🎯 高优先级论文 (包含数据表)

### 1. Parametric study of laser-induced graphene conductive traces

**标题:** Parametric study of laser‐induced graphene conductive traces and their application as flexible heaters

**作者:** G Karimi, I Lau, M Fowler

**期刊:** International Journal of Energy Research, 2021

**引用:** 24 次

**关键信息:**
> "The mean values of electrical resistances are also listed in Table 1"

**数据:** 包含 Table 1 - 电阻值数据表！

**链接:**
```
https://onlinelibrary.wiley.com/doi/abs/10.1002/er.6701
```

**优先级:** ⭐⭐⭐⭐⭐ (明确提到数据表)

---

### 2. Influence of lasing parameters on LIG resistance

**标题:** Influence of lasing parameters on the morphology and electrical resistance of polyimide-based laser-induced graphene (LIG)

**作者:** J de la Roche, I López-Cifuentes, A Jaramillo-Botero

**期刊:** Carbon Letters, 2023

**引用:** 71 次

**关键信息:** 研究激光参数对电阻的影响

**链接:**
```
https://link.springer.com/article/10.1007/s42823-022-00447-2
```

**优先级:** ⭐⭐⭐⭐⭐ (直接研究参数 - 电阻关系)

---

### 3. Design of experiments and optimization of LIG

**标题:** Design of experiments and optimization of laser-induced graphene

**作者:** R Murray, M Burke, D Iacopino, AJ Quinn

**期刊:** ACS omega, 2021

**引用:** 75 次

**关键信息:**
> "Sensing devices based on electrical conductivity or thermal conductivity changes"
> "sheet resistance, morphology, and Raman data"

**链接:**
```
https://pubs.acs.org/doi/pdf/10.1021/acsomega.1c00309
```

**优先级:** ⭐⭐⭐⭐ (实验优化，包含电阻数据)

---

### 4. Laser-induced graphene fibers

**标题:** Laser-induced graphene fibers

**作者:** LX Duy, Z Peng, Y Li, J Zhang, Y Ji, JM Tour

**期刊:** Carbon, 2018

**引用:** 543 次

**关键信息:**
> "high electrical conductivity"

**链接:**
```
https://www.sciencedirect.com/science/article/pii/S0008622317310370
```

**优先级:** ⭐⭐⭐⭐ (高引用，Tour 课题组)

---

### 5. Laser-induced porous graphene films (Nature Comm 2014)

**标题:** Laser-induced porous graphene films from commercial polymers

**作者:** J Lin, Z Peng, Y Liu, F Ruiz-Zepeda, R Ye, JM Tour

**期刊:** Nature Communications, 2014

**引用:** 3239 次 ⭐⭐⭐

**关键信息:** LIG 开创性论文

**链接:**
```
https://www.nature.com/articles/ncomms6714
https://www.nature.com/articles/ncomms6714.pdf (PDF)
```

**优先级:** ⭐⭐⭐⭐⭐ (开创性论文，必有数据)

---

## 📋 数据提取计划

### 第一步：获取 PDF

1. 打开上述链接
2. 下载 PDF (机构订阅或 ResearchGate)
3. 保存到 `theory/data/pdfs/`

### 第二步：提取数据

**从每篇论文查找:**
- Experimental Section (激光参数)
- Results and Discussion (电导率/电阻数据)
- Tables (数据表)
- Figures (图表数据)

**提取字段:**
- P (W) - 激光功率
- v (mm/s) - 扫描速度
- d (μm) - 光斑直径
- σ (S/m) 或 R (Ω) - 电导率或电阻

### 第三步：填入 CSV

**文件:** `literature_data.csv`

```csv
paper_id,P_W,v_mms,d_um,sigma_Sm,notes,status
LIG_001,10.6,50,100,1.2e5,From Nature Comm 2014,Extracted
...
```

---

## 🎯 目标

**从这 5 篇论文提取:**
- 预计 20-30 个数据点
- 覆盖不同 P, v, d 组合
- 验证理论模型

---

*创建日期：2026-03-06*  
*下一步：下载 PDF 并提取数据*
