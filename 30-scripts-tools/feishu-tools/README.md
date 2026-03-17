# Feishu API Tools - OpenClaw Integration

📬 Complete Feishu messaging toolkit with auto token management.

## 🚀 Features

- ✅ **Auto Token Refresh** - Caches tokens, refreshes before expiry
- ✅ **Multiple Message Types** - Text, Card, Image, File
- ✅ **Retry Logic** - Automatic retry with exponential backoff
- ✅ **Error Handling** - Comprehensive error detection and reporting
- ✅ **CLI Interface** - Easy command-line usage
- ✅ **Python API** - Import as module for programmatic use

## 📦 Installation

No additional dependencies required! Uses Python standard library + `requests`.

```bash
pip install requests
```

## ⚙️ Configuration

Edit `feishu-config.json`:

```json
{
  "app_id": "your_app_id",
  "app_secret": "your_app_secret",
  "receive_id_type": "open_id",
  "default_receive_id": "your_default_user_id",
  "token_cache_file": "feishu-token-cache.json",
  "token_refresh_before_expiry": 300
}
```

**Fields:**
- `app_id` - Feishu App ID (from Feishu Developer Console)
- `app_secret` - Feishu App Secret (from Feishu Developer Console)
- `receive_id_type` - User ID type: `open_id`, `user_id`, or `union_id`
- `default_receive_id` - Default recipient for messages
- `token_cache_file` - Token cache file name
- `token_refresh_before_expiry` - Refresh token N seconds before expiry (default: 300)

## 💻 Usage

### Command Line

```bash
# Send text message
python feishu-api.py send_text "Hello World"

# Send text to specific user
python feishu-api.py send_text "Hello" ou_xxxxx

# Send interactive card
python feishu-api.py send_card card-template.json

# Send image
python feishu-api.py send_image screenshot.png

# Send file
python feishu-api.py send_file report.pdf

# Check token status
python feishu-api.py token_info

# Force token refresh
python feishu-api.py refresh_token
```

### Python API

```python
from feishu_api import FeishuAPIClient

# Initialize client
client = FeishuAPIClient("feishu-config.json")

# Send text message
client.send_text("Hello from OpenClaw! 🐾")

# Send text to specific user
client.send_text("Private message", receive_id="ou_xxxxx")

# Send interactive card
card_content = {
    "title": "System Notification",
    "elements": [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**Alert:** High CPU usage detected"
            }
        }
    ]
}
client.send_poster("Alert", card_content["elements"])

# Send image
client.send_image("screenshot.png")

# Send file
client.send_file("report.pdf")

# Get token info
info = client.get_token_info()
print(f"Token status: {info['status']}")
print(f"Time left: {info['time_left_formatted']}")
```

## 📋 Card Templates

### Simple Notification

```json
{
  "title": "🔔 Notification",
  "elements": [
    {
      "tag": "div",
      "text": {
        "tag": "lark_md",
        "content": "**Message content here**"
      }
    }
  ]
}
```

### Task Completion

```json
{
  "title": "✅ Task Complete",
  "elements": [
    {
      "tag": "div",
      "text": {
        "tag": "lark_md",
        "content": "**Task:** Data Processing\n**Status:** Success\n**Duration:** 5 minutes"
      }
    },
    {
      "tag": "action",
      "actions": [
        {
          "tag": "button",
          "text": {
            "tag": "plain_text",
            "content": "View Report"
          },
          "url": "https://example.com/report",
          "type": "primary"
        }
      ]
    }
  ]
}
```

### Alert/Warning

```json
{
  "title": "⚠️ System Alert",
  "elements": [
    {
      "tag": "div",
      "text": {
        "tag": "lark_md",
        "content": "**Issue:** Disk space low\n**Server:** prod-01\n**Usage:** 95%"
      }
    },
    {
      "tag": "hr"
    },
    {
      "tag": "div",
      "text": {
        "tag": "lark_md",
        "content": "**Action Required:** Clean up old files"
      }
    }
  ]
}
```

