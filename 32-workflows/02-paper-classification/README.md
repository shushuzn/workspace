# 02 - 论文分类标注工作流 (Level 2)

**版本:** v4.0  
**创建时间:** 2026-03-05 17:07  
**更新时间:** 2026-03-05 17:15  
**自动化:** 每日 02:30 自动运行 (Level 1 完成后)  
**层次:** Level 2/5 - 分类标注

---

## 📋 工作流说明

### 功能 (Level 2)
- 自动分类论文 (材料体系/研究方法/应用领域)
- 关键词提取
- 重要性评分
- 相关性评分
- **为 Level 3 提供分类数据** ✨

### 输入
- Level 1 输出的 papers.json
- 关键词词典

### 输出
- 分类后的论文数据
- 按材料体系分类
- 保存位置：`classified/`

---

## 🔄 与上下游集成

### 数据流转
```
Level 1 (收集)
    ↓
papers.json
    ↓
Level 2 (分类标注) ← 本工作流
    ↓
classified/all_classified.json
    ↓
Level 3 (趋势分析)
```

---

## 🚀 使用方法

### 单次运行

```bash
cd D:\OpenClaw\workspace
python scripts/analysis/paper-classifier.py
```

### 完整流水线运行

```bash
bash scripts/analysis/run-pipeline.sh
```

---

## 📁 文件结构

```
workflows/paper-classification/
├── README.md              # 本文件
├── config.yaml            # 配置文件
├── keywords.yaml          # 关键词词典
├── run.sh                 # 运行脚本
├── logs/                  # 日志目录
└── outputs/               # 输出目录
    └── classified/
```

---

## ⚙️ 配置选项

### config.yaml
```yaml
classification:
  # 输入文件
  input_file: D:\\obsidian\\Vault\\Arxiv\\daily\\{date}\\raw\\papers.json
  
  # 输出目录
  output_dir: D:\\obsidian\\Vault\\Arxiv\\daily\\{date}\\classified\\
  
  # 分类体系
  material_systems:
    - oxide
    - sulfide
    - polymer
    - composite
  
  research_methods:
    - synthesis
    - characterization
    - testing
    - computation
  
  applications:
    - solid-state battery
    - Li-ion battery
    - Li-S battery
    - Li-air battery
  
  # 评分配置
  scoring:
    importance_threshold: 7.0
    relevance_threshold: 7.0
  
  # Level 3 集成
  level3_integration: true
  
  # 日志配置
  logging:
    level: INFO
    file: logs/classification.log
```

### keywords.yaml
```yaml
material_keywords:
  oxide:
    - oxide
    - LLZO
    - LATP
    - LLTO
    - garnet
    - perovskite
  sulfide:
    - sulfide
    - LGPS
    - LPS
    - argyrodite
    - thiophosphate
  polymer:
    - polymer
    - PEO
    - PVDF
    - PAN
    - polyethylene oxide
  composite:
    - composite
    - hybrid
    - ceramic-polymer

method_keywords:
  synthesis:
    - sol-gel
    - hydrothermal
    - ball milling
    - synthesis
  characterization:
    - XRD
    - SEM
    - TEM
    - XPS
    - characterization
  testing:
    - EIS
    - CV
    - cycling
    - electrochemical
  computation:
    - DFT
    - calculation
    - simulation
    - machine learning

application_keywords:
  solid-state battery:
    - solid-state
    - all-solid
    - ASSB
  Li-ion battery:
    - Li-ion
    - LIB
    - lithium-ion
```

---

## 📊 输出数据

### classified/all_classified.json
```json
[
  {
    "arxiv_id": "2603.00267",
    "classification": {
      "material_system": "oxide",
      "research_method": ["synthesis", "characterization"],
      "application": "solid-state battery"
    },
    "keywords": ["LLZO", "garnet", "solid electrolyte"],
    "importance_score": 8.5,
    "relevance_score": 9.2,
    "tags": ["high-priority", "must-read"]
  }
]
```

### 按材料体系分类
```
classified/
├── by_material/
│   ├── oxide.json
│   ├── sulfide.json
│   ├── polymer.json
│   └── composite.json
└── all_classified.json
```

---

## 📈 运行统计

### 分类统计
| 材料体系 | 论文数 | 占比 |
|----------|--------|------|
| oxide | ~40 | 31% |
| sulfide | ~35 | 28% |
| polymer | ~25 | 20% |
| composite | ~27 | 21% |

### 评分分布
| 评分 | 论文数 | 占比 |
|------|--------|------|
| 9-10 (must-read) | ~15 | 12% |
| 7-8 (high-priority) | ~40 | 31% |
| 5-6 (normal) | ~60 | 47% |
| <5 (low) | ~12 | 10% |

---

## 🔧 故障排除

### 常见问题

**1. 输入文件不存在**

症状：`papers.json not found`

解决：
```bash
# 检查 Level 1 是否运行
ls D:\\obsidian\\Vault\\Arxiv\\daily\\{date}\\raw\\papers.json

# 运行 Level 1
bash workflows/arxiv-collect/run.sh
```

**2. 分类结果为空**

症状：`Classified 0 papers`

解决：
```bash
# 检查关键词词典
cat workflows/paper-classification/keywords.yaml

# 检查输入数据
cat D:\\obsidian\\Vault\\Arxiv\\daily\\{date}\\raw\\papers.json
```

---

## 📞 相关文档

- [论文分析流水线](../../docs/PAPER-ANALYSIS-PIPELINE.md)
- [Level 1: 论文收集](../arxiv-collect/README.md)
- [Level 3: 趋势分析](../trend-analysis/README.md)

---

*最后更新：2026-03-05 17:07*  
*工作流版本：v1.0*  
*多层次分析：Level 2/5*
