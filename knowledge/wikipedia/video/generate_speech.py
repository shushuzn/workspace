"""
语音合成：读取阅读文案(speech.txt)，生成MP3
支持引擎: edge-tts (微软在线) / kokoro (本地-82M)
依赖: pip install edge-tts
      pip install kokoro-onnx; python -m kokoro_kai.generate --install
"""
import argparse
import re
import subprocess
import sys
import os
from pathlib import Path

# 导入音色配置
sys.path.insert(0, str(Path(__file__).parent))
try:
    from config import (
        KOKORO_VOICE_ZH, KOKORO_VOICE_EN,
        EDGE_VOICE_ZH, EDGE_VOICE_EN,
    )
except ImportError:
    KOKORO_VOICE_ZH = "zf_xiaoyi"
    KOKORO_VOICE_EN = "af_sarah"
    EDGE_VOICE_ZH = "zh-CN-XiaoyiNeural"
    EDGE_VOICE_EN = "en-US-AriaNeural"

# 查找所有 speech.txt
def find_speech_files(articles_dir):
    return [p for p in Path(articles_dir).rglob("*speech*.txt")
            if "阅读文案" not in p.name]

# 替换数学符号为可读英文
MATH_REPLACEMENTS = [
    (r'σ', 'sigma '),
    (r'λ', 'lambda '),
    (r'ω', 'omega '),
    (r'ε', 'epsilon '),
    (r'∂', 'delta '),
    (r'∫', 'integral '),
    (r'∑', 'sum '),
    (r'≤', ' less than or equal '),
    (r'≥', ' greater than or equal '),
    (r'≠', ' not equal '),
    (r'∞', ' infinity '),
    (r'→', ' to '),
    (r'↔', ' and '),
    (r'∈', ' belongs to '),
    (r'∉', ' does not belong to '),
    (r'⊂', ' subset of '),
    (r'∪', ' union '),
    (r'∩', ' intersection '),
    (r'√', ' square root of '),
    (r'∏', ' product '),
    # 下标
    (r'₀', '0'), (r'₁', '1'), (r'₂', '2'), (r'₃', '3'), (r'₄', '4'),
    (r'₅', '5'), (r'₆', '6'), (r'₇', '7'), (r'₈', '8'), (r'₉', '9'),
    # 上标
    (r'⁰', '0'), (r'¹', '1'), (r'²', '2'), (r'³', '3'), (r'⁴', '4'),
    (r'⁵', '5'), (r'⁶', '6'), (r'⁷', '7'), (r'⁸', '8'), (r'⁹', '9'),
    # 希腊字母
    (r'α', 'alpha '), (r'β', 'beta '), (r'γ', 'gamma '), (r'δ', 'delta '),
    (r'η', 'eta '), (r'θ', 'theta '), (r'ι', 'iota '), (r'κ', 'kappa '),
    (r'μ', 'mu '), (r'ν', 'nu '), (r'ξ', 'xi '), (r'π', 'pi '),
    (r'ρ', 'rho '), (r'ς', 'sigma '), (r'τ', 'tau '), (r'υ', 'upsilon '),
    (r'φ', 'phi '), (r'ψ', 'psi '), (r'ζ', 'zeta '),
    # 大写希腊
    (r'Σ', 'Sigma '), (r'Π', 'Pi '), (r'Δ', 'Delta '), (r'Ω', 'Omega '),
    (r'Λ', 'Lambda '), (r'Ψ', 'Psi '), (r'Φ', 'Phi '), (r'Γ', 'Gamma '),
    # 其他符号
    (r'ℤ', 'integers '), (r'ℝ', 'reals '), (r'ℕ', 'naturals '),
    (r'ℂ', 'complex '),
    # 带帽/波浪
    (r'ẋ', 'x dot '), (r'ẍ', 'x double dot '),
    (r'ŷ', 'y hat '),
    # 点号
    (r'·', '.'), (r'×', ' times '), (r'÷', ' divided by '),
    # 特殊
    (r'ℏ', 'h bar '), (r'ℏ', 'h bar '),
    (r'⊕', ' direct sum '), (r'⊗', ' tensor product '),
]

def replace_math(text):
    for pattern, replacement in MATH_REPLACEMENTS:
        text = re.sub(pattern, replacement, text)
    return text

# ── Kokoro TTS ──────────────────────────────────────────────────────────────
_KOKORO_DIR = Path(__file__).parent.parent / ".kokoro"
_KOKORO_MODEL = _KOKORO_DIR / "kokoro-v1.0.onnx"
_KOKORO_VOICES = _KOKORO_DIR / "voices-v1.0.bin"
_kokoro_instance = None


def _get_kokoro():
    """单例 Kokoro 实例"""
    global _kokoro_instance
    if _kokoro_instance is None:
        if not _KOKORO_MODEL.exists() or not _KOKORO_VOICES.exists():
            return None
        import kokoro_onnx
        _kokoro_instance = kokoro_onnx.Kokoro(str(_KOKORO_MODEL), str(_KOKORO_VOICES))
    return _kokoro_instance


