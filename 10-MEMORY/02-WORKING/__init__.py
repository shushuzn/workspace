# -*- coding: utf-8 -*-
"""
Dual-layer Memory System
AI Agent 双层记忆架构 - 短期工作记忆 + 长期归档记忆
"""

from .models import MemoryItem, MemoryStats
from .dual_layer_memory import DualLayerMemory
from .working_memory import WorkingMemory
from .archive_memory import ArchiveMemory
from .importance_scorer import ImportanceScorer
from .forgetting_mechanism import ForgettingMechanism
from .session_bridge import SessionBridge

__all__ = [
    'MemoryItem',
    'MemoryStats',
    'DualLayerMemory',
    'WorkingMemory',
    'ArchiveMemory',
    'ImportanceScorer',
    'ForgettingMechanism',
    'SessionBridge',
]

__version__ = '1.0.0'