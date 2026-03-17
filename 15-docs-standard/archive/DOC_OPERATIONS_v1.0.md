# 运维手册

**版本:** v2.0  
**创建时间:** 2026-03-05 18:00  
**状态:** 🟢 生产就绪

---

## 📋 日常运维

### 每日检查清单
- [ ] 检查 API 服务状态
- [ ] 检查日志文件
- [ ] 检查磁盘空间
- [ ] 检查监控指标
- [ ] 备份关键数据

### 每周检查清单
- [ ] 清理旧日志
- [ ] 更新依赖
- [ ] 性能基准测试
- [ ] 安全扫描
- [ ] 备份验证

---

## 🔍 监控指南

### 关键指标
| 指标 | 阈值 | 告警级别 |
|------|------|----------|
| CPU 使用率 | >80% | Warning |
| 内存使用率 | >90% | Critical |
| 磁盘使用率 | >85% | Warning |
| API 错误率 | >5% | Critical |
| API 响应时间 | >1s | Warning |

### 监控命令
```bash
# 查看系统状态
python scripts/monitoring/monitoring-system.py

# 查看 API 指标
curl http://localhost:5000/api/v1/metrics

# 查看告警
curl http://localhost:5000/api/v1/alerts
```

---

## 🛠️ 维护任务

### 日志清理
```bash
# 清理 30 天前的日志
find logs/ -name "*.log" -mtime +30 -delete
```

### 数据备份
```bash
# 备份数据湖
tar -czf backup-data-lake-$(date +%Y%m%d).tar.gz data-lake/

# 备份知识库
tar -czf backup-knowledge-$(date +%Y%m%d).tar.gz knowledge-graph/
```

### 依赖更新
```bash
# 检查更新
pip list --outdated

# 更新依赖
pip install --upgrade -r requirements.txt

# 验证更新
python -m pytest tests/
```

---

## 🚨 应急响应

### 服务宕机
1. 检查日志：`tail -f logs/*.log`
2. 重启服务：`python scripts/api/api-gateway.py`
3. 检查依赖：`pip check`
4. 联系支持

### 数据丢失
1. 停止所有服务
2. 从备份恢复：`tar -xzf backup-*.tar.gz`
3. 验证数据完整性
4. 重启服务

### 安全事件
1. 隔离受影响系统
2. 收集证据 (日志、配置)
3. 更改所有密钥
4. 安全审计

---

## 📞 支持联系

### 内部支持
- 运维团队：ops@example.com
- 开发团队：dev@example.com

### 外部支持
- GitHub Issues: https://github.com/shushuzn/obsidian-sync/issues
- 文档：https://github.com/shushuzn/obsidian-sync/docs

---

*最后更新：2026-03-05 18:00*
