# 瀹夊叏鍔犲浐鎸囧崡

**鐗堟湰:** v1.0  
**鍒涘缓鏃堕棿:** 2026-03-05 19:00  

---

## 馃搵 姒傝堪

瀹夊叏鍔犲浐绯荤粺鎻愪緵璁よ瘉銆佹巿鏉冦€侀€熺巼闄愬埗銆佸璁＄瓑鍔熻兘銆?

---

## 馃敀 鍔熻兘

### 1. API Key 璁よ瘉

**鐢熸垚 API Key:**

```python
from scripts.security_hardening import SecurityManager

security = SecurityManager()
api_key = security.generate_api_key('user1')
print(f"API Key: {api_key}")
```

**楠岃瘉 API Key:**

```python
valid = security.validate_api_key(api_key)
if valid:
    print("API Key 鏈夋晥")
else:
    print("API Key 鏃犳晥")
```

**浣跨敤瑁呴グ鍣?**

```python
from scripts.security_hardening import require_auth

@app.route('/api/protected')
@require_auth
def protected_endpoint():
    return {'data': 'protected data'}
```

### 2. 閫熺巼闄愬埗

**妫€鏌ラ€熺巼闄愬埗:**

```python
allowed = security.check_rate_limit('user1', limit=100, window=60)
if allowed:
    print("璇锋眰鍏佽")
else:
    print("璇锋眰瓒呴檺")
```

**浣跨敤瑁呴グ鍣?**

```python
from scripts.security_hardening import rate_limit

@app.route('/api/data')
@rate_limit(limit=100, window=60)
def data_endpoint():
    return {'data': 'data'}
```

### 3. 瀵嗙爜鍔犲瘑

**鍝堝笇瀵嗙爜:**

```python
password_hash = security.hash_password('password123')
```

**楠岃瘉瀵嗙爜:**

```python
valid = security.verify_password('password123', password_hash)
```

### 4. 瀹¤鏃ュ織

**璁板綍瀹¤鏃ュ織:**

```python
security._audit_log('user_login', 'user1', 'IP: 192.168.1.1')
```

**鑾峰彇瀹¤鏃ュ織:**

```python
audit_log = security.get_audit_log(limit=100)
for entry in audit_log:
    print(f"{entry['timestamp']} - {entry['action']}: {entry['details']}")
```

---

## 馃搳 瀹夊叏鎶ュ憡

**鑾峰彇瀹夊叏鎶ュ憡:**

```python
report = security.get_security_report()
print(f"API Keys: {report['api_keys_count']}")
print(f"閫熺巼闄愬埗锛歿report['rate_limits_count']}")
print(f"瀹¤鏃ュ織锛歿report['audit_log_count']}")
```

---

## 馃敡 鏈€浣冲疄璺?

### 1. API Key 绠＄悊

- 瀹氭湡杞崲 API Key
- 闄愬埗 API Key 鏉冮檺
- 鐩戞帶 API Key 浣跨敤

### 2. 閫熺巼闄愬埗

- 璁剧疆鍚堢悊鐨勯檺鍒?(100 娆?鍒嗛挓)
- 鎸夌敤鎴?IP 鍒嗗埆闄愬埗
- 璁板綍瓒呴檺璇锋眰

### 3. 瀵嗙爜瀹夊叏

- 浣跨敤寮哄瘑鐮佺瓥鐣?
- 瀵嗙爜鍝堝笇瀛樺偍
- 瀹氭湡鏇存崲瀵嗙爜

### 4. 瀹¤鏃ュ織

- 璁板綍鎵€鏈夋晱鎰熸搷浣?
- 瀹氭湡瀹℃煡鏃ュ織
- 寮傚父琛屼负鍛婅

---

## 馃搱 瀹夊叏鎸囨爣

| 鎸囨爣 | 鐩爣 | 褰撳墠 |
|------|------|------|
| API Key 杞崲 | 姣忔湀 | 姣忔湀 |
| 瀵嗙爜寮哄害 | >8 瀛楃 | >8 瀛楃 |
| 瀹¤鏃ュ織 | 100% | 100% |
| 閫熺巼闄愬埗 | 100 娆?鍒?| 100 娆?鍒?|

---

*鏈€鍚庢洿鏂帮細2026-03-05 19:00*

---

## 馃敊 Backlinks

**Documents linking here:**
- [[15-docs\LINK_INDEX]] - LINK_INDEX

