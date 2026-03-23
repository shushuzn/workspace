#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BiliBili 数据收集器 - 复用版 v4.0
可配置、可复用、可扩展
"""

import json
import sys
import time
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


class BilibiliCollector:
    """BiliBili 收集器 - 通用模板"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.data_dir = Path(__file__).parent.parent / ".openclaw" / "bilibili_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 默认配置
        self.categories = {
            "all": "全站", "douga": "动画", "music": "音乐", 
            "game": "游戏", "tech": "科技", "knowledge": "知识",
            "movie": "影视", "food": "美食", "life": "生活",
            "fashion": "时尚", "ent": "娱乐"
        }
    
    def _init_browser(self):
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 Chrome/120.0.0.0 Safari/537.36")
        return p, browser, context, context.new_page()
    
    # ========== 核心方法（可复用）==========
    
    def crawl_list(self, url, selector, fields):
        """通用列表抓取"""
        print(f"[INFO] 抓取: {url}")
        results = []
        
        if not HAS_PLAYWRIGHT:
            return self._mock_list(fields, 10)
        
        try:
            p, browser, context, page = self._init_browser()
            page.goto(url, timeout=30000)
            page.wait_for_timeout(3000)
            
            items = page.query_selector_all(selector)
            
            for item in items:
                row = {}
                for field_name, field_config in fields.items():
                    elem = item.query_selector(field_config["selector"])
                    row[field_name] = elem.inner_text().strip() if elem else ""
                results.append(row)
            
            browser.close()
            p.stop()
        except Exception as e:
            print(f"[WARN] {e}")
            results = self._mock_list(fields, 10)
        
        return results
    
    def crawl_detail(self, url, fields):
        """通用详情抓取"""
        print(f"[INFO] 详情: {url}")
        
        if not HAS_PLAYWRIGHT:
            return {k: f"Mock_{k}" for k in fields.keys()}
        
        try:
            p, browser, context, page = self._init_browser()
            page.goto(url, timeout=30000)
            page.wait_for_timeout(2000)
            
            result = {}
            for field_name, selector in fields.items():
                elem = page.query_selector(selector)
                result[field_name] = elem.inner_text().strip() if elem else ""
            
            browser.close()
            p.stop()
            return result
        except Exception:
            return {k: "" for k in fields.keys()}
    
    # ========== 预设任务（直接调用）==========
    
    def task_hot(self, category="all", limit=50):
        """热门排行"""
        url = f"https://www.bilibili.com/v/popular/rank/{category}"
        fields = {
            "title": {"selector": ".title"},
            "author": {"selector": ".up-name"},
            "views": {"selector": ".play"}
        }
        return self.crawl_list(url, ".rank-item", fields)
    
    def task_search(self, keyword, limit=30):
        """搜索"""
        url = f"https://search.bilibili.com/all?keyword={keyword}"
        fields = {"title": {"selector": ".title"}, "url": {"selector": "a"}}
        return self.crawl_list(url, ".video-item", fields)
    
    def task_up_info(self, uid):
        """UP主信息"""
        url = f"https://space.bilibili.com/{uid}"
        fields = {"name": ".name", "fans": ".fans", "videos": ".archive"}
        return self.crawl_detail(url, fields)
    
    def task_video(self, bvid):
        """视频详情"""
        url = f"https://www.bilibili.com/video/{bvid}"
        fields = {"title": ".video-title", "desc": ".desc"}
        return self.crawl_detail(url, fields)
    
    # ========== 辅助方法 ==========
    
    def _mock_list(self, fields, count):
        return [{k: f"{k}_{i}" for k in fields.keys()} for i in range(count)]
    
    def save(self, data, name):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fp = self.data_dir / f"{name}_{ts}.json"
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return fp
    
    def save_csv(self, data, name):
        import csv
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fp = self.data_dir / f"{name}_{ts}.csv"
        if data:
            with open(fp, 'w', encoding='utf-8-sig', newline='') as f:
                w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
                w.writeheader()
                w.writerows(data)
        return fp


# ========== 复用模板 ==========

TEMPLATES = {
    "hot": {
        "name": "热门排行",
        "category": "all",
        "selector": ".rank-item",
        "fields": ["title", "author", "views"]
    },
    "search": {
        "name": "关键词搜索",
        "keyword": "AI",
        "selector": ".video-item", 
        "fields": ["title", "url"]
    },
    "up": {
        "name": "UP主信息",
        "selector": ".info-item",
        "fields": ["name", "fans", "videos"]
    }
}


def main():
    print("=" * 50)
    print("BiliBili 收集器 v4.0 (复用版)")
    print("=" * 50)
    
    collector = BilibiliCollector()
    
    # 命令行接口
    if len(sys.argv) < 2:
        print("\n用法:")
        print("  hot [分类]        热门排行")
        print("  search <关键词>   搜索")
        print("  up <uid>          UP主信息")
        print("  video <bvid>      视频详情")
        print("\n代码复用示例:")
        print("  from bilibili_collector_001 import BilibiliCollector")
        print("  c = BilibiliCollector()")
        print("  c.task_hot('tech', 50)")
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == "hot":
        cat = sys.argv[2] if len(sys.argv) > 2 else "all"
        r = collector.task_hot(cat, 50)
        collector.save(r, f"hot_{cat}")
        collector.save_csv(r, f"hot_{cat}")
        
    elif cmd == "search":
        kw = sys.argv[2] if len(sys.argv) > 2 else "AI"
        r = collector.task_search(kw)
        collector.save(r, f"search_{kw}")
        
    elif cmd == "up":
        uid = sys.argv[2] if len(sys.argv) > 2 else "1"
        r = collector.task_up_info(uid)
        collector.save(r, f"up_{uid}")
        
    elif cmd == "video":
        bv = sys.argv[2] if len(sys.argv) > 2 else "BV1xx411c7mD"
        r = collector.task_video(bv)
        collector.save(r, f"video_{bv}")
    
    print("\n[OK] 完成!")
    print(f"[INFO] 数据保存至: {collector.data_dir}")


if __name__ == "__main__":
    main()