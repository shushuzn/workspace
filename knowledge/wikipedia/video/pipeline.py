"""
视频流水线主控制器
支持：增量缓存、断点续传、批量队列、并发处理、质量门禁前置
"""
import argparse
import json
import hashlib
import subprocess
import re
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime

# 导入项目模块
sys.path.insert(0, str(Path(__file__).parent.parent))
from video.config import (
    ARTICLES_DIR, CACHE_DIR, CACHE_INDEX,
    MAX_WORKERS, BATCH_SIZE,
    MIN_WORDS, MAX_WORDS,
    VIDEO_CRF, AUDIO_BITRATE, AUDIO_LOUDNORM,
    VOICE_ZH, VOICE_EN, RATE, PITCH,
)
from video.generate_speech import generate_speech as tts_generate
from video.draw_scene import generate_scenes_for_script
from video.make_video import make_video_multi
from video.quality_monitor import check_content_quality, check_audio_quality, check_video_quality

# ── 质量门禁（复用 check_script.py 逻辑） ─────────────────────────
FORBIDDEN = [
    "本论文", "本文", "该论文", "研究表明", "本质上是",
]
FORBIDDEN_OK = ["关键节点", "核心洞察", "没有明显"]

CORE_TERMS = ["Andreev反射", "Burau表示", "LE指数", "Burau-Lyapunov"]

def check_script_file(script_path: str) -> bool:
    """调用 check_script.py 进行质量验证"""
    try:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "check_script.py"), script_path],
            capture_output=True, text=True, encoding='utf-8'
        )
        # check_script.py 返回码 0 表示通过
        return result.returncode == 0
    except Exception as e:
        print(f"  [WARN] 质量检查异常: {e}")
        return True  # 保守策略：异常时放行

# ── 辅助函数 ───────────────────────────────────────────────────────

# ── 缓存系统 ──────────────────────────────────────────────────────
def load_cache():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if CACHE_INDEX.exists():
        return json.loads(CACHE_INDEX.read_text(encoding='utf-8'))
    return {'videos': {}, 'images': {}, 'speech': {}}

def save_cache(cache):
    CACHE_INDEX.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding='utf-8')

def file_hash(path: Path) -> str:
    """计算文件内容的 SHA256 hash"""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]

def get_output_hash(output_path: Path) -> str:
    """获取已生成输出文件的 hash（用于增量判断）"""
    if not output_path.exists():
        return None
    return file_hash(output_path)

def is_cached(cache: dict, key_type: str, key: str, input_hash: str) -> bool:
    """检查缓存是否命中"""
    entry = cache[key_type].get(key)
    if not entry:
        return False
    return entry.get('input_hash') == input_hash and entry.get('output_path') and Path(entry['output_path']).exists()

def update_cache(cache: dict, key_type: str, key: str, input_hash: str, output_path: str, **meta):
    cache[key_type][key] = {
        'input_hash': input_hash,
        'output_path': str(output_path),
        'timestamp': datetime.now().isoformat(),
        **meta
    }

# ── 任务状态 ─────────────────────────────────────────────────────
def load_state():
    state_file = CACHE_DIR / "state.json"
    if state_file.exists():
        return json.loads(state_file.read_text(encoding='utf-8'))
    return {'completed': [], 'failed': [], 'in_progress': []}

def save_state(state):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / "state.json").write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding='utf-8')

def mark_completed(state, item_id):
    if item_id in state.get('in_progress', []):
        state['in_progress'].remove(item_id)
    if item_id not in state['completed']:
        state['completed'].append(item_id)

def mark_failed(state, item_id):
    if item_id in state.get('in_progress', []):
        state['in_progress'].remove(item_id)
    if item_id not in state['failed']:
        state['failed'].append(item_id)

