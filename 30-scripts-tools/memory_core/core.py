"""
🧠 Memory Core - 统一记忆核心

所有记忆操作的单一入口
"""

import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from .config import MemoryConfig
from .optimization.cache import CacheManager
from .optimization.profiler import PerformanceProfiler
from .modules import (
    DistillerModule,
    QualityModule,
    SearchModule,
    AssociationModule,
    ForgettingModule,
    ConflictModule
)


class Memory:
    """记忆对象"""

    def __init__(self, content: str, **metadata):
        self.id = f"mem_{int(time.time() * 1000)}"
        self.content = content
        self.metadata = metadata
        self.score: float = 0.0
        self.links: List[str] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'content': self.content,
            'metadata': self.metadata,
            'score': self.score,
            'links': self.links,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Memory':
        """从字典创建"""
        mem = cls(content=data['content'], **data.get('metadata', {}))
        mem.id = data.get('id', mem.id)
        mem.score = data.get('score', 0.0)
        mem.links = data.get('links', [])
        return mem

    def __repr__(self):
        return f"Memory(id={self.id}, score={self.score:.2f})"


class MemoryCore:
    """
    统一记忆核心 - 所有记忆操作的单一入口
    
    功能:
    - 处理记忆 (蒸馏 → 评分 → 关联 → 存储)
    - 搜索记忆
    - 质量评估
    - 关联分析
    - 遗忘管理
    - 冲突检测
    - 性能优化 (缓存、预取)
    """

    def __init__(self, config: Optional[MemoryConfig] = None, **kwargs):
        """
        初始化 MemoryCore
        
        Args:
            config: 配置对象
            **kwargs: 配置参数
        """
        # 初始化配置
        self.config = config or MemoryConfig(**kwargs)

        # 初始化优化器
        self.cache = CacheManager(self.config) if self.config.enable_cache else None
        self.profiler = PerformanceProfiler()

        # 初始化功能模块
        self.distiller = DistillerModule(self.config)
        self.quality = QualityModule(self.config)
        self.search_module = SearchModule(self.config, self.cache)
        self.association = AssociationModule(self.config)
        self.forgetting = ForgettingModule(self.config)
        self.conflict = ConflictModule(self.config)

        # 内存存储
        self._memories: Dict[str, Memory] = {}

        # 日志
        if self.config.enable_logging:
            self._setup_logging()

        self._log("[INFO] MemoryCore initialized")

    def _setup_logging(self):
        """设置日志"""
        import logging

        log_file = self.config.workspace / self.config.get('log_file', 'memory_core.log')

        logging.basicConfig(
            level=getattr(logging, self.config.get('log_level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('MemoryCore')

    def _log(self, message: str):
        """记录日志"""
        if hasattr(self, 'logger'):
            self.logger.info(message)
        else:
            print(message)

    # ========== 核心 API ==========

    def process(self, raw_memory: Union[str, Dict]) -> Memory:
        """
        处理原始记忆 → 蒸馏 → 评分 → 关联 → 存储
        
        Args:
            raw_memory: 原始记忆 (字符串或字典)
        
        Returns:
            Memory: 处理后的记忆对象
        """
        self.profiler.start_timer('process')

        # 1. 标准化输入
        if isinstance(raw_memory, str):
            raw_memory = {'content': raw_memory}

        # 2. 蒸馏压缩
        self.profiler.start_timer('distill')
        distilled = self._distill(raw_memory)
        self.profiler.end_timer('distill')

        # 3. 质量评估
        self.profiler.start_timer('evaluate')
        score = self._evaluate(distilled)
        self.profiler.end_timer('evaluate')

        # 4. 创建记忆对象
        memory = Memory(
            content=distilled.get('content', ''),
            **{k: v for k, v in distilled.items() if k != 'content'}
        )
        memory.score = score

        # 5. 关联分析
        self.profiler.start_timer('associate')
        links = self._associate(memory)
        memory.links = links
        self.profiler.end_timer('associate')

        # 6. 冲突检测
        self.profiler.start_timer('detect_conflicts')
        conflicts = self._detect_conflicts(memory)
        if conflicts:
            self._log(f"[WARN] Found {len(conflicts)} conflicts")
        self.profiler.end_timer('detect_conflicts')

        # 7. 存储
        self._store(memory)

        # 8. 清除缓存
        if self.cache:
            self.cache.clear()

        duration = self.profiler.end_timer('process')
        self._log(f"[INFO] Processed memory in {duration:.3f}s (score={score:.2f})")

        return memory

    def search(self, query: str, limit: int = 10, **kwargs) -> List[Memory]:
        """
        搜索记忆
        
        Args:
            query: 搜索查询
            limit: 返回数量限制
            **kwargs: 搜索参数
        
        Returns:
            List[Memory]: 匹配的记忆列表
        """
        self.profiler.start_timer('search')

        # 检查缓存
        cache_key = f"search:{hash(query)}:{limit}"
        if self.cache and (cached := self.cache.get(cache_key)):
            self._log(f"[DEBUG] Cache hit for search: {query}")
            return cached

        # 执行搜索
        results = self._search_query(query, limit, **kwargs)

        # 缓存结果
        if self.cache:
            self.cache.set(cache_key, results)

        duration = self.profiler.end_timer('search')
        self._log(f"[INFO] Search found {len(results)} memories in {duration:.3f}s")

        return results

    def evaluate(self, memory: Memory) -> float:
        """评估记忆质量"""
        self.profiler.start_timer('evaluate')
        score = self._evaluate(memory.to_dict())
        duration = self.profiler.end_timer('evaluate')
        self._log(f"[DEBUG] Evaluated memory {memory.id}: {score:.2f}")
        return score

    def associate(self, memory: Memory, limit: int = None) -> List[Memory]:
        """查找关联记忆"""
        limit = limit or self.config.max_associations
        self.profiler.start_timer('associate')
        links = self._associate(memory, limit)
        duration = self.profiler.end_timer('associate')
        self._log(f"[DEBUG] Found {len(links)} associations in {duration:.3f}s")
        return links

    def forget(self, memory_id: str, strategy: str = 'archive') -> bool:
        """
        遗忘/归档记忆
        
        Args:
            memory_id: 记忆 ID
            strategy: 'archive' | 'delete' | 'compress'
        
        Returns:
            bool: 是否成功
        """
        self.profiler.start_timer('forget')
        success = self._forget(memory_id, strategy)
        duration = self.profiler.end_timer('forget')
        self._log(f"[INFO] Forgot memory {memory_id} ({strategy}) in {duration:.3f}s")

        if self.cache:
            self.cache.clear()

        return success

    # ========== 高级 API ==========

    def batch_process(self, memories: List[Union[str, Dict]], parallel: bool = None) -> List[Memory]:
        """批量处理记忆"""
        self.profiler.start_timer('batch_process')

        use_parallel = parallel if parallel is not None else self.config.parallel_processing

        if use_parallel:
            results = self._parallel_process(memories)
        else:
            results = [self.process(m) for m in memories]

        duration = self.profiler.end_timer('batch_process')
        self._log(f"[INFO] Batch processed {len(memories)} memories in {duration:.3f}s")

        return results

    def get_dashboard_data(self) -> Dict:
        """获取仪表板数据"""
        return {
            'total_memories': len(self._memories),
            'avg_score': sum(m.score for m in self._memories.values()) / len(self._memories) if self._memories else 0,
            'recent_memories': list(self._memories.values())[-10:],
            'performance': self.profiler.report(),
        }

    def get_stats(self) -> Dict:
        """获取统计信息"""
        memories = list(self._memories.values())

        if not memories:
            return {'total': 0}

        scores = [m.score for m in memories]

        return {
            'total': len(memories),
            'avg_score': sum(scores) / len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'high_quality': len([s for s in scores if s >= self.config.high_quality_threshold]),
            'low_quality': len([s for s in scores if s <= self.config.low_quality_threshold]),
        }

    # ========== 内部方法 ==========

    def _distill(self, raw_memory: Dict) -> Dict:
        """蒸馏压缩"""
        return self.distiller.compress(raw_memory)

    def _evaluate(self, memory_dict: Dict) -> float:
        """质量评估"""
        return self.quality.evaluate(memory_dict)

    def _associate(self, memory: Memory, limit: int = None) -> List[str]:
        """关联分析"""
        memories_list = [m.to_dict() for m in self._memories.values()]
        associations = self.association.find(memory.to_dict(), memories_list, limit)
        return [a.get('id') for a in associations]

    def _detect_conflicts(self, memory: Memory) -> List[Dict]:
        """冲突检测"""
        memories_list = [m.to_dict() for m in self._memories.values()]
        return self.conflict.detect(memory.to_dict(), memories_list)

    def _forget(self, memory_id: str, strategy: str) -> bool:
        """遗忘执行"""
        return self.forgetting.execute(memory_id, strategy)

    def _search_query(self, query: str, limit: int, **kwargs) -> List[Memory]:
        """搜索执行"""
        memories_list = [m.to_dict() for m in self._memories.values()]
        results = self.search_module.search(query, memories_list, limit, **kwargs)
        return [Memory.from_dict(r) for r in results]

    def _store(self, memory: Memory):
        """存储记忆"""
        self._memories[memory.id] = memory
        self._log(f"[DEBUG] Stored memory {memory.id}")

    def _parallel_process(self, memories: List[Union[str, Dict]]) -> List[Memory]:
        """并行处理"""
        from concurrent.futures import ThreadPoolExecutor

        max_workers = self.config.max_workers

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.process, memories))

        return results

    # ========== 性能分析 ==========

    def get_performance_report(self) -> str:
        """获取性能报告"""
        return self.profiler.report()

    def reset_stats(self):
        """重置统计"""
        self.profiler.reset()
        if self.cache:
            self.cache.clear()
