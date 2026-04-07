"""
自动化视频脚本处理：提取纯文本 + 符号替换 + 多语言版本生成
对应原手动步骤：2. 去掉 frontmatter/画面标注 → 3. 替换数学符号 → 4. 生成英文版
"""
import argparse
import re
from pathlib import Path

# 数学符号替换表（与 generate_speech.py 同步）
MATH_REPLACEMENTS = [
    (r'σ', 'sigma '), (r'λ', 'lambda '), (r'ω', 'omega '), (r'ε', 'epsilon '),
    (r'∂', 'delta '), (r'∫', 'integral '), (r'∑', 'sum '),
    (r'≤', ' less than or equal '), (r'≥', ' greater than or equal '),
    (r'≠', ' not equal '), (r'∞', ' infinity '), (r'→', ' to '), (r'↔', ' and '),
    (r'∈', ' belongs to '), (r'∉', ' does not belong to '), (r'⊂', ' subset of '),
    (r'∪', ' union '), (r'∩', ' intersection '), (r'√', ' square root of '),
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
    # 其他
    (r'ℤ', 'integers '), (r'ℝ', 'reals '), (r'ℕ', 'naturals '), (r'ℂ', 'complex '),
    (r'ẋ', 'x dot '), (r'ẍ', 'x double dot '), (r'ŷ', 'y hat '),
    (r'·', '.'), (r'×', ' times '), (r'÷', ' divided by '),
    (r'ℏ', 'h bar '),
    (r'⊕', ' direct sum '), (r'⊗', ' tensor product '),
]

def replace_math(text: str) -> str:
    for pattern, repl in MATH_REPLACEMENTS:
        text = re.sub(pattern, repl, text)
    return text

def extract_clean_text(md_path: Path) -> str:
    """从视频脚本提取纯阅读文本（去 frontmatter + 去 [画面：...] 行）"""
    content = md_path.read_text(encoding='utf-8')

    # 去掉 YAML frontmatter
    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

    # 去掉所有 [画面：...] 行
    lines = content.split('\n')
    clean_lines = [l for l in lines if not l.strip().startswith('[画面：')]

    # 去掉 markdown 标题标记（# 开头的行）
    text_lines = [l for l in clean_lines if not l.strip().startswith('#')]

    return '\n'.join(text_lines).strip()

def generate_speech_file(article_dir: Path, stem: str, force: bool = False) -> Path | None:
    """生成中文阅读文案（去 frontmatter + 去画面标注 + 换行合并）"""
    # 实际脚本文件名格式：NN-标题.md（带序号前缀）
    # 扫描目录下第一个 .md 文件
    md_candidates = list(article_dir.glob("*.md"))
    if not md_candidates:
        print(f"  [WARN] 未找到脚本文件: {article_dir}")
        return None
    md_path = md_candidates[0]  # 取第一个 md 文件

    speech_path = article_dir / f"{stem}-阅读文案.txt"
    if speech_path.exists() and not force:
        return speech_path

    text = extract_clean_text(md_path)
    speech_path.write_text(text, encoding='utf-8')
    print(f"  [OK] 生成阅读文案: {speech_path.name} ({len(text)} 字)")
    return speech_path

def generate_speech_en(article_dir: Path, stem: str, force: bool = False) -> Path | None:
    """生成英文阅读文案（符号替换）"""
    md_candidates = list(article_dir.glob("*.md"))
    if not md_candidates:
        return None
    md_path = md_candidates[0]

    speech_en_path = article_dir / f"{stem}-阅读文案-speech-en.txt"
    if speech_en_path.exists() and not force:
        return speech_en_path

    text = extract_clean_text(md_path)
    # 数学符号替换
    text = replace_math(text)
    speech_en_path.write_text(text, encoding='utf-8')
    print(f"  [OK] 生成英文文案: {speech_en_path.name}")
    return speech_en_path

def generate_speech_zh_processed(article_dir: Path, stem: str, force: bool = False) -> Path | None:
    """生成中文 speech.txt（用于 TTS，合并换行）"""
    speech_path = article_dir / f"{stem}-阅读文案.txt"
    if not speech_path.exists():
        return None

    speech_tts_path = article_dir / f"{stem}-speech.txt"
    if speech_tts_path.exists() and not force:
        return speech_tts_path

    text = speech_path.read_text(encoding='utf-8')
    # edge-tts 需单行，用逗号分隔
    text_one_line = text.replace('\n', '，')
    speech_tts_path.write_text(text_one_line, encoding='utf-8')
    print(f"  [OK] 生成 TTS 文案: {speech_tts_path.name}")
    return speech_tts_path

def process_article(article_dir: Path, force: bool = False):
    """单篇文章的完整脚本处理（3个输出文件）"""
    stem = article_dir.name
    print(f"\n处理: {article_dir.relative_to(Path(__file__).parent.parent / 'articles')}")

    # 1. 中文阅读文案
    _ = generate_speech_file(article_dir, stem, force)

    # 2. 英文阅读文案
    _ = generate_speech_en(article_dir, stem, force)

    # 3. 中文 TTS 文案
    _ = generate_speech_zh_processed(article_dir, stem, force)

def main():
    parser = argparse.ArgumentParser(description="自动化视频脚本处理（去 frontmatter/画面标注 + 符号替换 + 多语言）")
    parser.add_argument("article", nargs="?", help="文章目录相对路径（如 ai/outofdomain-stress-test）")
    parser.add_argument("--dir", default=None, help="articles 目录")
    parser.add_argument("--force", action="store_true", help="强制重新生成")
    args = parser.parse_args()

    base_dir = Path(args.dir) if args.dir else Path(__file__).parent.parent / "articles"

    if args.article:
        article_dir = base_dir / args.article
        if not article_dir.exists():
            print(f"[ERROR] 目录不存在: {article_dir}")
            exit(1)
        process_article(article_dir, force=args.force)
    else:
        # 批量处理所有含脚本的文章（扫描 articles/ 下所有子目录，找 .md 文件）
        article_dirs = []
        for d in base_dir.rglob("*"):
            if d.is_dir() and any(d.glob("*.md")):
                article_dirs.append(d)
        print(f"发现 {len(article_dirs)} 篇文章，开始自动化处理...\n")
        for article_dir in article_dirs:
            process_article(article_dir, force=args.force)

if __name__ == "__main__":
    main()
