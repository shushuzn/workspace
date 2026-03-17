# 🔄 arXiv 收集器整合方案

**分析日期:** 2026-03-13  
**状态:** 发现重复，需要整合

---

## 📊 现有系统对比

| 特性 | Python 版 (30-scripts) | Node.js 版 (41-arxiv) |
|------|------------------------|----------------------|
| **语言** | Python | Node.js |
| **API** | RSS Feed | arXiv API |
| **输出** | Obsidian Markdown | JSON |
| **类别** | 单类别 (cs.AI) | 多关键词 (5 个) |
| **数量** | 15 篇/次 | 50 篇/关键词 |
| **代理** | ✅ Clash 集成 | ❌ 无 |
| **去重** | ❌ 无 | ✅ 基于 ID |
| **存储** | Obsidian Vault | JSON 文件 |
| **CLI** | ✅ arxiv_ops_cli.py | ❌ 无 |

---

## 🎯 整合方案

### 方案 A: 统一为 Python 版（推荐）

**理由:**
- ✅ 已有完整 CLI
- ✅ 代理配置完善
- ✅ 与 Obsidian 集成
- ✅ 技术栈统一

**行动:**
1. 增强 Python 版支持多关键词
2. 添加 JSON 输出选项
3. 添加去重功能
4. 删除 Node.js 版

### 方案 B: 保留两者，分工使用

**Python 版:**
- 主力收集器
- Obsidian 集成
- 定时任务

**Node.js 版:**
- 快速测试
- API 验证
- 数据导出

---

## 📋 推荐执行计划

### 阶段 1: 增强 Python 版 (今天)
- [ ] 支持多关键词/多类别
- [ ] 添加 JSON 输出选项
- [ ] 添加去重功能
- [ ] 测试验证

### 阶段 2: 数据整合 (明天)
- [ ] Node.js 数据导入 Python 版
- [ ] 统一数据格式
- [ ] 创建迁移脚本

### 阶段 3: 清理 (后天)
- [ ] 删除 Node.js 版 (或标记为 deprecated)
- [ ] 更新文档
- [ ] 配置定时任务

---

## 🚀 立即执行：增强 Python 版

### 新功能配置

```python
# config.json
{
  "categories": [
    "cs.AI",
    "cs.LG",
    "cs.CL",
    "cs.CV",
    "physics.chem-ph",
    "cond-mat.mtrl-sci"
  ],
  "keywords": [
    "graph neural network molecular",
    "transformer drug discovery",
    "conductivity prediction"
  ],
  "max_papers_per_category": 50,
  "output_format": ["markdown", "json"],
  "output_dirs": {
    "markdown": "D:\\obsidian\\Vault\\Arxiv",
    "json": "D:\\OpenClaw\\workspace\\40-collectors-收集\\arxiv\\data"
  },
  "proxy": "http://127.0.0.1:7897",
  "enable_dedup": true
}
```

---

## 📊 预期效果

| 指标 | 当前 | 整合后 |
|------|------|--------|
| 支持类别 | 1 | 6+ |
| 支持关键词 | 0 | 5+ |
| 输出格式 | 1 | 2 |
| 去重功能 | ❌ | ✅ |
| 论文数/次 | 15 | 300+ |

---

*Created:* 2026-03-13  
*Status:* 📋 计划中  
*Next:* 增强 Python 版
