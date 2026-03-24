"""
News Aggregator - 新闻聚合器 v2
使用 RSS/JSON API 获取多源新闻

使用方式:
    py 30-scripts-tools/news_aggregator.py [category] [category] ...

参数:
    - 不带参数: 获取所有类别
    - all: 获取所有类别
    - politics/时政: 时政新闻
    - finance/财经: 财经新闻
    - society/社会: 社会新闻
    - world/国际: 国际新闻
    - tech/科技: 科技新闻
    - sports/体育: 体育新闻
    - entertainment/娱乐: 娱乐新闻

示例:
    py 30-scripts-tools/news_aggregator.py
    py 30-scripts-tools/news_aggregator.py tech sports
"""

import sys
import urllib.request
import json
import xml.etree.ElementTree as ET
import subprocess
from pathlib import Path
from datetime import datetime

# RSS 源配置
RSS_SOURCES = {
    "politics": {
        "name": "时政",
        "url": "https://www.chinanews.com.cn/rss/politics.xml",
    },
    "finance": {
        "name": "财经",
        "url": "https://www.chinanews.com.cn/rss/business.xml",
    },
    "society": {
        "name": "社会",
        "url": "https://www.chinanews.com.cn/rss/society.xml",
    },
    "world": {
        "name": "国际",
        "url": "https://www.chinanews.com.cn/rss/world.xml",
    },
    "tech": {
        "name": "科技",
        "url": "https://www.chinanews.com.cn/rss/tech.xml",
    },
    "sports": {
        "name": "体育",
        "url": "https://www.chinanews.com.cn/rss/sports.xml",
    },
    "entertainment": {
        "name": "娱乐",
        "url": "https://www.chinanews.com.cn/rss/entertainment.xml",
    },
}

# 备用 RSS 源
BACKUP_SOURCES = {
    "tech": [
        "https://www.36kr.com/feed",
        "https://feeds.feedburner.com/techcrunch/chinese",
    ],
    "finance": [],  # 使用 JSON API
    "world": [
        "https://www.dw.com/zh/rss/chinese_news",
        "https://www.bbc.com/zhongwen/simp/rss.xml",
    ],
    "entertainment": [
        "https://www.36kr.com/feed",  # 科技作为备用
    ],
}

# JSON API 源 (新浪)
JSON_SOURCES = {
    "finance": "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517&k=&num=10&page=1",
    "world": "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=1686&k=&num=10&page=1",
}

# 中文类别名到英文key
NAME_TO_KEY = {v["name"]: k for k, v in RSS_SOURCES.items()}


def parse_categories(args):
    """解析命令行参数"""
    if not args or args[0].lower() == "all":
        return list(RSS_SOURCES.keys())

    result = []
    for arg in args:
        if arg in NAME_TO_KEY:
            result.append(NAME_TO_KEY[arg])
        elif arg in RSS_SOURCES:
            result.append(arg)
        elif arg.lower() == "all":
            result.extend(list(RSS_SOURCES.keys()))

    return list(set(result)) if result else list(RSS_SOURCES.keys())


def fetch_rss(source_key, source_info):
    """通过 RSS 或 JSON API 获取新闻"""
    items = []

    # 尝试 JSON API (新浪)
    if source_key in JSON_SOURCES:
        try:
            items = fetch_json_api(JSON_SOURCES[source_key])
            if items:
                return items
        except Exception as e:
            print(f"  [!] JSON API failed: {str(e)[:40]}")

    # 尝试主 RSS
    try:
        items = parse_rss(source_info["url"])
        if items:
            return items
    except Exception as e:
        print(f"  [!] Main RSS failed: {str(e)[:40]}")

    # 尝试备用源
    if source_key in BACKUP_SOURCES:
        for backup_url in BACKUP_SOURCES[source_key]:
            try:
                items = parse_rss(backup_url)
                if items:
                    return items
            except:
                continue

    return items


def fetch_json_api(url):
    """获取新浪 JSON API"""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://news.sina.com.cn/",
        },
    )

    with urllib.request.urlopen(req, timeout=15) as response:
        content = response.read()

    data = json.loads(content)

    items = []
    if "result" in data and "data" in data["result"]:
        for item in data["result"]["data"]:
            title = item.get("title", "")
            if title:
                items.append({"title": title, "link": item.get("url", "")})

    return items[:10]


def parse_rss(url):
    """解析 RSS XML"""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
    )

    with urllib.request.urlopen(req, timeout=15) as response:
        content = response.read()
        # 尝试不同编码
        try:
            xml_text = content.decode("utf-8")
        except:
            try:
                xml_text = content.decode("gbk")
            except:
                xml_text = content.decode("latin-1")

    # 解析 XML
    root = ET.fromstring(xml_text)

    items = []

    # 处理 RSS 2.0
    if root.tag == "rss":
        channel = root.find("channel")
        if channel is not None:
            for item in channel.findall("item"):
                title = item.find("title")
                link = item.find("link")
                desc = item.find("description")

                item_text = ""
                if title is not None and title.text:
                    item_text = title.text.strip()
                elif desc is not None and desc.text:
                    # 去掉 HTML 标签
                    import re

                    item_text = re.sub(r"<[^>]+>", "", desc.text).strip()[:100]

                item_link = link.text if link is not None and link.text else ""

                if item_text:
                    items.append({"title": item_text, "link": item_link})

    # 处理 Atom
    elif root.tag.endswith("feed"):
        for entry in root.findall("entry"):
            title = entry.find("title")
            link_elem = entry.find("link")

            item_text = title.text if title is not None and title.text else ""
            item_link = ""
            if link_elem is not None:
                item_link = link_elem.get("href", "")

            if item_text:
                items.append({"title": item_text.strip(), "link": item_link})

    return items[:10]  # 限制数量


def main():
    # Critic v5.0 integration
    critic_result = subprocess.run(
        [sys.executable, "critic_v5_review.py", "--scenario", "tool_optimize"],
        cwd=str(Path(__file__).parent),
        timeout=300,
    )
    if critic_result.returncode != 0:
        print("[ERROR] Critic Review Failed. Aborting.")
        return

    print("[OK] Critic Review Passed")

    categories = parse_categories(sys.argv[1:])

    print(f"\n[NEWS] News Aggregator - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    results = []

    for key in categories:
        if key not in RSS_SOURCES:
            continue

        source = RSS_SOURCES[key]
        print(f"\n[*] Fetching: {source['name']}...")

        items = fetch_rss(key, source)

        results.append({"key": key, "name": source["name"], "items": items})

        if items:
            print(f"  [+] Got {len(items)} items")
        else:
            print(f"  [-] No items")

    # 输出结果
    print("\n" + "=" * 60)
    print("[NEWS] News Summary\n")

    for r in results:
        print(f"[{r['name']}]")
        if r["items"]:
            for i, item in enumerate(r["items"], 1):
                title = item["title"][:60] + ("..." if len(item["title"]) > 60 else "")
                print(f"  {i}. {title}")
        else:
            print("  (no data)")
        print()

    total_items = sum(len(r["items"]) for r in results)
    print(f"[OK] Done, {len(results)} categories, {total_items} items total")


if __name__ == "__main__":
    main()
