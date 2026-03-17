# CGCNN vs MEGNet - 妯″瀷瀵规瘮

**鐗堟湰:** v1.0  
**鍒涘缓鏃堕棿:** 2026-03-05 20:40  
**鐩殑:** 瀵规瘮涓ょ鏉愭枡鎬ц兘棰勬祴妯″瀷

---

## 馃搳 鏍稿績瀵规瘮

| 鐗规€?| CGCNN | MEGNet |
|------|-------|--------|
| **鍏ㄧО** | Crystal Graph Convolutional Neural Network | Materials Graph Network |
| **鏋舵瀯** | 鍥惧嵎绉缁忕綉缁?| 鍥剧缁忕綉缁?+ 鍏ㄥ眬鐘舵€?|
| **鎻愬嚭鏃堕棿** | 2018 | 2019 |
| **绮惧害 (褰㈡垚鑳?** | MAE ~0.03 eV/atom | MAE ~0.02 eV/atom |
| **绮惧害 (甯﹂殭)** | MAE ~0.35 eV | MAE ~0.28 eV |
| **鎺ㄧ悊閫熷害** | 杈冨揩 | 绋嶆參 |
| **妯″瀷澶у皬** | ~50 MB | ~100 MB |
| **閫傜敤鍦烘櫙** | 鏅朵綋鏉愭枡 | 鏅朵綋/鍒嗗瓙/鏉愭枡 |

---

## 馃幆 鏋舵瀯宸紓

### CGCNN

```
鍘熷瓙鐗瑰緛 鈫?鍗风Н灞?鈫?姹犲寲 鈫?鍏ㄨ繛鎺?鈫?鎬ц兘棰勬祴
    鈫?
鏅朵綋鍥?(鍘熷瓙 + 閿?
```

**鐗圭偣:**
- 涓撴敞鏅朵綋缁撴瀯
- 灞€閮ㄧ壒寰佹彁鍙?
- 璁＄畻鏁堢巼楂?

### MEGNet

```
鍘熷瓙鐗瑰緛 鈫?鍥剧綉缁?鈫?鍏ㄥ眬鐘舵€?鈫?鎬ц兘棰勬祴
    鈫?         鈫?         鈫?
  鍘熷瓙      閿俊鎭?   鏁翠綋鐗瑰緛
```

**鐗圭偣:**
- 寮曞叆鍏ㄥ眬鐘舵€佸悜閲?
- 鎹曡幏闀跨▼鐩镐簰浣滅敤
- 閫傜敤鎬ф洿骞?

---

## 馃捇 CPU 浼樺寲瀵规瘮

### 宸插疄鐜颁繚鎶ゆ満鍒?

| 鏈哄埗 | CGCNN | MEGNet |
|------|-------|--------|
| 绾跨▼闄愬埗 | 鉁?intra=4, inter=2 | 鉁?intra=4, inter=2 |
| 骞跺彂鎺у埗 | 鉁?max=1 | 鉁?max=1 |
| CPU 鐩戞帶 | 鉁?闃堝€?70% | 鉁?闃堝€?70% |
| 缂撳瓨绯荤粺 | 鉁?500 鏉?LRU | 鉁?500 鏉?LRU |
| 鎵瑰鐞?| 鉁?batch=10 | 鉁?batch=10 |

**涓よ€?CPU 浣跨敤瀹屽叏涓€鑷达紒** 鉁?

---

## 馃搱 鎬ц兘瀵规瘮 (棰勪及)

### 鍗曟棰勬祴

| 妯″瀷 | CPU 浣跨敤 | 鑰楁椂 | 鍐呭瓨 |
|------|---------|------|------|
| **CGCNN** | 40-50% | 2-3 绉?| ~500 MB |
| **MEGNet** | 45-55% | 2.5-4 绉?| ~800 MB |

### 鎵归噺棰勬祴 (10 涓?

| 妯″瀷 | CPU 浣跨敤 | 鑰楁椂 | 鍐呭瓨 |
|------|---------|------|------|
| **CGCNN** | 60-70% | 20-30 绉?| ~600 MB |
| **MEGNet** | 65-75% | 25-40 绉?| ~1 GB |

---

## 馃幆 浣跨敤寤鸿

### 閫夋嫨 CGCNN 鐨勫満鏅?

1. 鉁?**蹇€熺瓫閫?* - 闇€瑕佸揩閫熼娴嬪ぇ閲忔潗鏂?
2. 鉁?**璧勬簮鍙楅檺** - 鍐呭瓨鏈夐檺 (<1 GB)
3. 鉁?**鏅朵綋鏉愭枡** - 鍙鐞嗘櫠浣撶粨鏋?
4. 鉁?**鏃ュ父浣跨敤** - 瀵圭簿搴﹁姹備笉楂?

### 閫夋嫨 MEGNet 鐨勫満鏅?

1. 鉁?**楂樼簿搴﹂渶姹?* - 闇€瑕佹洿鍑嗙‘鐨勯娴?
2. 鉁?**澶氭牱鏉愭枡** - 鏅朵綋 + 鍒嗗瓙 + 鍏朵粬
3. 鉁?**鐮旂┒鐢ㄩ€?* - 鍙戣〃绾х簿搴?
4. 鉁?**澶嶆潅浣撶郴** - 闇€瑕侀暱绋嬬浉浜掍綔鐢?

---

## 馃敡 鍦ㄦ垜浠殑绯荤粺涓?

### 褰撳墠鐘舵€?

| 妯″瀷 | 鐘舵€?| 鑴氭湰 | 澶у皬 |
|------|------|------|------|
| **CGCNN** | 鉁?CPU 浼樺寲鐗?| cgcnn-model.py | 13.1 KB |
| **MEGNet** | 鉁?CPU 浼樺寲鐗?| megnet-model.py | 12.5 KB |

### 缁熶竴鎺ュ彛

```python
# 涓よ€呬娇鐢ㄧ浉鍚岀殑鎺ュ彛
from cgcnn_model import get_cgcnn_model
from megnet_model import get_megnet_model

# 鍒涘缓妯″瀷 (閰嶇疆鐩稿悓)
cgcnn = get_cgcnn_model(config)
megnet = get_megnet_model(config)

# 棰勬祴 (鎺ュ彛涓€鑷?
result_cgcnn = cgcnn.predict(structure)
result_megnet = megnet.predict(structure)
```

### 妯″瀷閫夋嫨绛栫暐

```python
def predict_with_best_model(structure, priority='accuracy'):
    if priority == 'speed':
        model = get_cgcnn_model()
    else:  # accuracy
        model = get_megnet_model()
    
    return model.predict(structure)
```

---

## 馃搳 绮惧害瀵规瘮 (Materials Project 鏁版嵁闆?

| 鎬ц兘 | CGCNN (MAE) | MEGNet (MAE) | 鎻愬崌 |
|------|-----------|------------|------|
| **褰㈡垚鑳?* | 0.030 eV | 0.020 eV | +33% |
| **甯﹂殭** | 0.35 eV | 0.28 eV | +20% |
| **浣撶Н妯￠噺** | 15 GPa | 12 GPa | +20% |
| **鍓垏妯￠噺** | 12 GPa | 10 GPa | +17% |

**MEGNet 绮惧害鍏ㄩ潰棰嗗厛锛?* 馃弳

---

## 馃挕 瀹為檯搴旂敤寤鸿

### 鏃ュ父鐮旂┒

```python
# 蹇€熺瓫閫夛細鐢?CGCNN
candidates = screen_1000_materials(model='cgcnn')

# 绮鹃€夋潗鏂欙細鐢?MEGNet
top_100 = rerank(candidates, model='megnet')

# 瀹為獙楠岃瘉锛氱敤 MEGNet + DFT
final_validation(top_10, model='megnet+dft')
```

### 楂橀€氶噺绛涢€?

```python
# 绗竴闃舵锛欳GCNN 蹇€熺瓫閫?
stage1 = cgcnn.predict_batch(1000_materials)

# 绗簩闃舵锛歁EGNet 绮剧‘棰勬祴
stage2 = megnet.predict_batch(stage1.top_100)

# 绗笁闃舵锛欴FT 楠岃瘉
stage3 = dft.calculate(stage2.top_10)
```

---

## 馃幆 鍦ㄦ垜浠殑 AI Research OS 涓?

### 闆嗘垚绛栫暐

```
璁烘枃鎻愬彇 鈫?鏅朵綋缁撴瀯 鈫?[CGCNN/MEGNet] 鈫?鎬ц兘棰勬祴 鈫?鐭ヨ瘑鍥捐氨
                                    鈫?
                              鑷姩閫夋嫨妯″瀷
                              (閫熷害 vs 绮惧害)
```

### 榛樿閰嶇疆

- **鏃ュ父浣跨敤:** CGCNN (蹇€?
- **閲嶈鐮旂┒:** MEGNet (绮剧‘)
- **澶ф壒閲?** CGCNN 鍒濈瓫 + MEGNet 绮鹃€?

---

## 馃摑 鎬荤粨

| 缁村害 | 鑳滆€?| 鐞嗙敱 |
|------|------|------|
| **绮惧害** | 馃弳 MEGNet | 鍏ㄩ潰棰嗗厛 17-33% |
| **閫熷害** | 馃弳 CGCNN | 蹇?20-30% |
| **鍐呭瓨** | 馃弳 CGCNN | 鍗犵敤灏?30-40% |
| **閫氱敤鎬?* | 馃弳 MEGNet | 鏀寔鏇村鏉愭枡绫诲瀷 |
| **CPU 浼樺寲** | 馃 骞虫墜 | 淇濇姢鏈哄埗鐩稿悓 |

**鎺ㄨ崘:**
- 鉁?**涓よ€呴兘瑁?* - 鏍规嵁鍦烘櫙閫夋嫨
- 鉁?**榛樿 CGCNN** - 鏃ュ父浣跨敤
- 鉁?**閲嶈鐢?MEGNet** - 楂樼簿搴﹂渶姹?

---

*鏂囨。鐢熸垚鏃堕棿锛?026-03-05 20:40*  
*浣滆€咃細Claw (AI Research OS)*

---

## 馃敊 Backlinks

**Documents linking here:**
- [[15-docs\LINK_INDEX]] - LINK_INDEX

