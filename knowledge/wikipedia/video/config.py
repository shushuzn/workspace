"""
视频流水线配置中心
"""
from pathlib import Path

# 根目录
WIKI_ROOT = Path(__file__).parent.parent
ARTICLES_DIR = WIKI_ROOT / "articles"
CACHE_DIR = WIKI_ROOT / ".video-cache"
CACHE_INDEX = CACHE_DIR / "index.json"

# 并行配置
MAX_WORKERS = 4  # 并发视频数
BATCH_SIZE = 5   # 每批视频数

# 质量门禁
MIN_WORDS = 500
MAX_WORDS = 1500

# 视频参数
VIDEO_CRF = {  # 场景类型 → CRF
    'formula': 18,    # 公式/证明：高清晰度
    'cover': 22,      # 封面：标准
    'scene': 22,      # 配图：标准
}
AUDIO_BITRATE = "192k"
AUDIO_LOUDNORM = "I=-16:LRA=11:tp=-1.5"

# TTS 配置
VOICE_ZH = "zh-CN-XiaoyiNeural"
VOICE_EN = "en-US-AriaNeural"
RATE = "+10%"
PITCH = "+0Hz"
