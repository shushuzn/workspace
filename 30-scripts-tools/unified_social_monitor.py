#!/usr/bin/env python3
"""Unified Social Monitor - Monitor Reddit and Twitter/X for AI/LLM content."""

import argparse
import json
import logging
import os
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    import praw
    import requests
    from requests_oauthlib import OAuth1
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install praw requests requests-oauthlib")
    sys.exit(1)


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "social-monitor"

REDDIT_DB = DATA_DIR / "reddit.db"
REDDIT_LOG = DATA_DIR / "reddit.log"

TWITTER_DB = DATA_DIR / "twitter.db"
TWITTER_LOG = DATA_DIR / "twitter.log"

DAILY_DIR = DATA_DIR / "daily"

REDDIT_SUBREDDITS = [
    "MachineLearning",
    "ArtificialIntelligence",
    "LearnMachineLearning",
    "MachineLearningProjects",
    "MLQuestions",
    "bigmodels",
    "LanguageModels",
]

TWITTER_USERS = [
    "ylecun",
    "karpathy",
    "sama",
    "geoffreyhinton",
    "AndrejKarpathy",
    "SamAltman",
    "IlyaSutskever",
    "fchollet",
    "huggingface",
    "OpenAI",
    "deepmind",
    "meta",
    "googleai",
]

TWITTER_HASHTAGS = ["#AI", "#LLM", "#MachineLearning", "#DeepLearning"]


def setup_logger(name: str, log_file: Path, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def init_database(db_path: Path, table_name: str) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id TEXT UNIQUE NOT NULL,
            title TEXT,
            content TEXT,
            author TEXT,
            url TEXT,
            timestamp TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    return conn


def post_exists(conn: sqlite3.Connection, table_name: str, post_id: str) -> bool:
    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM {table_name} WHERE post_id = ?", (post_id,))
    return cursor.fetchone() is not None


def insert_post(
    conn: sqlite3.Connection,
    table_name: str,
    post_id: str,
    title: str,
    content: str,
    author: str,
    url: str,
    timestamp: str,
) -> None:
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"INSERT OR IGNORE INTO {table_name} (post_id, title, content, author, url, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (post_id, title, content, author, url, timestamp),
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")


class RedditMonitor:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.conn = init_database(REDDIT_DB, "reddit_posts")
        self.reddit = None
        self._init_reddit()

    def _init_reddit(self):
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                user_agent="unified-social-monitor/1.0",
            )
            self.logger.info("Reddit API initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Reddit API: {e}")
            self.reddit = None

    def fetch_subreddit_posts(self, subreddit_name: str, limit: int = 20) -> list:
        if not self.reddit:
            self.logger.warning("Reddit API not available")
            return []
        posts = []
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            for submission in subreddit.hot(limit=limit):
                post_id = f"reddit_{submission.id}"
                if post_exists(self.conn, "reddit_posts", post_id):
                    continue
                posts.append(
                    {
                        "post_id": post_id,
                        "title": submission.title,
                        "content": submission.selftext[:500],
                        "author": str(submission.author)
                        if submission.author
                        else "unknown",
                        "url": f"https://www.reddit.com/r/{subreddit_name}/comments/{submission.id}",
                        "timestamp": datetime.fromtimestamp(
                            submission.created_utc
                        ).isoformat(),
                        "subreddit": subreddit_name,
                        "score": submission.score,
                        "num_comments": submission.num_comments,
                    }
                )
            self.logger.info(f"Fetched {len(posts)} new posts from r/{subreddit_name}")
        except Exception as e:
            self.logger.error(f"Error fetching r/{subreddit_name}: {e}")
        return posts

    def monitor_all(self, limit: int = 20) -> list:
        all_posts = []
        for subreddit in REDDIT_SUBREDDITS:
            self.logger.info(f"Monitoring r/{subreddit}...")
            posts = self.fetch_subreddit_posts(subreddit, limit)
            all_posts.extend(posts)
            for post in posts:
                insert_post(
                    self.conn,
                    "reddit_posts",
                    post["post_id"],
                    post["title"],
                    post["content"],
                    post["author"],
                    post["url"],
                    post["timestamp"],
                )
        return all_posts

    def generate_markdown_report(self, posts: list, date: datetime = None) -> str:
        if date is None:
            date = datetime.now()
        report_date = date.strftime("%Y-%m-%d")
        header = f"""# Reddit AI/ML Monitor Report - {report_date}

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
- Total Posts: {len(posts)}
- Subreddits Monitored: {len(REDDIT_SUBREDDITS)}

## Posts
"""
        if not posts:
            header += "\nNo new posts found.\n"
            return header
        by_subreddit = {}
        for post in posts:
            sr = post.get("subreddit", "unknown")
            if sr not in by_subreddit:
                by_subreddit[sr] = []
            by_subreddit[sr].append(post)
        for subreddit, sr_posts in sorted(by_subreddit.items()):
            header += f"\n### r/{subreddit} ({len(sr_posts)} posts)\n\n"
            for post in sr_posts[:10]:
                header += f"- **[{post['title']}]({post['url']})**\n"
                header += f"  - Author: u/{post['author']} | Score: {post.get('score', '?')} | Comments: {post.get('num_comments', '?')}\n"
                if post["content"]:
                    header += f"  - Preview: {post['content'][:200]}...\n"
                header += f"  - {post['timestamp']}\n\n"
        return header

    def save_daily_report(self, posts: list, date: datetime = None) -> Path:
        if date is None:
            date = datetime.now()
        report_date = date.strftime("%Y-%m-%d")
        report_path = DAILY_DIR / f"reddit-{report_date}.md"
        report_content = self.generate_markdown_report(posts, date)
        DAILY_DIR.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        self.logger.info(f"Saved daily report to {report_path}")
        return report_path


