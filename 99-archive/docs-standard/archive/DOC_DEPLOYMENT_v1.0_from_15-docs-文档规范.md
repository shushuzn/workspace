# 部署指南

**版本:** v2.0  
**创建时间:** 2026-03-05 18:00  
**状态:** 🟢 生产就绪

---

## 📋 系统要求

### 硬件要求
| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 4 核 | 8 核+ |
| 内存 | 8GB | 16GB+ |
| 磁盘 | 50GB | 100GB+ SSD |
| 网络 | 10Mbps | 100Mbps+ |

### 软件要求
- Python 3.11+
- Git
- Docker (可选)
- Node.js (可选，用于可视化)

---

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/shushuzn/obsidian-sync.git
cd obsidian-sync
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置系统
```bash
# 复制配置模板
cp config.example.yaml config.yaml

# 编辑配置
vim config.yaml
```

### 4. 设置环境变量
```bash
# API Key
export API_KEY='your-api-key-here'

# 其他配置
export MONGODB_URI='mongodb://localhost:27017'
```

### 5. 启动系统
```bash
# 启动 API 服务
python scripts/api/api-gateway.py

# 启动监控服务
python scripts/monitoring/monitoring-system.py
```

### 6. 验证部署
```bash
# 健康检查
curl http://localhost:5000/api/v1/health
```

---

## 🔧 配置说明

### 核心配置
```yaml
# config.yaml
global:
  version: "2.0"
  date_format: "%Y-%m-%d"
  
paths:
  workspace: "D:\\OpenClaw\\workspace"
  obsidian_vault: "D:\\obsidian\\Vault"

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### 安全配置
```yaml
security:
  authentication:
    enabled: true
    method: api_key
    api_key_header: X-API-Key
  
  rate_limiting:
    enabled: true
    requests_per_minute: 60
```

---

## 📦 Docker 部署 (可选)

### 构建镜像
```bash
docker build -t obsidian-sync:latest .
```

### 运行容器
```bash
docker run -d \
  -p 5000:5000 \
  -v /path/to/workspace:/app/workspace \
  -e API_KEY=your-api-key \
  --name obsidian-sync \
  obsidian-sync:latest
```

### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - API_KEY=your-api-key
    volumes:
      - ./workspace:/app/workspace
```

---

## 🔍 验证部署

### 健康检查
```bash
curl http://localhost:5000/api/v1/health
# 预期响应：{"status": "healthy", "version": "2.0"}
```

### 测试 API
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:5000/api/v1/papers
```

### 检查日志
```bash
tail -f logs/api-gateway.log
```

---

## ⚠️ 故障排除

### 常见问题

**1. API 服务无法启动**
```bash
# 检查端口占用
netstat -ano | findstr :5000

# 检查日志
cat logs/api-gateway.log
```

**2. 认证失败**
```bash
# 验证 API Key
echo $API_KEY

# 检查配置文件
cat config.yaml
```

**3. 依赖安装失败**
```bash
# 升级 pip
python -m pip install --upgrade pip

# 清理缓存
pip cache purge

# 重新安装
pip install -r requirements.txt
```

---

## 📊 性能基准

### 预期性能
| 指标 | 目标值 |
|------|--------|
| API 响应时间 | <100ms |
| 论文处理速度 | 100 篇/分钟 |
| 系统可用性 | >99% |
| 内存使用 | <2GB |

---

*最后更新：2026-03-05 18:00*
