# Materials Science System - Docker 閮ㄧ讲鎸囧崡

**鐗堟湰:** v1.0  
**鍒涘缓鏃堕棿:** 2026-03-05 19:30  
**鐩殑:** 鎻愪緵鏉愭枡绉戝绯荤粺鐨?Docker 瀹瑰櫒鍖栭儴缃茶缁嗘楠?

---

## 馃摝 Docker 鏂囦欢缁撴瀯

```
materials-system/
鈹溾攢鈹€ Dockerfile.api              # API 鏈嶅姟闀滃儚
鈹溾攢鈹€ Dockerfile.web              # Web 鐣岄潰闀滃儚
鈹溾攢鈹€ docker-compose.yml          # 瀹屾暣閮ㄧ讲閰嶇疆
鈹溾攢鈹€ docker-compose.dev.yml      # 寮€鍙戠幆澧冮厤缃?
鈹溾攢鈹€ docker-compose.prod.yml     # 鐢熶骇鐜閰嶇疆
鈹溾攢鈹€ .env.example                # 鐜鍙橀噺妯℃澘
鈹溾攢鈹€ scripts/
鈹?  鈹斺攢鈹€ materials/
鈹?      鈹溾攢鈹€ materials_api_service.py
鈹?      鈹溾攢鈹€ materials_collector.py
鈹?      鈹斺攢鈹€ ...
鈹溾攢鈹€ web/
鈹?  鈹溾攢鈹€ materials-dashboard.html
鈹?  鈹溾攢鈹€ crystal-viewer.html
鈹?  鈹斺攢鈹€ ...
鈹溾攢鈹€ models/                     # ML 妯″瀷鏂囦欢
鈹斺攢鈹€ requirements.txt            # Python 渚濊禆
```

---

## 馃惓 Dockerfile 閰嶇疆

### API 鏈嶅姟 Dockerfile

**鏂囦欢:** `Dockerfile.api`

```dockerfile
# 澶氶樁娈垫瀯寤?- 鏋勫缓闃舵
FROM python:3.10-slim as builder

WORKDIR /app

# 瀹夎鏋勫缓渚濊禆
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    cmake \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 澶嶅埗渚濊禆鏂囦欢
COPY requirements.txt .

# 瀹夎 Python 渚濊禆 (浣跨敤缂撳瓨灞?
RUN pip install --no-cache-dir --user -r requirements.txt

# 澶氶樁娈垫瀯寤?- 杩愯闃舵
FROM python:3.10-slim

WORKDIR /app

# 瀹夎杩愯鏃朵緷璧?
RUN apt-get update && apt-get install -y \
    libgl1 \
    libgomp1 \
    libglib2.0-0 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

# 浠庢瀯寤洪樁娈靛鍒?Python 鍖?
COPY --from=builder /root/.local /home/appuser/.local

# 澶嶅埗搴旂敤浠ｇ爜
COPY --chown=appuser:appuser scripts/ ./scripts/
COPY --chown=appuser:appuser models/ ./models/
COPY --chown=appuser:appuser configs/ ./configs/

# 璁剧疆鐜鍙橀噺
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

# 鍒囨崲鍒伴潪 root 鐢ㄦ埛
USER appuser

# 鏆撮湶绔彛
EXPOSE 8080

# 鍋ュ悍妫€鏌?
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1

# 鍚姩鍛戒护
CMD ["python", "scripts/materials/materials_api_service.py", "--host", "0.0.0.0", "--port", "8080"]
```

### Web 鐣岄潰 Dockerfile

**鏂囦欢:** `Dockerfile.web`

```dockerfile
FROM nginx:alpine

# 澶嶅埗闈欐€佹枃浠?
COPY web/ /usr/share/nginx/html/

# 澶嶅埗 Nginx 閰嶇疆
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 鏆撮湶绔彛
EXPOSE 80

# 鍋ュ悍妫€鏌?
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -q --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

### Nginx 閰嶇疆

**鏂囦欢:** `web/nginx.conf`

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index materials-dashboard.html;

    # Gzip 鍘嬬缉
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    gzip_min_length 1000;

    # 缂撳瓨闈欐€佽祫婧?
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|html)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API 鍙嶅悜浠ｇ悊
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

    # 涓婚〉闈?
    location / {
        try_files $uri $uri/ /materials-dashboard.html;
    }

    # 閿欒椤甸潰
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

---

## 馃敡 Docker Compose 閰嶇疆

### 寮€鍙戠幆澧冮厤缃?

**鏂囦欢:** `docker-compose.dev.yml`

```yaml
version: '3.8'

