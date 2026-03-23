import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
}

# Check news.jin10.com
print("=== news.jin10.com ===")
url = "https://news.jin10.com/"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as r:
    content = r.read().decode('utf-8')

# Find news links
links = re.findall(r'href="(https?://[^"]*jin10[^"]*)"', content)
print(f"Found {len(links)} links")
for link in links[:10]:
    print(f"  {link}")

# Find any RSS
rss = re.findall(r'<link[^>]+type="application/rss\+xml"[^>]*>', content)
if rss:
    print(f"\nRSS feeds found:")
    for r in rss:
        print(f"  {r}")

# Check for any data or text content
text_blocks = re.findall(r'>([^\n<>]{30,150})<', content)
print(f"\nText blocks: {len(text_blocks)}")
for t in text_blocks[:5]:
    t = t.strip()
    if any('\u4e00' <= c <= '\u9fff' for c in t):
        print(f"  {t[:80]}")

print("\n\n=== flash.jin10.com ===")
url2 = "https://flash.jin10.com/"
req2 = urllib.request.Request(url2, headers=headers)
with urllib.request.urlopen(req2, timeout=10) as r:
    content2 = r.read().decode('utf-8')

links2 = re.findall(r'href="(https?://[^"]+)"', content2)
print(f"Found {len(links2)} links")
for link in links2[:10]:
    print(f"  {link}")
