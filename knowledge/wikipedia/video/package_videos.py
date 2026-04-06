"""
视频打包：扫描 articles/ 下所有含 MP4 的目录，批量打包到子文件夹
用法：
  python package_videos.py --all             # 打包所有分类（ai/ + 其他）下所有视频
  python package_videos.py                   # 只打包 ai/ 下视频
  python package_videos.py --dry-run --all   # 预览所有分类
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

def find_all_video_dirs(scan_all_categories=False):
    """扫描含 *论文解读.mp4 或 *论文解读-en.mp4 的目录
    scan_all_categories=True 时扫描 articles/ 下所有子目录，否则只扫描 articles/ai/*/
    """
    dirs = []
    if scan_all_categories:
        search_root = ARTICLES_DIR
    else:
        search_root = ARTICLES_DIR / "ai"
    if not search_root.is_dir():
        return dirs
    for slug_dir in search_root.iterdir():
        if not slug_dir.is_dir():
            continue
        has_zh = any(p for p in slug_dir.glob("*论文解读.mp4") if "-en" not in p.stem)
        has_en = any(slug_dir.glob("*论文解读-en.mp4"))
        if not has_zh and not has_en:
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
    """打包中文版和英文版视频到 dist/ 和 dist-en/"""
    zh_mp4s = [p for p in article_dir.glob("*论文解读.mp4") if "-en" not in p.stem]
    en_mp4s = list(article_dir.glob("*论文解读-en.mp4"))

    if not zh_mp4s and not en_mp4s:
        return "SKIP", "无论文解读.mp4 且无论文解读-en.mp4"

    statuses = []

    # 中文版 → dist/
    if zh_mp4s:
        zh_mp4 = zh_mp4s[0]
        dst = article_dir / "dist"
        if not dry_run:
            dst.mkdir(exist_ok=True)
        dst_mp4 = dst / zh_mp4.name
        if not dry_run:
            shutil.copy2(zh_mp4, dst_mp4)
        statuses.append(f"  {zh_mp4.name} → dist/")

        intro = find_intro_md(article_dir)
        if intro:
            dst_intro = dst / "标题简介.md"
            if not dry_run:
                shutil.copy2(intro, dst_intro)
            statuses.append(f"  {intro.name} → dist/")
        else:
            statuses.append("  [WARN] 无标题简介.md")
    else:
        statuses.append("  [SKIP] 无中文版")

    # 英文版 → dist-en/
    if en_mp4s:
        en_mp4 = en_mp4s[0]
        dst_en = article_dir / "dist-en"
        if not dry_run:
            dst_en.mkdir(exist_ok=True)
        dst_en_mp4 = dst_en / en_mp4.name
        if not dry_run:
            shutil.copy2(en_mp4, dst_en_mp4)
        statuses.append(f"  {en_mp4.name} → dist-en/")
        en_intro = article_dir / "Title-Introduction.md"
        if en_intro.exists():
            dst_en_intro = dst_en / "Title-Introduction.md"
            if not dry_run:
                shutil.copy2(en_intro, dst_en_intro)
            statuses.append(f"  Title-Introduction.md → dist-en/")
        else:
            statuses.append("  [WARN] 无 Title-Introduction.md")
    else:
        statuses.append("  [SKIP] 无英文版")

    return statuses

def main():
    parser = argparse.ArgumentParser(description="视频打包工具")
    parser.add_argument("path", nargs="?", help="文章相对路径（如 ai/outofdomain-stress-test），不指定则打包所有")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不写入文件")
    parser.add_argument("--all", action="store_true", help="扫描 articles/ 下所有分类（不只是 ai/）")
    args = parser.parse_args()

    if args.path:
        article_dir = get_article_dir(args.path)
        if not article_dir.exists():
            print(f"[ERROR] 目录不存在: {article_dir}")
            exit(1)
        dirs = [article_dir]
    else:
        dirs = find_all_video_dirs(scan_all_categories=args.all)

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
        results = package_video(article_dir, dry_run=args.dry_run)
        for r in results:
            print(r)
        if results and "SKIP" in results[0]:
            skipped += 1
        else:
            success += 1

    print(f"\n完成：{success} 成功，{skipped} 跳过")

if __name__ == "__main__":
    main()
