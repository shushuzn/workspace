import logging
logger = logging.getLogger(__name__)

from smart_cache_001 import SmartCache
c = SmartCache()
c.set("test1", "response1")
c.set("test2", "response2")
r = c.get("test1")
print(f"Status: {r['status']}")
print(f"Hit count: {r['hit_count']}")
print("LRU test OK")