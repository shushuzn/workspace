# 🌤️ 超级优化版天气查询工具 v2.0
# Super Optimized Weather Tool v2.0

param(
    [string]$Location = "",
    [string]$Format = "0",
    [switch]$Celsius,
    [switch]$Fahrenheit,
    [string]$Language = "zh",
    [int]$CacheTTL = 1800,
    [switch]$NoCache,
    [switch]$Verbose,
    [switch]$JSON
)

# ==================== 配置 ====================
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CacheDir = "$env:TEMP\weather-cache"
$LogDir = "$env:TEMP\weather-logs"
$ConfigFile = Join-Path $ScriptDir "weather-config.json"
$ErrorActionPreference = "Continue"

# ==================== 日志函数 ====================
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    if ($Verbose) {
        $color = switch ($Level) {
            "ERROR" { "Red" }
            "WARN" { "Yellow" }
            "INFO" { "Cyan" }
            "DEBUG" { "Gray" }
            default { "White" }
        }
        Write-Host $logEntry -ForegroundColor $color
    }
    
    # 写入日志文件
    try {
        if (!(Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }
        $logFile = Join-Path $LogDir "weather-$(Get-Date -Format 'yyyy-MM-dd').log"
        $logEntry | Out-File -FilePath $logFile -Append -Encoding UTF8
    } catch { }
}

# ==================== 初始化 ====================
Write-Log "启动天气查询工具" "INFO"

if (!(Test-Path $CacheDir)) {
    try {
        New-Item -ItemType Directory -Path $CacheDir -Force | Out-Null
        Write-Log "创建缓存目录：$CacheDir" "DEBUG"
    } catch {
        Write-Log "无法创建缓存目录：$_" "WARN"
    }
}

# ==================== 加载配置 ====================
$defaultConfig = @{
    DefaultLocation = "Beijing"
    DefaultFormat = "0"
    DefaultLanguage = "zh"
    CacheTTL = 1800
    Timeout = 10
    MaxRetries = 3
    AutoDetect = $true
}

$config = $defaultConfig.Clone()

if (Test-Path $ConfigFile) {
    try {
        $savedConfig = Get-Content $ConfigFile -Raw | ConvertFrom-Json
        foreach ($key in $savedConfig.PSObject.Properties.Name) {
            $config[$key] = $savedConfig.$key
        }
        Write-Log "已加载配置文件" "DEBUG"
    } catch {
        Write-Log "配置文件读取失败，使用默认配置" "WARN"
    }
}

# ==================== 单位设置 ====================
$unitParam = ""
if ($Celsius) { $unitParam = "m" }
elseif ($Fahrenheit) { $unitParam = "u" }

# ==================== 语言映射 ====================
$langMap = @{
    "zh" = "zh"
    "zh-cn" = "zh"
    "zh-tw" = "zh-tw"
    "en" = "en"
    "ja" = "ja"
    "ko" = "ko"
    "es" = "es"
    "fr" = "fr"
    "de" = "de"
    "ru" = "ru"
}
$lang = if ($langMap.ContainsKey($Language)) { $langMap[$Language] } else { "zh" }

# ==================== 缓存函数 ====================
function Get-CacheKey {
    param($loc, $fmt, $u, $l)
    $safeLoc = $loc -replace '[^a-zA-Z0-9]', '_'
    return "weather_{0}_{1}_{2}_{3}.txt" -f $safeLoc, $fmt, $u, $l
}

function Get-FromCache {
    param($key)
    if ($NoCache) { return $null }
    
    $cachePath = Join-Path $CacheDir $key
    if (Test-Path $cachePath) {
        try {
            $cacheTime = (Get-Item $cachePath).LastWriteTimeUtc
            $age = (New-TimeSpan -Start $cacheTime -End (Get-Date).ToUniversalTime()).TotalSeconds
            if ($age -lt $CacheTTL) {
                Write-Log "缓存命中 (剩余：$([math]::Round($CacheTTL - $age, 0))s)" "DEBUG"
                Write-Host "📦 从缓存读取 (剩余：$([math]::Round($CacheTTL - $age, 0))s)" -ForegroundColor Gray
                return Get-Content $cachePath -Raw -Encoding UTF8
            } else {
                Write-Log "缓存过期 (已过期：$([math]::Round($age - $CacheTTL, 0))s)" "DEBUG"
            }
        } catch {
            Write-Log "缓存读取失败：$_" "WARN"
        }
    }
    return $null
}

