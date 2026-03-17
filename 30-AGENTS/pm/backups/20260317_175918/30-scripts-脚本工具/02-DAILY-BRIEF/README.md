# daily-brief - 日常简报系统

**版本:** v3.0 (2026-03-12)  
**最后更新:** 2026-03-12  
**位置:** `30-scripts-脚本工具/02-DAILY-BRIEF/`  
**状态:** ✅ 生产就绪

---

## 📋 一句话描述

自动化日常简报系统，聚合 arXiv/Medium/HackerNews/GitHub 动态，支持 Feishu 推送和 Markdown 日历集成。

---

## 🚀 快速开始

### 安装依赖

```bash
# 进入目录
cd 30-scripts/02-DAILY-BRIEF

# 安装依赖
pip install -r requirements.txt
```

**requirements.txt:**
```
requests>=2.28.0
feedparser>=6.0.0
pyyaml>=6.0
python-dateutil>=2.8.0
```

### 基础用法

```bash
# 生成今日简报
python daily-brief.py --date today

# 生成指定日期简报
python daily-brief.py --date 2026-03-12

# 生成并发送到 Feishu
python daily-brief.py --date today --send-feishu
```

### 预期输出

```
📅 日常简报 - 2026-03-12

📚 arXiv 论文 (5 篇)
  - Paper 1: Title...
  - Paper 2: Title...

📝 Medium 文章 (3 篇)
  - Article 1: Title...
  - Article 2: Title...

💻 HackerNews (5 条)
  - News 1: Title...
  - News 2: Title...

🔧 GitHub 动态 (3 条)
  - Repo 1: Update...
  - Repo 2: Update...

📊 域名段位评估
  - DeepLearning: 黑铁 717 级
  - LIG: 黑铁 473 级
```

**预计耗时：** ~2 分钟 (生成简报)

---

## ✨ 功能特性

- ✅ **多源聚合** - arXiv/Medium/HackerNews/GitHub
- ✅ **自动去重** - 基于标题/URL 去重
- ✅ **优先级评分** - 智能排序高价值内容
- ✅ **Feishu 推送** - 自动发送到飞书
- ✅ **Markdown 日历** - 日历集成支持
- ✅ **7 天趋势** - ASCII 图表可视化
- ✅ **历史对比** - 日/周环比分析
- ✅ **敏感内容过滤** - 自动跳过敏感论文

---

## 📖 使用示例

### 示例 1: 基础用法 - 生成今日简报

**场景:** 每天早上 7 点自动生成简报

```bash
# 手动生成
python daily-brief.py --date today

# 输出到文件
python daily-brief.py --date today --output brief-20260312.md

# 查看生成的简报
cat brief-20260312.md
```

**预期输出:**
```markdown
# 日常简报 - 2026-03-12

## 📚 arXiv 论文 (5 篇)

### 1. Paper Title 1
- **作者:** Author et al.
- **链接:** https://arxiv.org/abs/xxxx
- **摘要:** ...

### 2. Paper Title 2
...

## 📝 Medium 文章 (3 篇)
...

## 💻 HackerNews (5 条)
...
```

**说明:** 适合日常手动生成简报

---

### 示例 2: 进阶用法 - 配置定时任务

**场景:** 每天自动运行，无需手动干预

**Windows Task Scheduler:**
```powershell
# 创建定时任务 (每天 7AM)
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "30-scripts/02-DAILY-BRIEF/daily-brief.py --date today"
$trigger = New-ScheduledTaskTrigger -Daily -At 7am
Register-ScheduledTask -TaskName "Daily-Brief" `
  -Action $action -Trigger $trigger -RunLevel Highest
```

**Linux Cron:**
```bash
# 编辑 crontab
crontab -e

# 添加任务 (每天 7AM)
0 7 * * * cd /path/to/workspace && python 30-scripts/02-DAILY-BRIEF/daily-brief.py --date today
```

**说明:** 适合自动化日常简报

---

### 示例 3: 高级用法 - 自定义数据源

**场景:** 添加自定义 RSS 源或 API

**配置文件 (config.yaml):**
```yaml
sources:
  arxiv:
    enabled: true
    categories:
      - cs.AI
      - cs.LG
      - physics.nanotech
  
  medium:
    enabled: true
    tags:
      - artificial-intelligence
      - machine-learning
  
  hackernews:
    enabled: true
    min_points: 100
  
  github:
    enabled: true
    repos:
      - openclaw/openclaw
      - user/repo2
  
  custom:
    - name: "My Blog"
      type: rss
      url: "https://example.com/feed.xml"
