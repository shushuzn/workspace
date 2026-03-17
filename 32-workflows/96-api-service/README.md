# API 服务工作流

**版本:** v1.0  
**创建时间:** 2026-03-05 17:40  
**自动化:** 24/7 运行  
**层次:** 支撑系统

---

## 📋 工作流说明

### 功能
- REST API 服务
- 数据查询接口
- 监控指标接口
- 告警查询接口

### API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| /api/v1/health | GET | 健康检查 |
| /api/v1/papers | GET | 获取论文数据 |
| /api/v1/trends | GET | 获取趋势数据 |
| /api/v1/clusters | GET | 获取聚类数据 |
| /api/v1/graph | GET | 获取知识图谱 |
| /api/v1/metrics | GET | 获取监控指标 |
| /api/v1/alerts | GET | 获取告警数据 |

---

## 🚀 使用方法

### 启动服务

```bash
cd D:\OpenClaw\workspace
python scripts/api/api-gateway.py
```

### 访问 API

```bash
# 健康检查
curl http://localhost:5000/api/v1/health

# 获取论文数据
curl http://localhost:5000/api/v1/papers?date=2026-03-05

# 获取趋势数据
curl http://localhost:5000/api/v1/trends?date=2026-03-05

# 获取知识图谱
curl http://localhost:5000/api/v1/graph

# 获取监控指标
curl http://localhost:5000/api/v1/metrics

# 获取告警
curl http://localhost:5000/api/v1/alerts
```

---

## 📊 API 响应示例

### 健康检查
```json
{
  "status": "healthy",
  "version": "1.0"
}
```

### 论文数据
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
      "abstract": "摘要内容"
    }
  ]
}
```

---

## 🔒 安全配置

### 认证 (待实现)
```yaml
security:
  enabled: false
  api_key_required: false
  rate_limiting:
    enabled: false
    requests_per_minute: 60
```

### CORS (待实现)
```yaml
cors:
  enabled: false
  allowed_origins:
    - "http://localhost:3000"
```

---

*最后更新：2026-03-05 17:40*
