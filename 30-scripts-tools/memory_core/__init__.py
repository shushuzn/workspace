"""
🧠 Memory Core - 统一记忆核心系统

统一入口，整合所有记忆管理功能。
"""

__version__ = '2.0.0'
__author__ = 'Claw'
__date__ = '2026-03-17'

from .core import MemoryCore
from .config import MemoryConfig

__all__ = ['MemoryCore', 'MemoryConfig']
