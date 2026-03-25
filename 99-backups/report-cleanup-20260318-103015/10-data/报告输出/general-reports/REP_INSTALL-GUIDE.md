# 📦 依赖安装指南

**日期:** 2026-03-04  
**状态:** Python 依赖 ✅ | CLI 工具 ❌

---

## ✅ 已安装依赖

### Python 包 (全部已安装)

```
beautifulsoup4    4.13.4
feedparser        6.0.12
networkx          3.6.1
PyYAML            6.0.3
requests          2.32.5
requests-cache    1.2.1
requests-file     3.0.1
tqdm              4.67.1
```

**无需额外安装！** ✅

---

## ❌ 待安装 CLI 工具

### 1. Go + blogwatcher

**用途:** 技术博客监控  
**安装时间:** 5 分钟

#### 步骤 1: 安装 Go

1. **下载安装包:**
   - 访问：https://go.dev/dl/
   - 下载：`go-1.22.x.windows-amd64.msi` (Windows)

2. **运行安装程序:**
   - 双击 `.msi` 文件
   - 选择默认安装路径：`C:\Program Files\Go`
   - 勾选 "Add Go to PATH"
   - 完成安装

3. **验证安装:**
   ```powershell
   # 关闭并重新打开 PowerShell
   go version
   # 应该输出：go version go1.22.x windows/amd64
   ```

#### 步骤 2: 安装 blogwatcher

```powershell
# 打开新的 PowerShell (确保 PATH 已更新)
go install github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest

# 验证安装
blogwatcher --version
```

#### 步骤 3: 初始化订阅源

```powershell
# 添加 AI 专家博客
blogwatcher add "Andrej Karpathy" https://karpathy.ai/feed.xml
blogwatcher add "Simon Willison" https://simonwillison.net/atom/everything/
blogwatcher add "OpenAI Blog" https://openai.com/blog/rss/
blogwatcher add "Anthropic" https://www.anthropic.com/news/rss

# 查看订阅列表
blogwatcher blogs

# 扫描更新
blogwatcher scan

# 查看文章列表
blogwatcher articles
```

---

### 2. summarize CLI

**用途:** URL/PDF/YouTube 快速摘要  
**安装时间:** 3 分钟

#### Windows 安装方法

**方法 A: 手动下载 (推荐)**

1. **下载最新版本:**
   - 访问：https://github.com/steipete/summarize/releases
   - 下载最新的 `.exe` 文件 (如 `summarize-windows-amd64.exe`)

2. **添加到 PATH:**
   ```powershell
   # 创建目录
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\bin"
   
   # 复制 summarize.exe 到该目录
   Copy-Item "下载的 summarize.exe" "$env:USERPROFILE\bin\summarize.exe"
   
   # 添加到 PATH (永久)
   $env:Path += ";$env:USERPROFILE\bin"
   [Environment]::SetEnvironmentVariable("Path", $env:Path, "User")
   ```

3. **验证安装:**
   ```powershell
   # 关闭并重新打开 PowerShell
   summarize --version
   ```

**方法 B: 使用 Scoop (如果已安装)**

```powershell
# 添加 bucket
scoop bucket add extras

# 安装 summarize
scoop install summarize
```

**方法 C: 使用 Chocolatey (如果已安装)**

```powershell
choco install summarize
```

#### macOS 安装方法

```bash
brew install steipete/tap/summarize
summarize --version
```

#### 测试 summarize

```powershell
# 测试 URL 摘要
summarize "https://karpathy.ai/" --model google/gemini-3-flash-preview

# 测试 PDF (如果有 PDF 文件)
summarize "D:\OpenClaw\workspace\Arxiv\papers\2602.23681.pdf"
```

---

## 🔑 配置 API Keys

### Google API Key (推荐用于 summarize)

1. **获取 API Key:**
   - 访问：https://makersuite.google.com/app/apikey
   - 创建 API Key

