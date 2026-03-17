# 材料学部署方案 - 设计文档

**版本:** v0.1  
**创建时间:** 2026-03-05 13:34  
**目的:** 材料科学系统部署方案

---

## 📦 部署架构

### 生产环境架构
```
                    ┌─────────────┐
                    │   Nginx     │
                    │ (反向代理)   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──────┐ ┌──▼────────┐ ┌─▼───────────┐
       │  API Server │ │ Web Server│ │Task Queue   │
       │  (FastAPI)  │ │  (React)  │ │(Celery)     │
       └──────┬──────┘ └───────────┘ └─┬───────────┘
              │                        │
       ┌──────▼────────────────────────▼───────┐
       │           Database Layer              │
       │  ┌──────────┐  ┌──────────┐  ┌──────┐│
       │  │ MongoDB  │  │  Neo4j   │  │Redis ││
       │  │(材料数据)│  │(知识图谱)│  │(缓存)││
       │  └──────────┘  └──────────┘  └──────┘│
       └───────────────────────────────────────┘
```

---

## 🔧 部署方式

### 1. Docker 部署 (推荐)

#### docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: ./materials-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mongodb://mongodb:27017
      - NEO4J_URL=neo4j://neo4j:7687
    depends_on:
      - mongodb
      - neo4j

  web:
    build: ./materials-web
    ports:
      - "3000:80"
    depends_on:
      - api

  mongodb:
    image: mongo:7.0
    volumes:
      - mongodb_data:/data/db

  neo4j:
    image: neo4j:5.15
    environment:
      - NEO4J_AUTH=neo4j/password
    volumes:
      - neo4j_data:/data

  redis:
    image: redis:7.2

  celery:
    build: ./materials-api
    command: celery -A app worker
    depends_on:
      - redis
      - mongodb

volumes:
  mongodb_data:
  neo4j_data:
```

#### 部署命令
```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 备份数据
docker-compose run mongodb mongodump --out /backup
```

---

### 2. Kubernetes 部署

#### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: materials-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: materials-api
  template:
    metadata:
      labels:
        app: materials-api
    spec:
      containers:
      - name: api
        image: materials-api:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: materials-api
spec:
  selector:
    app: materials-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

### 3. 本地开发部署

#### 快速启动脚本
```bash
#!/bin/bash
# start-dev.sh

# 启动数据库
docker-compose up -d mongodb neo4j redis

# 安装依赖
cd materials-api && pip install -r requirements.txt
cd ../materials-web && npm install

# 启动 API 服务
cd materials-api && uvicorn main:app --reload &

# 启动 Web 服务
cd materials-web && npm start &

echo "Development environment started!"
echo "API: http://localhost:8000"
echo "Web: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
```

---

## 📊 监控与日志

### 监控指标
- API 响应时间
- 错误率
- 数据库连接数
- 内存/CPU 使用率
- 队列长度

### 日志收集
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Prometheus + Grafana

---

## 📅 实施计划

| 任务 | 用时 | 日期 |
|------|------|------|
| Docker 配置编写 | 2 小时 | 04-03 |
| Kubernetes 配置 | 3 小时 | 04-03 |
| CI/CD 流水线 | 3 小时 | 04-04 |
| 监控配置 | 2 小时 | 04-04 |
| 部署文档编写 | 2 小时 | 04-05 |
| **总计** | **12 小时** | - |

---

*最后更新：2026-03-05 13:34*
