# 故障排除指南

**版本:** v2.0  
**创建时间:** 2026-03-05 18:00  
**状态:** 🟢 生产就绪

---

## 🔍 诊断流程

### 1. 收集信息
```bash
# 系统信息
uname -a
python --version

# 服务状态
ps aux | grep python

# 日志检查
tail -100 logs/*.log
```

### 2. 定位问题
- API 问题 → 查看 `api-gateway.log`
- 质量问题 → 查看 `quality-control.log`
- 监控问题 → 查看 `monitoring.log`

### 3. 解决问题
- 参考下方常见问题
- 查看日志详细信息
- 联系支持团队

---

## ⚠️ 常见问题

### API 相关

**Q1: API 返回 401 Unauthorized**
```bash
# 原因：缺少或错误的 API Key
# 解决：
curl -H "X-API-Key: your-correct-key" http://localhost:5000/api/v1/health
```

**Q2: API 返回 404 Not Found**
```bash
# 原因：端点不存在或数据文件缺失
# 解决：
# 1. 检查端点 URL
# 2. 检查数据文件是否存在
ls -la data-lake/analytics/
```

**Q3: API 响应慢**
```bash
# 原因：数据量大或性能问题
# 解决：
# 1. 检查系统资源
top -o %MEM

# 2. 启用缓存
# 3. 优化查询
```

### 质量控制相关

**Q4: 质量评分低**
```bash
# 原因：数据质量问题
# 解决：
# 1. 查看质量报告
cat logs/quality-control.log

# 2. 检查原始数据
cat obsidian-vault/Arxiv/daily/*/raw/papers.json | jq

# 3. 调整质量阈值
vim config.yaml
```

**Q5: 大量无效论文**
```bash
# 原因：数据源问题或验证规则过严
# 解决：
# 1. 检查数据源
# 2. 调整验证规则
# 3. 联系数据源支持
```

### 监控相关

**Q6: 监控数据为空**
```bash
# 原因：监控服务未运行或配置错误
# 解决：
# 1. 检查监控服务
ps aux | grep monitoring

# 2. 检查配置文件
cat workflows/99-monitoring/config.yaml

# 3. 重启监控服务
python scripts/monitoring/monitoring-system.py
```

### 性能相关

**Q7: 内存使用过高**
```bash
# 原因：数据加载过多或内存泄漏
# 解决：
# 1. 重启服务
# 2. 检查内存使用
ps aux | grep python

# 3. 启用分页加载
# 4. 联系开发团队
```

**Q8: 磁盘空间不足**
```bash
# 原因：日志或数据积累
# 解决：
# 1. 清理旧日志
find logs/ -name "*.log" -mtime +30 -delete

# 2. 清理旧数据
find data-lake/ -mtime +90 -delete

# 3. 扩容磁盘
```

---

## 🛠️ 高级诊断

### 启用调试模式
```bash
# API 服务
export FLASK_DEBUG=1
python scripts/api/api-gateway.py

# 质量控制
export LOG_LEVEL=DEBUG
python scripts/level-0/quality-controller.py
```

### 性能分析
```bash
# Python 性能分析
python -m cProfile -o output.prof scripts/api/api-gateway.py

# 查看分析结果
python -m pstats output.prof
```

### 内存分析
```bash
# 使用 memory_profiler
pip install memory_profiler
python -m memory_profiler scripts/api/api-gateway.py
```

---

## 📞 获取帮助

### 日志位置
- API 日志：`logs/api-gateway.log`
- 质量日志：`logs/quality-control.log`
- 监控日志：`logs/monitoring.log`

### 配置文件
- 全局配置：`config/global.yaml`
- API 配置：`workflows/96-api-service/config.yaml`
- 监控配置：`workflows/99-monitoring/config.yaml`

### 支持渠道
- GitHub Issues: https://github.com/shushuzn/obsidian-sync/issues
- 文档：https://github.com/shushuzn/obsidian-sync/docs

---

*最后更新：2026-03-05 18:00*
