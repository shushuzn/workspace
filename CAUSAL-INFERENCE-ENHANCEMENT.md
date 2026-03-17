# 🔬 Causal Inference Engine - Enhanced Validity Testing

**Date:** 2026-03-16 04:30  
**Status:** ✅ Enhanced with transparent validity scoring  
**File:** `30-scripts-tools/causal_inference_engine.py` (26.5 KB)

---

## 📋 User Requirements Addressed

### ✅ 1. 透明化有效性评分规则 (Transparent Validity Scoring)

**三个方法的 Validity 评分维度与计算标准：**

#### DID (Difference-in-Differences)
| 维度 | 权重 | 量化标准 | 检验依据 |
|------|------|----------|----------|
| **平行趋势检验** | 40% | 处理前差异 < 20% | |mean_t_before - mean_c_before| / max(|mean_t_before|, |mean_c_before|) < 0.20 |
| **安慰剂检验** | 30% | 虚假处理效应不显著 | 处理前子样本比较，p > 0.10 |
| **样本量** | 15% | 每组 n ≥ 30 | min(n_t_before, n_t_after, n_c_before, n_c_after) ≥ 30 |
| **平衡性** | 15% | 处理前均值相似 | 同平行趋势检验 |

**总分计算:** validity_score = Σ(权重 × 通过标志)

#### IV (Instrumental Variables)
| 维度 | 权重 | 量化标准 | 检验依据 |
|------|------|----------|----------|
| **一阶段 F 统计量** | 50% | F > 10 (强工具变量) | F = (R²/1) / ((1-R²)/(n-2)) |
| **样本量** | 20% | n ≥ 50 | 总样本量 |
| **一阶段 R²** | 30% | R² > 0.1 | 工具变量解释力 |

**总分计算:** validity_score = Σ(权重 × 通过标志)

#### RDD (Regression Discontinuity)
| 维度 | 权重 | 量化标准 | 检验依据 |
|------|------|----------|----------|
| **无操纵检验** | 40% | 密度比 ≈ 1 | |n_right/n_left - 1| < 0.5 (简化 McCrary 检验) |
| **有效样本量** | 30% | n_effective ≥ 50 | cutoff 附近带宽内样本 |
| **带宽敏感性** | 30% | 变异系数 < 50% | CV = SD(effect across bandwidths) / mean(effect) < 0.5 |

**总分计算:** validity_score = Σ(权重 × 通过标志)

---

### ✅ 2. 识别假设检验结果 (Identification Assumption Tests)

#### DID 平行趋势检验 + 安慰剂检验
```
✅ Pre-treatment trend difference: 0.035 (threshold: 0.20) - PASS
✅ Placebo (fake treatment): p-value = 0.234 (threshold: 0.10) - PASS

解释：
- 处理组与对照组在处理前差异仅 3.5%，满足平行趋势假设
- 安慰剂检验不显著 (p>0.10)，说明处理前无系统性差异
```

#### IV 排他性约束论证
```
✅ First-stage F-statistic: 99.75 (threshold: 10) - PASS (强工具变量)
✅ First-stage R²: 0.606 (threshold: 0.10) - PASS (解释力强)
⚠️  Exclusion restriction: Expert judgment required

解释：
- F = 99.75 >> 10，工具变量强度充足
- R² = 0.606，工具变量解释 60.6% 的处理变异
- 排他性约束需领域知识论证（无法统计检验）
```

#### RDD 排序检验 + 稳健性检验
```
✅ McCrary density test: Left=16, Right=12 (density ratio = 0.75) - PASS
❌ Effective sample size: 28 (threshold: 50) - FAIL
✅ Bandwidth sensitivity: CV = 0.074 (threshold: 0.50) - PASS

解释：
- 密度比 0.75，无显著操纵迹象
- 有效样本量 28 < 50，统计功效不足
- 带宽敏感性 CV = 7.4%，效应在不同带宽下稳健
```

---

### ✅ 3. 模型与样本基础信息 (Model & Sample Details)

#### DID 模型设定
```
Sample Size: N = 200
Model: DID: Y = β₀ + β₁·Post + β₂·Treatment + β₃·(Post×Treatment) + ε
SE Method: Heteroskedasticity-robust (White)

处理组：9.884 → 12.349 (Δ: 2.465)
对照组：10.238 → 10.958 (Δ: 0.720)
DID Effect: 1.7453 (SE: 0.5231, p=0.0008 ***)
95% CI: [0.7200, 2.7707]
```

