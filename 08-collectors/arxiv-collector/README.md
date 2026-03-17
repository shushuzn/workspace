# arXiv 论文自动收集器

**功能:** 每日自动抓取 arXiv 最新论文，存储元数据，支持关键词订阅

---

## 🎯 功能

- [ ] 关键词订阅管理
- [ ] 每日自动抓取 arXiv API
- [ ] 论文元数据存储 (JSON)
- [ ] 新论文去重
- [ ] 与 OpenClaw 集成

---

## 🚀 快速开始

```bash
# 安装依赖
npm install

# 配置关键词
编辑 config.json

# 运行抓取
node arxiv-collector.js

# 查看结果
查看 data/papers/ 目录
```

---

## 📁 项目结构

```
41-arxiv-collector/
├── arxiv-collector.js    # 主程序
├── config.json           # 关键词配置
├── package.json          # 依赖
├── data/
│   └── papers/          # 抓取的论文元数据
└── README.md            # 本文档
```

---

## 🔧 配置

### config.json
```json
{
  "keywords": [
    "graph neural network",
    "transformer architecture",
    "reinforcement learning"
  ],
  "maxResults": 50,
  "sortBy": "submittedDate",
  "sortOrder": "descending"
}
```

---

## 📊 API 限制

- arXiv API: 每 3 秒最多 1 次请求
- 建议：添加延迟，避免被封

---

*Created:* 2026-03-13
*Status:* 🚧 开发中
