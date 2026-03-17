# OpenClaw Scheduled Tasks Setup

**Created:** 2026-03-13 (Critic v5.0 fix-007)  
**Status:** Script ready, requires admin installation

---

## Overview

This directory contains PowerShell scripts to configure Windows Task Scheduler for OpenClaw automation.

### Scheduled Tasks

| Task Name | Schedule | Purpose |
|-----------|----------|---------|
| OpenClaw-Heartbeat | Every 30 minutes | Heartbeat checks, task monitoring |
| OpenClaw-Domain-Ranking | Daily 9:00 AM | Domain ranking evaluation |
| OpenClaw-Daily-Log | Daily 12:00 AM | Create daily work log |
| LIG-Risk-Monitor | Daily 7:00 AM | LIG risk预警 system |

---

## Installation

### Option 1: Install All Tasks

Run PowerShell as **Administrator**, then:

```powershell
cd "D:\OpenClaw\workspace\30-scripts-脚本工具"
.\heartbeat-scheduler.ps1 -Install
```

### Option 2: Install Specific Tasks

```powershell
# Heartbeat only (every 30 min)
.\heartbeat-scheduler.ps1 -Heartbeat

# Daily tasks only (9AM, 12AM, 7AM)
.\heartbeat-scheduler.ps1 -Daily
```

### Option 3: Manual Installation

If the script fails, manually create tasks in Windows Task Scheduler:

1. Open **Task Scheduler** (taskschd.msc)
2. Click **Create Task** (not Create Basic Task)
3. Configure:
   - **General:** Run with highest privileges
   - **Triggers:** Set schedule (see table above)
   - **Actions:** Start program `PowerShell.exe` or `py.exe`
   - **Conditions:** Uncheck "Start only if on AC power"
4. Click **OK** and enter admin credentials

---

## Verification

Check task status:

```powershell
.\heartbeat-scheduler.ps1 -Status
```

Expected output:
```
[Ready] OpenClaw-Heartbeat
  Last Run: 3/13/2026 11:30:00 AM
  Next Run: 3/13/2026 12:00:00 PM

[Ready] OpenClaw-Domain-Ranking
  Last Run: 3/13/2026 9:00:00 AM
  Next Run: 3/14/2026 9:00:00 AM
...
```

---

## Removal

To remove all scheduled tasks:

```powershell
.\heartbeat-scheduler.ps1 -Remove
```

---

## Generated Scripts

The installer creates these helper scripts:

| Script | Purpose |
|--------|---------|
| `heartbeat-trigger.ps1` | Heartbeat check logic |
| `daily-log-creator.ps1` | Daily log file creation |

---

## Troubleshooting

### "Access Denied" Error
- Run PowerShell as Administrator
- Right-click PowerShell > Run as Administrator

### Task Not Running
- Check task history in Task Scheduler
- Verify script paths are correct
- Check execution policy: `Get-ExecutionPolicy`

### PowerShell Execution Policy
If blocked, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

---

## Files

- `heartbeat-scheduler.ps1` - Main installer script
- `SCHEDULED-TASKS-README.md` - This documentation
- `heartbeat-trigger.ps1` - (Generated) Heartbeat logic
- `daily-log-creator.ps1` - (Generated) Log creation

---

*Last Updated:* 2026-03-13 11:35  
*Status:* Ready for installation (admin required)