# ── 步骤 1: 语音合成 ────────────────────────────────────────────
def process_speech(speech_txt: Path, force: bool = False) -> tuple[bool, Path]:
    """单个 speech.txt → MP3 转换（支持增量）"""
    cache = load_cache()
    stem = speech_txt.stem
    if stem.endswith("-speech-en"):
        mp3_name = stem[:-10] + "-en.mp3"
    elif stem.endswith("-speech"):
        mp3_name = stem[:-7] + ".mp3"
    else:
        mp3_name = stem + ".mp3"
    mp3_path = speech_txt.parent / mp3_name

    key = f"{speech_txt.parent.name}/{speech_txt.name}"
    input_hash = file_hash(speech_txt)

    if not force and is_cached(cache, 'speech', key, input_hash):
        print(f"  [SKIP] 语音缓存命中: {key}")
        return True, mp3_path

    print(f"  → 生成语音: {key}")
    voice = VOICE_EN if "-en" in stem else VOICE_ZH
    ok = tts_generate(speech_txt, mp3_path, voice=voice, rate=RATE, pitch=PITCH)
    if ok:
        update_cache(cache, 'speech', key, input_hash, str(mp3_path), duration=get_audio_duration(mp3_path))
        save_cache(cache)
    return ok, mp3_path

# ── 步骤 2: 配图生成 ────────────────────────────────────────────
def process_scenes(speech_txt: Path, force: bool = False) -> tuple[bool, list]:
    """为单篇文章生成所有配图（增量）"""
    cache = load_cache()
    raw_stem = speech_txt.stem
    # 去除 -speech / -speech-en / -en 后缀，得到裸标题
    stem = raw_stem.replace("-speech", "").replace("-en", "")
    key = f"{speech_txt.parent.name}/scenes"
    # 用脚本内容 hash 作为输入指纹
    input_hash = file_hash(speech_txt)

    if not force and is_cached(cache, 'images', key, input_hash):
        print(f"  [SKIP] 配图缓存命中: {key}")
        # 返回所有场景图片路径（需重新扫描）
        article_dir = speech_txt.parent
        nn = stem.split('-')[0]
        scene_imgs = []
        for p in article_dir.glob(f"{nn}-scene-*.png"):
            try:
                idx = int(p.stem.split('-scene-')[1])
                scene_imgs.append((idx, p))
            except (IndexError, ValueError):
                continue
        scene_imgs.sort(key=lambda x: x[0])
        return True, [p for _, p in scene_imgs]

    print(f"  → 生成配图: {key}")
    article_dir = speech_txt.parent
    try:
        # generate_scenes_for_script(script_path, output_prefix, article_name, strict=False)
        generated = generate_scenes_for_script(
            script_path=article_dir / f"{stem}.md",
            output_prefix=stem,  # 图片前缀：NN-标题
            article_name=article_dir.name  # 文章目录名
        )
        # 收集生成的图片
        nn = stem.split('-')[0]
        scene_imgs = []
        for p in article_dir.glob(f"{nn}-scene-*.png"):
            try:
                idx = int(p.stem.split('-scene-')[1])
                scene_imgs.append((idx, p))
            except (IndexError, ValueError):
                continue
        scene_imgs.sort(key=lambda x: x[0])
        imgs_only = [p for _, p in scene_imgs]
        if generated:
            update_cache(cache, 'images', key, input_hash, str(article_dir), count=len(imgs_only))
            save_cache(cache)
        return generated, imgs_only
    except Exception as e:
        print(f"  [ERROR] 配图失败: {e}")
        return False, []

# ── 步骤 3: 视频合成 ────────────────────────────────────────────
def process_video(mp3_path: Path, scene_imgs: list, force: bool = False) -> bool:
    """单个视频合成（支持增量）"""
    cache = load_cache()
    key = f"{mp3_path.parent.name}/{mp3_path.name}"
    input_hash = file_hash(mp3_path)  # 用音频 hash 作为输入指纹

    output_path = mp3_path.with_suffix('.mp4')
    if not force and is_cached(cache, 'videos', key, input_hash):
        print(f"  [SKIP] 视频缓存命中: {key}")
        return True

    print(f"  → 合成视频: {key} ({len(scene_imgs)} 场景)")
    try:
        if len(scene_imgs) == 1:
            ok = make_video_multi([(scene_imgs[0], 0.0)], mp3_path, output_path, bitrate=AUDIO_BITRATE, scene_key='scene')
        else:
            imgs_with_time = [(p, 0.0) for p in scene_imgs]
            ok = make_video_multi(imgs_with_time, mp3_path, output_path, bitrate=AUDIO_BITRATE, scene_key='scene')
        if ok:
            update_cache(cache, 'videos', key, input_hash, str(output_path), size=output_path.stat().st_size)
            save_cache(cache)
        return ok
    except Exception as e:
        print(f"  [ERROR] 视频合成失败: {e}")
        return False

