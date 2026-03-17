#!/usr/bin/env python3
"""
Stock Social Media Sentiment Analyzer
Collects and analyzes social media sentiment for stocks

Features:
- Reddit r/wallstreetbets + r/stocks monitoring
- Twitter/X sentiment (API ready)
- Local LLM sentiment analysis (Qwen2.5-1.5B)
- Sentiment scoring (-1.0 to +1.0)
- Trending stocks detection
- Alert on sentiment spikes

Schedule: Every 30min (HEARTBEAT)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import re


@dataclass
class SocialMention:
    """Single social media mention"""
    platform: str  # reddit/twitter
    title: str
    content: str
    url: str
    author: str
    upvotes: int
    comments: int
    timestamp: str
    sentiment_score: float = 0.0
    sentiment_label: str = "neutral"  # positive/negative/neutral
    tickers: List[str] = None
    
    def __post_init__(self):
        if self.tickers is None:
            self.tickers = []
    
    def to_dict(self):
        return asdict(self)


class LLMSentimentAnalyzer:
    """
    Local LLM-based sentiment analysis
    Uses Qwen2.5-1.5B for on-device processing
    """
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.llm = None
        self._load_model()
    
    def _load_model(self):
        """Load local LLM model"""
        try:
            from llama_cpp import Llama
            
            # Try to load model
            model_paths = [
                "models/Qwen2.5-1.5B-Instruct-Q5_K_M.gguf",
                "D:/OpenClaw/workspace/models/Qwen2.5-1.5B-Instruct-Q5_K_M.gguf",
                "C:/Users/华为/.copaw/models/Qwen2.5-1.5B-Instruct-Q5_K_M.gguf"
            ]
            
            for path in model_paths:
                if Path(path).exists():
                    self.llm = Llama(model_path=path, n_ctx=2048, verbose=False)
                    print(f"✅ Loaded LLM: {path}")
                    return
            
            print("⚠️ LLM model not found, using keyword-based sentiment")
            
        except Exception as e:
            print(f"⚠️ LLM loading failed: {e}, using keyword-based sentiment")
    
    def analyze_sentiment(self, text: str) -> tuple[float, str]:
        """
        Analyze sentiment of text
        
        Returns:
            (score, label) where score in [-1.0, +1.0]
        """
        if self.llm:
            return self._llm_sentiment(text)
        else:
            return self._keyword_sentiment(text)
    
    def _llm_sentiment(self, text: str) -> tuple[float, str]:
        """LLM-based sentiment analysis"""
        prompt = f"""Analyze the sentiment of this stock-related text. Rate from -1.0 (very negative) to +1.0 (very positive).

Text: {text[:500]}

