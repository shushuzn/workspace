# Simple Optimized Weather Script
# Uses wttr.in directly with caching

param(
    [string]$Location = "",
    [string]$Format = "0",  # 0=current, 1=tomorrow, 2=day after, F=forecast
    [switch]$Celsius,
    [switch]$Fahrenheit,
    [int]$CacheTTL = 1800
)

$CacheDir = "$env:TEMP\weather-cache"

if (!(Test-Path $CacheDir)) {
    New-Item -ItemType Directory -Path $CacheDir -Force | Out-Null
}

$unit = ""
if ($Celsius) { $unit = "?m" }
if ($Fahrenheit) { $unit = "?u" }

function Get-CacheKey {
    param($loc, $fmt, $u)
    $safeLoc = $loc -replace '[^a-zA-Z0-9]', '_'
    return "weather_{0}_{1}_{2}.txt" -f $safeLoc, $fmt, $u
}

function Get-FromCache {
    param($key)
    $cachePath = Join-Path $CacheDir $key
    if (Test-Path $cachePath) {
        $cacheTime = (Get-Item $cachePath).LastWriteTime
        $age = (New-TimeSpan -Start $cacheTime -End (Get-Date)).TotalSeconds
        if ($age -lt $CacheTTL) {
            Write-Host "From cache ($([math]::Round($CacheTTL - $age, 0))s left)" -ForegroundColor Gray
            return Get-Content $cachePath -Raw -Encoding UTF8
        }
    }
    return $null
}

function Save-ToCache {
    param($key, $data)
    $cachePath = Join-Path $CacheDir $key
    $data | Out-File -FilePath $cachePath -Encoding UTF8 -Force
}

function Get-Weather {
    param($location, $format, $unit)
    
    $encodedLocation = $location -replace ' ', '+'
    $url = "https://wttr.in/{0}{1}{2}" -f $encodedLocation, $format, $unit
    
    $cacheKey = Get-CacheKey $location $format $unit
    $cached = Get-FromCache $cacheKey
    if ($cached) {
        return $cached
    }
    
    Write-Host "Fetching weather..." -ForegroundColor Cyan
    
    $maxRetries = 3
    $retryCount = 0
    while ($retryCount -lt $maxRetries) {
        try {
            $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 15
            Save-ToCache $cacheKey $response
            return $response
        } catch {
            $retryCount++
            if ($retryCount -eq $maxRetries) {
                throw "Weather service unavailable: $_"
            }
            Start-Sleep -Seconds (2 * $retryCount)
        }
    }
}

try {
    if ([string]::IsNullOrWhiteSpace($Location)) {
        Write-Host "Detecting location..." -ForegroundColor Cyan
        try {
            $ipInfo = Invoke-RestMethod -Uri "https://ipapi.co/json/" -TimeoutSec 5
            $Location = $ipInfo.city
            Write-Host "Detected: $Location" -ForegroundColor Green
        } catch {
            $Location = "Beijing"
            Write-Host "Using default: $Location" -ForegroundColor Yellow
        }
    }
    
    $weatherData = Get-Weather -Location $Location -Format $Format -Unit $unit
    Write-Host $weatherData
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
