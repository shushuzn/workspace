# LIG 稳定性预测模型训练框架

**创建日期:** 2026-03-08  
**状态:** 框架创建 (待数据填充)  
**目标:** 基于工艺参数预测 LIG 长期稳定性

---

## 📊 当前数据状态

### 已收集数据
- **文献数量:** 37 篇 (PubMed 搜索)
- **数据类型:** 定性描述为主
- **关键发现:** 
  - 稳定性是主要挑战 (综述确认)
  - 批次一致性是问题
  - 复合材料/表面改性/结构优化是改进策略

### 数据缺口
- ❌ 具体稳定性数值 (阻抗变化%、灵敏度保持率%)
- ❌ 工艺参数 (激光功率、速度、次数)
- ❌ 测试条件 (时间、温度、介质)
- ❌ 样本量 (n 值)

---

## 🔧 模型训练框架

### 1. 数据结构定义

```python
# 数据模型
@dataclass
class LIGStabilityData:
    # 论文元数据
    paper_id: str  # PMID/arXiv ID
    publication_year: int
    journal: str
    
    # 工艺参数 (特征)
    laser_type: str  # CO2/UV/fiber
    laser_power: float  # W
    scan_speed: float  # mm/s
    scan_passes: int  # 次数
    precursor: str  # PI/Kapton/其他
    
    # 后处理 (特征)
    has_coating: bool  # 是否有涂层
    coating_type: str  # PDMS/PU/其他
    has_composite: bool  # 是否复合材料
    composite_material: str  # Au/Pt/CuO/其他
    
    # 测试条件 (特征)
    test_duration: int  # 天
    test_condition: str  # PBS/air/sweat/blood
    test_temperature: float  # °C
    
    # 稳定性结果 (标签)
    initial_value: float  # 初始值 (阻抗/灵敏度)
    final_value: float  # 最终值
    change_percent: float  # 变化率% (标签)
    n_samples: int  # 样本量
    
    # 稳定性评级 (衍生标签)
    stability_grade: str  # A/B/C/D (基于变化率)
```

### 2. 稳定性评级标准

| 等级 | 变化率 | 描述 | 应用 |
|------|--------|------|------|
| **A** | <5% | 优异 | 植入式设备 |
| **B** | 5-15% | 良好 | 可穿戴设备 |
| **C** | 15-30% | 可接受 | 一次性传感器 |
| **D** | >30% | 不可接受 | 需要改进 |

---

## 🤖 ML 模型选择

### 模型 1: 回归模型 (预测变化率%)

```python
# 特征
X = [
    laser_power, scan_speed, scan_passes,
    has_coating, has_composite,
    test_duration, test_temperature
]

# 标签
y = change_percent

# 模型选择
- Random Forest Regressor (可解释性好)
- XGBoost Regressor (精度高)
- Neural Network (数据量>1000 时)
```

### 模型 2: 分类模型 (预测稳定性等级)

```python
# 特征
X = 同上

# 标签
y = stability_grade  # A/B/C/D

# 模型选择
- Random Forest Classifier
- Gradient Boosting Classifier
- Logistic Regression (基线)
```

### 模型 3: 生存分析 (预测失效时间)

```python
# 特征
X = 工艺参数 + 测试条件

# 标签
- time_to_failure: 失效时间 (天)
- event: 是否失效 (1/0)

# 模型选择
- Cox Proportional Hazards
- Random Survival Forest
```

---

## 📈 特征工程

### 数值特征
```python
numerical_features = [
    'laser_power',
    'scan_speed', 
    'scan_passes',
    'test_duration',
    'test_temperature'
]

# 衍生特征
- energy_density = laser_power / scan_speed  # 能量密度 (J/mm)
- total_exposure = laser_power * scan_passes  # 总曝光量
```

### 类别特征
```python
categorical_features = [
    'laser_type',  # CO2/UV/fiber
    'precursor',   # PI/Kapton/其他
    'coating_type',  # PDMS/PU/无
    'composite_material',  # Au/Pt/CuO/无
    'test_condition'  # PBS/air/sweat/blood
]

# 编码方式
- One-Hot Encoding (低基数)
- Target Encoding (高基数)
```

---

## 📝 数据收集计划

### 阶段 1: 手动提取 (本周)

**目标:** 5-10 篇关键论文

| 论文 | PMID | 状态 |
|------|------|------|
| Biomater Adv. 2026 | 41072172 | ❌ 待提取 |
| Nanomaterials 2025 | 40711189 | ❌ 待提取 |
| Biosens Bioelectron. 2025 | 40513290 | ❌ 待提取 |
| Anal Chim Acta 2025 | 40669990 | ❌ 待提取 |
| Biosensors 2025 | 40558466 | ❌ 待提取 |

**工具:** 
- PDF 解析 (pdfplumber/PyMuPDF)
- 手动标注 (Excel/Google Sheets)

### 阶段 2: 半自动提取 (本月)

**目标:** 30-50 篇论文

**工具:**
- NLP 信息提取 (spaCy/sciSpaCy)
- 表格解析 (camelot/tabula-py)
- LLM 辅助提取 (GPT-4/Claude)

**提取模板:**
```
From PDF:
- Laser parameters: ___ W, ___ mm/s, ___ passes
- Stability test: ___ days in ___
- Initial: ___, Final: ___, Change: ___%
```

### 阶段 3: 数据增强 (下月)