```

**运行:**
```bash
python daily-brief.py --config config.yaml
```

**说明:** 适合个性化定制简报内容

---

## 🔧 配置参数

### 命令行参数

| 参数 | 类型 | 默认值 | 必需 | 说明 |
|------|------|--------|------|------|
| `--date` | str | `today` | ❌ | 简报日期 (YYYY-MM-DD) |
| `--output` | str | `brief-YYYYMMDD.md` | ❌ | 输出文件路径 |
| `--send-feishu` | flag | `False` | ❌ | 发送到飞书 |
| `--config` | str | `config.yaml` | ❌ | 配置文件路径 |
| `--verbose` | flag | `False` | ❌ | 详细输出模式 |

### 配置文件参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `sources.arxiv.enabled` | bool | `true` | 启用 arXiv |
| `sources.arxiv.categories` | list | `[]` | arXiv 分类 |
| `sources.medium.enabled` | bool | `true` | 启用 Medium |
| `sources.medium.tags` | list | `[]` | Medium 标签 |
| `sensitivity.filter` | bool | `true` | 敏感内容过滤 |
| `output.format` | str | `markdown` | 输出格式 |

---

## 📊 API 参考

### `DailyBrief(date, config)`

**功能:** 创建简报生成器实例

**参数:**
- `date` (str): 日期 (YYYY-MM-DD 格式)
- `config` (dict): 配置字典

**返回:** DailyBrief 实例

**示例:**
```python
from daily_brief import DailyBrief

brief = DailyBrief("2026-03-12", config={
    "sources": {"arxiv": {"enabled": True}}
})
```

---

### `brief.fetch_arxiv()`

**功能:** 获取 arXiv 论文列表

**返回:** List[Dict] - 论文列表

**示例:**
```python
papers = brief.fetch_arxiv()
print(f"获取到 {len(papers)} 篇论文")
```

---

### `brief.fetch_medium()`

**功能:** 获取 Medium 文章列表

**返回:** List[Dict] - 文章列表

**示例:**
```python
articles = brief.fetch_medium()
```

---

### `brief.generate_markdown()`

**功能:** 生成 Markdown 格式简报

**返回:** str - Markdown 内容

**示例:**
```python
md = brief.generate_markdown()
with open("brief.md", "w") as f:
    f.write(md)
```

---

### `brief.send_feishu(webhook_url)`

**功能:** 发送到飞书 Webhook

**参数:**
- `webhook_url` (str): 飞书 Webhook URL

**返回:** bool - 发送是否成功

**示例:**
```python
success = brief.send_feishu("https://open.feishu.cn/open-apis/bot/v2/hook/xxx")
```

---

## 🐳 Docker 部署

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY 02-DAILY-BRIEF/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY 02-DAILY-BRIEF/ ./02-DAILY-BRIEF/

# 定时任务 (每天 7AM)
RUN apt-get update && apt-get install -y cron
COPY cron-daily-brief /etc/cron.d/daily-brief
RUN chmod 0644 /etc/cron.d/daily-brief && crontab /etc/cron.d/daily-brief

CMD ["cron", "-f"]
```

### 运行容器

```bash
# 构建镜像
docker build -t daily-brief .

# 运行 (后台定时任务)
docker run -d --name daily-brief daily-brief
```

---

## 📊 API 参考

### `DailyBrief(date, config)`

**功能:** 创建简报生成器实例

**参数:**
- `date` (str): 日期 (YYYY-MM-DD)
- `config` (dict): 配置字典

**返回:** DailyBrief 实例

**示例:**
```python
from daily_brief import DailyBrief

brief = DailyBrief("2026-03-12", config={
    "sources": {"arxiv": {"enabled": True}}
})
```

---

### `brief.fetch_arxiv()`

**功能:** 获取 arXiv 论文列表

**返回:** List[Dict] - 论文列表

**示例:**
```python
papers = brief.fetch_arxiv()
print(f"获取到 {len(papers)} 篇论文")
```

---

### `brief.fetch_medium()`

**功能:** 获取 Medium 文章列表

**返回:** List[Dict] - 文章列表

**示例:**
```python
articles = brief.fetch_medium()
```

---

### `brief.generate_markdown()`

**功能:** 生成 Markdown 格式简报

**返回:** str - Markdown 内容

**示例:**
```python
md = brief.generate_markdown()
with open("brief.md", "w") as f:
    f.write(md)
```

---

### `brief.send_feishu(webhook_url)`

