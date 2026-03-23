#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medium Watcher — Medium 文章监听器

功能:
- 按作者/标签/出版物订阅
- RSS 获取最新文章
- 内容提取
- 质量评分
- 自动归档

使用:
    python medium-watcher.py --tags ai,llm --output Medium/Raw/
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
import feedparser
import requests
from bs4 import BeautifulSoup

# 修复 Windows 中文输出编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    # 设置控制台编码为 UTF-8
    os.system('chcp 65001 >nul 2>&1')


# 默认配置
DEFAULT_TAGS = ["artificial-intelligence", "machine-learning", "llm"]
DEFAULT_AUTHORS = []
DEFAULT_MIN_SCORE = 3.0
DEFAULT_DELAY = 2  # 请求间隔 (秒)
DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT = 10
DEFAULT_PROXY = None  # 代理地址 (例如：http://127.0.0.1:7890)
DEFAULT_PROXY_POOL = []  # 代理池 (多个代理地址)


class MediumWatcher:
    """Medium 监听器"""

    def __init__(self, output_dir: str, delay: float = 2.0, auto_categorize: bool = False, category_rules: str = None, proxy: str = None, proxy_pool: list = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.articles = []
        self.seen_urls = set()  # 已见过的 URL (去重)
        self.delay = delay  # 请求间隔 (秒)
        self.last_request_time = 0
        self.last_update = None  # 上次更新时间
        self.error_log = []  # 错误日志
        self.auto_categorize = auto_categorize  # 自动分类
        self.proxy = proxy  # 主代理地址
        self.proxy_pool = proxy_pool or []  # 代理池
        self.current_proxy_index = 0  # 当前代理索引
        self.failed_proxies = set()  # 失败的代理

        # 默认分类关键词映射
        self.category_keywords = {
            "AI-Technical": ["ai", "llm", "machine-learning", "deep-learning", "nlp", "transformer", "model"],
            "AI-Application": ["application", "tool", "product", "business", "startup"],
            "Programming": ["code", "programming", "python", "javascript", "software", "developer"],
            "Data-Science": ["data", "analytics", "visualization", "statistics"],
            "Other": []  # 默认分类
        }

        # 加载自定义分类规则
        if category_rules:
            self._load_category_rules(category_rules)

        # 加载已有的文章 URL (防止重复收集)
        self._load_existing_urls()
        # 加载增量更新状态
        self._load_incremental_state()
        # 加载错误日志
        self._load_error_log()

        # 配置代理
        self._init_proxy()

    def _init_proxy(self):
        """初始化代理配置"""
        # 1. 优先使用显式配置的代理
        if self.proxy:
            self.proxies = {"http": self.proxy, "https": self.proxy}
            print(f"[INFO] 使用代理：{self.proxy}")
            return

        # 2. 从环境变量加载 (手动配置)
        env_proxy = self._load_proxy_from_env()
        if env_proxy:
            self.proxies = {"http": env_proxy, "https": env_proxy}
            return

        # 3. 使用代理池
        if self.proxy_pool:
            print(f"[INFO] 代理池：{len(self.proxy_pool)} 个代理")
            self._switch_proxy()
            return

        # 4. 无代理
        self.proxies = None

    def _switch_proxy(self):
        """自动切换代理"""
        if not self.proxy_pool:
            return False

        # 过滤掉失败的代理
        available_proxies = [p for p in self.proxy_pool if p not in self.failed_proxies]

        if not available_proxies:
            print(f"[WARN] 所有代理都已失败，尝试使用主代理")
            if self.proxy:
                self.proxies = {"http": self.proxy, "https": self.proxy}
                return True
            return False

        # 选择下一个可用代理
        proxy = available_proxies[self.current_proxy_index % len(available_proxies)]
        self.proxies = {"http": proxy, "https": proxy}
        self.current_proxy_index += 1

        print(f"[INFO] 切换代理：{proxy}")
        return True

    def _mark_proxy_failed(self, proxy: str):
        """标记代理为失败"""
        self.failed_proxies.add(proxy)
        print(f"[WARN] 代理失败：{proxy} (已失败：{len(self.failed_proxies)}/{len(self.proxy_pool)})")

    def _test_proxy(self, proxy: str, timeout: int = 5) -> bool:
        """测试代理是否可用"""
        try:
            test_proxies = {"http": proxy, "https": proxy}
            response = requests.get("https://www.google.com", proxies=test_proxies, timeout=timeout)
            return response.status_code == 200
        except Exception:
            return False

    def _load_proxy_from_env(self) -> str:
        """从环境变量加载代理 (手动配置)"""
        env_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
        for var in env_vars:
            proxy = os.environ.get(var)
            if proxy:
                print(f"[INFO] 从环境变量 {var} 加载代理：{proxy}")
                return proxy
        return None

    def _load_category_rules(self, rules_file: str):
        """加载自定义分类规则"""
        rules_path = Path(rules_file)
        if rules_path.exists():
            try:
                with open(rules_path, "r", encoding="utf-8") as f:
                    custom_rules = json.load(f)
                    # 合并规则 (自定义规则覆盖默认规则)
                    for category, keywords in custom_rules.items():
                        self.category_keywords[category] = keywords
                    print(f"[INFO] 已加载自定义分类规则：{len(custom_rules)} 个分类")
            except Exception as e:
                print(f"[WARN] 加载分类规则失败：{e}")
                print(f"[INFO] 使用默认分类规则")
        else:
            print(f"[WARN] 分类规则文件不存在：{rules_file}")
            print(f"[INFO] 使用默认分类规则")

    def _save_category_rules(self, rules_file: str):
        """保存当前分类规则到文件"""
        rules_path = Path(rules_file)
        with open(rules_path, "w", encoding="utf-8") as f:
            json.dump(self.category_keywords, f, indent=2, ensure_ascii=False)
        print(f"[INFO] 已保存分类规则到 {rules_file}")

    def _load_existing_urls(self):
        """加载已有文章 URL"""
        for md_file in self.output_dir.glob("medium-*.md"):
            # 从文件名提取 URL (如果有 meta 文件)
            meta_file = md_file.with_suffix(".meta.json")
            if meta_file.exists():
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        if "url" in meta:
                            self.seen_urls.add(meta["url"])
                except Exception:
                    pass

    def _load_incremental_state(self):
        """加载增量更新状态"""
        state_file = self.output_dir / ".medium_watcher_state.json"
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    if "last_update" in state:
                        self.last_update = datetime.fromisoformat(state["last_update"])
                        print(f"[INFO] 增量更新：上次更新时间 {self.last_update.strftime('%Y-%m-%d %H:%M')}")
            except Exception:
                pass
        else:
            print(f"[INFO] 首次运行，将获取所有文章")

    def _save_incremental_state(self):
        """保存增量更新状态"""
        state_file = self.output_dir / ".medium_watcher_state.json"
        state = {
            "last_update": datetime.now().isoformat(),
            "total_articles": len(self.seen_urls)
        }
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"[INFO] 已保存更新状态到 {state_file}")

    def _load_error_log(self):
        """加载错误日志"""
        log_file = self.output_dir / ".medium_watcher_errors.json"
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    self.error_log = json.load(f)
                    print(f"[INFO] 已加载 {len(self.error_log)} 条历史错误")
            except Exception:
                self.error_log = []
        else:
            self.error_log = []

    def _log_error(self, error_type: str, message: str, details: dict = None):
        """记录错误"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": message,
            "details": details or {}
        }
        self.error_log.append(error_entry)
        print(f"[ERROR] {error_type}: {message}")

    def _save_error_log(self):
        """保存错误日志"""
        log_file = self.output_dir / ".medium_watcher_errors.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(self.error_log, f, indent=2, ensure_ascii=False)
        print(f"[INFO] 已保存 {len(self.error_log)} 条错误到 {log_file}")

    def _save_error_log(self):
        """保存错误日志"""
        log_file = self.output_dir / ".medium_watcher_errors.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(self.error_log, f, indent=2, ensure_ascii=False)
        print(f"[INFO] 已保存 {len(self.error_log)} 条错误到 {log_file}")

    def _rate_limit(self):
        """速率限制"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            sleep_time = self.delay - elapsed
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _is_duplicate(self, article: dict) -> bool:
        """检查文章是否重复"""
        url = article.get("url", "")
        title = article.get("title", "")

        # URL 去重 (最准确)
        if url in self.seen_urls:
            return True

        # 标题相似度检查 (防止 URL 变化但内容相同)
        title_hash = hash(title.lower().strip())
        if hasattr(self, 'seen_titles') and title_hash in self.seen_titles:
            return True

        return False

    def _mark_as_seen(self, article: dict):
        """标记文章为已见"""
        url = article.get("url", "")
        title = article.get("title", "")

        if url:
            self.seen_urls.add(url)

        if not hasattr(self, 'seen_titles'):
            self.seen_titles = set()
        self.seen_titles.add(hash(title.lower().strip()))

    def fetch_by_tag(self, tag: str, limit: int = 20, timeout: int = 10, max_retries: int = 3) -> list:
        """按标签获取文章"""
        articles = []
        rss_url = f"https://medium.com/feed/tag/{tag}"

        # 速率限制
        self._rate_limit()

        for attempt in range(max_retries):
            try:
                # 使用 requests 获取 RSS (支持 timeout)
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(rss_url, headers=headers, timeout=timeout)
                response.raise_for_status()
                feed = feedparser.parse(response.content)

                # 成功获取，处理文章
                new_count = 0
                for entry in feed.entries[:limit]:
                    article = {
                        "title": entry.title,
                        "url": entry.link,
                        "author": entry.author if hasattr(entry, 'author') else "Unknown",
                        "published": entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                        "tags": [tag],
                        "summary": entry.summary if hasattr(entry, 'summary') else "",
                        "source": "medium",
                        "source_type": "tag"
                    }

                    # 去重检查
                    if not self._is_duplicate(article):
                        articles.append(article)
                        self._mark_as_seen(article)
                        new_count += 1

                dup_count = len(feed.entries[:limit]) - new_count
                print(f"[OK] 标签 #{tag}: 获取 {len(articles)} 篇新文章 (跳过 {dup_count} 篇重复)".encode('utf-8').decode('utf-8'), flush=True)
                break  # 成功则退出重试循环

            except requests.exceptions.Timeout:
                self._log_error("TIMEOUT", f"标签 #{tag} 请求超时", {"attempt": attempt+1, "max_retries": max_retries})
                # 代理池自动切换
                if self.proxy_pool and self.proxies:
                    current_proxy = self.proxies.get('http')
                    self._mark_proxy_failed(current_proxy)
                    self._switch_proxy()
                if attempt >= max_retries - 1:
                    print(f"[ERROR] 标签 #{tag} 获取失败：超时")
                    return []
                time.sleep(2 ** attempt)  # 指数退避
            except requests.exceptions.RequestException as e:
                self._log_error("NETWORK", f"标签 #{tag} 网络错误", {"attempt": attempt+1, "error": str(e)})
                # 代理池自动切换
                if self.proxy_pool and self.proxies:
                    current_proxy = self.proxies.get('http')
                    self._mark_proxy_failed(current_proxy)
                    self._switch_proxy()
                if attempt >= max_retries - 1:
                    print(f"[ERROR] 标签 #{tag} 获取失败：{e}")
                    return []
                time.sleep(2 ** attempt)
            except Exception as e:
                self._log_error("UNKNOWN", f"标签 #{tag} 未知错误", {"error": str(e)})
                print(f"[ERROR] 标签 #{tag} 获取失败：{e}".encode('utf-8').decode('utf-8'), flush=True)
                return []

        # 礼貌延迟
        time.sleep(1)

        return articles

    def fetch_by_author(self, author_url: str, limit: int = 20, timeout: int = 10, max_retries: int = 3) -> list:
        """按作者获取文章"""
        articles = []

        # 从作者 URL 构建 RSS
        if "@medium.com" in author_url:
            rss_url = author_url.replace("@medium.com", "@medium.com/feed")
        elif "medium.com/@" in author_url:
            username = author_url.split("@")[-1]
            rss_url = f"https://medium.com/feed/@{username}"
        else:
            print(f"[WARN] 无效作者 URL: {author_url}")
            return articles

        # 速率限制
        self._rate_limit()

        for attempt in range(max_retries):
            try:
                # 使用 requests 获取 RSS (支持 timeout)
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(rss_url, headers=headers, timeout=timeout)
                response.raise_for_status()
                feed = feedparser.parse(response.content)

                # 成功获取，处理文章
                new_count = 0
                for entry in feed.entries[:limit]:
                    article = {
                        "title": entry.title,
                        "url": entry.link,
                        "author": entry.author if hasattr(entry, 'author') else "Unknown",
                        "published": entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                        "tags": [],
                        "summary": entry.summary if hasattr(entry, 'summary') else "",
                        "source": "medium",
                        "source_type": "author"
                    }

                    # 去重检查
                    if not self._is_duplicate(article):
                        articles.append(article)
                        self._mark_as_seen(article)
                        new_count += 1

                dup_count = len(feed.entries[:limit]) - new_count
                print(f"[OK] 作者 {author_url}: 获取 {len(articles)} 篇新文章 (跳过 {dup_count} 篇重复)".encode('utf-8').decode('utf-8'), flush=True)
                break  # 成功则退出重试循环

            except requests.exceptions.Timeout:
                self._log_error("TIMEOUT", f"作者 {author_url} 请求超时", {"attempt": attempt+1, "max_retries": max_retries})
                if attempt >= max_retries - 1:
                    print(f"[ERROR] 作者 {author_url} 获取失败：超时")
                    return []
                time.sleep(2 ** attempt)
            except requests.exceptions.RequestException as e:
                self._log_error("NETWORK", f"作者 {author_url} 网络错误", {"attempt": attempt+1, "error": str(e)})
                if attempt >= max_retries - 1:
                    print(f"[ERROR] 作者 {author_url} 获取失败：{e}")
                    return []
                time.sleep(2 ** attempt)
            except Exception as e:
                self._log_error("UNKNOWN", f"作者 {author_url} 未知错误", {"error": str(e)})
                print(f"[ERROR] 作者 {author_url} 获取失败：{e}")
                return []

        # 礼貌延迟
        time.sleep(1)

        return articles

    def calculate_quality_score(self, article: dict) -> float:
        """计算质量评分"""
        score = 2.0  # 基础分

        # 标题长度 (适中更好)
        title_len = len(article.get("title", ""))
        if 30 <= title_len <= 100:
            score += 0.5

        # 摘要长度 (长摘要通常质量更高)
        summary_len = len(article.get("summary", ""))
        if summary_len > 500:
            score += 1.0
        elif summary_len > 200:
            score += 0.5

        # 知名作者 (简单关键词匹配)
        known_authors = ["karpathy", "simon willison", "andrej", "yann lecun"]
        if any(name in article.get("author", "").lower() for name in known_authors):
            score += 1.5

        # 标签相关性
        relevant_tags = ["ai", "llm", "machine-learning", "deep-learning", "nlp"]
        if any(tag in article.get("tags", []) for tag in relevant_tags):
            score += 0.5

        return min(5.0, max(1.0, score))

    def extract_content(self, url: str) -> str:
        """提取文章正文"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取正文 (Medium 文章主体)
            article_body = soup.find('article') or soup.find('main')

            if article_body:
                # 提取段落
                paragraphs = article_body.find_all('p')
                content = "\n\n".join([p.get_text() for p in paragraphs[:50]])  # 限制 50 段
                return content

            return ""

        except Exception as e:
            print(f"[WARN] 内容提取失败 {url}: {e}")
            return ""

    def _categorize_article(self, article: dict) -> str:
        """自动分类文章"""
        title = article.get("title", "").lower()
        tags = article.get("tags", [])
        summary = article.get("summary", "").lower()

        # 合并所有文本用于匹配
        all_text = f"{title} {' '.join(tags)} {summary}"

        # 匹配分类
        for category, keywords in self.category_keywords.items():
            if category == "Other":
                continue
            for keyword in keywords:
                if keyword in all_text:
                    return category

        return "Other"

    def save_article(self, article: dict, date_str: str):
        """保存文章"""
        # 自动分类
        category = "Uncategorized"
        if self.auto_categorize:
            category = self._categorize_article(article)
            print(f"[CAT] {article['title'][:40]}... → {category}")

        # 生成文件名
        safe_title = article["title"][:50].replace(" ", "-").replace(":", "")
        safe_title = "".join(c for c in safe_title if c.isalnum() or c in "-_")
        filename = f"medium-{date_str}-{safe_title}.md"

        # 分类目录
        if self.auto_categorize and category != "Uncategorized":
            category_dir = self.output_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            filepath = category_dir / filename
        else:
            filepath = self.output_dir / filename

        # Windows 兼容性：文件名 ASCII 化
        safe_filename = filename.encode('ascii', 'ignore').decode('ascii')
        filepath = filepath.parent / safe_filename

        # Markdown 格式
        md_content = f"""---
