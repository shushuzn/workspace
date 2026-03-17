# 🌤️ 超级优化版天气查询工具 v2.0

## ✨ 新特性总览

| 功能 | 说明 | 状态 |
|------|------|------|
| 📦 智能缓存 | 30 分钟缓存，减少 API 请求 | ✅ |
| 🌍 自动定位 | IP 检测位置，多服务 fallback | ✅ |
| 🔄 错误重试 | 3 次重试 + 指数退避 | ✅ |
| 📝 详细日志 | 按日记录，便于调试 | ✅ |
| 🔌 离线模式 | 无网络时显示友好提示 | ✅ |
| ⚙️ 配置文件 | 自定义默认参数 | ✅ |
| 🌐 多语言 | 支持 9 种语言 | ✅ |
| 📊 JSON 输出 | 机器可读格式 | ✅ |
| 🔍 网络检测 | 自动判断网络状态 | ✅ |
| 💾 配置持久化 | 记住常用位置 | ✅ |

---

## 📦 文件清单

```
scripts/
├── weather-v2.ps1              # 主程序（推荐）
├── weather-simple.ps1          # 简化版
├── weather-optimized.ps1       # 完整版
├── weather.sh                  # Bash 版 (Linux/Mac)
├── weather.bat                 # Windows 快捷启动
├── weather                     # PowerShell 快捷启动
├── weather-config.example.json # 配置模板
└── README-weather.md           # 说明文档
```

---

## 🚀 快速开始

### Windows

```powershell
# 方式 1：直接运行
.\scripts\weather-v2.ps1

# 方式 2：使用 bat 启动器
.\scripts\weather.bat

# 方式 3：指定城市
.\scripts\weather-v2.ps1 -Location "Shanghai"
```

### Linux / Mac

```bash
# 使用 Bash 版本
./scripts/weather.sh Beijing

# 或 PowerShell Core
pwsh -File scripts/weather-v2.ps1 -Location "Tokyo"
```

---

## 📖 参数说明

### 基本参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-Location` | string | 自动检测 | 城市名或机场代码 |
| `-Format` | string | "0" | 0=当前，1=明天，2=后天，F=3 天预报 |
| `-Celsius` | switch | - | 使用摄氏度 |
| `-Fahrenheit` | switch | - | 使用华氏度 |
| `-Language` | string | "zh" | 语言 (zh/en/ja/ko 等) |
| `-CacheTTL` | int | 1800 | 缓存时间（秒） |
| `-NoCache` | switch | - | 禁用缓存 |
| `-Verbose` | switch | - | 显示详细日志 |
| `-JSON` | switch | - | JSON 格式输出 |

### 格式代码

| 代码 | 说明 | 示例 |
|------|------|------|
| `0` | 当前天气 | 北京现在的气温 |
| `1` | 明天预报 | 明天会下雨吗 |
| `2` | 后天预报 | 后天气温如何 |
| `F` | 3 天预报 | 周末天气怎么样 |

---

## 💡 使用示例

### 日常查询

```powershell
# 自动检测位置，查询当前天气
.\scripts\weather-v2.ps1

# 查询指定城市
.\scripts\weather-v2.ps1 -Location "Beijing"

# 查询明天天气
.\scripts\weather-v2.ps1 -Location "Shanghai" -Format "1"

# 3 天预报
.\scripts\weather-v2.ps1 -Location "Guangzhou" -Format "F"
```

### 国际查询

```powershell
# 英文输出
.\scripts\weather-v2.ps1 -Location "London" -Language "en"

# 华氏度
.\scripts\weather-v2.ps1 -Location "New York" -Fahrenheit

# 日文
.\scripts\weather-v2.ps1 -Location "Tokyo" -Language "ja"
```

### 高级用法

```powershell
# 禁用缓存，强制刷新
.\scripts\weather-v2.ps1 -Location "Beijing" -NoCache

# 详细日志模式
.\scripts\weather-v2.ps1 -Location "Beijing" -Verbose

# JSON 输出（用于脚本处理）
.\scripts\weather-v2.ps1 -Location "Beijing" -JSON | ConvertFrom-Json

# 延长缓存时间到 1 小时
.\scripts\weather-v2.ps1 -Location "Beijing" -CacheTTL 3600
```

