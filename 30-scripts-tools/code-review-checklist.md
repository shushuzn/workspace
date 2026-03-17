# Code Review Checklist / 代码审查清单

**Created:** 2026-03-13 (Critic v5.0 fix-010)  
**Purpose:** Standardized code review checklist for quality assurance  
**Version:** v1.0

---

## 📋 Pre-Review / 审查前

- [ ] Code compiles without errors
- [ ] All tests pass locally
- [ ] No sensitive data (API keys, passwords) committed
- [ ] Git commit message follows convention
- [ ] Branch is up to date with main

---

## 🔍 Code Quality / 代码质量

### Readability / 可读性
- [ ] Clear and descriptive variable/function names
- [ ] Consistent indentation and formatting
- [ ] Appropriate comments (why, not what)
- [ ] No commented-out code
- [ ] Functions are small and focused (< 50 lines)

### Structure / 结构
- [ ] Single responsibility principle followed
- [ ] DRY (Don't Repeat Yourself)
- [ ] Proper error handling
- [ ] No deep nesting (< 3 levels)
- [ ] Logical file organization

---

## 🧪 Testing / 测试

- [ ] Unit tests added for new functionality
- [ ] Test coverage > 80%
- [ ] Edge cases covered
- [ ] Integration tests pass
- [ ] No hardcoded test data

---

## 🔒 Security / 安全

- [ ] No SQL injection vulnerabilities
- [ ] Input validation implemented
- [ ] Authentication/authorization checked
- [ ] No exposed secrets in logs
- [ ] Dependencies are up to date

---

## 📊 Performance / 性能

- [ ] No obvious performance bottlenecks
- [ ] Database queries optimized
- [ ] Caching used appropriately
- [ ] No memory leaks
- [ ] Async operations where appropriate

---

## 📝 Documentation / 文档

- [ ] README updated if needed
- [ ] API documentation complete
- [ ] Inline comments for complex logic
- [ ] CHANGELOG updated
- [ ] Usage examples provided

---

## ✅ Critic v5.0 Specific / 批判者 v5.0 专项

### Research Code / 研究代码
- [ ] Sample size justified (Power analysis)
- [ ] VIF < 3 for all features
- [ ] Bootstrap stability checked (10000+ iterations)
- [ ] External validation performed
- [ ] 95% CI reported for all metrics
- [ ] Effect size calculated
- [ ] GitHub repository public
- [ ] Reproducibility verified

### Data Quality / 数据质量
- [ ] Missing values < 2%
- [ ] Outliers handled
- [ ] Data distribution checked
- [ ] No data leakage
- [ ] Train/test split appropriate

---

## 📈 Scoring / 评分

| Category | Score (0-10) | Weight | Weighted |
|----------|--------------|--------|----------|
| Code Quality | /10 | 25% | |
| Testing | /10 | 25% | |
| Security | /10 | 20% | |
| Performance | /10 | 15% | |
| Documentation | /10 | 15% | |
| **Total** | | **100%** | **/10** |

**Pass Threshold:** ≥ 8/10  
**Critic v5.0 Threshold:** ≥ 9.5/10

---

## 📝 Review Comments / 审查意见

### Critical Issues (Must Fix) / 致命问题
1. 
2. 
3. 

### Major Issues (Should Fix) / 严重问题
1. 
2. 
3. 

### Minor Issues (Nice to Fix) / 一般问题
1. 
2. 
3. 

### Positive Feedback / 正面反馈
1. ✅
2. ✅
3. ✅

---

## ✅ Final Decision / 最终决定

- [ ] **Approve** - Ready to merge
- [ ] **Approve with Minor Changes** - Can merge after small fixes
- [ ] **Request Changes** - Must fix before merge
- [ ] **Reject** - Needs significant rework

**Reviewer:** _______________  
**Date:** YYYY-MM-DD  
**Signature:** _______________

---

*Template Version:* v1.0  
*Last Updated:* 2026-03-13  
*Usage:* Complete for every code review
