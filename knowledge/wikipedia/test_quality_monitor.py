"""
quality_monitor.py 测试套件
测试：文案质量、音频质量、视频质量、全链路
"""
import json
import sys
from pathlib import Path
import subprocess

# 添加 video 目录到路径（test_quality_monitor.py 在 wikipedia/ 下，video/ 在 wikipedia/video/ 下）
sys.path.insert(0, str(Path(__file__).parent / "video"))

from quality_monitor import (
    check_content_quality,
    check_audio_quality,
    check_video_quality,
    run_full_check,
    ContentQualityReport,
    AudioQualityReport,
    VideoQualityReport,
)

# articles 目录（与 test_quality_monitor.py 同级）
ARTICLES_DIR = Path(__file__).parent / "articles"

def create_test_speech(path: Path, content: str):
    """创建测试用 speech.txt"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def test_content_good():
    """测试用例 1：优秀文案（应高分通过）"""
    # 符合 B站/YouTube 科普视频标准：450-750字、口语化、数学符号已替换
    good_text = """sigma 1 和 sigma 2 是辫群的生成元。它们满足杨-巴克斯特方程。

这个方程非常重要。它保证了辫子的编织过程是可逆的。

想象三根线：上面三根线，下面三根线。上面的线从左到右分别是蓝、粉、绿。下面的线也是同样的颜色。

当蓝线穿过粉线时，我们记作 sigma 1。当粉线穿过绿线时，我们记作 sigma 2。

注意：sigma 1 sigma 2 不等于 sigma 2 sigma 1。交换的顺序不同，结果就不一样。

这就是非阿贝尔的含义。在数学上，运算的顺序会影响最终结果。

LE 指数就是 Burau 表示的最大特征值。它量化了权限图的危险程度。

聚焦型结构里，LE 值高，说明少数节点掌握大量权限。分散型结构里，LE 值低，权限分布均匀。

所以，通过 LE 的变化，我们可以判断云账号是否容易被攻击。

简单说：LE 高 = 危险集中，LE 低 = 安全分散。这就是我们为什么需要关注这个指数。"""
    tmp_dir = Path(__file__).parent / "test_data" / "good_article"
    create_test_speech(tmp_dir / "01-test-good-speech.txt", good_text)
    r = check_content_quality(tmp_dir / "01-test-good-speech.txt")
    assert r.score >= 70, f"优秀文案得分应 ≥70，实际 {r.score}"
    assert len(r.issues) == 0, f"优秀文案不应有 error 问题，实际 {r.issues}"
    print(f"✅ test_content_good: score={r.score}")

def test_content_academic():
    """测试用例 2：学术腔文案（应扣分并警告）"""
    academic_text = """本论文提出了一种基于辫群理论的特权升级检测方法。

本文首先定义了 IAM 权限图的编织表示。本文工作证明了 LE 指数的有效性。

实验结果表明，我们的方法能够准确识别特权升级路径。数据表明，LE 值在聚焦型结构中显著升高。

因此，我们可以得出结论：非阿贝尔结构是检测的关键。

