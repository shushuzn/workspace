# 部署到 Render.com - 免费云端服务

**目标:** 将知识卡片 Web UI 部署到 Render，然后用 WebIntoApp 打包 APK

---

## 📋 步骤 1: 准备 Render 配置

### 创建 `render.yaml`

```yaml
services:
  - type: web
    name: knowledge-card-generator
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python core/knowledge-card-webui.py --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PORT
        value: 10000
```

### 创建 `.dockerignore`

```
__pycache__/
*.pyc
.git/
tests/
*.md
```

---

## 📋 步骤 2: 推送到 GitHub

```bash
# 确保代码已推送
cd knowledge-card-generator
git add .
git commit -m "Add Render config"
git push origin main
```

---

## 📋 步骤 3: Render 部署

### 1. 注册 Render

- 打开 https://render.com
- 用 GitHub 登录
- 免费计划

### 2. 创建 Web Service

```
1. Dashboard → New → Web Service
2. Connect GitHub repository
3. 选择 knowledge-card-generator
4. 配置:
   - Name: knowledge-card
   - Environment: Python
   - Build Command: pip install -r requirements.txt
   - Start Command: python core/knowledge-card-webui.py --host 0.0.0.0 --port $PORT
5. 点击 "Create Web Service"
```

### 3. 等待部署

- 首次部署：5-10 分钟
- 获得域名：`knowledge-card-xxx.onrender.com`

---

## 📋 步骤 4: WebIntoApp 打包 APK

### 1. 打开 WebIntoApp

- 网址：https://webintoapp.com

### 2. 配置

```
- URL: https://knowledge-card-xxx.onrender.com
- App Name: 知识卡片生成器
- Package Name: org.knowledgecard.app
- Version: 1.0.0
```

### 3. 打包

```
1. 点击 "Build"
2. 等待 5-10 分钟
3. 下载 APK
```

---

## 📱 步骤 5: 安装测试

```
1. 传输 APK 到手机
2. 允许"未知来源"
3. 安装
4. 打开使用
```

---

## ⚠️ 注意事项

### Render 免费计划限制

- ✅ 750 小时/月 (24/7 运行)
- ✅ 512MB 内存
- ⚠️ 30 分钟无访问自动休眠
- ⚠️ 冷启动约 30 秒

### 解决方案

- 使用 [UptimeRobot](https://uptimerobot.com) 每 20 分钟 ping 一次
- 或升级到付费计划 ($7/月)

---

## 💰 成本

| 服务 | 免费 | 付费 |
|------|------|------|
| Render | ✅ 750 小时/月 | $7/月 (不休眠) |
| WebIntoApp | ✅ 免费版 (有广告) | $20 (去广告) |

**总计:** $0 (测试) 或 $27/月 (生产)

---

*部署指南完成*
