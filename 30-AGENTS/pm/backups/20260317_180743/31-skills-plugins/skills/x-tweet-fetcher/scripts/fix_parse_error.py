import re

with open('fetch_tweet.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复 parse_timeline_snapshot 函数的错误处理
old_parse = '''    # ── Step 3: parse each primary tweet card ──────────────────────────────
    for pi_pos, pi in enumerate(primary_indices):
        if len(tweets) >= limit:
            break

        start_i = content_anchors[pi][0]'''

new_parse = '''    # ── Step 3: parse each primary tweet card ──────────────────────────────
    if not content_anchors:
        print("[x-tweet-fetcher] 警告：Nitter 页面结构无法解析，可能是速率限制或页面结构变化", file=sys.stderr)
        return tweets
    
    for pi_pos, pi in enumerate(primary_indices):
        if len(tweets) >= limit:
            break

        if pi >= len(content_anchors):
            print(f"[x-tweet-fetcher] 警告：锚点索引超出范围，停止解析", file=sys.stderr)
            break
            
        start_i = content_anchors[pi][0]'''

content = content.replace(old_parse, new_parse)

with open('fetch_tweet.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('错误处理已添加！')
