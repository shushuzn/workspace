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
    """扫描 articles/ai/*/ 下含 *论文解读.mp4 的目录，排除 dist/"""
    dirs = []
    ai_dir = ARTICLES_DIR / "ai"
    if not ai_dir.is_dir():
        return dirs
    for slug_dir in ai_dir.iterdir():
        if not slug_dir.is_dir():
            continue
        candidates = list(slug_dir.glob("*论文解读.mp4"))
        if not candidates:
            continue
        mp4 = candidates[0]
        if mp4.parent.name == "dist":
            continue
        dirs.append(slug_dir)
    return dirs

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

def cleanup_nested_dirs(article_dir, dry_run=False):
    """清理历史遗留的嵌套打包目录（如 ai/slug/slug/）"""
    slug = article_dir.name
    nested = article_dir / slug
    if nested.is_dir():
        if not dry_run:
            shutil.rmtree(nested)
        return True
    return False

def package_video(article_dir, dry_run=False):
    """打包单个视频到子文件夹"""
    # 找视频文件
    mp4_files = [p for p in article_dir.glob("*论文解读.mp4")]
    if not mp4_files:
        return "SKIP", "无论文解读.mp4"
    mp4 = mp4_files[0]

    # 固定输出目录 dist/，永远不随 run 次数嵌套
    dst = article_dir / "dist"
    if not dry_run:
        dst.mkdir(exist_ok=True)

    # 复制视频
    dst_mp4 = dst / mp4.name
    if not dry_run:
        shutil.copy2(mp4, dst_mp4)
    mp4_status = f"  {mp4.name} → dist/{dst_mp4.name}"

    # 找标题简介
    intro = find_intro_md(article_dir)
    if intro:
        dst_intro = dst / "标题简介.md"
        if not dry_run:
            shutil.copy2(intro, dst_intro)
        intro_status = f"  {intro.name} → dist/{dst_intro.name}"
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
        # 先清理历史嵌套目录
        if cleanup_nested_dirs(article_dir, dry_run=args.dry_run):
            print(f"  [清理] 历史嵌套目录已删除: {article_dir.name}/{article_dir.name}/")
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
