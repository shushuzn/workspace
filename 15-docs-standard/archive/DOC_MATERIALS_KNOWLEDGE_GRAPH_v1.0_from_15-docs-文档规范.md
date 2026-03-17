# 鏉愭枡鐭ヨ瘑鍥捐氨 - 璁捐鏂囨。

**鐗堟湰:** v0.1  
**鍒涘缓鏃堕棿:** 2026-03-05 13:22  
**鐩殑:** 鏋勫缓鏉愭枡绉戝棰嗗煙鐭ヨ瘑鍥捐氨

---

## 馃搳 鍥捐氨璁捐

### 瀹炰綋绫诲瀷

| 绫诲瀷 | 鎻忚堪 | 绀轰緥 |
|------|------|------|
| Material | 鏉愭枡 | LiCoO2, Graphene |
| Element | 鍏冪礌 | Li, Co, O, C |
| Property | 鎬ц兘 | Band Gap, Elastic Modulus |
| Structure | 缁撴瀯 | FCC, BCC, Perovskite |
| Application | 搴旂敤 | Battery, Catalyst |
| Synthesis | 鍚堟垚鏂规硶 | Solid-state Reaction, CVD |

---

### 鍏崇郴绫诲瀷

| 鍏崇郴 | 婧愬疄浣?| 鐩爣瀹炰綋 | 绀轰緥 |
|------|--------|----------|------|
| contains | Material | Element | LiCoO2 contains Li |
| has_property | Material | Property | Graphene has_property High Conductivity |
| has_structure | Material | Structure | LiCoO2 has_structure Layered |
| used_for | Material | Application | LiCoO2 used_for Battery |
| synthesized_by | Material | Synthesis | Graphene synthesized_by CVD |

---

## 馃敡 鎶€鏈疄鐜?

### 1. 鏉愭枡瀹炰綋璇嗗埆

**鏂规硶:**
- 瑙勫垯鍖归厤 (鍖栧寮忔鍒欒〃杈惧紡)
- NER 妯″瀷 (鏉愭枡鍚嶇О璇嗗埆)
- 鏁版嵁搴撳尮閰?(Materials Project ID)

**绀轰緥:**
```python
import re

# 鍖栧寮忓尮閰?
formula_pattern = r'([A-Z][a-z]?\d*)+'
matches = re.findall(formula_pattern, text)
```

### 2. 鍏崇郴鎻愬彇

**鏂规硶:**
- 渚濆瓨鍙ユ硶鍒嗘瀽
- 棰勫畾涔夋ā鏉垮尮閰?
- 娣卞害瀛︿範妯″瀷

**绀轰緥妯℃澘:**
- "{material} is a {property} material" 鈫?has_property
- "{material} is used for {application}" 鈫?used_for
- "{material} can be synthesized by {synthesis}" 鈫?synthesized_by

### 3. 鍥捐氨瀛樺偍

**鏂规:**
- Neo4j (鍥炬暟鎹簱)
- RDF + SPARQL
- 杞婚噺绾э細JSON + NetworkX

### 4. 鍙鍖栦笌鏌ヨ

**鍙鍖?**
- D3.js (Web)
- Gephi (妗岄潰)
- PyVis (Python)

**鏌ヨ鎺ュ彛:**
- REST API
- GraphQL
- SPARQL endpoint

---

## 馃搱 鍥捐氨瑙勬ā

| 鎸囨爣 | 鐩爣鍊?|
|------|--------|
| 鏉愭枡瀹炰綋 | 10,000+ |
| 鍏冪礌瀹炰綋 | 118 (鍏ㄩ儴鍏冪礌) |
| 鎬ц兘瀹炰綋 | 100+ |
| 缁撴瀯瀹炰綋 | 50+ |
| 搴旂敤瀹炰綋 | 100+ |
| 鍚堟垚鏂规硶 | 100+ |
| 鍏崇郴鎬绘暟 | 50,000+ |

---

## 馃搮 瀹炴柦璁″垝

| 浠诲姟 | 鐢ㄦ椂 | 鏃ユ湡 |
|------|------|------|
| 鏉愭枡瀹炰綋璇嗗埆 | 2 灏忔椂 | 03-20 |
| 鎬ц兘 - 缁撴瀯鍏崇郴鍥捐氨 | 3 灏忔椂 | 03-20 |
| 鍚堟垚璺緞鍥捐氨 | 3 灏忔椂 | 03-20 |
| 搴旂敤 - 鏉愭枡鍏宠仈鍥捐氨 | 2 灏忔椂 | 03-20 |
| 鍙鍖栦笌鏌ヨ鎺ュ彛 | 2 灏忔椂 | 03-20 |
| **鎬昏** | **12 灏忔椂** | - |

---

*鏈€鍚庢洿鏂帮細2026-03-05 13:22*

---

## 馃敊 Backlinks

**Documents linking here:**
- [[15-docs\LINK_INDEX]] - LINK_INDEX

