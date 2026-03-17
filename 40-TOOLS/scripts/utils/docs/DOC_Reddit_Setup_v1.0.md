# Reddit 监听配置文档

**创建时间:** 2026-03-05 02:50  
**任务:** 4.1-4.5 Reddit 监听  
**状态:** ⚠️ 需要 API 认证

---

## ⚠️ 当前问题

**Reddit API 封锁:**
- 无需认证的 API 访问已被封锁
- 返回 403 Blocked 错误
- 需要正式 Reddit API 认证

---

## 🔧 解决方案

### 方案 A: Reddit API 正式认证 (推荐)

**步骤:**
1. 访问 https://www.reddit.com/prefs/apps
2. 创建应用 (选择 "script")
3. 获取 `client_id` 和 `client_secret`
4. 使用 OAuth2 认证

**配置:**
```yaml
reddit:
  client_id: "your_client_id"
  client_secret: "your_client_secret"
  user_agent: "OpenClaw-Research-Bot/1.0 by /u/yourusername"
```

**优点:**
- ✅ 官方支持
- ✅ 稳定可靠
- ✅ 完整功能

**缺点:**
- ⚠️ 需要 Reddit 账号
- ⚠️ 申请需要时间

---

### 方案 B: 第三方 RSS 服务

**选项:**
- https://www.reddit.com/r/MachineLearning/.rss
- 使用 RSS 阅读器

**优点:**
- ✅ 无需 API Key
- ✅ 立即可用

**缺点:**
- ⚠️ 功能有限
- ⚠️ 可能不稳定

---

### 方案 C: 模拟数据 (临时)

**用途:** 测试流程，等待 API 认证

**实现:**
- 创建示例帖子数据
- 验证分类和专家识别逻辑
- 准备正式集成

---

## 📊 预期效果

**监听版块:**
- r/MachineLearning
- r/artificial
- r/deeplearning
- r/reinforcementlearning
- r/LocalLLaMA

**每日收集:**
- 帖子：~100 篇
- 高质量讨论：~20 篇
- 识别专家：~10 人

---

## ⏭️ 下一步

1. **立即:** 使用模拟数据测试流程
2. **短期:** 申请 Reddit API 认证
3. **长期:** 正式集成到定时任务

---

*最后更新：2026-03-05 02:50*