**功能:** 发送到飞书 Webhook

**参数:**
- `webhook_url` (str): 飞书 Webhook URL

**返回:** bool - 发送是否成功

**示例:**
```python
success = brief.send_feishu("https://open.feishu.cn/open-apis/bot/v2/hook/xxx")
```

---

## ❓ FAQ

### Q1: 简报生成失败怎么办？

**A:** 
1. 检查网络连接
2. 检查 API 密钥 (如需要)
3. 启用 `--verbose` 查看详细错误
4. 查看日志文件 `logs/daily-brief.log`

---

### Q2: 如何添加新的数据源？

**A:** 
1. 在 `config.yaml` 中添加数据源配置
2. 实现对应的 `fetch_xxx()` 方法
3. 在 `generate_markdown()` 中添加渲染逻辑

---

### Q3: 敏感内容过滤如何工作？

**A:** 
基于关键词匹配：
- 生物武器、化学武器、恐怖主义等
- 命中后自动跳过，记录跳过日志

---

### Q4: 如何修改简报发送时间？

**A:** 
修改定时任务配置：
- Windows: 任务计划程序 → 修改触发器
- Linux: `crontab -e` → 修改时间

---

### Q5: 简报可以自定义模板吗？

**A:** 可以。修改 `templates/brief-template.md` 文件。

---

### Q6: 支持哪些输出格式？

**A:** 
- Markdown (默认)
- HTML (需配置)
- JSON (机器可读)
- Plain Text (简化版)

---

### Q7: 如何查看历史简报？

**A:** 
```bash
# 列出所有历史简报
ls brief-*.md

# 查看指定日期
cat brief-20260310.md
```

---

### Q8: 简报数据会保存多久？

**A:** 
默认永久保存。可配置自动清理：
```yaml
retention:
  days: 30  # 保留 30 天
```

---

## 🔗 相关资源

- [arXiv API 文档](https://arxiv.org/help/api) - 论文数据源
- [Medium RSS](https://medium.com/feed/) - 文章数据源
- [HackerNews API](https://github.com/HackerNews/API) - 技术新闻
- [Feishu Webhook](https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN) - 推送集成

---

## 📝 更新日志

### v3.0 (2026-03-12)
- ✨ 敏感内容过滤
- ✨ 域名段位集成
- ✨ 7 天趋势图表
- ✨ 历史对比分析

### v2.0 (2026-03-10)
- ✨ Feishu 推送
- ✨ Markdown 日历
- ✨ 优先级评分

### v1.0 (2026-03-08)
- ✨ 初始版本
- ✨ arXiv/Medium/HN 聚合

---

## 🧪 测试

### 运行测试

```bash
cd 30-scripts/02-DAILY-BRIEF

# 测试数据获取
python tests/test_sources.py

# 测试简报生成
python tests/test_generate.py
```

### 测试覆盖

- ✅ arXiv API 获取
- ✅ Medium RSS 解析
- ✅ HackerNews API
- ✅ GitHub API
- ✅ Markdown 生成
- ✅ Feishu 推送

---

## 🔒 安全说明

### API 密钥管理

**不要将 API 密钥提交到 Git:**

```bash
# 使用环境变量
export GITHUB_TOKEN="your_token_here"
export FEISHU_WEBHOOK="your_webhook_here"

# 或使用 .env 文件 (已加入.gitignore)
echo "GITHUB_TOKEN=your_token" > .env
```

### 敏感内容过滤

**自动过滤类别:**
- 生物武器、化学武器
- 恐怖主义相关内容
- 个人隐私数据
- 军事机密

**过滤日志:** 记录跳过内容，不存储详情

---

## 📝 Changelog

### v3.0 (2026-03-12)
- ✨ 敏感内容过滤
- ✨ 域名段位集成
- ✨ 7 天趋势图表
- ✨ 历史对比分析

### v2.0 (2026-03-10)
- ✨ Feishu 推送
- ✨ Markdown 日历
- ✨ 优先级评分

### v1.0 (2026-03-08)
- ✨ 初始版本
- ✨ arXiv/Medium/HN 聚合

---

## 📄 许可证

MIT License - 详见 [LICENSE](../../LICENSE)

---

## 👥 作者

- Claw - AI Research Agent
- 维护者：Claw

---

**最后测试:** 2026-03-12  
**测试状态:** ✅ 所有示例通过测试  
**测试环境:** Windows 11, Python 3.11

**模板验证:** ✅ 使用 README-TEMPLATE.md 创建，验证通过
