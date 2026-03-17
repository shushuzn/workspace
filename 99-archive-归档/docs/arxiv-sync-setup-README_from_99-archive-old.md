# arxiv-sync-setup.ps1 - 使用说明

## 功能

自动化创建 Obsidian arxiv 论文同步的标准化目录结构：

```
arxiv/
├── daily/           # 每日同步
│   └── 2026/
│       └── 03/
│           └── 2026-03-03/
│               ├── csAI/           # 领域子目录
│               ├── csLG/
│               ├── csCV/
│               ├── logs/           # 日志目录
│               │   ├── cron.md
│               │   ├── status.md
│               │   └── update.md
│               ├── 2026-03-03-summary.md   # 当日汇总
│               └── 2026-03-03-index.md     # 论文索引
├── weekly/          # 周汇总
│   └── 2026-W10-summary.md
├── monthly/         # 月汇总
│   └── 2026-03-summary.md
├── domains/         # 领域模板
│   ├── csAI/
│   ├── csLG/
│   └── ...
└── archive/         # 归档
```

---

## 快速开始

### 1. 初始化完整结构（首次使用）

```powershell
# 预览（不执行）
.\arxiv-sync-setup.ps1 -Init -DryRun

# 执行
.\arxiv-sync-setup.ps1 -Init
```

### 2. 创建今日目录（每日运行）

```powershell
# 默认创建今天
.\arxiv-sync-setup.ps1

# 或指定日期
.\arxiv-sync-setup.ps1 -CreateDaily -Date "2026-03-03"
```

### 3. 创建周/月汇总

```powershell
# 周汇总
.\arxiv-sync-setup.ps1 -CreateWeekly

# 月汇总
.\arxiv-sync-setup.ps1 -CreateMonthly

# 全部创建
.\arxiv-sync-setup.ps1 -CreateDaily -CreateWeekly -CreateMonthly
```

---

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-VaultPath` | Obsidian 仓库路径 | `D:\obsidian\Vault` |
| `-SyncRoot` | 同步根目录名 | `arxiv` |
| `-Init` | 初始化完整结构 | ❌ |
| `-CreateDaily` | 创建每日目录 | ❌ |
| `-CreateWeekly` | 创建周汇总 | ❌ |
| `-CreateMonthly` | 创建月汇总 | ❌ |
| `-Date` | 指定日期 (YYYY-MM-DD) | 今天 |
| `-DryRun` | 预览模式（不执行） | ❌ |

---

## 定时任务配置

### 方案 A: Windows 任务计划程序

```powershell
# 创建每日凌晨 2 点运行的任务
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
  -Argument "-ExecutionPolicy Bypass -File D:\scripts\arxiv-sync-setup.ps1 -CreateDaily"

$trigger = New-ScheduledTaskTrigger -Daily -At 2am

Register-ScheduledTask -TaskName "Obsidian-Arxiv-Sync" `
  -Action $action -Trigger $trigger -User "用户名"
```

### 方案 B: 手动调用

在收集脚本开始时调用：

```powershell
# 在 arxiv 收集脚本中
& D:\scripts\arxiv-sync-setup.ps1 -CreateDaily
```

---

## 领域分类

支持以下 arxiv 领域自动分类：

| 代码 | 领域 | 代码 | 领域 |
|------|------|------|------|
| csAI | 人工智能 | csCL | 计算语言学 |
| csLG | 机器学习 | csIR | 信息检索 |
| csCV | 计算机视觉 | csSE | 软件工程 |
| csDC | 分布式计算 | csPL | 编程语言 |
| csRO | 机器人 | csSY | 系统 |
| cross | 交叉领域 | ... | ... |

---

## 文件模板

每个创建的目录包含以下模板：

### 日志模板 (`logs/*.md`)
```markdown
---
created: 2026-03-03 04:00:00
tags: [arxiv, template]
---

# cron - 2026-03-03

待更新...
```

### 汇总模板 (`*-summary.md`)
```markdown
---
created: 2026-03-03 04:00:00
tags: [arxiv, template]
---

# 2026-03-03 汇总

## 当日论文汇总

### 统计
- 总论文数：0
- csAI: 0
- csLG: 0
- 其他：0

### 重点论文

待更新...

### 标签云

待更新...
```

### 索引模板 (`*-index.md`)
```markdown
---
created: 2026-03-03 04:00:00
tags: [arxiv, template]
---

# 2026-03-03 索引

## 论文索引

| ID | 标题 | 领域 | 状态 | 笔记 |
|----|------|------|------|------|
| 1  |      |      | 待处理 | [ ] |
```

---

## 迁移现有数据

如果已有 `github.com/shushuzn/obsidian-sync` 的数据：

```powershell
# 1. 备份现有数据
Copy-Item "D:\obsidian\Vault\arxiv" "D:\obsidian\Vault\arxiv-backup-20260303" -Recurse

# 2. 初始化新结构
.\arxiv-sync-setup.ps1 -Init

# 3. 手动迁移旧文件到对应目录
# 或使用迁移脚本（待创建）
```

---

## 故障排查

### 权限问题
```powershell
# 以管理员身份运行 PowerShell
# 或检查目录写入权限
```

### 编码问题
```powershell
# 确保使用 UTF8 编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### 路径问题
```powershell
# 检查 VaultPath 是否正确
Test-Path "D:\obsidian\Vault"
```

---

## 扩展开发

### 添加新领域
编辑脚本中的 `$Domains` 数组：

```powershell
$Domains = @(
    "csAI",
    "csNEW",  # 新增领域
    ...
)
```

### 自定义模板
修改 `New-TemplateFile` 函数中的 `$content` 变量。

---

*最后更新：2026-03-03*
