# Quick Start - Feishu API Tools

🚀 Get started in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install requests
```

## Step 2: Configure Credentials

Edit `feishu-config.json`:

```json
{
  "app_id": "your_app_id",
  "app_secret": "your_app_secret",
  "receive_id_type": "open_id",
  "default_receive_id": "your_user_id"
}
```

**Get credentials from:**
1. Go to [Feishu Developer Console](https://open.feishu.cn/app)
2. Create or select your app
3. Find App ID and App Secret in "Credentials" section

## Step 3: Test Installation

```bash
# Get token
python feishu_api.py refresh_token

# Check token status
python feishu_api.py token_info

# Send test message
python feishu_api.py send_text "Hello from Feishu API Tools!"
```

## Step 4: Common Commands

```bash
# Send text message
python feishu_api.py send_text "Your message"

# Send to specific user
python feishu_api.py send_text "Private message" ou_xxxxx

# Send card message
python feishu_api.py send_card card-template.json

# Send image
python feishu_api.py send_image screenshot.png

# Send file
python feishu_api.py send_file document.pdf

# Run all tests
python test_feishu.py

# Run examples
python examples.py all
```

## Step 5: Python API Usage

```python
from feishu_api import FeishuAPIClient

# Initialize
client = FeishuAPIClient()

# Send message
client.send_text("Hello World!")

# Send card
client.send_poster("Title", [
    {"tag": "div", "text": {"tag": "lark_md", "content": "Content"}}
])
```

## Troubleshooting

### Token Expired
```bash
python feishu_api.py refresh_token
```

### Invalid Credentials
- Check `app_id` and `app_secret` in `feishu-config.json`
- Verify app permissions in Feishu Developer Console

### Message Not Sent
- Ensure `default_receive_id` is set in config
- Check network connection
- Verify app has message sending permissions

## Next Steps

- Read full documentation: `README.md`
- Check examples: `examples.py`
- Run tests: `test_feishu.py`
- Customize card templates: `card-template.json`

---

**Need Help?** Check `README.md` for detailed documentation.
