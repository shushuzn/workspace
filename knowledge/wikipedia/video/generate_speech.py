"""
语音合成：读取阅读文案(speech.txt)，生成MP3
依赖: pip install edge-tts
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

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

def generate_speech(speech_txt_path, output_mp3_path, voice="zh-CN-XiaoyiNeural"):
    with open(speech_txt_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        print(f"  [SKIP] 空文件: {speech_txt_path}")
        return False

    # 替换数学符号
    content = replace_math(content)

    # edge-tts 不能处理换行，合并为单行，用逗号分隔
    content = content.replace("\n", "，")

    output_mp3_path.parent.mkdir(parents=True, exist_ok=True)

    # edge-tts 命令
    cmd = [
        sys.executable, "-m", "edge_tts",
        "-t", content,
        "-v", voice,
        "--write-media", str(output_mp3_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore')
        if result.returncode != 0:
            print(f"  [ERROR] edge-tts failed: {result.stderr[:200]}")
            return False
        size = output_mp3_path.stat().st_size
        print(f"  [OK] {output_mp3_path.name} ({size:,} bytes)")
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

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
    parser = argparse.ArgumentParser(description="语音合成")
    parser.add_argument("speech_txt", nargs="?", help="speech.txt 路径（不指定则处理所有）")
    parser.add_argument("--voice", default="zh-CN-XiaoyiNeural", help="声音名称")
    args = parser.parse_args()

    articles_dir = Path(__file__).parent.parent / "articles"

    if args.speech_txt:
        speech_path = Path(args.speech_txt)
        mp3_path = speech_path.parent / stem_to_mp3_name(speech_path.stem)
        voice = "en-US-AriaNeural" if is_english(speech_path.stem) else args.voice
        generate_speech(speech_path, mp3_path, voice)
        return

    files = find_speech_files(articles_dir)
    if not files:
        print("未找到任何 *-speech.txt 文件")
        return

    print(f"找到 {len(files)} 个 speech.txt，开始生成语音...\n")

    for speech_path in sorted(files):
        mp3_path = speech_path.parent / stem_to_mp3_name(speech_path.stem)
        voice = "en-US-AriaNeural" if is_english(speech_path.stem) else args.voice
        print(f"处理: {speech_path.relative_to(articles_dir)}")
        generate_speech(speech_path, mp3_path, voice)

if __name__ == "__main__":
    main()
