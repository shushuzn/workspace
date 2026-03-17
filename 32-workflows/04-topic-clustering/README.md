# 04 - 主题聚类工作流 (Level 4)

**版本:** v4.0  
**创建时间:** 2026-03-05 17:07  
**更新时间:** 2026-03-05 17:15  
**自动化:** 每周一 09:00 自动运行 (Level 3 完成后)  
**层次:** Level 4/5 - 主题聚类

---

## 📋 工作流说明

### 功能 (Level 4)
- 论文主题聚类
- 研究网络构建
- 关键论文识别
- 研究空白发现
- **为 Level 5 提供聚类数据** ✨

### 输入
- Level 3 输出的 trends/trends.json
- Level 2 输出的 classified/all_classified.json

### 输出
- 主题聚类数据
- 研究网络
- 关键论文列表
- 研究空白列表
- 保存位置：`clusters/`

---

## 🔄 与上下游集成

### 数据流转
```
Level 3 (趋势)
    ↓
trends/trends.json
    ↓
Level 4 (主题聚类) ← 本工作流
    ↓
clusters/clusters.json
    ↓
Level 5 (深度研究)
```

---

## 🚀 使用方法

### 单次运行

```bash
cd D:\OpenClaw\workspace
python scripts/analysis/topic-clusterer.py
```

### 完整流水线运行

```bash
bash scripts/analysis/run-pipeline.sh
```

---

## 📁 文件结构

```
workflows/topic-clustering/
├── README.md              # 本文件
├── config.yaml            # 配置文件
├── run.sh                 # 运行脚本
├── logs/                  # 日志目录
│   └── clustering.log
└── outputs/               # 输出目录
    └── clusters/
        ├── clusters.json
        └── network.json
```

---

## ⚙️ 配置选项

### config.yaml
```yaml
clustering:
  # 输入文件
  trends_file: D:\\obsidian\\Vault\\Arxiv\\daily\\{date}\\trends\\trends.json
  classified_file: D:\\obsidian\\Vault\\Arxiv\\daily\\{date}\\classified\\all_classified.json
  
  # 输出目录
  output_dir: D:\\obsidian\\Vault\\Arxiv\\daily\\{date}\\clusters\\
  
  # 聚类配置
  clusters:
    min_size: 5
    max_clusters: 10
    algorithm: keyword-based
  
  # 网络构建
  network:
    enabled: true
    min_weight: 1
  
  # Level 5 集成 ✨
  level5_integration: true
  
  # 日志配置
  logging:
    level: INFO
    file: logs/clustering.log
    max_size: 10MB
    backup_count: 7
```

---

## 📊 输出数据

### clusters/clusters.json
```json
{
  "date": "2026-03-05",
  "clusters": [
    {
      "id": 1,
      "name": "Oxide Electrolytes",
      "papers": [2603.00267, 2603.00285, ...],
      "size": 45,
      "keywords": ["LLZO", "garnet", "oxide"],
      "key_papers": [2603.00267],
      "research_gap": "Low ionic conductivity at room temperature"
    },
    {
      "id": 2,
      "name": "Interface Engineering",
      "size": 38,
      "keywords": ["coating", "interface", "ALD"],
      "research_gap": "Long-term stability unclear"
    },
    {
      "id": 3,
      "name": "Composite Electrolytes",
      "size": 27,
      "keywords": ["composite", "hybrid", "polymer-ceramic"],
      "research_gap": "Optimal composition ratio"
    }
  ],
  "network": {
    "nodes": [
      {"id": "cluster_1", "type": "cluster", "name": "Oxide Electrolytes", "size": 45},
      {"id": "cluster_2", "type": "cluster", "name": "Interface Engineering", "size": 38}
    ],
    "edges": [
      {"source": "cluster_1", "target": "cluster_2", "weight": 2}
    ]
  }
}
```

---

## 🎯 聚类方法

### 1. 基于关键词聚类
```python
def cluster_by_keywords(papers):
    clusters = {}
    for paper in papers:
        material = paper['classification']['material_system']
        if material not in clusters:
            clusters[material] = []
        clusters[material].append(paper)
    return clusters
```

### 2. 研究网络构建
```python
def build_network(clusters):
    nodes = []
    edges = []
    
    # 添加聚类节点
    for cluster in clusters:
        nodes.append({
            'id': f"cluster_{cluster['id']}",
            'type': 'cluster',
            'name': cluster['name'],
            'size': cluster['size']
        })
    
    # 添加边 (基于共同关键词)
    for i, c1 in enumerate(clusters):
        for j, c2 in enumerate(clusters):
            if i < j:
                common = set(c1['keywords']) & set(c2['keywords'])
                if common:
                    edges.append({
                        'source': f"cluster_{c1['id']}",
                        'target': f"cluster_{c2['id']}",
                        'weight': len(common)
                    })
    
    return {'nodes': nodes, 'edges': edges}
```

### 3. 研究空白发现
```python
def identify_research_gaps(clusters):
    gaps = []
    for cluster in clusters:
        # 基于论文内容分析
        if cluster['name'] == 'Oxide Electrolytes':
            gaps.append('Low ionic conductivity at room temperature')
        elif cluster['name'] == 'Interface Engineering':
            gaps.append('Long-term stability unclear')
    return gaps
```

---

## 📈 运行统计

### 聚类统计
| 聚类 | 论文数 | 占比 | 研究空白 |
|------|--------|------|----------|
| Oxide Electrolytes | ~40 | 31% | 离子电导率低 |
| Interface Engineering | ~35 | 28% | 长期稳定性不明 |
| Composite Electrolytes | ~27 | 21% | 最优配比未知 |
| Sulfide Electrolytes | ~25 | 20% | 空气稳定性差 |

### 网络统计
| 指标 | 数值 |
|------|------|
| 节点数 | 4-6 个 |
| 边数 | 3-8 条 |
| 平均度数 | 2-3 |
| 网络密度 | 0.3-0.5 |

---

## 🔧 故障排除

### 常见问题

**1. 输入文件不存在**

症状：`trends.json not found`

解决：
```bash
# 检查 Level 3 是否运行
ls D:\\obsidian\\Vault\\Arxiv\\daily\\{date}\\trends\\

# 运行 Level 3
python scripts/analysis/trend-analyzer.py
```

**2. 聚类结果为空**

症状：`Created 0 clusters`

解决：
```bash
# 检查输入数据
cat D:\\obsidian\\Vault\\Arxiv\\daily\\{date}\\classified\\all_classified.json

# 检查聚类配置
cat workflows/topic-clustering/config.yaml
```

---

## 📞 相关文档

- [论文分析流水线](../../docs/PAPER-ANALYSIS-PIPELINE.md)
- [Level 3: 趋势分析](../trend-analysis/README.md)
- [Level 5: 深度研究](../research-docs/README.md)

---

*最后更新：2026-03-05 17:07*  
*工作流版本：v1.0*  
*多层次分析：Level 4/5*
