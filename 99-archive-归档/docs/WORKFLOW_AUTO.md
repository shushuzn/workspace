# Medium 自动化收集工作流程

## 架构（方案 B+ 任务队列）

```
RSS 源 → 扫描添加任务 → 队列处理 → Obsidian
              ↓
         任务管理器 (status/retry/cleanup)
```

## 核心文件

| 文件 | 用途 |
|------|------|
| `D:\scripts\medium-rss-integrated.py` | 主脚本（扫描 + 处理） |
| `D:\scripts\medium-task-manager.py` | 任务队列管理 |
| `D:\scripts\medium-rss-config.json` | 500+ 订阅源配置 |
| `D:\scripts\medium_tasks.json` | 任务队列 |
| `D:\scripts\medium_seen_rss.db` | 去重数据库 |
| `D:\obsidian\Vault\Medium\` | 输出目录 |

## 运行命令

```powershell
# 收集文章
python D:\scripts\medium-rss-integrated.py

# 查看状态
python D:\scripts\medium-task-manager.py status

# 重试失败
python D:\scripts\medium-task-manager.py retry

# 清理 (7 天)
python D:\scripts\medium-task-manager.py cleanup

# 查看日志
Get-Content D:\scripts\medium_integrated.log -Tail 20 -Encoding UTF8
```

## 配置

- `minScoreToProcess`: 6
- `maxArticlesPerRun`: 10
- `checkIntervalMinutes`: 30
- 失败重试：最多 3 次

## 故障排查

| 问题 | 解决 |
|------|------|
| 文章未保存 | 检查网络/增加 timeout |
| 重复文章 | 删除 `medium_seen_rss.db` 重建 |
| 任务失败 | `medium-task-manager.py retry` |
| 编码错误 | 使用 `-Encoding UTF8` |

---

*最后更新：2026-03-02*
