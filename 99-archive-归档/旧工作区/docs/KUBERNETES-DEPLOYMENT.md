# Materials Science System - Kubernetes 部署指南

**版本:** v1.0  
**创建时间:** 2026-03-05 19:35  
**目的:** 提供材料科学系统的 Kubernetes 生产环境部署详细步骤

---

## 📦 Kubernetes 文件结构

```
k8s/
├── namespace.yaml              # 命名空间定义
├── secrets.yaml                # 密钥管理
├── configmap.yaml              # 配置文件
├── storage-class.yaml          # 存储类
├── mongodb/
│   ├── statefulset.yaml        # MongoDB StatefulSet
│   ├── service.yaml            # MongoDB Service
│   ├── pvc.yaml                # 持久化卷声明
│   └── init-replica-set.yaml   # 副本集初始化
├── redis/
│   ├── deployment.yaml         # Redis Deployment
│   ├── service.yaml            # Redis Service
│   └── pvc.yaml                # Redis PVC
├── api/
│   ├── deployment.yaml         # API Deployment
│   ├── service.yaml            # API Service
│   ├── hpa.yaml                # 水平自动扩缩
│   └── pdb.yaml                # Pod 中断预算
├── web/
│   ├── deployment.yaml         # Web Deployment
│   ├── service.yaml            # Web Service
│   └── ingress.yaml            # Ingress 配置
├── monitoring/
│   ├── prometheus/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   └── grafana/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── dashboards-configmap.yaml
├── network-policy.yaml         # 网络策略
└── rbac/
    ├── service-account.yaml
    └── role-binding.yaml
```

---

## 🏗️ 核心资源配置

### 命名空间

**文件:** `k8s/namespace.yaml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: materials-system
  labels:
    name: materials-system
    environment: production
    team: ai-research
```

### 密钥管理

**文件:** `k8s/secrets.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: materials-secrets
  namespace: materials-system
type: Opaque
stringData:
  # 数据库凭据
  mongo-root-username: admin
  mongo-root-password: "CHANGE_ME_SECURE_PASSWORD"
  mongo-connection-string: "mongodb://admin:CHANGE_ME_SECURE_PASSWORD@mongodb-0.mongodb:27017,mongodb-1.mongodb:27017,mongodb-2.mongodb:27017/materials?replicaSet=rs0"
  
  # Redis 密码
  redis-password: "CHANGE_ME_REDIS_PASSWORD"
  
  # API 密钥
  api-key: "CHANGE_ME_API_KEY"
  
  # Grafana 管理员密码
  grafana-admin-password: "CHANGE_ME_GRAFANA_PASSWORD"
  
  # TLS 证书 (如果使用 HTTPS)
  tls-cert: |
    -----BEGIN CERTIFICATE-----
    ...
    -----END CERTIFICATE-----
  tls-key: |
    -----BEGIN PRIVATE KEY-----
    ...
    -----END PRIVATE KEY-----
```

**创建命令:**
```bash
# 从字面值创建 Secret
kubectl create secret generic materials-secrets \
  --from-literal=mongo-root-username=admin \
  --from-literal=mongo-root-password=$(openssl rand -base64 32) \
  --from-literal=redis-password=$(openssl rand -base64 32) \
  --from-literal=api-key=$(openssl rand -base64 32) \
  --from-literal=grafana-admin-password=$(openssl rand -base64 32) \
  -n materials-system

# 或从文件创建
kubectl create secret generic materials-secrets \
  --from-file=.env \
  -n materials-system
```

### 配置中心

**文件:** `k8s/configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: materials-config
  namespace: materials-system
data:
  # 应用配置
  LOG_LEVEL: "info"
  ENVIRONMENT: "production"
  
  # 数据库配置
  DATABASE_NAME: "materials"
  DATABASE_PORT: "27017"
  
  # Redis 配置
  REDIS_HOST: "redis"
  REDIS_PORT: "6379"
  
  # API 配置
  API_RATE_LIMIT: "100"
  API_TIMEOUT: "30"
  
  # ML 模型配置
  MODEL_CACHE_SIZE: "1000"
  MODEL_PATH: "/app/models"
  
  # 监控配置
  PROMETHEUS_ENABLED: "true"
  METRICS_PORT: "8080"
  
  # Nginx 配置
  nginx.conf: |
    worker_processes auto;
    events {
        worker_connections 1024;
    }
    http {
        include /etc/nginx/mime.types;
        default_type application/octet-stream;
        
        sendfile on;
        keepalive_timeout 65;
        
        upstream api_backend {
            server materials-api:8080;
        }
        
        server {
            listen 80;
            server_name _;
            
            location /api/ {
                proxy_pass http://api_backend;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
            }
            
            location / {
                root /usr/share/nginx/html;
                index index.html;
                try_files $uri $uri/ /index.html;
            }
        }
    }
```

