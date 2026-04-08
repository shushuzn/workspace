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

# ── 动画场景注册表 ──────────────────────────────────────────────────
# 格式: {scene_key: (anim_func, (extra_args...))}
# anim_func 签名: (out_path, *extra_args, progress: float) -> None
_ANIMATION_SCENES = {}

def register_animation(scene_key, anim_func, *extra_args):
    """注册可动画化场景"""
    _ANIMATION_SCENES[scene_key] = (anim_func, extra_args)

# ── 预注册动画场景（从 draw_scene 导入）─────────────────────────────
try:
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent))
    from draw_scene import _draw_band_structure, _draw_iv_curve, _draw_burau_pipeline
    register_animation('band_structure', _draw_band_structure)
    register_animation('iv_curve', _draw_iv_curve)
    register_animation('burau_pipeline', _draw_burau_pipeline)
    del _sys
except ImportError:
    pass  # draw_scene 未安装时静默

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

def _read_scene_meta(img_path):
    """读取同目录同名 .scene.json，返回 (desc, key)"""
    json_path = Path(img_path).with_suffix('.scene.json')
    if json_path.exists():
        try:
            import json
            data = json.loads(json_path.read_text(encoding='utf-8'))
            return data.get('desc', ''), data.get('key', '')
        except Exception:
            pass
    return '', ''


def _infer_scene_key_from_path(img_path):
    """从图片路径推断 scene_key"""
    name = Path(img_path).stem.lower()
    for key in _ANIMATION_SCENES:
        if key.lower().replace('_', '') in name.replace('_', '').replace('-', ''):
            return key
    low_keys = {'band_structure', 'iv_curve', 'thermoelectric', 'le_formula',
                'burau_pipeline', 'abelian_proof', 'cloud_graph'}
    for k in low_keys:
        if k in name:
            return k
    return 'default'


def crf_for_scene(scene_key):
    """根据场景类型返回合适的 CRF 值（越低越清晰）"""
    # 公式/图表场景需要更高清晰度，用更低的 CRF
    low_crf_keys = {'formula', 'le_formula', 'burau_pipeline', 'abelian_proof',
                    'band_structure', 'braid_group', 'cloud_graph', 'le_flow',
                    'thermoelectric', 'iv_curve'}
    # 封面/简单文字用中间值
    if scene_key in low_crf_keys:
        return 16  # 高清晰度（从18提升）
    return 20  # 标准清晰度（从22提升）

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


