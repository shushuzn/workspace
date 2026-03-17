# AI Research OS - FAQ 常见问题

**版本:** v1.0  
**创建时间:** 2026-03-05 03:35

---

## 📌 基础问题

### Q: AI Research OS 是什么？

A: 这是一个自动化的 AI 研究辅助系统，可以：
- 自动收集 arXiv/Twitter/HN/Reddit/Medium 内容
- 自动解析论文并生成笔记
- AI 增强分析 (评分/趋势/推荐)
- 系统监控与优化

### Q: 如何开始使用？

A: 参考 [[USAGE-GUIDE.md]] 使用文档，从信息收集脚本开始。

### Q: 需要哪些依赖？

A: 
- Python 3.13+
- Docker Desktop (可选，用于 EverMemOS)
- Git
- n8n (定时任务调度)

---

## 🔧 技术问题

### Q: arXiv 收集失败怎么办？

A: 
1. 检查网络连接
2. 验证 arXiv API 可访问性
3. 查看 logs/ 目录下的错误日志

### Q: PDF 下载失败率高？

A: 
1. 检查网络连接
2. 降低并发数 (修改 MAX_WORKERS)
3. 添加重试机制

### Q: 如何添加新的信息源？

A: 
1. 参考 twitter-watcher.py 模板
2. 创建新的 watcher 脚本
3. 配置定时任务

---

## 📊 数据问题

### Q: 如何查看收集的数据？

A: 数据保存在 `D:\obsidian\Vault\` 各子目录中：
- Arxiv/ - arXiv 论文
- Twitter/ - Twitter 推文
- HackerNews/ - HN 文章
- 等等

### Q: 如何清理重复数据？

A: 运行 `py data-quality-checker.py` 检查并清理。

### Q: 如何备份数据？

A: 使用 Git 同步到 obsidian-sync 仓库，或手动备份 D:\obsidian\Vault\

---

## 🤖 AI 功能

### Q: 论文质量评分准确吗？

A: 当前为简化版 (基于关键词匹配)，准确率约 70-80%。未来可集成更复杂的 AI 模型。

### Q: 如何改进趋势预测？

A: 
1. 增加历史数据
2. 使用更复杂的模型 (LSTM/Transformer)
3. 人工校准

---

## 📞 其他问题

### Q: 如何贡献代码？

A: 欢迎提交 PR 到 GitHub 仓库！

### Q: 有社区或讨论群吗？

A: 暂无，计划中。

### Q: 如何联系作者？

A: 通过 GitHub Issues 或 Feishu。

---

*最后更新：2026-03-05 03:35*