**方法:**
- 联系作者请求原始数据
- 扩展到 Web of Science/Scopus
- 包含会议论文/学位论文

**目标:** 100+ 样本

---

## 🧪 模型验证策略

### 交叉验证
```python
from sklearn.model_selection import cross_val_score

# 5 折交叉验证
scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_absolute_error')
print(f"MAE: {-scores.mean():.2f} (+/- {scores.std():.2f})")
```

### 时间序列分割
```python
# 按发表年份分割 (模拟时间验证)
train = data[data['publication_year'] < 2025]
test = data[data['publication_year'] >= 2025]

# 训练 + 测试
model.fit(train[features], train['change_percent'])
pred = model.predict(test[features])
```

### 外部验证
```python
# 保留 20% 数据作为独立测试集
from sklearn.model_selection import train_test_split

train_data, external_test = train_test_split(data, test_size=0.2, random_state=42)
```

---

## 📊 模型解释

### 特征重要性
```python
import matplotlib.pyplot as plt

# Random Forest 特征重要性
importances = model.feature_importances_
features = feature_names

plt.barh(features, importances)
plt.xlabel('Importance')
plt.title('Feature Importance for LIG Stability')
plt.show()
```

### SHAP 分析
```python
import shap

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# 摘要图
shap.summary_plot(shap_values, X_test)

# 依赖图
shap.dependence_plot('laser_power', shap_values, X_test)
```

---

## 🎯 优化建议生成

### 基于模型的优化

```python
def generate_optimization_recommendations(current_params, target_stability='A'):
    """
    基于当前工艺参数，生成优化建议
    """
    # 预测当前稳定性
    current_pred = model.predict([current_params])[0]
    
    # 找到训练集中稳定性等级为 A 的样本
    grade_a_samples = data[data['stability_grade'] == 'A']
    
    # 找出差异最大的特征
    recommendations = []
    for feature in feature_names:
        current_val = current_params[feature]
        grade_a_mean = grade_a_samples[feature].mean()
        
        if abs(current_val - grade_a_mean) > threshold:
            recommendations.append({
                'feature': feature,
                'current': current_val,
                'recommended': grade_a_mean,
                'impact': calculate_impact(feature, current_val, grade_a_mean)
            })
    
    return sorted(recommendations, key=lambda x: x['impact'], reverse=True)
```

### 示例输出

```
当前工艺：
- 激光功率：8W
- 扫描速度：100 mm/s
- 无涂层
- 预测稳定性：C 级 (20% 变化)

优化建议：
1. 添加 PDMS 涂层 → 预计改善至 B 级 (-10%)
2. 降低激光功率至 6W → 预计改善至 B 级 (-5%)
3. 扫描次数从 1 次增至 3 次 → 预计改善至 B 级 (-3%)
```

---

## 📁 文件结构

```
lig-stability-ml/
├── data/
│   ├── raw/                  # 原始数据 (PDFs)
│   ├── processed/            # 处理后数据 (CSV/JSON)
│   └── lig_stability.csv     # 主数据集
├── scripts/
│   ├── collect_data.py       # 数据收集脚本
│   ├── extract_features.py   # 特征提取
│   ├── train_model.py        # 模型训练
│   └── predict.py            # 预测脚本
├── models/
│   ├── rf_regressor.pkl      # Random Forest 回归
│   ├── rf_classifier.pkl     # Random Forest 分类
│   └── survival_model.pkl    # 生存分析模型
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_model_training.ipynb
│   └── 03_optimization.ipynb
└── reports/
    ├── model_performance.md
    └── optimization_recommendations.md
```

---

## 📈 项目里程碑

| 阶段 | 目标 | 时间 | 状态 |
|------|------|------|------|
| **阶段 1** | 数据收集 (5-10 篇) | 1 周 | 🔴 未开始 |
| **阶段 2** | 数据收集 (30-50 篇) | 1 月 | 🔴 未开始 |
| **阶段 3** | 模型训练 + 验证 | 2 月 | 🔴 未开始 |
| **阶段 4** | 优化建议生成 | 3 月 | 🔴 未开始 |
| **阶段 5** | 实验验证 | 6 月 | 🔴 未开始 |

---

## 🚀 立即行动

### 1. 创建数据收集模板

```bash
# 创建 Excel 模板
cd lig-stability-ml/data/
python create_data_template.py
```

### 2. 下载关键论文 PDF

```bash
# 使用 sci-hub 或机构访问
python download_papers.py --pmids 41072172,40711189,40513290,40669990,40558466
```

### 3. 手动提取第一批数据

```bash
# 打开 Excel 模板，手动填写
# 目标：本周完成 5 篇
```

---

## 📚 参考资源

### 数据集
- [NIST LIG Database](https://www.nist.gov/) (待创建)
- [Graphene Flagship Database](https://graphene-flagship.eu/)

### 工具
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF 表格提取
- [sciSpaCy](https://scispacy.org/) - 生物医学 NLP
- [AutoML](https://github.com/microsoft/FLAML) - 自动模型选择

### 文献
- Massaglia G, Quaglio M. Nanomaterials (Basel). 2025. PMID: 40711189
- Khadeeja Thanha KP, et al. Biomater Adv. 2026. PMID: 41072172

---

**创建者:** Claw (AI Research OS)  
**创建日期:** 2026-03-08  
**状态:** 框架完成，等待数据填充  
**下次更新:** 完成 5-10 篇论文数据提取后
