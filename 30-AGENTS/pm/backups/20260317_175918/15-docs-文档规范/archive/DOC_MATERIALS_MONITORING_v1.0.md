# Materials Science System - 监控配置

**版本:** v0.1  
**创建时间:** 2026-03-05 14:04  
**目的:** 系统监控配置

---

## 📊 Prometheus 配置

### prometheus.yml
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'materials-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
    
  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongodb-exporter:9216']
      
  - job_name: 'neo4j'
    static_configs:
      - targets: ['neo4j-exporter:9217']
```

---

## 📈 Grafana 仪表板

### 关键指标
1. **API 性能**
   - 响应时间
   - 请求率
   - 错误率

2. **系统资源**
   - CPU 使用率
   - 内存使用率
   - 磁盘使用率

3. **业务指标**
   - 材料查询次数
   - 预测请求次数
   - 用户活跃度

---

## 🔔 告警配置

### 告警规则
```yaml
groups:
  - name: materials-alerts
    rules:
      - alert: HighAPIErrorRate
        expr: rate(api_errors_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "API 错误率过高"
          
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        annotations:
          summary: "API 响应时间过长"
          
      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
        for: 5m
        annotations:
          summary: "内存使用率过高"
```

---

## 📅 实施计划

| 任务 | 用时 | 状态 |
|------|------|------|
| Prometheus 配置 | 2 小时 | ✅ |
| Grafana 仪表板 | 3 小时 | 📋 |
| 告警配置 | 2 小时 | ✅ |

---

*最后更新：2026-03-05 14:04*
