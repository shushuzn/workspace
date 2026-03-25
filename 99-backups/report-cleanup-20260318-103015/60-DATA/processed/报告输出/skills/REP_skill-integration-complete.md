# 馃幆 鎶€鑳介泦鎴愬畬鎴愭姤鍛?

**鏃ユ湡:** 2026-03-04  
**宸ヤ綔绌洪棿:** D:\OpenClaw\workspace  
**鎵ц鑰?** AI Assistant

---

## 鉁?宸插畬鎴愭妧鑳介泦鎴?

### 1锔忊儯 璇箟鎼滅储 (knowledge-graph)

**鐘舵€?** 鉁?瀹屾垚  
**鎶€鑳借矾寰?** `D:\npm-global\node_modules\openclaw\skills\knowledge-graph\`

**浜у嚭:**
- `knowledge-graph/graph.json` - JSON 鏍煎紡鍥捐氨
- `knowledge-graph/graph.graphml` - Gephi 鍏煎鏍煎紡
- `knowledge-graph/graph.mmd` - Mermaid 鍙鍖?

**缁熻:**
- 瀹炰綋鏁帮細11 (7 璁烘枃 + 4 姒傚康)
- 鍏崇郴鏁帮細0 (寰呭畬鍠勫叧绯绘娊鍙?

**鑴氭湰:**
- `kg-builder.py` - 鍥捐氨鏋勫缓鍣?

---

### 2锔忊儯 鑷姩鍖栫爺绌跺姪鎵?(ai-research-os)

**鐘舵€?** 鉁?瀹屾垚  
**鎶€鑳借矾寰?** `D:\npm-global\node_modules\openclaw\skills\ai-research-os\`

**浜у嚭:**
- `D:\obsidian\Vault\Medium\P-*.md` - 10 绡?P-Note
- 瀹屾暣鐮旂┒娴佺▼ (Research Question 鈫?Decision)
- 瀵规姉寮忓绋挎ā鏉?

**鏍稿績鍔熻兘:**
- 鍗曠瘒璁烘枃娣卞害瑙ｆ瀽
- 澶氱瘒璁烘枃瀵规瘮鍒嗘瀽
- 鎶€鏈富棰樼爺绌?
- 鑷姩鐢熸垚鐮旂┒绗旇骞跺悓姝?GitHub

**鑴氭湰:**
- `arxiv-batch-processor.py` - 鎵归噺璁烘枃瑙ｆ瀽鍣?
- 鏀寔瀛愪唬鐞嗗苟琛屽鐞?(鏁堢巼 +70%)

---

### 3锔忊儯 鐭ヨ瘑鍥捐氨鍙鍖?(knowledge-graph-builder)

**鐘舵€?** 鉁?瀹屾垚  
**鎶€鑳借矾寰?** `D:\npm-global\node_modules\openclaw\skills\knowledge-graph-builder\`

**鏂板鑴氭湰:**
- `visualize.py` - D3.js 浜や簰寮忓彲瑙嗗寲鐢熸垚鍣?
- `query.py` - 鍥捐氨鏌ヨ寮曟搸

**浜у嚭:**
- `knowledge-graph/visualization/index.html` - D3.js 浜や簰寮忕綉缁滃浘
- `knowledge-graph/visualization/analysis.md` - 鍥捐氨鍒嗘瀽鎶ュ憡

**鍔熻兘:**
- 浜や簰寮忚妭鐐规嫋鎷?缂╂斁
- 宸ュ叿鎻愮ず鏄剧ず璇︽儏
- 鍥句緥鏍囪瘑瀹炰綋绫诲瀷
- PageRank 涓績鎬у垎鏋?
- 绀惧尯妫€娴?(Louvain 绠楁硶)

**鏌ヨ璇█:**
- `path:A鈫払` - 璺緞鏌ヨ
- `rank:pagerank --top 10` - 褰卞搷鍔涙帓鍚?
- `subgraph:Seed --depth 2` - 瀛愬浘鎻愬彇
- `evolution:Concept --years 2017-2026` - 鏃堕棿婕旇繘

---

### 4锔忊儯 缁熻鐪嬫澘 (research-stats)

**鐘舵€?** 鉁?瀹屾垚  
**鑴氭湰璺緞:** `D:\OpenClaw\workspace\scripts\research-stats.py`

**浜у嚭:**
- `reports/research-stats-2026-03-04.md` - 缁熻鎶ュ憡

**缁熻缁村害:**
- P-Note 鏀堕泦缁熻 (鎬绘暟/骞翠唤/鏍囩)
- C-Note 绠＄悊缁熻
- M-Note 瑙﹀彂缁熻
- 鐭ヨ瘑鍥捐氨缁熻 (瀹炰綋/鍏崇郴/绫诲瀷)
- 璁板繂鏂囦欢缁熻
- 绯荤粺鍋ュ悍搴﹁瘎浼?

**褰撳墠绯荤粺鐘舵€?**

| 缁勪欢 | 鐘舵€?| 鏁板€?|
|------|------|------|
| P-Note 鏀堕泦 | 鉁?| 10 绡?|
| C-Note 绠＄悊 | 鈿狅笍 | 0 绡?|
| M-Note 瑙﹀彂 | 鈿狅笍 | 0 绡?|
| 鐭ヨ瘑鍥捐氨 | 鉁?| 11 瀹炰綋 |
| 璁板繂绯荤粺 | 鉁?| 15 绡?|

---

## 馃搳 闆嗘垚鏁堟灉瀵规瘮

### 闆嗘垚鍓?(妗岄潰鐗?ai_research_os)

- 鉂?绾挎€х瑪璁帮紝鏃犵煡璇嗙綉缁?
- 鉂?鎵嬪姩杩愯锛屾棤鑷姩鍖?
- 鉂?鏃犲彲瑙嗗寲
- 鉂?鏃犵粺璁＄洃鎺?
- 鉂?鍗曠瘒澶勭悊锛屾晥鐜囦綆

### 闆嗘垚鍚?(OpenClaw 鎶€鑳界敓鎬?

- 鉁?鐭ヨ瘑鍥捐氨 + 绗旇鍙岃建鍒?
- 鉁?瀹氭椂浠诲姟 + 蹇冭烦妫€鏌?
- 鉁?D3.js 浜や簰寮忓彲瑙嗗寲
- 鉁?鑷姩鍖栫粺璁＄湅鏉?
- 鉁?瀛愪唬鐞嗗苟琛屽鐞?(鏁堢巼 +70%)
- 鉁?GitHub 鑷姩鍚屾
- 鉁?瀹夊叏瀹¤ (13 椤规寚鏍?
- 鉁?澶氭簮淇℃伅鏀堕泦 (璁烘枃 + Medium + HN)

---

## 馃殌 鏍稿績澧炲€肩偣

### 1. 鐭ヨ瘑琛ㄧず鍗囩骇
**浠庣嚎鎬у埌缃戠粶** - 鍙戠幇闅愯棌杩炴帴锛屾敮鎸佽矾寰勬煡璇㈠拰褰卞搷鍔涘垎鏋?

### 2. 澶勭悊鏁堢巼鎻愬崌
**瀛愪唬鐞嗗苟琛屾灦鏋?* - 4 绡囪鏂?~6 鍒嗛挓 (vs 涓茶 ~20+ 鍒嗛挓)

### 3. 鍙鍖栧寮?
**D3.js 浜や簰寮忓浘璋?* - 鎷栨嫿/缂╂斁/鎼滅储/楂樹寒璺緞

### 4. 鑷姩鍖栫▼搴?
**瀹氭椂浠诲姟 + 蹇冭烦** - 2am 鏀堕泦锛?am 瀹¤锛屾棤闇€鎵嬪姩骞查

### 5. 璐ㄩ噺淇濋殰
**13 椤瑰畨鍏ㄥ璁?* - OpenClaw/纾佺洏/Git/DLP/鎶€鑳藉畬鏁存€?

---

## 馃搱 浣跨敤鎸囧崡

### 鏋勫缓鐭ヨ瘑鍥捐氨

```bash
py D:\npm-global\node_modules\openclaw\skills\knowledge-graph\scripts\kg-builder.py ^
  --input memory\*.md topics\*.md ^
  --output knowledge-graph\graph.json ^
  --format all
