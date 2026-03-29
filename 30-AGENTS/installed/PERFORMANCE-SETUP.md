# ⚡ 性能配置

**创建日期:** 2026-03-27

---

## 执行限制

| 参数 | 值 | 说明 |
|------|-----|------|
| 命令超时 | 60s | 默认命令执行超时 |
| 浏览器超时 | 30s | 页面加载超时 |
| 搜索深度 | 1000 文件 | grep_search 默认限制 |
| 并发任务 | 3 | 同时执行的任务数 |

---

## 缓存策略

| 类型 | TTL | 位置 |
|------|-----|------|
| 文件读取 | 5 分钟 | 内存缓存 |
| API 响应 | 10 分钟 | `data/cache/` |
| 搜索结果 | 1 小时 | 上下文缓存 |
| 页面快照 | 30 分钟 | 浏览器缓存 |

---

## 记忆策略

```yaml
memory:
  session:
    # 每次会话读取
    - SOUL.md
    - USER.md
    - MEMORY.md (主会话)
    - today/yesterday memory
  
  long_term:
    # 重要信息持久化
    location: "memory/"
    retention: "indefinite"
  
  daily:
    # 每日记录
    location: "memory/YYYY-MM-DD.md"
    retention: "30 days"
  
  auto_archive:
    # 自动归档
    weekly_summary: true
    monthly_report: true
```

---

## 工具优先级

### 优先使用

| 工具 | 场景 |
|------|------|
| grep_search | 搜索文件内容 |
| glob_search | 查找文件 |
| read_file | 读取小文件 |
| execute_shell_command | 命令执行 |

### 慎用/延迟

| 工具 | 场景 | 原因 |
|------|------|------|
| browser_use | 大量网页抓取 | 资源消耗大 |
| desktop_screenshot | 频繁截图 | IO 密集 |
| send_file_to_user | 大文件 | 网络开销 |

---

## 性能优化技巧

### 1. 批量操作
```bash
# 不好：逐个执行
cmd1 && cmd2 && cmd3

# 好：并行执行
(cmd1 &) && (cmd2 &) && (cmd3 &)
```

### 2. 选择性读取
```python
# 不好：读取整个文件
read_file("large_file.md")

# 好：只读需要的部分
read_file("large_file.md", start_line=1, end_line=50)
```

### 3. 缓存结果
```python
# 重复使用的数据缓存到变量
data = read_file("config.json")
# 后续使用 data 而非重复读取
```

---

## 监控指标

| 指标 | 位置 | 告警阈值 |
|------|------|----------|
| Token 使用 | `token_usage.json` | >80% |
| 错误率 | `logs/error.log` | >5% |
| 响应时间 | session | >30s |
| 磁盘使用 | system | >90% |

---

## 自动优化

| 功能 | 状态 | 说明 |
|------|------|------|
| auto_fix_errors | ✅ 启用 | 自动修复错误 |
| auto_run_tests | ✅ 启用 | 运行测试 |
| max_retries | 3 | 自动重试次数 |
| cache_enabled | ✅ 启用 | 启用缓存 |

---

## 快捷命令

| 命令 | 执行 |
|------|------|
| `token` | 查看 Token 使用统计 |
| `日志` | 查看最近错误 |
| `清理缓存` | 清除临时缓存 |
| `性能报告` | 生成性能摘要 |
