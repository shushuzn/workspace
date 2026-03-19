# LRU Cache Manager 使用示例

from lru_cache_manager import LRUCache, lru_cache_decorator

# 方法 1: 直接使用 LRUCache 类
cache = LRUCache(capacity=100, ttl=3600)

# 设置缓存
cache.set("user_1", {"name": "Alice", "age": 25})
cache.set("user_2", {"name": "Bob", "age": 30}, ttl=1800)

# 获取缓存
user = cache.get("user_1")
if user:
    print(f"从缓存获取：{user}")
else:
    # 从数据库加载
    user = load_user_from_db("user_1")
    cache.set("user_1", user)

# 查看统计
stats = cache.stats()
print(f"命中率：{stats['hit_rate']}")

# 清理过期项
expired_count = cache.cleanup_expired()
print(f"清理 {expired_count} 个过期项")


# 方法 2: 使用装饰器
@lru_cache_decorator(capacity=100, ttl=3600)
def get_user_data(user_id):
    # 耗时操作
    return load_user_from_db(user_id)

# 自动缓存
user1 = get_user_data("user_1")  # miss
user2 = get_user_data("user_1")  # hit - 秒返回


# 方法 3: 持久化缓存
# 保存缓存
with open("cache.json", "w", encoding="utf-8") as f:
    json.dump(cache.to_dict(), f)

# 加载缓存
with open("cache.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    cache = LRUCache.from_dict(data)
