#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Integration Layer - Distributed caching and data management

Features:
- Redis connection management
- Distributed caching
- Pub/Sub messaging
- Data structures (hashes, lists, sets, sorted sets)
- TTL management
- Connection pooling
- Failover support
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Try to import redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️  Redis library not installed. Install with: pip install redis")

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
CONFIG_FILE = WORKSPACE / '30-scripts-tools' / 'config' / 'redis_config.json'

class RedisConfig:
    """Redis configuration management"""
    
    DEFAULT_CONFIG = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'password': None,
        'max_connections': 10,
        'socket_timeout': 5,
        'socket_connect_timeout': 5,
        'retry_on_timeout': True,
        'decode_responses': True,
        'encoding': 'utf-8',
    }
    
    def __init__(self, config_file: Path = None):
        self.config_file = config_file or CONFIG_FILE
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load Redis configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return {**self.DEFAULT_CONFIG, **json.load(f)}
        else:
            # Create default config
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.DEFAULT_CONFIG, f, indent=2)
            return self.DEFAULT_CONFIG
    
    def save_config(self, config: Dict):
        """Save Redis configuration"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    
    def get_connection_params(self) -> Dict:
        """Get connection parameters"""
        return self.config.copy()


class RedisCache:
    """
    Redis distributed cache layer
    
    Features:
    - Automatic serialization
    - TTL management
    - Key namespacing
    - Connection pooling
    """
    
    def __init__(self, namespace: str = 'workspace', config: RedisConfig = None):
        if not REDIS_AVAILABLE:
            self.client = None
            return
        
        self.namespace = namespace
        self.config = config or RedisConfig()
        
        try:
            pool = redis.ConnectionPool(**self.config.get_connection_params())
            self.client = redis.Redis(connection_pool=pool)
            self._test_connection()
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e}")
            self.client = None
    
    def _test_connection(self):
        """Test Redis connection"""
        if self.client:
            self.client.ping()
    
    def _make_key(self, key: str) -> str:
        """Create namespaced key"""
        return f"{self.namespace}:{key}"
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Set cache value
        
        Args:
            key: Cache key
            value: Value to cache (auto-serialized)
            ttl: Time to live in seconds
        
        Returns:
            Success status
        """
        if not self.client:
            return False
        
        try:
            serialized = json.dumps(value) if not isinstance(value, str) else value
            namespaced_key = self._make_key(key)
            
            if ttl:
                return bool(self.client.setex(namespaced_key, ttl, serialized))
            else:
                return bool(self.client.set(namespaced_key, serialized))
        except Exception as e:
            print(f"❌ Cache set error: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get cache value
        
        Args:
            key: Cache key
            default: Default value if not found
        
        Returns:
            Cached value or default
        """
        if not self.client:
            return default
        
        try:
            namespaced_key = self._make_key(key)
            value = self.client.get(namespaced_key)
            
            if value is None:
                return default
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            print(f"❌ Cache get error: {e}")
            return default
    
    def delete(self, key: str) -> bool:
        """Delete cache key"""
        if not self.client:
            return False
        
        try:
            namespaced_key = self._make_key(key)
            return bool(self.client.delete(namespaced_key))
        except Exception as e:
            print(f"❌ Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.client:
            return False
        
        try:
            namespaced_key = self._make_key(key)
            return bool(self.client.exists(namespaced_key))
        except Exception as e:
            print(f"❌ Cache exists error: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """Get TTL for key"""
        if not self.client:
            return -1
        
        try:
            namespaced_key = self._make_key(key)
            return self.client.ttl(namespaced_key)
        except Exception as e:
            print(f"❌ Cache TTL error: {e}")
            return -1
    
    def clear_namespace(self) -> bool:
        """Clear all keys in namespace"""
        if not self.client:
            return False
        
        try:
            pattern = self._make_key('*')
            keys = self.client.keys(pattern)
            if keys:
                return bool(self.client.delete(*keys))
            return True
        except Exception as e:
            print(f"❌ Clear namespace error: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        if not self.client:
            return {
                'connected': False,
                'namespace': self.namespace,
            }
        
        try:
            info = self.client.info('stats')
            keys_count = self.client.dbsize()
            
            return {
                'connected': True,
                'namespace': self.namespace,
                'keys_count': keys_count,
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'hit_rate': info.get('keyspace_hits', 0) / max(1, info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0)),
            }
        except Exception as e:
            return {
                'connected': False,
                'namespace': self.namespace,
                'error': str(e),
            }


class RedisPubSub:
    """Redis Pub/Sub messaging"""
    
    def __init__(self, channel: str, config: RedisConfig = None):
        if not REDIS_AVAILABLE:
            self.client = None
            return
        
        self.channel = channel
        self.config = config or RedisConfig()
        
        try:
            self.client = redis.Redis(**self.config.get_connection_params())
        except Exception as e:
            print(f"⚠️  Pub/Sub connection failed: {e}")
            self.client = None
    
    def publish(self, message: Dict) -> int:
        """Publish message to channel"""
        if not self.client:
            return 0
        
        try:
            serialized = json.dumps(message)
            return self.client.publish(self.channel, serialized)
        except Exception as e:
            print(f"❌ Publish error: {e}")
            return 0
    
    def subscribe(self, callback=None):
        """Subscribe to channel"""
        if not self.client:
            return
        
        try:
            pubsub = self.client.pubsub()
            pubsub.subscribe(self.channel)
            
            if callback:
                for message in pubsub.listen():
                    if message['type'] == 'message':
                        try:
                            data = json.loads(message['data'])
                        except:
                            data = message['data']
                        callback(data)
            else:
                return pubsub
        except Exception as e:
            print(f"❌ Subscribe error: {e}")


class RedisDataManager:
    """
    Redis data structure manager
    
    Features:
    - Hash operations
    - List operations
    - Set operations
    - Sorted set operations
    """
    
    def __init__(self, namespace: str = 'workspace', config: RedisConfig = None):
        if not REDIS_AVAILABLE:
            self.client = None
            return
        
        self.namespace = namespace
        self.config = config or RedisConfig()
        
        try:
            self.client = redis.Redis(**self.config.get_connection_params())
        except Exception as e:
            print(f"⚠️  Data manager connection failed: {e}")
            self.client = None
    
    def _make_key(self, key: str) -> str:
        """Create namespaced key"""
        return f"{self.namespace}:{key}"
    
    # Hash operations
    def hset(self, hash_name: str, key: str, value: Any) -> bool:
        """Set hash field"""
        if not self.client:
            return False
        
        try:
            namespaced_key = self._make_key(hash_name)
            serialized = json.dumps(value) if not isinstance(value, str) else value
            return bool(self.client.hset(namespaced_key, key, serialized))
        except Exception as e:
            print(f"❌ HSET error: {e}")
            return False
    
    def hget(self, hash_name: str, key: str, default: Any = None) -> Any:
        """Get hash field"""
        if not self.client:
            return default
        
        try:
            namespaced_key = self._make_key(hash_name)
            value = self.client.hget(namespaced_key, key)
            
            if value is None:
                return default
            
            try:
                return json.loads(value)
            except:
                return value
        except Exception as e:
            print(f"❌ HGET error: {e}")
            return default
    
    def hgetall(self, hash_name: str) -> Dict:
        """Get all hash fields"""
        if not self.client:
            return {}
        
        try:
            namespaced_key = self._make_key(hash_name)
            data = self.client.hgetall(namespaced_key)
            
            # Deserialize values
            return {
                k: (json.loads(v) if isinstance(v, str) else v)
                for k, v in data.items()
            }
        except Exception as e:
            print(f"❌ HGETALL error: {e}")
            return {}
    
    # List operations
    def lpush(self, list_name: str, *values) -> int:
        """Push to list left"""
        if not self.client:
            return 0
        
        try:
            namespaced_key = self._make_key(list_name)
            serialized = [json.dumps(v) if not isinstance(v, str) else v for v in values]
            return self.client.lpush(namespaced_key, *serialized)
        except Exception as e:
            print(f"❌ LPUSH error: {e}")
            return 0
    
    def rpush(self, list_name: str, *values) -> int:
        """Push to list right"""
        if not self.client:
            return 0
        
        try:
            namespaced_key = self._make_key(list_name)
            serialized = [json.dumps(v) if not isinstance(v, str) else v for v in values]
            return self.client.rpush(namespaced_key, *serialized)
        except Exception as e:
            print(f"❌ RPUSH error: {e}")
            return 0
    
    def lrange(self, list_name: str, start: int = 0, end: int = -1) -> List:
        """Get list range"""
        if not self.client:
            return []
        
        try:
            namespaced_key = self._make_key(list_name)
            values = self.client.lrange(namespaced_key, start, end)
            
            # Deserialize
            return [
                json.loads(v) if isinstance(v, str) else v
                for v in values
            ]
        except Exception as e:
            print(f"❌ LRANGE error: {e}")
            return []
    
    # Set operations
    def sadd(self, set_name: str, *values) -> int:
        """Add to set"""
        if not self.client:
            return 0
        
        try:
            namespaced_key = self._make_key(set_name)
            serialized = [json.dumps(v) if not isinstance(v, str) else v for v in values]
            return self.client.sadd(namespaced_key, *serialized)
        except Exception as e:
            print(f"❌ SADD error: {e}")
            return 0
    
    def smembers(self, set_name: str) -> List:
        """Get set members"""
        if not self.client:
            return []
        
        try:
            namespaced_key = self._make_key(set_name)
            members = self.client.smembers(namespaced_key)
            
            # Deserialize
            return [
                json.loads(m) if isinstance(m, str) else m
                for m in members
            ]
        except Exception as e:
            print(f"❌ SMEMBERS error: {e}")
            return []
    
    # Sorted set operations
    def zadd(self, sorted_set_name: str, mapping: Dict[str, float]) -> int:
        """Add to sorted set"""
        if not self.client:
            return 0
        
        try:
            namespaced_key = self._make_key(sorted_set_name)
            return self.client.zadd(namespaced_key, mapping)
        except Exception as e:
            print(f"❌ ZADD error: {e}")
            return 0
    
    def zrange(self, sorted_set_name: str, start: int = 0, end: int = -1, with_scores: bool = False) -> List:
        """Get sorted set range"""
        if not self.client:
            return []
        
        try:
            namespaced_key = self._make_key(sorted_set_name)
            return self.client.zrange(namespaced_key, start, end, withscores=with_scores)
        except Exception as e:
            print(f"❌ ZRANGE error: {e}")
            return []


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Redis Integration Layer")
    parser.add_argument('--test', action='store_true', help='Test Redis connection')
    parser.add_argument('--stats', action='store_true', help='Show cache statistics')
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--config', action='store_true', help='Show configuration')
    args = parser.parse_args()
    
    if not REDIS_AVAILABLE:
        print("❌ Redis library not installed")
        print("💡 Install with: pip install redis")
        sys.exit(1)
    
    config = RedisConfig()
    
    if args.test:
        cache = RedisCache(config=config)
        if cache.client:
            print("\n✅ Redis connection successful!")
            stats = cache.get_stats()
            print(f"   Keys: {stats.get('keys_count', 0)}")
            print(f"   Hit rate: {stats.get('hit_rate', 0):.2%}")
        else:
            print("\n❌ Redis connection failed")
            sys.exit(1)
    
    elif args.stats:
        cache = RedisCache(config=config)
        stats = cache.get_stats()
        print("\n📊 REDIS CACHE STATISTICS")
        print("=" * 60)
        print(f"Connected: {stats.get('connected', False)}")
        print(f"Namespace: {stats.get('namespace', 'N/A')}")
        print(f"Keys count: {stats.get('keys_count', 0)}")
        print(f"Cache hits: {stats.get('hits', 0)}")
        print(f"Cache misses: {stats.get('misses', 0)}")
        print(f"Hit rate: {stats.get('hit_rate', 0):.2%}")
        print("=" * 60)
    
    elif args.demo:
        print("\n🔴 REDIS INTEGRATION DEMO")
        print("=" * 60)
        
        cache = RedisCache(config=config)
        
        if not cache.client:
            print("⚠️  Redis not available, skipping demo")
        else:
            # Test set/get
            cache.set('test_key', {'message': 'Hello Redis', 'timestamp': datetime.now().isoformat()}, ttl=60)
            value = cache.get('test_key')
            print(f"✅ Set/Get test: {value}")
            
            # Test hash
            dm = RedisDataManager(config=config)
            dm.hset('test_hash', 'field1', 'value1')
            dm.hset('test_hash', 'field2', {'nested': 'data'})
            hash_data = dm.hgetall('test_hash')
            print(f"✅ Hash test: {hash_data}")
            
            # Test list
            dm.rpush('test_list', 'item1', 'item2', 'item3')
            list_data = dm.lrange('test_list')
            print(f"✅ List test: {list_data}")
            
            # Stats
            stats = cache.get_stats()
            print(f"\n📊 Stats: {stats['keys_count']} keys, {stats['hit_rate']:.2%} hit rate")
        
        print("\n" + "=" * 60)
        print("✅ Demo complete!")
    
    elif args.config:
        print("\n⚙️  REDIS CONFIGURATION")
        print("=" * 60)
        print(f"Config file: {config.config_file}")
        print(f"Host: {config.config['host']}")
        print(f"Port: {config.config['port']}")
        print(f"DB: {config.config['db']}")
        print(f"Max connections: {config.config['max_connections']}")
        print("=" * 60)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
