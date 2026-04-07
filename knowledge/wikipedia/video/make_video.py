"""
视频合成：图片 + MP3 → MP4（支持多画面按时序切换）
依赖: pip install imageio-ffmpeg
"""
import argparse
import subprocess
import sys
import tempfile
import re
from pathlib import Path
import imageio_ffmpeg
from PIL import Image

def get_duration(file_path):
    """用 ffmpeg -i 读取音频时长（秒）"""
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(file_path), "-f", "null", "-"]
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
    return None

def ensure_even(n):
    """返回最近的偶数"""
    return n if n % 2 == 0 else n + 1

def crf_for_scene(scene_key):
    """根据场景类型返回合适的 CRF 值（越低越清晰）"""
    # 公式/图表场景需要更高清晰度，用更低的 CRF
    low_crf_keys = {'formula', 'le_formula', 'burau_pipeline', 'abelian_proof',
                    'band_structure', 'braid_group', 'cloud_graph', 'le_flow',
                    'thermoelectric', 'iv_curve'}
    # 封面/简单文字用中间值
    if scene_key in low_crf_keys:
        return 18  # 高清晰度
    return 22  # 标准清晰度

def get_x264_preset(complexity='medium'):
    """根据场景复杂度返回 x264 preset（越慢=压缩效率越高）"""
    presets = {'low': 'fast', 'medium': 'medium', 'high': 'slow'}
    return presets.get(complexity, 'medium')

def get_img_size(img_path):
    """用 PIL 读取图片尺寸"""
    try:
        with Image.open(img_path) as im:
            return im.size
    except Exception:
        return None

def make_video_single(img_path, audio_path, output_path, bitrate=None, scene_key='default'):
    """单图片 + 音频 → 视频（优化版：感知场景类型 + 音频标准化 + fade）"""
    size = get_img_size(img_path)
    if not size:
        print(f"  [ERROR] 无法读取图片尺寸: {img_path}")
        return False
    w, h = size
    w_even = ensure_even(w)
    h_even = ensure_even(h)
    scale_filter = None
    if w != w_even or h != h_even:
        scale_filter = f"scale={w_even}:{h_even}:force_original_aspect_ratio=decrease,pad={w_even}:{h_even}:(ow-iw)/2:(oh-ih)/2"

    duration = get_duration(audio_path)
    if duration is None:
        print(f"  [ERROR] 无法读取音频时长: {audio_path}")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    crf = crf_for_scene(scene_key)
    preset = get_x264_preset('medium' if 'cover' in scene_key else 'medium')
    # fade in/out：时长<3s时跳过，避免掐尾
    fade_duration = min(0.5, duration * 0.05) if duration >= 3 else 0
    # 拼装 video filter chain
    vf_parts = []
    if scale_filter:
        vf_parts.append(scale_filter)
    if fade_duration > 0:
        vf_parts.append(f"fade=t=in:st=0:d={fade_duration}:alpha=1")
        vf_parts.append(f"fade=t=out:st={duration - fade_duration}:d={fade_duration}:alpha=1")
    vf = ",".join(vf_parts) if vf_parts else None

    cmd = [ffmpeg_exe, "-y",
           "-loop", "1", "-framerate", "1",
           "-i", str(img_path),
           "-i", str(audio_path),
           "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
           "-tune", "stillimage"]
    if bitrate:
        cmd += ["-b:v", bitrate]
    if vf:
        cmd += ["-vf", vf]
    cmd += ["-c:a", "aac", "-b:a", "192k",
            "-af", "loudnorm=I=-16:LRA=11:tp=-1.5",
            "-pix_fmt", "yuv420p",
            "-shortest", "-t", str(duration + 0.5),
            str(output_path)]

    result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore')
    if result.returncode != 0:
        print(f"  [ERROR] ffmpeg failed:\n{result.stderr[-300:]}")
        return False

    size_bytes = output_path.stat().st_size
    print(f"  [OK] {output_path.name} ({size_bytes:,} bytes, {duration:.1f}s)")
    return True

