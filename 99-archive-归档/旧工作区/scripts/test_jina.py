import feedparser
import requests
import re

# 测试 Jina AI 是否能正确解析 Medium RSS
medium_feeds = [
    'https://medium.com/feed/towards-data-science',
    'https://medium.com/feed/better-programming',
]

for feed_url in medium_feeds:
    # 方法 1: 直接解析（被 Cloudflare 阻挡）
    feed_direct = feedparser.parse(feed_url)
    
    # 方法 2: Jina AI 代理
    jina_url = 'https://r.jina.ai/' + feed_url.replace('https://', '')
    jina_content = requests.get(jina_url, timeout=30).text
    
    # Jina 返回的是 Markdown，需要提取文章链接
    medium_url_re = re.compile(r"https?://medium\.com/[^\s\?\"]+", re.I)
    matches = medium_url_re.findall(jina_content)
    
    print(f'{feed_url.split("/")[3]}:')
    print(f'  Direct RSS: {len(feed_direct.entries)} articles')
    print(f'  Jina Markdown: {len(matches)} Medium URLs found')
    if matches:
        print(f'  Sample: {matches[0][:80]}')
    print()
