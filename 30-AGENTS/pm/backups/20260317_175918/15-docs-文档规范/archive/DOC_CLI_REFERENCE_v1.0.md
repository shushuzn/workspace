# CLI 浣跨敤鏂囨。

**鐗堟湰:** v2.0  
**鍒涘缓鏃堕棿:** 2026-03-05 18:40  

---

## 馃搵 瀹夎

### 鏂规硶 1: 鐩存帴杩愯

```bash
python scripts/arxiv_ops_cli.py --help
```

### 鏂规硶 2: 瀹夎涓哄懡浠よ宸ュ叿

```bash
# 瀹夎渚濊禆
pip install click requests

# 鍒涘缓杞摼鎺?(Linux/Mac)
ln -s $(pwd)/scripts/arxiv_ops_cli.py /usr/local/bin/arxiv-ops

# Windows (PowerShell)
New-Item -ItemType SymbolicLink -Path "C:\ProgramData\arxiv-ops.py" -Target "$(pwd)\scripts\arxiv_ops_cli.py"
```

---

## 馃殌 蹇€熷紑濮?

### 鏌ョ湅甯姪

```bash
arxiv-ops --help
```

### 鍋ュ悍妫€鏌?

```bash
arxiv-ops health
```

杈撳嚭:
```
鉁?绯荤粺鍋ュ悍 (鐗堟湰锛?.0.0)
```

### 鏌ョ湅绯荤粺鐘舵€?

```bash
arxiv-ops status
```

杈撳嚭:
```
绯荤粺鐘舵€?
========================================
  鍋ュ悍鐘舵€侊細 鉁?2.0.0
  API 璇锋眰锛?1234
  CPU: 35.2%
  鍐呭瓨锛?5.8%
========================================
```

### 鏌ョ湅绯荤粺鎸囨爣

```bash
# 鏂囨湰鏍煎紡
arxiv-ops metrics

# JSON 鏍煎紡
arxiv-ops metrics --format json
```

杈撳嚭:
```
绯荤粺鎸囨爣:
  API 璇锋眰鏁帮細1234
  API 閿欒鏁帮細5
  CPU 浣跨敤鐜囷細35.2%
  鍐呭瓨浣跨敤鐜囷細65.8%
```

### 鏌ョ湅鍛婅

```bash
# 鏌ョ湅鎵€鏈夊憡璀?
arxiv-ops alerts

# 鏌ョ湅璀﹀憡绾у埆鍛婅
arxiv-ops alerts --severity warning

# 闄愬埗鏄剧ず鏁伴噺
arxiv-ops alerts --limit 5
```

杈撳嚭:
```
鍛婅鍒楄〃 (鍏?3 鏉?:
[WARNING] high_cpu: cpu_usage=85.5
[ERROR] high_memory: memory_usage=92.3
[CRITICAL] high_error_rate: error_rate=8.5
```

### 鏌ョ湅璐ㄩ噺鎶ュ憡

```bash
arxiv-ops quality
```

### 鏌ョ湅鏃ュ織

```bash
arxiv-ops logs
```

杈撳嚭:
```
鏃ュ織鏂囦欢:
  - api-gateway.log
  - quality-control.log
  - monitoring-enhanced.log

鏈€鏂版棩蹇?(monitoring-enhanced.log):
2026-03-05 18:40:00 - INFO - Starting monitoring
2026-03-05 18:40:01 - INFO - CPU usage: 35.2%
...
```

### 閰嶇疆绠＄悊

```bash
# 鏄剧ず鎵€鏈夐厤缃?
arxiv-ops config show

# 鑾峰彇閰嶇疆椤?
arxiv-ops config get security.api_key

# 璁剧疆閰嶇疆椤?
arxiv-ops config set security.api_key new-key
```

### 瑙﹀彂璁烘枃鏀堕泦

```bash
# 鏀堕泦浠婃棩璁烘枃
arxiv-ops collect

# 鏀堕泦鎸囧畾鏃ユ湡璁烘枃
arxiv-ops collect --date 2026-03-05

# 寮傛鎵ц
arxiv-ops collect --async
```

---

## 馃摉 鍛戒护鍙傝€?

### 绯荤粺鍛戒护

| 鍛戒护 | 璇存槑 | 绀轰緥 |
|------|------|------|
| `health` | 鍋ュ悍妫€鏌?| `arxiv-ops health` |
| `status` | 绯荤粺鐘舵€?| `arxiv-ops status` |
| `metrics` | 绯荤粺鎸囨爣 | `arxiv-ops metrics --format json` |
| `alerts` | 鏌ョ湅鍛婅 | `arxiv-ops alerts --severity warning` |
| `logs` | 鏌ョ湅鏃ュ織 | `arxiv-ops logs` |

### 璐ㄩ噺鍛戒护

| 鍛戒护 | 璇存槑 | 绀轰緥 |
|------|------|------|
| `quality` | 璐ㄩ噺鎶ュ憡 | `arxiv-ops quality` |

### 鏀堕泦鍛戒护

| 鍛戒护 | 璇存槑 | 绀轰緥 |
|------|------|------|
| `collect` | 瑙﹀彂鏀堕泦 | `arxiv-ops collect --date 2026-03-05` |

### 閰嶇疆鍛戒护

| 鍛戒护 | 璇存槑 | 绀轰緥 |
|------|------|------|
| `config show` | 鏄剧ず閰嶇疆 | `arxiv-ops config show` |
| `config get` | 鑾峰彇閰嶇疆 | `arxiv-ops config get key` |
| `config set` | 璁剧疆閰嶇疆 | `arxiv-ops config set key value` |

---

## 馃敡 楂樼骇鐢ㄦ硶

### 鑴氭湰闆嗘垚

```bash
#!/bin/bash
# 鍋ュ悍妫€鏌ヨ剼鏈?

if ! arxiv-ops health > /dev/null; then
    echo "绯荤粺寮傚父锛?
    # 鍙戦€佸憡璀?
    exit 1
fi

echo "绯荤粺姝ｅ父"
```

### 鐩戞帶闆嗘垚

```bash
# Prometheus Exporter
arxiv-ops metrics --format json | jq '.gauges' > /var/lib/prometheus/node-exporter/arxiv-ops.prom
```

---

*鏈€鍚庢洿鏂帮細2026-03-05 18:40*

---

## 馃敊 Backlinks

**Documents linking here:**
- [[15-docs\LINK_INDEX]] - LINK_INDEX