source: medium
url: {article['url']}
author: {article['author']}
date: {article['published'][:10]}
tags: {article['tags']}
quality_score: {article['quality_score']:.1f}
collected_date: {date_str}
---

# {article['title']}

**作者:** {article['author']}  
**发布:** {article['published'][:10]}  
**来源:** [{article['url']}]({article['url']})

---

## 摘要

{article['summary']}

---

## 正文

{article.get('content', '[内容待提取]')}

---

*原始文件，待处理*
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        # 元数据 JSON
        meta_path = filepath.with_suffix(".meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(article, f, indent=2, ensure_ascii=False)

        return filepath

    def cleanup_archive(self, archive_after_days: int = 30):
        """清理归档"""
        from datetime import timedelta

        archive_dir = self.output_dir.parent / "Archive" / datetime.now().strftime("%Y-%m")
        archive_dir.mkdir(parents=True, exist_ok=True)

        cutoff_date = datetime.now() - timedelta(days=archive_after_days)

        # 移动旧文件到归档
        for md_file in self.output_dir.glob("medium-*.md"):
            file_date = datetime.strptime(md_file.stem.split("-")[1], "%Y-%m-%d")

            if file_date < cutoff_date:
                # 移动到归档
                md_file.rename(archive_dir / md_file.name)
                meta_file = md_file.with_suffix(".meta.json")
                if meta_file.exists():
                    meta_file.rename(archive_dir / meta_file.name)
                print(f"📦 归档：{md_file.name}")

    def watch(self, tags: list = None, authors: list = None,
              min_score: float = DEFAULT_MIN_SCORE, limit_per_source: int = 20):
        """执行监听"""
        print(f"\n=== Medium Watcher — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")

        date_str = datetime.now().strftime("%Y-%m-%d")
        tags = tags or DEFAULT_TAGS
        authors = authors or DEFAULT_AUTHORS

        # 按标签获取
        for tag in tags:
            articles = self.fetch_by_tag(tag, limit=limit_per_source, timeout=DEFAULT_TIMEOUT, max_retries=DEFAULT_MAX_RETRIES)
            for article in articles:
                article['quality_score'] = self.calculate_quality_score(article)
                if article['quality_score'] >= min_score:
                    self.articles.append(article)

        # 按作者获取
        for author_url in authors:
            articles = self.fetch_by_author(author_url, limit=limit_per_source, timeout=DEFAULT_TIMEOUT, max_retries=DEFAULT_MAX_RETRIES)
            for article in articles:
                article['quality_score'] = self.calculate_quality_score(article)
                if article['quality_score'] >= min_score:
                    self.articles.append(article)

        print(f"\n[SUMMARY] 获取文章总数：{len(self.articles)} (≥{min_score}分)\n")

        # 保存文章
        saved_count = 0
        for article in self.articles:
            filepath = self.save_article(article, date_str)
            print(f"[SAVE] 保存：{filepath.name}")
            saved_count += 1

        print(f"\n[OK] 完成！保存 {saved_count} 篇文章到 {self.output_dir}")

        # 生成摘要
        self.generate_summary(date_str)

    def generate_summary(self, date_str: str):
        """生成摘要报告"""
        avg_score = 0
        if self.articles:
            avg_score = sum(a['quality_score'] for a in self.articles) / len(self.articles)

        summary = f"""# Medium Watcher 摘要 — {date_str}

**收集时间:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**文章总数:** {len(self.articles)}  
**平均评分:** {avg_score:.1f}

## 高质文章 (≥4.0 分)

| 评分 | 标题 | 作者 | 标签 |
|------|------|------|------|
"""

        high_quality = [a for a in self.articles if a['quality_score'] >= 4.0]
        high_quality.sort(key=lambda x: x['quality_score'], reverse=True)

        for article in high_quality[:10]:
            title_short = article['title'][:40] + "..." if len(article['title']) > 40 else article['title']
            summary += f"| {article['quality_score']:.1f} | [{title_short}]({article['url']}) | {article['author']} | {', '.join(article['tags'])} |\n"

        summary_file = self.output_dir / f"medium-summary-{date_str}.md"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"[SUMMARY] 摘要报告：{summary_file}")


