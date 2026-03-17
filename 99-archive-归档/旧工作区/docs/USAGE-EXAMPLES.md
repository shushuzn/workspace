# 使用示例

**版本:** v2.0  
**创建时间:** 2026-03-05 18:40  

---

## 📋 基础使用示例

### 1. 健康检查

```python
import requests

# 检查系统健康状态
response = requests.get('http://localhost:5000/api/v1/health')
if response.status_code == 200:
    print("系统健康")
    print(f"版本：{response.json()['version']}")
```

### 2. 获取论文数据

```python
import requests

API_KEY = 'your-api-key'
headers = {'X-API-Key': API_KEY}

# 获取今日论文
response = requests.get(
    'http://localhost:5000/api/v1/papers',
    headers=headers
)

if response.status_code == 200:
    papers = response.json()
    print(f"获取到 {len(papers.get('data', []))} 篇论文")
```

### 3. 查看系统指标

```python
import requests

response = requests.get('http://localhost:5000/api/v1/metrics')
if response.status_code == 200:
    metrics = response.json()
    print(f"API 请求数：{metrics['counters']['api_requests_total']}")
    print(f"CPU 使用率：{metrics['gauges']['cpu_usage']}%")
```

---

## 🔌 插件开发示例

### 创建自定义插件

```python
# plugins/plugin_my_plugin.py
from scripts.utils.plugin_system import BasePlugin

class MyPlugin(BasePlugin):
    name = "my_plugin"
    version = "1.0.0"
    description = "我的自定义插件"
    
    def initialize(self, config):
        self.setting = config.get('setting', 'default')
        print(f"MyPlugin initialized with {self.setting}")
    
    def process(self, data):
        # 添加自定义处理逻辑
        data['processed_by_my_plugin'] = True
        return data
    
    def shutdown(self):
        print("MyPlugin shutdown")
```

### 加载和使用插件

```python
from scripts.utils.plugin_system import PluginManager

# 创建管理器
manager = PluginManager()

# 加载插件
manager.load_plugin("my_plugin", {"setting": "value"})

# 处理数据
data = {"input": "test"}
result = manager.process_all(data)

print(result)
# 输出：{'input': 'test', 'processed_by_my_plugin': True}
```

---

## 🚀 性能优化示例

### 使用缓存

```python
from scripts.utils.performance_optimizer import CacheOptimizer

cache = CacheOptimizer(max_size=1000, ttl_seconds=300)

# 设置缓存
cache.set('key', expensive_data)

# 获取缓存
data = cache.get('key')
if data is None:
    # 缓存未命中，加载数据
    data = load_expensive_data()
    cache.set('key', data)
```

### 使用缓存装饰器

```python
from scripts.utils.performance_optimizer import cached

@cached(ttl_seconds=300)
def get_paper_data(arxiv_id):
    # 昂贵的数据库查询
    return query_database(arxiv_id)

# 第一次调用会执行查询
data1 = get_paper_data('2603.00267')

# 第二次调用会命中缓存
data2 = get_paper_data('2603.00267')
```

### 批量处理优化

```python
from scripts.utils.performance_optimizer import PerformanceOptimizer

optimizer = PerformanceOptimizer()

def process_paper(paper):
    # 处理单篇论文
    return analyze(paper)

papers = load_papers()  # 1000 篇论文

# 批量处理 (批次大小：100)
results = optimizer.optimize_batch_processing(
    papers,
    process_paper,
    batch_size=100
)
```

---

## 🔄 重试机制示例

### 使用重试装饰器

```python
from scripts.utils.retry_manager import retry

@retry(max_attempts=3, delay_seconds=1, backoff_factor=2)
def call_external_api():
    # 可能失败的 API 调用
    return requests.get('http://api.example.com/data')

# 自动重试 3 次，每次延迟翻倍
result = call_external_api()
```

### 使用重试管理器

```python
from scripts.utils.retry_manager import RetryManager

manager = RetryManager(max_attempts=3, delay_seconds=1)

def unstable_operation():
    # 不稳定的操作
    pass

try:
    result = manager.execute(unstable_operation)
except RetryError as e:
    print(f"操作失败：{e}")
```

---

## 📊 监控示例

### 记录自定义指标

```python
from scripts.monitoring.enhanced_monitoring import EnhancedMonitoringSystem

monitor = EnhancedMonitoringSystem()

# 记录 API 请求
monitor.record_api_request('/api/v1/custom', 50.0, 200)

# 记录工作流执行
monitor.record_workflow_execution('custom_workflow', 120.5, 'success')

# 检查告警
alerts = monitor.check_and_alert()
```

### 获取监控数据

```python
import requests

response = requests.get('http://localhost:5000/api/v1/metrics')
if response.status_code == 200:
    metrics = response.json()
    
    # 查看计数器
    print(f"API 请求数：{metrics['counters']['api_requests_total']}")
    
    # 查看仪表盘
    print(f"CPU 使用率：{metrics['gauges']['cpu_usage']}%")
    
    # 查看指标统计
    for name, stats in metrics['metrics'].items():
        print(f"{name}: avg={stats['avg']:.2f}, max={stats['max']:.2f}")
```

---

## 🛠️ 故障排除示例

### 查看日志

```bash
# 查看 API 日志
tail -f logs/api-gateway.log

# 查看质量日志
tail -f logs/quality-control.log

# 查看监控日志
tail -f logs/monitoring-enhanced.log
```

### 使用 CLI 工具

```bash
# 健康检查
arxiv-ops health

# 查看系统状态
arxiv-ops status

# 查看告警
arxiv-ops alerts --severity error
```

---

*最后更新：2026-03-05 18:40*
