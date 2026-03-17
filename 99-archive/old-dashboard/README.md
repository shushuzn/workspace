# 📊 Dashboard - 统一仪表盘

**位置:** `03-dashboard/`  
**版本:** v4.1-Persona (7 人格增强版)  
**状态:** ✅ 单一精简版

---

## 🎯 精简策略

**保留:**
- ✅ **api/** - 后端 API 服务器
- ✅ **web/** - 前端页面

**已迁移:**
- → `02-deploy-scripts/dashboard/` - 启动脚本 (*.bat)
- → `12-tests/dashboard/` - 测试脚本
- → `13-docs-reports/dashboard/` - 文档

**已归档:**
- → `99-archive/old-dashboards/33-dashboard/` - 旧版本仪表盘
- → `99-archive/old-dashboards/` - 其他旧版本文件

---

## 📁 文件夹结构

```
03-dashboard/
├── api/
│   └── dashboard-api-v4-persona.py   ← 唯一 API
├── web/
│   └── index-with-theme.html         ← 唯一前端
└── README.md                         ← 本索引
```

**相关文件位置:**
- **启动脚本:** `02-deploy-scripts/dashboard/*.bat`
- **测试脚本:** `12-tests/dashboard/`
- **文档:** `13-docs-reports/dashboard/`

---

## 🚀 快速启动

### 方式 1: 根目录启动 (推荐)
```bash
# 工作区根目录
start-dashboard.bat
```

### 方式 2: 部署脚本目录
```bash
# 部署脚本目录
02-deploy-scripts\dashboard\start-dashboard.bat
```

### 方式 3: 直接运行 API
```bash
# 启动 API 服务器
cd 03-dashboard/api
python dashboard-api-v4-persona.py

# 访问 http://localhost:8448
```

### 方式 4: 直接打开前端
```bash
# 打开主页面
start 03-dashboard/web/index-with-theme.html
```

---

## 📊 功能特性

### v4.1-Persona 核心功能

| 特性 | 说明 |
|------|------|
| **异步 I/O** | FastAPI + asyncio 非阻塞 |
| **Redis 队列** | 任务异步处理 |
| **WebSocket** | 实时推送 |
| **7-Persona** | 多人格协作引擎 |
| **人格任务分发** | Planner/Executor/Critic 等 |
| **人格状态追踪** | 实时状态监控 |
| **i18n 支持** | 多语言切换 |

### 7 人格系统

| 人格 | 职责 |
|------|------|
| **Planner** | 规划与分解任务 |
| **Executor** | 执行具体任务 |
| **Critic** | 批判性审查 |
| **Learner** | 学习与记忆 |
| **Coordinator** | 协调与仲裁 |
| **Innovator** | 创新与建议 |
| **Metacognition** | 元认知监控 |

---

## 🔧 配置

### 端口配置
- **默认端口:** 8448
- **修改位置:** `api/dashboard-api-v4-persona.py` 第 600 行

### Redis 配置
- **地址:** localhost:6379
- **修改位置:** 代码中 `redis.asyncio.from_url()`

### CORS 配置
- **允许所有源:** `CORSMiddleware` 配置
- **生产环境:** 需限制具体域名

---

## 🧪 测试

**测试位置:** `12-tests/dashboard/`

```bash
# 压力测试
python 12-tests/dashboard/load_test_v4.py --requests 500 --concurrent 50

# 国际化测试
python 12-tests/dashboard/test-i18n-dashboard.py
```

---

## 📖 文档

**文档位置:** `13-docs-reports/dashboard/`

| 文档 | 内容 |
|------|------|
| `DASHBOARD-V4-DEPLOYMENT.md` | v4 部署指南 |
| `DEFAULT-DASHBOARD-V4-PERSONA.md` | v4-Persona 默认配置 |
| `DASHBOARD-V3-DEPLOYMENT.md` | v3 部署指南 (参考) |

---

## 🔗 相关索引

- **工作区总索引:** `15-docs-standard/FOLDER-INDEX.md`
- **部署脚本:** `02-deploy-scripts/README.md`
- **智能体系统:** `08-agent-system/README.md`
- **测试目录:** `12-tests/README.md`
- **文档目录:** `13-docs-reports/README.md`

---

## 📞 故障排查

### API 无法启动
```bash
# 检查端口占用
netstat -ano | findstr :8448

# 检查依赖
pip install fastapi uvicorn aiohttp redis psutil
```

### 页面无法访问
```bash
# 检查 API 是否运行
curl http://localhost:8448

# 检查防火墙
netsh advfirewall firewall show rule name=all | findstr Python
```

---

**最后更新:** 2026-03-17  
**维护者:** Claw 🐾  
**版本:** v4.1-Persona (单一精简版)  
**归类完成:** ✅ 脚本→02-deploy-scripts, 测试→12-tests, 文档→13-docs-reports
