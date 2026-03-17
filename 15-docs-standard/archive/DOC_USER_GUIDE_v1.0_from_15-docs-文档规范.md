# 用户指南

**版本:** v2.0  
**创建时间:** 2026-03-05 18:20  
**状态:** 🟢 生产就绪

---

## 📋 系统概述

AI Research OS 是一个智能化的研究辅助系统，帮助您：
- 自动收集学术论文
- 质量控制与验证
- 趋势分析与洞察
- 知识图谱构建

---

## 🚀 快速开始

### 1. 访问系统

**Web 界面:**
```
http://localhost:5000
```

**API 端点:**
```
http://localhost:5000/api/v1
```

### 2. 获取 API Key

API Key 在配置文件中设置：
```yaml
# config.yaml
security:
  api_key: "your-api-key-here"
```

### 3. 第一次 API 调用

```bash
# 健康检查 (无需认证)
curl http://localhost:5000/api/v1/health

# 获取论文数据 (需要认证)
curl -H "X-API-Key: your-api-key" \
  http://localhost:5000/api/v1/papers
```

---

## 📖 核心功能

### 1. 论文收集

**功能:** 自动收集 arXiv 论文

**使用:**
```bash
# 手动触发
python scripts/level-0/quality-controller.py

# 自动运行 (每日 02:00)
# 系统自动执行
```

**输出:**
- `quality-controlled/validated_papers.json` - 验证后的论文

### 2. 质量检查

**功能:** 数据质量验证

**使用:**
```bash
# 查看质量报告
cat logs/quality-control.log
```

**质量指标:**
- 数据验证通过率
- 异常检测率
- 质量评分 (A-F)

### 3. 趋势分析

**功能:** 研究趋势分析

**使用 API:**
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:5000/api/v1/trends
```

**输出:**
- 热门话题
- 新兴领域
- 技术演进

### 4. 知识图谱

**功能:** 知识关系网络

**使用 API:**
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:5000/api/v1/graph
```

**输出:**
- 实体列表
- 关系网络

---

## 🔌 API 使用

### 认证

所有 API 端点 (除 `/health` 外) 需要 API Key:

```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:5000/api/v1/endpoint
```

### 端点列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/papers` | GET | 获取论文 |
| `/api/v1/trends` | GET | 获取趋势 |
| `/api/v1/clusters` | GET | 获取聚类 |
| `/api/v1/graph` | GET | 获取图谱 |
| `/api/v1/metrics` | GET | 获取指标 |
| `/api/v1/alerts` | GET | 获取告警 |

### 错误处理

**400 Bad Request:**
```json
{
  "error": "Bad Request",
  "message": "Invalid parameter"
}
```

**401 Unauthorized:**
```json
{
  "error": "Unauthorized",
  "message": "Missing API key"
}
```

**404 Not Found:**
```json
{
  "error": "Not Found",
  "message": "No data found"
}
```

---

## 📊 查看监控

### 系统指标

```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:5000/api/v1/metrics
```

### 告警信息

```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:5000/api/v1/alerts
```

### 日志文件

```bash
# 系统日志
tail -f logs/monitoring-enhanced.log

# API 日志
tail -f logs/api-gateway.log

# 质量日志
tail -f logs/quality-control.log
```

---

## ⚙️ 配置系统

### 配置文件

```yaml
# config.yaml
global:
  version: "2.0"
  date_format: "%Y-%m-%d"

paths:
  workspace: "D:\\OpenClaw\\workspace"
  obsidian_vault: "D:\\obsidian\\Vault"

security:
  authentication:
    enabled: true
    api_key: "your-api-key"

logging:
  level: INFO
```

### 插件配置

```yaml
# config.yaml
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
        - type: add_field
          field: processed_at
          value: 2026-03-05
```

---

## 🧪 故障排除

### 常见问题

**Q1: API 返回 401**
```bash
# 原因：缺少或错误的 API Key
# 解决：
curl -H "X-API-Key: correct-key" http://localhost:5000/api/v1/health
```

**Q2: 数据为空**
```bash
# 原因：数据文件不存在
# 解决：
# 1. 运行质量控制
python scripts/level-0/quality-controller.py

# 2. 检查文件
ls -la data-lake/analytics/
```

**Q3: 服务无法启动**
```bash
# 检查端口
netstat -ano | findstr :5000

# 查看日志
tail -f logs/api-gateway.log
```

---

## 📞 获取帮助

### 文档

- [部署指南](DEPLOYMENT.md)
- [运维手册](OPERATIONS.md)
- [故障排除](TROUBLESHOOTING.md)
- [API 文档](API.md)
- [插件开发](PLUGIN-DEVELOPMENT.md)

### 支持

- GitHub Issues: https://github.com/shushuzn/obsidian-sync/issues
- 系统日志：`logs/`

---

*最后更新：2026-03-05 18:20*
