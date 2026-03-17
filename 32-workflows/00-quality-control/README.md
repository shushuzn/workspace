# Level 0: 质量控制工作流

**版本:** v1.0  
**创建时间:** 2026-03-05 17:30  
**自动化:** 每日 01:50 自动运行 (Level 1 之前)  
**层次:** Level 0/6 - 质量控制

---

## 📋 工作流说明

### 功能 (Level 0)
- 数据验证 (格式/完整性)
- 异常检测 (重复/错误)
- 数据清洗 (去重/标准化)
- 质量评分 (可信度评估)
- 质量检查点 (Quality Gate)

### 输入
- Level 1 输出的 raw/papers.json

### 输出
- quality-controlled/validated_papers.json
- quality-controlled/quality_report.json

---

## 🔄 数据流转

```
Level 1 (收集)
    ↓
raw/papers.json
    ↓
Level 0 (质量控制) ← 本工作流
    ↓
quality-controlled/validated_papers.json
    ↓
Level 2 (分类标注)
```

---

## ⚙️ 质量检查点 (Quality Gate)

### 通过标准
| 指标 | 阈值 | 状态 |
|------|------|------|
| 质量评分 | ≥ 0.80 | ✅ 通过 |
| 质量评分 | < 0.80 | ❌ 失败，停止流程 |

### 评分计算
```
score = pass_rate * 0.7 + (1 - anomaly_rate) * 0.3
```

### 等级划分
| 分数 | 等级 | 操作 |
|------|------|------|
| ≥ 0.95 | A | 优秀 |
| ≥ 0.90 | B | 良好 |
| ≥ 0.80 | C | 通过 |
| ≥ 0.70 | D | 警告 |
| < 0.70 | F | 失败，停止 |

---

## 🚀 使用方法

### 单次运行

```bash
cd D:\OpenClaw\workspace
python scripts/level-0/quality-controller.py
```

### 完整流水线运行

```bash
bash scripts/analysis/run-pipeline.sh
```

---

## 📊 验证规则

### 必填字段检查
- arxiv_id
- title
- abstract

### 格式验证
- arxiv_id 格式：YYMM.NNNNN
- 标题长度：≥ 10 字符
- 摘要长度：≥ 50 字符

### 异常检测
- 重复论文检测
- 标题长度异常
- 摘要长度异常

---

## 📁 输出数据

### validated_papers.json
```json
{
  "metadata": {
    "source": "level-0-quality-control",
    "version": "1.0",
    "processed_at": "2026-03-05T01:50:00",
    "checksum": "abc123..."
  },
  "data": [
    {
      "arxiv_id": "2603.00267",
      "title": "论文标题",
      "abstract": "摘要内容",
      "validation_status": "valid",
      "processed_at": "2026-03-05T01:50:00"
    }
  ]
}
```

### quality_report.json
```json
{
  "date": "2026-03-05",
  "total_papers": 127,
  "valid": 125,
  "invalid": 2,
  "anomalies": 3,
  "quality_score": {
    "score": 0.965,
    "level": "A",
    "pass_rate": 0.984,
    "anomaly_rate": 0.024
  },
  "invalid_papers": [...],
  "anomalies": [...]
}
```

---

## 🔧 故障排除

### 常见问题

**1. 质量评分低**

症状：`Quality gate FAILED`

解决：
```bash
# 查看质量报告
cat D:\obsidian\Vault\Arxiv\daily\{date}\quality-controlled\quality_report.json

# 检查无效论文
# 检查异常数据
```

**2. 大量无效数据**

症状：`Invalid: 50+`

解决：
```bash
# 检查 Level 1 输出
cat D:\obsidian\Vault\Arxiv\daily\{date}\raw\papers.json

# 重新运行 Level 1
bash workflows/01-arxiv-collect/run.sh
```

---

## 📞 相关文档

- [论文分析流水线](../../docs/PAPER-ANALYSIS-PIPELINE.md)
- [Level 1: 论文收集](../01-arxiv-collect/README.md)
- [Level 2: 分类标注](../02-paper-classification/README.md)

---

*最后更新：2026-03-05 17:30*  
*工作流版本：v1.0*  
*多层次分析：Level 0/6*
