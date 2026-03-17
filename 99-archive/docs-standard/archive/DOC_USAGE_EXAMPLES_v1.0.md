# 浣跨敤绀轰緥

**鐗堟湰:** v2.0  
**鍒涘缓鏃堕棿:** 2026-03-05 18:40  

---

## 馃搵 鍩虹浣跨敤绀轰緥

### 1. 鍋ュ悍妫€鏌?

```python
import requests

# 妫€鏌ョ郴缁熷仴搴风姸鎬?
response = requests.get('http://localhost:5000/api/v1/health')
if response.status_code == 200:
    print("绯荤粺鍋ュ悍")
    print(f"鐗堟湰锛歿response.json()['version']}")
```

### 2. 鑾峰彇璁烘枃鏁版嵁

```python
import requests

API_KEY = 'your-api-key'
headers = {'X-API-Key': API_KEY}

# 鑾峰彇浠婃棩璁烘枃
response = requests.get(
    'http://localhost:5000/api/v1/papers',
    headers=headers
)

if response.status_code == 200:
    papers = response.json()
    print(f"鑾峰彇鍒?{len(papers.get('data', []))} 绡囪鏂?)
```

### 3. 鏌ョ湅绯荤粺鎸囨爣

```python
import requests

response = requests.get('http://localhost:5000/api/v1/metrics')
if response.status_code == 200:
    metrics = response.json()
    print(f"API 璇锋眰鏁帮細{metrics['counters']['api_requests_total']}")
    print(f"CPU 浣跨敤鐜囷細{metrics['gauges']['cpu_usage']}%")
```

---

## 馃攲 鎻掍欢寮€鍙戠ず渚?

### 鍒涘缓鑷畾涔夋彃浠?

```python
# plugins/plugin_my_plugin.py
from scripts.utils.plugin_system import BasePlugin

class MyPlugin(BasePlugin):
    name = "my_plugin"
    version = "1.0.0"
    description = "鎴戠殑鑷畾涔夋彃浠?
    
    def initialize(self, config):
        self.setting = config.get('setting', 'default')
        print(f"MyPlugin initialized with {self.setting}")
    
    def process(self, data):
        # 娣诲姞鑷畾涔夊鐞嗛€昏緫
        data['processed_by_my_plugin'] = True
        return data
    
    def shutdown(self):
        print("MyPlugin shutdown")
```

### 鍔犺浇鍜屼娇鐢ㄦ彃浠?

```python
from scripts.utils.plugin_system import PluginManager

# 鍒涘缓绠＄悊鍣?
manager = PluginManager()

# 鍔犺浇鎻掍欢
manager.load_plugin("my_plugin", {"setting": "value"})

# 澶勭悊鏁版嵁
data = {"input": "test"}
result = manager.process_all(data)

print(result)
# 杈撳嚭锛歿'input': 'test', 'processed_by_my_plugin': True}
```

---

## 馃殌 鎬ц兘浼樺寲绀轰緥

### 浣跨敤缂撳瓨

```python
from scripts.utils.performance_optimizer import CacheOptimizer

cache = CacheOptimizer(max_size=1000, ttl_seconds=300)

# 璁剧疆缂撳瓨
cache.set('key', expensive_data)

# 鑾峰彇缂撳瓨
data = cache.get('key')
if data is None:
    # 缂撳瓨鏈懡涓紝鍔犺浇鏁版嵁
    data = load_expensive_data()
    cache.set('key', data)
```

### 浣跨敤缂撳瓨瑁呴グ鍣?

```python
from scripts.utils.performance_optimizer import cached

@cached(ttl_seconds=300)
def get_paper_data(arxiv_id):
    # 鏄傝吹鐨勬暟鎹簱鏌ヨ
    return query_database(arxiv_id)

# 绗竴娆¤皟鐢ㄤ細鎵ц鏌ヨ
data1 = get_paper_data('2603.00267')

# 绗簩娆¤皟鐢ㄤ細鍛戒腑缂撳瓨
data2 = get_paper_data('2603.00267')
```