```

### 鐢熸垚鍙鍖?

```bash
py D:\npm-global\node_modules\openclaw\skills\knowledge-graph-builder\scripts\visualize.py ^
  --graph knowledge-graph\graph.json ^
  --output knowledge-graph\visualization\
```

### 鏌ヨ鍥捐氨

```bash
py D:\npm-global\node_modules\openclaw\skills\knowledge-graph-builder\scripts\query.py ^
  --graph knowledge-graph\graph.json ^
  --query "rank:pagerank --top 10"
```

### 鐢熸垚缁熻鎶ュ憡

```bash
py D:\OpenClaw\workspace\scripts\research-stats.py ^
  --output reports\research-stats.md
```

---

## 鈿狅笍 寰呭畬鍠勯」

### 1. 鍏崇郴鎶藉彇浼樺寲
褰撳墠鍏崇郴鏁帮細0  
**鏀硅繘鏂瑰悜:**
- 澧炲己寮曠敤鍏崇郴璇嗗埆 (cites/extends/refutes)
- 浠庡弬鑰冩枃鐚彁鍙栧紩鐢ㄧ綉缁?
- 浠庡姣斿垎鏋愭彁鍙栧叧绯?

### 2. C-Note/M-Note 鑷姩鍖?
褰撳墠 C-Note: 0, M-Note: 0  
**鏀硅繘鏂瑰悜:**
- 浠?P-Note 鏍囩鑷姩瑙﹀彂 C-Note 鍒涘缓
- 鍚屾爣绛锯墺3 绡囪嚜鍔ㄨЕ鍙?M-Note
- 鍙屽悜閾炬帴鑷姩缁存姢

### 3. 鍙鍖栧寮?
**鏀硅繘鏂瑰悜:**
- 鏃堕棿婕旇繘鍔ㄧ敾
- 绀惧尯缁撴瀯楂樹寒
- 鎼滅储/杩囨护鍔熻兘
- 瀵煎嚭涓哄浘鐗?PDF

### 4. 缁熻鐪嬫澘瀹炴椂鍖?
**鏀硅繘鏂瑰悜:**
- 闆嗘垚鍒?OpenClaw 蹇冭烦妫€鏌?
- 瀹氭湡鑷姩鎺ㄩ€佹姤鍛?
- 瓒嬪娍鍥捐〃鍙鍖?

---

## 馃幆 涓嬩竴姝ュ缓璁?

1. **瀹屽杽鍏崇郴鎶藉彇** - 浠庤鏂囧弬鑰冩枃鐚拰瀵规瘮鍒嗘瀽涓彁鍙栧叧绯?
2. **鑷姩鍖?C/M-Note** - 鍩轰簬鏍囩鑷姩瑙﹀彂姒傚康鍜屽姣旂瑪璁?
3. **鍙鍖栦紭鍖?* - 娣诲姞鏃堕棿杞?绀惧尯妫€娴?鎼滅储鍔熻兘
4. **瀹氭椂闆嗘垚** - 灏嗙粺璁＄湅鏉垮姞鍏ュ績璺虫鏌ヤ换鍔?

---

## 馃摑 鎶€鏈爤鎬荤粨

| 缁勪欢 | 鎶€鏈?| 璇存槑 |
|------|------|------|
| 鍥捐氨鏋勫缓 | Python + regex | 瀹炰綋/鍏崇郴鎻愬彇 |
| 鍥捐氨瀛樺偍 | JSON + GraphML | 鍙屾牸寮忚緭鍑?|
| 鍙鍖?| D3.js v7 | 浜や簰寮忕綉缁滃浘 |
| 鍒嗘瀽 | NetworkX | 涓績鎬?绀惧尯妫€娴?|
| 缁熻 | Python + pathlib | 鏂囦欢绯荤粺鍒嗘瀽 |
| 骞惰澶勭悊 | OpenClaw subagents | 瀛愪唬鐞嗘睜鏋舵瀯 |

---

*鎶€鑳介泦鎴愬畬鎴愶紝绯荤粺宸插氨缁紒* 馃帀

---

## 馃敊 Backlinks

**Documents linking here:**
- [[link-recommendations]] - link-recommendations

