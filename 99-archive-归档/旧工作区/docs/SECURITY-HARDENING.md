# 安全加固指南

**版本:** v1.0  
**创建时间:** 2026-03-05 19:00  

---

## 📋 概述

安全加固系统提供认证、授权、速率限制、审计等功能。

---

## 🔒 功能

### 1. API Key 认证

**生成 API Key:**

```python
from scripts.security_hardening import SecurityManager

security = SecurityManager()
api_key = security.generate_api_key('user1')
print(f"API Key: {api_key}")
```

**验证 API Key:**

```python
valid = security.validate_api_key(api_key)
if valid:
    print("API Key 有效")
else:
    print("API Key 无效")
```

**使用装饰器:**

```python
from scripts.security_hardening import require_auth

@app.route('/api/protected')
@require_auth
def protected_endpoint():
    return {'data': 'protected data'}
```

### 2. 速率限制

**检查速率限制:**

```python
allowed = security.check_rate_limit('user1', limit=100, window=60)
if allowed:
    print("请求允许")
else:
    print("请求超限")
```

**使用装饰器:**

```python
from scripts.security_hardening import rate_limit

@app.route('/api/data')
@rate_limit(limit=100, window=60)
def data_endpoint():
    return {'data': 'data'}
```

### 3. 密码加密

**哈希密码:**

```python
password_hash = security.hash_password('password123')
```

**验证密码:**

```python
valid = security.verify_password('password123', password_hash)
```

### 4. 审计日志

**记录审计日志:**

```python
security._audit_log('user_login', 'user1', 'IP: 192.168.1.1')
```

**获取审计日志:**

```python
audit_log = security.get_audit_log(limit=100)
for entry in audit_log:
    print(f"{entry['timestamp']} - {entry['action']}: {entry['details']}")
```

---

## 📊 安全报告

**获取安全报告:**

```python
report = security.get_security_report()
print(f"API Keys: {report['api_keys_count']}")
print(f"速率限制：{report['rate_limits_count']}")
print(f"审计日志：{report['audit_log_count']}")
```

---

## 🔧 最佳实践

### 1. API Key 管理

- 定期轮换 API Key
- 限制 API Key 权限
- 监控 API Key 使用

### 2. 速率限制

- 设置合理的限制 (100 次/分钟)
- 按用户/IP 分别限制
- 记录超限请求

### 3. 密码安全

- 使用强密码策略
- 密码哈希存储
- 定期更换密码

### 4. 审计日志

- 记录所有敏感操作
- 定期审查日志
- 异常行为告警

---

## 📈 安全指标

| 指标 | 目标 | 当前 |
|------|------|------|
| API Key 轮换 | 每月 | 每月 |
| 密码强度 | >8 字符 | >8 字符 |
| 审计日志 | 100% | 100% |
| 速率限制 | 100 次/分 | 100 次/分 |

---

*最后更新：2026-03-05 19:00*
