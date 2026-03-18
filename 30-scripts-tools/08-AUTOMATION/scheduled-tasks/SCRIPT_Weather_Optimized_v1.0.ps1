# Optimized Weather Script for OpenClaw
param(
    [string]$Location = "",
    [string]$Format = "current",
    [switch]$Celsius,
    [switch]$Fahrenheit,
    [string]$Language = "zh-cn",
    [int]$CacheTTL = 1800
)

$CacheDir = "$env:TEMP\weather-cache"
$ErrorActionPreference = "Stop"

if (!(Test-Path $CacheDir)) {
    New-Item -ItemType Directory -Path $CacheDir -Force | Out-Null
}

$unit = ""
if ($Celsius) { $unit = "m" }
if ($Fahrenheit) { $unit = "u" }

$langMap = @{
    "zh-cn" = "zh"
    "zh-tw" = "zh-tw"
    "en" = "en"
    "ja" = "ja"
    "ko" = "ko"
}
$lang = if ($langMap.ContainsKey($Language)) { $langMap[$Language] } else { "zh" }

function Get-CacheKey {
    param($loc, $fmt, $u)
    $safeLoc = $loc -replace '[^a-zA-Z0-9]', '_'
    return "weather_{0}_{1}_{2}.json" -f $safeLoc, $fmt, $u
}

function Get-FromCache {
    param($key)
    $cachePath = Join-Path $CacheDir $key
    if (Test-Path $cachePath) {
        $cache = Get-Content $cachePath -Raw | ConvertFrom-Json
        $cacheTime = [DateTime]::Parse($cache.timestamp)
        $age = (New-TimeSpan -Start $cacheTime -End (Get-Date)).TotalSeconds
        if ($age -lt $CacheTTL) {
            Write-Host "From cache ($([math]::Round($CacheTTL - $age, 0))s left)" -ForegroundColor Gray
            return $cache.data
        }
    }
    return $null
}

function Save-ToCache {
    param($key, $data)
    $cachePath = Join-Path $CacheDir $key
    $cacheObj = New-Object PSObject -Property @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        data = $data
    }
    $cacheObj | ConvertTo-Json -Depth 10 | Out-File -FilePath $cachePath -Encoding utf8 -Force
}

function Get-Weather {
    param($location, $format)
    
    # Simple URL encoding (replace spaces with +)
    $encodedLocation = $location -replace ' ', '+'
    $baseUrl = "https://wttr.in/{0}" -f $encodedLocation
    $queryParams = @()
    
    if ($format -eq "current" -or $format -eq "forecast") {
        $queryParams += "format=j1"
    } elseif ($format -eq "week") {
        $queryParams += "format=v2"
    }
    
    if ($unit) { $queryParams += $unit }
    $queryParams += "lang={0}" -f $lang
    
    $url = $baseUrl
    if ($queryParams.Count -gt 0) {
        $url += "?{0}" -f ($queryParams -join "&")
    }
    
    $cacheKey = Get-CacheKey $location $format $unit
    $cached = Get-FromCache $cacheKey
    if ($cached) {
        return $cached
    }
    
    $maxRetries = 3
    $retryCount = 0
    while ($retryCount -lt $maxRetries) {
        try {
            Write-Host "Fetching weather data..." -ForegroundColor Cyan
            $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 10
            Save-ToCache $cacheKey $response
            return $response
        } catch {
            $retryCount++
            if ($retryCount -eq $maxRetries) {
                throw "Weather service unavailable after $retryCount retries: $_"
            }
            Start-Sleep -Seconds (2 * $retryCount)
        }
    }
}

function Format-WeatherOutput {
    param($data, $format)
    
    if ($format -eq "current" -and $data.current_condition) {
        $current = $data.current_condition[0]
        $nearestArea = $data.nearest_area[0]
        $locationName = $nearestArea.areaName[0].value
        
        if ($locationName.Length -gt 25) {
            $locationName = $locationName.Substring(0, 22) + "..."
        }
        
        $tempC = $current.temp_C
        $feelsLike = $current.FeelsLikeC
        $weatherDesc = $current.weatherDesc[0].value
        $windSpeed = $current.windspeedKmph
        $windDir = $current.winddir16Point
        $humidity = $current.humidity
        $chanceOfRain = $current.chanceofrain
        $visibility = $current.visibility
        
        $output = @"

+==========================================+
|         Weather Conditions               |
+==========================================+
| Location: $("{0,-25}" -f $locationName) |
| Temperature: $("{0,-21}" -f ("{0}C" -f $tempC)) |
| Feels Like: $("{0,-22}" -f ("{0}C" -f $feelsLike)) |
| Condition: $("{0,-23}" -f $weatherDesc) |
| Wind: $("{0,-26}" -f ("{0} km/h {1}" -f $windSpeed, $windDir)) |
| Humidity: $("{0,-24}" -f ("{0}%" -f $humidity)) |
| Precip: $("{0,-25}" -f ("{0}%" -f $chanceOfRain)) |
| Visibility: $("{0,-22}" -f ("{0} km" -f $visibility)) |
+==========================================+

"@
        return $output
    }
    
    if ($format -eq "forecast" -and $data.weather) {
        $output = "`nWeather Forecast`n"
        $output += "=" * 40 + "`n"
        
        for ($i = 0; $i -lt [Math]::Min(3, $data.weather.Count); $i++) {
            $day = $data.weather[$i]
            $date = $day.date
            $maxTemp = $day.maxtempC
            $minTemp = $day.mintempC
            $weatherDesc = $day.avgWeatherDesc[0].value
            $chanceOfRain = $day.chanceofrain
            
            $output += @"

Date: $date
  High: $maxTemp C  Low: $minTemp C
  Condition: $weatherDesc
  Precip Chance: $chanceOfRain%

"@
        }
        return $output
    }
    
    return $data | ConvertTo-Json -Depth 5
}

try {
    if ([string]::IsNullOrWhiteSpace($Location)) {
        Write-Host "Detecting your location..." -ForegroundColor Cyan
        try {
            $ipInfo = Invoke-RestMethod -Uri "https://ipapi.co/json/" -TimeoutSec 5
            $Location = $ipInfo.city
            Write-Host "Detected location: $Location" -ForegroundColor Green
        } catch {
            $Location = "Beijing"
            Write-Host "Cannot detect location, using default: $Location" -ForegroundColor Yellow
        }
    }
    
    $weatherData = Get-Weather -Location $Location -Format $Format
    $output = Format-WeatherOutput -Data $weatherData -Format $Format
    Write-Host $output
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