def _encode_scene_animation(anim_func, anim_kwargs, output_path, w_even, h_even, dur, crf, fps=18):
    """动画帧编码：调用绘图函数生成 N 帧 → FFmpeg 编码为无声 MP4

    Args:
        anim_func: 绘图函数 (out_path, progress=..., **kw) → None
        anim_kwargs: dict 传给绘图函数的 kwargs（不含 progress）
        output_path: 输出 MP4 路径
        w_even, h_even: 输出分辨率（偶数）
        dur: 动画时长（秒）
        crf: 视频质量
        fps: 帧率
    """
    import imageio_ffmpeg, subprocess, tempfile
    from pathlib import Path
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    n_frames = max(2, int(dur * fps))
    frames_dir = Path(tempfile.mkdtemp(prefix="anim_"))

    for i in range(n_frames):
        t = i / n_frames
        frame_path = frames_dir / f"frame_{i:04d}.png"
        try:
            anim_func(frame_path, progress=t, **(anim_kwargs or {}))
        except Exception as e:
            print(f"  [WARN] 动画帧 {i} 渲染失败: {e}")
            return False  # fallback handled in caller

    rulfile = frames_dir / "rulfile.txt"
    with open(rulfile, 'w') as f:
        for i in range(n_frames):
            f.write(f"{frames_dir / f'frame_{i:04d}.png'}\n")

    cmd = [
        str(ffmpeg_exe), "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(rulfile),
        "-vf", f"scale={w_even}:{h_even}:force_original_aspect_ratio=decrease,pad={w_even}:{h_even}:(ow-iw)/2:(oh-ih)/2,fps={fps}",
        "-c:v", "libx264", "-preset", "fast", "-crf", str(crf),
        "-tune", "stillimage", "-pix_fmt", "yuv420p", "-an",
        str(output_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    import shutil as _shutil
    _shutil.rmtree(frames_dir, ignore_errors=True)
    if r.returncode != 0:
        print(f"  [WARN] 动画编码失败，fallback to 静态: {r.stderr[-100:]}")
        return False
    return True


def _encode_scene_ken_burns(img_path, output_path, w_even, h_even, dur, crf, zoom_in=True):
    """Ken Burns 效果编码单场景（无声）
    zoom_in=True: 从1.0x放大到1.15x（细节→全景）
    zoom_in=False: 从1.15x缩小到1.0x（全景→细节）
    """
    import imageio_ffmpeg, subprocess
    from pathlib import Path
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    scale_pad = (f"scale={w_even}:{h_even}:"
                 f"force_original_aspect_ratio=decrease,"
                 f"pad={w_even}:{h_even}:(ow-iw)/2:(oh-ih)/2")

    if zoom_in:
        z_expr = "min(zoom+0.0007,1.15)"
    else:
        z_expr = "max(zoom-0.0007,1.0)"
    x_expr = "(iw-iw/zoom)/2"
    y_expr = "(ih-ih/zoom)/2"
    zoompan = (f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':"
               f"d=1:s={w_even}x{h_even}:fps=25")

    n_frames = max(1, int(dur * 25))
    cmd = [
        str(ffmpeg_exe), "-y",
        "-loop", "1", "-i", str(img_path),
        "-vf", f"{scale_pad},{zoompan}",
        "-t", str(dur),
        "-frames:v", str(n_frames),
        "-c:v", "libx264", "-preset", "fast", "-crf", str(crf),
        "-tune", "stillimage", "-pix_fmt", "yuv420p", "-an",
        str(output_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if r.returncode != 0:
        # Fallback: 静态图
        cmd2 = [
            str(ffmpeg_exe), "-y",
            "-loop", "1", "-framerate", "1", "-i", str(img_path),
            "-vf", scale_pad, "-t", str(dur),
            "-c:v", "libx264", "-preset", "fast", "-crf", str(crf),
            "-tune", "stillimage", "-pix_fmt", "yuv420p", "-an",
            str(output_path),
        ]
        r2 = subprocess.run(cmd2, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        return r2.returncode == 0
    return True


def make_video_multi(img_paths, audio_path, output_path, bitrate=None, scene_key='default',
                    use_transitions=True, transition_dur=0.75):
    """多图片按时序切换 + 音频 → 视频（Ken Burns + Cross-dissolve 过渡）

    升级版特性：
    - Ken Burns 效果：每张静态图缓慢缩放（zoom-in/zoom-out 交替）
    - Cross-dissolve 过渡（xfade）：场景之间淡入淡出
    - transition_dur: 过渡时长秒（默认 0.75s，每场景最多用22%）

    img_paths: [(img_path, start_second), ...]
    """
    import imageio_ffmpeg, subprocess, shutil
    from pathlib import Path

    duration = get_duration(audio_path)
    if duration is None:
        print(f"  [ERROR] 无法读取音频时长: {audio_path}")
        return False

    n = len(img_paths)
    if n == 0:
        print(f"  [ERROR] 无场景图片")
        return False

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

    with tempfile.TemporaryDirectory() as _tmpdir:
        tmpdir = Path(_tmpdir)

        # ── 1. 编码每个场景（动画/Ken Burns） ──────────────────────────
        seg_files = []
        for i, (img_path, _start_t) in enumerate(img_paths):
            seg_path = tmpdir / f"seg_{i:02d}.mp4"
            seg_files.append(seg_path)
            # 从路径推断 scene_key（兼容 "NN-scene-XX.png" 命名）
            scene_key_for_anim = _infer_scene_key_from_path(img_path)
            anim_entry = _ANIMATION_SCENES.get(scene_key_for_anim)

            if anim_entry is not None:
                # 动画场景：生成帧序列
                anim_func, extra_args = anim_entry
                desc, key_from_meta = _read_scene_meta(img_path)
                anim_key = key_from_meta or scene_key_for_anim
                print(f"  [ANIM] 场景{i}: {anim_key} ({seg_duration:.1f}s, 12fps)")
                ok = _encode_scene_animation(
                    anim_func,
                    {'desc': desc},  # kwargs passed to draw func
                    seg_path, w_even, h_even, seg_duration, crf, fps=12
                )
                if not ok:
                    print(f"  [WARN] 动画场景{i} 失败，fallback to Ken Burns")
            else:
                # Ken Burns 静态图
                pass

            # Ken Burns 兜底（动画失败或非动画场景）
            if not seg_path.exists() or seg_path.stat().st_size < 1000:
                zoom_in = (i % 2 == 0)
                ok = _encode_scene_ken_burns(
                    img_path, seg_path, w_even, h_even, seg_duration, crf, zoom_in=zoom_in
                )
                if not ok:
                    print(f"  [ERROR] Ken Burns 场景{i} 编码失败")
                    return False

        # ── 2. Cross-dissolve 过渡（xfade） ───────────────────────────
        if use_transitions and n > 1:
            trans = min(transition_dur, seg_duration * 0.22)
            # 每段实际输出时长（去掉过渡重叠部分）
            seg_out = seg_duration - trans          # 末段去掉开头 trans
            mid_out = seg_duration - 2 * trans      # 中间段去掉首尾各 trans

            # 逐个 xfade
            cur = seg_files[0]
            # 首段：截掉末尾 trans
            out = tmpdir / "fade_00.mp4"
            r = subprocess.run([
                str(ffmpeg_exe), "-y", "-i", str(cur),
                "-t", str(seg_out), "-c:v", "copy", str(out),
            ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if r.returncode != 0:
                shutil.copy(str(cur), str(out))

            for i in range(1, n):
                nxt = seg_files[i]
                out = tmpdir / f"fade_{i:02d}.mp4"
                offset = seg_out + (i - 1) * mid_out - trans

                r = subprocess.run([
                    str(ffmpeg_exe), "-y",
                    "-i", str(cur), "-i", str(nxt),
                    "-filter_complex",
                    f"[0:v][1:v]xfade=transition=crossfade:"
                    f"duration={trans:.2f}:offset={offset:.2f}[v]",
                    "-map", "[v]",
                    "-c:v", "libx264", "-crf", str(crf), "-preset", "fast",
                    "-pix_fmt", "yuv420p",
                    str(out),
                ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
                if r.returncode != 0:
                    # Fallback: 简单 concat
                    clist = tmpdir / "fc.txt"
                    with open(clist, 'w', encoding='utf-8') as f:
                        f.write(f"file '{cur}'\n")
                        f.write(f"file '{nxt}'\n")
                    r2 = subprocess.run([
                        str(ffmpeg_exe), "-y", "-f", "concat", "-safe", "0",
                        "-i", str(clist), "-c:v", "libx264",
                        "-crf", str(crf), "-preset", "fast", "-an", str(out),
                    ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
                    if r2.returncode != 0:
                        print(f"  [ERROR] fallback concat failed: {r2.stderr[-100:]}")
                        return False
                cur = out
            final_video = cur
        else:
            # 无过渡：简单 concat
            clist = tmpdir / "concat.txt"
            with open(clist, 'w', encoding='utf-8') as f:
                for seg in seg_files:
                    f.write(f"file '{seg}'\n")
            final_video = tmpdir / "concat_video.mp4"
            r = subprocess.run([
                str(ffmpeg_exe), "-y", "-f", "concat", "-safe", "0",
                "-i", str(clist),
                "-c:v", "libx264", "-crf", str(crf), "-preset", "fast", "-an",
                str(final_video),
            ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if r.returncode != 0:
                print(f"  [ERROR] concat failed:\n{r.stderr[-200:]}")
                return False

        # ── 3. 音频标准化 ───────────────────────────────────────────────
        video_dur = get_duration(str(final_video)) or duration
        audio_final = tmpdir / "audio_final.aac"
        r_audio = subprocess.run([
            str(ffmpeg_exe), "-y", "-i", str(audio_path),
            "-af", "loudnorm=I=-16:LRA=11:tp=-1.5",
            "-t", str(video_dur),
            "-c:a", "aac", "-b:a", "192k",
            str(audio_final),
        ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if r_audio.returncode != 0:
            print(f"  [ERROR] audio failed: {r_audio.stderr[-150:]}")
            return False

        # ── 4. 混流 ──────────────────────────────────────────────────────
        r_mux = subprocess.run([
            str(ffmpeg_exe), "-y",
            "-i", str(final_video), "-i", str(audio_final),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", str(output_path),
        ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if r_mux.returncode != 0:
            print(f"  [ERROR] mux failed:\n{r_mux.stderr[-200:]}")
            return False

    size_bytes = output_path.stat().st_size
    trans_str = f"+xfade({trans:.1f}s)" if (use_transitions and n > 1) else ""
    print(f"  [OK] {output_path.name} ({size_bytes:,} bytes, {n} scenes x {seg_duration:.1f}s, KBxfade{trans_str}, CRF={crf})")
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
    if 'cover' in name or len(list(mp3_path.parent.glob("*-scene-*.png"))) <= 1:
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