本质上，这是一种拓扑数学的应用。"""
    tmp_dir = Path(__file__).parent / "test_data" / "academic_article"
    create_test_speech(tmp_dir / "02-academic-speech.txt", academic_text)
    r = check_content_quality(tmp_dir / "02-academic-speech.txt")
    assert r.score < 80, f"学术腔文案应扣分，实际 {r.score}"
    assert any("学术腔" in w for w in r.issues + r.warnings), "应检测到学术腔"
    print(f"✅ test_content_academic: score={r.score}, issues={r.issues}")

def test_content_short():
    """测试用例 3：字数不足（应警告）"""
    short_text = """σ₁ 和 σ₂ 交换。非阿贝尔。"""
    tmp_dir = Path(__file__).parent / "test_data" / "short_article"
    create_test_speech(tmp_dir / "03-short-speech.txt", short_text)
    r = check_content_quality(tmp_dir / "03-short-speech.txt")
    assert any("字数" in w for w in r.warnings), "应警告字数不足"
    print(f"✅ test_content_short: score={r.score}, warnings={r.warnings}")

def test_content_math_unreplaced():
    """测试用例 4：数学符号未替换（应 error）"""
    math_text = """使用 σ₁ 和 λᵢ 计算。∑ 所有值。α 和 β 很关键。"""
    tmp_dir = Path(__file__).parent / "test_data" / "unreplaced_math"
    create_test_speech(tmp_dir / "04-unreplaced-speech.txt", math_text)
    r = check_content_quality(tmp_dir / "04-unreplaced-speech.txt")
    assert len(r.issues) > 0, "未替换数学符号应报 error"
    assert any("数学符号" in i for i in r.issues), "应检测到未替换符号"
    print(f"✅ test_content_math_unreplaced: score={r.score}, issues={r.issues}")

def test_content_long_sentence():
    """测试用例 5：超长句（应警告）"""
    long_sentence_text = """辫群元素由生成元 σ₁ σ₂ σ₃ 通过有限次的乘法操作组合而成，每一个 σᵢ 代表相邻两根线的交换动作，而整个辫子的等价类构成一个群结构，这个群的单位元是恒等辫子即没有任何交叉的直上直下的配置，每个元素都有对应的逆元可以通过反向编织得到，同时满足结合律即先编织 A 再编织 B 最后编织 C 等同于先编织 A 和 B 的组合再编织 C，这些性质共同定义了辫群作为数学对象的完备性。"""
    tmp_dir = Path(__file__).parent / "test_data" / "long_sentence"
    create_test_speech(tmp_dir / "05-long-speech.txt", long_sentence_text)
    r = check_content_quality(tmp_dir / "05-long-speech.txt")
    assert any("平均句长" in i for i in r.issues), "应检测到超长句"
    print(f"✅ test_content_long_sentence: score={r.score}, issues={r.issues}")

def test_audio_good():
    """测试用例 6：音频质量（需真实 MP3）"""
    # 找一个已存在的 MP3
    sample_mp3 = None
    for p in ARTICLES_DIR.rglob("*.mp3"):
        if "speech-tts" not in p.name:
            sample_mp3 = p
            break
    if sample_mp3 and sample_mp3.exists():
        r = check_audio_quality(sample_mp3)
        print(f"✅ test_audio_good: score={r.score}, metrics={r.metrics}")
    else:
        print("⏭️  test_audio_good: 未找到真实 MP3，跳过")

def test_video_good():
    """测试用例 7：视频质量（需真实 MP4）"""
    sample_mp4 = None
    for p in ARTICLES_DIR.rglob("*.mp4"):
        if "论文解读" in p.name:
            sample_mp4 = p
            break
    if sample_mp4 and sample_mp4.exists():
        r = check_video_quality(sample_mp4)
        print(f"✅ test_video_good: score={r.score}, metrics={r.metrics}")
    else:
        print("⏭️  test_video_good: 未找到真实 MP4，跳过")

def test_full_pipeline():
    """测试用例 8：全链路验收（需完整文章目录）"""
    # 找一个完整的文章目录（含 speech.txt + mp3 + mp4）
    sample_dir = None
    for d in ARTICLES_DIR.iterdir():
        if not d.is_dir():
            continue
        speech = d.glob("*-speech.txt")
        mp3 = d.glob("*.mp3")
        mp4 = d.glob("*.mp4")
        if any(speech) and any(mp3) and any(mp4):
            sample_dir = d
            break
    if sample_dir:
        r = run_full_check(sample_dir)
        print(f"✅ test_full_pipeline: overall={r.overall_score}, passed={r.passed}")
        print(f"  内容: {r.content.score} | 音频: {r.audio.score if r.audio else 'N/A'} | 视频: {r.video.score if r.video else 'N/A'}")
    else:
        print("⏭️  test_full_pipeline: 未找到完整文章目录，跳过")

def run_all():
    print("=" * 50)
    print("视频质量监控模块测试")
    print("=" * 50)

    tests = [
        test_content_good,
        test_content_academic,
        test_content_short,
        test_content_math_unreplaced,
        test_content_long_sentence,
        test_audio_good,
        test_video_good,
        test_full_pipeline,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} 异常: {e}")
            failed += 1

    print()
    print("=" * 50)
    print(f"结果: {passed} 通过, {failed} 失败")
    print("=" * 50)

    return failed == 0

if __name__ == '__main__':
    success = run_all()
    sys.exit(0 if success else 1)
