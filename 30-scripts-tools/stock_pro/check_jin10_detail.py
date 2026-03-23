import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

# Check a flash news detail page
detail_id = "20260322183626806800"
url = f"https://flash.jin10.com/detail/{detail_id}"
print(f"=== Checking: {url} ===\n")

req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as r:
    content = r.read().decode('utf-8')

print(f"Page length: {len(content)} chars")

# Find title
title_match = re.search(r'<title>([^<]+)</title>', content)
if title_match:
    print(f"Title: {title_match.group(1)}")

# Find article content
content_match = re.search(r'<article[^>]*>(.*?)</article>', content, re.DOTALL)
if content_match:
    text = re.sub(r'<[^>]+>', '', content_match.group(1))
    text = re.sub(r'\s+', ' ', text).strip()
    print(f"\nArticle content:\n{text[:500]}")

# Find any text blocks
print("\n\n=== Looking for content ===")
texts = re.findall(r'>([^\n<]{50,500})<', content)
cn_texts = [t.strip() for t in texts if any('\u4e00' <= c <= '\u9fff' for c in t)]
for t in cn_texts[:5]:
    print(f"  - {t[:100]}")

# Check if VIP indicator exists
if 'vip' in content.lower() or '会员' in content:
    print("\n⚠️ Page may have VIP content")
else:
    print("\n✓ Appears to be free content")
