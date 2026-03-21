import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SA-016: Sentiment Aggregator - Aggregate multiple sentiment sources"""

import json
from datetime import datetime
from pathlib import Path

class SentimentAggregator:
    def __init__(self, data_dir="60-DATA/stock_sentiment"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.sentiment_log = self._load_log()
    
    def _load_log(self):
        log_file = self.data_dir / "sentiment_log.json"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"version": "1.0", "analyses": [], "stats": {"total_analyses": 0}}
    
    def _save_log(self):
        with open(self.data_dir / "sentiment_log.json", 'w', encoding='utf-8') as f:
            json.dump(self.sentiment_log, f, ensure_ascii=False, indent=2)
    
    def aggregate_sentiment(self, symbol: str, sources: dict) -> dict:
        if not sources:
            return {"error": "No sentiment sources"}
        
        scores = []
        for source_name, source_data in sources.items():
            score = source_data.get("score", 0)
            weight = source_data.get("weight", 1.0)
            scores.append(score * weight)
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        if avg_score > 0.3:
            sentiment = "bullish"
        elif avg_score < -0.3:
            sentiment = "bearish"
        else:
            sentiment = "neutral"
        
        result = {
            "symbol": symbol,
            "aggregated_at": datetime.now().isoformat(),
            "sources": sources,
            "aggregate_score": round(avg_score, 3),
            "sentiment": sentiment,
            "confidence": min(1.0, abs(avg_score) * 2)
        }
        
        with open(self.data_dir / f"{symbol}_sentiment.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        self.sentiment_log["analyses"].append({"timestamp": datetime.now().isoformat(), "symbol": symbol})
        self.sentiment_log["stats"]["total_analyses"] += 1
        self.sentiment_log["analyses"] = self.sentiment_log["analyses"][-100:]
        self._save_log()
        
        return result
    
    def get_stats(self):
        return self.sentiment_log["stats"].copy()

logging.basicConfig(level=logging.INFO)
def main():
    print("=" * 70)
    print(" " * 16 + "SA-016: Sentiment Aggregator")
    print("=" * 70)
    
    agg = SentimentAggregator()
    
    sources = {
        "news": {"score": 0.6, "weight": 0.4},
        "social": {"score": 0.3, "weight": 0.3},
        "analyst": {"score": 0.5, "weight": 0.3}
    }
    
    result = agg.aggregate_sentiment("TEST", sources)
    
    print(f"\n  Symbol:          {result['symbol']}")
    print(f"  Aggregate Score: {result['aggregate_score']}")
    print(f"  Sentiment:       {result['sentiment'].upper()}")
    print(f"  Confidence:      {result['confidence']*100:.0f}%")
    print(f"\n  Sources:")
    for name, data in result["sources"].items():
        print(f"    {name}: {data['score']} (weight: {data['weight']})")
    
    print(f"\n[OK] SA-016 Sentiment Aggregator test completed")

if __name__ == "__main__":
    main()
