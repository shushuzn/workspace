# MCP 宸ュ叿闆嗘垚鎸囧崡

**鍒涘缓鏃堕棿:** 2026-03-04  
**鏈€鍚庢洿鏂?** 2026-03-05 01:10  
**鐘舵€?** 鉁?宸查厤缃?(4 涓湇鍔″櫒)

---

## 馃摝 浠€涔堟槸 MCP锛?

**MCP (Model Context Protocol)** 鏄繛鎺?LLM 涓庡閮ㄧ郴缁熺殑鏍囧噯鍗忚锛屾彁渚涳細
- 鏍囧噯鍖栧伐鍏锋帴鍙?
- 璺ㄥ钩鍙颁簰鎿嶄綔鎬?
- 瀹夊叏鐨勬潈闄愭帶鍒?

---

## 馃殌 蹇€熷紑濮?

### 1. 鍒濆鍖栭厤缃?

```powershell
cd D:\OpenClaw\workspace\scripts
py mcp-integrator.py init
```

鐢熸垚閰嶇疆鏂囦欢锛歚D:\OpenClaw\workspace\mcp-config.json`

### 2. 鏌ョ湅鍙敤宸ュ叿

```powershell
py mcp-integrator.py list
```

### 3. 鏌ョ湅鐘舵€?

```powershell
py mcp-integrator.py status
```

---

## 馃敡 鍙敤 MCP 鏈嶅姟鍣?

### 鉁?宸插惎鐢?(4 涓?

| 鏈嶅姟鍣?| 鍔熻兘 | 妯″紡 | 鐘舵€?|
|--------|------|------|------|
| **filesystem** | 鏂囦欢绯荤粺鎿嶄綔 | HTTP (8080) | 鉁?闇€淇 |
| **fetch** | 缃戦〉鍐呭鎶撳彇 | stdio | 鉁?鍙敤 |
| **github** | GitHub API | stdio | 鉁?宸查厤缃?|
| **notion** | Notion API | stdio | 鉁?宸查厤缃?|
| **tavily** | Tavily 鏅鸿兘鎼滅储 | stdio | 鉁?宸查厤缃?|

### 鈴革笍 寰呭惎鐢?

| 鏈嶅姟鍣?| 鍔熻兘 | 閰嶇疆瑕佹眰 |
|--------|------|---------|
| **slack** | Slack 娑堟伅 | 璁剧疆 `SLACK_TOKEN` 鐜鍙橀噺 |
| **postgres** | PostgreSQL | 閰嶇疆鏁版嵁搴撹繛鎺ュ瓧绗︿覆 |

---

## 馃洜锔?宸ュ叿鍒楄〃

### 鏂囦欢绯荤粺宸ュ叿

| 宸ュ叿 | 鍔熻兘 | 鍙傛暟 |
|------|------|------|
| `filesystem.read_file` | 璇诲彇鏂囦欢 | `{"path": "鏂囦欢璺緞"}` |
| `filesystem.write_file` | 鍐欏叆鏂囦欢 | `{"path": "璺緞", "content": "鍐呭"}` |
| `filesystem.search` | 鎼滅储鏂囦欢 | `{"pattern": "*.md", "path": "鐩綍"}` |
| `filesystem.list_directory` | 鍒楀嚭鐩綍 | `{"path": "鐩綍璺緞"}` |

### 缃戦〉鎶撳彇宸ュ叿

| 宸ュ叿 | 鍔熻兘 | 鍙傛暟 |
|------|------|------|
| `fetch.get` | 鑾峰彇缃戦〉 | `{"url": "https://..."}` |

### GitHub 宸ュ叿

| 宸ュ叿 | 鍔熻兘 | 鍙傛暟 |
|------|------|------|
| `github.get_issue` | 鑾峰彇 issue | `{"owner": "", "repo": "", "issue_number": 1}` |
| `github.create_issue` | 鍒涘缓 issue | `{"owner": "", "repo": "", "title": "", "body": ""}` |
| `github.list_issues` | 鍒楀嚭 issues | `{"owner": "", "repo": "", "state": "open"}` |
| `github.get_pull_request` | 鑾峰彇 PR | `{"owner": "", "repo": "", "pull_number": 1}` |

### Notion 宸ュ叿

| 宸ュ叿 | 鍔熻兘 | 鍙傛暟 |
|------|------|------|
| `notion.query_database` | 鏌ヨ鏁版嵁搴?| `{"database_id": "xxx"}` |
| `notion.create_page` | 鍒涘缓椤甸潰 | `{"parent": {}, "properties": {}}` |
| `notion.append_block` | 娣诲姞鍧?| `{"block_id": "xxx", "children": []}` |

### Tavily 鎼滅储宸ュ叿

| 宸ュ叿 | 鍔熻兘 | 鍙傛暟 |
|------|------|------|
| `tavily.search` | 鏅鸿兘鎼滅储 | `{"query": "鍏抽敭璇?, "max_results": 5}` |
| `tavily.extract` | 鎻愬彇鍐呭 | `{"url": "https://..."}` |

---

## 馃摉 浣跨敤绀轰緥

### 绀轰緥 1: 鎼滅储鏂囦欢

```python
from mcp-integrator import call_tool
import asyncio

result = asyncio.run(call_tool("filesystem.search", {
    "pattern": "*.md",
    "path": "D:\\OpenClaw\\workspace\\Arxiv"
}))

print(f"鎵惧埌 {len(result['files'])} 涓枃浠?)
```

### 绀轰緥 2: 璇诲彇鏂囦欢

```python
result = asyncio.run(call_tool("filesystem.read_file", {
    "path": "D:\\OpenClaw\\workspace\\MEMORY.md"
}))

print(result['content'][:500])
```

### 绀轰緥 3: 鎶撳彇缃戦〉

```python
result = asyncio.run(call_tool("fetch.get", {
    "url": "https://arxiv.org/list/cs.AI/recent"
}))

print(f"鐘舵€佺爜锛歿result['status']}")
print(f"鍐呭锛歿result['content'][:500]}")
```

### 绀轰緥 4: 鍐欏叆鏂囦欢

```python
result = asyncio.run(call_tool("filesystem.write_file", {
    "path": "D:\\OpenClaw\\workspace\\mcp-output\\test.md",
    "content": "# 娴嬭瘯\n\n杩欐槸 MCP 宸ュ叿鐢熸垚鐨勫唴瀹广€?
}))

print(f"鍐欏叆鎴愬姛锛歿result['success']}")
```

---

## 鈿欙笍 鐜鍙橀噺閰嶇疆

### 蹇呴渶鐨勭幆澧冨彉閲?

```powershell
# GitHub Token
$env:GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# Notion Integration Token
$env:NOTION_INTEGRATION_TOKEN="secret_xxxxxxxxxxxx"

# Tavily API Key
$env:TAVILY_API_KEY="tvly-xxxxxxxxxxxx"
```

### 姘镐箙璁剧疆锛堢敤鎴风骇鍒級

```powershell
[System.Environment]::SetEnvironmentVariable('GITHUB_TOKEN', 'ghp_xxx', 'User')
[System.Environment]::SetEnvironmentVariable('NOTION_INTEGRATION_TOKEN', 'secret_xxx', 'User')
[System.Environment]::SetEnvironmentVariable('TAVILY_API_KEY', 'tvly-xxx', 'User')
```

### 鑾峰彇 API Key

| 鏈嶅姟 | 鑾峰彇鍦板潃 | 鏉冮檺瑕佹眰 |
|------|---------|---------|
| GitHub | https://github.com/settings/tokens | `repo` |
| Notion | https://www.notion.so/my-integrations | 鍒涘缓 Integration |
| Tavily | https://app.tavily.com/home | API Keys |

---

## 馃敡 Filesystem MCP HTTP 妯″紡淇

**闂:** Filesystem MCP 鍦?stdio 妯″紡涓嬪彲鑳藉嚭鐜拌繛鎺ラ棶棰?

**瑙ｅ喅鏂规:** 浣跨敤 HTTP 妯″紡杩愯

```powershell
# 鍚姩 HTTP 妯″紡
npx -y @modelcontextprotocol/server-filesystem D:\OpenClaw\workspace --port 8080

# 楠岃瘉鏈嶅姟
curl http://localhost:8080/health
```

**閰嶇疆:** `mcp-config.json` 涓凡璁剧疆 `"mode": "http", "port": 8080`

---

## 馃搳 娴嬭瘯缁撴灉

**娴嬭瘯鏃堕棿:** 2026-03-04 03:12

| 宸ュ叿 | 鐘舵€?| 缁撴灉 |
|------|------|------|
| `filesystem.search` | 鉁?| 鎵惧埌 50 涓枃浠?|
| `filesystem.read_file` | 鉁?| 璇诲彇鎴愬姛 |
| `fetch.get` | 鉁?| 鎶撳彇鎴愬姛锛堢姸鎬佺爜 200锛?|

**寰呮祴璇?**
- [ ] Tavily 鎼滅储闆嗘垚
- [ ] Notion 鏁版嵁搴撴煡璇?
- [ ] GitHub issues 鎿嶄綔

---

## 馃攲 鎵╁睍 MCP 鏈嶅姟鍣?

### 瀹夎鏂版湇鍔″櫒

```powershell
# 绀轰緥锛氬畨瑁?Git 鏈嶅姟鍣?
npx -y @modelcontextprotocol/server-git

# 绀轰緥锛氬畨瑁?AWS 鏈嶅姟鍣?
npx -y @modelcontextprotocol/server-aws
```

### 娣诲姞鍒伴厤缃?

缂栬緫 `mcp-config.json`:

```json
{
  "servers": {
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"],
      "description": "Git 鎿嶄綔",
      "enabled": true
    }
  }
}
```

---

## 馃搧 杈撳嚭鐩綍

MCP 宸ュ叿杈撳嚭淇濆瓨鍒帮細`D:\OpenClaw\workspace\mcp-output\`

---

## 馃洃 绂佺敤鏈嶅姟鍣?

```powershell
py mcp-integrator.py disable github
```

---

## 馃摉 鐩稿叧璧勬簮

- MCP 瀹樼綉锛歨ttps://modelcontextprotocol.io
- MCP 鏈嶅姟鍣ㄥ垪琛細https://github.com/modelcontextprotocol/servers
- 鏈湴鑴氭湰锛歚D:\OpenClaw\workspace\scripts\mcp-integrator.py`

---

**鏈€鍚庢洿鏂?** 2026-03-04

---

## 馃敊 Backlinks

**Documents linking here:**
- [[link-recommendations]] - link-recommendations

