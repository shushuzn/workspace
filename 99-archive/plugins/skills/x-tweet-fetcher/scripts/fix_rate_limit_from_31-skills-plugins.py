import re

with open('fetch_tweet.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 while 循环并添加初始延迟
old_while = '    while len(tweets) < limit and page <= MAX_PAGES:'
new_while = '''    # Rate limiting: initial delay before first request
    print(f"[x-tweet-fetcher] 等待 3 秒避免速率限制...", file=sys.stderr)
    time.sleep(3)
    
    consecutive_failures = 0
    MAX_CONSECUTIVE_FAILURES = 2
    
    while len(tweets) < limit and page <= MAX_PAGES:'''

content = content.replace(old_while, new_while)

# 修改错误处理逻辑
old_error = '''        if not snapshot:
            if page == 1:
                result["error"] = t("err_snapshot_failed")
                return result
            # Partial failure on later pages — stop gracefully
            print(f"[x-tweet-fetcher] 第 {page} 页快照失败，停止翻页", file=sys.stderr)
            break'''

new_error = '''        if not snapshot:
            consecutive_failures += 1
            if page == 1:
                result["error"] = t("err_snapshot_failed")
                return result
            
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                print(f"[x-tweet-fetcher] 连续 {consecutive_failures} 次失败，停止翻页", file=sys.stderr)
                break
            
            # Retry with longer delay
            print(f"[x-tweet-fetcher] 第 {page} 页快照失败，等待 5 秒后重试...", file=sys.stderr)
            time.sleep(5)
            continue
        
        consecutive_failures = 0  # Reset on success'''

content = content.replace(old_error, new_error)

# 修改翻页延迟
old_sleep = '            time.sleep(2)  # be polite between pages'
new_sleep = '''            # Increased delay between pages to avoid rate limiting
            delay = 4 + (page * 0.5)  # Progressive delay: 4.5s, 5s, 5.5s...
            print(f"[x-tweet-fetcher] 等待 {delay} 秒...", file=sys.stderr)
            time.sleep(delay)'''

content = content.replace(old_sleep, new_sleep)

with open('fetch_tweet.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修复完成！')
