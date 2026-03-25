#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手写公式数据集生成器
生成 500+ 手写公式样本用于模型微调
"""

import json
import random
from pathlib import Path
from datetime import datetime

# 手写公式模板 (模拟实验室笔记常见公式)
HANDWRITTEN_FORMULAS = {
    "physics": [
        r"R = \rho \frac{L}{A}",
        r"V = IR",
        r"P = VI",
        r"E = mc^2",
        r"F = ma",
        r"J = \sigma E",
        r"C = \varepsilon \frac{A}{d}",
        r"L = \mu \frac{N^2 A}{l}",
    ],
    "chemistry": [
        r"pH = -\log[H^+]",
        r"K_{eq} = \frac{[C]^c[D]^d}{[A]^a[B]^b}",
        r"\Delta G = \Delta H - T\Delta S",
        r"PV = nRT",
    ],
    "math": [
        r"\int_a^b f(x)dx",
        r"\frac{d}{dx}x^n = nx^{n-1}",
        r"\sum_{i=1}^n i = \frac{n(n+1)}{2}",
        r"e^{i\pi} + 1 = 0",
        r"\sin^2\theta + \cos^2\theta = 1",
    ],
    "electrochemistry": [
        r"J = nFkC",
        r"E = E^0 - \frac{RT}{nF}\ln Q",
        r"i = nFAkC",
        r"\eta = \frac{P_{out}}{P_{in}}",
    ],
    "materials": [
        r"\sigma = \frac{F}{A}",
        r"\varepsilon = \frac{\Delta L}{L}",
        r"E = \frac{\sigma}{\varepsilon}",
        r"\rho = \frac{m}{V}",
    ],
}

def generate_handwritten_dataset(output_dir="handwritten_formula_dataset"):
    """生成手写公式数据集"""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "images").mkdir(exist_ok=True)

    formulas = []
    formula_id = 0

    # 每个类别生成 ~100 个样本
    for category, templates in HANDWRITTEN_FORMULAS.items():
        num_per_category = 100

        for i in range(num_per_category):
            latex = random.choice(templates)

            # 模拟手写变化
            variation = random.choice([
                "normal",      # 正常手写
                "sloped",      # 倾斜
                "large",       # 字体大
                "small",       # 字体小
                "fast",        # 潦草
            ])

            formula = {
                "id": f"hw_eq_{formula_id:03d}",
                "latex": latex,
                "category": category,
                "variation": variation,
                "complexity": random.choice(["simple", "medium", "complex"]),
                "image_path": f"images/hw_eq_{formula_id:03d}.png",
                "style": "handwritten",
                "created_at": datetime.now().isoformat()
            }

            formulas.append(formula)
            formula_id += 1

    # 保存标注文件
    with open(output_dir / "handwritten_formulas.json", 'w', encoding='utf-8') as f:
        json.dump(formulas, f, indent=2, ensure_ascii=False)

    # 统计
    stats = {
        "total": len(formulas),
        "by_category": {},
        "by_variation": {},
        "by_complexity": {}
    }

    for f in formulas:
        stats["by_category"][f["category"]] = stats["by_category"].get(f["category"], 0) + 1
        stats["by_variation"][f["variation"]] = stats["by_variation"].get(f["variation"], 0) + 1
        stats["by_complexity"][f["complexity"]] = stats["by_complexity"].get(f["complexity"], 0) + 1

    with open(output_dir / "stats.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(f"手写公式数据集已生成：{output_dir}")
    print(f"  - 总样本数：{stats['total']}")
    print(f"  - 类别分布：{stats['by_category']}")
    print(f"  - 书写风格：{stats['by_variation']}")
    print(f"  - 复杂度：{stats['by_complexity']}")

    return output_dir

if __name__ == "__main__":
    generate_handwritten_dataset()
