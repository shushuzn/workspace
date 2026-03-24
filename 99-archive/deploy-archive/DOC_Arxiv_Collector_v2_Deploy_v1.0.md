# arxiv-collector v2 部署说明

## 文件清单

| 文件 | 位置 | 用途 |
|------|------|------|
| `arxiv-sync-setup.ps1` | 工作区 → D:\scripts | 目录自动化 |
| `arxiv-sync-start.ps1` | 工作区 → D:\scripts | 快速启动 |
| `arxiv-collector-v2.py` | 工作区 → D:\obsidian\Vault\scripts | 收集脚本 v2 |

---

## 部署步骤

### 1. 复制脚本到目标目录

```powershell
# 复制 PowerShell 脚本到 D:\scripts
Copy-Item "C:\Users\华为\.openclaw\workspace\arxiv-sync-setup.ps1" "D:\scripts\" -Force
Copy-Item "C:\Users\华为\.openclaw\workspace\arxiv-sync-start.ps1" "D:\scripts\" -Force

# 复制 Python 收集脚本
Copy-Item "C:\Users\华为\.openclaw\workspace\arxiv-collector-v2.py" "D:\obsidian\Vault\scripts\" -Force
```

### 2. 安装依赖

```powershell
pip install feedparser requests
```

### 3. 测试运行（预览模式）

```powershell
# 测试目录创建（不实际执行）
cd D:\scripts
.\arxiv-sync-setup.ps1 -CreateDaily -DryRun

# 测试收集脚本（实际运行）
cd D:\obsidian\Vault\scripts
python arxiv-collector-v2.py
```

---

## v2 新功能

### 对比 v1

| 功能 | v1 | v2 |
|------|----|----|
| 单领域 | ✅ cs.AI only | ❌ |
| 多领域 | ❌ | ✅ 10 个领域 |
| 目录自动化 | ❌ | ✅ 调用 PS 脚本 |
| 领域分类 | ❌ | ✅ 自动映射 |
| 状态日志 | ❌ | ✅ logs/status.md |
| 当日汇总 | ❌ | ✅ summary.md |
| YAML Frontmatter | ❌ | ✅ Obsidian 标签 |
| 错误处理 | 基础 | ✅ 回退模式 |

### 支持的领域

```
cs.AI    → csAI/    (人工智能)
cs.LG    → csLG/    (机器学习)
cs.CV    → csCV/    (计算机视觉)
cs.CL    → csCL/    (计算语言学)
cs.IR    → csIR/    (信息检索)
cs.SE    → csSE/    (软件工程)
cs.DC    → csDC/    (分布式计算)
cs.RO    → csRO/    (机器人)
cs.SY    → csSY/    (系统)
stat.ML  → csLG/    (统计 ML)
```

---

## 输出结构

```
arxiv/daily/2026/03/2026-03-03/
├── csAI/
│   ├── 143022-Attention-Based-Neural-Network.md
│   └── 143045-Deep-Learning-Survey.md
├── csLG/
│   └── 143011-Optimization-Methods.md
├── csCV/
│   └── 143033-Image-Segmentation.md
├── logs/
│   ├── 2026-03-03-cron.md
│   ├── 2026-03-03-status.md    ← 同步状态
│   └── 2026-03-03-update.md
├── 2026-03-03-summary.md        ← 当日汇总
└── 2026-03-03-index.md          ← 论文索引
```

---

## 定时任务配置

### 方案 A: Windows 任务计划程序

```powershell
# 创建每日凌晨 2 点运行的任务
$action = New-ScheduledTaskAction -Execute "python.exe" `
  -Argument "D:\obsidian\Vault\scripts\arxiv-collector-v2.py" `
  -WorkingDirectory "D:\obsidian\Vault\scripts"

$trigger = New-ScheduledTaskTrigger -Daily -At 2am

Register-ScheduledTask -TaskName "Arxiv-Collector" `
  -Action $action -Trigger $trigger `
  -User "华为" -RunLevel Highest
```

### 方案 B: 手动运行

```powershell
cd D:\obsidian\Vault\scripts
python arxiv-collector-v2.py
```

---

## 日志查看

```powershell
# 查看状态日志
Get-Content "D:\obsidian\Vault\arxiv\daily\2026\03\2026-03-03\logs\status.md"

# 查看最近错误
Get-Content "D:\obsidian\Vault\arxiv\daily\2026\03\2026-03-03\logs\errors.md"
```

---

## 配置自定义

编辑 `arxiv-collector-v2.py`:

```python
# 添加/删除领域
CATEGORIES = [
    'cs.AI',
    'cs.LG',
    # 'cs.CV',  # 注释掉不需要的
    'cs.NEW',  # 新增领域
]

# 调整每领域论文数
MAX_PAPERS_PER_CATEGORY = 15  # 默认 10

# 修改输出路径
VAULT_PATH = r"D:\obsidian\Vault"  # 你的 Obsidian 仓库
```

---

## 故障排查

### 问题 1: PowerShell 脚本执行策略

```powershell
# 临时允许执行
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# 或永久允许当前用户
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 问题 2: 目录权限

```powershell
# 检查写入权限
Test-Path "D:\obsidian\Vault\arxiv" -PathType Container

# 如果需要，获取权限
icacls "D:\obsidian\Vault\arxiv" /grant 华为:(OI)(CI)F
```

### 问题 3: 网络超时

```python
# 增加超时时间（编辑脚本）
response = requests.get(rss_url, timeout=60)  # 默认 30 秒
```

---

## 迁移旧数据

如果已有 `D:\obsidian\Vault\Arxiv\` 的旧数据：

```powershell
# 1. 备份
Copy-Item "D:\obsidian\Vault\Arxiv" "D:\obsidian\Vault\Arxiv-backup-20260303" -Recurse

# 2. 运行 v2 收集新论文
python arxiv-collector-v2.py

# 3. 手动迁移重要旧论文（可选）
# 或使用迁移脚本
```

---

## 下一步

1. ✅ 复制脚本到目标目录
2. ✅ 安装依赖
3. ✅ 测试运行
4. ⬜ 配置定时任务
5. ⬜ 迁移旧数据

---

*最后更新：2026-03-03*
