# Kubernetes 部署配置

**版本:** v0.1  
**创建时间:** 2026-03-05 14:01  
**目的:** Kubernetes 部署配置

---

## 📦 deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: materials-api
  labels:
    app: materials-api
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
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
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
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: materials-ingress
spec:
  rules:
  - host: materials.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: materials-api
            port:
              number: 80
```

---

## 🚀 部署命令

### 应用配置
```bash
# 应用部署
kubectl apply -f deployment.yaml

# 查看状态
kubectl get deployments
kubectl get pods
kubectl get services

# 查看日志
kubectl logs -f deployment/materials-api

# 扩展副本
kubectl scale deployment materials-api --replicas=5

# 回滚
kubectl rollout undo deployment/materials-api
```

---

## 📊 监控配置

### Prometheus 配置
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: materials-api
spec:
  selector:
    matchLabels:
      app: materials-api
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

---

## 📅 实施计划

| 任务 | 用时 | 状态 |
|------|------|------|
| K8s 配置编写 | 3 小时 | ✅ |
| 监控配置 | 2 小时 | 📋 |
| CI/CD 集成 | 3 小时 | 📋 |

---

*最后更新：2026-03-05 14:01*