---

## 🗄️ 数据库部署

### MongoDB StatefulSet

**文件:** `k8s/mongodb/statefulset.yaml`

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
  namespace: materials-system
  labels:
    app: mongodb
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
      serviceAccountName: materials-service-account
      securityContext:
        fsGroup: 999
      containers:
      - name: mongodb
        image: mongo:7.0
        command:
          - mongod
          - "--replSet"
          - "rs0"
          - "--bind_ip_all"
          - "--keyFile"
          - "/etc/mongodb-keyfile/keyfile"
        ports:
        - containerPort: 27017
          name: mongodb
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
        volumeMounts:
        - name: mongodb-data
          mountPath: /data/db
        - name: mongodb-keyfile
          mountPath: /etc/mongodb-keyfile
          readOnly: true
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          valueFrom:
            secretKeyRef:
              name: materials-secrets
              key: mongo-root-username
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: materials-secrets
              key: mongo-root-password
        livenessProbe:
          exec:
            command:
              - mongosh
              - --eval
              - "db.adminCommand('ping')"
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          exec:
            command:
              - mongosh
              - --eval
              - "db.adminCommand('ping')"
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 2
          failureThreshold: 3
      volumes:
      - name: mongodb-keyfile
        secret:
          secretName: mongodb-keyfile
          defaultMode: 0400
  volumeClaimTemplates:
  - metadata:
      name: mongodb-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: standard
      resources:
        requests:
          storage: 50Gi
---
# MongoDB 副本集初始化 Job
apiVersion: batch/v1
kind: Job
metadata:
  name: mongodb-init-replica-set
  namespace: materials-system
  annotations:
    "helm.sh/hook": post-install,post-upgrade
    "helm.sh/hook-delete-policy": before-hook-creation
spec:
  template:
    spec:
      containers:
      - name: mongodb-init
        image: mongo:7.0
        command:
          - mongosh
          - --host
          - mongodb-0.mongodb
          - --eval
          - |
            rs.initiate({
              _id: "rs0",
              members: [
                { _id: 0, host: "mongodb-0.mongodb:27017" },
                { _id: 1, host: "mongodb-1.mongodb:27017" },
                { _id: 2, host: "mongodb-2.mongodb:27017" }
              ]
            })
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          valueFrom:
            secretKeyRef:
              name: materials-secrets
              key: mongo-root-username
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: materials-secrets
              key: mongo-root-password
      restartPolicy: OnFailure
  backoffLimit: 5
```

### MongoDB Service

**文件:** `k8s/mongodb/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mongodb
  namespace: materials-system
  labels:
    app: mongodb
spec:
  ports:
  - port: 27017
    targetPort: 27017
    name: mongodb
  clusterIP: None
  selector:
    app: mongodb
---
# Headless Service for StatefulSet
apiVersion: v1
kind: Service
metadata:
  name: mongodb-headless
  namespace: materials-system
spec:
  ports:
  - port: 27017
    name: mongodb
  clusterIP: None
  selector:
    app: mongodb
```

---

## 🚀 API 服务部署

### API Deployment

**文件:** `k8s/api/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: materials-api
  namespace: materials-system
  labels:
    app: materials-api
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: materials-api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: materials-api
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: materials-service-account
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: api-service
        image: materials-api:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
          name: http
          protocol: TCP
        - containerPort: 8080
          name: metrics
          protocol: TCP
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: materials-secrets
              key: mongo-connection-string
        - name: REDIS_URL
          value: "redis://:$(REDIS_PASSWORD)@redis:6379"
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: materials-secrets
              key: redis-password
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: materials-secrets
              key: api-key
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: materials-config
              key: LOG_LEVEL
        - name: MODEL_PATH
          valueFrom:
            configMapKeyRef:
              name: materials-config
              key: MODEL_PATH
        resources:
          requests:
            cpu: "250m"
            memory: "512Mi"
          limits:
            cpu: "1"
            memory: "2Gi"
        volumeMounts:
        - name: models-volume
          mountPath: /app/models
          readOnly: true
        - name: logs-volume
          mountPath: /app/logs
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 2
          failureThreshold: 3
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: false
          capabilities:
            drop:
              - ALL
      volumes:
      - name: models-volume
        persistentVolumeClaim:
          claimName: models-pvc
      - name: logs-volume
        emptyDir: {}
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: materials-api
              topologyKey: kubernetes.io/hostname
      terminationGracePeriodSeconds: 30
