"""
AI Memory System - Local-first memory system for AI agents.
"""

from .short_term import ShortTermMemory
from .long_term import LongTermMemory
from .memory_system import MemorySystem
from .distiller import MemoryDistiller
from .retrieval import MemoryRetriever
from .openclaw_integration import OpenClawMemoryTool

__version__ = "0.1.0"
__all__ = [
    "MemorySystem",
    "ShortTermMemory",
    "LongTermMemory",
    "MemoryDistiller",
    "MemoryRetriever",
    "OpenClawMemoryTool",
]

try:
    from .ai_research_tool import ResearchTool, get_research_tool

    __all__.extend(["ResearchTool", "get_research_tool"])
except ImportError:
    pass