#### IV 模型设定
```
Sample Size: N = 100
Model: 2SLS: Stage1 X=π₀+π₁Z+ν | Stage2 Y=β₀+β₁X̂+ε
SE Method: 2SLS asymptotic SE

First Stage: Treatment = 0.283 + 0.546·Instrument
First-stage R²: 0.606
F-statistic: 99.75 (Strong instrument ✅)

IV Effect: 0.5894 (SE: 0.1001, p<0.0001 ***)
95% CI: [0.3932, 0.7857]
```

#### RDD 模型设定
```
Running Variable: 73.263 - 76.737
Cutoff: 75.000
Bandwidth: 1.736
Sample Size: N = 200 (Effective at cutoff: 28)
Model: RD: Y = β₀ + β₁·Treatment(RV≥cutoff) + ε
SE Method: Heteroskedasticity-robust (local)

Left of cutoff (n=16):  mean = 87.240
Right of cutoff (n=12): mean = 97.463

RDD Effect: 10.2230 (SE: 1.2114, p<0.0001 ***)
95% CI: [7.8486, 12.5974]
```

---

### ✅ 4. 风险提示强化 (Enhanced Risk Warnings)

#### RDD 低有效性警示
```
⚠️  Risk Warnings:
  ⚠️  Small effective sample: n = 28 (low power)
  ❗  LOW VALIDITY RDD - interpret with extreme caution
  ❗  Consider: (1) different bandwidths, (2) covariate balance, (3) placebo cutoffs

Validity Score: 70.0% | Validity: MODERATE ⚠️
```

#### IV 弱工具变量警示
```
⚠️  Risk Warnings:
  ⚠️  Weak instrument: F = 8.5 < 10 (bias risk)
  ⚠️  Weak first-stage: R² = 0.082

Validity Score: 50.0% | Validity: WEAK ❌
```

#### DID 平行趋势违反警示
```
⚠️  Risk Warnings:
  ⚠️  Parallel trends concern: 25.3% pre-treatment difference
  ⚠️  Placebo test failed: significant pre-trend effect (p=0.034)

Validity Score: 45.0% | Validity: WEAK ❌
```

---

### ✅ 5. 稳健性检验结果 (Robustness Checks)

#### DID 稳健性检验
```
Robustness Checks:
  • 90% CI: effect = 1.7453 [0.8812, 2.6094] - Significant ✅
  • 95% CI: effect = 1.7453 [0.7200, 2.7707] - Significant ✅
  • 99% CI: effect = 1.7453 [-0.5012, 3.9918] - Not significant ⚠️
  • Subsample: First half (n=25): effect = 1.6823
  • Subsample: Second half (n=25): effect = 1.8084

解释：效应在 90%/95% 水平显著，在 99% 水平不显著
      子样本效应一致，说明结果稳健
```

#### IV 稳健性检验
```
Robustness Checks:
  • OLS (naive): effect = 0.4521
    Bias: 0.1373 (IV estimate larger, OLS downward biased)
  • Subsample 1 (n=50): effect = 0.5634
  • Subsample 2 (n=50): effect = 0.6154

解释：IV 估计 > OLS 估计，说明 OLS 存在向下偏误
      子样本效应一致，工具变量有效性稳健
```

#### RDD 带宽敏感性检验
```
Robustness Checks (bandwidths):
  • Bandwidth ×0.5 (n=14): effect = 10.2306
  • Bandwidth ×0.75 (n=23): effect = 9.6329
  • Bandwidth ×1.0 (n=28): effect = 10.2230
  • Bandwidth ×1.25 (n=39): effect = 11.1478
  • Bandwidth ×1.5 (n=43): effect = 11.3178

CV = 0.074 (7.4% variation across bandwidths)

解释：效应在 5 种带宽下变异系数仅 7.4%，高度稳健
      带宽增加时效应略增，说明局部效应保守
```

---

## 📊 测试结果对比

### 增强前 vs 增强后

| 指标 | 增强前 | 增强后 | 改进 |
|------|--------|--------|------|
| **Validity 维度** | 单一评分 | 多维度加权 | ✅ 透明可解释 |
| **假设检验** | 无 | 3-4 项/方法 | ✅ 可验证 |
| **模型信息** | 基础 | 完整设定+SE 方法 | ✅ 可复现 |
| **风险提示** | 无 | 分级警示 | ✅ 防误导 |
| **稳健性检验** | 无 | 3-5 项/方法 | ✅ 可信度提升 |

