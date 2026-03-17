# 🔗 技能集成指南

**集成日期:** 2026-03-04  
**工作空间:** D:\OpenClaw\workspace

---

## ✅ 已集成技能

### 1. arxiv-daily (每日论文收集)

**配置:** `D:\OpenClaw\workspace\Arxiv\config.yaml`  
**输出:** `D:\OpenClaw\workspace\Arxiv\collected\`  
**定时:** 每天 2:00 AM

**手动执行:**
```bash
py D:\OpenClaw\workspace\Arxiv\arxiv-daily.py --categories cs.AI,cs.LG --output D:\OpenClaw\workspace\Arxiv\collected\
```

**功能:**
- ✅ 多类别监听 (cs.AI, cs.LG, cs.CL, etc.)
- ✅ 优先级评分 (1-5 分)
- ✅ 去重处理 (基于 arXiv ID)
- ✅ JSON/Markdown 输出

---

### 2. medium-watcher (文章监听)

**配置:** `D:\OpenClaw\workspace\Medium\config.yaml`  
**输出:** `D:\OpenClaw\workspace\Medium\Raw\`  
**定时:** 每天 8:00 AM

**手动执行:**
```bash
py D:\OpenClaw\workspace\Medium\medium-watcher.py --tags ai,llm --output D:\OpenClaw\workspace\Medium\Raw\
```

**功能:**
- ✅ 按标签/作者/出版物订阅
- ✅ 内容提取 (正文/图片/代码)
- ✅ 质量评分 (阅读数/点赞/评论)
- ✅ 自动归档 (30 天)

---

### 3. memory-distiller (知识蒸馏)

**配置:** `D:\OpenClaw\workspace\memory\distiller-config.yaml`  
**输出:** `D:\OpenClaw\workspace\MEMORY.md`  
**定时:** 每周日 11:00 PM

**手动执行:**
```bash
py D:\OpenClaw\workspace\memory\distiller.py --input D:\OpenClaw\workspace\memory\ --output D:\OpenClaw\workspace\MEMORY.md
```

**功能:**
- ✅ 观点提取 (从每日笔记)
- ✅ 去重合并 (语义相似度)
- ✅ 置信度评估 (高/中/低)
- ✅ 增量更新 MEMORY.md

---

## 🔄 工作流集成

```
arxiv-daily (2am)
    ↓
Arxiv/collected/*.json
    ↓
ai-research-os (深度解析)
    ↓
P-Note/C-Note/M-Note

medium-watcher (8am)
    ↓
Medium/Raw/*.md
    ↓
筛选高质内容
    ↓
深度分析/归档

memory/*.md (每日笔记)
    ↓
memory-distiller (周日 11pm)
    ↓
MEMORY.md (长期记忆)
```

---

## 📊 依赖安装

```bash
py -m pip install feedparser requests beautifulsoup4 pyyaml
```

---

## ⚙️ 配置说明

### arxiv-daily

编辑 `D:\OpenClaw\workspace\Arxiv\config.yaml`:
- `categories`: 添加/删除监听类别
- `keywords.include`: 核心关键词 (加分)
- `keywords.exclude`: 排除关键词 (减分)
- `min_score`: 最低分数阈值 (默认 3.0)

### medium-watcher

编辑 `D:\OpenClaw\workspace\Medium\config.yaml`:
- `tags`: 订阅标签
- `authors`: 订阅作者
- `publications`: 订阅出版物
- `min_score`: 最低质量分数 (默认 3.0)

### memory-distiller

编辑 `D:\OpenClaw\workspace\memory\distiller-config.yaml`:
- `categories`: 观点分类
- `distillation.min_confidence`: 最小置信度
- `schedule.frequency`: 执行频率

---

## 🚀 下一步

1. **安装依赖:**
   ```bash
   py -m pip install feedparser requests beautifulsoup4 pyyaml
   ```

2. **测试运行:**
   ```bash
   # 测试 arxiv-daily
   py D:\OpenClaw\workspace\skills\arxiv-daily\scripts\arxiv-daily.py --categories cs.AI --output D:\OpenClaw\workspace\Arxiv\collected\
   
   # 测试 medium-watcher
   py D:\OpenClaw\workspace\skills\medium-watcher\scripts\medium-watcher.py --tags ai --output D:\OpenClaw\workspace\Medium\Raw\
   ```

3. **配置定时任务:**
   - OpenClaw 心跳检查已集成
   - 或使用 Windows 定时任务

4. **监控运行:**
   - 查看输出目录
   - 检查日志文件
   - 验证 MEMORY.md 更新

---

## 📝 文件结构

```
D:\OpenClaw\workspace\
├── Arxiv/
│   ├── config.yaml              # arxiv-daily 配置
│   ├── papers/                  # 原始 PDF 存储
│   └── collected/               # 收集的论文元数据
│
├── Medium/
│   ├── config.yaml              # medium-watcher 配置
│   ├── Raw/                     # 原始文章
│   └── Archive/                 # 归档 (30 天+)
│
├── memory/
│   ├── distiller-config.yaml    # memory-distiller 配置
│   ├── YYYY-MM-DD.md            # 每日笔记
│   └── MEMORY.md                # 长期记忆
│
└── scripts/
    ├── integrate-collectors.py  # 集成脚本
    └── research-stats.py        # 统计看板
```

---

*集成完成，系统已就绪！* 🎉
