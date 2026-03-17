# API 文档

**版本:** v2.0  
**创建时间:** 2026-03-05 18:00  
**状态:** 🟢 生产就绪

---

## 📋 概述

### 基础信息
- **基础 URL:** `http://localhost:5000/api/v1`
- **认证方式:** API Key (Header: `X-API-Key`)
- **数据格式:** JSON
- **速率限制:** 60 请求/分钟

### 认证
所有 API 端点 (除 `/health` 外) 需要 API Key 认证：

```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:5000/api/v1/papers
```

---

## 🔌 端点

### GET /health
健康检查 (无需认证)

**响应:**
```json
{
  "status": "healthy",
  "version": "2.0",
  "auth_enabled": true
}
```

### GET /papers
获取论文数据

**参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | 否 | 日期 (YYYY-MM-DD) |

**响应:**
```json
{
  "metadata": {
    "source": "level-0-quality-control",
    "version": "1.0",
    "processed_at": "2026-03-05T01:50:00"
  },
  "data": [
    {
      "arxiv_id": "2603.00267",
      "title": "论文标题",
      "abstract": "摘要内容",
      "categories": ["cs.AI"]
    }
  ]
}
```

### GET /trends
获取趋势数据

**参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | 否 | 日期 |

**响应:**
```json
{
  "date": "2026-03-05",
  "total_papers": 127,
  "hot_topics": [
    {"topic": "LLZO", "count": 45}
  ],
  "emerging_fields": ["solid-state"]
}
```

### GET /clusters
获取聚类数据

**参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | 否 | 日期 |

### GET /graph
获取知识图谱

**响应:**
```json
{
  "entities": [...],
  "relations": [...]
}
```

### GET /metrics
获取监控指标

**响应:**
```json
{
  "timestamp": "2026-03-05T18:00:00",
  "workflows": {...},
  "performance": {...}
}
```

### GET /alerts
获取告警数据

**响应:**
```json
{
  "timestamp": "2026-03-05T18:00:00",
  "alerts": [...],
  "total": 0
}
```

---

## ❌ 错误响应

### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Invalid parameter"
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Missing API key"
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "Invalid API key"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "No data found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

---

## 📝 使用示例

### Python
```python
import requests

API_KEY = 'your-api-key'
BASE_URL = 'http://localhost:5000/api/v1'

headers = {'X-API-Key': API_KEY}

# 获取论文
response = requests.get(f'{BASE_URL}/papers', headers=headers)
papers = response.json()

# 获取趋势
response = requests.get(f'{BASE_URL}/trends', headers=headers)
trends = response.json()
```

### JavaScript
```javascript
const API_KEY = 'your-api-key';
const BASE_URL = 'http://localhost:5000/api/v1';

async function getPapers() {
  const response = await fetch(`${BASE_URL}/papers`, {
    headers: {'X-API-Key': API_KEY}
  });
  return await response.json();
}
```

---

*最后更新：2026-03-05 18:00*
