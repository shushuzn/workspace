# 飞书通信问题诊断报告

**时间:** 2026-03-17 13:45  
**问题:** 用户在飞书发消息没有响应

---

## 🔍 问题分类

### 情况 A: 发送消息到飞书 ❌ → ✅ 已修复

**症状:** 程序发送消息到飞书，但用户收不到

**检查结果:**
- ✅ App ID 配置正确：`cli_a93a6936eff81bcd`
- ✅ User ID 配置正确：`999d5a38`
- ✅ App Secret 配置正确
- ✅ API 调用成功
- ✅ 消息已发送（消息 ID: `om_x100b54bae3e62c88b38f900ca9d3902`）

**测试:**
```bash
python -c "from feishu_notification import FeishuNotifier; n = FeishuNotifier(); n.send_text('测试消息')"
```

**结果:** ✅ **发送功能正常**

---

### 情况 B: 飞书机器人接收消息 ❌ **这是真正的问题！**

**症状:** 用户在飞书给机器人发消息，但机器人没有响应

**根本原因:**
1. **机器人没有运行** ❌
   - `feishu-chatbot.py` 需要 24/7 运行在服务器上
   - 当前没有后台进程监听飞书消息

2. **Webhook 未配置** ❌
   - 飞书应用需要配置 Webhook URL
   - 需要公网可访问的服务器地址

3. **没有消息监听器** ❌
   - 聊天机器人需要监听飞书的 HTTP POST 请求
   - 需要 Flask/FastAPI 等 Web 服务器

---

## 📋 飞书双向通信架构

```
┌─────────────┐                    ┌──────────────┐
│   用户      │                    │  飞书服务器  │
│             │                    │              │
│ 1. 发送消息 │ ──────────────────>│  接收消息    │
└─────────────┘                    └──────┬───────┘
                                          │
                                          │ Webhook POST
                                          ▼
┌─────────────┐                    ┌──────────────┐
│  响应消息   │ <──────────────────│  你的机器人  │
│             │    HTTP 200 OK     │ (feishu-     │
└─────────────┘                    │  chatbot.py) │
                                   │              │
                                   │ 需要运行在：  │
                                   │ - 服务器     │
                                   │ - 有公网 IP  │
                                   │ - 开放端口   │
                                   └──────────────┘
```

---

## 🛠️ 解决方案

### 方案 1: 本地测试（推荐用于开发）

**使用 ngrok 暴露本地服务：**

1. **安装 ngrok:**
   ```bash
   choco install ngrok
   # 或下载：https://ngrok.com/download
   ```

2. **启动机器人:**
   ```bash
   cd 30-scripts-tools
   python feishu-chatbot.py
   ```

3. **暴露端口（假设机器人监听 8080）:**
   ```bash
   ngrok http 8080
   ```

4. **配置飞书应用:**
   - 登录飞书开发者后台
   - 应用管理 → 你的应用 → 事件订阅
   - 配置 Webhook URL: `https://xxxx.ngrok.io/webhook`

### 方案 2: 部署到服务器（生产环境）

**使用云服务器（阿里云/腾讯云/AWS）：**

1. **购买服务器** (最低配置即可)
2. **部署代码:**
   ```bash
   git clone <your-repo>
   cd 30-scripts-tools
   pip install -r requirements.txt
   ```

3. **配置防火墙:**
   - 开放端口 8080

4. **配置飞书 Webhook:**
   - Webhook URL: `http://<your-server-ip>:8080/webhook`

5. **后台运行:**
   ```bash
   nohup python feishu-chatbot.py &
   # 或使用 systemd/supervisor
   ```

### 方案 3: 使用云函数（无服务器）

**使用腾讯云云函数/阿里云函数计算：**

1. **打包代码为云函数**
2. **配置 API 网关触发器**
3. **将 API 网关 URL 配置为飞书 Webhook**

---

## 🔧 当前代码状态检查

### feishu-chatbot.py

**功能:** 聊天机器人主程序

