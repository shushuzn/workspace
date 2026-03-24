"""
记忆系统配置管理
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class MemoryConfig:
    """记忆系统配置"""

    DEFAULT_CONFIG = {
        # 基础配置
        'workspace': None,  # 自动检测
        'memory_dir': '13-memory-记忆系统',
        'backup_dir': 'backup/memory-scripts',

        # 质量阈值
        'quality_threshold': 0.5,
        'low_quality_threshold': 0.3,
        'high_quality_threshold': 0.8,

        # 关联配置
        'max_associations': 10,
        'min_similarity': 0.6,

        # 缓存配置
        'enable_cache': True,
        'cache_ttl': 300,  # 5 分钟
        'cache_max_size': 1000,

        # 性能配置
        'parallel_processing': True,
        'max_workers': 4,
        'batch_size': 100,

        # 遗忘配置
        'auto_forget': False,
        'forget_after_days': 90,

        # 日志配置
        'enable_logging': True,
        'log_level': 'INFO',
        'log_file': 'memory_core.log',
    }

    def __init__(self, config_path: Optional[str] = None, **kwargs):
        """
        初始化配置
        
        Args:
            config_path: 配置文件路径 (JSON)
            **kwargs: 覆盖的配置项
        """
        self.config = self.DEFAULT_CONFIG.copy()

        # 自动检测工作区
        self.config['workspace'] = self._detect_workspace()

        # 加载配置文件
        if config_path and os.path.exists(config_path):
            self._load_from_file(config_path)

        # 应用覆盖配置
        self.config.update(kwargs)

    def _detect_workspace(self) -> Path:
        """自动检测工作区路径"""
        # 尝试常见路径
        candidates = [
            Path(r'D:\OpenClaw\workspace'),
            Path(os.getcwd()),
            Path(__file__).parent.parent,
        ]

        for path in candidates:
            if path.exists():
                return path

        return Path.cwd()

    def _load_from_file(self, path: str):
        """从 JSON 文件加载配置"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                self.config.update(file_config)
        except Exception as e:
            print(f"[WARN] Failed to load config from {path}: {e}")

    def save_to_file(self, path: str):
        """保存配置到 JSON 文件"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"[INFO] Config saved to {path}")
        except Exception as e:
            print(f"[ERROR] Failed to save config: {e}")

    def get(self, key: str, default=None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置项"""
        self.config[key] = value

    @property
    def workspace(self) -> Path:
        """工作区路径"""
        return Path(self.config['workspace'])

    @property
    def memory_dir(self) -> Path:
        """记忆存储目录"""
        return self.workspace / self.config['memory_dir']

    @property
    def backup_dir(self) -> Path:
        """备份目录"""
        return self.workspace / self.config['backup_dir']

    @property
    def quality_threshold(self) -> float:
        """质量阈值"""
        return self.config['quality_threshold']

    @property
    def enable_cache(self) -> bool:
        """是否启用缓存"""
        return self.config['enable_cache']

    @property
    def enable_logging(self) -> bool:
        """是否启用日志"""
        return self.config.get('enable_logging', True)

    @property
    def parallel_processing(self) -> bool:
        """是否并行处理"""
        return self.config.get('parallel_processing', True)

    @property
    def max_workers(self) -> int:
        """最大工作线程数"""
        return self.config.get('max_workers', 4)

    @property
    def max_associations(self) -> int:
        """最大关联数"""
        return self.config.get('max_associations', 10)

    @property
    def high_quality_threshold(self) -> float:
        """高质量阈值"""
        return self.config.get('high_quality_threshold', 0.8)

    @property
    def low_quality_threshold(self) -> float:
        """低质量阈值"""
        return self.config.get('low_quality_threshold', 0.3)

    def __repr__(self):
        return f"MemoryConfig(workspace={self.workspace})"