### 鎵归噺澶勭悊浼樺寲

```python
from scripts.utils.performance_optimizer import PerformanceOptimizer

optimizer = PerformanceOptimizer()

def process_paper(paper):
    # 澶勭悊鍗曠瘒璁烘枃
    return analyze(paper)

papers = load_papers()  # 1000 绡囪鏂?

# 鎵归噺澶勭悊 (鎵规澶у皬锛?00)
results = optimizer.optimize_batch_processing(
    papers,
    process_paper,
    batch_size=100
)
```

---

## 馃攧 閲嶈瘯鏈哄埗绀轰緥

### 浣跨敤閲嶈瘯瑁呴グ鍣?

```python
from scripts.utils.retry_manager import retry

@retry(max_attempts=3, delay_seconds=1, backoff_factor=2)
def call_external_api():
    # 鍙兘澶辫触鐨?API 璋冪敤
    return requests.get('http://api.example.com/data')

# 鑷姩閲嶈瘯 3 娆★紝姣忔寤惰繜缈诲€?
result = call_external_api()
```

### 浣跨敤閲嶈瘯绠＄悊鍣?

```python
from scripts.utils.retry_manager import RetryManager

manager = RetryManager(max_attempts=3, delay_seconds=1)

def unstable_operation():
    # 涓嶇ǔ瀹氱殑鎿嶄綔
    pass

try:
    result = manager.execute(unstable_operation)
except RetryError as e:
    print(f"鎿嶄綔澶辫触锛歿e}")
```

---

## 馃搳 鐩戞帶绀轰緥

### 璁板綍鑷畾涔夋寚鏍?

```python
from scripts.monitoring.enhanced_monitoring import EnhancedMonitoringSystem

monitor = EnhancedMonitoringSystem()

# 璁板綍 API 璇锋眰
monitor.record_api_request('/api/v1/custom', 50.0, 200)

# 璁板綍宸ヤ綔娴佹墽琛?
monitor.record_workflow_execution('custom_workflow', 120.5, 'success')

# 妫€鏌ュ憡璀?
alerts = monitor.check_and_alert()
```

### 鑾峰彇鐩戞帶鏁版嵁

```python
import requests

response = requests.get('http://localhost:5000/api/v1/metrics')
if response.status_code == 200:
    metrics = response.json()
    
    # 鏌ョ湅璁℃暟鍣?
    print(f"API 璇锋眰鏁帮細{metrics['counters']['api_requests_total']}")
    
    # 鏌ョ湅浠〃鐩?
    print(f"CPU 浣跨敤鐜囷細{metrics['gauges']['cpu_usage']}%")
    
    # 鏌ョ湅鎸囨爣缁熻
    for name, stats in metrics['metrics'].items():
        print(f"{name}: avg={stats['avg']:.2f}, max={stats['max']:.2f}")
```

---

## 馃洜锔?鏁呴殰鎺掗櫎绀轰緥

### 鏌ョ湅鏃ュ織

```bash
# 鏌ョ湅 API 鏃ュ織
tail -f logs/api-gateway.log

# 鏌ョ湅璐ㄩ噺鏃ュ織
tail -f logs/quality-control.log

# 鏌ョ湅鐩戞帶鏃ュ織
tail -f logs/monitoring-enhanced.log
```

### 浣跨敤 CLI 宸ュ叿

```bash
# 鍋ュ悍妫€鏌?
arxiv-ops health

# 鏌ョ湅绯荤粺鐘舵€?
arxiv-ops status

# 鏌ョ湅鍛婅
arxiv-ops alerts --severity error
```

---

*鏈€鍚庢洿鏂帮細2026-03-05 18:40*

---

## 馃敊 Backlinks

**Documents linking here:**
- [[README]] - README
- [[15-docs\LINK_INDEX]] - LINK_INDEX

