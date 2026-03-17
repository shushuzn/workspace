# 材料知识图谱 - 设计文档

**版本:** v0.1  
**创建时间:** 2026-03-05 13:22  
**目的:** 构建材料科学领域知识图谱

---

## 📊 图谱设计

### 实体类型

| 类型 | 描述 | 示例 |
|------|------|------|
| Material | 材料 | LiCoO2, Graphene |
| Element | 元素 | Li, Co, O, C |
| Property | 性能 | Band Gap, Elastic Modulus |
| Structure | 结构 | FCC, BCC, Perovskite |
| Application | 应用 | Battery, Catalyst |
| Synthesis | 合成方法 | Solid-state Reaction, CVD |

---

### 关系类型

| 关系 | 源实体 | 目标实体 | 示例 |
|------|--------|----------|------|
| contains | Material | Element | LiCoO2 contains Li |
| has_property | Material | Property | Graphene has_property High Conductivity |
| has_structure | Material | Structure | LiCoO2 has_structure Layered |
| used_for | Material | Application | LiCoO2 used_for Battery |
| synthesized_by | Material | Synthesis | Graphene synthesized_by CVD |

---

## 🔧 技术实现

### 1. 材料实体识别

**方法:**
- 规则匹配 (化学式正则表达式)
- NER 模型 (材料名称识别)
- 数据库匹配 (Materials Project ID)

**示例:**
```python
import re

# 化学式匹配
formula_pattern = r'([A-Z][a-z]?\d*)+'
matches = re.findall(formula_pattern, text)
```

### 2. 关系提取

**方法:**
- 依存句法分析
- 预定义模板匹配
- 深度学习模型

**示例模板:**
- "{material} is a {property} material" → has_property
- "{material} is used for {application}" → used_for
- "{material} can be synthesized by {synthesis}" → synthesized_by

### 3. 图谱存储

**方案:**
- Neo4j (图数据库)
- RDF + SPARQL
- 轻量级：JSON + NetworkX

### 4. 可视化与查询

**可视化:**
- D3.js (Web)
- Gephi (桌面)
- PyVis (Python)

**查询接口:**
- REST API
- GraphQL
- SPARQL endpoint

---

## 📈 图谱规模

| 指标 | 目标值 |
|------|--------|
| 材料实体 | 10,000+ |
| 元素实体 | 118 (全部元素) |
| 性能实体 | 100+ |
| 结构实体 | 50+ |
| 应用实体 | 100+ |
| 合成方法 | 100+ |
| 关系总数 | 50,000+ |

---

## 📅 实施计划

| 任务 | 用时 | 日期 |
|------|------|------|
| 材料实体识别 | 2 小时 | 03-20 |
| 性能 - 结构关系图谱 | 3 小时 | 03-20 |
| 合成路径图谱 | 3 小时 | 03-20 |
| 应用 - 材料关联图谱 | 2 小时 | 03-20 |
| 可视化与查询接口 | 2 小时 | 03-20 |
| **总计** | **12 小时** | - |

---

*最后更新：2026-03-05 13:22*
