#!/usr/bin/env python3
"""
投稿文件打包脚本

将所有投稿文件收集到单一目录，便于上传 Carbon 投稿系统。
"""

import shutil
from pathlib import Path

def create_submission_package(output_dir='submission_package'):
    """创建投稿文件包"""

    # 创建输出目录
    out_path = Path(output_dir)
    if out_path.exists():
        shutil.rmtree(out_path)
    out_path.mkdir(parents=True)

    print("=" * 50)
    print("Creating Submission Package")
    print("=" * 50)

    # 复制论文文件
    paper_files = [
        '../paper/00_abstract.md',
        '../paper/01_introduction.md',
        '../paper/02_related_work.md',
        '../paper/03_methods.md',
        '../paper/04_results.md',
        '../paper/05_conclusion.md',
        '../paper/references_formatted.bib',
        '../paper/cover_letter.md',
        '../paper/highlights.md',
    ]

    print("\n📄 Copying paper files...")
    for file in paper_files:
        src = Path(file)
        if src.exists():
            shutil.copy(src, out_path / src.name)
            print(f"  [OK] {src.name}")
        else:
            print(f"  [WARN] Not found: {src}")

    # 复制图表
    print("\n📊 Copying figures...")
    figures_dir = out_path / 'figures'
    figures_dir.mkdir()

    figure_files = [
        '../figures/GP_200samples_prediction.png',
        '../figures/GP_200samples_residuals.png',
        '../figures/GP_200samples_uncertainty.png',
        '../figures/GP_performance_comparison.png',
    ]

    for file in figure_files:
        src = Path(file)
        if src.exists():
            shutil.copy(src, figures_dir / src.name)
            print(f"  [OK] {src.name}")
        else:
            print(f"  [WARN] Not found: {src}")

    # 复制补充材料
    print("\n📦 Copying supplementary materials...")
    supp_dir = out_path / 'supplementary'
    supp_dir.mkdir()

    supp_files = [
        '../data/lig_dataset_200.csv',
        '../data/README.md',
        '../models/model_card.md',
        '../scripts/predict.py',
        '../scripts/requirements.txt',
        '../scripts/LICENSE',
    ]

    for file in supp_files:
        src = Path(file)
        if src.exists():
            shutil.copy(src, supp_dir / src.name)
            print(f"  [OK] {src.name}")
        else:
            print(f"  [WARN] Not found: {src}")

    # 创建 README
    print("\n📝 Creating package README...")
    readme_content = """# Carbon Submission Package

**Paper:** Machine Learning-Assisted Prediction of Electrical Conductivity in Laser-Induced Graphene Using Gaussian Process Regression

**First Author:** Claw (AI Agent Researcher)

**Submission Date:** 2026-03-15

---

## Files Included

- `00_abstract.md` - Abstract (Chinese + English)
- `01_introduction.md` - Introduction
- `02_related_work.md` - Related Work
- `03_methods.md` - Methods
- `04_results.md` - Results and Discussion
- `05_conclusion.md` - Conclusion
- `references_formatted.bib` - References (BibTeX)
- `cover_letter.md` - Cover Letter
- `highlights.md` - Highlights (5 items)

## Figures

- `figures/GP_200samples_prediction.png`
- `figures/GP_200samples_residuals.png`
- `figures/GP_200samples_uncertainty.png`
- `figures/GP_performance_comparison.png`

## Supplementary Materials

- `supplementary/lig_dataset_200.csv` - Dataset (200 samples)
- `supplementary/predict.py` - Prediction script
- `supplementary/model_card.md` - Model documentation
- `supplementary/requirements.txt` - Python dependencies
- `supplementary/LICENSE` - MIT License

---

**Contact:** [待填写]
"""

    (out_path / 'README.md').write_text(readme_content)
    print("  [OK] README.md")

    print("\n" + "=" * 50)
    print(f"Package created: {out_path.absolute()}")
    print("=" * 50)

    return out_path

if __name__ == '__main__':
    create_submission_package()
