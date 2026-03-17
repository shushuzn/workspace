# CNT 特征工程方案

**创建日期:** 2026-03-13 18:50  
**版本:** v1.0

---

## 🎯 特征工程目标

| 目标 | 说明 |
|------|------|
| 特征数量 | 3-5 个核心特征 |
| VIF | <3 (严格筛选) |
| 物理意义 | 每个特征必须有明确物理意义 |
| 相关性 | 与导电性显著相关 (p<0.05) |

---

## 📊 候选特征池

### 1. CNT 本征特性

| 特征 | 符号 | 单位 | 物理意义 | 优先级 |
|------|------|------|----------|--------|
| 长度 | L | μm | CNT 长度 | 🔴 高 |
| 直径 | D | nm | CNT 直径 | 🔴 高 |
| 长径比 | AR | - | L/D | 🔴 高 |
| 手性 | Chirality | - | 金属性/半导体性 | 🔴 高 |
| 纯度 | P | % | CNT 纯度 | 🔴 高 |
| 层数 | N | - | 单层/多层 | 🟡 中 |

### 2. 处理工艺特征

| 特征 | 符号 | 单位 | 物理意义 | 优先级 |
|------|------|------|----------|--------|
| 分散方法 | DispMethod | - | 分散方式 | 🟡 中 |
| 分散剂浓度 | C_disp | mg/mL | 分散剂用量 | 🟡 中 |
| 处理温度 | T | °C | 处理温度 | 🟢 低 |
| 处理时间 | t | min | 处理时间 | 🟢 低 |
| 超声功率 | P_us | W | 超声功率 | 🟡 中 |

### 3. 衍生特征

| 特征 | 公式 | 物理意义 | 优先级 |
|------|------|----------|--------|
| 体积分数 | φ | CNT 体积占比 | 🔴 高 |
| 渗流阈值 | φc | 渗流理论参数 | 🔴 高 |
| 比表面积 | SSA | m²/g | 表面活性 | 🟡 中 |

---

## 🔍 特征选择流程

### 步骤 1: 单变量分析

**方法:**
- 相关性分析 (Pearson/Spearman)
- 单变量回归 (R²)

**筛选标准:**
- |r| > 0.3
- p < 0.05

### 步骤 2: 多重共线性检查

**方法:**
- VIF (方差膨胀因子)

**筛选标准:**
- VIF < 3 (严格)
- VIF < 5 (宽松)

### 步骤 3: 特征重要性

**方法:**
- 随机森林特征重要性
- XGBoost 特征重要性

**筛选标准:**
- 重要性 > 0.05

### 步骤 4: 物理意义验证

**检查项:**
- 特征是否有明确物理意义
- 是否符合已知理论
- 是否与文献一致

---

## 📊 推荐特征组合

### 组合 A (3 特征 - 推荐)

| 特征 | 符号 | VIF 预期 | 物理意义 |
|------|------|----------|----------|
| 长径比 | AR | <2 | CNT 几何特性 |
| 纯度 | P | <2 | CNT 质量 |
| 体积分数 | φ | <2 | 复合材料配比 |

**预期性能:** R² ~ 0.70-0.75

### 组合 B (5 特征 - 扩展)

| 特征 | 符号 | VIF 预期 | 物理意义 |
|------|------|----------|----------|
| 长径比 | AR | <2 | CNT 几何特性 |
| 纯度 | P | <2 | CNT 质量 |
| 体积分数 | φ | <2 | 复合材料配比 |
| 分散剂浓度 | C_disp | <3 | 分散效果 |
| 超声功率 | P_us | <3 | 处理强度 |

**预期性能:** R² ~ 0.75-0.80

---

## 🔧 特征工程脚本

```python
def create_features(df):
    """创建特征"""
    
    # 衍生特征
    df['aspect_ratio'] = df['length'] * 1000 / df['diameter']  # 转换为相同单位
    df['volume_fraction'] = calculate_volume_fraction(df)
    
    # 对数转换 (如果数据偏态)
    df['log_conductivity'] = np.log10(df['conductivity'])
    
    return df

def check_vif(df, features):
    """检查 VIF"""
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    
    vif_data = pd.DataFrame()
    vif_data["Feature"] = features
    vif_data["VIF"] = [variance_inflation_factor(df[features].values, i) 
                       for i in range(len(features))]
    
    return vif_data

def select_features(df, target, method='rf'):
    """特征选择"""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.feature_selection import SelectFromModel
    
    X = df[feature_candidates]
    y = df[target]
    
    if method == 'rf':
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        selector = SelectFromModel(model, threshold='mean')
        selector.fit(X, y)
        selected_features = X.columns[selector.get_support()].tolist()
    
    return selected_features
```

---

## ⚠️ 注意事项

1. **单位统一:** 确保所有特征单位一致
2. **缺失值处理:** 缺失率>50% 的特征考虑删除
3. **异常值处理:** 3σ原则或 IQR 方法
4. **特征缩放:** 树模型不需要，线性模型需要

---

*Created:* 2026-03-13 18:50  
*Status:* ✅ 特征工程方案完成  
*Next:* 模型建立方案
