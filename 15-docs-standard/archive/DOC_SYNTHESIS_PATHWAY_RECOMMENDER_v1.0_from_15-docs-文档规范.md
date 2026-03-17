#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Synthesis Pathway Recommender v1 - 设计文档
材料合成路径推荐系统
"""

# 技术方案

## 1. 反应数据库集成

### 数据源
| 数据库 | 类型 | 访问方式 |
|--------|------|----------|
| ICSD | 晶体结构 | 付费 API |
| Pearson's Crystal Data | 晶体数据 | 付费 |
| NIST Chemistry WebBook | 反应数据 | 免费 |
| PubChem | 化合物信息 | 免费 API |

### 自建数据库
**字段设计:**
```json
{
  "reaction_id": "RXN001",
  "reactants": ["Li2CO3", "CoCO3"],
  "products": ["LiCoO2", "CO2"],
  "conditions": {
    "temperature": 900,
    "time": 12,
    "atmosphere": "air"
  },
  "yield": 0.95,
  "reference": "DOI:10.1000/xxx"
}
```

## 2. 合成条件提取

### NLP 方法
1. **规则匹配**
   ```python
   import re
   
   # 温度匹配
   temp_pattern = r'(\d+)\s*[°℃]'
   temps = re.findall(temp_pattern, text)
   
   # 时间匹配
   time_pattern = r'(\d+)\s*(hour|hr|h)'
   times = re.findall(time_pattern, text)
   ```

2. **命名实体识别 (NER)**
   - 训练材料科学专用 NER 模型
   - 识别：温度、时间、气氛、溶剂等

3. **关系提取**
   - 反应物→产物关系
   - 条件→反应关系

### 示例
```
原文: "LiCoO2 was synthesized by solid-state reaction 
      of Li2CO3 and CoCO3 at 900°C for 12h in air."

提取结果:
{
  "product": "LiCoO2",
  "reactants": ["Li2CO3", "CoCO3"],
  "method": "solid-state reaction",
  "temperature": 900,
  "time": 12,
  "atmosphere": "air"
}
```

## 3. 路径规划算法

### 算法选择
1. **广度优先搜索 (BFS)**
   - 适用：短路径搜索
   - 复杂度：O(b^d)

2. **A* 算法**
   - 适用：有启发式函数的场景
   - 复杂度：O(b^d)

3. ** retrosynthesis 算法**
   - 适用：逆向合成规划
   - 从目标材料反向推导

### 示例代码
```python
from collections import deque

def find_synthesis_path(target, available_reactants, reaction_db):
    """BFS 搜索合成路径"""
    queue = deque([(target, [])])
    visited = set()
    
    while queue:
        current, path = queue.popleft()
        
        if current in available_reactants:
            return path
        
        if current in visited:
            continue
        visited.add(current)
        
        # 查找能生成 current 的反应
        for reaction in reaction_db:
            if current in reaction['products']:
                reactants = reaction['reactants']
                new_path = path + [reaction]
                for reactant in reactants:
                    queue.append((reactant, new_path))
    
    return None  # 无可行路径
```

## 4. 成本估算

### 成本组成
1. **原材料成本**
   - 从化学品供应商获取价格
   - Sigma-Aldrich, Alfa Aesar 等

2. **能源成本**
   - 高温处理能耗
   - 真空/气氛成本

3. **设备成本**
   - 专用设备折旧
   - 人工成本

### 估算公式
```
总成本 = Σ(原材料成本) + 能源成本 + 设备成本
```

## 5. 安全性评估

### 评估因素
1. **化学品危险性**
   - 易燃、易爆、有毒
   - GHS 分类

2. **反应条件危险性**
   - 高温、高压
   - 放热反应

3. **产物危险性**
   - 毒性、环境影响

### 安全评分
```
安全评分 = 100 - (危险性分数 × 权重)
```

## 6. 预计工作量

| 任务 | 用时 |
|------|------|
| 反应数据库集成 | 2 小时 |
| 合成条件提取 | 2 小时 |
| 路径规划算法 | 2 小时 |
| 成本估算 | 1 小时 |
| 安全性评估 | 1 小时 |
| **总计** | **8 小时** |

## 7. 实施计划

**时间:** 2026-03-19 ~ 03-23  
**优先级:** 🟡 中

---

*创建时间：2026-03-05 13:25*
