# Materials Science System - Docker 部署配置

**版本:** v0.1  
**创建时间:** 2026-03-05 13:56  
**目的:** Docker 部署配置

---

## 📦 docker-compose.yml

```yaml
version: '3.8'

services:
  # API 服务
  api:
    build:
      context: ./materials-api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mongodb://mongodb:27017
      - NEO4J_URL=neo4j://neo4j:7687
    depends_on:
      - mongodb
      - neo4j
    volumes:
      - ./data:/app/data
    networks:
      - materials-network

  # Web 界面
  web:
    build:
      context: ./materials-web
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - api
    networks:
      - materials-network

  # MongoDB
  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    networks:
      - materials-network

  # Neo4j
  neo4j:
    image: neo4j:5.15
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
    volumes:
      - neo4j_data:/data
    networks:
      - materials-network

  # Redis (缓存)
  redis:
    image: redis:7.2
    ports:
      - "6379:6379"
    networks:
      - materials-network

  # Celery (任务队列)
  celery:
    build:
      context: ./materials-api
      dockerfile: Dockerfile
    command: celery -A app worker
    depends_on:
      - redis
      - mongodb
    networks:
      - materials-network

volumes:
  mongodb_data:
  neo4j_data:

networks:
  materials-network:
    driver: bridge
```

---

## 🚀 部署命令

### 启动服务
```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

### 数据备份
```bash
# 备份 MongoDB
docker-compose run mongodb mongodump --out /backup

# 备份 Neo4j
docker-compose run neo4j neo4j-admin dump --to=/backup/neo4j.dump
```

### 数据恢复
```bash
# 恢复 MongoDB
docker-compose run mongodb mongorestore /backup

# 恢复 Neo4j
docker-compose run neo4j neo4j-admin load --from=/backup/neo4j.dump
```

---

## 📊 监控配置

### Prometheus + Grafana
```yaml
# 添加到 docker-compose.yml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
  volumes:
    - grafana_data:/var/lib/grafana
```

---

## 📅 实施计划

| 任务 | 用时 | 状态 |
|------|------|------|
| Docker 配置编写 | 2 小时 | ✅ |
| docker-compose 配置 | 2 小时 | ✅ |
| Kubernetes 配置 | 3 小时 | 📋 |
| 监控配置 | 2 小时 | 📋 |
| 部署文档编写 | 2 小时 | ✅ |

---

*最后更新：2026-03-05 13:56*