## 🔧 Advanced Usage

### Batch Messages

```python
client = FeishuAPIClient()

users = ["ou_user1", "ou_user2", "ou_user3"]
for user_id in users:
    client.send_text("Broadcast message", receive_id=user_id)
```

### Scheduled Notifications

```python
import schedule
import time

client = FeishuAPIClient()

def daily_report():
    client.send_text("Daily report: All systems operational")

schedule.every().day.at("09:00").do(daily_report)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Error Handling

```python
from feishu_api import FeishuAPIClient, Exception

client = FeishuAPIClient()

try:
    client.send_text("Important message")
except Exception as e:
    print(f"Failed to send: {e}")
    # Implement fallback logic
```

## 🔐 Security

- **Never commit** `feishu-config.json` with real credentials
- Use environment variables for production:
  ```python
  import os
  config = {
      "app_id": os.getenv("FEISHU_APP_ID"),
      "app_secret": os.getenv("FEISHU_APP_SECRET")
  }
  ```
- Token cache file is automatically created/updated
- Tokens expire after 2700 seconds (45 minutes)

## 🐛 Troubleshooting

### Token Expired Error
```bash
python feishu-api.py refresh_token
```

### Invalid App Credentials
- Verify `app_id` and `app_secret` in Feishu Developer Console
- Ensure app has necessary permissions

### Message Not Delivered
- Check `receive_id` is correct
- Verify `receive_id_type` matches your ID type
- Ensure app has message sending permissions

### Rate Limiting
- API has rate limits (check Feishu docs)
- Script implements automatic retry with backoff

## 📊 Token Management

The token manager automatically:
1. Caches tokens to `feishu-token-cache.json`
2. Checks expiry before each API call
3. Refreshes 5 minutes before expiry (configurable)
4. Handles token expiration during API calls

**Cache File Format:**
```json
{
  "token": "t-xxxxx...",
  "expires_at": "2026-03-14T16:30:00",
  "app_id": "cli_xxxxx"
}
```

## 🎯 Use Cases

### 1. System Monitoring Alerts
```python
if cpu_usage > 90:
    client.send_poster("🚨 High CPU Alert", [
        {"tag": "div", "text": {"tag": "lark_md", "content": f"CPU: {cpu_usage}%"}}
    ])
```

### 2. Task Completion Notifications
```python
client.send_text(f"✅ Task '{task_name}' completed in {duration}s")
```

### 3. Daily Reports
```python
client.send_poster("📊 Daily Report", [
    {"tag": "div", "text": {"tag": "lark_md", "content": report_content}}
])
```

### 4. File Sharing
```python
client.send_file("daily_report.pdf")
```

### 5. Screenshot Sharing
```python
client.send_image("error_screenshot.png")
```

## 📝 API Reference

### FeishuAPIClient

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `send_text` | Send text message | `text`, `receive_id` | `Dict` |
| `send_poster` | Send card message | `title`, `content`, `receive_id` | `Dict` |
| `send_image` | Send image message | `image_path`, `receive_id` | `Dict` |
| `send_file` | Send file message | `file_path`, `receive_id` | `Dict` |
| `get_token_info` | Get token status | - | `Dict` |

### FeishuTokenManager

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `get_token` | Get valid token | - | `str` |
| `refresh` | Force token refresh | - | `str` |
| `load_from_cache` | Load from cache file | - | `bool` |
| `save_to_cache` | Save to cache file | `token`, `expires_in` | `void` |

## 🔗 Resources

- [Feishu Open Platform](https://open.feishu.cn/)
- [Feishu API Documentation](https://open.feishu.cn/document/ukTMukTMukTM/uEjNwUjLxYDM14SM2ATN)
- [Interactive Card Builder](https://open.feishu.cn/tool/cardbuilder)

## 📄 License

MIT License - OpenClaw Project

---

**Author:** OpenClaw Team  
**Version:** 1.0.0  
**Date:** 2026-03-14  
**Contact:** OpenClaw Workspace