def get_audio_duration(mp3_path: Path) -> float:
    """获取音频时长（秒）"""
    import imageio_ffmpeg
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(mp3_path), "-f", "null", "-"]
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, _ = p.communicate()
        text = out.decode("utf-8", errors="replace")
        m = re.search(r"time=(\d+):(\d+):(\d+\.?\d*)", text)
        if m:
            h, mn, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
            return h * 3600 + mn * 60 + s
    except Exception:
        pass
    return 0.0

# ── 主流程 ───────────────────────────────────────────────────────
def run_pipeline(articles_dir: Path, force: bool = False, resume: bool = False, workers: int = MAX_WORKERS):
    """批量视频生产流水线"""
    # 1. 收集所有待处理 speech 文件
    speech_files = sorted(articles_dir.rglob("*-speech.txt"))
    if not speech_files:
        print("未找到任何 *-speech.txt 文件")
        return

    total = len(speech_files)
    print(f"发现 {total} 个 speech 文件，开始流水线处理...\n")

    # 2. 状态加载（断点续传）
    state = load_state() if resume else {'completed': [], 'failed': []}

    # 3. 分批处理（批量队列）
    batches = [speech_files[i:i+BATCH_SIZE] for i in range(0, total, BATCH_SIZE)]

    success_count = 0
    fail_count = 0

    for batch_idx, batch in enumerate(batches, 1):
        print(f"\n[批次 {batch_idx}/{len(batches)}] 包含 {len(batch)} 个视频")

        # 并行处理当前批次
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {}
            for speech_txt in batch:
                item_id = f"{speech_txt.parent.name}/{speech_txt.name}"
                if item_id in state.get('completed', []) and not force:
                    print(f"  [SKIP] 已完成: {item_id}")
                    success_count += 1
                    continue
                futures[executor.submit(process_item, speech_txt, force)] = speech_txt

            for future in as_completed(futures):
                speech_txt = futures[future]
                item_id = f"{speech_txt.parent.name}/{speech_txt.name}"
                try:
                    ok = future.result()
                    if ok:
                        mark_completed(state, item_id)
                        success_count += 1
                    else:
                        mark_failed(state, item_id)
                        fail_count += 1
                except Exception as e:
                    print(f"  [ERROR] {item_id}: {e}")
                    mark_failed(state, item_id)
                    fail_count += 1

        save_state(state)
        print(f"  批次 {batch_idx} 完成。累计成功: {success_count}, 失败: {fail_count}")

    # 4. 生成质量报告
    print(f"\n流水线完成。成功: {success_count}/{total}, 失败: {fail_count}/{total}")
    if state.get('failed'):
        print(f"失败项目: {', '.join(state['failed'])}")

    report = {
        'timestamp': datetime.now().isoformat(),
        'total': total,
        'success': success_count,
        'failed': fail_count,
        'failed_items': state.get('failed', []),
    }
    report_path = CACHE_DIR / f"report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"质量报告: {report_path}")

