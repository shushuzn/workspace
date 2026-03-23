import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')

# Try different API approaches
test_urls = [
    # Jin10 public APIs
    "https://xnews.jin10.com/get_flash_news?channel_id=-1",
    "https://xnews.jin10.com/get_flash_news?channel_id=0",
    "https://xnews.jin10.com/get_flash_news?type=0",
    # Alternative
    "https://xnews.jin10.com/index/get_flash_news",
    "https://xnews.jin10.com/news/get_flash_news",
    # Try with different headers
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://xnews.jin10.com/',
    'Origin': 'https://xnews.jin10.com',
    'X-Requested-With': 'XMLHttpRequest',
}

for url in test_urls:
    print(f"\nTesting: {url}")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as r:
            data = r.read()
            if b'<html' not in data[:100]:
                print(f"  ✓ JSON response: {len(data)} bytes")
                print(f"  {data[:200]}")
            else:
                print(f"  ✗ HTML response (not JSON)")
    except Exception as e:
        print(f"  ✗ {type(e).__name__}: {e}")

# Check if there's a different subdomain
print("\n\n=== Trying alternative subdomains ===")
subs = [
    "https://news.jin10.com/",
    "https://flash.jin10.com/",
    "https://api.jin10.com/",
]
for sub in subs:
    try:
        req = urllib.request.Request(sub, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as r:
            print(f"✓ {sub} - {r.status}")
    except Exception as e:
        print(f"✗ {sub} - {e}")

# Check current cached data
print("\n\n=== Current cached Jin10 data ===")
import json, os
cache_file = r"D:\OpenClaw\workspace\30-scripts-tools\stock_pro\data_jin10_news.json"
if os.path.exists(cache_file):
    with open(cache_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Cached items: {len(data)}")
    for item in data[:3]:
        print(f"  - {item.get('title', 'N/A')[:60]}")
else:
    print("No cache file found")
