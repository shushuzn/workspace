# Materials Science System - Kubernetes 閮ㄧ讲鎸囧崡

**鐗堟湰:** v1.0  
**鍒涘缓鏃堕棿:** 2026-03-05 19:35  
**鐩殑:** 鎻愪緵鏉愭枡绉戝绯荤粺鐨?Kubernetes 鐢熶骇鐜閮ㄧ讲璇︾粏姝ラ

---

## 馃摝 Kubernetes 鏂囦欢缁撴瀯

```
k8s/
鈹溾攢鈹€ namespace.yaml              # 鍛藉悕绌洪棿瀹氫箟
鈹溾攢鈹€ secrets.yaml                # 瀵嗛挜绠＄悊
鈹溾攢鈹€ configmap.yaml              # 閰嶇疆鏂囦欢
鈹溾攢鈹€ storage-class.yaml          # 瀛樺偍绫?
鈹溾攢鈹€ mongodb/
鈹?  鈹溾攢鈹€ statefulset.yaml        # MongoDB StatefulSet
鈹?  鈹溾攢鈹€ service.yaml            # MongoDB Service
鈹?  鈹溾攢鈹€ pvc.yaml                # 鎸佷箙鍖栧嵎澹版槑
鈹?  鈹斺攢鈹€ init-replica-set.yaml   # 鍓湰闆嗗垵濮嬪寲
鈹溾攢鈹€ redis/
鈹?  鈹溾攢鈹€ deployment.yaml         # Redis Deployment
鈹?  鈹溾攢鈹€ service.yaml            # Redis Service
鈹?  鈹斺攢鈹€ pvc.yaml                # Redis PVC
鈹溾攢鈹€ api/
鈹?  鈹溾攢鈹€ deployment.yaml         # API Deployment
鈹?  鈹溾攢鈹€ service.yaml            # API Service
鈹?  鈹溾攢鈹€ hpa.yaml                # 姘村钩鑷姩鎵╃缉
鈹?  鈹斺攢鈹€ pdb.yaml                # Pod 涓柇棰勭畻
鈹溾攢鈹€ web/
鈹?  鈹溾攢鈹€ deployment.yaml         # Web Deployment
鈹?  鈹溾攢鈹€ service.yaml            # Web Service
鈹?  鈹斺攢鈹€ ingress.yaml            # Ingress 閰嶇疆
鈹溾攢鈹€ monitoring/
鈹?  鈹溾攢鈹€ prometheus/
鈹?  鈹?  鈹溾攢鈹€ deployment.yaml
鈹?  鈹?  鈹溾攢鈹€ service.yaml
鈹?  鈹?  鈹斺攢鈹€ configmap.yaml
鈹?  鈹斺攢鈹€ grafana/
鈹?      鈹溾攢鈹€ deployment.yaml
鈹?      鈹溾攢鈹€ service.yaml
鈹?      鈹斺攢鈹€ dashboards-configmap.yaml
鈹溾攢鈹€ network-policy.yaml         # 缃戠粶绛栫暐
鈹斺攢鈹€ rbac/
    鈹溾攢鈹€ service-account.yaml
    鈹斺攢鈹€ role-binding.yaml
```

---

## 馃彈锔?鏍稿績璧勬簮閰嶇疆

### 鍛藉悕绌洪棿

**鏂囦欢:** `k8s/namespace.yaml`

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

### 瀵嗛挜绠＄悊

**鏂囦欢:** `k8s/secrets.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: materials-secrets
  namespace: materials-system
type: Opaque
stringData:
  # 鏁版嵁搴撳嚟鎹?
  mongo-root-username: admin
  mongo-root-password: "CHANGE_ME_SECURE_PASSWORD"
  mongo-connection-string: "mongodb://admin:CHANGE_ME_SECURE_PASSWORD@mongodb-0.mongodb:27017,mongodb-1.mongodb:27017,mongodb-2.mongodb:27017/materials?replicaSet=rs0"
  
  # Redis 瀵嗙爜
  redis-password: "CHANGE_ME_REDIS_PASSWORD"
  
  # API 瀵嗛挜
  api-key: "CHANGE_ME_API_KEY"
  
  # Grafana 绠＄悊鍛樺瘑鐮?
  grafana-admin-password: "CHANGE_ME_GRAFANA_PASSWORD"
  
  # TLS 璇佷功 (濡傛灉浣跨敤 HTTPS)
  tls-cert: |
    -----BEGIN CERTIFICATE-----
    ...
    -----END CERTIFICATE-----
  tls-key: |
    -----BEGIN PRIVATE KEY-----
    ...
    -----END PRIVATE KEY-----
```