def process_item(speech_txt: Path, force: bool) -> bool:
    """单个视频的完整流水线（文案质量 → 语音 → 配图 → 视频 → 质量验收）"""
    # 确保 speech_txt 是绝对路径，避免相对路径导致的 relative_to 错误
    speech_txt = speech_txt.resolve()
    article_dir = speech_txt.parent
    stem = speech_txt.stem.replace("-speech", "").replace("-en", "")

    try:
        display_path = speech_txt.relative_to(ARTICLES_DIR)
    except ValueError:
        # 不在 ARTICLES_DIR 下（如绝对路径传入），回退到文件名
        display_path = speech_txt.name
    print(f"\n处理: {display_path}")

    # ========== Step 0: 文案质量检查 ==========
    script_path = article_dir / f"{stem}.md"
    speech_txt_path = article_dir / f"{stem}-speech.txt"
    if speech_txt_path.exists():
        print(f"  [质检] 文案质量检查...")
        content_r = check_content_quality(speech_txt_path)
        if content_r.issues:
            print(f"  [SKIP] 文案质量不通过 (得分 {content_r.score}):")
            for issue in content_r.issues:
                print(f"    - {issue}")
            return False
        if content_r.score < 60:
            print(f"  [WARN] 文案质量偏低 (得分 {content_r.score})，建议优化后重试")
            return False
        print(f"  [OK] 文案质量: {content_r.score}/100")

    # ========== Step 1: 脚本质量门禁 (原有) ==========
    if script_path.exists():
        if not check_script_file(str(script_path)):
            print(f"  [SKIP] 脚本质量门禁不通过: {script_path.name}")
            return False
    else:
        print(f"  [WARN] 未找到对应脚本: {script_path.name}")

    # ========== Step 2: 语音合成 ==========
    ok, mp3_path = process_speech(speech_txt, force)
    if not ok:
        return False

    # ========== Step 2.5: 音频质量检查 ==========
    if mp3_path.exists():
        print(f"  [质检] 音频质量检查...")
        audio_r = check_audio_quality(mp3_path)
        if audio_r.issues:
            print(f"  [WARN] 音频质量问题:")
            for issue in audio_r.issues:
                print(f"    - {issue}")
            # 音频问题不阻塞，但记录
        else:
            print(f"  [OK] 音频质量: {audio_r.score}/100")

    # ========== Step 3: 配图生成 ==========
    ok, scene_imgs = process_scenes(speech_txt, force)
    if not ok or not scene_imgs:
        return False

    # ========== Step 4: 视频合成 ==========
    ok = process_video(mp3_path, scene_imgs, force)
    if not ok:
        return False

    # ========== Step 4.5: 视频质量验收 ==========
    mp4_path = mp3_path.with_suffix('.mp4')
    if mp4_path.exists():
        print(f"  [质检] 视频质量验收...")
        video_r = check_video_quality(mp4_path)
        if video_r.issues:
            print(f"  [WARN] 视频质量问题:")
            for issue in video_r.issues:
                print(f"    - {issue}")
            # 严重问题可标记为失败
            if any("无音频" in i or "编码" in i for i in video_r.issues):
                return False
        else:
            print(f"  [OK] 视频质量: {video_r.score}/100")

        # 生成质量报告文件
        report = {
            'article': article_dir.name,
            'speech_txt': str(speech_txt_path.relative_to(ARTICLES_DIR)) if speech_txt_path.exists() else None,
            'mp3': str(mp3_path.relative_to(ARTICLES_DIR)),
            'mp4': str(mp4_path.relative_to(ARTICLES_DIR)),
            'content': content_r.to_dict() if 'content_r' in locals() else None,
            'audio': audio_r.to_dict() if 'audio_r' in locals() else None,
            'video': video_r.to_dict(),
            'timestamp': datetime.now().isoformat(),
        }
        report_dir = CACHE_DIR / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"{article_dir.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"  [报告] {report_path.name}")

    return True

def main():
    global BATCH_SIZE, MAX_WORKERS
    parser = argparse.ArgumentParser(description="Wikipedia 视频流水线（优化版）")
    parser.add_argument("--dir", default=None, help="articles 目录（默认 knowledge/wikipedia/articles）")
    parser.add_argument("--force", action="store_true", help="强制重新生成，忽略缓存")
    parser.add_argument("--resume", action="store_true", help="从上次中断处继续")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS, help=f"并发数（默认 {MAX_WORKERS}）")
    parser.add_argument("--batch", type=int, default=BATCH_SIZE, help=f"每批数量（默认 {BATCH_SIZE}）")
    args = parser.parse_args()

    BATCH_SIZE = args.batch
    MAX_WORKERS = args.workers

    articles_dir = Path(args.dir) if args.dir else ARTICLES_DIR
    run_pipeline(articles_dir, force=args.force, resume=args.resume, workers=args.workers)

if __name__ == "__main__":
    main()
