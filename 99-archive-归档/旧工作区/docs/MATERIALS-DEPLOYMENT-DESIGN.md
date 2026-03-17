# Materials Science System - 部署设计文档

**版本:** v1.0  
**创建时间:** 2026-03-05 19:25  
**目的:** 定义材料科学系统的部署架构和流程

---

## 🏗️ 部署架构

### 生产环境架构

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    │    (Nginx)      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼────────┐    │    ┌────────▼────────┐
     │  API Service 1  │    │    │  API Service 2  │
     │   (Port 8080)   │    │    │   (Port 8080)   │
     └────────┬────────┘    │    └────────┬────────┘
              │             │             │
              └─────────────┼─────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
     ┌────────▼────────┐   │    ┌────────▼────────┐
     │   MongoDB       │   │    │      Redis      │
     │  (Replica Set)  │   │    │    (Cache)      │
     └─────────────────┘   │    └─────────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
     ┌────────▼────────┐  │   ┌────────▼────────┐
     │  ML Model Store │  │   │  File Storage   │
     │   (S3/MinIO)    │  │   │   (CIF Files)   │
     └─────────────────┘  │   └─────────────────┘
                          │
                 ┌────────▼────────┐
                 │  Monitoring     │
                 │  (Prometheus)   │
                 └─────────────────┘
```

---

## 📦 部署选项

### 选项 1: Docker Compose (开发/测试)

**文件:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  # API 服务
  api-service:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=mongodb://mongodb:27017/materials
      - REDIS_URL=redis://redis:6379
      - API_KEY=${API_KEY}
      - LOG_LEVEL=info
    depends_on:
      - mongodb
      - redis
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - materials-network

  # MongoDB
  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
      - mongodb_config:/data/configdb
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD}
    networks:
      - materials-network
    restart: unless-stopped

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    networks:
      - materials-network
    restart: unless-stopped

  # Web 界面
  web-ui:
    build:
      context: ./web
      dockerfile: Dockerfile.web
    ports:
      - "3000:80"
    depends_on:
      - api-service
    networks:
      - materials-network
    restart: unless-stopped

  # 监控 (可选)
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - materials-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    depends_on:
      - prometheus
    networks:
      - materials-network
    restart: unless-stopped

volumes:
  mongodb_data:
  mongodb_config:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  materials-network:
    driver: bridge
```

### 部署命令

```bash
# 设置环境变量
export API_KEY="your_api_key"
export MONGO_PASSWORD="secure_password"
export GRAFANA_PASSWORD="secure_password"

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f api-service

# 停止服务
docker-compose down

# 重建并启动
docker-compose up -d --build
```

---

### 选项 2: Kubernetes (生产环境)

**文件:** `k8s/api-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: materials-api
  namespace: materials-system
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
      - name: api-service
        image: materials-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: materials-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: materials-config
              key: redis-url
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: materials-secrets
              key: api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: models-volume
          mountPath: /app/models
      volumes:
      - name: models-volume
        persistentVolumeClaim:
          claimName: models-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: materials-api-service
  namespace: materials-system
spec:
  selector:
    app: materials-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: materials-api-hpa
  namespace: materials-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: materials-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**文件:** `k8s/mongodb-statefulset.yaml`

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
  namespace: materials-system
spec:
  serviceName: mongodb
  replicas: 3
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:7.0
        ports:
        - containerPort: 27017
        volumeMounts:
        - name: mongodb-data
          mountPath: /data/db
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          valueFrom:
            secretKeyRef:
              name: materials-secrets
              key: mongo-username
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: materials-secrets
              key: mongo-password
  volumeClaimTemplates:
  - metadata:
      name: mongodb-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 50Gi
---
apiVersion: v1
kind: Service
metadata:
  name: mongodb
  namespace: materials-system
spec:
  clusterIP: None
  selector:
    app: mongodb
  ports:
  - port: 27017
    targetPort: 27017
```

**文件:** `k8s/ingress.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: materials-ingress
  namespace: materials-system
  annotations:
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - materials.example.com
    secretName: materials-tls
  rules:
  - host: materials.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: materials-api-service
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: materials-web-service
            port:
              number: 80
```

### 部署命令

```bash
# 创建命名空间
kubectl create namespace materials-system

# 创建 Secret
kubectl create secret generic materials-secrets \
  --from-literal=database-url="mongodb://admin:password@mongodb:27017" \
  --from-literal=api-key="your_api_key" \
  --from-literal=mongo-username="admin" \
  --from-literal=mongo-password="secure_password" \
  -n materials-system

# 创建 ConfigMap
kubectl create configmap materials-config \
  --from-literal=redis-url="redis://redis:6379" \
  --from-literal=log-level="info" \
  -n materials-system

# 应用所有配置
kubectl apply -f k8s/

# 查看部署状态
kubectl get all -n materials-system

# 查看日志
kubectl logs -f deployment/materials-api -n materials-system

# 扩缩容
kubectl scale deployment materials-api --replicas=5 -n materials-system
```

---

### 选项 3: 本地开发部署

**文件:** `scripts/deploy-local.ps1`

```powershell
# 本地开发环境部署脚本

Write-Host "🚀 开始本地部署..." -ForegroundColor Green

# 1. 检查依赖
Write-Host "`n📦 检查依赖..." -ForegroundColor Yellow

$dependencies = @("python", "pip", "docker", "docker-compose")
foreach ($dep in $dependencies) {
    try {
        $null = Get-Command $dep -ErrorAction Stop
        Write-Host "  ✅ $dep" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ $dep 未安装" -ForegroundColor Red
        exit 1
    }
}

