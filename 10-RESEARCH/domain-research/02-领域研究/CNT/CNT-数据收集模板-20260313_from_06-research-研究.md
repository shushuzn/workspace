# CNT 数据收集模板

**创建日期:** 2026-03-13 18:32  
**版本:** v1.0

---

## 📊 数据字段定义

### 必填字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| sample_id | string | 样本 ID | CNT-001 |
| cnt_type | enum | CNT 类型 | SWCNT/MWCNT |
| length | float | 长度 (μm) | 10.5 |
| diameter | float | 直径 (nm) | 50.0 |
| aspect_ratio | float | 长径比 | 210 |
| purity | float | 纯度 (%) | 95.5 |
| conductivity | float | 导电性 (S/m) | 1.5e+06 |
| source | string | 数据来源 | PMID:12345678 |

### 选填字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| dispersion_method | string | 分散方法 | 超声分散 |
| dispersant_type | string | 分散剂类型 | SDS |
| dispersant_conc | float | 分散剂浓度 (mg/mL) | 1.0 |
| treatment_temp | float | 处理温度 (°C) | 25.0 |
| treatment_time | float | 处理时间 (min) | 30.0 |
| sonication_power | float | 超声功率 (W) | 100.0 |
| measurement_method | string | 测量方法 | 四探针法 |

---

## 📋 数据收集表

| sample_id | cnt_type | length | diameter | aspect_ratio | purity | conductivity | source |
|-----------|----------|--------|----------|--------------|--------|--------------|--------|
| CNT-001 | SWCNT | 5.0 | 2.0 | 2500 | 90.0 | 1.2e+06 | PMID:xxx |
| CNT-002 | MWCNT | 10.0 | 50.0 | 200 | 95.0 | 1.5e+06 | PMID:xxx |
| ... | ... | ... | ... | ... | ... | ... | ... |

---

## 🔍 PubMed 检索策略

### 检索式

```
("carbon nanotube" OR "CNT" OR "SWCNT" OR "MWCNT") 
AND ("conductivity" OR "conductive" OR "electrical property") 
AND ("prediction" OR "model" OR "machine learning")
AND ("2020/01/01"[Date - Publication] : "2026/12/31"[Date - Publication])
```

### 纳入标准

1. 报告 CNT 导电性数据
2. 提供 CNT 物理参数 (长度/直径/纯度等)
3. 人类语言：英文或中文
4. 发表年份：2020-2026

### 排除标准

1. 仅定性描述，无定量数据
2. 综述文章 (除非引用原始数据)
3. 无法获取全文
4. 数据不完整

---

## 📊 数据质量标准

### 完整性检查

- [ ] 所有必填字段有值
- [ ] 数值在合理范围内
- [ ] 单位统一

### 一致性检查

- [ ] 长径比 = 长度/直径 (允许±10% 误差)
- [ ] 纯度范围：0-100%
- [ ] 导电性>0

### 异常值检测

- [ ] 长径比>10000 (标记为异常)
- [ ] 纯度<50% (标记为低纯度)
- [ ] 导电性>1e+08 (标记为超高)

---

## 📝 数据提取流程

1. PubMed 检索 → 获取文献列表
2. 筛选标题/摘要 → 纳入/排除
3. 获取全文 → 提取数据
4. 填写数据表 → 质量检查
5. 存入数据库 → 备份

---

*Created:* 2026-03-13 18:32  
*Status:* ✅ 数据收集模板完成  
*Next:* PubMed 检索策略实施