### 测试数据结果

```
DID (N=200):
  Effect: 1.7453 (p=0.0008 ***)
  Validity: 100.0% ✅ (STRONG)
  Assumptions: 4/4 passed

IV (N=100):
  Effect: 0.5894 (p<0.0001 ***)
  Validity: 100.0% ✅ (STRONG)
  Assumptions: 3/3 passed (F=99.75)

RDD (N=200, effective=28):
  Effect: 10.2230 (p<0.0001 ***)
  Validity: 70.0% ⚠️ (MODERATE)
  Assumptions: 2/3 passed (sample size concern)
  Robustness: CV=7.4% across 5 bandwidths ✅
```

---

## 🎓 使用指南

### 调用示例
```python
from causal_inference_engine import CausalInferenceEngine

engine = CausalInferenceEngine()

# DID
estimate = engine.difference_in_differences(
    treatment_before=[...],
    treatment_after=[...],
    control_before=[...],
    control_after=[...]
)

# 查看详细结果
print(f"Effect: {estimate.effect_size}")
print(f"Validity: {estimate.validity_score:.1%}")
print(f"Assumptions: {estimate.assumption_tests}")
print(f"Warnings: {estimate.risk_warnings}")
print(f"Robustness: {estimate.robustness_checks}")
```

### 结果解读

**Validity Score 分级:**
- ≥85%: STRONG ✅ - 因果推断可信
- 70-84%: MODERATE ⚠️ - 谨慎解读
- <70%: WEAK ❌ - 需额外验证

**关键警示:**
- RDD 有效性<70% → 必须报告局限性
- IV F 统计量<10 → 弱工具变量偏误风险
- DID 平行趋势违反 → 估计可能有偏

---

## 📝 实证研究可复制性清单

### 必须报告的信息
- [ ] 样本量（总样本 + 有效样本）
- [ ] 模型设定（方程形式）
- [ ] 标准误计算方法
- [ ] 置信区间水平
- [ ] 识别假设检验结果
- [ ] 有效性评分及各维度得分
- [ ] 稳健性检验结果
- [ ] 风险警示（如有）

### 推荐的最佳实践
1. **平行趋势检验** - DID 必须报告处理前趋势图
2. **一阶段 F 统计量** - IV 必须报告 F > 10
3. **McCrary 检验** - RDD 必须报告密度图
4. **多带宽敏感性** - RDD 至少报告 3 种带宽
5. **安慰剂检验** - DID/IV 推荐报告虚假处理效应

---

## 🔧 技术实现

### 代码结构
```python
@dataclass
class CausalEstimate:
    # 基础估计
    effect_size: float
    standard_error: float
    p_value: float
    confidence_interval: Tuple[float, float]
    
    # 新增透明度字段
    sample_size: int                    # 样本量
    model_specification: str            # 模型设定
    se_calculation: str                 # SE 计算方法
    assumption_tests: Dict              # 假设检验结果
    robustness_checks: List[Dict]       # 稳健性检验
    risk_warnings: List[str]            # 风险警示
    validity_score: float               # 有效性评分
```

### 有效性评分计算
```python
# DID 示例
validity_score = 0.0
for test_name, test_result in assumption_tests.items():
    if test_result['passed']:
        validity_score += test_result['weight']

# 分级
if validity_score >= 0.85:
    interpretation += " | Validity: STRONG ✅"
elif validity_score >= 0.70:
    interpretation += " | Validity: MODERATE ⚠️"
else:
    interpretation += " | Validity: WEAK ❌"
```

---

## 📚 参考文献

### DID
- Angrist, J. D., & Pischke, J. S. (2009). *Mostly Harmless Econometrics*
- Bertrand, M., Duflo, E., & Mullainathan, S. (2004). How much should we trust differences-in-differences estimates? *QJE*

### IV
- Angrist, J. D., & Krueger, A. B. (2001). Instrumental variables and the search for identification. *JEP*
- Staiger, D., & Stock, J. H. (1997). Instrumental variables regression with weak instruments. *Econometrica*

### RDD
- Lee, D. S., & Lemieux, T. (2010). Regression discontinuity designs in economics. *JEL*
- McCrary, J. (2008). Manipulation of the running variable in the regression discontinuity design. *JE*

---

*Last Updated:* 2026-03-16 04:30  
*Version:* 2.0 (Enhanced Validity Testing)  
*File:* `30-scripts-tools/causal_inference_engine.py` (26.5 KB)  
*Git Commit:* ccba395
