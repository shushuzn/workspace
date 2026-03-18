# 🔄 arXiv 收集器集成计划

**创建时间:** 2026-03-13 22:50  
**状态:** 📋 计划中

---

## 📊 当前状态

### 现有系统
| 系统 | 位置 | 状态 | 功能 |
|------|------|------|------|
| Python 版 v1 | `30-scripts/04-COLLECTORS/arxiv-collector.py` | ✅ 运行中 | 单类别 RSS |
| Python 版 v2 | `30-scripts/04-COLLECTORS/arxiv-collector-v2.py` | ✅ 新增 | 多类别 + 关键词 + 去重 |
| Node.js 版 | `41-arxiv-collector/` | ✅ 新增 | 轻量级测试 |
| PowerShell | `30-scripts/04-COLLECTORS/arxiv/arxiv-research-orchestrator.ps1` | ✅ 存在 | 38 领域编排 |

### 首次运行结果 (v2)
```
类别抓取:
  cs.AI: 50 篇 ✅
  cs.LG: 超时 ⚠️
  cs.CL: 50 篇 ✅

关键词抓取:
  graph neural network molecular: 50 篇 ✅
  transformer drug discovery: 50 篇 ✅
  conductivity prediction: 50 篇 ✅

总计：250 篇新论文
```

---

## 🎯 集成目标

### 短期 (本周)
1. ✅ 统一 Python v2 为主力收集器
2. ⏳ 配置定时任务 (每天 8AM)
3. ⏳ 添加 PDF 自动下载
4. ⏳ 集成到 OpenClaw 工作流

### 中期 (下周)
1. ⏳ 添加更多类别 (cs.CV, physics.chem-ph...)
2. ⏳ 优化代理配置
3. ⏳ 添加错误重试机制
4. ⏳ 创建 Web 界面

### 长期 (本月)
1. ⏳ 与知识卡片生成器集成
2. ⏳ 自动摘要生成
3. ⏳ 研究领域推荐
4. ⏳ 协作编辑功能

---

## 🔧 集成方案

### 方案 A: Python v2 作为主力 (推荐)

**理由:**
- ✅ 功能最全 (多类别 + 关键词 + 去重)
- ✅ 代理配置完善
- ✅ 双格式输出 (Markdown + JSON)
- ✅ 与 Obsidian 集成

**架构:**
```
arxiv-collector-v2.py
    ↓
data/papers/*.json (JSON 数据)
    ↓
../obsidian/Vault/Arxiv/*.md (Markdown 笔记)
    ↓
OpenClaw 分析流程
```

### 方案 B: PowerShell 编排器 + Python 收集

**理由:**
- ✅ 38 领域覆盖
- ✅ 已有编排逻辑
- ✅ 可扩展性强

**架构:**
```
arxiv-research-orchestrator.ps1
    ↓
调用 arxiv-collector-v2.py
    ↓
多领域并行收集
```

---

## 📋 实施步骤

### 步骤 1: 配置优化 (今天)
```python
# arxiv-collector-v2.py 配置
CATEGORIES = [
    'cs.AI',      # 人工智能
    'cs.LG',      # 机器学习
    'cs.CL',      # 计算语言学
    'cs.CV',      # 计算机视觉
    'physics.chem-ph',  # 计算化学
    'cond-mat.mtrl-sci' # 材料科学
]

KEYWORDS = [
    'graph neural network molecular',
    'transformer drug discovery',
    'conductivity prediction',
    'machine learning materials'
]

MAX_PAPERS = 50  # 每类别/关键词
```

### 步骤 2: 定时任务配置 (明天)
```bash
# Windows 任务计划程序
# 创建基本任务
# 名称：arXiv Daily Collector
# 触发器：每天 8:00 AM
# 操作：启动程序
# 程序：python.exe
# 参数：arxiv-collector-v2.py
# 起始于：D:\OpenClaw\workspace\30-scripts-脚本工具\04-COLLECTORS
```

### 步骤 3: PDF 自动下载 (后天)
```python
# 添加 PDF 下载功能
def download_pdf(paper):
    pdf_url = paper['link'].replace('abs', 'pdf')
    save_path = f"pdfs/{paper['id']}.pdf"
    # 下载逻辑...
    return save_path
```

