# 批量安装 OpenClaw Skills
$skillsFile = "D:\OpenClaw\workspace\skill_ids.txt"
$logFile = "D:\OpenClaw\workspace\install_log.txt"
$errorLog = "D:\OpenClaw\workspace\install_errors.txt"

$skills = Get-Content $skillsFile -Encoding UTF8
$total = $skills.Count
$success = 0
$failed = 0

Write-Host "Starting installation of $total skills..."
Start-Transcript -Path $logFile -Append

foreach ($skillId in $skills) {
    $skillId = $skillId.Trim()
    if ([string]::IsNullOrWhiteSpace($skillId)) { continue }
    
    # 转换格式: 作者-技能名 -> 作者/技能名 (第一个 - 替换为 /)
    $installId = $skillId -replace '^(.+?)-(.+)$', '$1/$2'
    
    Write-Host "Installing: $installId ($installId)"
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    try {
        $result = & clawhub install $installId 2>&1
        if ($LASTEXITCODE -eq 0) {
            $success++
            Write-Host "  [OK] $installId"
        } else {
            $failed++
            Write-Host "  [FAIL] $installId - Exit code: $LASTEXITCODE"
            "$timestamp FAILED: $installId - $result" | Out-File $errorLog -Append -Encoding UTF8
        }
    } catch {
        $failed++
        Write-Host "  [ERROR] $installId - $_"
        "$timestamp ERROR: $installId - $_" | Out-File $errorLog -Append -Encoding UTF8
    }
}

Stop-Transcript

Write-Host "`n========================================"
Write-Host "Installation complete!"
Write-Host "Total: $total, Success: $success, Failed: $failed"
Write-Host "Log: $logFile"
Write-Host "Errors: $errorLog"