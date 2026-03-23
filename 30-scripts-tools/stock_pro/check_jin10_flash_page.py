import urllib.request, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://flash.jin10.com/',
}

# Check the main flash.jin10.com page
url = "https://flash.jin10.com/"
print(f"=== Checking: {url} ===\n")

req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as r:
    content = r.read().decode('utf-8')

print(f"Page length: {len(content)} chars")

# Look for news list data embedded in page
print("\n=== Looking for embedded data ===")

# Check for __NUXT__ or window.__INITIAL_STATE__
nuxt = re.search(r'window\.__NUXT__\s*=\s*({.*?});', content, re.DOTALL)
if nuxt:
    print("Found __NUXT__ data")
    try:
        data = json.loads(nuxt.group(1))
        print(json.dumps(data, ensure_ascii=False)[:500])
    except:
        print(nuxt.group(1)[:500])

# Look for JSON data
json_pattern = r'"\d{17,20}"\s*:\s*{[^}]+}'
matches = re.findall(json_pattern, content)
print(f"\nJSON patterns: {len(matches)}")
for m in matches[:2]:
    print(f"  {m[:100]}")

# Find all detail IDs
ids = re.findall(r'/detail/(\d{17,20})', content)
print(f"\nDetail IDs found: {len(set(ids))}")
unique_ids = list(dict.fromkeys(ids))[:20]
for id in unique_ids:
    print(f"  {id}")

# Look for any text content
print("\n=== News content ===")
# Try to find substantial text blocks
text_blocks = re.findall(r'>([【\[][^\]]{5,20}[\]】][^\n<]{10,100})<', content)
for t in text_blocks[:10]:
    print(f"  {t.strip()}")
