# Docker 閮ㄧ讲鎸囧崡

**鐗堟湰:** v1.0  
**鍒涘缓鏃堕棿:** 2026-03-05 14:50  
**鐩殑:** Docker 閮ㄧ讲閰嶇疆鎸囧崡

---

## 馃摝 鏂囦欢缁撴瀯

```
D:\OpenClaw\workspace\
鈹溾攢鈹€ docker-compose.yml      # Docker 缂栨帓閰嶇疆
鈹溾攢鈹€ Dockerfile.api          # API 鏈嶅姟闀滃儚
鈹溾攢鈹€ requirements.txt        # Python 渚濊禆
鈹溾攢鈹€ nginx.conf              # Nginx 閰嶇疆
鈹溾攢鈹€ scripts/                # Python 鑴氭湰
鈹斺攢鈹€ web/                    # Web 椤甸潰
```

---

## 馃殌 蹇€熷惎鍔?

### 1. 鍚姩鎵€鏈夋湇鍔?

```bash
cd D:\OpenClaw\workspace
docker-compose up -d
```

### 2. 鏌ョ湅鏈嶅姟鐘舵€?

```bash
docker-compose ps
```

**棰勬湡杈撳嚭:**
```
NAME                STATUS              PORTS
workspace-api       Up                  0.0.0.0:8000->8000/tcp
workspace-mongodb   Up                  0.0.0.0:27017->27017/tcp
workspace-web       Up                  0.0.0.0:3000->80/tcp
workspace-redis     Up                  0.0.0.0:6379->6379/tcp
```

### 3. 鏌ョ湅鏃ュ織

```bash
# 鏌ョ湅鎵€鏈夋湇鍔℃棩蹇?
docker-compose logs -f

# 鏌ョ湅 API 鏃ュ織
docker-compose logs -f api

# 鏌ョ湅 MongoDB 鏃ュ織
docker-compose logs -f mongodb
```

### 4. 鍋滄鏈嶅姟

```bash
docker-compose down
```

### 5. 閲嶅惎鏈嶅姟

```bash
docker-compose restart
```

---

## 馃И 娴嬭瘯閮ㄧ讲

### 1. 娴嬭瘯 API 鍋ュ悍

```bash
curl http://localhost:8000/health
```

**棰勬湡鍝嶅簲:**
```json
{"status": "healthy", "timestamp": "2026-03-05T14:50:00"}
```

### 2. 娴嬭瘯 Web 椤甸潰

鎵撳紑娴忚鍣ㄨ闂?
- Web 鐣岄潰锛歨ttp://localhost:3000
- API 鏂囨。锛歨ttp://localhost:8000/docs

### 3. 娴嬭瘯 MongoDB 杩炴帴

```bash
docker-compose exec mongodb mongosh --eval "db.stats()"
```

---

## 馃敡 甯歌闂

### 1. 绔彛鍐茬獊

**閿欒:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**瑙ｅ喅:**
```bash
# 鍋滄鍗犵敤绔彛鐨勬湇鍔?
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# 鎴栬€呬慨鏀?docker-compose.yml 绔彛鏄犲皠
ports:
  - "8001:8000"  # 鏀逛负 8001
```

### 2. MongoDB 杩炴帴澶辫触

**閿欒:** `MongoDB connection failed`

**瑙ｅ喅:**
```bash
# 妫€鏌?MongoDB 鏄惁杩愯
docker-compose ps mongodb

# 閲嶅惎 MongoDB
docker-compose restart mongodb

# 鏌ョ湅 MongoDB 鏃ュ織
docker-compose logs mongodb
```

### 3. API 鏈嶅姟鍚姩澶辫触

**閿欒:** `Error starting API service`

**瑙ｅ喅:**
```bash
# 鏌ョ湅 API 鏃ュ織
docker-compose logs api

# 閲嶅缓 API 闀滃儚
docker-compose build api

# 閲嶅惎 API 鏈嶅姟
docker-compose restart api
```

---

## 馃搳 鐩戞帶

### 1. 鏌ョ湅璧勬簮浣跨敤

```bash
docker stats
```

### 2. 杩涘叆瀹瑰櫒

```bash
# 杩涘叆 API 瀹瑰櫒
docker-compose exec api bash

# 杩涘叆 MongoDB 瀹瑰櫒
docker-compose exec mongodb mongosh
```

### 3. 澶囦唤鏁版嵁

```bash
# 澶囦唤 MongoDB 鏁版嵁
docker-compose exec mongodb mongodump --out /backup

# 鎭㈠ MongoDB 鏁版嵁
docker-compose exec mongodb mongorestore /backup
```

---

## 馃搮 瀹炴柦璁″垝

| 浠诲姟 | 鐢ㄦ椂 | 鐘舵€?|
|------|------|------|
| Docker 閰嶇疆缂栧啓 | 2 灏忔椂 | 鉁?|
| docker-compose 閰嶇疆 | 1 灏忔椂 | 鉁?|
| 閮ㄧ讲娴嬭瘯 | 1 灏忔椂 | 馃搵 |
| 鏂囨。缂栧啓 | 1 灏忔椂 | 鉁?|

---

*鏈€鍚庢洿鏂帮細2026-03-05 14:50*

---

## 馃敊 Backlinks

**Documents linking here:**
- [[link-recommendations]] - link-recommendations

