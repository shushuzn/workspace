# 03-LIG-KNOWLEDGE-GRAPH - LIG 知识图谱

**用途:** LIG (激光诱导石墨烯) 领域知识图谱可视化和分析

**版本:** v6.0 (2026-03-11)

---

## 📁 目录结构

```
03-LIG-KNOWLEDGE-GRAPH/
├── graph-optimizer/           # 图谱优化
├── multimodal-kg/             # 多模态图谱
├── workers/                   # Web Worker (6 个)
│   ├── lig-worker.js
│   ├── lig-worker-v6.js
│   └── lig-worker-*.js
├── html/                      # HTML 工具 (19 个)
│   ├── LIG-Knowledge-Graph.html
│   ├── LIG-Graph-Editor.html
│   ├── LIG-Export-Tool.html
│   └── ...
├── scripts/                   # PowerShell 脚本 (11 个)
│   ├── lig-fetch-papers.ps1
│   ├── lig-update-graph.ps1
│   ├── lig-team-monitor.ps1
│   └── ...
├── ml/                        # 机器学习
│   └── train_lig_stability_model.py
└── README.md
```

---

## 🚀 快速使用

### 更新图谱
```powershell
# 获取最新论文
.\scripts\lig-fetch-papers.ps1

# 更新图谱
.\scripts\lig-update-graph.ps1
```

### 打开工具
```bash
# 主图谱
start html/LIG-Knowledge-Graph.html

# 编辑器
start html/LIG-Graph-Editor.html

# 导出工具
start html/LIG-Export-Tool.html
```

---

## ✨ 核心功能

### 图谱可视化
- ✅ **力导向布局** - D3.js 力导向图
- ✅ **聚类布局** - X/Y 约束聚类
- ✅ **边捆绑** - FDEB 算法
- ✅ **多布局切换** - 6 种布局算法

### 性能优化
- ✅ **Web Worker** - 后台计算
- ✅ **零拷贝传输** - ArrayBuffer
- ✅ **自适应阈值** - 动态调整
- ✅ **持久化存储** - localStorage
- ✅ **数据压缩** - LZ-String

### 数据分析
- ✅ **团队监控** - 核心研究组追踪
- ✅ **机会发现** - 研究空白识别
- ✅ **产业分析** - 公司/专利地图
- ✅ **稳定性预测** - ML 模型

---

## 📊 统计信息

| 类别 | 数量 | 大小 |
|------|------|------|
| Web Worker | 6 | 127KB |
| HTML 工具 | 19 | 400KB+ |
| PowerShell 脚本 | 11 | 35KB |
| Python 脚本 | 3 | 30KB |
| **总计** | **50** | **~600KB** |

---

*最后更新：2026-03-11 | 版本 v6.0*
