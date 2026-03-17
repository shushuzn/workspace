# Materials Science System - Docker 部署指南

**版本:** v1.0  
**创建时间:** 2026-03-05 19:30  
**目的:** 提供材料科学系统的 Docker 容器化部署详细步骤

---

## 📦 Docker 文件结构

```
materials-system/
├── Dockerfile.api              # API 服务镜像
├── Dockerfile.web              # Web 界面镜像
├── docker-compose.yml          # 完整部署配置
├── docker-compose.dev.yml      # 开发环境配置
├── docker-compose.prod.yml     # 生产环境配置
├── .env.example                # 环境变量模板
├── scripts/
│   └── materials/
│       ├── materials_api_service.py
│       ├── materials_collector.py
│       └── ...
├── web/
│   ├── materials-dashboard.html
│   ├── crystal-viewer.html
│   └── ...
├── models/                     # ML 模型文件
└── requirements.txt            # Python 依赖
```

---

## 🐳 Dockerfile 配置

### API 服务 Dockerfile

**文件:** `Dockerfile.api`

```dockerfile
# 多阶段构建 - 构建阶段
FROM python:3.10-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    cmake \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖 (使用缓存层)
RUN pip install --no-cache-dir --user -r requirements.txt

# 多阶段构建 - 运行阶段
FROM python:3.10-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libgl1 \
    libgomp1 \
    libglib2.0-0 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

# 从构建阶段复制 Python 包
COPY --from=builder /root/.local /home/appuser/.local

# 复制应用代码
COPY --chown=appuser:appuser scripts/ ./scripts/
COPY --chown=appuser:appuser models/ ./models/
COPY --chown=appuser:appuser configs/ ./configs/

# 设置环境变量
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1

# 启动命令
CMD ["python", "scripts/materials/materials_api_service.py", "--host", "0.0.0.0", "--port", "8080"]
```

### Web 界面 Dockerfile

**文件:** `Dockerfile.web`

```dockerfile
FROM nginx:alpine

# 复制静态文件
COPY web/ /usr/share/nginx/html/

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -q --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

### Nginx 配置

**文件:** `web/nginx.conf`

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index materials-dashboard.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    gzip_min_length 1000;

    # 缓存静态资源
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|html)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API 反向代理
    location /api/ {
        proxy_pass http://api-service:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }

    # 主页面
    location / {
        try_files $uri $uri/ /materials-dashboard.html;
    }

    # 错误页面
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

---

## 🔧 Docker Compose 配置

### 开发环境配置

**文件:** `docker-compose.dev.yml`

```yaml
version: '3.8'

services:
  # MongoDB (仅基础服务)
  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_dev_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=devpassword

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes

  # API 服务 (开发模式)
  api-service:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8080:8080"
    volumes:
      - ./scripts:/app/scripts
      - ./models:/app/models
      - ./logs:/app/logs
    environment:
      - DATABASE_URL=mongodb://admin:devpassword@mongodb:27017/materials
      - REDIS_URL=redis://redis:6379
      - API_KEY=dev_api_key_12345
      - LOG_LEVEL=debug
      - DEBUG=true
    depends_on:
      - mongodb
      - redis
    command: >
      python scripts/materials/materials_api_service.py
      --host 0.0.0.0
      --port 8080
      --reload
      --debug

  # Web 界面 (开发模式)
  web-ui:
    image: python:3.10-slim
    working_dir: /app
    volumes:
      - ./web:/app/web
    ports:
      - "3000:3000"
    command: python -m http.server 3000 -d web

volumes:
  mongodb_dev_data:
```

### 生产环境配置

**文件:** `docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - nginx_logs:/var/log/nginx
    depends_on:
      - api-service
    restart: always
    networks:
      - materials-prod-network

  # API 服务 (多实例)
  api-service:
    build:
      context: .
      dockerfile: Dockerfile.api
    environment:
      - DATABASE_URL=mongodb://admin:${MONGO_PASSWORD}@mongodb:27017/materials?authSource=admin
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - API_KEY=${API_KEY}
      - LOG_LEVEL=info
      - WORKERS=4
    volumes:
      - ./models:/app/models:ro
      - api_logs:/app/logs
    depends_on:
      - mongodb
      - redis
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    networks:
      - materials-prod-network
    restart: always

  # MongoDB (副本集)
  mongodb:
    image: mongo:7.0
    volumes:
      - mongodb_prod_data:/data/db
      - mongodb_config:/data/configdb
      - ./mongodb/init-replica-set.js:/docker-entrypoint-initdb.d/init-replica-set.js:ro
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD}
    command: mongod --replSet rs0 --bind_ip_all --keyFile /etc/mongodb-keyfile
    networks:
      - materials-prod-network
    restart: always

  # Redis (带密码)
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
    volumes:
      - redis_prod_data:/data
    networks:
      - materials-prod-network
    restart: always

  # Prometheus 监控
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports:
      - "9090:9090"
    networks:
      - materials-prod-network
    restart: always

  # Grafana 可视化
  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    ports:
      - "3001:3000"
    depends_on:
      - prometheus
    networks:
      - materials-prod-network
    restart: always