```

### API Service

**文件:** `k8s/api/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: materials-api
  namespace: materials-system
  labels:
    app: materials-api
  annotations:
    prometheus.io/scrape: "true"
spec:
  type: ClusterIP
  ports:
  - port: 8080
    targetPort: 8080
    protocol: TCP
    name: http
  - port: 8080
    targetPort: 8080
    protocol: TCP
    name: metrics
  selector:
    app: materials-api
```

### 水平自动扩缩 (HPA)

**文件:** `k8s/api/hpa.yaml`

```yaml
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
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Max
```

### Pod 中断预算 (PDB)

**文件:** `k8s/api/pdb.yaml`

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: materials-api-pdb
  namespace: materials-system
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: materials-api
```

---

## 🌐 Web 界面与 Ingress

### Web Deployment

**文件:** `k8s/web/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: materials-web
  namespace: materials-system
spec:
  replicas: 2
  selector:
    matchLabels:
      app: materials-web
  template:
    metadata:
      labels:
        app: materials-web
    spec:
      containers:
      - name: nginx
        image: materials-web:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 80
          name: http
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "200m"
            memory: "256Mi"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Ingress 配置

**文件:** `k8s/web/ingress.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: materials-ingress
  namespace: materials-system
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    nginx.ingress.kubernetes.io/connection-proxy-header: "keep-alive"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - materials.example.com
    secretName: materials-tls-secret
  rules:
  - host: materials.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: materials-api
            port:
              number: 8080
      - path: /metrics
        pathType: Prefix
        backend:
          service:
            name: materials-api
            port:
              number: 8080
      - path: /
        pathType: Prefix
        backend:
          service:
            name: materials-web
            port:
              number: 80
```

---

## 📊 监控部署

### Prometheus 配置

**文件:** `k8s/monitoring/prometheus/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: materials-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      serviceAccountName: prometheus
      containers:
      - name: prometheus
        image: prom/prometheus:v2.45.0
        ports:
        - containerPort: 9090
        args:
          - "--config.file=/etc/prometheus/prometheus.yml"
          - "--storage.tsdb.path=/prometheus"
          - "--storage.tsdb.retention.time=15d"
          - "--web.enable-lifecycle"
        volumeMounts:
        - name: prometheus-config
          mountPath: /etc/prometheus
        - name: prometheus-data
          mountPath: /prometheus
        resources:
          requests:
            cpu: "500m"
            memory: "2Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
      volumes:
      - name: prometheus-config
        configMap:
          name: prometheus-config
      - name: prometheus-data
        persistentVolumeClaim:
          claimName: prometheus-pvc
```

### Grafana Dashboard 配置

**文件:** `k8s/monitoring/grafana/dashboards-configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboards
  namespace: materials-system
data:
  api-dashboard.json: |
    {
      "dashboard": {
        "title": "Materials API Dashboard",
        "panels": [
          {
            "title": "Request Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(http_requests_total[5m])"
              }
            ]
          },
          {
            "title": "Response Time (P95)",
            "type": "graph",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
              }
            ]
          },
          {
            "title": "Error Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
              }
            ]
          }
        ]
      }
    }
```

---

## 🚀 部署流程

### 步骤 1: 前置准备

```bash
# 确保 kubectl 已配置
kubectl config current-context

# 创建命名空间
kubectl apply -f k8s/namespace.yaml

# 创建 Secret
kubectl apply -f k8s/secrets.yaml

# 创建 ConfigMap
kubectl apply -f k8s/configmap.yaml

# 创建存储类 (如果需要)
kubectl apply -f k8s/storage-class.yaml
```

### 步骤 2: 部署基础设施

```bash
# 部署 MongoDB
kubectl apply -f k8s/mongodb/