def main():
    parser = argparse.ArgumentParser(description="Medium 监听器")
    parser.add_argument("--tags", type=str, default=",".join(DEFAULT_TAGS),
                        help="标签列表，逗号分隔")
    parser.add_argument("--authors", type=str, default="",
                        help="作者 URL 列表，逗号分隔")
    parser.add_argument("--output", type=str, default="Medium/Raw/",
                        help="输出目录")
    parser.add_argument("--min-score", type=float, default=DEFAULT_MIN_SCORE,
                        help="最低质量评分 (默认 3.0)")
    parser.add_argument("--high-quality-only", action="store_true",
                        help="只保存高质量文章 (≥4.0 分)")
    parser.add_argument("--incremental", action="store_true",
                        help="增量更新模式 (只获取新文章)")
    parser.add_argument("--show-errors", action="store_true",
                        help="显示历史错误日志")
    parser.add_argument("--auto-categorize", action="store_true",
                        help="自动分类文章到子目录")
    parser.add_argument("--category-rules", type=str, default=None,
                        help="自定义分类规则 JSON 文件")
    parser.add_argument("--export-rules", type=str, default=None,
                        help="导出当前分类规则到 JSON 文件")
    parser.add_argument("--show-rules", action="store_true",
                        help="显示当前分类规则")
    parser.add_argument("--proxy", type=str, default=DEFAULT_PROXY,
                        help="代理地址 (例如：http://127.0.0.1:7890)")
    parser.add_argument("--proxy-pool", type=str, default=None,
                        help="代理池 JSON 文件 (包含多个代理地址)")
    parser.add_argument("--test-proxy", action="store_true",
                        help="测试代理连接")
    parser.add_argument("--test-proxy-pool", action="store_true",
                        help="测试代理池中所有代理")
    parser.add_argument("--limit", type=int, default=20,
                        help="每个源的文章数量限制")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY,
                        help="请求间隔 (秒)，防止被屏蔽")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help="请求超时 (秒)")
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES,
                        help="最大重试次数")
    parser.add_argument("--cleanup", action="store_true",
                        help="执行清理归档")
    parser.add_argument("--archive-after-days", type=int, default=30,
                        help="归档天数阈值")
    args = parser.parse_args()

    # 显示分类规则
    if args.show_rules:
        watcher_temp = MediumWatcher(args.output)
        print("\n=== 当前分类规则 ===\n")
        for category, keywords in watcher_temp.category_keywords.items():
            print(f"{category}:")
            if keywords:
                print(f"  关键词：{', '.join(keywords)}")
            else:
                print(f"  (默认分类)")
            print()
        return

    # 导出分类规则
    if args.export_rules:
        watcher_temp = MediumWatcher(args.output)
        watcher_temp._save_category_rules(args.export_rules)
        return

    # 显示错误日志
    if args.show_errors:
        error_file = Path(args.output) / ".medium_watcher_errors.json"
        if error_file.exists():
            with open(error_file, "r", encoding="utf-8") as f:
                errors = json.load(f)
                print(f"\n=== 错误日志 ({len(errors)} 条) ===\n")
                for err in errors[-10:]:  # 显示最近 10 条
                    print(f"[{err['timestamp']}] {err['type']}: {err['message']}")
                    if err.get('details'):
                        print(f"  详情：{err['details']}")
                    print()
        else:
            print("\n[INFO] 无错误日志\n")
        return

    # 高质量模式
    if args.high_quality_only:
        args.min_score = 4.0
        print(f"\n[INFO] 高质量模式：只保存≥4.0 分的文章\n")

    # 自动分类模式
    if args.auto_categorize:
        print(f"\n[INFO] 自动分类模式：文章将按主题分类到子目录\n")

    # 测试代理
    if args.test_proxy:
        if args.proxy:
            print(f"\n[INFO] 测试代理：{args.proxy}")
            try:
                proxies = {"http": args.proxy, "https": args.proxy}
                response = requests.get("https://www.google.com", proxies=proxies, timeout=10)
                print(f"[OK] 代理连接成功！状态码：{response.status_code}")
            except Exception as e:
                print(f"[ERROR] 代理连接失败：{e}")
        else:
            print("\n[WARN] 未指定代理地址 (--proxy)")
        return

    # 测试代理池
    if args.test_proxy_pool:
        if args.proxy_pool:
            print(f"\n[INFO] 测试代理池：{args.proxy_pool}")
            try:
                with open(args.proxy_pool, "r", encoding="utf-8") as f:
                    proxy_pool = json.load(f)
                print(f"[INFO] 代理池包含 {len(proxy_pool)} 个代理\n")

                working = 0
                for i, proxy in enumerate(proxy_pool[:10]):  # 测试前 10 个
                    print(f"[{i+1}/{len(proxy_pool)}] 测试 {proxy}...", end=" ")
                    watcher_temp = MediumWatcher(args.output)
                    if watcher_temp._test_proxy(proxy):
                        print("✅ OK")
                        working += 1
                    else:
                        print("❌ FAIL")

                print(f"\n[SUMMARY] 可用代理：{working}/{min(10, len(proxy_pool))}")
            except Exception as e:
                print(f"[ERROR] 测试失败：{e}")
        else:
            print("\n[WARN] 未指定代理池文件 (--proxy-pool)")
        return

    # 加载代理池
    proxy_pool = []
    if args.proxy_pool:
        try:
            with open(args.proxy_pool, "r", encoding="utf-8") as f:
                proxy_pool = json.load(f)
            print(f"\n[INFO] 已加载代理池：{len(proxy_pool)} 个代理")
        except Exception as e:
            print(f"[WARN] 加载代理池失败：{e}")

    watcher = MediumWatcher(
        args.output,
        delay=args.delay,
        auto_categorize=args.auto_categorize,
        category_rules=args.category_rules,
        proxy=args.proxy,
        proxy_pool=proxy_pool
    )

    if args.cleanup:
        watcher.cleanup_archive(args.archive_after_days)
    else:
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        authors = [a.strip() for a in args.authors.split(",")] if args.authors else []

        watcher.watch(
            tags=tags,
            authors=authors,
            min_score=args.min_score,
            limit_per_source=args.limit
        )

    return 0


if __name__ == "__main__":
    exit(main())
