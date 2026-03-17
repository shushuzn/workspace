# 閮ㄧ讲鎸囧崡

**鐗堟湰:** v2.0  
**鍒涘缓鏃堕棿:** 2026-03-05 18:50  

---

## 馃搵 姒傝堪

鏈寚鍗椾粙缁嶅浣曢儴缃?AI Research OS銆?

---

## 馃殌 蹇€熼儴缃?

### 鏂规硶 1: 涓€閿儴缃?

```bash
# 閮ㄧ讲
./deploy.sh

# 鍋滄
./stop.sh

# 澶囦唤
./backup.sh
```

### 鏂规硶 2: 鎵嬪姩閮ㄧ讲

```bash
# 1. 瀹夎渚濊禆
pip install -r requirements.txt

# 2. 鍒涘缓鐩綍
mkdir -p logs scripts/cache data pids

# 3. 鍚姩 API 鏈嶅姟
python scripts/api/api-gateway.py > logs/api-gateway.log 2>&1 &
echo $! > pids/api.pid

# 4. 鍚姩鐩戞帶鏈嶅姟
python scripts/monitoring/enhanced_monitoring.py > logs/monitoring.log 2>&1 &
echo $! > pids/monitor.pid

# 5. 妫€鏌ュ仴搴风姸鎬?
curl http://localhost:5000/api/v1/health
```

---

## 馃敡 閰嶇疆

### 閰嶇疆鏂囦欢

```yaml
# config.yaml
global:
  version: "2.0"

security:
  api_key: "your-api-key"

paths:
  workspace: "D:\\OpenClaw\\workspace"
  logs: "logs"
  cache: "scripts/cache"
```

---

## 馃搳 楠岃瘉閮ㄧ讲

### 鍋ュ悍妫€鏌?

```bash
curl http://localhost:5000/api/v1/health
```

棰勬湡杈撳嚭:
```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

### 鏌ョ湅鏃ュ織

```bash
# API 鏃ュ織
tail -f logs/api-gateway.log

# 鐩戞帶鏃ュ織
tail -f logs/monitoring.log

# 鎭㈠鏃ュ織
tail -f logs/auto-recovery.log
```

---

## 馃攧 鍗囩骇

```bash
# 1. 鍋滄鏈嶅姟
./stop.sh

# 2. 澶囦唤鏁版嵁
./backup.sh

# 3. 鎷夊彇鏈€鏂颁唬鐮?
git pull

# 4. 瀹夎鏂颁緷璧?
pip install -r requirements.txt

# 5. 鍚姩鏈嶅姟
./deploy.sh
```

---

## 馃洜锔?鏁呴殰鎺掗櫎

### 鏈嶅姟鏃犳硶鍚姩

```bash
# 妫€鏌ョ鍙ｅ崰鐢?
netstat -ano | findstr :5000

# 妫€鏌ユ棩蹇?
tail -f logs/api-gateway.log
```

### 鏁版嵁搴撹繛鎺ュけ璐?

```bash
# 妫€鏌ユ暟鎹簱鐘舵€?
# TODO: 瀹炵幇鏁版嵁搴撶姸鎬佹鏌?
```

---

*鏈€鍚庢洿鏂帮細2026-03-05 18:50*

---

## 馃敊 Backlinks

**Documents linking here:**
- [[README]] - README
- [[15-docs\LINK_INDEX]] - LINK_INDEX

