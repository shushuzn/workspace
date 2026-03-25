# 手动安装 summarize 指南

## ✅ blogwatcher 已完成！

**状态:** 已安装并配置 ✅  
**订阅源:** 3 个博客  
**扫描:** 已完成

---

## 📦 summarize 安装

由于网络原因，需要手动下载：

### 方法 1: 直接下载

1. **打开下载页面:**
   ```
   https://github.com/steipete/summarize/releases
   ```

2. **下载文件:**
   - 点击最新版本的 `summarize-windows-amd64.exe`
   - 或访问：https://github.com/steipete/summarize/releases/latest

3. **保存到:**
   ```
   C:\Users\你的用户名\bin\summarize.exe
   ```

4. **添加到 PATH:**
   ```powershell
   $env:Path += ";$env:USERPROFILE\bin"
   [Environment]::SetEnvironmentVariable("Path", $env:Path, "User")
   ```

5. **验证 (重新打开 PowerShell):**
   ```powershell
   summarize --version
   ```

---

### 方法 2: 使用国内镜像

```powershell
# 创建目录
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\bin"

# 使用镜像下载
$mirror = "https://ghproxy.com/https://github.com/steipete/summarize/releases/latest/download/summarize-windows-amd64.exe"
Invoke-WebRequest -Uri $mirror -OutFile "$env:USERPROFILE\bin\summarize.exe" -UseBasicParsing

# 添加到 PATH
$env:Path += ";$env:USERPROFILE\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path, "User")

# 验证
summarize --version
```

---

## 🔑 配置 Google API Key

```powershell
# 获取 API Key: https://makersuite.google.com/app/apikey

# 设置环境变量
[Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", "你的 API Key", "User")

# 验证
echo $env:GOOGLE_API_KEY
```

---

## 🎯 测试

### blogwatcher

```powershell
blogwatcher blogs
blogwatcher scan
blogwatcher articles
```

### summarize (安装后)

```powershell
summarize --version
summarize "https://karpathy.ai/" --model google/gemini-3-flash-preview
```

---

## ✅ 当前状态

- [x] Go 已安装
- [x] blogwatcher 已安装 ✅
- [x] blogwatcher 已配置 (3 个订阅源)
- [ ] summarize 待手动下载
- [ ] Google API Key 待配置

---

**下一步:** 下载 summarize 并配置 API Key！