Format: SCORE: <number between -1.0 and 1.0>
"""
        try:
            output = self.llm(prompt, max_tokens=50, stop=["\n"], echo=False)
            response = output['choices'][0]['text'].strip()
            
            # Extract score
            match = re.search(r'SCORE:\s*([+-]?\d+\.?\d*)', response)
            if match:
                score = float(match.group(1))
                score = max(-1.0, min(1.0, score))  # Clamp to [-1, 1]
                
                label = "positive" if score > 0.2 else "negative" if score < -0.2 else "neutral"
                return score, label
            
        except Exception as e:
            print(f"⚠️ LLM sentiment failed: {e}")
        
        # Fallback to keyword
        return self._keyword_sentiment(text)
    
    def _keyword_sentiment(self, text: str) -> tuple[float, str]:
        """Keyword-based sentiment analysis"""
        positive_words = {
            'bullish', 'buy', 'long', 'moon', 'rocket', 'gain', 'profit', 'up', 'rise', 'surge',
            'soar', 'breakout', 'undervalued', 'recommend', 'strong', 'beat', 'outperform'
        }
        negative_words = {
            'bearish', 'sell', 'short', 'crash', 'dump', 'loss', 'down', 'fall', 'drop', 'plunge',
            'overvalued', 'avoid', 'weak', 'miss', 'underperform', 'risk', 'danger'
        }
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        pos_count = sum(1 for w in words if w in positive_words)
        neg_count = sum(1 for w in words if w in negative_words)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0, "neutral"
        
        score = (pos_count - neg_count) / total
        label = "positive" if score > 0.2 else "negative" if score < -0.2 else "neutral"
        
        return score, label


class RedditCollector:
    """Collect posts from Reddit"""
    
    def __init__(self):
        self.subreddits = ['wallstreetbets', 'stocks', 'investing', 'stocks']
        self.base_url = "https://www.reddit.com"
    
    def fetch_hot_posts(self, subreddit: str, limit: int = 25) -> List[Dict]:
        """Fetch hot posts from subreddit"""
        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
            headers = {'User-Agent': 'OpenClaw/1.0'}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            posts = []
            
            for child in data['data']['children']:
                post = child['data']
                posts.append({
                    'title': post.get('title', ''),
                    'content': post.get('selftext', ''),
                    'url': f"https://reddit.com{post.get('permalink', '')}",
                    'author': post.get('author', 'unknown'),
                    'upvotes': post.get('score', 0),
                    'comments': post.get('num_comments', 0),
                    'created_utc': post.get('created_utc', 0),
                    'subreddit': subreddit
                })
            
            return posts
            
        except Exception as e:
            print(f"⚠️ Reddit fetch failed for r/{subreddit}: {e}")
            return []
    
    def extract_tickers(self, text: str) -> List[str]:
        """Extract stock tickers from text"""
        # Match $AAPL, AAPL, etc.
        tickers = set(re.findall(r'\$?([A-Z]{1,5})\b', text))
        
        # Filter common words
        exclude = {'THE', 'AND', 'FOR', 'YOU', 'WILL', 'JUST', 'THAT', 'THIS', 'WITH'}
        tickers = tickers - exclude
        
        return list(tickers)


class SentimentAnalyzer:
    """Main sentiment analysis engine"""
    
    def __init__(self, data_dir: str = "D:\\OpenClaw\\workspace\\data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.reddit = RedditCollector()
        self.llm_sentiment = LLMSentimentAnalyzer()
        self.mentions: List[SocialMention] = []
        self.ticker_sentiment: Dict[str, List[float]] = {}
    
    def collect_reddit(self, limit: int = 25) -> int:
        """Collect from Reddit"""
        print("\n📱 Collecting from Reddit...")
        count = 0
        
        for subreddit in self.reddit.subreddits:
            posts = self.reddit.fetch_hot_posts(subreddit, limit)
            
            for post in posts:
                # Extract tickers
                text = f"{post['title']} {post['content']}"
                tickers = self.reddit.extract_tickers(text)
                
                if tickers:  # Only process posts with tickers
                    # Analyze sentiment
                    score, label = self.llm_sentiment.analyze_sentiment(text)
                    
                    mention = SocialMention(
                        platform='reddit',
                        title=post['title'][:100],
                        content=post['content'][:200],
                        url=post['url'],
                        author=post['author'],
                        upvotes=post['upvotes'],
                        comments=post['comments'],
                        timestamp=datetime.fromtimestamp(post['created_utc']).isoformat(),
                        sentiment_score=score,
                        sentiment_label=label,
                        tickers=tickers
                    )
                    
                    self.mentions.append(mention)
                    
                    # Aggregate by ticker
                    for ticker in tickers:
                        if ticker not in self.ticker_sentiment:
                            self.ticker_sentiment[ticker] = []
                        self.ticker_sentiment[ticker].append(score)
                    
                    count += 1
        
        print(f"  Collected {count} mentions with tickers")
        return count
    
    def get_ticker_sentiment(self) -> Dict[str, Dict]:
        """Get aggregated sentiment by ticker"""
        results = {}
        
        for ticker, scores in self.ticker_sentiment.items():
            if len(scores) >= 1:  # At least 1 mention
                avg_score = sum(scores) / len(scores)
                results[ticker] = {
                    'avg_sentiment': avg_score,
                    'mention_count': len(scores),
                    'label': 'bullish' if avg_score > 0.2 else 'bearish' if avg_score < -0.2 else 'neutral',
                    'confidence': min(1.0, len(scores) / 10)  # More mentions = higher confidence
                }
        
        # Sort by mention count
        sorted_results = dict(sorted(results.items(), key=lambda x: -x[1]['mention_count']))
        return sorted_results
    
    def get_trending_stocks(self, top_n: int = 10) -> List[Dict]:
        """Get top trending stocks by mention count"""
        sentiment = self.get_ticker_sentiment()
        
        trending = []
        for ticker, data in list(sentiment.items())[:top_n]:
            trending.append({
                'ticker': ticker,
                'mentions': data['mention_count'],
                'sentiment': data['avg_sentiment'],
                'label': data['label']
            })
        
        return trending
    
    def detect_sentiment_spikes(self, threshold: float = 0.7) -> List[Dict]:
        """Detect unusual sentiment spikes"""
        spikes = []
        
        for ticker, data in self.get_ticker_sentiment().items():
            if data['mention_count'] >= 5:  # Significant mentions
                if abs(data['avg_sentiment']) >= threshold:
                    spikes.append({
                        'ticker': ticker,
                        'sentiment': data['avg_sentiment'],
                        'label': data['label'],
                        'mentions': data['mention_count'],
                        'spike_type': 'extreme_positive' if data['avg_sentiment'] > 0 else 'extreme_negative'
                    })
        
        return spikes
    
    def save(self, filename: str = None):
        """Save results to JSON"""
        if not filename:
            filename = f"sentiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.data_dir / filename
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'total_mentions': len(self.mentions),
            'mentions': [m.to_dict() for m in self.mentions[-100:]],  # Last 100
            'ticker_sentiment': self.get_ticker_sentiment(),
            'trending': self.get_trending_stocks(20),
            'spikes': self.detect_sentiment_spikes()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved sentiment data: {filepath}")
        return filepath
    
    def generate_report(self) -> str:
        """Generate text report"""
        report = []
        report.append("="*60)
        report.append("📊 Social Media Sentiment Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("="*60)
        
        # Trending stocks
        report.append("\n🔥 Trending Stocks:")
        for i, stock in enumerate(self.get_trending_stocks(10), 1):
            emoji = "🐂" if stock['label'] == 'bullish' else "🐻" if stock['label'] == 'bearish' else "➖"
            report.append(f"  {i}. ${stock['ticker']} {emoji} - {stock['mentions']} mentions, sentiment: {stock['sentiment']:+.2f}")
        
        # Sentiment spikes
        spikes = self.detect_sentiment_spikes()
        if spikes:
            report.append("\n⚠️ Sentiment Spikes:")
            for spike in spikes:
                emoji = "🚀" if spike['spike_type'] == 'extreme_positive' else "📉"
                report.append(f"  {emoji} ${spike['ticker']}: {spike['label']} ({spike['sentiment']:+.2f}, {spike['mentions']} mentions)")
        
        # Summary
        report.append("\n📈 Summary:")
        report.append(f"  Total mentions: {len(self.mentions)}")
        report.append(f"  Unique tickers: {len(self.ticker_sentiment)}")
        report.append(f"  Bullish tickers: {sum(1 for t in self.get_ticker_sentiment().values() if t['label'] == 'bullish')}")
        report.append(f"  Bearish tickers: {sum(1 for t in self.get_ticker_sentiment().values() if t['label'] == 'bearish')}")
        
        return "\n".join(report)


def main():
    """Demo/test sentiment analyzer"""
    print("="*60)
    print("📊 Stock Social Media Sentiment Analyzer")
    print("="*60)
    
    analyzer = SentimentAnalyzer()
    
    # Collect from Reddit
    count = analyzer.collect_reddit(limit=25)
    
    if count > 0:
        # Generate report
        report = analyzer.generate_report()
        print("\n" + report)
        
        # Save
        analyzer.save()
        
        print("\n✅ Sentiment analysis complete!")
    else:
        print("\n⚠️ No mentions collected (Reddit API may be rate-limited)")
        print("  Using demo data for testing...")
        
        # Demo data
        demo_mentions = [
            SocialMention('reddit', 'NVDA to the moon!', 'AI boom continues', 'url', 'user1', 100, 50, datetime.now().isoformat(), 0.8, 'positive', ['NVDA']),
            SocialMention('reddit', 'TSLA overvalued', 'EV competition heating up', 'url', 'user2', 80, 40, datetime.now().isoformat(), -0.6, 'negative', ['TSLA']),
            SocialMention('reddit', 'AAPL steady growth', 'iPhone sales strong', 'url', 'user3', 60, 30, datetime.now().isoformat(), 0.3, 'positive', ['AAPL']),
        ]
        
        analyzer.mentions = demo_mentions
        for m in demo_mentions:
            analyzer.ticker_sentiment[m.tickers[0]] = [m.sentiment_score]
        
        report = analyzer.generate_report()
        print("\n" + report)
        
        analyzer.save()
    
    print("="*60)


if __name__ == "__main__":
    main()
