import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://flash.jin10.com/',
}

# Check flash.jin10.com for RSS/API
print("=== Checking flash.jin10.com ===\n")

# Try RSS
rss_urls = [
    "https://flash.jin10.com/rss",
    "https://flash.jin10.com/feed",
    "https://flash.jin10.com/atom.xml",
    "https://flash.jin10.com/rss.xml",
    "https://flash.jin10.com/news.xml",
]

for rss_url in rss_urls:
    try:
        req = urllib.request.Request(rss_url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as r:
            data = r.read()
            if b'<rss' in data or b'<feed' in data or b'<xml' in data:
                print(f"✓ RSS found: {rss_url}")
                print(f"  {data[:300]}")
            else:
                print(f"✗ {rss_url} - Not RSS")
    except Exception as e:
        print(f"✗ {rss_url} - {e}")

# Try JSON API for flash news
print("\n=== Trying Flash News API ===\n")
api_urls = [
    "https://flash.jin10.com/api/news",
    "https://flash.jin10.com/api/flash",
    "https://flash.jin10.com/api/list",
    "https://flash.jin10.com/get_flash_news",
    "https://flash.jin10.com/news/list",
]

for api_url in api_urls:
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as r:
            data = r.read()
            if b'{' in data or b'[' in data:
                print(f"✓ JSON API: {api_url}")
                print(f"  {data[:200]}")
            else:
                print(f"✗ {api_url} - Not JSON")
    except Exception as e:
        print(f"✗ {api_url} - {e}")

# Check the page source for API patterns
print("\n=== Checking page source for API patterns ===\n")
url = "https://flash.jin10.com/"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as r:
    content = r.read().decode('utf-8')

# Find API patterns
patterns = [
    r'api["\']?\s*:\s*["\']([^"\']+)["\']',
    r'url\s*:\s*["\']([^"\']*news[^"\']*)["\']',
    r'fetch\(["\']([^"\']+)["\']',
    r'axios\.get\(["\']([^"\']+)["\']',
]
for pat in patterns:
    matches = re.findall(pat, content, re.IGNORECASE)
    if matches:
        print(f"Pattern '{pat[:30]}...': {matches[:3]}")

# Find data IDs
ids = re.findall(r'/detail/(\d+)', content)
if ids:
    print(f"\nDetail IDs: {ids[:10]}")
