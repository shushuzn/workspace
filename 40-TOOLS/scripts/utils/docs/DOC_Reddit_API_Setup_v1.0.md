# Reddit API 配置指南

**创建时间:** 2026-03-05 02:57  
**任务:** 4.1 Reddit API 认证配置  
**状态:** ⏳ 待申请

---

## 🔑 申请步骤

### 1. 创建 Reddit 账号
- 访问 https://www.reddit.com/register
- 完成注册和邮箱验证

### 2. 创建 Reddit App
- 访问 https://www.reddit.com/prefs/apps
- 点击 "create another app..."
- 选择 "script" 类型
- 填写:
  - name: OpenClaw-Research-Bot
  - about url: (可选)
  - redirect uri: http://localhost:8080

### 3. 获取凭证
- **client_id:** 显示在应用下方 (14 字符)
- **client_secret:** 点击 "edit" 查看
- **user_agent:** 自定义标识

### 4. 配置到项目

创建 `.env` 文件:
```bash
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=OpenClaw-Research-Bot/1.0 by /u/yourusername
```

### 5. 更新脚本

修改 `reddit-watcher.py`:
```python
import praw

reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT')
)
```

---

## ⏱️ 预计时间

| 步骤 | 用时 |
|------|------|
| 账号注册 | 5 分钟 |
| App 创建 | 2 分钟 |
| 配置集成 | 10 分钟 |
| **总计** | **17 分钟** |

---

## 📝 当前状态

- [ ] Reddit 账号注册
- [ ] App 创建
- [ ] 凭证获取
- [ ] 脚本集成
- [ ] 测试验证

---

*最后更新：2026-03-05 02:57*
