# CNT 数据质量检查流程

**创建日期:** 2026-03-13 18:44  
**版本:** v1.0

---

## 📊 质量检查层级

### Level 1: 完整性检查

**目标:** 确保所有必填字段有值

| 字段 | 检查规则 | 处理 |
|------|----------|------|
| sample_id | 非空 | 自动生成 |
| cnt_type | 非空，SWCNT/MWCNT | 手动补充 |
| length | 非空，>0 | 手动补充 |
| diameter | 非空，>0 | 手动补充 |
| purity | 非空，0-100 | 手动补充 |
| conductivity | 非空，>0 | 手动补充 |
| source | 非空 | 必填 |

**通过率目标:** >95%

---

### Level 2: 一致性检查

**目标:** 确保数据内部一致

| 检查项 | 规则 | 容差 | 处理 |
|--------|------|------|------|
| 长径比计算 | length/diameter = aspect_ratio | ±10% | 自动修正 |
| 纯度范围 | 0 ≤ purity ≤ 100 | - | 标记异常 |
| 导电性 | conductivity > 0 | - | 标记异常 |

**通过率目标:** >90%

---

### Level 3: 异常值检测

**目标:** 识别潜在错误数据

| 字段 | 异常阈值 | 处理 |
|------|----------|------|
| aspect_ratio | >10000 | 标记为"超高长径比" |
| purity | <50% | 标记为"低纯度" |
| conductivity | >1e+08 S/m | 标记为"超高导电性" |
| length | >1000 μm | 标记为"超长" |
| diameter | >500 nm | 标记为"超粗" |

**异常率预期:** <5%

---

### Level 4: 交叉验证

**目标:** 多来源数据一致性

| 检查项 | 方法 | 处理 |
|--------|------|------|
| 同文献多数据点 | 比较一致性 | 取平均值或标记 |
| 同团队多文献 | 比较趋势 | 识别异常 |
| 同类型 CNT | 统计分布 | 识别离群值 |

**通过率目标:** >85%

---

## 🔧 质量检查脚本

```python
def quality_check(record, config):
    """数据质量检查"""
    issues = []
    warnings = []
    
    # Level 1: 完整性
    for field in REQUIRED_FIELDS:
        if field not in record or record[field] is None:
            issues.append(f"缺失必填字段：{field}")
    
    # Level 2: 一致性
    if "aspect_ratio" in record and "length" in record and "diameter" in record:
        calculated_ar = record["length"] * 1000 / record["diameter"]  # 转换为相同单位
        if abs(calculated_ar - record["aspect_ratio"]) / calculated_ar > 0.1:
            issues.append(f"长径比计算不一致")
    
    # Level 3: 异常值
    if record.get("aspect_ratio", 0) > config["max_aspect_ratio"]:
        warnings.append(f"长径比异常：{record['aspect_ratio']}")
    
    if record.get("purity", 100) < config["min_purity"]:
        warnings.append(f"纯度低：{record['purity']}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "quality_score": 100 - len(issues)*10 - len(warnings)*5
    }
```

---

## 📊 质量报告模板

```markdown
# CNT 数据质量报告

**检查日期:** YYYY-MM-DD
**总记录数:** XXX
**有效记录:** XXX (XX%)
**无效记录:** XXX (XX%)

---

## 问题分布

| 问题类型 | 数量 | 占比 |
|----------|------|------|
| 缺失必填字段 | XX | XX% |
| 长径比不一致 | XX | XX% |
| 纯度异常 | XX | XX% |
| 导电性异常 | XX | XX% |

---

## 处理建议

1. 手动补充缺失字段 (XX 条)
2. 修正长径比计算 (XX 条)
3. 核实异常值 (XX 条)

---

*Generated:* YYYY-MM-DD HH:MM
```

---

## 📝 质量检查流程

1. **自动检查:** 运行质量检查脚本
2. **问题分类:** 按问题类型分类
3. **手动核实:** 对异常值进行人工核实
4. **修正/排除:** 修正错误或排除无效数据
5. **质量报告:** 生成质量检查报告

---

*Created:* 2026-03-13 18:44  
*Status:* ✅ 数据质量检查流程完成  
*Next:* 执行质量检查测试
