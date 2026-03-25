"""
优化模块
"""

from .cache import CacheManager
from .profiler import PerformanceProfiler
from .prefetch import Prefetcher

__all__ = ['CacheManager', 'PerformanceProfiler', 'Prefetcher']
