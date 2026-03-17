# Nightly Security Audit 定时任务配置指南

**创建时间:** 2026-03-04 20:41  
**任务名称:** `OpenClaw-Nightly-Security-Audit`  
**执行时间:** 每日凌晨 3:00 AM

---

## 📋 配置方案

### 方案 A: 使用安装脚本（推荐）

**步骤:**

1. **以管理员身份打开 PowerShell**
   - 右键点击 PowerShell → "以管理员身份运行"

2. **运行安装脚本**
   ```powershell
   cd D:\OpenClaw\workspace
   .\setup-security-audit-task.ps1
   ```

3. **验证安装**
   ```powershell
   Get-ScheduledTask -TaskName "OpenClaw-Nightly-Security-Audit"
   ```

---

### 方案 B: 手动命令行（备用）

**管理员 PowerShell 执行:**

```powershell
schtasks /Create /TN "OpenClaw-Nightly-Security-Audit" `
  /TR "pwsh.exe -NoProfile -ExecutionPolicy Bypass -File 'D:\OpenClaw\workspace\nightly-security-audit.ps1'" `
  /SC DAILY `
  /ST 03:00 `
  /RU "huawei" `
  /RL HIGHEST `
  /F
```

---

### 方案 C: 任务计划程序 GUI

1. **打开任务计划程序**
   - `Win + R` → `taskschd.msc` → Enter

2. **创建基本任务**
   - 右侧 "创建基本任务..."
   - 名称：`OpenClaw-Nightly-Security-Audit`

3. **配置触发器**
   - 触发器：每天
   - 时间：03:00:00

4. **配置操作**
   - 操作：启动程序
   - 程序：`pwsh.exe`
   - 参数：`-NoProfile -ExecutionPolicy Bypass -File "D:\OpenClaw\workspace\nightly-security-audit.ps1"`

5. **完成配置**
   - 勾选 "打开属性对话框"
   - 常规选项卡：勾选 "使用最高权限运行"
   - 条件选项卡：配置网络/电源选项

---

## 🔍 验证命令

**查看任务状态:**
```powershell
Get-ScheduledTask -TaskName "OpenClaw-Nightly-Security-Audit" | Select-Object TaskName, State, LastRunTime, NextRunTime
```

**手动触发测试:**
```powershell
Start-ScheduledTask -TaskName "OpenClaw-Nightly-Security-Audit"
```

**查看任务历史:**
```powershell
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-TaskScheduler/Operational'; Id=100} | Where-Object {$_.Message -like "*OpenClaw-Nightly-Security-Audit*"} | Select-Object -First 10
```

**查看审计报告:**
```powershell
Get-ChildItem D:\OpenClaw\workspace\memory\security-audit-*.md | Sort-Object LastWriteTime -Descending | Select-Object -First 3
```

---

## 📊 定时任务配置总览

| 任务名称 | 执行时间 | 状态 |
|----------|----------|------|
| OpenClaw-Arxiv-Collector | 每日 2:00 AM | ✅ 已配置 |
| **OpenClaw-Nightly-Security-Audit** | **每日 3:00 AM** | ⏳ **待配置** |
| OpenClaw-Medium-Watcher | 每日 4:00 AM | ✅ 已配置 |
| OpenClaw-Memory-Distiller | 每周日 5:00 AM | ✅ 已配置 |
| OpenClaw-Daily-Collect | 每日 9:00 AM | ✅ 已配置 |
| OpenClaw-Weekly-Report | 每周一 10:00 AM | ✅ 已配置 |

---

## 📁 相关文件

| 文件 | 说明 |
|------|------|
| `nightly-security-audit.ps1` | 安全审计脚本 (3.2KB) |
| `setup-security-audit-task.ps1` | 定时任务安装脚本 (2.5KB) |
| `memory/security-audit-*.md` | 审计报告输出 |

---

## ⚠️ 注意事项

1. **权限要求:** 需要管理员权限创建定时任务
2. **用户账户:** 任务以 `huawei` 用户身份运行
3. **电源设置:** 配置为 "电池供电时也运行"
4. **网络要求:** 配置为 "仅在网络可用时运行"
5. **执行超时:** 限制为 1 小时，避免长时间占用

---

## 🔧 故障排查

**问题:** 任务创建失败，提示 "拒绝访问"
- **解决:** 以管理员身份运行 PowerShell

**问题:** 任务未执行
- **检查:** 任务计划程序历史记录
- **检查:** 用户账户权限
- **检查:** 电源/网络条件

**问题:** 脚本执行失败
- **检查:** `memory/security-audit-*.md` 错误信息
- **检查:** PowerShell 执行策略
- **检查:** 脚本路径是否正确

---

*配置完成后，每日凌晨 3:00 自动执行安全审计*
