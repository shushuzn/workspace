# X-Tweet-Fetcher 技能集成

**安装日期:** 2026-03-07  
**来源:** https://github.com/ythx-101/x-tweet-fetcher  
**版本:** Latest

---

## ✅ 安装状态

| 项目 | 状态 |
|------|------|
| 技能克隆 | ✅ 完成 |
| 文件检查 | ✅ 完成 |
| 帮助测试 | ✅ 通过 |
| Camofox | ⏸️ 未安装 (可选) |

---

## 📁 文件结构

```
skills/x-tweet-fetcher/
├── SKILL.md                    # 技能文档
├── README.md                   # 完整文档
├── scripts/
│   ├── fetch_tweet.py          # 主抓取器
│   ├── fetch_china.py          # 中文平台抓取
│   ├── camofox_client.py       # Camofox 客户端
│   └── x_discover.py           # X 发现功能
└── ...
```

---

## 🔧 功能

### 无需依赖 (基础功能)
- ✅ 单条推文抓取 (FxTwitter API)
- ✅ 文本/JSON 输出
- ✅ 长推文支持 (Twitter Blue)
- ✅ X 文章抓取

### 需要 Camofox (高级功能)
- ⏸️ 回复链抓取
- ⏸️ 用户时间线
- ⏸️ 中文平台 (微博/B 站/CSDN/微信)
- ⏸️ Google 搜索 (无 API)

---

## 🚀 使用示例

### 基础用法 (无需 Camofox)

```powershell
# 抓取单条推文 (JSON)
cd D:\OpenClaw\workspace\skills\x-tweet-fetcher\scripts
py fetch_tweet.py --url "https://x.com/user/status/123456"

# 人类可读格式
py fetch_tweet.py --url "https://x.com/user/status/123456" --text-only

# 格式化 JSON
py fetch_tweet.py --url "https://x.com/user/status/123456" --pretty
```

### 高级用法 (需要 Camofox)

```powershell
# 抓取回复链
py fetch_tweet.py --url "https://x.com/user/status/123456" --replies

# 用户时间线
py fetch_tweet.py --user "username" --limit 50

# 中文平台
py fetch_china.py --url "https://weibo.com/..."
```

---

## 📋 集成到工作流

### 1. 添加到 HEARTBEAT

```markdown
### 社交媒体监控
- [ ] 监控 AI 领域专家动态
- [ ] 跟踪热门话题
- [ ] 归档重要推文
```

### 2. 集成到数据收集

```python
# 添加到 40-arxiv 类似的目录
# 41-x-tweets/
```

### 3. 定时任务

```powershell
# 添加到任务计划程序
# 每日运行监控
```

---

## ⚠️ 注意事项

1. **遵守 X/Twitter 使用条款**
2. **注意速率限制**
5. **尊重隐私**
4. **不要滥用**

---

## 🔍 下一步

1. ⏸️ 安装 Camofox (可选，用于高级功能)
2. ⏸️ 测试基础功能
3. ⏸️ 集成到数据收集工作流
4. ⏸️ 设置定时监控

---

*Claw @ OpenClaw*
