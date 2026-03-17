# 知识卡片生成器 - 部署方案

**版本:** v1.0  
**时间:** 2026-03-12 09:10  
**目标:** 2-3 天内部署上线

---

## 🎯 部署目标

**用户需求:**
- 打开网站就能用
- 无需安装 Python
- 拖拽上传 PDF
- 下载知识卡片

**技术要求:**
- 支持 100MB PDF 上传
- 并发处理 10+ 用户
- API 配额管理 (CrossRef 600/小时)
- 临时文件清理

---

## 📦 部署方案对比

| 方案 | 平台 | 成本 | 时间 | 难度 |
|------|------|------|------|------|
| **方案 A** | Vercel + Serverless | $0 起步 | 1 天 | ⭐⭐ |
| **方案 B** | Railway.app | $5/月 | 2 小时 | ⭐ |
| **方案 C** | Render.com | $0 起步 | 2 小时 | ⭐ |
| **方案 D** | AWS EC2 | $3/月 | 1 天 | ⭐⭐⭐ |
| **方案 E** | 本地运行+ 内网穿透 | $0 | 30 分钟 | ⭐ |

---

## 🚀 推荐方案：Railway.app

**理由:**
- ✅ 一键部署 (连接 GitHub 自动部署)
- ✅ 免费额度$5/月 (够用)
- ✅ 支持 Flask
- ✅ 自动 HTTPS
- ✅ 域名免费

**成本:** $0-5/月 (初期免费)

---

## 📝 Railway 部署步骤

### 1. 准备文件

**需要创建:**
```
01-KNOWLEDGE-CARDS/
├── railway.json          # Railway 配置
├── requirements.txt      # 已有
├── core/
│   └── knowledge-card-webui.py
└── tests/
    └── test_pdfs/        # 测试文件
```

**railway.json:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python core/knowledge-card-webui.py --port $PORT --host 0.0.0.0",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

---

### 2. 修改 Web UI 代码

**修改:**
- 监听 `$PORT` 环境变量 (Railway 自动注入)
- 监听 `0.0.0.0` (允许外部访问)
- 禁用 debug 模式

**已修改:** ✅

---

### 3. 部署流程

```
1. 创建 GitHub 仓库
   ↓
2. 推送代码到 GitHub
   ↓
3. Railway 连接 GitHub
   ↓
4. 自动部署
   ↓
5. 获得域名：xxx.railway.app
```

**时间:** 30 分钟

---

## 🌐 部署后测试

**测试清单:**

| 测试项 | 方法 | 预期结果 |
|--------|------|----------|
| 首页访问 | 浏览器打开 | 显示上传界面 |
| 单文件上传 | 上传 1 篇 PDF | 生成 HTML 卡片 |
| 批量上传 | 上传 10 篇 PDF | 全部处理完成 |
| 文件下载 | 下载生成的 HTML | 文件完整 |
| 进度显示 | 观察进度条 | 实时更新 |
| API 配额 | 查看配额显示 | 正常显示 |

---

## 🔒 安全配置

### 环境变量

| 变量 | 说明 | 值 |
|------|------|-----|
| `MAX_CONTENT_LENGTH` | 最大上传 | 100MB |
| `CROSSREF_API_KEY` | CrossRef API | (可选) |
| `ARXIV_API_KEY` | arXiv API | (可选) |

### 使用限制

| 限制 | 值 | 说明 |
|------|-----|------|
| 免费用户 | 5 张/月 | 需登录 |
| Pro 用户 | 无限 | $9/月 |
| 单文件最大 | 100MB | 防止滥用 |

---

## 📊 监控方案

### 免费监控

- **Uptime:** Railway 自带
- **日志:** Railway Dashboard
- **错误:** 邮件通知

### 付费监控 ($10/月)

- **Sentry:** 错误追踪
- **Google Analytics:** 用户分析
- **UptimeRobot:** 外部监控

---

## 💰 成本估算

| 项目 | 免费 | 付费 |
|------|------|------|
| 托管 | Railway $0 | Railway $5 |
| 域名 | xxx.railway.app | 自定义$10/年 |
| API | CrossRef 免费 | - |
| 监控 | Railway 自带 | Sentry $10 |
| **总计** | **$0/月** | **$15-20/月** |

---

## 🗓️ 时间表

| 时间 | 任务 | 产出 |
|------|------|------|
| **Day 1 (今天)** | 准备部署文件 | railway.json + GitHub 仓库 |
| **Day 2 (明天)** | Railway 部署 + 测试 | 上线 xxx.railway.app |
| **Day 3 (后天)** | 找 3-5 用户试用 | 收集反馈 |

---

## ⚠️ 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| API 配额超限 | 中 | 高 | 缓存 + 限流 |
| 并发过高 | 低 | 中 | 队列处理 |
| 文件存储爆满 | 中 | 中 | 定时清理 |
| 恶意上传 | 低 | 高 | 文件类型检查 |

---

## 📝 下一步

**立即执行:**

1. [ ] 创建 GitHub 仓库
2. [ ] 创建 railway.json
3. [ ] 推送代码
4. [ ] Railway 部署
5. [ ] 测试上线

**然后:**

6. [ ] 找 3-5 用户试用
7. [ ] 收集反馈
8. [ ] 迭代优化

---

*部署方案完成。开始执行。*
