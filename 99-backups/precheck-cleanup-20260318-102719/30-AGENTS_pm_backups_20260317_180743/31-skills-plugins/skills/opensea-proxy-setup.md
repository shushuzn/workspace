# OpenSea MCP 代理配置指南

**配置时间:** 2026-03-07 12:57  
**状态:** ✅ 代理配置已创建

---

## 🌐 代理配置

### 代理地址

**默认代理:** `http://127.0.0.1:7890`

**如果不同，请修改为:**
- 你的代理地址
- 你的代理端口

---

## 📁 配置文件

### 带代理的 MCP 配置

**文件:** `skills/opensea-mcp-proxy-config.json`

**内容:**
```json
{
  "mcpServers": {
    "opensea": {
      "url": "https://mcp.opensea.io/mcp",
      "headers": {
        "Authorization": "Bearer 043YNIvCADXDtxSyxQDQSYyXUrULyo1GJSJ0yhDueQaMR2cq"
      },
      "env": {
        "HTTPS_PROXY": "http://127.0.0.1:7890",
        "HTTP_PROXY": "http://127.0.0.1:7890",
        "NO_PROXY": "localhost,127.0.0.1"
      }
    }
  }
}
```

---

## 🔧 配置步骤

### Step 1: 确认代理地址

**常见代理地址:**
| 代理软件 | 默认地址 |
|----------|----------|
| Clash | `http://127.0.0.1:7890` |
| V2Ray | `http://127.0.0.1:10809` |
| Shadowsocks | `http://127.0.0.1:1080` |
| Surge | `http://127.0.0.1:6152` |

**如果你的代理不同，请修改配置文件。**

---

### Step 2: 复制配置文件

**PowerShell:**
```powershell
# 备份原配置
Copy-Item "$env:APPDATA\Claude\mcp.json" -Destination "$env:APPDATA\Claude\mcp.json.bak" -Force

# 复制带代理的配置
Copy-Item "D:\OpenClaw\workspace\skills\opensea-mcp-proxy-config.json" -Destination "$env:APPDATA\Claude\mcp.json" -Force
```

---

### Step 3: 验证代理配置

**检查配置文件:**
```powershell
Get-Content "$env:APPDATA\Claude\mcp.json"
```

**预期输出:**
```json
{
  "mcpServers": {
    "opensea": {
      "url": "https://mcp.opensea.io/mcp",
      "headers": {
        "Authorization": "Bearer 043YNIvCADXDtxSyxQDQSYyXUrULyo1GJSJ0yhDueQaMR2cq"
      },
      "env": {
        "HTTPS_PROXY": "http://127.0.0.1:7890",
        "HTTP_PROXY": "http://127.0.0.1:7890"
      }
    }
  }
}
```

---

### Step 4: 测试代理连接

**测试命令:**
```powershell
# 测试代理是否可用
Test-NetConnection -ComputerName mcp.opensea.io -Port 443 -ProxyAddress 127.0.0.1 -ProxyPort 7890
```

**预期输出:**
```
TcpTestSucceeded : True
RemoteAddress    : [IP 地址]
```

---

### Step 5: 重启 Claude

**操作:**
1. 完全退出 Claude Desktop
2. 重新打开 Claude Desktop
3. 在 Claude 中测试

---

## 🧪 测试连接

### 在 Claude 中测试

**测试命令:**
```
@opensea Get the floor price for Bored Ape Yacht Club
```

**或使用 MCP 工具:**
```
Use opensea MCP to get collection stats for boredapeyachtclub
```

---

### 预期响应

```json
{
  "collection": {
    "name": "Bored Ape Yacht Club",
    "slug": "boredapeyachtclub",
    "floor_price": {
      "value": 12.5,
      "currency": "ETH"
    },
    "volume": {
      "1d": 125.5,
      "7d": 890.2,
      "30d": 3500.8
    }
  }
}
```

---

## 🔍 故障排除

### 问题 1: 代理不可用

**错误:**
```
Proxy connection failed
```

**解决:**
1. 确认代理软件已启动
2. 检查代理地址和端口
3. 测试代理是否可用:
   ```powershell
   curl -x http://127.0.0.1:7890 https://www.google.com
   ```

---

### 问题 2: 代理地址错误

**错误:**
```
Unable to connect to proxy
```

**解决:**
1. 检查代理软件配置的端口
2. 修改配置文件中的代理地址
3. 重启 Claude

---

### 问题 3: 认证失败

**错误:**
```
401 Unauthorized
```

**解决:**
1. 确认 MCP Token 正确
2. 检查 Token 是否过期
3. 重新生成 MCP Token

---

## 📋 常用代理配置

### Clash
```json
{
  "env": {
    "HTTPS_PROXY": "http://127.0.0.1:7890",
    "HTTP_PROXY": "http://127.0.0.1:7890"
  }
}
```

### V2Ray
```json
{
  "env": {
    "HTTPS_PROXY": "http://127.0.0.1:10809",
    "HTTP_PROXY": "http://127.0.0.1:10809"
  }
}
```

### Shadowsocks
```json
{
  "env": {
    "HTTPS_PROXY": "http://127.0.0.1:1080",
    "HTTP_PROXY": "http://127.0.0.1:1080"
  }
}
```

### Surge
```json
{
  "env": {
    "HTTPS_PROXY": "http://127.0.0.1:6152",
    "HTTP_PROXY": "http://127.0.0.1:6152"
  }
}
```

---

## 📚 相关文档

**配置文件:** `skills/opensea-mcp-proxy-config.json`

**配置指南:** `skills/opensea-mcp-setup.md`

**验证报告:** `skills/opensea-verification-report.md`

---

## ✅ 配置检查清单

- [ ] 确认代理软件已启动
- [ ] 确认代理地址和端口
- [ ] 修改配置文件 (如果需要)
- [ ] 复制配置文件到 Claude 目录
- [ ] 验证代理连接
- [ ] 重启 Claude Desktop
- [ ] 测试 MCP 连接
- [ ] 测试功能

---

*代理配置完成！准备测试连接*
