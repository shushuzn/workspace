import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\OpenClaw\workspace\30-scripts-tools')
from stock_pro.rss_server import fetch_jin10, Cache

# Get all news
cache = Cache()
cache.load()

jin10_news = fetch_jin10()
rss_news = cache.news

print("=" * 70)
print("                    全  部  新  闻")
print("=" * 70)
print()

# Jin10 first
print("【金十数据】 中文 · 金融 · 黄金外汇宏观")
print("-" * 70)
for i, n in enumerate(jin10_news, 1):
    print(f"  {i}. {n['title']}")
    if n.get('content') and len(n.get('content', '')) > 10:
        content = n['content'][:80].replace('\n', ' ')
        print(f"     {content}...")
print()

# RSS news
print("【RSS Feeds】 英文 · 金融科技商业")
print("-" * 70)
for i, n in enumerate(rss_news, 1):
    print(f"  {i}. {n['title']}")
    if n.get('content') and len(n.get('content', '')) > 10:
        content = n['content'][:60].replace('\n', ' ')
        print(f"     [{n.get('source', 'RSS')}] {content}...")
print()

print("=" * 70)
print(f"金十: {len(jin10_news)} 条 | RSS: {len(rss_news)} 条 | 共: {len(jin10_news) + len(rss_news)} 条")
print("=" * 70)
