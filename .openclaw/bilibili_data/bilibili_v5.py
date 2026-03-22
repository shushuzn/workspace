#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BiliBili 收集器 v5.0 - 迭代版
修复问题：
1. 添加更多数据字段
2. 添加重试机制
3. 添加日志
4. 添加配置管理
"""

import json
import sys
import time
import logging
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


# ========== 配置管理 ==========
class Config:
    """配置管理"""
    def __init__(self):
        self.data_dir = Path(r"D:\OpenClaw\workspace\.openclaw\bilibili_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 默认配置
        self.retry = 3
        self.timeout = 30
        self.delay = 1
        
        # 日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(self.data_dir / "bilibili.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 分类
        self.categories = {
            "all": "全站", "tech": "科技", "game": "游戏",
            "music": "音乐", "knowledge": "知识", "food": "美食"
        }
    
    def save(self, data, name):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fp = self.data_dir / f"{name}_{ts}.json"
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return fp


# ========== 收集器 ==========
class BilibiliCollector:
    """BiliBili 收集器 v5.0"""
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.logger = self.config.logger
        
    def _init_browser(self):
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        return p, browser, context, context.new_page()
    
    def _retry(self, func, *args, **kwargs):
        """重试装饰器"""
        for i in range(self.config.retry):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.logger.warning(f"Retry {i+1}/{self.config.retry}: {e}")
                time.sleep(self.config.delay)
        return []
    
    # ========== 热门排行（增强版）==========
    def get_hot(self, category="all", limit=100):
        """获取热门 - 增强字段"""
        self.logger.info(f"获取热门: {category}")
        results = []
        
        def _crawl():
            p, browser, context, page = self._init_browser()
            url = f"https://www.bilibili.com/v/popular/rank/{category}"
            page.goto(url, timeout=self.config.timeout * 1000)
            page.wait_for_timeout(3000)
            
            items = page.query_selector_all('.rank-item')
            self.logger.info(f"找到 {len(items)} 条")
            
            for i, item in enumerate(items[:limit]):
                try:
                    # 增强字段
                    title = item.query_selector('.title')
                    up = item.query_selector('.up-name')
                    play = item.query_selector('.play')
                    like = item.query_selector('.like')
                    coins = item.query_selector('.coin')
                    
                    # 链接
                    link = item.query_selector('a')
                    href = link.get_attribute('href') if link else ""
                    
                    results.append({
                        "rank": i + 1,
                        "title": title.inner_text().strip() if title else "",
                        "author": up.inner_text().strip() if up else "",
                        "views": play.inner_text().strip() if play else "",
                        "likes": like.inner_text().strip() if like else "",
                        "coins": coins.inner_text().strip() if coins else "",
                        "url": f"https:{href}" if href.startswith("//") else href,
                        "category": self.config.categories.get(category, category),
                        "crawled_at": datetime.now().isoformat()
                    })
                except Exception as e:
                    self.logger.warning(f"解析失败: {e}")
            
            browser.close()
            p.stop()
            return results
        
        return self._retry(_crawl)
    
    # ========== 搜索（增强版）==========
    def search(self, keyword, limit=50):
        """搜索 - 增强字段"""
        self.logger.info(f"搜索: {keyword}")
        results = []
        
        def _crawl():
            p, browser, context, page = self._init_browser()
            page.goto(f"https://search.bilibili.com/all?keyword={keyword}", timeout=self.config.timeout * 1000)
            page.wait_for_timeout(3000)
            
            items = page.query_selector_all('.video-item')
            
            for i, item in enumerate(items[:limit]):
                try:
                    title = item.query_selector('.title')
                    link = item.query_selector('a')
                    meta = item.query_selector_all('.data-box')
                    duration = item.query_selector('.duration')
                    
                    results.append({
                        "index": i + 1,
                        "title": title.inner_text().strip() if title else "",
                        "url": link.get_attribute('href') if link else "",
                        "views": meta[0].inner_text().strip() if len(meta) > 0 else "",
                        "likes": meta[1].inner_text().strip() if len(meta) > 1 else "",
                        "duration": duration.inner_text().strip() if duration else "",
                        "keyword": keyword,
                        "crawled_at": datetime.now().isoformat()
                    })
                except: pass
            
            browser.close()
            p.stop()
            return results
        
        return self._retry(_crawl)
    
    # ========== UP主（增强版）==========
    def get_up(self, uid):
        """UP主信息 - 增强字段"""
        self.logger.info(f"UP主: {uid}")
        
        def _crawl():
            p, browser, context, page = self._init_browser()
            page.goto(f"https://space.bilibili.com/{uid}", timeout=self.config.timeout * 1000)
            page.wait_for_timeout(3000)
            
            name = page.query_selector('.name')
            fans = page.query_selector('.fans')
            likes = page.query_selector('.likes')
            videos = page.query_selector('.archive')
            sign = page.query_selector('.sign')
            
            info = {
                "uid": uid,
                "name": name.inner_text().strip() if name else "",
                "fans": fans.inner_text().strip() if fans else "",
                "likes": likes.inner_text().strip() if likes else "",
                "videos": videos.inner_text().strip() if videos else "",
                "sign": sign.inner_text().strip() if sign else "",
                "url": f"https://space.bilibili.com/{uid}",
                "crawled_at": datetime.now().isoformat()
            }
            
            browser.close()
            p.stop()
            return info
        
        return self._retry(_crawl)
    
    # ========== 视频详情（增强版）==========
    def get_video(self, bvid):
        """视频详情 - 增强字段"""
        self.logger.info(f"视频: {bvid}")
        
        def _crawl():
            p, browser, context, page = self._init_browser()
            page.goto(f"https://www.bilibili.com/video/{bvid}", timeout=self.config.timeout * 1000)
            page.wait_for_timeout(3000)
            
            title = page.query_selector('.video-title')
            desc = page.query_selector('.desc')
            view_count = page.query_selector('.view-count')
            like_count = page.query_selector('.like-count')
            
            info = {
                "bvid": bvid,
                "title": title.inner_text().strip() if title else "",
                "description": desc.inner_text().strip() if desc else "",
                "views": view_count.inner_text().strip() if view_count else "",
                "likes": like_count.inner_text().strip() if like_count else "",
                "url": f"https://www.bilibili.com/video/{bvid}",
                "crawled_at": datetime.now().isoformat()
            }
            
            browser.close()
            p.stop()
            return info
        
        return self._retry(_crawl)


# ========== 主函数 ==========
def main():
    print("=" * 60)
    print("BiliBili 收集器 v5.0 (迭代版)")
    print("=" * 60)
    
    config = Config()
    collector = BilibiliCollector(config)
    
    if len(sys.argv) < 2:
        print("\n功能:")
        print("  hot [分类]        热门排行")
        print("  search <关键词>   搜索")
        print("  up <uid>          UP主")
        print("  video <bvid>      视频")
        print("\n增强功能:")
        print("  - 重试机制 (3次)")
        print("  - 日志记录")
        print("  - 增强字段")
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == "hot":
        cat = sys.argv[2] if len(sys.argv) > 2 else "all"
        r = collector.get_hot(cat, 100)
        config.save(r, f"hot_{cat}")
        print(f"[OK] 获取 {len(r)} 条热门")
        
    elif cmd == "search":
        kw = sys.argv[2] if len(sys.argv) > 2 else "AI"
        r = collector.search(kw, 50)
        config.save(r, f"search_{kw}")
        print(f"[OK] 找到 {len(r)} 条")
        
    elif cmd == "up":
        uid = sys.argv[2] if len(sys.argv) > 2 else "1"
        r = collector.get_up(uid)
        config.save(r, f"up_{uid}")
        print(f"[OK] UP主: {r.get('name', 'N/A')}")
        
    elif cmd == "video":
        bv = sys.argv[2] if len(sys.argv) > 2 else "BV1xx411c7mD"
        r = collector.get_video(bv)
        config.save(r, f"video_{bv}")
        print(f"[OK] {r.get('title', 'N/A')}")
    
    print("\n[OK] 完成!")
    print(f"[INFO] 日志: {config.data_dir / 'bilibili.log'}")


if __name__ == "__main__":
    main()