# Medium 鏂囩珷鏀堕泦绯荤粺 - 鏀堕泦鏁寸悊鎶ュ憡

**鐢熸垚鏃堕棿:** 2026-03-02 18:38 (Asia/Hong_Kong)  
**浠诲姟:** 鏀堕泦鏁寸悊锛岃嫢鏃犲垯鎵╁ぇ鏀堕泦鑼冨洿

---

## 褰撳墠鏀堕泦鐘舵€?

### 鏁版嵁缁熻
| 鎸囨爣 | 鏁板€?|
|------|------|
| RSS 璁㈤槄婧?| 45 涓?|
| Obsidian 绗旇鎬绘暟 | 28 绡?|
| 浠婃棩鏂板绗旇 | 10+ 绡?|
| SQLite 鍘婚噸璁板綍 | 0 鏉?(鏂版竻鐞? |
| 鏂版枃绔犲彂鐜?(鏈鎵弿) | 0 绡?|

### 璁㈤槄婧愬垎绫?
| 绫诲埆 | 鏁伴噺 |
|------|------|
| AI/ML | 12 |
| 缂栫▼寮€鍙?| 10 |
| 鏁版嵁绉戝 | 6 |
| 绉戞妧鍗氬 (澶у巶) | 8 |
| UX/璁捐 | 3 |
| 鍒涗笟/鍟嗕笟 | 4 |
| 鍏朵粬鍦板尯 | 2 |

---

## 鏈鎵弿缁撴灉

**鏃堕棿:** 2026-03-02 18:38  
**鎵弿璁㈤槄婧?** 25 涓?(閮ㄥ垎)  
**鏂版枃绔?** 0 绡?

**鍘熷洜鍒嗘瀽:**
- 鎵€鏈夎闃呮簮褰撳墠鏃犳柊鏂囩珷
- 鎴栨枃绔犲凡鍦ㄤ箣鍓嶆敹闆?
- RSS 鏇存柊棰戠巼闄愬埗

---

## 绯荤粺缁勪欢鐘舵€?

| 缁勪欢 | 鐘舵€?| 璇存槑 |
|------|------|------|
| Watcher V1 | 鈿狅笍 杩愯涓?(鏈?bug) | normalize_url 鍑芥暟鎶ラ敊 |
| Watcher V2 | 鉁?灏辩华 | 鏂偣缁紶/鎵归噺妯″紡 |
| Watcher V3 | 鉁?灏辩华 | 杩涘害鍙鍖?閰嶇疆鐑噸杞?|
| RSS Collector | 鉁?姝ｅ父 | 5 鍒嗛挓妫€鏌ラ棿闅?|
| Healthcheck | 鉁?姝ｅ父 | 2.3 绉掑搷搴?|
| OpenClaw Gateway | 鉁?姝ｅ父 | Fallback 姝ｅ父 |

---

## 寰呬慨澶嶉棶棰?

### Watcher Bug
**鏂囦欢:** `D:\scripts\medium_watcher_event.py`  
**琛屽彿:** ~197  
**閿欒:** `ValueError: not enough values to unpack (expected 7, got 6)`  
**鍘熷洜:** `urlunparse` 鍙傛暟鏁伴噺閿欒

**淇寤鸿:**
```python
# 褰撳墠 (閿欒)
return urlunparse((scheme, netloc, path, "", ""))

# 淇 (6 涓弬鏁?
return urlunparse((scheme, netloc, path, "", "", ""))
```

---

## 鎵╁ぇ鏀堕泦鑼冨洿寤鸿

### 鏂规 A: 澧炲姞璁㈤槄婧?(鎺ㄨ崘)
鏂板浠ヤ笅楂樿川閲?RSS 婧?

1. **MIT Technology Review**
   - `https://www.technologyreview.com/feed/`

2. **Ars Technica**
   - `https://feeds.arstechnica.com/arstechnica/technology-lab`

3. **Hacker News (RSS)**
   - `https://hnrss.org/frontpage`

4. **Lobsters**
   - `https://lobste.rs/rss`

5. **ACM Queue**
   - `https://queue.acm.org/feed.cfm`

6. **IEEE Spectrum**
   - `https://spectrum.ieee.org/rss/feed`

### 鏂规 B: 闄嶄綆鏀堕泦闃堝€?
**褰撳墠閰嶇疆:** `minScoreToProcess: 3`  
**寤鸿璋冩暣:** `minScoreToProcess: 2`

**褰卞搷:** 鏀堕泦鏇村鏂囩珷锛屼絾闇€鍚庣画绛涢€?

### 鏂规 C: 澧炲姞妫€鏌ラ鐜?
**褰撳墠閰嶇疆:** `checkIntervalMinutes: 5`  
**寤鸿璋冩暣:** `checkIntervalMinutes: 3`

**褰卞搷:** 鏇村揩鍙戠幇鏂版枃绔狅紝澧炲姞 API 璋冪敤

### 鏂规 D: 鎵╁睍鏀堕泦骞冲彴
闄?Medium 澶栵紝澧炲姞浠ヤ笅骞冲彴:

1. **Substack** - 鎶€鏈被 Newsletter
2. **Dev.to** - 寮€鍙戣€呯ぞ鍖?
3. **Hashnode** - 寮€鍙戣€呭崥瀹?
4. **arXiv** - 瀛︽湳璁烘枃 (AI/ML)

---

## 涓嬩竴姝ヨ鍔?

### 绔嬪嵆鎵ц
- [ ] 淇 Watcher normalize_url bug
- [ ] 閲嶅惎 Watcher V3

### 鏈湡鎵ц
- [ ] 娣诲姞 6 涓柊 RSS 璁㈤槄婧?
- [ ] 娴嬭瘯鏂拌闃呮簮鎶撳彇
- [ ] 鏇存柊閰嶇疆鏂囦欢

### 涓嬫湡瑙勫垝
- [ ] 璇勪及 Substack/Dev.to 闆嗘垚
- [ ] 瀹炵幇鏂囩珷璐ㄩ噺鑷姩绛涢€?
- [ ] 娣诲姞缁熻闈㈡澘

---

**鎶ュ憡鐢熸垚瀹屾垚**  
涓嬫鑷姩妫€鏌ワ細2026-03-02 18:43

---

## 馃敊 Backlinks

**Documents linking here:**
- [[link-recommendations]] - link-recommendations

