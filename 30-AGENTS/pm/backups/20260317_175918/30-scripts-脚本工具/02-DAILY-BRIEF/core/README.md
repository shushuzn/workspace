# 每日简报生成器

自动生成每日研究简报，聚合 arXiv/Medium/GitHub/HackerNews 数据。

---

## 🚀 快速开始

```bash
# 生成昨日简报
py daily-brief.py

# 生成指定日期
py daily-brief.py --date 2026-03-10

# 发送到 Feishu
py daily-brief.py --send

# 查看帮助
py daily-brief.py --help
```

---

## 📋 功能特性

- ✅ arXiv 论文收集统计
- ✅ Medium 文章分析
- ✅ GitHub 提交状态
- ✅ HackerNews 热门
- ✅ 天气信息
- ✅ 日历事件
- ✅ 历史对比
- ✅ 7 天趋势图表
- ✅ Feishu 推送

---

## ⚙️ 配置

### 定时任务 (Windows)

```powershell
# 以管理员身份运行
schtasks /create /tn "DailyBrief-Feishu" /tr "py D:\OpenClaw\workspace\30-scripts\daily-brief.py --send" /sc weekly /st 08:00 /d MON,TUE,WED,THU,FRI /mo 1 /ru SYSTEM /f
```

### Feishu 推送

简报自动加入发送队列，由 `process-feishu-queue.py` 处理。

---

## 📁 输出文件

- **简报:** `21-reports/daily-briefs/brief-YYYY-MM-DD.md`
- **发送队列:** `13-memory/feishu-queue.json`
- **发送日志:** `21-reports/feishu-send-log.jsonl`

---

## 🐛 故障排查

**问题:** GitHub 状态检查失败

**解决:** 确认在 Git 仓库目录运行，或检查网络连接。

**问题:** 天气数据不可用

**解决:** 检查网络连接，wttr.in 可能被临时拦截。

---

*最后更新：2026-03-10*
