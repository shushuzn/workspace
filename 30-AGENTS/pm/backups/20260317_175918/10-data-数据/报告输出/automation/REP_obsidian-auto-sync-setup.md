# Obsidian 自动同步配置指南

**创建时间:** 2026-03-04 21:00  
**同步脚本:** `scripts/obsidian-auto-sync.ps1`  
**安装脚本:** `scripts/setup-obsidian-sync-task.ps1`

---

## ✅ 快速配置

### 步骤 1: 以管理员身份打开 PowerShell

1. 按 `Win + X`
2. 选择 "Windows PowerShell (管理员)" 或 "终端 (管理员)"

### 步骤 2: 运行安装脚本

```powershell
cd D:\OpenClaw\workspace\scripts
.\setup-obsidian-sync-task.ps1
```

### 步骤 3: 验证安装

```powershell
Get-ScheduledTask -TaskName "Obsidian-Auto-Sync"
```

应显示:
```
TaskName             State
--------             -----
Obsidian-Auto-Sync   Ready
```

---

## 📊 同步配置

### 同步目录

| 源目录 | 目标目录 | 说明 |
|--------|----------|------|
| `workspace/memory/` | `Vault/memory/` | 每日笔记/学习笔记 |
| `workspace/Medium/` | `Vault/Medium/` | 论文/文章收集 |
| `workspace/MEMORY.md` | `Vault/MEMORY.md` | 长期记忆 |
| `workspace/knowledge-graph/` | `Vault/knowledge-graph/` | 知识图谱 |
| `workspace/reports/` | `Vault/reports/` | 报告/仪表板 |

### 同步间隔

- **默认:** 每 30 分钟
- **可调整:** 修改 `setup-obsidian-sync-task.ps1` 中的 `$syncInterval`

### 同步文件类型

- `*.md` - Markdown 笔记
- `*.json` - JSON 数据
- `*.yaml` - 配置文件
- `*.txt` - 文本文件
- `*.graphml` - 知识图谱
- `*.mmd` - Mermaid 图表
- `*.html` - HTML 报告

---

## 🔧 手动同步

### 立即执行同步

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\OpenClaw\workspace\scripts\obsidian-auto-sync.ps1"
```

### 创建桌面快捷方式

1. 右键桌面 → 新建 → 快捷方式
2. 输入:
   ```
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\OpenClaw\workspace\scripts\obsidian-auto-sync.ps1"
   ```
3. 命名: "Obsidian 同步"
4. (可选) 右键快捷方式 → 属性 → 更改图标

---

## 📋 定时任务管理

### 查看任务状态

```powershell
Get-ScheduledTask -TaskName "Obsidian-Auto-Sync" | Select-Object TaskName, State, LastRunTime, NextRunTime
```

### 手动触发同步

```powershell
Start-ScheduledTask -TaskName "Obsidian-Auto-Sync"
```

### 查看任务历史

```powershell
Get-ScheduledTaskInfo -TaskName "Obsidian-Auto-Sync"
```

### 暂停任务

```powershell
Disable-ScheduledTask -TaskName "Obsidian-Auto-Sync"
```

### 恢复任务

```powershell
Enable-ScheduledTask -TaskName "Obsidian-Auto-Sync"
```

### 删除任务

```powershell
Unregister-ScheduledTask -TaskName "Obsidian-Auto-Sync" -Confirm:$false
```

---

## 🔍 验证同步

### 1. 检查 Obsidian Vault

打开 Obsidian，确认以下目录存在且有内容:

```
D:\obsidian\Vault/
├── memory/           ✅ 应有 26+ 个文件
├── Medium/           ✅ 应有论文/文章
├── knowledge-graph/  ✅ 应有图谱文件
├── reports/          ✅ 应有报告
└── MEMORY.md         ✅ 应有 181+ 观点
```

### 2. 测试文件更新

1. 在工作区创建测试文件:
   ```powershell
   echo "Test sync" > D:\OpenClaw\workspace\memory\sync-test.md
   ```

2. 等待同步或手动触发:
   ```powershell
   Start-ScheduledTask -TaskName "Obsidian-Auto-Sync"
   ```

3. 在 Obsidian Vault 验证:
   ```powershell
   Test-Path "D:\obsidian\Vault\memory\sync-test.md"
   ```

4. 清理测试文件:
   ```powershell
   Remove-Item "D:\OpenClaw\workspace\memory\sync-test.md"
   Remove-Item "D:\obsidian\Vault\memory\sync-test.md"
   ```

---

## ⚙️ 高级配置

### 修改同步间隔

编辑 `setup-obsidian-sync-task.ps1`:

```powershell
$syncInterval = 15  # 改为 15 分钟
```

重新运行安装脚本。

### 添加/移除同步目录

编辑 `obsidian-auto-sync.ps1`,修改 `Sync-Folder` 调用:

```powershell
# 添加新目录
Sync-Folder -Src "notes" -Dst "notes"

# 移除目录 (注释掉)
# Sync-Folder -Src "reports" -Dst "reports"
```

### 添加文件类型过滤

编辑 `obsidian-auto-sync.ps1`,修改 `-Include` 参数:

```powershell
-Include *.md,*.json,*.yaml,*.txt,*.pdf,*.png
```

---

## 🐛 故障排查

### 问题 1: 同步任务未执行

**检查:**
```powershell
Get-ScheduledTask -TaskName "Obsidian-Auto-Sync"
```

**解决:**
- 确认任务状态为 "Ready"
- 检查用户账户权限
- 查看任务历史记录

### 问题 2: 文件未同步

**检查:**
```powershell
Get-ChildItem "D:\OpenClaw\workspace\memory" -File | Measure-Object
Get-ChildItem "D:\obsidian\Vault\memory" -File | Measure-Object
```

**解决:**
- 手动执行同步脚本
- 检查文件权限
- 确认 Vault 路径正确

### 问题 3: 同步冲突

**场景:** Obsidian 和 OpenClaw 同时修改同一文件

**解决:**
- 同步脚本会以工作区为准 (覆盖 Vault)
- 如需保留 Obsidian 修改，先手动备份
- 考虑使用 Git 版本控制

---

## 📈 同步统计

### 今日同步结果

| 指标 | 数值 |
|------|------|
| 复制文件 | 739 个 |
| 跳过文件 | 296 个 |
| 同步目录 | 5 个 |
| 总大小 | ~10MB |

### 同步性能

- **首次同步:** ~5-10 秒 (全量)
- **增量同步:** ~1-2 秒 (仅变更文件)
- **资源占用:** 极低 (仅文件复制)

---

## 🎯 最佳实践

### 1. 同步频率

- **推荐:** 每 30 分钟
- **高频:** 每 15 分钟 (活跃编辑期)
- **低频:** 每 60 分钟 (节省资源)

### 2. 文件组织

- 使用清晰的目录结构
- 避免在 Vault 直接编辑 (可能被覆盖)
- 使用 Obsidian 的只读模式查看同步内容

### 3. 备份策略

- 启用 GitHub 自动备份 (obsidian-sync 仓库)
- 定期导出 Vault 快照
- 保留关键笔记的本地副本

---

## 📝 相关文档

- [Obsidian 同步状态报告](obsidian-sync-status-2026-03-04.md)
- [GitHub Sync 技能文档](../skills/github-sync/SKILL.md)
- [MEMORY.md 知识管理](../MEMORY.md)

---

*配置完成 · Obsidian 自动同步就绪 · 2026-03-04 21:00*
