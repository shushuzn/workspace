#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context-Aware Cache - L1++ with conversation context tracking
"""

import os
import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import OrderedDict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
CACHE_DIR = WORKSPACE / 'data' / 'context_cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class ConversationContext:
    """Track conversation context for intelligent caching"""
    
    def __init__(self, session_id: str, max_context_length: int = 10):
        self.session_id = session_id
        self.max_context_length = max_context_length
        
        # Conversation history
        self.queries: List[Dict] = []
        self.topics: List[str] = []
        self.last_query_time: datetime = datetime.now()
        
        # Topic clustering
        self.current_topic: Optional[str] = None
        self.topic_history: List[str] = []
        
        # Follow-up detection
        self.follow_up_patterns = [
            "它的", "这个", "那个", "那", "呢", "吗",
            "what about", "how about", "and", "but",
            "缺点", "优点", "问题", "为什么", "怎么"
        ]
    
    def add_query(self, query: str, response_time_ms: float, 
                  cache_hit: bool, result_count: int):
        """Add query to conversation history"""
        entry = {
            'query': query,
            'timestamp': datetime.now(),
            'response_time_ms': response_time_ms,
            'cache_hit': cache_hit,
            'result_count': result_count,
        }
        
        self.queries.append(entry)
        
        # Keep only recent queries
        if len(self.queries) > self.max_context_length:
            self.queries.pop(0)
        
        # Detect topic
        topic = self._extract_topic(query)
        if topic:
            self._update_topic(topic)
    
    def _extract_topic(self, query: str) -> Optional[str]:
        """Extract main topic from query"""
        # Simple keyword-based topic extraction
        # In production, use NLP/LLM for better extraction
        
        keywords = {
            'memory': ['memory', '缓存', '检索', '搜索', '查询'],
            'security': ['security', '安全', '漏洞', '风险', '审计'],
            'workflow': ['workflow', '工作流', '自动化', '流程'],
            'optimization': ['optimization', '优化', '性能', '加速'],
            'neural': ['neural', '神经网络', 'embedding', '向量'],
        }
        
        query_lower = query.lower()
        for topic, words in keywords.items():
            if any(word in query_lower for word in words):
                return topic
        
        return None
    
    def _update_topic(self, topic: str):
        """Update current topic tracking"""
        if self.current_topic != topic:
            # Topic changed
            if self.current_topic:
                self.topic_history.append(self.current_topic)
            self.current_topic = topic
    
    def is_follow_up(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Check if query is a follow-up to previous queries
        
        Returns:
            (is_follow_up, related_topic)
        """
        if not self.queries:
            return False, None
        
        # Check for follow-up patterns
        query_lower = query.lower()
        for pattern in self.follow_up_patterns:
            if pattern in query_lower:
                return True, self.current_topic
        
        # Check semantic similarity to recent queries
        if len(self.queries) >= 2:
            last_query = self.queries[-1]['query'].lower()
            
            # Simple overlap check (use embeddings in production)
            words1 = set(last_query.split())
            words2 = set(query_lower.split())
            overlap = len(words1 & words2)
            
            if overlap >= 2:
                return True, self.current_topic
        
        return False, self.current_topic
    
    def get_context_vector(self) -> Dict:
        """Get context vector for cache lookup"""
        return {
            'session_id': self.session_id,
            'current_topic': self.current_topic,
            'recent_topics': self.topic_history[-3:] if self.topic_history else [],
            'query_count': len(self.queries),
            'avg_response_time': sum(q['response_time_ms'] for q in self.queries) / len(self.queries) if self.queries else 0,
            'cache_hit_rate': sum(1 for q in self.queries if q['cache_hit']) / len(self.queries) * 100 if self.queries else 0,
        }
    
    def get_related_queries(self, max_results: int = 3) -> List[str]:
        """Get recent related queries"""
        if not self.queries:
            return []
        
        # Return queries from same topic
        if self.current_topic:
            topic_queries = [
                q['query'] for q in self.queries
                if self._extract_topic(q['query']) == self.current_topic
            ]
            return topic_queries[-max_results:]
        
        # Fallback: most recent queries
        return [q['query'] for q in self.queries[-max_results:]]