# 部署 Redis
kubectl apply -f k8s/redis/

# 等待基础设施就绪
kubectl wait --for=condition=ready pod -l app=mongodb -n materials-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n materials-system --timeout=120s
```

### 步骤 3: 部署应用服务

```bash
# 部署 API 服务
kubectl apply -f k8s/api/

# 部署 Web 界面
kubectl apply -f k8s/web/

# 部署监控
kubectl apply -f k8s/monitoring/

# 部署网络策略
kubectl apply -f k8s/network-policy.yaml
```

### 步骤 4: 验证部署

```bash
# 查看所有 Pod 状态
kubectl get pods -n materials-system

# 查看服务
kubectl get svc -n materials-system

# 查看 Ingress
kubectl get ingress -n materials-system

# 查看 API Pod 日志
kubectl logs -f deployment/materials-api -n materials-system

# 测试 API 端点
kubectl port-forward svc/materials-api 8080:8080 -n materials-system
curl http://localhost:8080/api/v1/health
```

### 步骤 5: 配置 DNS 和 TLS

```bash
# 安装 cert-manager (如果未安装)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml

# 创建 ClusterIssuer
kubectl apply -f k8s/ingress/cluster-issuer.yaml

# 等待证书签发
kubectl get certificate -n materials-system
```

---

## 🔍 运维命令

### 查看状态

```bash
# 查看所有资源
kubectl get all -n materials-system

# 查看 Pod 详情
kubectl describe pod <pod-name> -n materials-system

# 查看事件
kubectl get events -n materials-system --sort-by='.lastTimestamp'
```

### 扩缩容

```bash
# 手动扩缩容
kubectl scale deployment materials-api --replicas=5 -n materials-system

# 查看 HPA 状态
kubectl get hpa -n materials-system
```

### 滚动更新

```bash
# 更新镜像
kubectl set image deployment/materials-api api-service=materials-api:v2.0 -n materials-system

# 查看更新状态
kubectl rollout status deployment/materials-api -n materials-system

# 回滚
kubectl rollout undo deployment/materials-api -n materials-system

# 查看历史
kubectl rollout history deployment/materials-api -n materials-system
```

### 故障排查

```bash
# 进入 Pod
kubectl exec -it <pod-name> -n materials-system -- bash

# 查看日志
kubectl logs <pod-name> -n materials-system
kubectl logs <pod-name> -c <container-name> -n materials-system

# 端口转发
kubectl port-forward <pod-name> 8080:8080 -n materials-system

# 测试网络
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://materials-api:8080/api/v1/health
```

---

## 📈 监控与告警

### Prometheus 查询示例

```promql
# API 请求率
rate(http_requests_total{namespace="materials-system"}[5m])

# P95 响应时间
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# 错误率
sum(rate(http_requests_total{status=~"5..", namespace="materials-system"}[5m])) 
/ 
sum(rate(http_requests_total{namespace="materials-system"}[5m]))

# MongoDB 连接数
mongodb_ss_connections{conn_type="current"}

# Redis 内存使用
redis_memory_used_bytes
```

### 告警规则

**文件:** `k8s/monitoring/prometheus/alerts.yaml`

```yaml
groups:
- name: materials-system
  rules:
  - alert: HighErrorRate
    expr: |
      sum(rate(http_requests_total{status=~"5..", namespace="materials-system"}[5m])) 
      / 
      sum(rate(http_requests_total{namespace="materials-system"}[5m])) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value | humanizePercentage }}"
  
  - alert: HighResponseTime
    expr: |
      histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "P95 response time is {{ $value }}s"
  
  - alert: PodCrashLooping
    expr: |
      rate(kube_pod_container_status_restarts_total{namespace="materials-system"}[15m]) > 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Pod is crash looping"
      description: "Pod {{ $labels.pod }} is restarting frequently"
```

---

## 🔐 安全最佳实践

1. **使用 RBAC 限制权限**
2. **启用 NetworkPolicy 隔离网络**
3. **使用 Secret 管理敏感信息**
4. **启用 Pod Security Standards**
5. **定期扫描镜像漏洞**
6. **启用审计日志**
7. **限制容器资源**
8. **使用只读文件系统 (如可能)**

---

*最后更新：2026-03-05 19:35*
