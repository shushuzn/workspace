# Google Workspace CLI 安装指南

**创建时间:** 2026-03-07 13:21  
**状态:** ⚠️ 安装失败 (网络问题)

---

## 📦 项目信息

**仓库:** https://github.com/googleworkspace/cli

**用途:** 
- 管理 Google Workspace 资源
- 自动化管理任务
- 与 Google API 交互

---

## 🔧 安装方法

### 方法 1: npm 安装 (推荐)

```bash
npm install -g @googleworkspace/cli
```

**问题:** 需要访问 GitHub 下载二进制文件

---

### 方法 2: 手动下载

**步骤:**

1. **下载二进制文件:**
   ```
   https://github.com/googleworkspace/cli/releases/download/v0.8.0/gws-x86_64-pc-windows-msvc.zip
   ```

2. **解压到目录:**
   ```powershell
   Expand-Archive -Path gws-cli.zip -DestinationPath C:\tools\gws-cli
   ```

3. **添加到 PATH:**
   ```powershell
   $env:Path += ";C:\tools\gws-cli"
   ```

4. **验证安装:**
   ```bash
   gws --version
   ```

---

## 🔑 认证配置

**安装后需要认证:**

```bash
gws auth login
```

**认证流程:**
1. 运行命令
2. 打开浏览器
3. 登录 Google 账号
4. 授权 CLI 访问
5. 复制授权码
6. 粘贴到终端

---

## 📋 可用命令

**查看帮助:**
```bash
gws --help
```

**常用命令:**

| 命令 | 用途 |
|------|------|
| `gws auth login` | 认证登录 |
| `gws drive files list` | 列出 Drive 文件 |
| `gws drive files upload` | 上传文件 |
| `ggsuite gmail send` | 发送邮件 |
| `ggsuite calendar events create` | 创建日程 |
| `ggsuite sheets append` | 添加到表格 |

---

## 💡 使用场景

### 1. 研究数据备份

```bash
# 备份研究数据到 Google Drive
gws drive files upload ./research-data/ --parent-folder-id XXX
```

### 2. 数据存储

```bash
# 使用 Google Sheets 存储数据
ggsuite sheets append --spreadsheet-id XXX --values "data"
```

### 3. 自动通知

```bash
# 任务完成时发送邮件
ggsuite gmail send --to user@example.com --subject "Task Complete"
```

---

## ⚠️ 安装问题

**当前问题:** 网络连接失败

**错误信息:**
```
Error fetching release: read ECONNRESET
```

**解决方案:**
1. 检查网络连接
2. 配置代理 (如果需要)
3. 手动下载二进制文件
4. 稍后重试

---

## 📋 下一步

### 选项 1: 稍后重试

等待网络恢复后：
```bash
npm install -g @googleworkspace/cli
```

### 选项 2: 手动下载

1. 访问 https://github.com/googleworkspace/cli/releases
2. 下载 Windows 版本
3. 手动安装

### 选项 3: 继续其他工作

- Google Workspace CLI 不是必需的
- 可以继续其他任务
- 需要时再安装

---

## 🔗 相关资源

**官方资源:**
- GitHub: https://github.com/googleworkspace/cli
- 文档：https://developers.google.com/workspace
- API: https://developers.google.com/workspace/api

---

*安装指南已创建，等待网络恢复后重试*
