# 📰 新闻源配置

**创建日期:** 2026-03-27

---

## 预设分类与来源

| 分类 | 来源 | URL |
|------|------|-----|
| **科技** | Hacker News | https://news.ycombinator.com/ |
| **科技** | TechCrunch | https://techcrunch.com/ |
| **科技** | Verge | https://www.theverge.com/ |
| **AI** | AI News | https://www.artificialintelligence-news.com/ |
| **AI** | Hugging Face Blog | https://huggingface.co/blog |
| **财经** | 华尔街见闻 | https://wallstreetcn.com/ |
| **财经** | 36氪 | https://36kr.com/ |
| **财经** | Bloomberg | https://www.bloomberg.com/ |
| **开发** | DEV Community | https://dev.to/ |
| **开发** | Reddit r/programming | https://reddit.com/r/programming |
| **安全** | The Hacker News | https://thehackernews.com/ |
| **安全** | Krebs on Security | https://krebsonsecurity.com/ |

---

## 推荐快捷新闻源组合

### 🖥️ 开发者日常
```
Hacker News + DEV + Reddit r/programming
```
覆盖: 技术趋势、社区热点、开源项目

### 🤖 AI 爱好者
```
Hugging Face + AI News + Hacker News
```
覆盖: 模型发布、论文解读、AI 应用

### 💼 商业/财经
```
36氪 + 华尔街见闻 + Bloomberg
```
覆盖: 国内商业动态、全球财经、创投

### 🔒 安全关注
```
The Hacker News + Krebs + Reddit/netsec
```
覆盖: 漏洞披露、攻击事件、安全研究

---

## 自定义配置

### 添加自定义 RSS 源

```yaml
news_sources:
  custom:
    - name: "我的关注"
      url: "https://example.com/feed.xml"
      category: "tech"
      priority: 1
```

### 设置推送频率

```yaml
news_schedule:
  quick_digest: "0 8,18 * * *"  # 早8点、晚6点
  deep_scan: "0 20 * * 5"       # 周五晚深度分析
  breaking: "0 9-21 * * 1-5"   # 工作日每小时检查
```

---

## News Curator Agent 配置

```markdown
## Configuration
- NEWS_SOURCES: ["hackernews", "techcrunch", "36kr", "reddit"]
- CATEGORIES: ["ai", "tech", "finance"]
- MAX_ITEMS: 20
- LANGUAGE: "zh-CN"
- TIMEZONE: "Asia/Shanghai"
```

---

## 快捷命令

| 命令 | 执行 |
|------|------|
| `新闻` | 获取今日热点 |
| `科技新闻` | 科技行业资讯 |
| `AI 资讯` | AI/ML 最新动态 |
| `财经新闻` | 商业财经资讯 |
| `安全资讯` | 安全漏洞新闻 |
