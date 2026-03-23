import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\OpenClaw\workspace\30-scripts-tools')

from stock_pro.rss_server import fetch_jin10

news = fetch_jin10()

print("=" * 70)
print("                    金 十 全 部 新 闻")
print("=" * 70)
print()

for i, n in enumerate(news, 1):
    print(f"【{i}】 {n['title']}")
    if n.get('content'):
        print(f"    {n['content']}")
    print(f"    🔗 {n['link']}")
    print()

print("=" * 70)
print(f"共 {len(news)} 条")
print("=" * 70)
