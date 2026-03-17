# Scientific Rigor - Research Methodology

**Location:** `10-RESEARCH/docs/methodology.md`

**Last Updated:** 2026-03-18 00:50

---

## Core Principles

> "未经严格验证的结论不值得相信"
> "质量 > 数量，物理 > 统计，批判 > 盲从"
> "宁可 R²=0.58 (真实)，不要 R²=0.799 (幻觉)"

---

## Lessons from CNT Conductivity Prediction (Day 2)

**Source:** CNT 导电性预测研究 Day 2 - 批判者 v2.0 严格审查

### 1. 质量 > 数量

**Finding:**
- 194 高质量样本 > 511 混合样本
- R²=0.58 (真实) > R²=0.799 (幻觉)

**Lesson:** 不要盲目追求数据量

**Action:**
- Prioritize data quality over quantity
- Remove outliers and low-quality samples
- Document data cleaning decisions

---

### 2. 验证 > 自信

**Finding:**
- Unvalidated R² is meaningless
- Confidence intervals are essential

**Lesson:** 没有验证的 R²毫无意义

**Requirements:**
- ✅ Nested cross-validation (gold standard)
- ✅ 95% confidence intervals for all metrics
- ✅ Truly independent external validation set

---

### 3. 物理 > 统计

**Finding:**
- 14 statistical features → 3 physical features
- VIF must be <5 (avoid multicollinearity)

**Lesson:** 黑箱模型不可信

**Requirements:**
- ✅ Each feature must have physical meaning
- ✅ VIF < 5 for all features
- ✅ Avoid purely statistical correlations

---

### 4. 批判 > 盲从

**Finding:**
- Critic v2.0 score improved from 35 to 88
- Every critique is an opportunity to improve

**Lesson:** 批判是科研的守护者

**Practice:**
- Welcome harsh criticism
- Never be defensive about feedback
- Use critiques to strengthen work

---

### 5. 透明 > 完美

**Finding:**
- Reproducibility matters more than perfect results

**Lesson:** 可复现性比完美结果重要

**Requirements:**
- ✅ Public code and data
- ✅ Report negative results
- ✅ Document limitations
- ✅ Third-party reproduction

---

### 6. 功效分析 (Power Analysis)

**Finding:**
- Sample size must achieve statistical power ≥ 0.8
- 194 samples for 3 features: Power = 1.0 ✓

**Lesson:** 样本量不足的研究是浪费

**Practice:**
- Calculate required sample size before starting
- Report statistical power in all studies
- Never underpower your study

---

## Critic v5.0 Embedded Checklist

### Before Starting (Design Review)

```markdown
### 批判者设计审查
- [ ] 研究问题有科学意义 (≥3 篇文献支持)
- [ ] 样本量先验功效分析 (Power≥0.95)
- [ ] 特征文献依据 (每个≥3 篇)
- [ ] VIF 预分析 (<3)
- [ ] 验证方案 (5×5×5 嵌套 CV+10000Bootstrap)
- [ ] 外部验证方案 (真正独立≥50 样本)
**审查结果:** 通过/不通过 (不通过不允许开始)
```

### During Execution (Monitoring)

```markdown
### 批判者中期检查
- [ ] 数据质量 (缺失值<2%, VIF<3)
- [ ] 进度正常 (每 30% 检查一次)
- [ ] 无致命问题
**检查结果:** 继续/暂停调整
```

### After Completion (Final Review)

```markdown
### 批判者最终审查
- [ ] 致命问题 0 个
- [ ] 严重问题≤2 个
- [ ] 一般问题≤10 个
- [ ] 置信区间报告 (所有指标 95% CI)
- [ ] 效应量报告 (Cohen's f²)
- [ ] 统计功效 (Power≥0.95)
- [ ] VIF 检验 (全部<3)
- [ ] 外部验证 (真正独立≥50 样本)
- [ ] SHAP 分析 (p<0.001+95%CI)
- [ ] GitHub 公开 + 第三方复现
**最终评分:** ≥95 分通过/<95 分返工
```

---

## Validation Standards

### Cross-Validation

**Gold Standard:** 5×5×5 Nested CV
- 5 outer folds
- 5 inner folds
- 5 repetitions
- Total: 125 model evaluations

### Bootstrap

**Standard:** 10,000 Bootstrap samples
- 95% confidence intervals
- Bias-corrected and accelerated (BCa)

### External Validation

**Requirements:**
- ≥50 truly independent samples
- Different source/time/location
- No overlap with training data

---

## Reporting Standards

### Must Report

1. **Performance Metrics**
   - R² with 95% CI
   - RMSE with 95% CI
   - MAE with 95% CI

2. **Model Diagnostics**
   - VIF for all features
   - Residual analysis
   - Homoscedasticity check

3. **Statistical Tests**
   - Statistical power (≥0.95)
   - Effect size (Cohen's f²)
   - P-values with corrections

4. **Interpretability**
   - SHAP values with 95% CI
   - Feature importance ranking
   - Physical interpretation

5. **Reproducibility**
   - GitHub repository link
   - Data availability statement
   - Code version tag

---

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Data leakage | Strict train/test separation |
| Overfitting | Nested CV, regularization |
| P-hacking | Pre-register analysis plan |
| Small sample | Power analysis before start |
| Black box | Use interpretable models + SHAP |
| No CI | Always report confidence intervals |
| Cherry picking | Report all results, including negatives |

---

## Tools

**Statistical Analysis:**
- Python: `scikit-learn`, `statsmodels`, `scipy`
- R: `caret`, `randomForest`, `shap`

**Validation:**
- `40-TOOLS/scripts/memory_quality_scorer.py` (adapt for research)
- Custom validation scripts

**Reporting:**
- Jupyter notebooks
- R Markdown
- GitHub repositories

---

**Source:** CNT 导电性预测研究 Day 2 (2026-03-11) - Critic v2.0 review
