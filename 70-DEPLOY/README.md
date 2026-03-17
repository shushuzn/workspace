# 🚀 Deploy Scripts - 部署脚本索引

**位置:** `02-deploy-scripts/`  
**用途:** 所有部署、安装、配置脚本的集中管理

---

## 📁 文件夹结构

```
02-deploy-scripts/
├── scripts/      # 部署执行脚本 (6 个)
├── configs/      # 配置脚本 (6 个)
├── installers/   # 安装脚本 (3 个)
└── README.md     # 本索引
```

---

## 🗂️ 文件清单

### 📦 部署脚本 (`scripts/`) - 6 个

| 文件 | 用途 | 目标 |
|------|------|------|
| `deploy-dashboard-v3.bat` | 部署仪表盘 v3 | Windows |
| `deploy-dashboard-v3.py` | 部署仪表盘 v3 | Python |
| `deploy-dashboard.sh` | 部署仪表盘 v3 | Linux/Mac |
| `deploy-to-server.py` | 部署到服务器 | 通用 |
| `deploy-innovator.py` | 部署创新者系统 | 通用 |
| `deploy-stock-v11-server.sh` | 部署股票分析器 v11 | Linux |

**使用示例:**
```bash
# 部署仪表盘 v3
python scripts/deploy-dashboard-v3.py

# 部署到服务器
python scripts/deploy-to-server.py
```

---

### ⚙️ 配置脚本 (`configs/`) - 6 个

| 文件 | 用途 |
|------|------|
| `configure-domain.py` | 配置域名 |
| `configure-main-domain.py` | 配置主域名 |
| `configure-nginx.py` | 配置 Nginx |
| `reconfigure-nginx.py` | 重新配置 Nginx |
| `update-main-domain.py` | 更新主域名 |
| `replace-main-config.py` | 替换主配置 |

**使用示例:**
```bash
# 配置域名
python configs/configure-domain.py

# 配置 Nginx
python configs/configure-nginx.py
```

---

### 📥 安装脚本 (`installers/`) - 3 个

| 文件 | 用途 |
|------|------|
| `install-cli.bat` | 安装 CLI 工具 |
| `install-dashboard-v4.bat` | 安装仪表盘 v4 |
| `setup-system-env.bat` | 设置系统环境 |

**使用示例:**
```bash
# 安装 CLI
installers\install-cli.bat

# 设置环境
installers\setup-system-env.bat
```

---

**最后更新:** 2026-03-17  
**维护者:** Claw 🐾
