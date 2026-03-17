# 🚀 Innovator Dashboard 部署指南

## 📦 部署包内容
- `33-dashboard/` - 仪表板文件 (index.html, README.md)
- `deploy-dashboard.sh` - 自动部署脚本
- `innovator-dashboard-deploy.tar.gz` - 打包文件

---

## 🔧 方案 A: 自动部署 (推荐)

### 步骤 1: SSH 连接服务器
```bash
ssh root@8.208.30.28
```
输入密码后进入服务器。

### 步骤 2: 上传文件
**方法 1 - 使用 scp (本地执行):**
```bash
scp -r D:\OpenClaw\workspace\33-dashboard\* root@8.208.30.28:/var/www/innovator/
```

**方法 2 - 使用 WinSCP:**
1. 下载 WinSCP: https://winscp.net/
2. 主机名：`8.208.30.28`
3. 用户名：`root`
4. 密码：(你的服务器密码)
5. 上传 `33-dashboard/` 到 `/var/www/innovator/`

### 步骤 3: 配置 nginx
SSH 连接后执行：
```bash
# 创建目录
mkdir -p /var/www/innovator

# 设置权限
chmod -R 755 /var/www/innovator

# 创建 nginx 配置
cat > /etc/nginx/sites-available/innovator << 'EOF'
server {
    listen 8443 ssl http2;
    server_name innovator.felixxii.xyz;
    
    ssl_certificate /etc/letsencrypt/live/felixxii.xyz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/felixxii.xyz/privkey.pem;
    
    root /var/www/innovator;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/innovator /etc/nginx/sites-enabled/

# 测试并重启 nginx
nginx -t
systemctl reload nginx
```

---

## 🌐 方案 B: 手动部署 (无 SSH)

### 使用服务器控制面板
如果有服务器控制面板 (如宝塔、cPanel)：
1. 登录控制面板
2. 文件管理 → 上传 `33-dashboard/` 到 `/var/www/innovator/`
3. 网站管理 → 添加站点 → `innovator.felixxii.xyz:8443`
4. SSL → Let's Encrypt 自动申请

---

## ✅ 验证部署

部署完成后访问：
- **HTTPS:** https://innovator.felixxii.xyz:8443
- **HTTP:** http://8.208.30.28:8443

---

## 🔒 SSL 证书配置

### 申请 Let's Encrypt 证书
```bash
# SSH 连接后执行
apt update
apt install certbot python3-certbot-nginx -y

# 申请证书
certbot --nginx -d innovator.felixxii.xyz

# 自动续期
certbot renew --dry-run
```

---

## 📊 Cloudflare DNS 配置

登录 Cloudflare 添加 DNS 记录：

| 类型 | 名称 | 内容 | 代理 |
|------|------|------|------|
| A | @ | 8.208.30.28 | ✅ 已代理 |
| A | www | 8.208.30.28 | ✅ 已代理 |
| CNAME | innovator | felixxii.xyz | ✅ 已代理 |
| CNAME | api | felixxii.xyz | ✅ 已代理 |

---

## 🐛 故障排查

### 1. 无法访问
```bash
# 检查 nginx 状态
systemctl status nginx

# 检查防火墙
ufw status
ufw allow 8443/tcp
```

### 2. SSL 错误
```bash
# 检查证书
ls -la /etc/letsencrypt/live/felixxii.xyz/

# 重新申请
certbot --nginx -d innovator.felixxii.xyz --force-renewal
```

### 3. 权限问题
```bash
chown -R www-data:www-data /var/www/innovator
chmod -R 755 /var/www/innovator
```

---

## 📞 需要帮助？

提供以下信息：
1. SSH 密码 (私信)
2. 或者服务器控制面板访问权限
3. 或者允许我使用 SSH 密钥部署

---

**创建时间:** 2026-03-14 17:30  
**版本:** 1.0  
**状态:** Ready for Deployment
