# 插件开发指南

**版本:** v1.0  
**创建时间:** 2026-03-05 18:10  
**状态:** 🟢 生产就绪

---

## 📋 概述

插件系统允许您扩展系统功能而无需修改核心代码。

### 特性
- 热插拔插件
- 配置驱动
- 链式处理
- 错误隔离

---

## 🚀 快速开始

### 1. 创建插件文件

在 `plugins/` 目录创建 `plugin_your_plugin.py`:

```python
from scripts.utils.plugin_system import BasePlugin

class YourPlugin(BasePlugin):
    name = "your_plugin"
    version = "1.0.0"
    description = "Your plugin description"
    
    def initialize(self, config):
        pass
    
    def process(self, data):
        return data
    
    def shutdown(self):
        pass
```

### 2. 配置插件

在配置文件中添加:

```yaml
plugins:
  your_plugin:
    enabled: true
    config:
      setting1: value1
      setting2: value2
```

### 3. 加载插件

```python
from scripts.utils.plugin_system import PluginManager

manager = PluginManager()
manager.load_plugin("your_plugin", config)
```

---

## 🔌 插件接口

### BasePlugin

所有插件必须继承 `BasePlugin` 并实现以下方法:

#### initialize(config: Dict) -> None
初始化插件

**参数:**
- `config`: 插件配置字典

**示例:**
```python
def initialize(self, config):
    self.setting = config.get('setting', 'default')
```

#### process(data: Dict) -> Dict
处理数据

**参数:**
- `data`: 输入数据

**返回:**
- 处理后的数据

**示例:**
```python
def process(self, data):
    data['processed'] = True
    return data
```

#### shutdown() -> None
关闭插件

**示例:**
```python
def shutdown(self):
    # 清理资源
    pass
```

---

## 📝 插件示例

### 数据验证插件

```python
from scripts.utils.plugin_system import BasePlugin

class DataValidatorPlugin(BasePlugin):
    name = "data_validator"
    version = "1.0.0"
    description = "Validate input data"
    
    def initialize(self, config):
        self.required_fields = config.get('required_fields', [])
    
    def process(self, data):
        errors = []
        for field in self.required_fields:
            if field not in data:
                errors.append(f"Missing: {field}")
        
        if errors:
            data['valid'] = False
            data['errors'] = errors
        else:
            data['valid'] = True
        
        return data
    
    def shutdown(self):
        pass
```

### 数据转换插件

```python
from scripts.utils.plugin_system import BasePlugin

class DataTransformerPlugin(BasePlugin):
    name = "data_transformer"
    version = "1.0.0"
    description = "Transform data format"
    
    def initialize(self, config):
        self.transformations = config.get('transformations', [])
    
    def process(self, data):
        result = data.copy()
        
        for transform in self.transformations:
            if transform['type'] == 'rename':
                result[transform['new']] = result.pop(transform['old'])
        
        return result
    
    def shutdown(self):
        pass
```

---

## 🔧 插件管理器

### 基本用法

```python
from scripts.utils.plugin_system import PluginManager

# 创建管理器
manager = PluginManager()

# 发现插件
available = manager.discover_plugins()

# 加载插件
manager.load_plugin("plugin_name", config)

# 处理数据
result = manager.process_all(data)

# 列出插件
plugins = manager.list_plugins()

# 卸载插件
manager.unload_plugin("plugin_name")
```

### 配置示例

```yaml
plugins:
  data_validator:
    enabled: true
    config:
      required_fields:
        - arxiv_id
        - title
        - abstract
  
  data_transformer:
    enabled: true
    config:
      transformations:
        - type: rename
          old_key: old_name
          new_key: new_name
        - type: add_field
          field: processed_at
          value: 2026-03-05
```

---

## 📊 最佳实践

### 1. 错误处理

```python
def process(self, data):
    try:
        # 处理逻辑
        return result
    except Exception as e:
        # 记录错误但不中断
        print(f"Plugin error: {e}")
        return data  # 返回原始数据
```

### 2. 性能优化

```python
def initialize(self, config):
    # 预加载资源
    self.cache = {}
    
def process(self, data):
    # 使用缓存
    if data['id'] in self.cache:
        return self.cache[data['id']]
    
    # 处理并缓存
    result = self._process(data)
    self.cache[data['id']] = result
    return result
```

### 3. 配置管理

```python
def initialize(self, config):
    # 使用默认值
    self.setting = config.get('setting', 'default_value')
    
    # 验证配置
    if not isinstance(self.setting, str):
        raise ValueError("setting must be string")
```

---

## 🧪 测试插件

### 单元测试

```python
import unittest
from plugins.plugin_your_plugin import YourPlugin

class TestYourPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = YourPlugin()
        self.plugin.initialize({})
    
    def test_process(self):
        data = {'input': 'test'}
        result = self.plugin.process(data)
        self.assertIn('processed', result)
```

---

## 📞 故障排除

### 插件未加载

**问题:** 插件未被发现

**解决:**
1. 检查文件名：`plugin_*.py`
2. 检查类继承：`BasePlugin`
3. 检查类属性：`name`, `version`

### 处理失败

**问题:** 插件处理抛出异常

**解决:**
1. 添加错误处理
2. 检查输入数据格式
3. 查看日志输出

---

*最后更新：2026-03-05 18:10*