class TwitterMonitor:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.conn = init_database(TWITTER_DB, "twitter_posts")
        self.auth = None
        self._init_auth()

    def _init_auth(self):
        consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
        consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        if all([consumer_key, consumer_secret, access_token, access_token_secret]):
            self.auth = OAuth1(
                consumer_key, consumer_secret, access_token, access_token_secret
            )
            self.logger.info("Twitter API authenticated successfully")
        else:
            self.logger.warning(
                "Twitter API credentials not found. Using limited mode."
            )

    def search_tweets(self, query: str, max_results: int = 20) -> list:
        if not self.auth:
            self.logger.warning("Twitter API not authenticated")
            return []
        tweets = []
        try:
            url = "https://api.twitter.com/2/tweets/search/recent"
            params = {
                "query": query,
                "max_results": min(max_results, 100),
                "tweet.fields": "created_at,author_id,public_metrics",
                "user.fields": "username,name",
                "expansions": "author_id",
            }
            response = requests.get(url, auth=self.auth, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
            for tweet in data.get("data", []):
                post_id = f"twitter_{tweet['id']}"
                if post_exists(self.conn, "twitter_posts", post_id):
                    continue
                user = users.get(tweet["author_id"], {})
                username = user.get("username", "unknown")
                tweets.append(
                    {
                        "post_id": post_id,
                        "title": tweet.get("text", "")[:100],
                        "content": tweet.get("text", ""),
                        "author": username,
                        "url": f"https://twitter.com/{username}/status/{tweet['id']}",
                        "timestamp": tweet.get("created_at", ""),
                        "tweet_id": tweet["id"],
                        "author_id": tweet["author_id"],
                        "retweet_count": tweet.get("public_metrics", {}).get(
                            "retweet_count", 0
                        ),
                        "reply_count": tweet.get("public_metrics", {}).get(
                            "reply_count", 0
                        ),
                        "like_count": tweet.get("public_metrics", {}).get(
                            "like_count", 0
                        ),
                        "quote_count": tweet.get("public_metrics", {}).get(
                            "quote_count", 0
                        ),
                    }
                )
            self.logger.info(f"Found {len(tweets)} new tweets for query: {query}")
        except Exception as e:
            self.logger.error(f"Error searching tweets for '{query}': {e}")
        return tweets

    def search_user_tweets(self, username: str, max_results: int = 20) -> list:
        if not self.auth:
            self.logger.warning("Twitter API not authenticated")
            return []
        tweets = []
        try:
            user_url = f"https://api.twitter.com/2/users/by/username/{username}"
            user_response = requests.get(user_url, auth=self.auth, timeout=30)
            if user_response.status_code != 200:
                self.logger.warning(f"Could not find user: {username}")
                return []
            user_data = user_response.json()
            user_id = user_data["data"]["id"]
            tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
            params = {
                "max_results": min(max_results, 100),
                "tweet.fields": "created_at,public_metrics",
            }
            response = requests.get(
                tweets_url, auth=self.auth, params=params, timeout=30
            )
            response.raise_for_status()
            data = response.json()
            for tweet in data.get("data", []):
                post_id = f"twitter_{tweet['id']}"
                if post_exists(self.conn, "twitter_posts", post_id):
                    continue
                tweets.append(
                    {
                        "post_id": post_id,
                        "title": tweet.get("text", "")[:100],
                        "content": tweet.get("text", ""),
                        "author": username,
                        "url": f"https://twitter.com/{username}/status/{tweet['id']}",
                        "timestamp": tweet.get("created_at", ""),
                        "tweet_id": tweet["id"],
                        "author_id": user_id,
                        "retweet_count": tweet.get("public_metrics", {}).get(
                            "retweet_count", 0
                        ),
                        "reply_count": tweet.get("public_metrics", {}).get(
                            "reply_count", 0
                        ),
                        "like_count": tweet.get("public_metrics", {}).get(
                            "like_count", 0
                        ),
                        "quote_count": tweet.get("public_metrics", {}).get(
                            "quote_count", 0
                        ),
                    }
                )
            self.logger.info(f"Found {len(tweets)} new tweets from @{username}")
        except Exception as e:
            self.logger.error(f"Error fetching tweets from @{username}: {e}")
        return tweets

    def monitor_users(self, max_results: int = 20) -> list:
        all_tweets = []
        for username in TWITTER_USERS:
            self.logger.info(f"Monitoring @{username}...")
            tweets = self.search_user_tweets(username, max_results)
            all_tweets.extend(tweets)
            for tweet in tweets:
                insert_post(
                    self.conn,
                    "twitter_posts",
                    tweet["post_id"],
                    tweet["title"],
                    tweet["content"],
                    tweet["author"],
                    tweet["url"],
                    tweet["timestamp"],
                )
        return all_tweets

    def monitor_hashtags(self, max_results: int = 20) -> list:
        all_tweets = []
        for hashtag in TWITTER_HASHTAGS:
            self.logger.info(f"Monitoring {hashtag}...")
            query = hashtag.replace("#", "")
            tweets = self.search_tweets(f"#{query}", max_results)
            all_tweets.extend(tweets)
            for tweet in tweets:
                insert_post(
                    self.conn,
                    "twitter_posts",
                    tweet["post_id"],
                    tweet["title"],
                    tweet["content"],
                    tweet["author"],
                    tweet["url"],
                    tweet["timestamp"],
                )
        return all_tweets

    def monitor_all(self, max_results: int = 20) -> list:
        user_tweets = self.monitor_users(max_results)
        hashtag_tweets = self.monitor_hashtags(max_results)
        all_tweets = user_tweets + hashtag_tweets
        seen_ids = set()
        unique_tweets = []
        for tweet in all_tweets:
            if tweet["post_id"] not in seen_ids:
                seen_ids.add(tweet["post_id"])
                unique_tweets.append(tweet)
        return unique_tweets

    def generate_markdown_report(self, tweets: list, date: datetime = None) -> str:
        if date is None:
            date = datetime.now()
        report_date = date.strftime("%Y-%m-%d")
        header = f"""# Twitter/X AI/LLM Monitor Report - {report_date}

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
- Total Tweets: {len(tweets)}
- Users Monitored: {len(TWITTER_USERS)}
- Hashtags Monitored: {len(TWITTER_HASHTAGS)}

## Tweets
"""
        if not tweets:
            header += "\nNo new tweets found.\n"
            return header
        by_author = {}
        for tweet in tweets:
            author = tweet.get("author", "unknown")
            if author not in by_author:
                by_author[author] = []
            by_author[author].append(tweet)
        for author, author_tweets in sorted(by_author.items()):
            header += f"\n### @{author} ({len(author_tweets)} tweets)\n\n"
            for tweet in author_tweets[:10]:
                header += f"- **[{tweet['title']}]({tweet['url']})**\n"
                metrics = []
                if tweet.get("retweet_count", 0) > 0:
                    metrics.append(f"Retweets: {tweet['retweet_count']}")
                if tweet.get("like_count", 0) > 0:
                    metrics.append(f"Likes: {tweet['like_count']}")
                if tweet.get("reply_count", 0) > 0:
                    metrics.append(f"Replies: {tweet['reply_count']}")
                if tweet.get("quote_count", 0) > 0:
                    metrics.append(f"Quotes: {tweet['quote_count']}")
                if metrics:
                    header += f"  - {' | '.join(metrics)}\n"
                if tweet["content"]:
                    header += f"  - Content: {tweet['content'][:200]}...\n"
                header += f"  - {tweet['timestamp']}\n\n"
        return header

    def save_daily_report(self, tweets: list, date: datetime = None) -> Path:
        if date is None:
            date = datetime.now()
        report_date = date.strftime("%Y-%m-%d")
        report_path = DAILY_DIR / f"twitter-{report_date}.md"
        report_content = self.generate_markdown_report(tweets, date)
        DAILY_DIR.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        self.logger.info(f"Saved daily report to {report_path}")
        return report_path


def get_stats() -> dict:
    stats = {
        "generated_at": datetime.now().isoformat(),
        "reddit": {
            "database": str(REDDIT_DB),
            "posts_count": 0,
            "subreddits_monitored": len(REDDIT_SUBREDDITS),
        },
        "twitter": {
            "database": str(TWITTER_DB),
            "posts_count": 0,
            "users_monitored": len(TWITTER_USERS),
            "hashtags_monitored": len(TWITTER_HASHTAGS),
        },
    }
    try:
        if REDDIT_DB.exists():
            conn = sqlite3.connect(REDDIT_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM reddit_posts")
            stats["reddit"]["posts_count"] = cursor.fetchone()[0]
            conn.close()
    except Exception as e:
        stats["reddit"]["error"] = str(e)
    try:
        if TWITTER_DB.exists():
            conn = sqlite3.connect(TWITTER_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM twitter_posts")
            stats["twitter"]["posts_count"] = cursor.fetchone()[0]
            conn.close()
    except Exception as e:
        stats["twitter"]["error"] = str(e)
    return stats


def save_stats_json(stats: dict, output_path: Path = None) -> Path:
    if output_path is None:
        output_path = DATA_DIR / "stats.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    return output_path


def cmd_reddit(args):
    logger = setup_logger("reddit", REDDIT_LOG)
    logger.info("=" * 60)
    logger.info("Starting Reddit Monitor")
    logger.info("=" * 60)
    monitor = RedditMonitor(logger)
    posts = monitor.monitor_all(limit=args.limit)
    logger.info(f"Total new posts: {len(posts)}")
    report_path = monitor.save_daily_report(posts)
    logger.info(f"Report saved: {report_path}")
    return posts


def cmd_twitter(args):
    logger = setup_logger("twitter", TWITTER_LOG)
    logger.info("=" * 60)
    logger.info("Starting Twitter/X Monitor")
    logger.info("=" * 60)
    monitor = TwitterMonitor(logger)
    tweets = monitor.monitor_all(max_results=args.limit)
    logger.info(f"Total new tweets: {len(tweets)}")
    report_path = monitor.save_daily_report(tweets)
    logger.info(f"Report saved: {report_path}")
    return tweets


def cmd_all(args):
    logger = setup_logger("unified", DATA_DIR / "unified.log")
    logger.info("=" * 60)
    logger.info("Starting Unified Social Monitor")
    logger.info("=" * 60)
    logger.info("\n--- Reddit Monitor ---")
    reddit_posts = cmd_reddit(args)
    logger.info("\n--- Twitter Monitor ---")
    twitter_tweets = cmd_twitter(args)
    logger.info("\n" + "=" * 60)
    logger.info("Unified Monitor Complete")
    logger.info(f"Reddit posts: {len(reddit_posts)}")
    logger.info(f"Twitter tweets: {len(twitter_tweets)}")
    logger.info("=" * 60)
    return reddit_posts, twitter_tweets


def cmd_stats(args):
    stats = get_stats()
    print("\n" + "=" * 60)
    print("Social Monitor Statistics")
    print("=" * 60)
    print(f"\nReddit:")
    print(f"  Database: {stats['reddit']['database']}")
    print(f"  Posts: {stats['reddit']['posts_count']}")
    print(f"  Subreddits: {stats['reddit']['subreddits_monitored']}")
    print(f"\nTwitter/X:")
    print(f"  Database: {stats['twitter']['database']}")
    print(f"  Posts: {stats['twitter']['posts_count']}")
    print(f"  Users: {stats['twitter']['users_monitored']}")
    print(f"  Hashtags: {stats['twitter']['hashtags_monitored']}")
    output_path = save_stats_json(stats)
    print(f"\nStats saved to: {output_path}")
    print("=" * 60)
    return stats


def main():
    # Critic v5.0 integration
    critic_result = subprocess.run(
        [sys.executable, "critic_v5_review.py", "--scenario", "tool_optimize", "--auto"],
        cwd=str(Path(__file__).parent),
        timeout=300,
    )
    if critic_result.returncode != 0:
        print("[ERROR] Critic Review Failed. Aborting.")
        return

    print("[OK] Critic Review Passed")

    parser = argparse.ArgumentParser(
        prog="unified_social_monitor",
        description="Unified Social Monitor - Monitor Reddit and Twitter/X for AI/LLM content",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    reddit_parser = subparsers.add_parser("reddit", help="Monitor Reddit AI subreddits")
    reddit_parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=20,
        help="Maximum posts to fetch per subreddit (default: 20)",
    )
    twitter_parser = subparsers.add_parser(
        "twitter", help="Monitor Twitter/X AI researchers"
    )
    twitter_parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=20,
        help="Maximum tweets to fetch per source (default: 20)",
    )
    all_parser = subparsers.add_parser(
        "all", help="Run both Reddit and Twitter monitors"
    )
    all_parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=20,
        help="Maximum posts/tweets to fetch (default: 20)",
    )
    stats_parser = subparsers.add_parser("stats", help="Show monitoring statistics")
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    if args.command == "reddit":
        cmd_reddit(args)
    elif args.command == "twitter":
        cmd_twitter(args)
    elif args.command == "all":
        cmd_all(args)
    elif args.command == "stats":
        cmd_stats(args)


if __name__ == "__main__":
    main()
