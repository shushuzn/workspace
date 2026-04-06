"""
视频打包：扫描 articles/ 下所有含 MP4 的目录，批量打包到子文件夹
用法：
  python package_videos.py                    # 打包所有视频
  python package_videos.py --dry-run          # 预览（不写入）
  python package_videos.py ai/outofdomain-stress-test  # 打包指定目录
"""
import shutil
import argparse
from pathlib import Path

WIKI_ROOT = Path(__file__).parent.parent
ARTICLES_DIR = WIKI_ROOT / "articles"

def get_article_dir(relative_path):
    """将 ai/outofdomain-stress-test 转为绝对路径"""
    return ARTICLES_DIR / relative_path

def find_all_video_dirs():
    """扫描 articles/ 下所有含 .mp4 的子目录，保留路径最深的"""
    all_dirs = []
    for mp4 in ARTICLES_DIR.rglob("*.mp4"):
        if "scene" in mp4.stem:
            continue
        # Skip packaging outputs: original mp4s are at relative depth ≤3 under articles/
        rel_parts = mp4.relative_to(ARTICLES_DIR).parts
        if len(rel_parts) > 3:
            continue
        all_dirs.append(mp4.parent)
    # Sort by depth (deepest first), then dedupe preferring longer paths
    all_dirs.sort(key=lambda p: -len(p.parts))
    seen = set()
    result = []
    for d in all_dirs:
        if d not in seen:
            result.append(d)
            for parent in d.parents:
                seen.add(parent)
    return result

def find_intro_md(article_dir):
    """在文章目录下找标题简介.md 或类似文件"""
    candidates = [
        article_dir / "标题简介.md",
        article_dir / "简介.md",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None

def package_video(article_dir, dry_run=False):
    """打包单个视频到子文件夹"""
    # 找视频文件
    mp4_files = [p for p in article_dir.glob("*论文解读.mp4")]
    if not mp4_files:
        return "SKIP", "无论文解读.mp4"
    mp4 = mp4_files[0]

    # 子文件夹名 = 目录名（如 05-Out-of-Domain-Stress-Test）
    folder_name = article_dir.name
    dst = article_dir / folder_name

    if not dry_run:
        dst.mkdir(exist_ok=True)

    # 复制视频
    dst_mp4 = dst / mp4.name
    if not dry_run:
        shutil.copy2(mp4, dst_mp4)
    mp4_status = f"  {mp4.name} → {dst_mp4.relative_to(article_dir)}"

    # 找标题简介
    intro = find_intro_md(article_dir)
    if intro:
        dst_intro = dst / "标题简介.md"
        if not dry_run:
            shutil.copy2(intro, dst_intro)
        intro_status = f"  {intro.name} → {dst_intro.relative_to(article_dir)}"
    else:
        intro_status = "  [WARN] 无标题简介.md，跳过"

    return mp4_status, intro_status

def main():
    parser = argparse.ArgumentParser(description="视频打包工具")
    parser.add_argument("path", nargs="?", help="文章相对路径（如 ai/outofdomain-stress-test），不指定则打包所有")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不写入文件")
    args = parser.parse_args()

    if args.path:
        article_dir = get_article_dir(args.path)
        if not article_dir.exists():
            print(f"[ERROR] 目录不存在: {article_dir}")
            exit(1)
        dirs = [article_dir]
    else:
        dirs = find_all_video_dirs()

    if not dirs:
        print("未找到任何论文解读.mp4 文件")
        exit(0)

    print(f"\n{'[DRY-RUN] 预览' if args.dry_run else '打包'} {len(dirs)} 个视频\n")
    success, skipped = 0, 0
    for article_dir in dirs:
        rel = article_dir.relative_to(ARTICLES_DIR)
        print(f"处理: {rel}")
        mp4_status, intro_status = package_video(article_dir, dry_run=args.dry_run)
        print(f"  {mp4_status}")
        print(f"  {intro_status}")
        if "SKIP" in mp4_status:
            skipped += 1
        else:
            success += 1

    print(f"\n完成：{success} 成功，{skipped} 跳过")

if __name__ == "__main__":
    main()
