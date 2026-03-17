# 鏁呴殰鎺掗櫎鎸囧崡

**鐗堟湰:** v2.0  
**鍒涘缓鏃堕棿:** 2026-03-05 18:00  
**鐘舵€?** 馃煝 鐢熶骇灏辩华

---

## 馃攳 璇婃柇娴佺▼

### 1. 鏀堕泦淇℃伅
```bash
# 绯荤粺淇℃伅
uname -a
python --version

# 鏈嶅姟鐘舵€?
ps aux | grep python

# 鏃ュ織妫€鏌?
tail -100 logs/*.log
```

### 2. 瀹氫綅闂
- API 闂 鈫?鏌ョ湅 `api-gateway.log`
- 璐ㄩ噺闂 鈫?鏌ョ湅 `quality-control.log`
- 鐩戞帶闂 鈫?鏌ョ湅 `monitoring.log`

### 3. 瑙ｅ喅闂
- 鍙傝€冧笅鏂瑰父瑙侀棶棰?
- 鏌ョ湅鏃ュ織璇︾粏淇℃伅
- 鑱旂郴鏀寔鍥㈤槦

---

## 鈿狅笍 甯歌闂

### API 鐩稿叧

**Q1: API 杩斿洖 401 Unauthorized**
```bash
# 鍘熷洜锛氱己灏戞垨閿欒鐨?API Key
# 瑙ｅ喅锛?
curl -H "X-API-Key: your-correct-key" http://localhost:5000/api/v1/health
```

**Q2: API 杩斿洖 404 Not Found**
```bash
# 鍘熷洜锛氱鐐逛笉瀛樺湪鎴栨暟鎹枃浠剁己澶?
# 瑙ｅ喅锛?
# 1. 妫€鏌ョ鐐?URL
# 2. 妫€鏌ユ暟鎹枃浠舵槸鍚﹀瓨鍦?
ls -la data-lake/analytics/
```

**Q3: API 鍝嶅簲鎱?*
```bash
# 鍘熷洜锛氭暟鎹噺澶ф垨鎬ц兘闂
# 瑙ｅ喅锛?
# 1. 妫€鏌ョ郴缁熻祫婧?
top -o %MEM

# 2. 鍚敤缂撳瓨
# 3. 浼樺寲鏌ヨ
```

### 璐ㄩ噺鎺у埗鐩稿叧

**Q4: 璐ㄩ噺璇勫垎浣?*
```bash
# 鍘熷洜锛氭暟鎹川閲忛棶棰?
# 瑙ｅ喅锛?
# 1. 鏌ョ湅璐ㄩ噺鎶ュ憡
cat logs/quality-control.log

# 2. 妫€鏌ュ師濮嬫暟鎹?
cat obsidian-vault/Arxiv/daily/*/raw/papers.json | jq

# 3. 璋冩暣璐ㄩ噺闃堝€?
vim config.yaml
```

**Q5: 澶ч噺鏃犳晥璁烘枃**
```bash
# 鍘熷洜锛氭暟鎹簮闂鎴栭獙璇佽鍒欒繃涓?
# 瑙ｅ喅锛?
# 1. 妫€鏌ユ暟鎹簮
# 2. 璋冩暣楠岃瘉瑙勫垯
# 3. 鑱旂郴鏁版嵁婧愭敮鎸?
```

### 鐩戞帶鐩稿叧

**Q6: 鐩戞帶鏁版嵁涓虹┖**
```bash
# 鍘熷洜锛氱洃鎺ф湇鍔℃湭杩愯鎴栭厤缃敊璇?
# 瑙ｅ喅锛?
# 1. 妫€鏌ョ洃鎺ф湇鍔?
ps aux | grep monitoring

# 2. 妫€鏌ラ厤缃枃浠?
cat workflows/99-monitoring/config.yaml

# 3. 閲嶅惎鐩戞帶鏈嶅姟
python scripts/monitoring/monitoring-system.py
```

### 鎬ц兘鐩稿叧

**Q7: 鍐呭瓨浣跨敤杩囬珮**
```bash
# 鍘熷洜锛氭暟鎹姞杞借繃澶氭垨鍐呭瓨娉勬紡
# 瑙ｅ喅锛?
# 1. 閲嶅惎鏈嶅姟
# 2. 妫€鏌ュ唴瀛樹娇鐢?
ps aux | grep python

# 3. 鍚敤鍒嗛〉鍔犺浇
# 4. 鑱旂郴寮€鍙戝洟闃?
```

**Q8: 纾佺洏绌洪棿涓嶈冻**
```bash
# 鍘熷洜锛氭棩蹇楁垨鏁版嵁绉疮
# 瑙ｅ喅锛?
# 1. 娓呯悊鏃ф棩蹇?
find logs/ -name "*.log" -mtime +30 -delete

# 2. 娓呯悊鏃ф暟鎹?
find data-lake/ -mtime +90 -delete

# 3. 鎵╁纾佺洏
```

---

## 馃洜锔?楂樼骇璇婃柇

### 鍚敤璋冭瘯妯″紡
```bash
# API 鏈嶅姟
export FLASK_DEBUG=1
python scripts/api/api-gateway.py

# 璐ㄩ噺鎺у埗
export LOG_LEVEL=DEBUG
python scripts/level-0/quality-controller.py
```

### 鎬ц兘鍒嗘瀽
```bash
# Python 鎬ц兘鍒嗘瀽
python -m cProfile -o output.prof scripts/api/api-gateway.py

# 鏌ョ湅鍒嗘瀽缁撴灉
python -m pstats output.prof
```

### 鍐呭瓨鍒嗘瀽
```bash
# 浣跨敤 memory_profiler
pip install memory_profiler
python -m memory_profiler scripts/api/api-gateway.py
```

---

## 馃摓 鑾峰彇甯姪

### 鏃ュ織浣嶇疆
- API 鏃ュ織锛歚logs/api-gateway.log`
- 璐ㄩ噺鏃ュ織锛歚logs/quality-control.log`
- 鐩戞帶鏃ュ織锛歚logs/monitoring.log`

### 閰嶇疆鏂囦欢
- 鍏ㄥ眬閰嶇疆锛歚config/global.yaml`
- API 閰嶇疆锛歚workflows/96-api-service/config.yaml`
- 鐩戞帶閰嶇疆锛歚workflows/99-monitoring/config.yaml`

### 鏀寔娓犻亾
- GitHub Issues: https://github.com/shushuzn/obsidian-sync/issues
- 鏂囨。锛歨ttps://github.com/shushuzn/obsidian-sync/docs

---

*鏈€鍚庢洿鏂帮細2026-03-05 18:00*

---

## 馃敊 Backlinks

**Documents linking here:**
- [[15-docs\LINK_INDEX]] - LINK_INDEX

