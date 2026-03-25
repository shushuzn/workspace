# 📦 快速安装指南

## ✅ 已完成
- Python 依赖全部安装 ✅

## ❌ 需要手动安装

---

## 步骤 1: 安装 Go (5 分钟)

**为什么需要:** blogwatcher 依赖 Go

### 操作:

1. **打开下载页面:**
   ```
   https://go.dev/dl/
   ```

2. **下载安装包:**
   - 点击：`go-1.22.x.windows-amd64.msi`
   - 等待下载完成

3. **运行安装:**
   - 双击 `.msi` 文件
   - 选择默认安装路径
   - ✅ 确保勾选 "Add Go to PATH"
   - 点击 Next → Install

4. **验证安装:**
   ```powershell
   # 关闭并重新打开 PowerShell
   go version
   # 应输出：go version go1.22.x windows/amd64
   ```

---

## 步骤 2: 安装 blogwatcher (2 分钟)

**安装 Go 后运行:**

```powershell
go install github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest
```

**验证:**
```powershell
blogwatcher --version
```

**初始化订阅:**
```powershell
blogwatcher add "Andrej Karpathy" https://karpathy.ai/feed.xml
blogwatcher add "OpenAI Blog" https://openai.com/blog/rss/
blogwatcher scan
blogwatcher articles
```

---

## 步骤 3: 安装 summarize (3 分钟)

### 方法 A: 自动下载脚本

```powershell
# 创建目录
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\bin"

# 下载 summarize
Invoke-WebRequest -Uri "https://github.com/steipete/summarize/releases/latest/download/summarize-windows-amd64.exe" -OutFile "$env:USERPROFILE\bin\summarize.exe" -UseBasicParsing

# 添加到 PATH
$env:Path += ";$env:USERPROFILE\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path, "User")

# 验证 (需要重新打开 PowerShell)
summarize --version
```

### 方法 B: 手动下载

1. 打开：https://github.com/steipete/summarize/releases
2. 下载：`summarize-windows-amd64.exe`
3. 重命名为：`summarize.exe`
4. 放到：`C:\Users\你的用户名\bin\summarize.exe`

---

## 步骤 4: 配置 Google API Key (2 分钟)

1. **获取 API Key:**
   ```
   https://makersuite.google.com/app/apikey
   ```

2. **设置环境变量:**
   ```powershell
   [Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", "你的 API Key", "User")
   ```

3. **验证:**
   ```powershell
   echo $env:GOOGLE_API_KEY
   ```

---

## 🎯 测试

### 测试 blogwatcher

```powershell
blogwatcher scan
blogwatcher articles
```

### 测试 summarize

```powershell
summarize "https://karpathy.ai/" --model google/gemini-3-flash-preview
```

---

## 📋 检查清单

- [ ] Go 已安装 (`go version`)
- [ ] blogwatcher 已安装 (`blogwatcher --version`)
- [ ] blogwatcher 订阅已添加
- [ ] summarize 已安装 (`summarize --version`)
- [ ] Google API Key 已配置

---

## 🆘 遇到问题？

告诉我具体错误信息，我会帮你解决！