**问题:** 
- ❌ 没有 Webhook 服务器实现
- ❌ 没有监听飞书消息的代码
- ❌ 需要添加 Flask/FastAPI 服务

**需要添加的代码:**
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def feishu_webhook():
    data = request.json
    # 处理飞书消息
    # 1. 验证签名
    # 2. 解析消息
    # 3. 生成回复
    # 4. 发送回复
    return jsonify({'code': 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

---

## 📝 立即行动清单

### 开发环境（本地测试）

- [ ] 安装 ngrok
- [ ] 检查 feishu-chatbot.py 是否有 webhook 实现
- [ ] 启动本地服务器
- [ ] 启动 ngrok 隧道
- [ ] 在飞书开发者后台配置 Webhook URL
- [ ] 测试发送消息给机器人

### 生产环境（服务器部署）

- [ ] 购买云服务器
- [ ] 部署 Python 环境
- [ ] 部署代码
- [ ] 配置防火墙
- [ ] 配置域名（可选）
- [ ] 在飞书开发者后台配置 Webhook URL
- [ ] 设置开机自启动

---

## 🎯 快速验证步骤

**验证发送功能（已正常）：**
```bash
cd 30-scripts-tools
python -c "from feishu_notification import FeishuNotifier; n = FeishuNotifier(); n.send_text('测试')"
```

**验证接收功能（需要配置）：**
1. 确保机器人正在运行
2. 在飞书中@机器人或发送消息
3. 检查机器人是否回复
4. 查看日志输出

---

## 📞 飞书开发者后台配置检查清单

登录：https://open.feishu.cn/app

### 应用配置
- [ ] App ID: `cli_a93a6936eff81bcd` ✅
- [ ] App Secret: 已配置 ✅
- [ ] 应用版本：已发布

### 权限配置
- [ ] 消息读写权限
- [ ] 事件订阅权限
- [ ] 机器人权限

### 事件订阅
- [ ] 启用事件订阅
- [ ] Webhook URL: 配置为你的服务器地址
- [ ] 订阅消息事件：`im.message.receive_v1`

### 机器人配置
- [ ] 启用机器人
- [ ] 配置机器人头像和名称
- [ ] 添加到群聊或私聊

---

## 🔍 故障排查

### 问题：收不到用户消息

**检查:**
1. Webhook URL 是否正确配置
2. 服务器是否可公网访问
3. 防火墙是否开放端口
4. 事件订阅是否启用
5. 是否订阅了正确的消息事件

### 问题：机器人回复失败

**检查:**
1. App Secret 是否正确
2. User ID 是否正确
3. 是否有发送消息权限
4. 日志中的错误信息

---

## 💡 建议

**对于个人开发/测试:**
- 使用 **ngrok** 快速搭建测试环境
- 本地运行机器人，ngrok 暴露公网 URL
- 免费、快速、适合开发

**对于生产环境:**
- 部署到 **云服务器**
- 配置 **域名 + HTTPS**
- 使用 **进程管理工具** (systemd/supervisor)
- 配置 **日志轮转**

**对于企业应用:**
- 考虑 **云函数** 方案（按需付费）
- 配置 **负载均衡**
- 实现 **高可用**

---

## 📚 相关文档

- [飞书开放平台](https://open.feishu.cn/document/)
- [事件订阅](https://open.feishu.cn/document/ukTMukTMukTM/ugjM14COyLjL0IzM)
- [消息发送](https://open.feishu.cn/document/ukTMukTMukTM/uYjNwYjL2YDM14SM2ATN)
- [机器人开发](https://open.feishu.cn/document/ukTMukTMukTM/uYjNwYjL2YDM14SM2ATN)

---

**结论:** 
- ✅ **发送功能正常** - 你可以发送消息到飞书
- ❌ **接收功能未配置** - 需要部署机器人并配置 Webhook

**下一步:** 选择部署方案（本地 ngrok / 云服务器 / 云函数），然后配置飞书 Webhook。