2. **设置环境变量:**
   ```powershell
   # 临时设置 (当前会话)
   $env:GOOGLE_API_KEY="你的 API Key"
   
   # 永久设置
   [Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", "你的 API Key", "User")
   ```

### OpenAI API Key (可选)

```powershell
# 临时设置
$env:OPENAI_API_KEY="sk-..."

# 永久设置
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")
```

---

## ✅ 验证安装

### 验证 blogwatcher

```powershell
# 检查版本
blogwatcher --version

# 查看订阅
blogwatcher blogs

# 扫描更新
blogwatcher scan

# 查看文章
blogwatcher articles
```

**预期输出:**
```
Tracked blogs (3):

  Andrej Karpathy
    URL: https://karpathy.ai/feed.xml
  
  Simon Willison
    URL: https://simonwillison.net/atom/everything/
  
  OpenAI Blog
    URL: https://openai.com/blog/rss/
```

### 验证 summarize

```powershell
# 检查版本
summarize --version

# 测试 URL 摘要
summarize "https://karpathy.ai/" --model google/gemini-3-flash-preview
```

**预期输出:**
```
[Summary of the URL]
...
```

---

## 🚀 快速测试流程

### 1. 测试 blogwatcher

```powershell
# 1. 添加订阅
blogwatcher add "Lilian Weng" https://lilianweng.github.io/index.xml

# 2. 扫描更新
blogwatcher scan

# 3. 查看文章
blogwatcher articles

# 4. 标记已读
blogwatcher read 1
```

### 2. 测试 summarize

```powershell
# 1. 测试简单 URL
summarize "https://simonwillison.net/" --model google/gemini-3-flash-preview

# 2. 测试 YouTube (如果有兴趣)
summarize "https://www.youtube.com/watch?v=VIDEO_ID" --youtube auto

# 3. 输出到文件
summarize "https://karpathy.ai/" --model google/gemini-3-flash-preview > Medium/Summarized/test-summary.md
```

---

## ⚠️ 常见问题

### Q1: Go 安装后 `go version` 不识别

**解决:**
1. 关闭所有 PowerShell 窗口
2. 重新打开 PowerShell
3. 检查 PATH: `$env:Path -split ";" | Select-String "Go"`

### Q2: blogwatcher 安装失败

**解决:**
```powershell
# 检查 Go 是否正确安装
go version

# 设置 GOPATH
$env:GOPATH = "$env:USERPROFILE\go"
$env:Path += ";$env:GOPATH\bin"

# 重新安装
go install github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest
```

### Q3: summarize 无法下载

**解决:**
- 使用镜像：https://ghproxy.com/https://github.com/steipete/summarize/releases
- 或等待网络好转再试

### Q4: API Key 错误

**解决:**
```powershell
# 检查环境变量
echo $env:GOOGLE_API_KEY

# 如果为空，重新设置
[Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", "你的 API Key", "User")

# 关闭并重新打开 PowerShell
```

---

## 📝 安装检查清单

- [ ] Go 已安装 (`go version`)
- [ ] blogwatcher 已安装 (`blogwatcher --version`)
- [ ] blogwatcher 订阅源已添加 (`blogwatcher blogs`)
- [ ] summarize 已安装 (`summarize --version`)
- [ ] Google API Key 已配置 (`echo $env:GOOGLE_API_KEY`)
- [ ] blogwatcher 扫描测试成功 (`blogwatcher scan`)
- [ ] summarize 测试成功 (`summarize "https://karpathy.ai/"`)

---

## 🎯 下一步

安装完成后，运行测试：

```powershell
# 1. 测试 blogwatcher
blogwatcher scan

# 2. 测试 summarize
summarize "https://karpathy.ai/" --model google/gemini-3-flash-preview

# 3. 查看输出目录
Get-ChildItem Medium\Blogwatcher
Get-ChildItem Medium\Summarized
```

---

*安装过程中遇到问题？告诉我具体错误信息！* 🔧