def make_video_multi(img_paths, audio_path, output_path, bitrate=None, scene_key='default'):
    """多图片按时序切换 + 音频 → 视频（优化版：crf感知 + fade + 音频标准化）
    img_paths: [(img, start_second), ...] 按时间顺序
    策略：①视频段单独编码(无声) ②concat ③音频与 concat 视频混流
    """
    duration = get_duration(audio_path)
    if duration is None:
        print(f"  [ERROR] 无法读取音频时长: {audio_path}")
        return False

    n = len(img_paths)
    seg_duration = duration / n

    sizes = [get_img_size(p) for p, _ in img_paths]
    if any(s is None for s in sizes):
        print(f"  [ERROR] 无法读取某些图片尺寸")
        return False
    w, h = sizes[0]
    w_even = ensure_even(w)
    h_even = ensure_even(h)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    crf = crf_for_scene(scene_key)

    seg_files = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for i, (img_path, start_t) in enumerate(img_paths):
            seg_path = Path(tmpdir) / f"seg_{i:02d}.mp4"
            seg_files.append(seg_path)

            vf_parts = []
            if w != w_even or h != h_even:
                vf_parts.append(f"scale={w_even}:{h_even}:force_original_aspect_ratio=decrease,pad={w_even}:{h_even}:(ow-iw)/2:(oh-ih)/2")
            # 每段视频添加淡入（首段）或淡出（末段）
            fade_in_dur = min(0.5, seg_duration * 0.03) if i == 0 else 0
            fade_out_dur = min(0.5, seg_duration * 0.03) if i == n - 1 else 0
            if fade_in_dur > 0:
                vf_parts.append(f"fade=t=in:st=0:d={fade_in_dur}:alpha=1")
            if fade_out_dur > 0:
                vf_parts.append(f"fade=t=out:st={seg_duration - fade_out_dur}:d={fade_out_dur}:alpha=1")

            # 视频段无声编码
            cmd = [
                ffmpeg_exe, "-y",
                "-loop", "1", "-framerate", "1",
                "-i", str(img_path),
                "-t", str(seg_duration + 0.05),
                "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
                "-tune", "stillimage",
            ]
            if bitrate:
                cmd.extend(["-b:v", bitrate])
            if vf_parts:
                cmd.extend(["-vf", ",".join(vf_parts)])
            cmd.extend([
                "-pix_fmt", "yuv420p",
                "-an",
                str(seg_path),
            ])

            r = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore')
            if r.returncode != 0:
                print(f"  [ERROR] 片段{i} 编码失败: {r.stderr[-200:]}")
                return False

        # concat 所有视频段
        concat_list = Path(tmpdir) / "concat.txt"
        with open(concat_list, 'w') as f:
            for seg in seg_files:
                f.write(f"file '{seg}'\n")

        concat_path = Path(tmpdir) / "concat_video.mp4"
        r = subprocess.run([
            ffmpeg_exe, "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_list),
            "-c:v", "libx264", "-crf", str(crf),
            "-preset", "medium",
            "-an",
            str(concat_path),
        ], capture_output=True, encoding='utf-8', errors='ignore')
        if r.returncode != 0:
            print(f"  [ERROR] concat failed:\n{r.stderr[-300:]}")
            return False

        # 音频与 concat 视频混流：用 atrim+adelay 将每段音频对齐到正确位置
        # 构造每段的音频片段（带音频标准化）
        audio_seg_files = []
        for i in range(n):
            seg_audio = Path(tmpdir) / f"audio_seg_{i:02d}.aac"
            audio_seg_files.append(seg_audio)
            start_s = seg_duration * i
            delay_ms = int(start_s * 1000)
            r = subprocess.run([
                ffmpeg_exe, "-y",
                "-ss", str(start_s),
                "-i", str(audio_path),
                "-t", str(seg_duration),
                "-af", f"adelay={delay_ms}|{delay_ms},loudnorm=I=-16:LRA=11:tp=-1.5",
                "-c:a", "aac",
                str(seg_audio),
            ], capture_output=True, encoding='utf-8', errors='ignore')
            if r.returncode != 0:
                print(f"  [ERROR] 音频片段{i} 失败:\n{r.stderr[-200:]}")
                return False

        # concat 所有音频段
        audio_list = Path(tmpdir) / "concat_audio.txt"
        with open(audio_list, 'w') as f:
            for af in audio_seg_files:
                f.write(f"file '{af}'\n")

        concat_audio = Path(tmpdir) / "concat_audio.aac"
        r = subprocess.run([
            ffmpeg_exe, "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(audio_list),
            "-c:a", "aac",
            str(concat_audio),
        ], capture_output=True, encoding='utf-8', errors='ignore')
        if r.returncode != 0:
            print(f"  [ERROR] audio concat failed:\n{r.stderr[-300:]}")
            return False

        # 最终合并视频+音频
        r = subprocess.run([
            ffmpeg_exe, "-y",
            "-i", str(concat_path),
            "-i", str(concat_audio),
            "-c:v", "libx264", "-crf", str(crf),
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(output_path),
        ], capture_output=True, encoding='utf-8', errors='ignore')
        if r.returncode != 0:
            print(f"  [ERROR] final merge failed:\n{r.stderr[-300:]}")
            return False

    size_bytes = output_path.stat().st_size
    print(f"  [OK] {output_path.name} ({size_bytes:,} bytes, {n} scenes × {seg_duration:.1f}s, CRF={crf})")
    return True

