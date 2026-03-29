# News Workflow Engine

**智能新闻工作流引擎** - 整合 NewsHub + agentic-bpm + patrol-agent

## ✨ 特性

| 特性 | 描述 |
|------|------|
| 📰 **自动抓取** | 多源新闻定时抓取 |
| 🧠 **智能分析** | AI 分析重要性、分类、情感 |
| 🔗 **工作流触发** | 基于新闻自动创建任务 |
| 🤖 **自动执行** | patrol-agent 执行任务 |
| 📊 **反馈闭环** | 结果分析优化模型 |
| 📬 **多渠道推送** | 飞书、Telegram、邮件等 |

## 🏗️ 架构

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  NewsHub    │───►│ agentic-bpm │───►│patrol-agent │
│ (信息获取)   │    │ (工作流编排) │    │ (任务执行)  │
└─────────────┘    └─────────────┘    └─────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌────────────────────────────────────────────────────┐
│              统一数据库 (SQLite)                    │
└────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────┐    ┌─────────────┐
│  推送模块    │    │  反馈模块    │
└─────────────┘    └─────────────┘
```

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置
copy config\config.example.yaml config\config.yaml

# 初始化数据库
python -m news_workflow init

# 启动服务
python -m news_workflow run

# 或使用定时任务
python -m news_workflow scheduler
```

## 📁 项目结构

```
news-workflow-engine/
├── src/
│   └── news_workflow/
│       ├── __init__.py
│       ├── core/           # 核心引擎
│       ├── analyzer/       # 新闻分析
│       ├── workflow/       # 工作流管理
│       ├── executor/       # 任务执行
│       ├── feedback/       # 反馈闭环
│       └── push/           # 推送模块
├── config/
│   ├── config.example.yaml
│   └── workflows/          # 工作流模板
├── tests/
├── docs/
├── requirements.txt
└── README.md
```

## 🔧 配置示例

```yaml
# config.yaml
news:
  sources:
    - sina_finance
    - wallstreet_cn
    - 36kr
    - huxiu
  fetch_interval: 300  # 5 分钟

analysis:
  model: ollama/llama3
  importance_threshold: 0.7

workflows:
  templates:
    - tech_research
    - market_monitor
    - risk_alert

push:
  channels:
    - feishu
    - telegram
  importance_threshold: 0.8

feedback:
  enabled: true
  optimize_interval: 3600  # 1 小时
```

## 📊 工作流模板

### 科技新闻调研 (tech_research)

触发条件：新闻分类 = 科技，重要性 > 0.7

```
1. 搜索相关 GitHub 项目
2. 分析项目 stars、活跃度
3. 生成调研报告
4. 推送到指定渠道
```

### 市场监控 (market_monitor)

触发条件：新闻分类 = 金融/市场

```
1. 提取关键数据
2. 更新监控仪表板
3. 异常波动告警
4. 生成日报
```

### 风险预警 (risk_alert)

触发条件：情感 = 负面，重要性 > 0.8

```
1. 提取风险因素
2. 评估影响范围
3. 生成应对建议
4. 高优先级推送
```

## 📈 成功指标

| 指标 | 目标值 |
|------|--------|
| 新闻抓取延迟 | < 5 分钟 |
| 工作流触发准确率 | > 85% |
| 任务执行成功率 | > 95% |
| 端到端延迟 | < 30 分钟 |

## 🧪 测试

```bash
# 单元测试
pytest tests/ -v

# 集成测试
python -m news_workflow test --integration

# 端到端测试
python -m news_workflow test --e2e
```

## 📝 许可证

MIT License
