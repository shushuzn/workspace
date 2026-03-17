# 🛠️ Tools & Utils - 工具脚本索引

**位置:** `11-tools-utils/`  
**用途:** 所有通用工具和 CLI 脚本

---

## 📁 文件夹结构

```
11-tools-utils/
├── scripts/    # 通用脚本 (6 个)
├── cli/        # CLI 工具 (11 个)
└── README.md   # 本索引
```

---

## 🗂️ 文件清单

### 🐍 通用脚本 (`scripts/`) - 6 个

| 文件 | 用途 |
|------|------|
| `cleanup-root.bat` | 清理根目录 |
| `find-conflicts.py` | 查找冲突 |
| `python_startup.py` | Python 启动 |
| `redis_task_queue.py` | Redis 任务队列 |
| `remove-conflicts.py` | 移除冲突 |
| `start-nginx.py` | 启动 Nginx |

**使用示例:**
```bash
# 清理根目录
scripts\cleanup-root.bat

# 查找冲突
python scripts/find-conflicts.py

# 启动 Nginx
python scripts/start-nginx.py
```

---

### 🖥️ CLI 工具 (`cli/`) - 11 个

| 文件 | 用途 |
|------|------|
| `activate-personas.bat` | 激活人格 |
| `cron-notify.py` | Cron 通知 |
| `final-verify.py` | 最终验证 |
| `find-project.bat` | 查找项目 |
| `git-commit-p6.ps1` | Git 提交 P6 |
| `openclaw-cli.py` | OpenClaw CLI |
| `openclaw.bat` | OpenClaw 快捷 |
| `send-innovator-live.py` | 发送创新者直播 |
| `send-live-notification.py` | 发送直播通知 |
| `send-notification.py` | 发送通知 |
| `ssh-test.py` | SSH 测试 |

**使用示例:**
```bash
# OpenClaw CLI
cli\openclaw.bat --help

# 查找项目
cli\find-project.bat

# 发送通知
python cli/send-notification.py
```

---

**最后更新:** 2026-03-17  
**维护者:** Claw 🐾