def find_scene_images(mp3_path):
    """为 MP3 找封面图和所有场景图片"""
    stem = mp3_path.stem
    nn = stem.split('-')[0]
    article_dir = mp3_path.parent

    # 封面图
    cover_path = article_dir / f"{nn}-cover.png"
    has_cover = cover_path.exists()

    # 查找 scene 图片（NN-scene-XX.png）
    import re
    scene_imgs = []
    for p in article_dir.glob(f"{nn}-scene-*.png"):
        m = re.search(r'-scene-(\d+)', p.name)
        if m:
            idx = int(m.group(1))
            scene_imgs.append((idx, p))
    scene_imgs.sort(key=lambda x: x[0])

    if not scene_imgs:
        # 回退：找单图
        candidates = [
            article_dir / f"{stem}.png",
            article_dir / f"{stem}.jpg",
        ]
        img = next((p for p in candidates if p.exists()), None)
        if img:
            return [(cover_path, img) if has_cover else (None, img)], 'cover'
        return [], 'default'

    return [(p, None) for _, p in scene_imgs], 'scene'

def infer_scene_key(mp3_path):
    """从 MP3 文件名推断场景类型，用于 CRF 选择"""
    name = mp3_path.stem.lower()
    # 公式/理论类 → 低 CRF
    if any(k in name for k in ['formula', 'le_', 'burau', 'abelian', 'band', ' braid', 'cloud_graph']):
        return 'formula'
    # 封面/标题 → 较高 CRF
    if 'cover' in name or len(mp3_path.parent.glob("*-scene-*.png")) <= 1:
        return 'cover'
    # 图表/流程 → 中等
    return 'scene'

def make_video(img_path, audio_path, output_path, bitrate=None, scene_key='default'):
    """兼容性别名"""
    return make_video_single(img_path, audio_path, output_path, bitrate=bitrate, scene_key=scene_key)

def main():
    parser = argparse.ArgumentParser(description="视频合成（支持多画面按时序切换）")
    parser.add_argument("mp3_file", nargs="?", help="MP3 路径（不指定则处理所有）")
    parser.add_argument("--dir", default=None, help="articles 目录")
    parser.add_argument("--bitrate", default=None, help="视频码率，如 1M/2M/5M，默认用 libx264 internal default")
    args = parser.parse_args()

    articles_dir = Path(args.dir) if args.dir else Path(__file__).parent.parent / "articles"

    if args.mp3_file:
        mp3_path = Path(args.mp3_file)
        scene_imgs, inferred_key = find_scene_images(mp3_path)
        if not scene_imgs:
            print(f"未找到配图: {mp3_path.stem}")
            return
        output = mp3_path.with_suffix(".mp4")
        scene_key = infer_scene_key(mp3_path)
        if len(scene_imgs) == 1 and scene_imgs[0][0] is not None:
            make_video_multi([(scene_imgs[0][0], 0.0)], mp3_path, output, bitrate=args.bitrate, scene_key=scene_key)
        else:
            imgs_only = [(p, 0.0) for p, _ in scene_imgs]
            make_video_multi(imgs_only, mp3_path, output, bitrate=args.bitrate, scene_key=scene_key)
        return

    # 处理所有 speech MP3（跳过 speech-tts）
    mp3_files_en = [p for p in articles_dir.rglob("*.mp3")
                    if "speech-tts" not in p.name and p.stem.endswith("-en")]
    mp3_files_zh = [p for p in articles_dir.rglob("*.mp3")
                    if "speech-tts" not in p.name and "-en" not in p.stem and p.name.endswith("论文解读.mp3")]
    mp3_files = mp3_files_en + mp3_files_zh
    if not mp3_files:
        print("未找到 speech MP3 文件")
        return

    for mp3 in sorted(mp3_files):
        scene_imgs, inferred_key = find_scene_images(mp3)
        if not scene_imgs:
            print(f"  [WARN] 无配图: {mp3.stem}")
            continue
        # -en.mp3 → -en.mp4，其他 → .mp4
        if mp3.stem.endswith("-en"):
            output = mp3.parent / (mp3.stem + ".mp4")
        else:
            output = mp3.with_suffix(".mp4")
        imgs_only = [(p, 0.0) for p, _ in scene_imgs]
        scene_key = infer_scene_key(mp3)
        print(f"处理: {mp3.name} → {len(imgs_only)} scenes [key={scene_key}]")
        make_video_multi(imgs_only, mp3, output, bitrate=args.bitrate, scene_key=scene_key)

if __name__ == "__main__":
    main()
