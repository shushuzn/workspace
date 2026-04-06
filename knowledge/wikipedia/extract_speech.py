#!/usr/bin/env python3
"""Extract clean speech text from video script markdown for TTS."""
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ARTICLES_DIR = SCRIPT_DIR / 'articles'

REPLACEMENTS = [
    # Unicode math subscripts/superscripts
    ('₀', ' 0'), ('₁', ' 1'), ('₂', ' 2'), ('₃', ' 3'), ('₄', ' 4'),
    ('₅', ' 5'), ('₆', ' 6'), ('₇', ' 7'), ('₈', ' 8'), ('₉', ' 9'),
    ('⁰', ' 0'), ('¹', ' 1'), ('²', ' 2'), ('³', ' 3'), ('⁴', ' 4'),
    ('⁵', ' 5'), ('⁶', ' 6'), ('⁷', ' 7'), ('⁸', ' 8'), ('⁹', ' 9'),
    ('ᵢ', ' i'), ('ⱼ', ' j'), ('ₖ', ' k'), ('ₗ', ' l'),
    ('σ', 'sigma'), ('λ', 'lambda'), ('Σ', 'Sigma'), ('Δ', 'Delta'),
    # Special punctuation/arrows
    ('→', ' → '), ('←', ' ← '), ('↑', ' ↑ '), ('↓', ' ↓ '),
    ('—', ' '), ('–', ' '), ('…', '...'),
    # Greek letters common in physics
    ('α', 'alpha'), ('β', 'beta'), ('γ', 'gamma'), ('δ', 'delta'),
    ('ε', 'epsilon'), ('μ', 'mu'), ('ν', 'nu'), ('π', 'pi'),
    ('ρ', 'rho'), ('τ', 'tau'), ('φ', 'phi'), ('ω', 'omega'),
    ('Γ', 'Gamma'), ('Φ', 'Phi'), ('Ψ', 'Psi'), ('Ω', 'Omega'),
    # TTS awkward
    ('NbSe', 'NbSe'), ('MoS', 'MoS'), ('TMDC', 'TMDC'),
    ('Ising', 'Ising'), ('Andreev', 'Andreev'), ('Burau', 'Burau'),
    ('IAM', 'IAM'), ('IAM', 'IAM'), ('vdW', 'van der Waals'),
]


def clean_content(content: str) -> str:
    """Clean markdown content for TTS."""
    # Remove frontmatter
    content = re.sub(r'^---\n[\s\S]+?\n---\n', '', content)

    # Remove [画面：xxx] scene annotations (and surrounding blank lines)
    content = re.sub(r'\n*\[画面：[^\]]+\]\n*', '\n', content)

    # Remove markdown headings (keep text, drop ##)
    content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)

    # Remove bold/italic markers
    content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
    content = re.sub(r'\*([^*]+)\*', r'\1', content)
    content = re.sub(r'`([^`]+)`', r'\1', content)

    # Apply symbol replacements
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)

    # Collapse multiple blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content.strip()


def process_file(md_path: Path) -> bool:
    """Process a single script file. Returns True if speech was written."""
    content = md_path.read_text(encoding='utf-8')
    cleaned = clean_content(content)

    # Build output paths
    stem = md_path.stem          # 01-Detection-of-spin-valley-polarized-states论文解读
    parent = md_path.parent
    speech_file = parent / f'{stem}-speech.txt'
    tts_file = parent / f'{stem}-speech-tts.txt'

    speech_file.write_text(cleaned, encoding='utf-8')
    tts_file.write_text(cleaned, encoding='utf-8')
    print(f'  [OK] {stem}')
    print(f'       speech: {speech_file.name}  ({len(cleaned)} chars)')
    return True


def main():
    if len(sys.argv) > 1:
        # Process specific file
        path = Path(sys.argv[1])
        if not path.is_absolute():
            path = Path.cwd() / path
        process_file(path)
        return

    # Process all *论文解读.md files under articles/
    md_files = list(ARTICLES_DIR.rglob('*论文解读.md'))
    if not md_files:
        print('[WARN] No *论文解读.md files found')
        return

    print(f'Processing {len(md_files)} script(s)...')
    for f in sorted(md_files):
        try:
            process_file(f)
        except Exception as e:
            print(f'  [ERROR] {f.name}: {e}')


if __name__ == '__main__':
    main()

