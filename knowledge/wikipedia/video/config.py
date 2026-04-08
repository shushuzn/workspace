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
# 引擎: edge (微软在线) / kokoro (本地-已禁用)
TTS_ENGINE = "edge"  # 严格默认 edge 在线API，禁止本地 TTS 模型

# Edge TTS 音色
EDGE_VOICE_ZH = "zh-CN-XiaoyiNeural"
EDGE_VOICE_EN = "en-US-AriaNeural"

# Kokoro-82M 音色（需先运行 python -m kokoro_kai.generate --install 下载）
KOKORO_VOICE_ZH = "zf_xiaoyi"   # 中文女声（匹配 edge XiaoyiNeural）
KOKORO_VOICE_EN = "af_sarah"  # 英文女声

# T2I 配置（无本地 LLM — 严格禁止本地 SD/diffusers）
# 云端 API: "replicate"/"together"/"openai" 或 "matplotlib"（默认，回退）
# 未来接入 cloud API 时设置 T2I_ENGINE="replicate" + T2I_API_KEY
T2I_ENGINE = "matplotlib"  # 严格默认 matplotlib，本地 SD 已禁用
T2I_MODEL = ""             # cloud model name（待配置）
T2I_API_KEY = ""            # cloud API key（待配置）
T2I_STEPS = 25             # 推理步数（云端用）
T2I_GUIDANCE = 7.5         # CFG guidance scale
T2I_SEED = 42              # 固定种子（可复现）

# 通用参数
RATE = "+10%"
PITCH = "+0Hz"

# 向后兼容别名
VOICE_ZH = EDGE_VOICE_ZH
VOICE_EN = EDGE_VOICE_EN
