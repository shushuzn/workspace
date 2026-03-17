# 全局配置管理中心

**版本:** v1.0  
**创建时间:** 2026-03-05 17:30  
**用途:** 统一配置管理

---

## 📋 配置结构

```
config/
├── global.yaml          # 全局配置
├── level-0.yaml         # Level 0 配置
├── level-1.yaml         # Level 1 配置
├── level-2.yaml         # Level 2 配置
├── level-3.yaml         # Level 3 配置
├── level-4.yaml         # Level 4 配置
├── level-5.yaml         # Level 5 配置
├── level-6.yaml         # Level 6 配置
├── quality-gates.yaml   # 质量检查点配置
└── monitoring.yaml      # 监控配置
```

---

## ⚙️ 全局配置

### global.yaml
```yaml
# 全局配置
global:
  # 系统版本
  version: "2.0"
  
  # 日期格式
  date_format: "%Y-%m-%d"
  datetime_format: "%Y-%m-%dT%H:%M:%S"
  
  # 路径配置
  paths:
    workspace: "D:\\OpenClaw\\workspace"
    obsidian_vault: "D:\\obsidian\\Vault"
  
  # 日志配置
  logging:
    level: INFO
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  # 重试配置
  retry:
    max_attempts: 3
    delay_seconds: 60
  
  # 超时配置
  timeout:
    http_request: 30
    file_operation: 10
```

---

## 🚀 使用方法

### 加载配置

```python
from config_loader import load_config

# 加载全局配置
global_config = load_config('config/global.yaml')

# 加载 Level 配置
level_config = load_config('config/level-1.yaml')

# 合并配置
config = {**global_config, **level_config}
```

---

## 📊 配置版本控制

### 版本历史
```bash
# 查看配置历史
git log config/

# 回滚配置
git checkout <commit> -- config/global.yaml
```

### 配置变更流程
1. 修改配置文件
2. 运行测试验证
3. 提交 Git
4. 通知相关人员

---

## 🔒 配置安全

### 敏感信息
```yaml
# 使用环境变量
database:
  password: ${DB_PASSWORD}
  api_key: ${API_KEY}
```

### 权限控制
- 配置文件只读权限
- 敏感信息加密存储
- 访问日志记录

---

*最后更新：2026-03-05 17:30*
