import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\OpenClaw\workspace\30-scripts-tools')
from stock_pro.rss_server import fetch_jin10

news = fetch_jin10()

print("=" * 70)
print("                    金十数据 RSS Feed")
print("=" * 70)
print()

for i, n in enumerate(news, 1):
    print(f"【{i}】 {n['title']}")
    if n.get('content'):
        print(f"    {n['content'][:100]}...")
    print(f"    🔗 {n['link']}")
    print()

print("=" * 70)
print(f"共 {len(news)} 条新闻")
print("=" * 70)
