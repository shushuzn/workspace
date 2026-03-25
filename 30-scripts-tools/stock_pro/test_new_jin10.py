import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\OpenClaw\workspace\30-scripts-tools')
from stock_pro.rss_server import fetch_jin10

news = fetch_jin10()
print("=" * 70)
print("                    金 十 快 讯（免费实时）")
print("=" * 70)
print()

for i, n in enumerate(news, 1):
    print(f"【{i}】 {n['title']}")
    print(f"    🔗 {n['link']}")
    print()

print("=" * 70)
print(f"共 {len(news)} 条快讯")
print("=" * 70)