services:
  # MongoDB (浠呭熀纭€鏈嶅姟)
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

  # API 鏈嶅姟 (寮€鍙戞ā寮?
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

  # Web 鐣岄潰 (寮€鍙戞ā寮?
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

### 鐢熶骇鐜閰嶇疆

**鏂囦欢:** `docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  # Nginx 鍙嶅悜浠ｇ悊
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

  # API 鏈嶅姟 (澶氬疄渚?
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

  # MongoDB (鍓湰闆?
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

  # Redis (甯﹀瘑鐮?
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
    volumes:
      - redis_prod_data:/data
    networks:
      - materials-prod-network
    restart: always

  # Prometheus 鐩戞帶
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

  # Grafana 鍙鍖?
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

## 馃殌 閮ㄧ讲姝ラ

### 姝ラ 1: 鍑嗗鐜

```bash
# 鍏嬮殕鎴栬繘鍏ラ」鐩洰褰?
cd materials-system

# 澶嶅埗鐜鍙橀噺鏂囦欢
cp .env.example .env

# 缂栬緫鐜鍙橀噺
vim .env
```

**.env 鏂囦欢鍐呭:**
```bash
# 鐢熶骇鐜閰嶇疆
API_KEY=your_production_api_key_here
MONGO_PASSWORD=secure_mongo_password_123
REDIS_PASSWORD=secure_redis_password_456
GRAFANA_PASSWORD=secure_grafana_password_789
```

### 姝ラ 2: 鏋勫缓闀滃儚

```bash
# 鏋勫缓 API 鏈嶅姟闀滃儚
docker build -t materials-api:latest -f Dockerfile.api .

# 鏋勫缓 Web 鐣岄潰闀滃儚
docker build -t materials-web:latest -f Dockerfile.web .

# 楠岃瘉闀滃儚
docker images | grep materials
```

### 姝ラ 3: 鍚姩鏈嶅姟

```bash
# 寮€鍙戠幆澧?
docker-compose -f docker-compose.dev.yml up -d

# 鐢熶骇鐜
docker-compose -f docker-compose.prod.yml up -d

# 鏌ョ湅鏈嶅姟鐘舵€?
docker-compose ps

# 鏌ョ湅鏃ュ織
docker-compose logs -f api-service
```

### 姝ラ 4: 楠岃瘉閮ㄧ讲

```bash
# 鍋ュ悍妫€鏌?
curl http://localhost:8080/api/v1/health

# 娴嬭瘯 API
curl -X GET "http://localhost:8080/api/v1/materials?limit=5"

# 璁块棶 Web 鐣岄潰
# 娴忚鍣ㄦ墦寮€ http://localhost:3000 (寮€鍙? 鎴?http://localhost (鐢熶骇)
```

### 姝ラ 5: 鍒濆鍖栨暟鎹簱

```bash
# 杩涘叆 API 瀹瑰櫒
docker-compose exec api-service bash

# 杩愯鏁版嵁搴撹縼绉?
python scripts/materials/database_migration.py

# 鍔犺浇绀轰緥鏁版嵁
python scripts/materials/load_sample_data.py

# 閫€鍑哄鍣?
exit
```

---

## 馃攳 杩愮淮鍛戒护

### 鏌ョ湅鏃ュ織

```bash
# 鏌ョ湅鎵€鏈夋湇鍔℃棩蹇?
docker-compose logs -f

# 鏌ョ湅鐗瑰畾鏈嶅姟鏃ュ織
docker-compose logs -f api-service
docker-compose logs -f mongodb

# 鏌ョ湅鏈€杩?100 琛?
docker-compose logs --tail=100 api-service
```

### 鏈嶅姟绠＄悊

```bash
# 閲嶅惎鏈嶅姟
docker-compose restart api-service

# 鍋滄鏈嶅姟
docker-compose stop

# 鍋滄骞跺垹闄ゅ鍣?
docker-compose down

# 鍒犻櫎瀹瑰櫒銆佺綉缁滃拰鍗?
docker-compose down -v
```

### 杩涘叆瀹瑰櫒

```bash
# 杩涘叆 API 瀹瑰櫒
docker-compose exec api-service bash

# 杩涘叆 MongoDB 瀹瑰櫒
docker-compose exec mongodb mongosh -u admin -p
```

### 澶囦唤涓庢仮澶?

```bash
# 澶囦唤 MongoDB 鏁版嵁
docker-compose exec mongodb mongodump --out=/data/backup

