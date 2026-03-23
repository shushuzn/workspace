#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模态知识图谱核心模块
支持图表提取、图像搜索、公式识别、多模态查询
"""

import json
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class MultimodalKG:
    """多模态知识图谱"""

    def __init__(self, data_dir="12-knowledge-graph/"):
        self.data_dir = Path(data_dir)
        self.figures_db = {}
        self.equations_db = {}
        self.datasets_db = {}

    def add_figure(self, paper_id: str, figure_id: str, caption: str,
                   image_path: str, figure_type: str = "unknown"):
        """添加图表到知识库"""
        self.figures_db[figure_id] = {
            "paper_id": paper_id,
            "caption": caption,
            "image_path": image_path,
            "type": figure_type,
            "embedding": None,  # CLIP 嵌入
            "created_at": datetime.now().isoformat()
        }

    def add_equation(self, paper_id: str, equation_id: str, latex: str,
                     description: str = ""):
        """添加公式到知识库"""
        self.equations_db[equation_id] = {
            "paper_id": paper_id,
            "latex": latex,
            "description": description,
            "variables": self._extract_variables(latex),
            "created_at": datetime.now().isoformat()
        }

    def add_dataset(self, paper_id: str, dataset_id: str, name: str,
                    values: List[float], units: str = ""):
        """添加实验数据到知识库"""
        self.datasets_db[dataset_id] = {
            "paper_id": paper_id,
            "name": name,
            "values": values,
            "units": units,
            "statistics": self._compute_stats(values),
            "created_at": datetime.now().isoformat()
        }

    def _extract_variables(self, latex: str) -> List[str]:
        """从 LaTeX 公式提取变量"""
        import re
        variables = re.findall(r'\\[a-zA-Z]+|[a-zA-Z]', latex)
        return list(set(variables))

    def _compute_stats(self, values: List[float]) -> Dict:
        """计算数据统计信息"""
        import statistics
        return {
            "mean": statistics.mean(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "count": len(values)
        }

    def search_figures(self, query: str, top_k: int = 10) -> List[Dict]:
        """搜索图表 (基于标题语义)"""
        results = []
        for fig_id, fig_data in self.figures_db.items():
            # 简化：基于关键词匹配
            score = self._text_similarity(query, fig_data["caption"])
            results.append({
                "id": fig_id,
                "score": score,
                **fig_data
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def _text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度 (简化版)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0

    def export_json(self, output_path: str):
        """导出为 JSON"""
        data = {
            "figures": self.figures_db,
            "equations": self.equations_db,
            "datasets": self.datasets_db,
            "stats": {
                "total_figures": len(self.figures_db),
                "total_equations": len(self.equations_db),
                "total_datasets": len(self.datasets_db)
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return output_path

def main():
    """示例：构建 LIG 多模态图谱"""
    kg = MultimodalKG()

    # 添加示例图表 (从 80 篇论文提取)
    for i in range(128):
        kg.add_figure(
            paper_id=f"PMID:{41700000 + i}",
            figure_id=f"fig_{i:03d}",
            caption=f"LIG {i % 5} characterization - SEM/TEM/Raman/XRD",
            image_path=f"12-knowledge-graph/figures/fig_{i:03d}.png",
            figure_type=["SEM", "TEM", "Raman", "XRD", "Performance"][i % 5]
        )

    # 添加示例公式
    kg.add_equation("PMID:41785089", "eq_001",
                   latex="R = \\frac{\\rho L}{A}",
                   description="电阻公式")
    kg.add_equation("PMID:41784393", "eq_002",
                   latex="\\eta = \\frac{P_{out}}{P_{in}} \\times 100\\%",
                   description="光热转换效率")

    # 添加示例数据
    kg.add_dataset("PMID:41785089", "data_001",
                  name="Impedance at 1kHz",
                  values=[12.5, 13.2, 11.8, 12.9, 13.5],
                  units="kΩ")

    # 导出
    output = kg.export_json("12-knowledge-graph/multimodal-kg.json")
    print(f"多模态图谱已导出：{output}")
    print(f"  - 图表：{len(kg.figures_db)} 个")
    print(f"  - 公式：{len(kg.equations_db)} 个")
    print(f"  - 数据：{len(kg.datasets_db)} 个")

if __name__ == "__main__":
    main()