volumes:
  mongodb_prod_data:
  mongodb_config:
  redis_prod_data:
  prometheus_data:
  grafana_data:
  nginx_logs:
  api_logs:

networks:
  materials-prod-network:
    driver: bridge
```

---

## 🚀 部署步骤

### 步骤 1: 准备环境

```bash
# 克隆或进入项目目录
cd materials-system

# 复制环境变量文件
cp .env.example .env

# 编辑环境变量
vim .env
```

**.env 文件内容:**
```bash
# 生产环境配置
API_KEY=your_production_api_key_here
MONGO_PASSWORD=secure_mongo_password_123
REDIS_PASSWORD=secure_redis_password_456
GRAFANA_PASSWORD=secure_grafana_password_789
```

### 步骤 2: 构建镜像

```bash
# 构建 API 服务镜像
docker build -t materials-api:latest -f Dockerfile.api .

# 构建 Web 界面镜像
docker build -t materials-web:latest -f Dockerfile.web .

# 验证镜像
docker images | grep materials
```

### 步骤 3: 启动服务

```bash
# 开发环境
docker-compose -f docker-compose.dev.yml up -d

# 生产环境
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f api-service
```

### 步骤 4: 验证部署

```bash
# 健康检查
curl http://localhost:8080/api/v1/health

# 测试 API
curl -X GET "http://localhost:8080/api/v1/materials?limit=5"

# 访问 Web 界面
# 浏览器打开 http://localhost:3000 (开发) 或 http://localhost (生产)
```

### 步骤 5: 初始化数据库

```bash
# 进入 API 容器
docker-compose exec api-service bash

# 运行数据库迁移
python scripts/materials/database_migration.py

# 加载示例数据
python scripts/materials/load_sample_data.py

# 退出容器
exit
```

---

## 🔍 运维命令

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api-service
docker-compose logs -f mongodb

# 查看最近 100 行
docker-compose logs --tail=100 api-service
```

### 服务管理

```bash
# 重启服务
docker-compose restart api-service

# 停止服务
docker-compose stop

# 停止并删除容器
docker-compose down

# 删除容器、网络和卷
docker-compose down -v
```

### 进入容器

```bash
# 进入 API 容器
docker-compose exec api-service bash

# 进入 MongoDB 容器
docker-compose exec mongodb mongosh -u admin -p
```

### 备份与恢复

```bash
# 备份 MongoDB 数据
docker-compose exec mongodb mongodump --out=/data/backup

# 从宿主机复制备份
docker cp materials-system-mongodb-1:/data/backup ./mongodb-backup

# 恢复数据
docker cp ./mongodb-restore materials-system-mongodb-1:/data/restore
docker-compose exec mongodb mongorestore /data/restore
```

---

## 📊 监控配置

### 查看资源使用

```bash
# 查看容器资源使用
docker stats

# 查看特定容器
docker stats materials-system-api-service-1
```

### Prometheus 指标

访问 `http://localhost:9090` 查看 Prometheus

**关键指标:**
- `http_requests_total` - 总请求数
- `http_request_duration_seconds` - 请求耗时
- `mongodb_connections` - 数据库连接数
- `redis_connected_clients` - Redis 客户端数

### Grafana 仪表板

访问 `http://localhost:3001` 查看 Grafana

**默认账号:** admin / (你在 .env 中设置的密码)

**预置仪表板:**
- API 性能监控
- 数据库监控
- 系统资源监控
- 业务指标监控

---

## 🐛 故障排查

### 常见问题

#### 1. API 服务无法启动

```bash
# 查看日志
docker-compose logs api-service

# 检查端口占用
docker-compose ps

# 重建容器
docker-compose up -d --force-recreate api-service
```

#### 2. MongoDB 连接失败

```bash
# 检查 MongoDB 状态
docker-compose ps mongodb

# 查看 MongoDB 日志
docker-compose logs mongodb

# 测试连接
docker-compose exec api-service python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://admin:password@mongodb:27017')
print(client.admin.command('ping'))
"
```

#### 3. 内存不足

```bash
# 限制容器内存
docker-compose up -d --build api-service

# 编辑 docker-compose.yml 添加:
# deploy:
#   resources:
#     limits:
#       memory: 1G
```

#### 4. 磁盘空间不足

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的卷
docker volume prune

# 查看磁盘使用
docker system df
```

---

## 📈 性能优化

### 构建优化

```dockerfile
# 使用多阶段构建减少镜像大小
# 利用 Docker 缓存层
# 合并 RUN 指令减少层数
```

### 运行时优化

```yaml
# 在 docker-compose.yml 中添加:
services:
  api-service:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 512M
```

### 网络优化

```yaml
# 使用自定义网络
networks:
  materials-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

---

## 🔐 安全最佳实践

1. **使用非 root 用户运行容器**
2. **定期更新基础镜像**
3. **扫描镜像漏洞:** `docker scan materials-api:latest`
4. **使用 Docker Secret 管理敏感信息**
5. **限制容器资源**
6. **启用日志记录**
7. **定期备份数据**

---

*最后更新：2026-03-05 19:30*
