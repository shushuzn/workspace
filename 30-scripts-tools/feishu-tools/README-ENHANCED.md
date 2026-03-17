# Feishu API Tools - Enhanced Features v2.0

🚀 Complete Feishu messaging toolkit with advanced features.

## 🆕 New Features (v2.0)

### 1. Image Compression 🖼️
- Automatic image compression before sending
- Configurable quality (1-100) and max width
- Uses Pillow library
- Reduces bandwidth by 50-80%

### 2. Message Queue 📬
- Queue messages for batch sending
- Priority-based ordering
- Automatic retry on failure (max 3 attempts)
- Persistent queue (JSON file)

### 3. Daily Report Automation 📊
- Automated daily reports at 9:00 AM
- Customizable report templates
- Cron job integration ready
- Test mode available

### 4. Statistics Tracking 📈
- Track success rate
- Monitor average latency
- Per-message-type statistics
- Hourly breakdown

### 5. @User Mentions 📣
- Mention users in messages
- Support multiple mentions
- Works with text and card messages
- Automatic mention tag generation

## 📦 Installation

```bash
# Install dependencies
pip install requests pillow

# Verify installation
python feishu_api_enhanced.py --help
```

## ⚙️ Configuration

Edit `feishu-config.json`:

```json
{
  "app_id": "your_app_id",
  "app_secret": "your_app_secret",
  "receive_id_type": "open_id",
  "default_receive_id": "your_user_id",
  "token_cache_file": "feishu-token-cache.json",
  "token_refresh_before_expiry": 300
}
```

## 💻 Usage Examples

### Send Text with @Mention

```bash
# Single mention
python feishu_api_enhanced.py send_text "Hello @user" --mention ou_xxxxx

# Multiple mentions
python feishu_api_enhanced.py send_text "Team meeting" --mention ou_111,ou_222,ou_333
```

### Send Compressed Image

```bash
# Auto-compress with defaults (quality=80, max_width=1200)
python feishu_api_enhanced.py send_image photo.png --compress

# Custom quality and size
python feishu_api_enhanced.py send_image photo.png --compress --quality 90 --max-width 1920
```

### Message Queue

```bash
# Add messages to queue
python feishu_api_enhanced.py queue_add "Message 1" --type text --priority 5
python feishu_api_enhanced.py queue_add "Message 2" --type text --priority 3
python feishu_api_enhanced.py queue_add "Urgent!" --type text --priority 10

# List queued messages
python feishu_api_enhanced.py queue_list

# Send all queued messages
python feishu_api_enhanced.py queue_send

# Clear queue
python feishu_api_enhanced.py queue_clear
```

### Statistics

```bash
# View statistics
python feishu_api_enhanced.py stats

# Reset statistics
python feishu_api_enhanced.py stats_reset
```

### Daily Report

```bash
# Test report (preview)
python daily-report.py --test

# Send daily report
python daily-report.py

# Schedule with cron (Windows Task Scheduler)
# See: cron-daily-report.json for configuration
```

## 🔧 Advanced Usage

### Python API

```python
from feishu_api_enhanced import FeishuAPIClient

client = FeishuAPIClient()

# Send with mention
client.send_text(
    "Meeting in 5 minutes!",
    mention_users=["ou_user1", "ou_user2"]
)

# Send compressed image
client.send_image(
    "screenshot.png",
    compress=True,
    quality=85,
    max_width=1600
)

# Add to queue
client.queue.add(
    msg_type="text",
    content="Batch message",
    receive_id="ou_xxxxx",
    priority=5
)

# Send queued messages
results = client.send_queued_messages()
print(f"Sent: {results['sent']}, Failed: {results['failed']}")

# Get statistics
stats = client.get_stats()
print(f"Success rate: {stats['success_rate']}")
print(f"Avg latency: {stats['avg_latency_ms']}")
```

### Custom Daily Report

