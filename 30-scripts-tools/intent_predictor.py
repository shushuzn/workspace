#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intent Predictor - LLM-based query intent prediction and pre-fetching
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
INTENT_DIR = WORKSPACE / 'data' / 'intent_predictor'
INTENT_DIR.mkdir(parents=True, exist_ok=True)

class IntentPredictor:
    """
    LLM-based Intent Predictor
    
    Features:
    - Query intent classification
    - Next query prediction
    - Document pre-fetching
    - Ollama integration (Qwen2.5:1.5b)
    - Intent history tracking
    """
    
    # Intent categories
    INTENT_CATEGORIES = [
        'information_retrieval',    # Looking for specific information
        'exploration',              # Browsing/exploring topics
        'comparison',               # Comparing concepts/items
        'problem_solving',          # Seeking solutions
        'learning',                 # Educational/learning intent
        'verification',             # Fact-checking/verification
        'navigation',               # Looking for specific location/doc
        'recommendation',           # Seeking recommendations
    ]
    
    # Topic clusters
    TOPIC_CLUSTERS = {
        'memory': ['memory', 'cache', 'retrieval', 'storage', 'optimization'],
        'security': ['security', 'protection', 'safety', 'vulnerability', 'encryption'],
        'workflow': ['workflow', 'automation', 'pipeline', 'orchestration', 'agent'],
        'ml': ['ml', 'neural', 'embedding', 'semantic', 'vector', 'learning'],
        'performance': ['performance', 'optimization', 'speed', 'efficiency', 'tuning'],
        'infrastructure': ['infrastructure', 'cloud', 'server', 'deployment', 'docker'],
    }
    
    def __init__(self, use_ollama: bool = True,
                 model: str = "qwen2.5:1.5b",
                 history_size: int = 50):
        """
        Args:
            use_ollama: Use Ollama for LLM predictions
            model: Ollama model to use
            history_size: Number of queries to track in history
        """
        self.use_ollama = use_ollama
        self.model = model
        self.history_size = history_size
        
        # Query history
        self.query_history: List[Dict] = []
        
        # Intent patterns
        self.intent_patterns: Dict[str, int] = defaultdict(int)
        
        # Pre-fetch cache
        self.prefetch_cache: Dict[str, List[str]] = {}
        
        # Statistics
        self.stats = {
            'total_predictions': 0,
            'accurate_predictions': 0,
            'prefetch_hits': 0,
            'prefetch_misses': 0,
        }
        
        # Ollama endpoint
        self.ollama_url = "http://localhost:11434/api/generate"
    
    def _classify_topic(self, query: str) -> str:
        """Classify query into topic cluster"""
        query_lower = query.lower()
        
        best_topic = 'general'
        best_score = 0
        
        for topic, keywords in self.TOPIC_CLUSTERS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > best_score:
                best_score = score
                best_topic = topic
        
        return best_topic
    
    def _predict_intent_llm(self, query: str, 
                           context: List[str] = None) -> Dict:
        """Use LLM to predict intent"""
        if not self.use_ollama:
            return self._predict_intent_rule_based(query, context)
        
        try:
            import requests
            
            # Build prompt
            context_str = ""
            if context:
                context_str = f"Previous queries: {', '.join(context[-5:])}\n\n"
            
            prompt = f"""{context_str}Current query: "{query}"

Classify the intent into one of these categories:
{', '.join(self.INTENT_CATEGORIES)}

Also predict the next likely query topic.

Respond in JSON format:
{{
    "intent": "category",
    "confidence": 0.0-1.0,
    "next_topic": "predicted topic",
    "keywords": ["keyword1", "keyword2"]
}}
"""
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('response', '')
                
                # Parse JSON from response
                try:
                    # Find JSON in response
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start >= 0 and end > start:
                        json_str = text[start:end]
                        prediction = json.loads(json_str)
                        return prediction
                except:
                    pass
            
            # Fallback to rule-based
            return self._predict_intent_rule_based(query, context)
            
        except Exception as e:
            # Fallback to rule-based
            return self._predict_intent_rule_based(query, context)
    
    def _predict_intent_rule_based(self, query: str,
                                   context: List[str] = None) -> Dict:
        """Rule-based intent prediction"""
        query_lower = query.lower()
        
        # Intent keywords
        intent_keywords = {
            'information_retrieval': ['what', 'how', 'explain', 'describe', 'define'],
            'exploration': ['explore', 'browse', 'show', 'list', 'overview'],
            'comparison': ['compare', 'vs', 'versus', 'difference', 'better'],
            'problem_solving': ['fix', 'solve', 'error', 'issue', 'problem'],
            'learning': ['learn', 'tutorial', 'guide', 'understand', 'study'],
            'verification': ['verify', 'check', 'confirm', 'validate', 'true'],
            'navigation': ['go to', 'open', 'find', 'location', 'path'],
            'recommendation': ['recommend', 'suggest', 'best', 'top', 'favorite'],
        }
        
        # Match intent
        best_intent = 'information_retrieval'
        best_score = 0
        
        for intent, keywords in intent_keywords.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > best_score:
                best_score = score
                best_intent = intent
        
        # Predict next topic based on current topic
        current_topic = self._classify_topic(query)
        next_topic = current_topic  # Default: same topic
        
        # Simple topic transition logic
        topic_transitions = {
            'memory': ['performance', 'optimization'],
            'security': ['infrastructure', 'verification'],
            'workflow': ['automation', 'ml'],
            'ml': ['performance', 'optimization'],
        }
        
        if current_topic in topic_transitions:
            next_topic = topic_transitions[current_topic][0]
        
        # Extract keywords
        import re
        keywords = re.findall(r'\b[a-zA-Z]{4,}\b', query_lower)
        keywords = [kw for kw in keywords if kw not in ['what', 'how', 'the', 'and', 'with', 'for']]
        
        return {
            'intent': best_intent,
            'confidence': min(0.9, 0.5 + best_score * 0.1),
            'next_topic': next_topic,
            'keywords': keywords[:5],
        }
    
    def predict(self, query: str, context: List[str] = None) -> Dict:
        """
        Predict intent for query
        
        Args:
            query: Current query
            context: Previous queries (optional)
        
        Returns:
            Prediction dict with intent, confidence, next_topic, keywords
        """
        # Get prediction
        prediction = self._predict_intent_llm(query, context)
        
        # Add metadata
        prediction['query'] = query
        prediction['topic'] = self._classify_topic(query)
        prediction['timestamp'] = datetime.now().isoformat()
        
        # Update history
        self.query_history.append(prediction)
        if len(self.query_history) > self.history_size:
            self.query_history = self.query_history[-self.history_size:]
        
        # Update patterns
        self.intent_patterns[prediction['intent']] += 1
        self.stats['total_predictions'] += 1
        
        return prediction
    
    def get_prefetch_queries(self, prediction: Dict) -> List[str]:
        """
        Generate prefetch queries based on prediction
        
        Args:
            prediction: Intent prediction
        
        Returns:
            List of queries to prefetch
        """
        prefetch_queries = []
        
        topic = prediction.get('next_topic', 'general')
        keywords = prediction.get('keywords', [])
        intent = prediction.get('intent', 'information_retrieval')
        
        # Generate based on intent
        if intent == 'information_retrieval':
            # Generate "how to" and "what is" queries
            for kw in keywords[:3]:
                prefetch_queries.append(f"how to {kw}")
                prefetch_queries.append(f"what is {kw}")
        
        elif intent == 'comparison':
            # Generate comparison queries
            for kw in keywords[:2]:
                prefetch_queries.append(f"{kw} vs alternative")
                prefetch_queries.append(f"{kw} best practices")
        
        elif intent == 'problem_solving':
            # Generate troubleshooting queries
            for kw in keywords[:3]:
                prefetch_queries.append(f"{kw} common issues")
                prefetch_queries.append(f"{kw} fix error")
        
        elif intent == 'learning':
            # Generate tutorial queries
            for kw in keywords[:2]:
                prefetch_queries.append(f"{kw} tutorial")
                prefetch_queries.append(f"{kw} guide for beginners")
        
        # Add topic-specific queries
        if topic in self.TOPIC_CLUSTERS:
            cluster_keywords = self.TOPIC_CLUSTERS[topic]
            for kw in cluster_keywords[:3]:
                prefetch_queries.append(f"{topic} {kw}")
        
        # Deduplicate
        prefetch_queries = list(set(prefetch_queries))
        
        return prefetch_queries[:10]  # Limit to 10
    
    def record_outcome(self, prediction: Dict, 
                      actual_next_query: str = None,
                      prefetch_hit: bool = False):
        """
        Record prediction outcome for learning
        
        Args:
            prediction: Original prediction
            actual_next_query: Actual next query (if known)
            prefetch_hit: Whether prefetch was useful
        """
        # Update stats
        if prefetch_hit:
            self.stats['prefetch_hits'] += 1
        else:
            self.stats['prefetch_misses'] += 1
        
        # Check accuracy if actual query known
        if actual_next_query:
            predicted_topic = prediction.get('next_topic', '')
            actual_topic = self._classify_topic(actual_next_query)
            
            if predicted_topic == actual_topic:
                self.stats['accurate_predictions'] += 1
    
    def get_stats(self) -> Dict:
        """Get predictor statistics"""
        total_prefetch = self.stats['prefetch_hits'] + self.stats['prefetch_misses']
        prefetch_hit_rate = (
            self.stats['prefetch_hits'] / total_prefetch * 100 
            if total_prefetch > 0 else 0
        )
        
        prediction_accuracy = (
            self.stats['accurate_predictions'] / self.stats['total_predictions'] * 100
            if self.stats['total_predictions'] > 0 else 0
        )
        
        # Intent distribution
        intent_dist = dict(self.intent_patterns)
        total = sum(intent_dist.values())
        if total > 0:
            intent_dist = {
                k: round(v / total * 100, 2) 
                for k, v in intent_dist.items()
            }
        
        return {
            'total_predictions': self.stats['total_predictions'],
            'prediction_accuracy_percent': round(prediction_accuracy, 2),
            'prefetch_hit_rate_percent': round(prefetch_hit_rate, 2),
            'prefetch_hits': self.stats['prefetch_hits'],
            'prefetch_misses': self.stats['prefetch_misses'],
            'intent_distribution': intent_dist,
            'history_size': len(self.query_history),
        }
    
    def get_recent_predictions(self, limit: int = 10) -> List[Dict]:
        """Get recent predictions"""
        return self.query_history[-limit:]
    
    def save(self, model_file: Path = None) -> Path:
        """Save predictor state"""
        if model_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            model_file = INTENT_DIR / f'intent_predictor_{timestamp}.json'
        
        data = {
            'config': {
                'use_ollama': self.use_ollama,
                'model': self.model,
                'history_size': self.history_size,
            },
            'stats': self.stats,
            'intent_patterns': dict(self.intent_patterns),
            'recent_history': self.query_history[-50:],
            'prefetch_cache': self.prefetch_cache,
            'created_at': datetime.now().isoformat(),
        }
        
        with open(model_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Intent predictor saved to: {model_file}")
        return model_file
    
    @classmethod
    def load(cls, model_file: Path) -> 'IntentPredictor':
        """Load predictor from disk"""
        with open(model_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        predictor = cls(
            use_ollama=data['config']['use_ollama'],
            model=data['config']['model'],
            history_size=data['config']['history_size']
        )
        
        predictor.stats = data['stats']
        predictor.intent_patterns = defaultdict(int, data['intent_patterns'])
        predictor.query_history = data['recent_history']
        predictor.prefetch_cache = data['prefetch_cache']
        
        print(f"✅ Intent predictor loaded from: {model_file}")
        return predictor


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Intent Predictor")
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--no-llm', action='store_true', help='Disable LLM (rule-based only)')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    args = parser.parse_args()
    
    if args.demo:
        print("\n🔮 Intent Predictor Demo")
        print("=" * 80)
        print(f"LLM Mode: {'Enabled (Ollama)' if not args.no_llm else 'Disabled (Rule-based)'}\n")
        
        # Create predictor
        predictor = IntentPredictor(use_ollama=not args.no_llm)
        
        # Sample queries with context
        print("📊 Predicting intents for sample queries:\n")
        
        queries = [
            ("what is memory optimization?", []),
            ("how to implement caching?", ["what is memory optimization?"]),
            ("security best practices", ["how to implement caching?"]),
            ("compare BM25 vs neural search", ["security best practices"]),
            ("fix cache miss issue", ["compare BM25 vs neural search"]),
        ]
        
        for query, context in queries:
            print(f"Query: '{query}'")
            
            prediction = predictor.predict(query, context)
            
            print(f"   Intent: {prediction['intent']}")
            print(f"   Confidence: {prediction['confidence']:.2%}")
            print(f"   Topic: {prediction['topic']}")
            print(f"   Next topic: {prediction['next_topic']}")
            print(f"   Keywords: {', '.join(prediction['keywords'][:3])}")
            
            # Get prefetch queries
            prefetch = predictor.get_prefetch_queries(prediction)
            if prefetch:
                print(f"   Prefetch queries: {', '.join(prefetch[:3])}")
            
            print()
        
        # Show stats
        print("\n📈 Intent Predictor Statistics:")
        stats = predictor.get_stats()
        
        print(f"   Total predictions: {stats['total_predictions']}")
        print(f"   Prediction accuracy: {stats['prediction_accuracy_percent']}%")
        print(f"   Prefetch hit rate: {stats['prefetch_hit_rate_percent']}%")
        
        print(f"\n   Intent Distribution:")
        for intent, percent in stats['intent_distribution'].items():
            print(f"      {intent}: {percent}%")
        
        # Save predictor
        predictor.save()
        
        print("\n✅ Demo complete!")
    
    elif args.stats:
        predictor = IntentPredictor()
        stats = predictor.get_stats()
        
        print("\n📈 Intent Predictor Statistics")
        print("=" * 80)
        print(f"Total predictions: {stats['total_predictions']}")
        print(f"Prediction accuracy: {stats['prediction_accuracy_percent']}%")
        print(f"Prefetch hit rate: {stats['prefetch_hit_rate_percent']}%")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