class ContextAwareCache:
    """
    L1++ Cache with conversation context awareness
    
    Features:
    - Context-aware lookup (not just exact match)
    - Follow-up detection and optimization
    - Topic-based clustering
    - Session persistence
    - Smart eviction based on context
    """
    
    def __init__(self, max_size: int = 100, 
                 session_ttl: int = 3600):
        self.max_size = max_size
        self.session_ttl = session_ttl
        
        # Session management
        self.sessions: Dict[str, ConversationContext] = {}
        
        # Cache: key → {value, context, timestamp, access_count}
        self.cache: OrderedDict = OrderedDict()
        self.metadata: Dict[str, Dict] = {}
        
        # Statistics
        self.stats = {
            'total_queries': 0,
            'context_hits': 0,
            'exact_hits': 0,
            'misses': 0,
            'follow_up_queries': 0,
        }
        
        # Load persisted sessions
        self._load_sessions()
    
    def _get_session(self, session_id: str) -> ConversationContext:
        """Get or create session context"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationContext(session_id)
        
        return self.sessions[session_id]
    
    def _load_sessions(self):
        """Load persisted sessions from disk"""
        session_file = CACHE_DIR / 'sessions.json'
        
        if session_file.exists():
            try:
                import json
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Restore recent sessions
                for session_id, session_data in data.items():
                    ctx = ConversationContext(session_id)
                    ctx.current_topic = session_data.get('current_topic')
                    ctx.topic_history = session_data.get('topic_history', [])
                    self.sessions[session_id] = ctx
                
                print(f"✅ Loaded {len(self.sessions)} sessions")
            except Exception as e:
                print(f"⚠️  Failed to load sessions: {e}")
    
    def _save_sessions(self):
        """Save sessions to disk"""
        session_file = CACHE_DIR / 'sessions.json'
        
        try:
            import json
            data = {}
            for session_id, ctx in self.sessions.items():
                data[session_id] = {
                    'current_topic': ctx.current_topic,
                    'topic_history': ctx.topic_history,
                    'query_count': len(ctx.queries),
                }
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Failed to save sessions: {e}")
    
    def _generate_cache_key(self, query: str, context: Dict = None) -> str:
        """Generate cache key with optional context"""
        if context and context.get('current_topic'):
            # Include topic in key for context-aware caching
            key_str = f"{context['current_topic']}:{query}"
        else:
            key_str = query
        
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, query: str, session_id: str = "default",
            use_context: bool = True) -> Optional[Any]:
        """
        Get value with context awareness
        
        Args:
            query: Search query
            session_id: Session identifier
            use_context: Use context for lookup
        
        Returns:
            Cached value or None
        """
        start_time = time.time()
        self.stats['total_queries'] += 1
        
        session = self._get_session(session_id)
        context = session.get_context_vector()
        
        # Check if this is a follow-up query
        is_follow_up, topic = session.is_follow_up(query)
        
        if is_follow_up:
            self.stats['follow_up_queries'] += 1
        
        # Exact match
        exact_key = hashlib.md5(query.encode()).hexdigest()
        if exact_key in self.cache:
            entry = self.cache[exact_key]
            
            if not self._is_expired(entry):
                # Update access count
                entry['access_count'] += 1
                self.cache.move_to_end(exact_key)
                
                elapsed = (time.time() - start_time) * 1000
                session.add_query(query, elapsed, True, 1)
                
                self.stats['exact_hits'] += 1
                return entry['value']
        
        # Context-aware match
        if use_context and is_follow_up and topic:
            context_key = self._generate_cache_key(query, {'current_topic': topic})
            
            if context_key in self.cache:
                entry = self.cache[context_key]
                
                if not self._is_expired(entry):
                    entry['access_count'] += 1
                    self.cache.move_to_end(context_key)
                    
                    elapsed = (time.time() - start_time) * 1000
                    session.add_query(query, elapsed, True, 1)
                    
                    self.stats['context_hits'] += 1
                    return entry['value']
        
        # Cache miss
        elapsed = (time.time() - start_time) * 1000
        session.add_query(query, elapsed, False, 0)
        
        self.stats['misses'] += 1
        return None
    
    def put(self, query: str, value: Any, 
            session_id: str = "default",
            use_context: bool = True,
            ttl: int = 3600):
        """
        Put value in cache with context
        
        Args:
            query: Search query
            value: Value to cache
            session_id: Session identifier
            use_context: Use context for key generation
            ttl: Time to live in seconds
        """
        session = self._get_session(session_id)
        context = session.get_context_vector()
        
        # Generate key (with or without context)
        if use_context and context.get('current_topic'):
            key = self._generate_cache_key(query, context)
        else:
            key = hashlib.md5(query.encode()).hexdigest()
        
        # Evict if needed
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        # Store in cache
        self.cache[key] = {
            'value': value,
            'query': query,
            'topic': context.get('current_topic'),
            'created_at': datetime.now(),
            'ttl': ttl,
            'access_count': 1,
        }
        
        self.cache.move_to_end(key)
        
        # Store metadata
        self.metadata[key] = {
            'query': query,
            'topic': context.get('current_topic'),
            'session_id': session_id,
        }
    
    def _is_expired(self, entry: Dict) -> bool:
        """Check if cache entry is expired"""
        if 'ttl' not in entry:
            return False
        
        expiry = entry['created_at'] + timedelta(seconds=entry['ttl'])
        return datetime.now() > expiry
    
    def _evict_oldest(self):
        """Evict oldest entry"""
        if self.cache:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            
            if oldest_key in self.metadata:
                del self.metadata[oldest_key]
    
    def get_context_stats(self, session_id: str = "default") -> Dict:
        """Get context statistics for session"""
        session = self._get_session(session_id)
        context = session.get_context_vector()
        
        total = self.stats['total_queries']
        hit_rate = (
            (self.stats['exact_hits'] + self.stats['context_hits']) / total * 100
        ) if total > 0 else 0
        
        return {
            'session_id': session_id,
            'current_topic': context['current_topic'],
            'recent_topics': context['recent_topics'],
            'query_count': context['query_count'],
            'avg_response_time_ms': round(context['avg_response_time'], 2),
            'cache_hit_rate': round(context['cache_hit_rate'], 2),
            'total_queries': total,
            'exact_hits': self.stats['exact_hits'],
            'context_hits': self.stats['context_hits'],
            'follow_up_queries': self.stats['follow_up_queries'],
            'misses': self.stats['misses'],
            'overall_hit_rate': round(hit_rate, 2),
            'cache_size': len(self.cache),
        }
    
    def get_related_results(self, session_id: str = "default") -> List[str]:
        """Get related queries from current session"""
        session = self._get_session(session_id)
        return session.get_related_queries()
    
    def clear(self):
        """Clear all cache and sessions"""
        self.cache.clear()
        self.metadata.clear()
        self.sessions.clear()
        
        print("✅ Context-aware cache cleared")
    
    def export_stats(self, output_file: Path = None) -> Path:
        """Export statistics to JSON"""
        if output_file is None:
            output_file = CACHE_DIR / 'context_cache_stats.json'
        
        import json
        data = {
            'stats': {
                **self.stats,
                'cache_size': len(self.cache),
                'session_count': len(self.sessions),
            },
            'timestamp': datetime.now().isoformat(),
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Stats exported to: {output_file}")
        return output_file
    
    def save(self):
        """Persist sessions to disk"""
        self._save_sessions()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Context-Aware Cache")
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    parser.add_argument('--clear', action='store_true', help='Clear cache')
    args = parser.parse_args()
    
    cache = ContextAwareCache(max_size=100)
    
    if args.demo:
        print("\n🧠 Context-Aware Cache Demo")
        print("=" * 80)
        
        session_id = "demo_session"
        
        # Simulate conversation
        print("\n💬 Simulating conversation...\n")
        
        queries = [
            "memory optimization",
            "memory optimization techniques",  # Follow-up
            "what about security?",  # Topic change
            "security vulnerabilities",  # Follow-up
            "how to fix them?",  # Follow-up (pronoun reference)
            "workflow automation",  # New topic
        ]
        
        for i, query in enumerate(queries, 1):
            # Check cache
            result = cache.get(query, session_id)
            
            if result is None:
                # Cache miss - simulate result
                result = f"Results for: {query}"
                cache.put(query, result, session_id)
                print(f"{i}. Query: {query}")
                print(f"   → Cache MISS (stored)")
            else:
                print(f"{i}. Query: {query}")
                print(f"   → Cache HIT: {result}")
            
            # Check if follow-up
            session = cache._get_session(session_id)
            is_follow_up, topic = session.is_follow_up(query)
            
            if is_follow_up:
                print(f"   → Follow-up detected (topic: {topic})")
            
            print()
        
        # Show stats
        print("\n📊 Context Statistics:")
        stats = cache.get_context_stats(session_id)
        
        print(f"   Session ID: {stats['session_id']}")
        print(f"   Current topic: {stats['current_topic']}")
        print(f"   Recent topics: {stats['recent_topics']}")
        print(f"   Query count: {stats['query_count']}")
        print(f"   Cache hit rate: {stats['overall_hit_rate']}%")
        print(f"   Follow-up queries: {stats['follow_up_queries']}")
        print(f"   Exact hits: {stats['exact_hits']}")
        print(f"   Context hits: {stats['context_hits']}")
        print(f"   Misses: {stats['misses']}")
        
        # Save sessions
        cache.save()
        
        print("\n✅ Demo complete!")
    
    elif args.stats:
        stats = cache.get_context_stats()
        print("\n📊 Context-Aware Cache Statistics")
        print("=" * 80)
        for key, val in stats.items():
            print(f"   {key}: {val}")
    
    elif args.clear:
        cache.clear()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