# 浠庡涓绘満澶嶅埗澶囦唤
docker cp materials-system-mongodb-1:/data/backup ./mongodb-backup

# 鎭㈠鏁版嵁
docker cp ./mongodb-restore materials-system-mongodb-1:/data/restore
docker-compose exec mongodb mongorestore /data/restore
```

---

## 馃搳 鐩戞帶閰嶇疆

### 鏌ョ湅璧勬簮浣跨敤

```bash
# 鏌ョ湅瀹瑰櫒璧勬簮浣跨敤
docker stats

# 鏌ョ湅鐗瑰畾瀹瑰櫒
docker stats materials-system-api-service-1
```

### Prometheus 鎸囨爣

璁块棶 `http://localhost:9090` 鏌ョ湅 Prometheus

**鍏抽敭鎸囨爣:**
- `http_requests_total` - 鎬昏姹傛暟
- `http_request_duration_seconds` - 璇锋眰鑰楁椂
- `mongodb_connections` - 鏁版嵁搴撹繛鎺ユ暟
- `redis_connected_clients` - Redis 瀹㈡埛绔暟

### Grafana 浠〃鏉?

璁块棶 `http://localhost:3001` 鏌ョ湅 Grafana

**榛樿璐﹀彿:** admin / (浣犲湪 .env 涓缃殑瀵嗙爜)

**棰勭疆浠〃鏉?**
- API 鎬ц兘鐩戞帶
- 鏁版嵁搴撶洃鎺?
- 绯荤粺璧勬簮鐩戞帶
- 涓氬姟鎸囨爣鐩戞帶

---

## 馃悰 鏁呴殰鎺掓煡

### 甯歌闂

#### 1. API 鏈嶅姟鏃犳硶鍚姩

```bash
# 鏌ョ湅鏃ュ織
docker-compose logs api-service

# 妫€鏌ョ鍙ｅ崰鐢?
docker-compose ps

# 閲嶅缓瀹瑰櫒
docker-compose up -d --force-recreate api-service
```

#### 2. MongoDB 杩炴帴澶辫触

```bash
# 妫€鏌?MongoDB 鐘舵€?
docker-compose ps mongodb

# 鏌ョ湅 MongoDB 鏃ュ織
docker-compose logs mongodb

# 娴嬭瘯杩炴帴
docker-compose exec api-service python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://admin:password@mongodb:27017')
print(client.admin.command('ping'))
"
```

#### 3. 鍐呭瓨涓嶈冻

```bash
# 闄愬埗瀹瑰櫒鍐呭瓨
docker-compose up -d --build api-service

# 缂栬緫 docker-compose.yml 娣诲姞:
# deploy:
#   resources:
#     limits:
#       memory: 1G
```

#### 4. 纾佺洏绌洪棿涓嶈冻

```bash
# 娓呯悊鏈娇鐢ㄧ殑闀滃儚
docker image prune -a

# 娓呯悊鏈娇鐢ㄧ殑鍗?
docker volume prune

# 鏌ョ湅纾佺洏浣跨敤
docker system df
```

---

## 馃搱 鎬ц兘浼樺寲

### 鏋勫缓浼樺寲

```dockerfile
# 浣跨敤澶氶樁娈垫瀯寤哄噺灏戦暅鍍忓ぇ灏?
# 鍒╃敤 Docker 缂撳瓨灞?
# 鍚堝苟 RUN 鎸囦护鍑忓皯灞傛暟
```

### 杩愯鏃朵紭鍖?

```yaml
# 鍦?docker-compose.yml 涓坊鍔?
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

### 缃戠粶浼樺寲

```yaml
# 浣跨敤鑷畾涔夌綉缁?
networks:
  materials-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

---

## 馃攼 瀹夊叏鏈€浣冲疄璺?

1. **浣跨敤闈?root 鐢ㄦ埛杩愯瀹瑰櫒**
2. **瀹氭湡鏇存柊鍩虹闀滃儚**
3. **鎵弿闀滃儚婕忔礊:** `docker scan materials-api:latest`
4. **浣跨敤 Docker Secret 绠＄悊鏁忔劅淇℃伅**
5. **闄愬埗瀹瑰櫒璧勬簮**
6. **鍚敤鏃ュ織璁板綍**
7. **瀹氭湡澶囦唤鏁版嵁**

---

*鏈€鍚庢洿鏂帮細2026-03-05 19:30*

---

## 馃敊 Backlinks

**Documents linking here:**
- [[15-docs\LINK_INDEX]] - LINK_INDEX