def generate_kokoro(text: str, output_path: Path, voice: str, speed: float = 1.0) -> bool:
    """使用 Kokoro-82M 本地生成 WAV（转MP3）"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    kokoro = _get_kokoro()
    if kokoro is None:
        print(f"  [Kokoro] 模型文件未就绪，跳过")
        return False

    # Kokoro 支持换行作为自然停顿
    text = text.replace("\n", " ")

    # 语言检测: Kokoro 用 cmn (Mandarin) / en-us
    lang = "cmn" if voice.startswith("z") else "en-us"

    try:
        import soundfile as sf
        samples, sr = kokoro.create(text, voice, speed=speed, lang=lang)
        # Kokoro 输出 float32 WAV，转为 MP3 需用 ffmpeg
        wav_path = output_path.with_suffix(".wav")
        sf.write(str(wav_path), samples, sr)
        # ffmpeg 转 MP3 (保持与 edge-tts 输出格式一致)
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_cmd = [
            str(ffmpeg_exe), "-y", "-i", str(wav_path),
            "-codec:a", "libmp3lame", "-b:a", "192k",
            str(output_path)
        ]
        result = subprocess.run(ffmpeg_cmd, capture_output=True, errors='ignore')
        if result.returncode != 0:
            print(f"  [Kokoro] ffmpeg 转换失败: {result.stderr[:100]}")
            # fallback: 直接用 WAV
            return True if output_path.exists() else False
        # 删除中间 WAV
        if wav_path.exists():
            wav_path.unlink()
        size = output_path.stat().st_size
        print(f"  [OK] {output_path.name} ({size:,} bytes, kokoro/{voice})")
        return True
    except ImportError as e:
        print(f"  [Kokoro] 缺少 soundfile: {e}")
        return False
    except Exception as e:
        print(f"  [Kokoro ERROR] {e}")
        return False

# ── Edge TTS ─────────────────────────────────────────────────────────────────
def generate_edge(text: str, output_path: Path, voice: str, rate: str, pitch: str) -> bool:
    """使用 Edge-TTS 在线生成 MP3"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, "-m", "edge_tts",
        "-t", text,
        "-v", voice,
        "--write-media", str(output_path),
        "--rate", rate,
        "--pitch", pitch,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore')
        if result.returncode != 0:
            print(f"  [ERROR] edge-tts failed: {result.stderr[:200]}")
            return False
        size = output_path.stat().st_size
        print(f"  [OK] {output_path.name} ({size:,} bytes, edge)")
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def generate_speech(speech_txt_path, output_mp3_path, voice=None,
                    rate="+10%", pitch="+0Hz", engine="auto"):
    with open(speech_txt_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        print(f"  [SKIP] 空文件: {speech_txt_path}")
        return False

    # 替换数学符号
    content = replace_math(content)

    # Kokoro 支持换行，edge-tts 不能处理换行
    if engine == "kokoro":
        # Kokoro: 保留换行（作为自然停顿），用 speed 参数控制
        kokoro_text = content.replace("\n", " ")
        speed = 1.1  # 对应 +10% 语速
        kokoro_voice = voice or (KOKORO_VOICE_EN if is_english(output_mp3_path.stem) else KOKORO_VOICE_ZH)
        return generate_kokoro(kokoro_text, output_mp3_path, kokoro_voice, speed)

    elif engine == "edge":
        content = content.replace("\n", "，")
        edge_voice = voice or (EDGE_VOICE_EN if is_english(output_mp3_path.stem) else EDGE_VOICE_ZH)
        return generate_edge(content, output_mp3_path, edge_voice, rate, pitch)

    else:  # auto: 优先 Kokoro，回退 Edge
        kokoro_text = content.replace("\n", " ")
        kokoro_voice = voice or (KOKORO_VOICE_EN if is_english(output_mp3_path.stem) else KOKORO_VOICE_ZH)
        if generate_kokoro(kokoro_text, output_mp3_path, kokoro_voice, speed=1.1):
            return True
        print(f"  [FALLBACK] 切换到 edge-tts...")
        content = content.replace("\n", "，")
        edge_voice = voice or (EDGE_VOICE_EN if is_english(output_mp3_path.stem) else EDGE_VOICE_ZH)
        return generate_edge(content, output_mp3_path, edge_voice, rate, pitch)

def stem_to_mp3_name(stem):
    """NN-标题-阅读文案-speech → NN-标题.mp3; -speech-en → -en.mp3"""
    if stem.endswith("-speech-en"):
        return stem[:-10] + "-en.mp3"
    for suffix in ["-阅读文案-speech", "-speech"]:
        if stem.endswith(suffix):
            return stem[:-len(suffix)] + ".mp3"
    return stem + ".mp3"

def is_english(stem):
    return "-en" in stem

def main():
    parser = argparse.ArgumentParser(description="语音合成 (edge-tts + Kokoro-82M)")
    parser.add_argument("speech_txt", nargs="?", help="speech.txt 路径（不指定则处理所有）")
    parser.add_argument("--engine", default="auto", choices=["auto", "kokoro", "edge"],
                        help="TTS 引擎: auto(优先Kokoro回退Edge) / kokoro / edge")
    parser.add_argument("--voice", default=None, help="声音名称（kokoro音色名或edge voice名）")
    args = parser.parse_args()

    articles_dir = Path(__file__).parent.parent / "articles"

    if args.speech_txt:
        speech_path = Path(args.speech_txt)
        mp3_path = speech_path.parent / stem_to_mp3_name(speech_path.stem)
        # voice=None 时由 generate_speech 根据 engine 选择对应默认音色
        generate_speech(speech_path, mp3_path, args.voice, engine=args.engine)
        return

    files = find_speech_files(articles_dir)
    if not files:
        print("未找到任何 *-speech.txt 文件")
        return

    print(f"找到 {len(files)} 个 speech.txt，引擎={args.engine}...\n")

    for speech_path in sorted(files):
        mp3_path = speech_path.parent / stem_to_mp3_name(speech_path.stem)
        print(f"处理: {speech_path.relative_to(articles_dir)}")
        generate_speech(speech_path, mp3_path, args.voice, engine=args.engine)

if __name__ == "__main__":
    main()
