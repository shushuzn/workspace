# 03 - 趋势分析工作流 (Level 3)

**版本:** v4.0  
**创建时间:** 2026-03-05 16:40  
**更新时间:** 2026-03-05 17:15  
**自动化:** 每日 03:00 自动运行 (Level 2 完成后)  
**层次:** Level 3/5 - 趋势分析

---

## 📋 工作流说明

### 功能 (Level 3)
- 自动分析材料科学论文趋势
- 识别研究热点
- 发现新兴领域
- 追踪技术演进
- **为 Level 4 提供趋势数据** ✨

### 输入
- Level 2 输出的 classified/all_classified.json
- 历史趋势数据 (可选)

### 输出
- 趋势分析数据
- 热门主题列表
- 新兴领域列表
- 技术演进分析
- 保存位置：`trends/`

---

## 🔄 与上下游集成

### 数据流转
```
Level 2 (分类)
    ↓
classified/all_classified.json
    ↓
Level 3 (趋势分析) ← 本工作流
    ↓
trends/trends.json
    ↓
Level 4 (主题聚类)
```

---

## 🚀 使用方法

### 单次运行

```bash
cd D:\OpenClaw\workspace
python scripts/analysis/trend-analyzer.py
```

### 完整流水线运行

```bash
bash scripts/analysis/run-pipeline.sh
```

---

## 📁 文件结构

```
workflows/trend-analysis/
├── README.md              # 本文件
├── config.yaml            # 配置文件 (已更新)
├── keywords.txt           # 关键词列表
├── run.sh                 # 运行脚本
├── logs/                  # 日志目录
│   └── analysis.log
└── outputs/               # 输出目录
    └── trends/
        ├── trends.json
        └── hot-topics.md
```

---

## ⚙️ 配置选项

### config.yaml (已更新)
```yaml
# 趋势分析配置 (Level 3)
analysis:
  # 输入来自 Level 2 ✨
  input_from_level2: true
  input_file: D:\\obsidian\\Vault\\Arxiv\\daily\\{date}\\classified\\all_classified.json
  
  # 关键词文件
  keywords_file: keywords.txt
  
  # 热门主题数量
  hot_topics_count: 10
  
  # 新兴领域阈值
  emerging_threshold: 5
  
  # 技术演进分析
  tech_evolution:
    enabled: true
    stages:
      - emerging
      - growing
      - mature
  
  # Level 4 集成 ✨
  level4_integration: true
  
  # 输出配置
  output:
    format: json
    file: outputs/trends.json
    include_markdown: true
    markdown_file: outputs/hot-topics.md
  
  # 日志配置
  logging:
    level: INFO
    file: logs/analysis.log
    max_size: 10MB
    backup_count: 7
```

---

## 📊 输出数据

### trends/trends.json
```json
{
  "date": "2026-03-05",
  "total_papers": 127,
  "hot_topics": [
    ["Solid-state batteries", 45],
    ["AI materials design", 38],
    ["Perovskites", 32]
  ],
  "emerging_fields": [
    "Quantum materials",
    "2D materials"
  ],
  "technology_evolution": [
    {"tech": "sulfide electrolyte", "stage": "mature"},
    {"tech": "composite electrolyte", "stage": "growing"},
    {"tech": "AI-designed materials", "stage": "emerging"}
  ],
  "by_category": {
    "oxide": 40,
    "sulfide": 35,
    "polymer": 25,
    "composite": 27
  }
}
```

---

## 📈 分析算法

### 热点话题识别
```python
def identify_hot_topics(papers):
    # 统计关键词频率
    keyword_counter = Counter()
    for paper in papers:
        keywords = paper.get('keywords', [])
        keyword_counter.update(keywords)
    
    # 获取前 10 个热点
    hot_topics = keyword_counter.most_common(10)
    return hot_topics
```

### 新兴方向发现
```python
def discover_emerging_fields(papers):
    # 高重要性但数量少的方向
    emerging = []
    for paper in papers:
        if paper['importance_score'] >= 8.0:
            material = paper['classification']['material_system']
            # 数量少但重要性高 = 新兴方向
            emerging.append(material)
    return emerging
```

### 技术演进分析
```python
def analyze_tech_evolution(papers):
    tech_stages = {
        'emerging': [],   # AI/ML 相关
        'growing': [],    # 复合材料相关
        'mature': []      # 硫化物相关
    }
    # 基于关键词分类
    return tech_stages
```

---

## 🔧 故障排除

### 常见问题

**1. 输入文件不存在**

症状：`all_classified.json not found`

解决：
```bash
# 检查 Level 2 是否运行
ls D:\\obsidian\\Vault\\Arxiv\\daily\\{date}\\classified\\

# 运行 Level 2
python scripts/analysis/paper-classifier.py
```

**2. 分析结果为空**

症状：`Hot topics: 0`

解决：
```bash
# 检查关键词列表
cat workflows/trend-analysis/keywords.txt

# 添加新关键词
echo "New keyword" >> workflows/trend-analysis/keywords.txt
```

---

## 📞 相关文档

- [论文分析流水线](../../docs/PAPER-ANALYSIS-PIPELINE.md)
- [Level 2: 分类标注](../paper-classification/README.md)
- [Level 4: 主题聚类](../topic-clustering/README.md)

---

*最后更新：2026-03-05 17:07*  
*工作流版本：v3.0*  
*多层次分析：Level 3/5*
