#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CIF Parser v1
CIF 文件解析器实现
"""

import re
from typing import Dict, List, Tuple

class CIFParser:
    """CIF 文件解析器"""

    def __init__(self):
        self.data = {}
        self.atoms = []
        self.lattice = {}

    def parse(self, content: str) -> Dict:
        """解析 CIF 文件内容"""
        lines = content.split('\n')
        current_block = None

        for line in lines:
            line = line.strip()

            # 跳过空行和注释
            if not line or line.startswith('#'):
                continue

            # 数据块开始
            if line.startswith('data_'):
                current_block = line[5:]
                self.data[current_block] = {}
                continue

            # 键值对
            if line.startswith('_'):
                parts = line.split(None, 1)
                if len(parts) == 2:
                    key, value = parts
                    if current_block:
                        self.data[current_block][key] = value
                    else:
                        self.data[key] = value

        # 提取晶格参数
        self._extract_lattice()

        # 提取原子位置
        self._extract_atoms()

        return {
            'formula': self.data.get('_chemical_formula_sum', 'Unknown'),
            'space_group': self.data.get('_space_group_name_H-M_alt', 'Unknown'),
            'lattice': self.lattice,
            'atoms': self.atoms
        }

    def _extract_lattice(self):
        """提取晶格参数"""
        self.lattice = {
            'a': float(self.data.get('_cell_length_a', 0)),
            'b': float(self.data.get('_cell_length_b', 0)),
            'c': float(self.data.get('_cell_length_c', 0)),
            'alpha': float(self.data.get('_cell_angle_alpha', 90)),
            'beta': float(self.data.get('_cell_angle_beta', 90)),
            'gamma': float(self.data.get('_cell_angle_gamma', 90)),
        }

    def _extract_atoms(self):
        """提取原子位置"""
        # 查找原子位置循环
        loop_keys = [k for k in self.data.keys() if isinstance(k, str) and 'atom_site' in k.lower()]

        if loop_keys:
            # 简化处理：提取关键信息
            for key, value in self.data.items():
                if '_atom_site_label' in str(key):
                    self.atoms.append({
                        'label': value,
                        'x': 0,
                        'y': 0,
                        'z': 0
                    })

    def parse_file(self, filepath: str) -> Dict:
        """从文件解析 CIF"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.parse(content)

    def to_html(self, material_id: str = "material") -> str:
        """生成 3Dmol.js HTML 可视化"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Crystal Structure - {material_id}</title>
    <script src="https://3dmol.org/build/3Dmol-min.js"></script>
    <style>
        body {{ margin: 0; padding: 0; }}
        #viewer {{ width: 100%; height: 600px; position: relative; }}
    </style>
</head>
<body>
    <div id="viewer"></div>
    <script>
        $(document).ready(function () {{
            let element = $("#viewer");
            let config = {{ backgroundColor: "white" }};
            let viewer = $3Dmol.createViewer(element, config);
            
            // CIF 内容
            let cif = `{self.data}`;
            
            $3Dmol.downloadCIF(cif, viewer, {{
                doAssembly: true,
                doNormalize: true
            }});
            
            viewer.setStyle({{}}, {{stick: {{radius: 0.15}}, sphere: {{scale: 0.3}}}});
            viewer.zoomTo();
            viewer.render();
        }});
    </script>
</body>
</html>
"""
        return html

def demo():
    """演示使用"""
    print("=" * 60)
    print("CIF Parser v1 Demo")
    print("=" * 60)

    # 示例 CIF 内容 (LiCoO2)
    cif_content = """
data_LiCoO2
_chemical_formula_sum 'Li Co O2'
_space_group_name_H-M_alt 'R-3m'
_cell_length_a 2.82
_cell_length_b 2.82
_cell_length_c 14.08
_cell_angle_alpha 90
_cell_angle_beta 90
_cell_angle_gamma 120
"""

    parser = CIFParser()
    result = parser.parse(cif_content)

    print(f"\nFormula: {result['formula']}")
    print(f"Space Group: {result['space_group']}")
    print(f"Lattice Parameters:")
    print(f"  a = {result['lattice']['a']} Å")
    print(f"  b = {result['lattice']['b']} Å")
    print(f"  c = {result['lattice']['c']} Å")

    # 生成 HTML
    html = parser.to_html("LiCoO2")
    print(f"\nHTML visualization generated ({len(html)} bytes)")

    print("-" * 60)
    print("[COMPLETE]")
    print("=" * 60)

if __name__ == "__main__":
    demo()
