"""
Configuration for AI Memory System.
"""

import os
from pathlib import Path

# Base paths
WORKSPACE = Path("D:/OpenClaw/workspace")
DATA_DIR = WORKSPACE / "ai-memory-system" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Short-term memory config
SHORT_TERM_MAX_ITEMS = 100
SHORT_TERM_TTL_SECONDS = 3600  # 1 hour

# Long-term memory config
LONG_TERM_STORAGE_PATH = DATA_DIR / "memory_long_term.json"
LONG_TERM_MAX_ITEMS = 10000

# LLM config (for distillation)
LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "qwen2.5:1.5b")
LLM_BASE_URL = os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:11434")
LLM_API_TIMEOUT = 30

# Retrieval config
RETRIEVAL_TOP_K = 5
RETRIEVAL_SIMILARITY_THRESHOLD = 0.7

# Distillation config
DISTILL_BATCH_SIZE = 10
DISTILL_COMPRESSION_RATIO = 0.3

# Export
__all__ = [
    "WORKSPACE",
    "DATA_DIR",
    "SHORT_TERM_MAX_ITEMS",
    "SHORT_TERM_TTL_SECONDS",
    "LONG_TERM_STORAGE_PATH",
    "LONG_TERM_MAX_ITEMS",
    "LLM_MODEL",
    "LLM_BASE_URL",
    "LLM_API_TIMEOUT",
    "RETRIEVAL_TOP_K",
    "RETRIEVAL_SIMILARITY_THRESHOLD",
    "DISTILL_BATCH_SIZE",
    "DISTILL_COMPRESSION_RATIO",
]
