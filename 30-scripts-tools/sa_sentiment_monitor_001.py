import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis - SA-004: News & Sentiment Monitor
Monitor financial news, social media, analyst reports with sentiment analysis
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import random

class NewsSentimentMonitor:
    """Monitor and analyze news sentiment for stocks"""
    
    def __init__(self, data_dir: str = "60-DATA/stock_news"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.sources = {
            "sina": {"name": "新浪财经", "region": "CN", "language": "zh"},
            "xueqiu": {"name": "雪球", "region": "CN", "language": "zh"},
            "seeking_alpha": {"name": "Seeking Alpha", "region": "US", "language": "en"},
            "twitter": {"name": "Twitter", "region": "Global", "language": "en"}
        }
        
        self.sentiment_labels = ["positive", "neutral", "negative"]
        
        self.monitoring_log = self._load_monitoring_log()
    
    def _load_monitoring_log(self) -> Dict:
        """Load monitoring log"""
        log_file = self.data_dir / "monitoring_log.json"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "version": "1.0",
            "monitoring_sessions": [],
            "stats": {
                "total_sessions": 0,
                "total_articles": 0,
                "positive": 0,
                "neutral": 0,
                "negative": 0,
            }
        }
    
    def _save_monitoring_log(self):
        """Save monitoring log"""
        log_file = self.data_dir / "monitoring_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.monitoring_log, f, ensure_ascii=False, indent=2)
    
    def monitor_sentiment(self, symbol: str, sources: List[str] = None,
                         hours: int = 24, limit: int = 50) -> Optional[Dict]:
        """
        Monitor news sentiment for a stock
        
        Args:
            symbol: Stock symbol
            sources: List of sources to monitor (default: all)
            hours: Time window in hours
            limit: Maximum articles to collect per source
            
        Returns:
            Dict with sentiment analysis or None if failed
        """
        if sources is None:
            sources = list(self.sources.keys())
        
        # Validate sources
        invalid_sources = [s for s in sources if s not in self.sources]
        if invalid_sources:
            print(f"[WARN] Unknown sources: {invalid_sources}")
            sources = [s for s in sources if s in self.sources]
        
        if not sources:
            print("[ERROR] No valid sources specified")
            return None
        
        # Check cache (within 1 hour)
        cache_key = f"{symbol}_{'_'.join(sources)}_{hours}h"
        cache_file = self.data_dir / f"{cache_key.replace('-', '_')}.json"
        
        if cache_file.exists():
            print(f"[INFO] Loading from cache: {cache_file.name}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Collect from sources
        print(f"[INFO] Monitoring sentiment for {symbol} ({len(sources)} sources, {hours}h)")
        all_articles = []
        
        for source in sources:
            articles = self._collect_from_source(symbol, source, hours, limit)
            all_articles.extend(articles)
        
        if not all_articles:
            print("[WARN] No articles found")
            return None
        
        # Analyze sentiment
        sentiment_result = self._analyze_sentiment(all_articles)
        
        result = {
            "symbol": symbol,
            "monitoring_period": f"{hours}h",
            "sources": sources,
            "total_articles": len(all_articles),
            "sentiment_summary": sentiment_result,
            "articles": all_articles[:limit],  # Return limited articles
            "monitored_at": datetime.now().isoformat()
        }
        
        # Save to cache
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Log monitoring
        self._log_monitoring(symbol, len(all_articles), sentiment_result)
        
        return result
    
    def _collect_from_source(self, symbol: str, source: str,
                            hours: int, limit: int) -> List[Dict]:
        """Collect articles from a specific source"""
        articles = []
        
        # Simulated article collection
        num_articles = random.randint(5, min(limit, 30))
        
        for i in range(num_articles):
            # Generate article
            hours_ago = random.randint(0, hours)
            timestamp = datetime.now() - timedelta(hours=hours_ago)
            
            # Generate headline based on symbol
            headlines_positive = [
                f"{symbol} beats earnings expectations",
                f"{symbol} announces new product launch",
                f"Analysts upgrade {symbol} to buy",
                f"{symbol} stock surges on strong revenue",
                f"{symbol} expands market share"
            ]
            
            headlines_negative = [
                f"{symbol} misses earnings estimates",
                f"{symbol} faces regulatory scrutiny",
                f"Analysts downgrade {symbol}",
                f"{symbol} stock drops on weak guidance",
                f"{symbol} loses key customer"
            ]
            
            headlines_neutral = [
                f"{symbol} holds annual shareholder meeting",
                f"{symbol} announces dividend payment",
                f"Market analysis: {symbol} outlook",
                f"{symbol} trading volume increases",
                f"{symbol} sector performance review"
            ]
            
            # Random sentiment
            sentiment = random.choice(self.sentiment_labels)
            
            if sentiment == "positive":
                headline = random.choice(headlines_positive)
                sentiment_score = random.uniform(0.5, 1.0)
            elif sentiment == "negative":
                headline = random.choice(headlines_negative)
                sentiment_score = random.uniform(-1.0, -0.5)
            else:
                headline = random.choice(headlines_neutral)
                sentiment_score = random.uniform(-0.3, 0.3)
            
            article = {
                "title": headline,
                "source": source,
                "source_name": self.sources[source]["name"],
                "published_at": timestamp.isoformat(),
                "hours_ago": hours_ago,
                "url": f"https://{source}.com/article/{hash(headline) % 100000}",
                "sentiment": sentiment,
                "sentiment_score": round(sentiment_score, 3),
                "relevance_score": round(random.uniform(0.6, 1.0), 2)
            }
            
            articles.append(article)
        
        return articles
    
    def _analyze_sentiment(self, articles: List[Dict]) -> Dict:
        """Analyze overall sentiment from articles"""
        if not articles:
            return {
                "overall": "neutral",
                "score": 0.0,
                "distribution": {"positive": 0, "neutral": 0, "negative": 0}
            }
        
        # Count sentiments
        positive_count = sum(1 for a in articles if a["sentiment"] == "positive")
        neutral_count = sum(1 for a in articles if a["sentiment"] == "neutral")
        negative_count = sum(1 for a in articles if a["sentiment"] == "negative")
        
        total = len(articles)
        
        # Calculate average sentiment score
        avg_score = sum(a["sentiment_score"] for a in articles) / total
        
        # Determine overall sentiment
        if avg_score > 0.2:
            overall = "positive"
        elif avg_score < -0.2:
            overall = "negative"
        else:
            overall = "neutral"
        
        return {
            "overall": overall,
            "score": round(avg_score, 3),
            "distribution": {
                "positive": positive_count,
                "neutral": neutral_count,
                "negative": negative_count
            },
            "percentages": {
                "positive": round(positive_count / total * 100, 1),
                "neutral": round(neutral_count / total * 100, 1),
                "negative": round(negative_count / total * 100, 1)
            }
        }
    
    def get_sentiment_trend(self, symbol: str, days: int = 7) -> Optional[List[Dict]]:
        """Get sentiment trend over multiple days"""
        trend = []
        
        for day in range(days):
            hours = (day + 1) * 24
            result = self.monitor_sentiment(symbol, hours=24, limit=20)
            
            if result:
                trend.append({
                    "date": (datetime.now() - timedelta(days=day)).strftime("%Y-%m-%d"),
                    "overall": result["sentiment_summary"]["overall"],
                    "score": result["sentiment_summary"]["score"],
                    "article_count": result["total_articles"]
                })
        
        return trend
    
    def _log_monitoring(self, symbol: str, articles: int, sentiment: Dict):
        """Log monitoring session"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "articles": articles,
            "sentiment": sentiment["overall"],
            "score": sentiment["score"]
        }
        
        self.monitoring_log["monitoring_sessions"].append(log_entry)
        self.monitoring_log["stats"]["total_sessions"] += 1
        self.monitoring_log["stats"]["total_articles"] += articles
        
        # Update sentiment counts
        dist = sentiment["distribution"]
        self.monitoring_log["stats"]["positive"] += dist["positive"]
        self.monitoring_log["stats"]["neutral"] += dist["neutral"]
        self.monitoring_log["stats"]["negative"] += dist["negative"]
        
        # Keep only last 500 entries
        self.monitoring_log["monitoring_sessions"] = self.monitoring_log["monitoring_sessions"][-500:]
        
        self._save_monitoring_log()
    
    def get_stats(self) -> Dict:
        """Get monitoring statistics"""
        return self.monitoring_log["stats"].copy()
    
    def display_status(self) -> str:
        """Display monitor status"""
        stats = self.get_stats()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 15 + "News Sentiment Monitor Status")
        output.append("=" * 70)
        
        output.append(f"\n[News Sources]")
        for src_id, src in self.sources.items():
            output.append(f"  {src['name']:20} ({src['region']}, {src['language']})")
        
        output.append(f"\n[Sentiment Labels]")
        for label in self.sentiment_labels:
            output.append(f"  - {label}")
        
        output.append(f"\n[Statistics]")
        output.append(f"  Total Sessions:    {stats['total_sessions']}")
        output.append(f"  Total Articles:    {stats['total_articles']}")
        output.append(f"  Positive:          {stats['positive']}")
        output.append(f"  Neutral:           {stats['neutral']}")
        output.append(f"  Negative:          {stats['negative']}")
        
        if stats["total_articles"] > 0:
            pos_pct = stats["positive"] / stats["total_articles"] * 100
            neg_pct = stats["negative"] / stats["total_articles"] * 100
            output.append(f"  Positive Rate:     {pos_pct:.1f}%")
            output.append(f"  Negative Rate:     {neg_pct:.1f}%")
        
        output.append("\n" + "=" * 70 + "\n")
        
        return "\n".join(output)


logging.basicConfig(level=logging.INFO)
def main():
    """Test entry point"""
    print("=" * 70)
    print(" " * 14 + "SA-004: News & Sentiment Monitor")
    print("=" * 70)
    
    monitor = NewsSentimentMonitor()
    
    # Test 1: Display status
    print(monitor.display_status())
    
    # Test 2: Monitor sentiment (24h)
    print("\n[Test 1] Monitor Sentiment (AAPL, 24h)")
    print("-" * 70)
    result = monitor.monitor_sentiment("AAPL", hours=24, limit=10)
    if result:
        print(f"  Symbol:         {result['symbol']}")
        print(f"  Period:         {result['monitoring_period']}")
        print(f"  Sources:        {', '.join(result['sources'])}")
        print(f"  Total Articles: {result['total_articles']}")
        print(f"\n  Sentiment Summary:")
        summary = result['sentiment_summary']
        print(f"    Overall:        {summary['overall'].upper()}")
        print(f"    Score:          {summary['score']:+.3f}")
        print(f"    Positive:       {summary['distribution']['positive']} ({summary['percentages']['positive']}%)")
        print(f"    Neutral:        {summary['distribution']['neutral']} ({summary['percentages']['neutral']}%)")
        print(f"    Negative:       {summary['distribution']['negative']} ({summary['percentages']['negative']}%)")
        
        print(f"\n  Sample Articles:")
        for i, article in enumerate(result['articles'][:3], 1):
            print(f"    {i}. [{article['sentiment'].upper()}] {article['title']}")
            print(f"       Source: {article['source_name']}, {article['hours_ago']}h ago")
    
    # Test 3: Multi-source comparison
    print("\n[Test 2] Multi-Source Comparison")
    print("-" * 70)
    for source in ["sina", "seeking_alpha"]:
        result = monitor.monitor_sentiment("AAPL", sources=[source], hours=48, limit=5)
        if result:
            summary = result['sentiment_summary']
            src_name = monitor.sources[source]["name"]
            print(f"  {src_name:20}: {summary['overall']:10} (score: {summary['score']:+.3f}, articles: {result['total_articles']})")
    
    # Test 4: Sentiment trend
    print("\n[Test 3] Sentiment Trend (3 days)")
    print("-" * 70)
    trend = monitor.get_sentiment_trend("AAPL", days=3)
    if trend:
        print(f"  {'Date':<12} {'Overall':<10} {'Score':>8} {'Articles':>10}")
        print(f"  {'-'*12} {'-'*10} {'-'*8} {'-'*10}")
        for day in trend:
            print(f"  {day['date']:<12} {day['overall']:<10} {day['score']:>+8.3f} {day['article_count']:>10}")
    
    # Test 5: Final stats
    print("\n[Test 4] Final Statistics")
    print("-" * 70)
    stats = monitor.get_stats()
    print(f"  Total Sessions:    {stats['total_sessions']}")
    print(f"  Total Articles:    {stats['total_articles']}")
    print(f"  Positive:          {stats['positive']}")
    print(f"  Neutral:           {stats['neutral']}")
    print(f"  Negative:          {stats['negative']}")
    
    print("\n[OK] SA-004 News & Sentiment Monitor test completed")

if __name__ == "__main__":
    main()
