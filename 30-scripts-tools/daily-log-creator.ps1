# Daily Log Creator
# 每日 0:00 AM 创建新的工作日志文件

$workspace = "D:\OpenClaw\workspace"
$today = Get-Date -Format 'yyyy-MM-dd'
$logFile = "$workspace\13-memory-记忆系统\$today.md"

if (-not (Test-Path $logFile)) {
    $header = @"
# $today 工作日志

## 🕐 时间戳
- **创建时间:** $(Get-Date -Format 'o')
- **最后更新:** $(Get-Date -Format 'o')

---

## 📋 今日计划
- [ ] 待填写

---

## 📝 执行记录
- [ ] 待记录

---

*最后更新:* $(Get-Date -Format 'yyyy-MM-dd HH:mm')
*状态:* 🟡 计划中
"@
    $header | Out-File -FilePath $logFile -Encoding UTF8
    Write-Host "Daily log created: $logFile"
}
else {
    Write-Host "Log file already exists: $logFile"
}
