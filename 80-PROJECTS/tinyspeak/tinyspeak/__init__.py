"""
TinySpeak - Lightweight Local-First TTS Tool
"""

__version__ = "0.2.0"
__author__ = "OpenClaw"

from .engine import TTSEngine, Voice, VoicePreset
from .converter import AudioConverter

__all__ = ["TTSEngine", "Voice", "VoicePreset", "AudioConverter"]