**鍒涘缓鍛戒护:**
```bash
# 浠庡瓧闈㈠€煎垱寤?Secret
kubectl create secret generic materials-secrets \
  --from-literal=mongo-root-username=admin \
  --from-literal=mongo-root-password=$(openssl rand -base64 32) \
  --from-literal=redis-password=$(openssl rand -base64 32) \
  --from-literal=api-key=$(openssl rand -base64 32) \
  --from-literal=grafana-admin-password=$(openssl rand -base64 32) \
  -n materials-system

# 鎴栦粠鏂囦欢鍒涘缓
kubectl create secret generic materials-secrets \
  --from-file=.env \
  -n materials-system
```

### 閰嶇疆涓績

**鏂囦欢:** `k8s/configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: materials-config
  namespace: materials-system
data:
  # 搴旂敤閰嶇疆
  LOG_LEVEL: "info"
  ENVIRONMENT: "production"
  
  # 鏁版嵁搴撻厤缃?
  DATABASE_NAME: "materials"
  DATABASE_PORT: "27017"
  
  # Redis 閰嶇疆
  REDIS_HOST: "redis"
  REDIS_PORT: "6379"
  
  # API 閰嶇疆
  API_RATE_LIMIT: "100"
  API_TIMEOUT: "30"
  
  # ML 妯″瀷閰嶇疆
  MODEL_CACHE_SIZE: "1000"
  MODEL_PATH: "/app/models"
  
  # 鐩戞帶閰嶇疆
  PROMETHEUS_ENABLED: "true"
  METRICS_PORT: "8080"
  
  # Nginx 閰嶇疆
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

## 馃梽锔?鏁版嵁搴撻儴缃?

### MongoDB StatefulSet

**鏂囦欢:** `k8s/mongodb/statefulset.yaml`

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
# MongoDB 鍓湰闆嗗垵濮嬪寲 Job
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

**鏂囦欢:** `k8s/mongodb/service.yaml`

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

## 馃殌 API 鏈嶅姟閮ㄧ讲

### API Deployment

**鏂囦欢:** `k8s/api/deployment.yaml`

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

**鏂囦欢:** `k8s/api/service.yaml`

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

### 姘村钩鑷姩鎵╃缉 (HPA)

**鏂囦欢:** `k8s/api/hpa.yaml`

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

### Pod 涓柇棰勭畻 (PDB)

**鏂囦欢:** `k8s/api/pdb.yaml`

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

## 馃寪 Web 鐣岄潰涓?Ingress

### Web Deployment

**鏂囦欢:** `k8s/web/deployment.yaml`

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

### Ingress 閰嶇疆

**鏂囦欢:** `k8s/web/ingress.yaml`

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

## 馃搳 鐩戞帶閮ㄧ讲

### Prometheus 閰嶇疆

**鏂囦欢:** `k8s/monitoring/prometheus/deployment.yaml`

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

### Grafana Dashboard 閰嶇疆

**鏂囦欢:** `k8s/monitoring/grafana/dashboards-configmap.yaml`

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

## 馃殌 閮ㄧ讲娴佺▼

### 姝ラ 1: 鍓嶇疆鍑嗗

```bash
# 纭繚 kubectl 宸查厤缃?
kubectl config current-context

# 鍒涘缓鍛藉悕绌洪棿
kubectl apply -f k8s/namespace.yaml

# 鍒涘缓 Secret
kubectl apply -f k8s/secrets.yaml

# 鍒涘缓 ConfigMap
kubectl apply -f k8s/configmap.yaml

# 鍒涘缓瀛樺偍绫?(濡傛灉闇€瑕?
kubectl apply -f k8s/storage-class.yaml
```

### 姝ラ 2: 閮ㄧ讲鍩虹璁炬柦

```bash
# 閮ㄧ讲 MongoDB
kubectl apply -f k8s/mongodb/

# 閮ㄧ讲 Redis
kubectl apply -f k8s/redis/

# 绛夊緟鍩虹璁炬柦灏辩华
kubectl wait --for=condition=ready pod -l app=mongodb -n materials-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n materials-system --timeout=120s
```

### 姝ラ 3: 閮ㄧ讲搴旂敤鏈嶅姟

```bash
# 閮ㄧ讲 API 鏈嶅姟
kubectl apply -f k8s/api/

# 閮ㄧ讲 Web 鐣岄潰
kubectl apply -f k8s/web/

