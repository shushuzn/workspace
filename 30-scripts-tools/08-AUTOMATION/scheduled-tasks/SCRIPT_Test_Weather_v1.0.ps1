# 天气脚本测试套件

param([switch]$All)

Write-Host "`nWeather Script Test Suite`n" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Gray

$passed = 0
$failed = 0

function Test-Case {
    param($Name, $ScriptBlock)
    
    Write-Host "`n[Test] $Name" -ForegroundColor Yellow
    
    try {
        & $ScriptBlock
        Write-Host "  PASSED" -ForegroundColor Green
        $script:passed++
    } catch {
        Write-Host "  FAILED: $_" -ForegroundColor Red
        $script:failed++
    }
}

# Test 1: Script files exist
Test-Case "Script files exist" {
    $files = @(
        "weather-v2.ps1",
        "weather-simple.ps1",
        "weather.bat",
        "README-weather.md"
    )
    
    foreach ($file in $files) {
        $path = Join-Path $PSScriptRoot $file
        if (!(Test-Path $path)) {
            throw "File not found: $file"
        }
    }
}

# Test 2: Cache directory writable
Test-Case "Cache directory writable" {
    $testFile = "$env:TEMP\weather-cache\test.txt"
    "test" | Out-File -FilePath $testFile -Encoding UTF8 -Force
    if (!(Test-Path $testFile)) {
        throw "Cannot write to cache directory"
    }
    Remove-Item $testFile -Force
}

# Test 3: Log directory writable
Test-Case "Log directory writable" {
    if (!(Test-Path "$env:TEMP\weather-logs")) {
        New-Item -ItemType Directory -Path "$env:TEMP\weather-logs" -Force | Out-Null
    }
    $testFile = "$env:TEMP\weather-logs\test.txt"
    "test" | Out-File -FilePath $testFile -Encoding UTF8 -Force
    Start-Sleep -Milliseconds 100
    if (!(Test-Path $testFile)) {
        throw "Cannot write to log directory"
    }
    Remove-Item $testFile -Force
}

# Test 4: Config file format
Test-Case "Config file format valid" {
    $configFile = Join-Path $PSScriptRoot "weather-config.example.json"
    if (Test-Path $configFile) {
        $content = Get-Content $configFile -Raw
        $json = $content | ConvertFrom-Json
        if (!$json.DefaultLocation) {
            throw "Config missing DefaultLocation"
        }
    }
}

# Test 5: Parameter validation
Test-Case "Parameters defined" {
    $scriptPath = Join-Path $PSScriptRoot "weather-v2.ps1"
    $scriptContent = Get-Content $scriptPath -Raw
    
    $requiredParams = @("Location", "Format", "Celsius", "Fahrenheit", "Language", "CacheTTL")
    foreach ($param in $requiredParams) {
        $pattern = '[\$]' + $param
        if (!($scriptContent -match $pattern)) {
            throw "Missing parameter: $param"
        }
    }
}

# Test 6: Network test (optional)
if ($All) {
    Test-Case "Network connection" {
        try {
            $response = Invoke-WebRequest -Uri "https://wttr.in" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            if ($response.StatusCode -ne 200) {
                throw "wttr.in returned: $($response.StatusCode)"
            }
        } catch {
            throw "Cannot connect to wttr.in: $_"
        }
    }
    
    Test-Case "Location service" {
        try {
            $response = Invoke-RestMethod -Uri "https://ipapi.co/json/" -TimeoutSec 5 -ErrorAction Stop
            if (!$response.city) {
                throw "Cannot get location"
            }
            Write-Host "  Detected: $($response.city)" -ForegroundColor Gray
        } catch {
            throw "Location detection failed: $_"
        }
    }
}

# Summary
Write-Host ""
Write-Host "==================================================" -ForegroundColor Gray
Write-Host "Results: $passed passed, $failed failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Yellow" })

if ($failed -eq 0) {
    Write-Host "All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some tests failed, please check" -ForegroundColor Yellow
    exit 1
}
