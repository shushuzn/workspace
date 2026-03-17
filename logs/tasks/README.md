# 定时任务日志配置

**创建时间:** 2026-03-04 05:00

---

## 日志目录

`D:\OpenClaw\workspace\logs\tasks\`

---

## 日志文件命名规范

| 任务 | 日志文件 |
|------|----------|
| arxiv-collector | `arxiv-collector-YYYY-MM-DD.log` |
| batch-processor | `batch-processor-YYYY-MM-DD.log` |
| nightly-security-audit | `security-audit-YYYY-MM-DD.log` |
| medium-watcher | `medium-watcher-YYYY-MM-DD.log` |
| memory-distiller | `memory-distiller-YYYY-MM-DD.log` |
| github-sync | `github-sync-YYYY-MM-DD.log` |
| citation-tracker | `citation-tracker-YYYY-MM-DD.log` |

---

## 日志格式

```
[YYYY-MM-DD HH:MM:SS] [LEVEL] 消息内容
```

**级别:**
- `INFO` - 正常执行信息
- `WARN` - 警告 (非阻塞问题)
- `ERROR` - 错误 (任务失败)
- `DEBUG` - 调试信息

---

## 日志保留策略

- **活跃日志:** 最近 7 天
- **归档日志:** 30 天 (压缩)
- **删除:** 超过 90 天

---

## 监控命令

```powershell
# 查看今日日志
Get-ChildItem "D:\OpenClaw\workspace\logs\tasks" -Filter "*-$(Get-Date -Format 'yyyy-MM-dd').log" | Get-Content

# 查看错误日志
Get-ChildItem "D:\OpenClaw\workspace\logs\tasks" -Filter "*.log" | Select-String "ERROR" | Select-Object -First 20

# 查看最新 50 行
Get-Content "D:\OpenClaw\workspace\logs\tasks\arxiv-collector-2026-03-04.log" -Tail 50
```

---

*日志自动记录，定期清理*