### 步骤 4: OpenClaw 集成 (本周)
```javascript
// OpenClaw 工作流
1. arXiv 收集器运行 → JSON 数据
2. PDF 自动下载 → PDF 文件
3. PDF 解析器 → 文本内容
4. OpenAI 分析 → 结构化数据
5. 记忆系统 → 长期存储
6. 知识卡片 → HTML 展示
```

---

## 📊 预期效果

### 收集能力
| 指标 | 当前 | 集成后 |
|------|------|--------|
| 支持类别 | 3 | 6+ |
| 支持关键词 | 3 | 10+ |
| 论文数/天 | 250 | 500+ |
| PDF 下载 | ❌ | ✅ |
| 自动分析 | ❌ | ✅ |

### 时间节省
| 任务 | 手动 | 自动 | 节省 |
|------|------|------|------|
| 论文收集 | 30 分钟/天 | 0 | 100% |
| 去重筛选 | 20 分钟/天 | 0 | 100% |
| 摘要阅读 | 60 分钟/天 | 10 分钟 | 83% |
| **总计** | **110 分钟/天** | **10 分钟/天** | **91%** |

---

## 🗂️ 文件结构

### 推荐结构
```
30-scripts-脚本工具/
└── 04-COLLECTORS/
    ├── arxiv/
    │   ├── arxiv-research-orchestrator.ps1  # 编排器
    │   └── arxiv_ops_cli.py                 # CLI 工具
    ├── arxiv-collector.py                   # v1 (保留)
    ├── arxiv-collector-v2.py                # v2 (主力) ✅
    ├── ARXIV-INTEGRATION-PLAN.md            # 集成计划
    ├── INTEGRATION-COMPLETE.md              # 完成报告
    └── data/                                # 数据目录
        ├── papers/                          # JSON 数据
        └── seen_ids.json                    # 去重数据库

40-collectors-收集/
└── arxiv/
    ├── arxiv-collector.js                   # Node.js 版 (轻量)
    └── data/                                # 输出数据

obsidian/
└── Vault/
    └── Arxiv/                               # Markdown 笔记
```

---

## 🔗 与其他项目集成

### 知识卡片生成器
```
arXiv 收集器 → JSON 数据
    ↓
知识卡片生成器 → HTML 卡片
    ↓
网站展示 / 分享
```

### OpenClaw 研究助手
```
arXiv 收集器 → 新论文
    ↓
PDF 解析 + OpenAI 分析
    ↓
7 人格研究团队 → 深度分析
    ↓
记忆系统 → 知识沉淀
```

### TON Hackathon 项目
```
arXiv 收集器 → 数据源
    ↓
OpenClaw Research Agent
    ↓
Telegram Bot 展示
    ↓
用户交互
```

---

## ⏭️ 下一步

### 立即可做 (5 分钟)
- [ ] 确认 v2 运行正常
- [ ] 检查输出文件
- [ ] 验证 JSON 格式

### 今天完成 (30 分钟)
- [ ] 优化配置 (添加更多类别)
- [ ] 测试代理稳定性
- [ ] 创建定时任务

### 本周完成 (2 小时)
- [ ] PDF 自动下载功能
- [ ] OpenClaw 集成测试
- [ ] 文档完善

---

## 📞 依赖关系

### 需要安装
```bash
pip install feedparser requests
```

### 需要配置
- 代理：`http://127.0.0.1:7897` (Clash)
- 输出目录：`D:\obsidian\Vault\Arxiv`
- JSON 目录：`D:\OpenClaw\workspace\40-collectors-收集\arxiv\data`

---

## 🎉 成功标准

### 功能标准
- [ ] 每日自动收集 500+ 篇论文
- [ ] 支持 6+ 个研究领域
- [ ] 自动去重准确率 100%
- [ ] PDF 下载成功率>90%

### 性能标准
- [ ] 运行时间<5 分钟
- [ ] 内存占用<500MB
- [ ] 网络请求成功率>95%

### 用户标准
- [ ] 零人工干预
- [ ] 输出格式统一
- [ ] 易于扩展新领域

---

*Created:* 2026-03-13 22:50  
*Status:* 📋 计划中  
*Next:* 配置优化 + 定时任务  
*Priority:* P1 (高)
