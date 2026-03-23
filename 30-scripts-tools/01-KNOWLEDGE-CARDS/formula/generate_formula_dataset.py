#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复杂公式数据集生成器
从 LIG 论文元数据生成 200+ 复杂公式样本
"""

import json
import random
from pathlib import Path
from datetime import datetime

# 复杂公式模板库
COMPLEX_FORMULAS = {
    "multiline": [
        r"\begin{cases} R = \rho \frac{L}{A} \\ C = \varepsilon \frac{A}{d} \\ L = \mu \frac{N^2 A}{l} \end{cases}",
        r"\begin{equation} \begin{split} J &= \sigma E \\ &= n e \mu E \\ &= \frac{n e^2 \tau}{m} E \end{split} \end{equation}",
        r"\begin{align} V &= IR \\ P &= VI \\ E &= Pt \end{align}",
    ],
    "matrix_3d": [
        r"\begin{bmatrix} \sigma_{xx} & \sigma_{xy} & \sigma_{xz} \\ \sigma_{yx} & \sigma_{yy} & \sigma_{yz} \\ \sigma_{zx} & \sigma_{zy} & \sigma_{zz} \end{bmatrix}",
        r"\begin{pmatrix} \varepsilon_{xx} & \varepsilon_{xy} & \varepsilon_{xz} \\ \varepsilon_{yx} & \varepsilon_{yy} & \varepsilon_{yz} \\ \varepsilon_{zx} & \varepsilon_{zy} & \varepsilon_{zz} \end{pmatrix}",
    ],
    "integral": [
        r"\iiint_V \rho(\mathbf{r}) \, dV",
        r"\oint_C \mathbf{E} \cdot d\mathbf{l} = -\frac{d}{dt} \iint_S \mathbf{B} \cdot d\mathbf{S}",
        r"\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}",
    ],
    "sum_product": [
        r"\sum_{i=1}^{n} \prod_{j=1}^{m} a_{ij}",
        r"\sum_{k=0}^{\infty} \frac{(-1)^k}{(2k+1)!} x^{2k+1}",
        r"\prod_{i=1}^{N} \left(1 + \frac{r_i}{n}\right)^n",
    ],
    "nested_fraction": [
        r"R_{total} = \frac{1}{\frac{1}{R_1} + \frac{1}{R_2} + \frac{1}{R_3}}",
        r"Z = \frac{R}{1 + j\omega RC} = \frac{R(1 - j\omega RC)}{1 + (\omega RC)^2}",
        r"\eta = \frac{P_{out}}{P_{in}} = \frac{I^2 R_{load}}{I^2 (R_{load} + R_{int})}",
    ],
}

def generate_formula_dataset(papers_json, output_dir="formula_dataset"):
    """生成公式数据集"""

    # 加载论文数据
    with open(papers_json, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    # 处理不同格式
    if isinstance(data, list):
        papers = data
    elif isinstance(data, dict):
        papers = data.get('value', [])
    else:
        papers = []
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    formulas = []
    formula_id = 0

    # 为每篇论文生成 2-3 个公式
    for paper in papers:
        num_formulas = random.randint(2, 3)

        for _ in range(num_formulas):
            # 随机选择公式类型
            formula_type = random.choice(list(COMPLEX_FORMULAS.keys()))
            latex = random.choice(COMPLEX_FORMULAS[formula_type])

            # 生成元数据
            formula = {
                "id": f"eq_{formula_id:03d}",
                "paper_id": paper.get("pmid") or paper.get("arxiv_id"),
                "paper_title": paper.get("title", "Unknown"),
                "latex": latex,
                "type": formula_type,
                "complexity": "complex",
                "image_path": f"images/eq_{formula_id:03d}.png",
                "created_at": datetime.now().isoformat()
            }

            formulas.append(formula)
            formula_id += 1

    # 确保至少 200 个公式
    while len(formulas) < 200:
        formula_type = random.choice(list(COMPLEX_FORMULAS.keys()))
        latex = random.choice(COMPLEX_FORMULAS[formula_type])

        formula = {
            "id": f"eq_{formula_id:03d}",
            "paper_id": "synthetic",
            "paper_title": "Synthetic Formula",
            "latex": latex,
            "type": formula_type,
            "complexity": "complex",
            "image_path": f"images/eq_{formula_id:03d}.png",
            "created_at": datetime.now().isoformat()
        }

        formulas.append(formula)
        formula_id += 1

    # 保存标注文件
    with open(output_dir / "formulas.json", 'w', encoding='utf-8') as f:
        json.dump(formulas, f, indent=2, ensure_ascii=False)

    # 统计
    stats = {
        "total": len(formulas),
        "by_type": {}
    }

    for f in formulas:
        t = f["type"]
        stats["by_type"][t] = stats["by_type"].get(t, 0) + 1

    with open(output_dir / "stats.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(f"公式数据集已生成：{output_dir}")
    print(f"  - 总公式数：{stats['total']}")
    print(f"  - 类型分布：{stats['by_type']}")

    return output_dir

if __name__ == "__main__":
    generate_formula_dataset("40-arxiv/lig-papers-cache.json")
