import os

drafts_dir = "D:/OpenClaw/workspace/50-novels/drafts"

for f in os.listdir(drafts_dir):
    if f.startswith('第 2') and '5000' not in f:
        path = os.path.join(drafts_dir, f)
        print(f"Reading: {f}")
        # Try different encodings
        for enc in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
            try:
                with open(path, 'r', encoding=enc) as file:
                    content = file.read()
                print(f"Encoding: {enc}")
                break
            except:
                continue
        print(f"Length: {len(content)} chars")
        print("\n--- Content (first 1000 chars) ---\n")
        print(content[:1000])
        break