# 2. 创建虚拟环境
Write-Host "`n🐍 创建 Python 虚拟环境..." -ForegroundColor Yellow
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. 安装依赖
Write-Host "`n📥 安装 Python 依赖..." -ForegroundColor Yellow
pip install -r requirements.txt

# 4. 启动 Docker 服务
Write-Host "`n🐳 启动 Docker 服务..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml up -d mongodb redis

# 5. 等待服务就绪
Write-Host "`n⏳ 等待服务就绪..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 6. 运行数据库迁移
Write-Host "`n🔧 运行数据库迁移..." -ForegroundColor Yellow
python scripts/materials/database_migration.py

# 7. 加载预训练模型
Write-Host "`n📊 加载预训练模型..." -ForegroundColor Yellow
if (!(Test-Path "models")) {
    New-Item -ItemType Directory -Path "models"
    Write-Host "  ⚠️  模型目录为空，请手动下载模型" -ForegroundColor Yellow
}

# 8. 启动 API 服务
Write-Host "`n🌐 启动 API 服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python scripts/materials/materials_api_service.py"

# 9. 启动 Web 界面
Write-Host "`n🎨 启动 Web 界面..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m http.server 3000 -d web"

Write-Host "`n✅ 部署完成!" -ForegroundColor Green
Write-Host "`n访问地址:" -ForegroundColor Cyan
Write-Host "  API:     http://localhost:8080" -ForegroundColor White
Write-Host "  Web UI:  http://localhost:3000" -ForegroundColor White
Write-Host "  MongoDB: mongodb://localhost:27017" -ForegroundColor White
Write-Host "  Redis:   redis://localhost:6379" -ForegroundColor White
```

---

## 🔐 安全配置

### 环境变量

**文件:** `.env.example`

```bash
# API 配置
API_KEY=your_super_secret_api_key
API_RATE_LIMIT=100

# 数据库配置
DATABASE_URL=mongodb://admin:password@localhost:27017/materials
MONGO_USERNAME=admin
MONGO_PASSWORD=secure_password

# Redis 配置
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=redis_password

# ML 模型配置
MODEL_PATH=./models
MODEL_CACHE_SIZE=1000

# 日志配置
LOG_LEVEL=info
LOG_FILE=./logs/api.log

# 监控配置
PROMETHEUS_ENABLED=true
GRAFANA_PASSWORD=grafana_password
```

### CORS 配置

```python
# API 服务中的 CORS 设置
CORS_CONFIG = {
    "allow_origins": [
        "http://localhost:3000",
        "https://materials.example.com"
    ],
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE"],
    "allow_headers": ["Content-Type", "X-API-Key"],
}
```

---

## 📊 监控与日志

### Prometheus 配置

**文件:** `monitoring/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'materials-api'
    static_configs:
      - targets: ['api-service:8080']
    metrics_path: '/metrics'
    
  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongodb-exporter:9216']
      
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### Grafana 仪表板

**关键指标:**
- API 请求量 (QPS)
- 响应时间 (P50, P95, P99)
- 错误率
- 数据库连接数
- 缓存命中率
- ML 模型推理时间

---

## 🔄 CI/CD 流程

### GitHub Actions

**文件:** `.github/workflows/deploy.yml`

```yaml
name: Deploy Materials System

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest --cov=scripts/materials
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t materials-api:latest .
      
      - name: Push to registry
        run: |
          docker tag materials-api:latest registry.example.com/materials-api:${{ github.sha }}
          docker push registry.example.com/materials-api:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/materials-api api-service=registry.example.com/materials-api:${{ github.sha }} -n materials-system
```

---

## 📈 性能优化

### 缓存策略

```python
# Redis 缓存配置
CACHE_CONFIG = {
    'material_details': {'ttl': 3600},      # 1 小时
    'predictions': {'ttl': 86400},          # 24 小时
    'search_results': {'ttl': 1800},        # 30 分钟
    'knowledge_graph': {'ttl': 7200},       # 2 小时
}
```

### 数据库索引

```javascript
// MongoDB 索引
db.materials.createIndex({ "material_id": 1 }, { unique: true })
db.materials.createIndex({ "formula": 1 })
db.materials.createIndex({ "elements": 1 })
db.materials.createIndex({ "band_gap": 1 })
db.materials.createIndex({ "space_group": 1 })
db.materials.createIndex({ "$**": "text" })  // 全文搜索
```

---

## 📝 部署检查清单

### 部署前

- [ ] 代码审查通过
- [ ] 所有测试通过 (覆盖率 >85%)
- [ ] 安全扫描通过
- [ ] 性能基准测试通过
- [ ] 备份现有数据
- [ ] 通知相关人员

### 部署中

- [ ] 滚动更新 (Kubernetes)
- [ ] 监控错误率
- [ ] 检查健康端点
- [ ] 验证关键功能

### 部署后

- [ ] 运行冒烟测试
- [ ] 检查日志无异常
- [ ] 验证监控仪表板
- [ ] 更新文档
- [ ] 通知用户 (如有重大变更)

---

## 🆘 故障恢复

### 回滚命令

```bash
# Kubernetes 回滚
kubectl rollout undo deployment/materials-api -n materials-system

# Docker Compose 回滚
docker-compose up -d --force-recreate api-service
```

### 数据备份

```bash
# MongoDB 备份
mongodump --uri="mongodb://admin:password@localhost:27017/materials" \
  --out=/backups/materials_$(date +%Y%m%d)

# Redis 备份
redis-cli BGSAVE

# 模型备份
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/
```

---

*最后更新：2026-03-05 19:25*
