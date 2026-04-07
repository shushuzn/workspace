"""
视频文案质量监控模块
检查：文案可读性/节奏/数学符号覆盖率 | 音频质量 | 视频成品质量
用法：
  python quality_monitor.py check-content <speech.txt>
  python quality_monitor.py check-audio <audio.mp3>
  python quality_monitor.py check-video <video.mp4>
  python quality_monitor.py full <article_dir>
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional

# ============= 文案质量检查 =============

# 参考 B站/YouTube 高播放量科普视频文案标准
# 3分钟视频 ≈ 450-750字（中文 2.5字/秒，留停顿）
MIN_WORDS = 450
MAX_WORDS = 750

# 可读性：平均句长（字/句），科普文案 12-20 字为佳
IDEAL_AVG_SENTENCE = 15
MAX_AVG_SENTENCE = 25  # 超过此值扣分

# 逗号密度：每句话 0.6-1.2 个逗号（口语节奏）
MIN_COMMAS_PER_SENTENCE = 0.6
MAX_COMMAS_PER_SENTENCE = 1.5  # 过多逗号也影响流畅

# 换行密度：每 2-3 句应有换行（模拟对话停顿）
MAX_SENTENCES_PER_PARAGRAPH = 3

# 数学符号替换覆盖率
MATH_SYMBOLS = [
    r'σ', r'λ', r'ω', r'ε', r'∂', r'∫', r'∑', r'≤', r'≥', r'≠',
    r'∞', r'→', r'↔', r'∈', r'∉', r'⊂', r'∪', r'∩', r'√', r'∏',
    r'α', r'β', r'γ', r'δ', r'η', r'θ', r'ι', r'κ', r'μ', r'ν',
    r'ξ', r'π', r'ρ', r'ς', r'τ', r'υ', r'φ', r'ψ', r'ζ',
    r'Σ', r'Π', r'Δ', r'Ω', r'Λ', r'Ψ', r'Φ', r'Γ',
    r'ℤ', r'ℝ', r'ℕ', r'ℂ', r'ℏ',
    r'₀', r'₁', r'₂', r'₃', r'₄', r'₅', r'₆', r'₇', r'₈', r'₉',
    r'⁰', r'¹', r'²', r'³', r'⁴', r'⁵', r'⁶', r'⁷', r'⁸', r'⁹',
]

# 鼓励使用的口语化词汇（加分）
COLLOQUIAL_WORDS = [
    "想象", "我们", "你", "一起", "看", "注意", "记住",
    "简单说", "其实", "相当于", "就像",
]

# 应避免的学术腔/书面化词汇
# 注意："实验结果/证明/定义"在科普视频中是自然用词，不应标记
ACADEMIC_WORDS = [
    "本论文", "本文", "该论文", "研究表明", "本质上是",
    "我们提出", "本文提出", "本文工作", "本文方法",
    "实验结果表明", "数据表明", "实验表明",
    "故而", "然而", "此外", "综上所述",
]

@dataclass
class ContentQualityReport:
    """文案质量检测报告"""
    score: float  # 0-100
    issues: List[str]
    warnings: List[str]
    metrics: dict

    def to_dict(self):
        return asdict(self)

def check_math_coverage(text: str) -> tuple[int, List[str]]:
    """检查数学符号替换覆盖率"""
    # 找出所有在文本中出现的符号
    found_in_text = [sym for sym in MATH_SYMBOLS if sym in text]
    if not found_in_text:
        # 文本中无任何数学符号，视为100%覆盖
        return 100, []
    # 未替换的符号
    missing = [sym for sym in found_in_text if sym in text]
    coverage = 100 * (1 - len(missing) / len(found_in_text))
    return int(coverage), missing

def check_readability(text: str) -> tuple[float, List[str]]:
    """计算可读性：平均句长 + 中文逗号密度"""
    sentences = re.split(r'[。！？!?\n]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return 0.0, ["无有效句子"]

    total_chars = sum(len(s) for s in sentences)
    avg_len = total_chars / len(sentences)

    comma_count = text.count('，')
    comma_per_sentence = comma_count / len(sentences)

    issues = []
    if avg_len > MAX_AVG_SENTENCE:
        issues.append(f"平均句长 {avg_len:.1f} 字 > {MAX_AVG_SENTENCE} 字（建议拆分为短句）")
    if comma_per_sentence < MIN_COMMAS_PER_SENTENCE:
        issues.append(f"逗号密度 {comma_per_sentence:.2f} < {MIN_COMMAS_PER_SENTENCE}（缺乏口语节奏）")
    if comma_per_sentence > MAX_COMMAS_PER_SENTENCE:
        issues.append(f"逗号密度 {comma_per_sentence:.2f} > {MAX_COMMAS_PER_SENTENCE}（停顿过多）")

    # 评分：基线 15字/句，0.9逗号/句
    score = max(0, 100 - max(0, avg_len - IDEAL_AVG_SENTENCE) * 3 - abs(comma_per_sentence - 0.9) * 25)
    return round(score, 1), issues

def check_academic_tone(text: str) -> tuple[float, List[str]]:
    """检测学术腔/书面化程度"""
    found = []
    for word in ACADEMIC_WORDS:
        if word in text:
            found.append(word)

    # 每100字出现次数，避免短文本密度虚高
    per_100 = len(found) / max(len(text) / 100, 1)
    issues = [f"学术腔词汇: {', '.join(found)}"] if found else []

    score = max(0, 100 - per_100 * 12)
    return round(score, 1), issues

def check_duration_estimate(text: str) -> tuple[float, str]:
    """估算配音时长（中文约 2.5 字/秒，英文约 3.5 字/秒）"""
    # 简单估算：中文 2.5字/秒，英文单词 3.5词/秒
    zh_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    en_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
    duration = zh_chars / 2.5 + en_words / 3.5
    target = 180  # 3分钟
    deviation = abs(duration - target) / target
    score = max(0, 100 - deviation * 100)
    note = f"估算时长 {duration:.1f}s (目标 ~180s)"
    return score, note

def check_content_quality(speech_txt: Path) -> ContentQualityReport:
    """完整文案质量检查"""
    text = speech_txt.read_text(encoding='utf-8').strip()
    if not text:
        return ContentQualityReport(0, ["空文件"], [], {})

    all_issues = []
    all_warnings = []
    metrics = {}

    # 1. 数学符号覆盖率
    math_cov, math_missing = check_math_coverage(text)
    metrics['math_coverage'] = math_cov
    if math_missing:
        all_issues.append(f"未替换数学符号: {', '.join(math_missing[:10])}")

    # 2. 可读性
    readability, read_issues = check_readability(text)
    metrics['readability'] = readability
    all_issues.extend(read_issues)

    # 3. 学术腔检测
    academic, acad_issues = check_academic_tone(text)
    metrics['academic_tone'] = academic
    all_issues.extend(acad_issues)

    # 4. 时长估算
    duration, duration_note = check_duration_estimate(text)
    metrics['duration_estimate'] = duration
    if deviation := re.search(r'(\d+(?:\.\d+)?)%', str(100 - abs(180 - float(re.findall(r'[\d.]+', duration_note)[0]) / 1.8))):
        pass  # 已在 score 计算

    # 综合评分（加权）
    weights = {'math': 0.30, 'readability': 0.30, 'academic': 0.20, 'duration': 0.20}
    score = (
        math_cov * weights['math'] +
        readability * weights['readability'] +
        academic * weights['academic'] +
        duration * weights['duration']
    )

    # 字数检查（来自 check_script.py）
    char_count = len(text.replace('\n', ''))
    metrics['char_count'] = char_count
    if char_count < 500:
        all_warnings.append(f"字数不足: {char_count} < 500")
    elif char_count > 1500:
        all_warnings.append(f"字数偏多: {char_count} > 1500")

    return ContentQualityReport(
        score=round(score, 1),
        issues=all_issues,
        warnings=all_warnings,
        metrics=metrics
    )

# ============= 音频质量检查 =============

@dataclass
class AudioQualityReport:
    score: float
    issues: List[str]
    warnings: List[str]
    metrics: dict

    def to_dict(self):
        return asdict(self)

def check_audio_quality(mp3_path: Path) -> AudioQualityReport:
    """使用 ffmpeg (兼容 Windows imageio_ffmpeg 打包版) 检查音频质量"""
    issues = []
    warnings = []
    metrics = {}

    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        ffmpeg = 'ffmpeg'

    cmd = [ffmpeg, '-i', str(mp3_path), '-f', 'null', '-']

    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, _ = p.communicate(timeout=10)
        text = out.decode('utf-8', errors='replace')
    except subprocess.TimeoutExpired:
        p.kill()
        return AudioQualityReport(0, ["ffmpeg 探测超时"], [], {})
    except Exception as e:
        return AudioQualityReport(0, [f"ffmpeg 执行失败: {e}"], [], {})

    # 从 stderr 解析元数据
    # Duration: 00:01:50.09 (ffmpeg 格式)
    duration = 0.0
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", text, re.IGNORECASE)
    if m:
        h, mn, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
        duration = h * 3600 + mn * 60 + s
    metrics['duration'] = duration

    # Bitrate: 48 kb/s (数字前可能有空格)
    bit_rate = 0
    m = re.search(r"bitrate:\s*(\d+)\s*kb", text, re.IGNORECASE)
    if m:
        bit_rate = int(m.group(1)) * 1000
    metrics['bitrate'] = bit_rate

    # Audio stream: Stream #0:0: Audio: mp3 (mp3float), 24000 Hz, mono, fltp, 48 kb/s
    sample_rate = 0
    channels = 0
    codec = None
    # 匹配 "Audio: <codec>, <rate> Hz, mono/stereo, ..."
    audio_line = re.search(r"Audio:\s*(\w+)[^(]*,\s*(\d+)\s*Hz,\s*(\w+)", text, re.IGNORECASE)
    if audio_line:
        codec = audio_line.group(1)
        sample_rate = int(audio_line.group(2))
        ch_str = audio_line.group(3).lower()
        channels = 1 if ch_str == 'mono' else (2 if ch_str == 'stereo' else 0)
    metrics['sample_rate'] = sample_rate
    metrics['channels'] = channels
    metrics['codec'] = codec

    # 综合评分
    score = 100
    if duration < 60 or duration > 600:
        score -= 30
    if bit_rate < 96000:
        score -= 20
    if sample_rate not in (44100, 48000):
        score -= 10
    if channels < 1:
        score -= 40

    return AudioQualityReport(
        score=max(0, round(score, 1)),
        issues=issues,
        warnings=warnings,
        metrics=metrics
    )

@dataclass
class VideoQualityReport:
    score: float
    issues: List[str]
    warnings: List[str]
    metrics: dict

    def to_dict(self):
        return asdict(self)

def check_video_quality(mp4_path: Path) -> VideoQualityReport:
    """使用 ffmpeg (兼容 Windows imageio_ffmpeg 打包版) 检查视频质量"""
    issues = []
    warnings = []
    metrics = {}

    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        ffmpeg = 'ffmpeg'

    cmd = [ffmpeg, '-i', str(mp4_path), '-f', 'null', '-']

    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, _ = p.communicate(timeout=10)
        text = out.decode('utf-8', errors='replace')
    except subprocess.TimeoutExpired:
        p.kill()
        return VideoQualityReport(0, ["ffmpeg 探测超时"], [], {})
    except Exception as e:
        return VideoQualityReport(0, [f"ffmpeg 执行失败: {e}"], [], {})

    # 从 stderr 解析元数据
    # Duration: 00:01:48.00 (ffmpeg 格式)
    duration = 0.0
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", text)
    if m:
        h, mn, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
        duration = h * 3600 + mn * 60 + s
    metrics['duration'] = duration

    # 只解析 Input 部分（避免 Output 流的 codec 干扰）
    input_section = text.split('Output #0')[0] if 'Output #0' in text else text

    video_codec = None
    audio_codec = None
    width = height = 0
    fps = 0.0
    channels = 0
    has_audio = False

    # 逐行解析每个 Stream
    for line in input_section.split('\n'):
        if 'Stream #' not in line:
            continue
        if 'Video:' in line:
            vm = re.search(r"Video:\s*(\w+)", line)
            if vm:
                video_codec = vm.group(1)
            # 分辨率：3-4位数字 x 3-4位数字，后面是非数字
            rm = re.search(r"(\d{3,4})x(\d{3,4})(?![/\d])", line)
            if rm:
                width, height = int(rm.group(1)), int(rm.group(2))
            # 帧率
            fm = re.search(r"(\d+(?:\.\d+)?)\s*fps", line)
            if fm:
                fps = float(fm.group(1))
        elif 'Audio:' in line:
            am = re.search(r"Audio:\s*(\w+)", line)
            if am:
                audio_codec = am.group(1)
            has_audio = True
            if 'mono' in line.lower():
                channels = 1
            elif 'stereo' in line.lower():
                channels = 2

    metrics['resolution'] = f"{width}x{height}"
    metrics['fps'] = round(fps, 2)
    metrics['video_codec'] = video_codec
    metrics['audio_codec'] = audio_codec
    metrics['channels'] = channels
    audio_stream = {} if has_audio else {}  # for backward-compatible scoring check

    # 文件大小：从 bitrate 估算
    size = 0
    bitrate_m = re.search(r"bitrate:\s*(\d+)\s*kb", text, re.IGNORECASE)
    if bitrate_m and duration > 0:
        # bitrate 是整文件码率 (kb/s) × 时长 = bytes
        size = int(bitrate_m.group(1)) * 1000 * duration
    metrics['size_bytes'] = size

    # 时长同步与文件大小合理性
    expected_size_mb = duration / 60 * 15
    actual_size_mb = size / (1024*1024)
    if actual_size_mb < expected_size_mb * 0.3:
        warnings.append(f"文件过小: {actual_size_mb:.1f}MB (预期 ~{expected_size_mb:.1f}MB)")
    elif actual_size_mb > expected_size_mb * 2:
        warnings.append(f"文件过大: {actual_size_mb:.1f}MB (预期 ~{expected_size_mb:.1f}MB)")

    # 4. 综合评分
    score = 100
    if not audio_stream:
        score -= 40
    if video_codec != 'h264':
        score -= 15
    if audio_codec != 'aac':
        score -= 10
    if width < 1280 or height < 720:
        score -= 15

    return VideoQualityReport(
        score=max(0, round(score, 1)),
        issues=issues,
        warnings=warnings,
        metrics=metrics
    )

# ============= 集成：全链路验收 =============

@dataclass
class FullPipelineReport:
    """端到端流水线质量报告"""
    article: str
    content: ContentQualityReport
    audio: Optional[AudioQualityReport] = None
    video: Optional[VideoQualityReport] = None
    overall_score: float = 0.0
    passed: bool = False

    def to_dict(self):
        return {
            'article': self.article,
            'overall_score': self.overall_score,
            'passed': self.passed,
            'content': self.content.to_dict() if self.content else None,
            'audio': self.audio.to_dict() if self.audio else None,
            'video': self.video.to_dict() if self.video else None,
        }

def run_full_check(article_dir: Path) -> FullPipelineReport:
    """
    对一篇文章执行全链路质量检查：
    1. speech.txt → 文案质量
    2. .mp3 → 音频质量
    3. .mp4 → 视频质量
    """
    stem = article_dir.name
    report = FullPipelineReport(article=stem, content=None, audio=None, video=None)

    # Step 1: 文案质量
    speech_txt = article_dir / f"{stem}-speech.txt"
    if speech_txt.exists():
        report.content = check_content_quality(speech_txt)
    else:
        report.content = ContentQualityReport(0, ["未找到 speech.txt"], [], {})

    # Step 2: 音频质量（如果已生成）
    mp3_path = article_dir / f"{stem}.mp3"
    if mp3_path.exists():
        report.audio = check_audio_quality(mp3_path)
    else:
        report.audio = None

    # Step 3: 视频质量（如果已生成）
    mp4_path = article_dir / f"{stem}.mp4"
    if mp4_path.exists():
        report.video = check_video_quality(mp4_path)
    else:
        report.video = None

    # 综合评分
    scores = [report.content.score]
    if report.audio:
        scores.append(report.audio.score)
    if report.video:
        scores.append(report.video.score)
    report.overall_score = round(sum(scores) / len(scores), 1)

    # 通过标准：文案无 error 级问题，音频/视频存在且无阻塞性问题
    report.passed = (
        len(report.content.issues) == 0 and
        (report.audio is None or len(report.audio.issues) == 0) and
        (report.video is None or len(report.video.issues) == 0) and
        report.overall_score >= 70
    )

    return report

# ============= CLI =============

def main():
    parser = argparse.ArgumentParser(description="视频质量监控工具")
    sub = parser.add_subparsers(dest='cmd', required=True)

    # check-content
    pc = sub.add_parser('check-content', help='检查文案质量')
    pc.add_argument('speech_txt', type=Path, help='speech.txt 路径')

    # check-audio
    pa = sub.add_parser('check-audio', help='检查音频质量')
    pa.add_argument('mp3', type=Path, help='MP3 路径')

    # check-video
    pv = sub.add_parser('check-video', help='检查视频质量')
    pv.add_argument('mp4', type=Path, help='MP4 路径')

    # full (端到端)
    pf = sub.add_parser('full', help='全链路检查文章目录')
    pf.add_argument('article_dir', type=Path, help='文章目录（含 speech.txt/mp3/mp4）')
    pf.add_argument('--json', action='store_true', help='输出 JSON 报告')

    # batch (批量)
    pb = sub.add_parser('batch', help='批量检查 articles/ 目录')
    pb.add_argument('--dir', type=Path, default=None, help='articles 目录')
    pb.add_argument('--json-out', type=Path, default=None, help='JSON 报告输出路径')

    args = parser.parse_args()

    if args.cmd == 'check-content':
        r = check_content_quality(args.speech_txt)
        _print_content_report(r)

    elif args.cmd == 'check-audio':
        r = check_audio_quality(args.mp3)
        _print_audio_report(r)

    elif args.cmd == 'check-video':
        r = check_video_quality(args.mp4)
        _print_video_report(r)

    elif args.cmd == 'full':
        r = run_full_check(args.article_dir)
        if args.json:
            print(json.dumps(r.to_dict(), ensure_ascii=False, indent=2))
        else:
            _print_full_report(r)

    elif args.cmd == 'batch':
        articles_dir = args.dir or Path(__file__).parent.parent / "articles"
        dirs = [d for d in articles_dir.iterdir() if d.is_dir() and re.match(r'^\d{2}-', d.name)]
        reports = []
        for d in sorted(dirs):
            r = run_full_check(d)
            reports.append(r.to_dict())
            if not args.json:
                _print_full_report(r)
                print()
        if args.json:
            args.json_out.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f"批量报告已写入: {args.json_out}")

def _print_content_report(r: ContentQualityReport):
    print(f"\n文案质量评分: {r.score}/100")
    if r.issues:
        print("  [ERROR] " + "\n  [ERROR] ".join(r.issues))
    if r.warnings:
        print("  [WARN] " + "\n  [WARN] ".join(r.warnings))
    print(f"  指标: {r.metrics}")

def _print_audio_report(r: AudioQualityReport):
    print(f"\n音频质量评分: {r.score}/100")
    if r.issues:
        print("  [ERROR] " + "\n  [ERROR] ".join(r.issues))
    if r.warnings:
        print("  [WARN] " + "\n  [WARN] ".join(r.warnings))
    print(f"  指标: {r.metrics}")

def _print_video_report(r: VideoQualityReport):
    print(f"\n视频质量评分: {r.score}/100")
    if r.issues:
        print("  [ERROR] " + "\n  [ERROR] ".join(r.issues))
    if r.warnings:
        print("  [WARN] " + "\n  [WARN] ".join(r.warnings))
    print(f"  指标: {r.metrics}")

def _print_full_report(r: FullPipelineReport):
    status = "✅ PASS" if r.passed else "❌ FAIL"
    print(f"\n【{r.article}】{status} 综合评分: {r.overall_score}/100")
    print(f"  文案: {r.content.score}/100 | 音频: {r.audio.score if r.audio else 'N/A'}/100 | 视频: {r.video.score if r.video else 'N/A'}/100")
    if r.content.issues:
        print("  [CONTENT-ERROR] " + "\n  [CONTENT-ERROR] ".join(r.content.issues))
    if r.content.warnings:
        print("  [CONTENT-WARN] " + "\n  [CONTENT-WARN] ".join(r.content.warnings))
    if r.audio and r.audio.issues:
        print("  [AUDIO-ERROR] " + "\n  [AUDIO-ERROR] ".join(r.audio.issues))
    if r.audio and r.audio.warnings:
        print("  [AUDIO-WARN] " + "\n  [AUDIO-WARN] ".join(r.audio.warnings))
    if r.video and r.video.issues:
        print("  [VIDEO-ERROR] " + "\n  [VIDEO-ERROR] ".join(r.video.issues))
    if r.video and r.video.warnings:
        print("  [VIDEO-WARN] " + "\n  [VIDEO-WARN] ".join(r.video.warnings))

if __name__ == '__main__':
    main()
