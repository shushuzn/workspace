# 06-MONITORING - 监控工具

**用途:** 系统监控、CPU 限制、指标收集、健康检查

---

## 📁 目录结构

```
06-MONITORING/
├── monitoring/                # 监控核心
├── scripts/                   # 监控脚本
│   ├── METRICS_COLLECTOR.ps1
│   ├── heartbeat-check.ps1
│   ├── heartbeat-exec.ps1
│   └── heartbeat-done.ps1
├── metrics/                   # 指标数据
│   ├── METRICS_DASHBOARD.html
│   ├── metrics_history.csv
│   └── metrics_collector.log
└── README.md
```

---

## ✨ 功能特性

- ✅ **指标收集** - CPU/内存/磁盘监控
- ✅ **心跳检查** - 定期健康检查
- ✅ **可视化仪表板** - HTML 图表
- ✅ **历史数据** - CSV 记录
- ✅ **自动告警** - 阈值触发

---

## 📊 统计信息

| 类别 | 数量 | 大小 |
|------|------|------|
| 监控核心 | 1 文件夹 | ~20KB |
| 脚本 | 4 | 25KB |
| 指标数据 | 3 | 28KB |
| **总计** | **9** | **~73KB** |

---

*最后更新：2026-03-11 | 版本 v1.0*
