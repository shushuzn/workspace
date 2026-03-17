# 娴嬭瘯妗嗘灦

**鐗堟湰:** v1.0  
**鍒涘缓鏃堕棿:** 2026-03-05 17:30  
**鐢ㄩ€?** 鍗曞厓娴嬭瘯 + 闆嗘垚娴嬭瘯

---

## 馃搵 娴嬭瘯缁撴瀯

```
tests/
鈹溾攢鈹€ test_all.py              # 杩愯鎵€鏈夋祴璇?
鈹溾攢鈹€ unit/                    # 鍗曞厓娴嬭瘯
鈹?  鈹溾攢鈹€ test_quality.py
鈹?  鈹溾攢鈹€ test_classification.py
鈹?  鈹斺攢鈹€ test_analysis.py
鈹溾攢鈹€ integration/             # 闆嗘垚娴嬭瘯
鈹?  鈹溾攢鈹€ test_pipeline.py
鈹?  鈹斺攢鈹€ test_quality_gates.py
鈹斺攢鈹€ fixtures/                # 娴嬭瘯鏁版嵁
    鈹溾攢鈹€ sample_papers.json
    鈹斺攢鈹€ expected_results.json
```

---

## 馃殌 浣跨敤鏂规硶

### 杩愯鎵€鏈夋祴璇?

```bash
cd D:\OpenClaw\workspace
python tests/test_all.py
```

### 杩愯鍗曞厓娴嬭瘯

```bash
python -m unittest tests.unit.test_quality
```

### 杩愯闆嗘垚娴嬭瘯

```bash
python -m unittest tests.integration.test_pipeline
```

---

## 馃搳 娴嬭瘯瑕嗙洊鐜?

### 鐩爣瑕嗙洊鐜?
| 绫诲瀷 | 鐩爣 | 褰撳墠 |
|------|------|------|
| 鍗曞厓娴嬭瘯 | 80% | 寰呭疄鐜?|
| 闆嗘垚娴嬭瘯 | 60% | 寰呭疄鐜?|
| 绔埌绔祴璇?| 40% | 寰呭疄鐜?|

---

## 馃敡 鎸佺画闆嗘垚

### CI/CD 閰嶇疆
```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Run tests
      run: python tests/test_all.py
```

---

## 馃搧 娴嬭瘯鏁版嵁

### 鏍锋湰鏁版嵁
```json
// fixtures/sample_papers.json
[
  {
    "arxiv_id": "2603.00267",
    "title": "Test Paper Title",
    "abstract": "This is a test abstract..."
  }
]
```

### 棰勬湡缁撴灉
```json
// fixtures/expected_results.json
{
  "valid_count": 1,
  "invalid_count": 0,
  "quality_score": 0.95
}
```

---

*鏈€鍚庢洿鏂帮細2026-03-05 17:30*

---

## 馃敊 Backlinks

**Documents linking here:**
- [[README]] - README
- [[15-docs\LINK_INDEX]] - LINK_INDEX