# 閮ㄧ讲鐩戞帶
kubectl apply -f k8s/monitoring/

# 閮ㄧ讲缃戠粶绛栫暐
kubectl apply -f k8s/network-policy.yaml
```

### 姝ラ 4: 楠岃瘉閮ㄧ讲

```bash
# 鏌ョ湅鎵€鏈?Pod 鐘舵€?
kubectl get pods -n materials-system

# 鏌ョ湅鏈嶅姟
kubectl get svc -n materials-system

# 鏌ョ湅 Ingress
kubectl get ingress -n materials-system

# 鏌ョ湅 API Pod 鏃ュ織
kubectl logs -f deployment/materials-api -n materials-system

# 娴嬭瘯 API 绔偣
kubectl port-forward svc/materials-api 8080:8080 -n materials-system
curl http://localhost:8080/api/v1/health
```

### 姝ラ 5: 閰嶇疆 DNS 鍜?TLS

```bash
# 瀹夎 cert-manager (濡傛灉鏈畨瑁?
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml

# 鍒涘缓 ClusterIssuer
kubectl apply -f k8s/ingress/cluster-issuer.yaml

# 绛夊緟璇佷功绛惧彂
kubectl get certificate -n materials-system
```

---

## 馃攳 杩愮淮鍛戒护

### 鏌ョ湅鐘舵€?

```bash
# 鏌ョ湅鎵€鏈夎祫婧?
kubectl get all -n materials-system

# 鏌ョ湅 Pod 璇︽儏
kubectl describe pod <pod-name> -n materials-system

# 鏌ョ湅浜嬩欢
kubectl get events -n materials-system --sort-by='.lastTimestamp'
```

### 鎵╃缉瀹?

```bash
# 鎵嬪姩鎵╃缉瀹?
kubectl scale deployment materials-api --replicas=5 -n materials-system

# 鏌ョ湅 HPA 鐘舵€?
kubectl get hpa -n materials-system
```

### 婊氬姩鏇存柊

```bash
# 鏇存柊闀滃儚
kubectl set image deployment/materials-api api-service=materials-api:v2.0 -n materials-system

# 鏌ョ湅鏇存柊鐘舵€?
kubectl rollout status deployment/materials-api -n materials-system

# 鍥炴粴
kubectl rollout undo deployment/materials-api -n materials-system

# 鏌ョ湅鍘嗗彶
kubectl rollout history deployment/materials-api -n materials-system
```

### 鏁呴殰鎺掓煡

```bash
# 杩涘叆 Pod
kubectl exec -it <pod-name> -n materials-system -- bash

# 鏌ョ湅鏃ュ織
kubectl logs <pod-name> -n materials-system
kubectl logs <pod-name> -c <container-name> -n materials-system

# 绔彛杞彂
kubectl port-forward <pod-name> 8080:8080 -n materials-system

# 娴嬭瘯缃戠粶
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://materials-api:8080/api/v1/health
```

---

## 馃搱 鐩戞帶涓庡憡璀?

### Prometheus 鏌ヨ绀轰緥

```promql
# API 璇锋眰鐜?
rate(http_requests_total{namespace="materials-system"}[5m])

# P95 鍝嶅簲鏃堕棿
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# 閿欒鐜?
sum(rate(http_requests_total{status=~"5..", namespace="materials-system"}[5m])) 
/ 
sum(rate(http_requests_total{namespace="materials-system"}[5m]))

# MongoDB 杩炴帴鏁?
mongodb_ss_connections{conn_type="current"}

# Redis 鍐呭瓨浣跨敤
redis_memory_used_bytes
```

### 鍛婅瑙勫垯

**鏂囦欢:** `k8s/monitoring/prometheus/alerts.yaml`

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

## 馃攼 瀹夊叏鏈€浣冲疄璺?

1. **浣跨敤 RBAC 闄愬埗鏉冮檺**
2. **鍚敤 NetworkPolicy 闅旂缃戠粶**
3. **浣跨敤 Secret 绠＄悊鏁忔劅淇℃伅**
4. **鍚敤 Pod Security Standards**
5. **瀹氭湡鎵弿闀滃儚婕忔礊**
6. **鍚敤瀹¤鏃ュ織**
7. **闄愬埗瀹瑰櫒璧勬簮**
8. **浣跨敤鍙鏂囦欢绯荤粺 (濡傚彲鑳?**

---

*鏈€鍚庢洿鏂帮細2026-03-05 19:35*

---

## 馃敊 Backlinks

**Documents linking here:**
- [[15-docs\LINK_INDEX]] - LINK_INDEX

