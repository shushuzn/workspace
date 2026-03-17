# M-Note: LIG 知识图谱 v2 - 扩展与自动推理

**创建日期:** 2026-03-11  
**类型:** 知识图谱 + 推理引擎  
**领域:** 激光诱导石墨烯 (LIG)  
**版本:** v2.0  
**置信度:** 0.90

---

## 📊 图谱统计

| 维度 | v1 (之前) | v2 (当前) | 提升 |
|------|----------|----------|------|
| **样本数** | 31 论文 | 200 样本 | +545% |
| **实体数** | 19 实体 | 26 实体 | +37% |
| **关系数** | 18 关系 | 360 关系 | +1900% |
| **推理规则** | 0 | 4 条 | 新增 |
| **研究机会** | 10 个 | 6 个 (1 高优) | 聚焦 |

---

## 🔍 实体分类

### 材料实体 (6 个)
- PI (聚酰亚胺)
- Kapton
- PET
- 纸张
- 生物材料
- 聚合物薄膜

### 方法实体 (1 个)
- Laser-Induced Graphene (LIG)

### 性能指标 (3 个)
- electrical_conductivity (电导率)
- specific_surface_area (比表面积)
- raman_id_ig (拉曼 ID/IG 比)

### 应用领域 (10 个)
- supercapacitor (超级电容器)
- sensor (传感器)
- biomedical (生物医学)
- neural (神经)
- strain (应变)
- pressure (压力)
- flexible (柔性)
- wearable (可穿戴)
- energy (能源)
- battery (电池)

### 工艺参数 (6 个)
- P_W (激光功率)
- v_mms (扫描速度)
- E_Jcm2 (能量密度)
- wavelength_um (波长)
- atmosphere (气氛)
- temperature_C (温度)

---

## 🔗 关系类型

### 1. processed_by (材料→方法)
```
PI → processed_by → LIG
Kapton → processed_by → LIG
...
```

### 2. achieves_conductivity (方法→性能)
```
LIG → achieves_conductivity → high (σ > 1000 S/m)
LIG → achieves_conductivity → medium (100-1000 S/m)
LIG → achieves_conductivity → low (<100 S/m)
```

### 3. leads_to (参数→性能)
```
power_high → leads_to → conductivity_high
power_medium → leads_to → conductivity_medium
```

---

## 🧠 推理规则库

### RULE-001: 功率 - 速度因果律
```
IF: 高激光功率 + 慢扫描速度
THEN: 高电导率
置信度：0.85
```

### RULE-002: 前驱体效应
```
IF: PI 前驱体
THEN: 高电导率
置信度：0.75
```

### RULE-003: 缺陷 - 电导率负相关
```
IF: 高 ID/IG 比 (高缺陷)
THEN: 低电导率
置信度：0.70
```

### RULE-004: 研究机会识别
```
IF: 空气气氛 + 中等功率
THEN: 优化缺陷的研究机会
置信度：0.60
```

---

## 💡 研究机会发现

### 高优先级 (1 个)

#### 机会 1: 低功率区域 (<50mW) 研究不足
- **类型:** 参数空白
- **优先级:** 高
- **理由:** 当前研究集中在 100-1000mW，低功率机制未知
- **建议:** 系统研究 10-50mW 功率窗口

### 中优先级 (5 个)

1. **非常规前驱体研究不足**
   - 纸张、生物材料样本<5 个
   - 建议：拓展可持续前驱体

2. **神经应用研究空白**
   - 仅 3 篇论文
   - 建议：神经探针/脑机接口

3. **空气气氛优化空间**
   - 多数研究用惰性气体
   - 建议：空气气氛工艺优化

4. **中等功率参数窗口**
   - 50-500mW 研究分散
   - 建议：系统性参数扫描

5. **缺陷工程机会**
   - ID/IG 比与性能关系未明
   - 建议：可控缺陷引入

---

## 📈 知识图谱应用

### 1. 查询接口
```python
# 示例查询
query = {
    'precursor': 'PI',
    'target_conductivity': '>1000 S/m'
}
# 返回：最优工艺参数组合
```

### 2. 推理引擎
```python
# 因果推断
if power > 0.5W and speed < 20mm/s:
    predict conductivity = 'high'
```

### 3. 机会发现
- 自动识别研究空白
- 推荐实验方向
- 预测性能边界

---

## 🔬 技术实现

### 图谱构建流程
```
文献数据 → 实体提取 → 关系提取 → 图谱构建 → 推理引擎
   ↓           ↓           ↓           ↓           ↓
200 样本    26 实体     360 关系    JSON 存储    4 规则
```

### 文件格式
- **图谱数据:** `lig_knowledge_graph_v2.json`
- **机会报告:** `research_opportunities.md`
- **可视化:** (待生成 HTML 交互式图谱)

---

## 📊 与 CNT 知识图谱对比

| 维度 | CNT | LIG |
|------|-----|-----|
| 样本数 | 533 | 200 |
| 实体数 | ~30 | 26 |
| 关系数 | ~500 | 360 |
| 成熟度 | 高 | 中 |
| 推理规则 | 0 | 4 |

**互补性:**
- CNT: 高性能，理论成熟
- LIG: 低成本，应用创新
- 协同：CNT-LIG 复合材料

---

## 🎯 下一步扩展

### 短期 (1 周)
- [ ] 扩展到 500+ 样本
- [ ] 添加时间维度 (演化分析)
- [ ] 生成 HTML 可视化

### 中期 (1 月)
- [ ] 集成推理引擎到查询系统
- [ ] 添加不确定性量化
- [ ] 自动论文推荐

### 长期 (3 月)
- [ ] 跨材料图谱 (CNT+LIG+ 石墨烯)
- [ ] 预测模型集成
- [ ] 自动化实验设计

---

## 📁 文件位置

```
11-research/lig-knowledge-graph/
├── lig_knowledge_graph_v2.json      # 图谱数据
├── research_opportunities.md        # 机会报告
└── M-LIG-Knowledge-Graph-v2-2026-03-11.md  # 本文档
```

---

## 🔗 相关资源

### 脚本
- `11-research/scripts/lig_knowledge_graph_expander.py`

### 数据
- `11-research/data/lig_dataset_200.csv`

### 关联研究
- CNT 导电性预测：R²=0.799
- CNT vs LIG 对比：M-Note 已完成

---

*创建时间：2026-03-11*  
*版本：v2.0*  
*置信度：0.90*