function Save-ToCache {
    param($key, $data)
    if ($NoCache) { return }
    
    try {
        $cachePath = Join-Path $CacheDir $key
        $data | Out-File -FilePath $cachePath -Encoding UTF8 -Force
        Write-Log "缓存已保存" "DEBUG"
    } catch {
        Write-Log "缓存保存失败：$_" "WARN"
    }
}

# ==================== 位置检测 ====================
function Test-InternetConnection {
    try {
        $response = Invoke-WebRequest -Uri "https://www.microsoft.com" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Get-LocationFromIP {
    Write-Host "🔍 正在检测位置..." -ForegroundColor Cyan
    Write-Log "尝试自动检测位置" "INFO"
    
    $services = @(
        "https://ipapi.co/json/",
        "https://ipapi.com/ip_api.php",
        "https://freeipapi.com/api/json"
    )
    
    foreach ($service in $services) {
        try {
            Write-Log "尝试位置服务：$service" "DEBUG"
            $response = Invoke-RestMethod -Uri $service -TimeoutSec 5 -ErrorAction Stop
            if ($response.city) {
                $city = $response.city
                Write-Host "📍 检测到位置：$city" -ForegroundColor Green
                Write-Log "位置检测成功：$city" "INFO"
                return $city
            }
        } catch {
            Write-Log "位置服务失败 ($service): $_" "DEBUG"
            continue
        }
    }
    
    Write-Log "所有位置服务失败" "WARN"
    return $null
}

# ==================== 天气获取 ====================
function Get-WeatherData {
    param($location, $format, $unit, $lang)
    
    $encodedLocation = $location -replace ' ', '+'
    $url = "https://wttr.in/{0}" -f $encodedLocation
    
    $queryParams = @()
    if ($format -and $format -ne "0") { $queryParams += $format }
    if ($unit) { $queryParams += $unit }
    if ($lang) { $queryParams += "lang=$lang" }
    
    if ($queryParams.Count -gt 0) {
        $url += "?{0}" -f ($queryParams -join "&")
    }
    
    Write-Log "请求 URL: $url" "DEBUG"
    
    # 检查缓存
    $cacheKey = Get-CacheKey $location $format $unit $lang
    $cached = Get-FromCache $cacheKey
    if ($cached) {
        return $cached
    }
    
    # 发送请求
    $maxRetries = $config.MaxRetries
    $timeout = $config.Timeout
    $retryCount = 0
    $lastError = $null
    
    while ($retryCount -lt $maxRetries) {
        try {
            Write-Host "🌤️  正在获取天气数据..." -ForegroundColor Cyan
            Write-Log "发送请求 (尝试 $($retryCount + 1)/$maxRetries)" "INFO"
            
            $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec $timeout -UserAgent "Mozilla/5.0" -ErrorAction Stop
            
            Save-ToCache $cacheKey $response
            Write-Log "天气数据获取成功" "INFO"
            return $response
        } catch {
            $lastError = $_
            $retryCount++
            Write-Log "请求失败 (尝试 $($retryCount)/$maxRetries): $_" "WARN"
            
            if ($retryCount -lt $maxRetries) {
                $delay = 2 * $retryCount
                Write-Host "⚠️  重试中... ($delay 秒)" -ForegroundColor Yellow
                Start-Sleep -Seconds $delay
            }
        }
    }
    
    throw "天气服务不可用（重试 $maxRetries 次后失败）：$($lastError.Exception.Message)"
}

# ==================== 离线模式数据 ====================
function Get-OfflineWeather {
    param($location)
    
    Write-Host "⚠️  离线模式 - 显示示例数据" -ForegroundColor Yellow
    Write-Log "进入离线模式" "WARN"
    
    $offlineData = @"

╔══════════════════════════════════════════╗
║         🌤️  实时天气 (离线模式)          ║
╠══════════════════════════════════════════╣
║ 📍 地点：$("{0,-25}" -f $location) ║
║ 🌡️  温度：$("{0,-25}" -f "--°C") ║
║ 😊 体感：$("{0,-25}" -f "--°C") ║
║ ☁️  天气：$("{0,-25}" -f "暂时无法获取") ║
║ 💨 风速：$("{0,-25}" -f "-- km/h") ║
║ 💧 湿度：$("{0,-25}" -f "--%") ║
║ 🌧️  降水：$("{0,-25}" -f "--%") ║
║ 👁️  能见度：$("{0,-25}" -f "-- km") ║
╠══════════════════════════════════════════╣
║ 💡 提示：检查网络连接后重试              ║
╚══════════════════════════════════════════╝

"@
    return $offlineData
}

# ==================== 格式化输出 ====================
function Format-WeatherOutput {
    param($data, $format, $location)
    
    # 如果数据是文本格式，直接返回
    if ($data -is [string] -and $data.Contains("┌")) {
        return $data
    }
    
    # JSON 模式
    if ($JSON) {
        return $data | ConvertTo-Json -Depth 10
    }
    
    # 尝试解析 JSON
    try {
        $parsed = $data | ConvertFrom-Json
        
        if ($parsed.current_condition) {
            $current = $parsed.current_condition[0]
            $area = $parsed.nearest_area[0]
            $locName = if ($area.areaName) { $area.areaName[0].value } else { $location }
            
            if ($locName.Length -gt 25) { $locName = $locName.Substring(0, 22) + "..." }
            
            $output = @"

╔══════════════════════════════════════════╗
║         🌤️  实时天气                     ║
╠══════════════════════════════════════════╣
║ 📍 地点：$("{0,-25}" -f $locName) ║
║ 🌡️  温度：$("{0,-25}" -f ("{0}°C" -f $current.temp_C)) ║
║ 😊 体感：$("{0,-25}" -f ("{0}°C" -f $current.FeelsLikeC)) ║
║ ☁️  天气：$("{0,-25}" -f $current.weatherDesc[0].value) ║
║ 💨 风速：$("{0,-25}" -f ("{0} km/h {1}" -f $current.windspeedKmph, $current.winddir16Point)) ║
║ 💧 湿度：$("{0,-25}" -f ("{0}%" -f $current.humidity)) ║
║ 🌧️  降水：$("{0,-25}" -f ("{0}%" -f $current.chanceofrain)) ║
║ 👁️  能见度：$("{0,-25}" -f ("{0} km" -f $current.visibility)) ║
╚══════════════════════════════════════════╝

"@
            return $output
        }
    } catch {
        # 不是 JSON，返回原始文本
    }
    
    return $data
}

# ==================== 保存配置 ====================
function Save-Config {
    param($location)
    
    $config.DefaultLocation = $location
    try {
        $config | ConvertTo-Json | Out-File -FilePath $ConfigFile -Encoding UTF8 -Force
        Write-Log "配置已保存" "DEBUG"
    } catch {
        Write-Log "配置保存失败：$_" "WARN"
    }
}

# ==================== 主程序 ====================
try {
    Write-Log "========== 天气查询开始 ==========" "INFO"
    
    # 检查网络连接
    $hasInternet = Test-InternetConnection
    Write-Log "网络连接状态：$hasInternet" "DEBUG"
    
    # 获取位置
    if ([string]::IsNullOrWhiteSpace($Location)) {
        if ($config.AutoDetect -and $hasInternet) {
            $detectedLocation = Get-LocationFromIP
            if ($detectedLocation) {
                $Location = $detectedLocation
                Save-Config $Location
            } else {
                $Location = $config.DefaultLocation
                Write-Host "⚠️  使用默认位置：$Location" -ForegroundColor Yellow
            }
        } else {
            $Location = $config.DefaultLocation
            Write-Host "📍 使用默认位置：$Location" -ForegroundColor Cyan
        }
    }
    
    # 获取天气
    if ($hasInternet) {
        $weatherData = Get-WeatherData -Location $Location -Format $Format -Unit $unitParam -Lang $lang
        $output = Format-WeatherOutput -Data $weatherData -Format $Format -Location $Location
        Write-Host $output
    } else {
        $output = Get-OfflineWeather -Location $Location
        Write-Host $output
    }
    
    Write-Log "========== 天气查询完成 ==========" "INFO"
    
} catch {
    Write-Log "错误：$($_.Exception.Message)" "ERROR"
    Write-Host "❌ 错误：$($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 建议:" -ForegroundColor Cyan
    Write-Host "   1. 检查网络连接" -ForegroundColor Yellow
    Write-Host "   2. 确认城市名称正确" -ForegroundColor Yellow
    Write-Host "   3. 稍后重试" -ForegroundColor Yellow
    exit 1
}