---

## ⚙️ 配置文件

首次运行后会自动创建 `weather-config.json`：

```json
{
  "DefaultLocation": "Beijing",
  "DefaultFormat": "0",
  "DefaultLanguage": "zh",
  "CacheTTL": 1800,
  "Timeout": 10,
  "MaxRetries": 3,
  "AutoDetect": true
}
```

### 配置项说明

| 配置项 | 说明 | 推荐值 |
|--------|------|--------|
| `DefaultLocation` | 默认城市 | 你所在的城市 |
| `DefaultFormat` | 默认格式 | "0" |
| `DefaultLanguage` | 默认语言 | "zh" |
| `CacheTTL` | 缓存时间（秒） | 1800 (30 分钟) |
| `Timeout` | 请求超时（秒） | 10 |
| `MaxRetries` | 最大重试次数 | 3 |
| `AutoDetect` | 自动检测位置 | true |

---

## 📊 输出示例

### 当前天气

```
╔══════════════════════════════════════════╗
║         🌤️  实时天气                     ║
╠══════════════════════════════════════════╣
║ 📍 地点：Beijing                    ║
║ 🌡️  温度：3°C                       ║
║ 😊 体感：1°C                        ║
║ ☁️  天气：Overcast                  ║
║ 💨 风速：7 km/h SSW               ║
║ 💧 湿度：70%                        ║
║ 🌧️  降水：0%                        ║
║ 👁️  能见度：10 km                     ║
╚══════════════════════════════════════════╝
```

### 缓存提示

```
📦 从缓存读取 (剩余：1245s)
```

### 离线模式

```
⚠️  离线模式 - 显示示例数据
╔══════════════════════════════════════════╗
║         🌤️  实时天气 (离线模式)          ║
╠══════════════════════════════════════════╣
║ 💡 提示：检查网络连接后重试              ║
╚══════════════════════════════════════════╝
```

---

## 🔧 故障排除

### 问题 1：无法获取天气数据

**原因：** 网络连接问题或 wttr.in 服务不可用

**解决：**
```powershell
# 1. 检查网络
Test-NetConnection wttr.in -Port 80

# 2. 使用详细模式查看错误
.\scripts\weather-v2.ps1 -Verbose

# 3. 检查日志文件
Get-Content "$env:TEMP\weather-logs\weather-$(Get-Date -Format 'yyyy-MM-dd').log"
```

### 问题 2：位置检测失败

**原因：** IP 定位服务不可用

**解决：**
```powershell
# 手动指定城市
.\scripts\weather-v2.ps1 -Location "YourCity"

# 或修改配置文件
notepad scripts\weather-config.json
```

### 问题 3：缓存不生效

**原因：** 缓存目录权限问题

**解决：**
```powershell
# 清理缓存
Remove-Item "$env:TEMP\weather-cache\*" -Force

# 检查目录权限
Get-Acl "$env:TEMP\weather-cache" | Format-List
```

---

## 📁 目录结构

```
%TEMP%/
├── weather-cache/          # 缓存文件
│   ├── weather_Beijing_0__.txt
│   └── ...
└── weather-logs/           # 日志文件
    └── weather-2026-03-02.log
```

---

## 🔐 隐私说明

- **位置检测：** 仅用于获取天气，不存储个人信息
- **缓存数据：** 仅包含天气数据，本地存储
- **日志文件：** 仅记录操作，不包含敏感信息
- **无追踪：** 不收集任何用户行为数据

---

## 📝 更新日志

### v2.0 (2026-03-02)
- ✅ 新增离线模式
- ✅ 新增配置文件支持
- ✅ 新增详细日志功能
- ✅ 新增网络状态检测
- ✅ 新增多位置服务 fallback
- ✅ 优化错误处理和重试机制
- ✅ 优化输出格式
- ✅ 新增 JSON 输出模式

### v1.0 (初始版本)
- 基础天气查询功能
- 简单缓存机制
- 自动位置检测

---

## 🙏 致谢

- 数据源：[wttr.in](https://wttr.in)
- 灵感来源：OpenClaw Weather Skill

---

## 📄 许可证

MIT License - 自由使用、修改和分发