```python
# Edit daily-report.py
REPORT_CONFIG = {
    "title": "[Daily Report] Your Project",
    "receive_id": "ou_xxxxx",
    "mention_users": ["ou_manager"],  # @mention manager
    "sections": [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**Your custom content**"
            }
        }
    ]
}
```

### Queue with Retry Logic

```python
client = FeishuAPIClient()

# High priority message
client.queue.add(
    msg_type="text",
    content="Critical alert!",
    receive_id="ou_xxxxx",
    mention_users=["ou_admin"],
    priority=10  # Higher priority = sent first
)

# Normal priority
client.queue.add(
    msg_type="text",
    content="Regular update",
    priority=0
)

# Send queue (automatically retries failed messages up to 3 times)
client.send_queued_messages()
```

## 📊 Statistics Format

```
Message Statistics:
  Total Messages: 150
  Success Rate: 98.67%
  Avg Latency: 856.32ms

By Type:
  text: 100/100 (100.0%)
  card: 30/30 (100.0%)
  image: 15/15 (100.0%)
  file: 5/5 (100.0%)

Last Reset: 2026-03-14T15:50:06
```

## 🕐 Cron Integration

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9:00 AM
4. Action: Start a program
   - Program: `python`
   - Arguments: `daily-report.py`
   - Start in: `D:\OpenClaw\workspace\30-scripts-tools\feishu-tools`

### Linux Cron

```bash
# Edit crontab
crontab -e

# Add daily report at 9 AM
0 9 * * * cd /path/to/feishu-tools && python daily-report.py
```

## 🐛 Troubleshooting

### Image Upload Fails
- Check file format (JPEG/PNG supported)
- Verify file size (<10MB recommended)
- Ensure Pillow is installed: `pip install pillow`

### Queue Messages Not Sending
- Check queue file: `feishu-message-queue.json`
- Verify token is valid: `python feishu_api_enhanced.py token_info`
- Check error logs in console output

### Statistics Not Tracking
- Verify stats file: `feishu-stats.json`
- Check file permissions
- Reset stats: `python feishu_api_enhanced.py stats_reset`

### @Mention Not Working
- Ensure user IDs are correct (open_id format)
- Check mention_users parameter format: `--mention user1,user2`
- Verify app has mention permissions

## 📈 Performance Tips

1. **Use Queue for Batch Messages**
   - More efficient than individual sends
   - Automatic retry on failure
   - Priority-based ordering

2. **Compress Images**
   - Reduces bandwidth by 50-80%
   - Faster upload times
   - Default settings work well for most cases

3. **Monitor Statistics**
   - Track success rate trends
   - Identify slow endpoints
   - Optimize based on data

4. **Cache Token**
   - Automatic token caching enabled
   - Refreshes 5 minutes before expiry
   - Reduces API calls

## 📝 File Structure

```
feishu-tools/
├── feishu_api_enhanced.py    # Main API client (v2.0)
├── feishu_api.py             # Original API client (v1.0)
├── feishu-config.json        # Configuration
├── daily-report.py           # Daily report automation
├── cron-daily-report.json    # Cron job config
├── card-template.json        # Card message template
├── examples.py               # Usage examples
├── test_feishu.py            # Test suite
├── feishu-token-cache.json   # Token cache (auto-generated)
├── feishu-message-queue.json # Message queue (auto-generated)
├── feishu-stats.json         # Statistics (auto-generated)
├── README.md                 # This file
├── QUICKSTART.md             # Quick start guide
└── .gitignore                # Git ignore rules
```

## 🔗 Resources

- [Feishu Open Platform](https://open.feishu.cn/)
- [Feishu API Docs](https://open.feishu.cn/document/ukTMukTMukTM/uEjNwUjLxYDM14SM2ATN)
- [Interactive Card Builder](https://open.feishu.cn/tool/cardbuilder)
- [Pillow Documentation](https://pillow.readthedocs.io/)

## 📄 License

MIT License - OpenClaw Project

---

**Author:** OpenClaw Team  
**Version:** 2.0.0 Enhanced  
**Date:** 2026-03-14  
**Contact:** OpenClaw Workspace
