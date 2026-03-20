#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-030 情绪分析器
【Phase 6 - AI 增强】

功能:
  - 新闻情绪分析
  - 社交媒体情绪
  - 舆情监控
  - 情绪指标计算

依赖: requests, beautifulsoup4 (可选)
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime
import random

# 配置
SENTIMENT_DIR = Path("60-DATA/stock_030")
CONFIG_FILE = Path("30-scripts-tools/sa_030_config.json")


class SentimentAnalyzer:
    """情绪分析器"""
    
    def __init__(self):
        self.sentiment_dir = SENTIMENT_DIR
        self.config = self._load_config()
        
        self.sentiment_dir.mkdir(parents=True, exist_ok=True)
        
        self.history_file = self.sentiment_dir / "sentiment_history.json"
        self.news_cache = self.sentiment_dir / "news_cache.json"
    
    def _load_config(self) -> dict:
        default = {
            "demo_mode": True,
            "news_api_key": os.environ.get("NEWS_API_KEY", ""),
            "sentiment_threshold": 0.3
        }
        
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return {**default, **json.load(f)}
            except:
                return default
        return default
    
    def _generate_demo_news(self, symbol: str) -> list:
        """生成模拟新闻数据"""
        random.seed(hash(symbol) % 10000)
        
        news_templates = [
            {"title": f"{symbol} 发布 Q4 财报，营收超预期", "sentiment": 0.8},
            {"title": f"分析师上调 {symbol} 目标价", "sentiment": 0.7},
            {"title": f"{symbol} 获得大额订单", "sentiment": 0.9},
            {"title": f"{symbol} 面临监管调查", "sentiment": -0.7},
            {"title": f"{symbol} CEO 辞职", "sentiment": -0.8},
            {"title": f"{symbol} 产品销量下滑", "sentiment": -0.6},
            {"title": f"市场看好 {symbol} 前景", "sentiment": 0.6},
            {"title": f"{symbol} 宣布回购计划", "sentiment": 0.5},
            {"title": f"竞争加剧影响 {symbol}", "sentiment": -0.4},
            {"title": f"{symbol} 创新技术获突破", "sentiment": 0.7}
        ]
        
        # 随机选3-5条新闻
        count = random.randint(3, 5)
        selected = random.sample(news_templates, count)
        
        news = []
        for i, n in enumerate(selected):
            news.append({
                "id": f"news_{i+1}",
                "title": n["title"],
                "sentiment": n["sentiment"],
                "source": random.choice(["Reuters", "Bloomberg", "WSJ", "CNBC"]),
                "timestamp": datetime.now().isoformat()
            })
        
        return news
    
    def _analyze_sentiment(self, news: list) -> dict:
        """分析情绪"""
        if not news:
            return {
                "score": 0,
                "label": "NEUTRAL",
                "confidence": 0
            }
        
        scores = [n["sentiment"] for n in news]
        avg_score = sum(scores) / len(scores)
        
        # 置信度基于新闻数量
        confidence = min(0.5 + len(news) * 0.1, 0.95)
        
        # 情绪标签
        if avg_score > 0.3:
            label = "POSITIVE"
        elif avg_score < -0.3:
            label = "NEGATIVE"
        else:
            label = "NEUTRAL"
        
        return {
            "score": round(avg_score, 2),
            "label": label,
            "confidence": round(confidence, 2),
            "news_count": len(news)
        }
    
    def analyze(self, symbol: str) -> dict:
        """分析情绪"""
        # 获取新闻
        news = self._generate_demo_news(symbol)
        
        # 分析
        sentiment = self._analyze_sentiment(news)
        
        result = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "news": news,
            "sentiment": sentiment,
            "score": sentiment["score"],
            "label": sentiment["label"],
            "confidence": sentiment["confidence"]
        }
        
        # 保存
        self._save_sentiment(result)
        
        return result
    
    def _save_sentiment(self, result: dict):
        """保存情绪历史"""
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except:
                pass
        
        history.append({
            "symbol": result["symbol"],
            "score": result["score"],
            "label": result["label"],
            "timestamp": result["timestamp"]
        })
        
        history = history[-100:]
        
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def get_history(self, symbol: str = None, limit: int = 20) -> dict:
        """获取情绪历史"""
        if not self.history_file.exists():
            return {"status": "error", "message": "No history"}
        
        with open(self.history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
        
        if symbol:
            history = [h for h in history if h["symbol"] == symbol]
        
        return {
            "status": "success",
            "total": len(history),
            "data": history[-limit:]
        }
    
    def batch_analyze(self, symbols: list) -> dict:
        """批量分析"""
        results = []
        
        for symbol in symbols:
            result = self.analyze(symbol)
            results.append({
                "symbol": symbol,
                "score": result["score"],
                "label": result["label"],
                "confidence": result["confidence"]
            })
        
        # 计算市场情绪
        avg_score = sum(r["score"] for r in results) / len(results)
        
        return {
            "status": "success",
            "analyzed": len(results),
            "market_sentiment": "POSITIVE" if avg_score > 0.2 else "NEGATIVE" if avg_score < -0.2 else "NEUTRAL",
            "market_score": round(avg_score, 2),
            "results": results
        }
    
    def compare(self, symbols: list) -> dict:
        """比较多个标的情绪"""
        results = []
        
        for symbol in symbols:
            result = self.analyze(symbol)
            results.append({
                "symbol": symbol,
                "score": result["score"],
                "label": result["label"],
                "confidence": result["confidence"]
            })
        
        # 排序
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "most_positive": results[0] if results else None,
            "most_negative": results[-1] if results else None,
            "comparison": results
        }
    
    def get_trending(self, direction: str = "positive") -> dict:
        """获取趋势情绪"""
        if not self.history_file.exists():
            return {"status": "error", "message": "No history"}
        
        with open(self.history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
        
        if direction == "positive":
            filtered = [h for h in history if h["score"] > 0.3]
        elif direction == "negative":
            filtered = [h for h in history if h["score"] < -0.3]
        else:
            filtered = history
        
        return {
            "status": "success",
            "direction": direction,
            "count": len(filtered),
            "data": filtered[-20:]
        }


def main():
    analyzer = SentimentAnalyzer()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--analyze":
            symbol = sys.argv[2] if len(sys.argv) > 2 else "AAPL"
            result = analyzer.analyze(symbol)
            print(json.dumps({
                "symbol": result["symbol"],
                "score": result["score"],
                "label": result["label"],
                "confidence": result["confidence"]
            }, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--batch":
            symbols = sys.argv[2].split(",") if len(sys.argv) > 2 else ["AAPL", "GOOGL", "MSFT"]
            result = analyzer.batch_analyze(symbols)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--compare":
            symbols = sys.argv[2].split(",") if len(sys.argv) > 2 else ["AAPL", "GOOGL"]
            result = analyzer.compare(symbols)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--history":
            symbol = sys.argv[2] if len(sys.argv) > 2 else None
            result = analyzer.get_history(symbol)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--trending":
            direction = sys.argv[2] if len(sys.argv) > 2 else "positive"
            result = analyzer.get_trending(direction)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("SA-030 Sentiment Analyzer")
    print("Usage:")
    print("  py sa_030_sentiment.py --analyze AAPL      # Analyze symbol")
    print("  py sa_030_sentiment.py --batch AAPL,GOOGL  # Batch analyze")
    print("  py sa_030_sentiment.py --compare AAPL,GOOGL # Compare")
    print("  py sa_030_sentiment.py --history AAPL      # History")
    print("  py sa_030_sentiment.py --trending positive # Trending")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())