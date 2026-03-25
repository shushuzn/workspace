#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
"""
Crystal Structure Extractor - 晶体结构提取器

功能：
1. 从论文/文本中提取晶体结构信息
2. 解析 CIF 格式数据
3. 提取晶格参数、原子位置、空间群
4. 结构化输出

作者：Claw (AI Research OS)
创建时间：2026-03-05 20:05
"""

import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


# ============================================================================
# 1. 数据结构定义
# ============================================================================

@dataclass
class LatticeParameters:
    """晶格参数"""
    a: float  # Å
    b: float  # Å
    c: float  # Å
    alpha: float  # degrees
    beta: float  # degrees
    gamma: float  # degrees

    @property
    def crystal_system(self) -> str:
        """判断晶系"""
        # 简化判断逻辑
        if abs(self.a - self.b) < 0.01 and abs(self.b - self.c) < 0.01:
            if abs(self.alpha - 90) < 0.1 and abs(self.beta - 90) < 0.1 and abs(self.gamma - 90) < 0.1:
                return 'cubic'
            elif abs(self.alpha - 90) < 0.1 and abs(self.beta - 90) < 0.1 and abs(self.gamma - 120) < 0.1:
                return 'hexagonal'
        return 'unknown'


@dataclass
class AtomPosition:
    """原子位置"""
    element: str
    x: float
    y: float
    z: float
    occupancy: float = 1.0
    u_iso: float = 0.0


@dataclass
class CrystalStructure:
    """晶体结构"""
    material_name: str
    formula: str
    space_group_number: Optional[int] = None
    space_group_symbol: Optional[str] = None
    lattice: Optional[LatticeParameters] = None
    atoms: List[AtomPosition] = None
    volume: Optional[float] = None  # Å³
    density: Optional[float] = None  # g/cm³

    def __post_init__(self):
        if self.atoms is None:
            self.atoms = []

    def to_dict(self) -> Dict:
        """转换为字典"""
        result = {
            'material_name': self.material_name,
            'formula': self.formula,
            'space_group_number': self.space_group_number,
            'space_group_symbol': self.space_group_symbol,
            'volume': self.volume,
            'density': self.density,
        }

        if self.lattice:
            result['lattice'] = asdict(self.lattice)
            result['crystal_system'] = self.lattice.crystal_system

        if self.atoms:
            result['atoms'] = [asdict(a) for a in self.atoms]

        return result


# ============================================================================
# 2. CIF 解析器
# ============================================================================

class CIFParser:
    """CIF 文件解析器"""

    def __init__(self):
        # CIF 标签模式
        self.tag_pattern = re.compile(r'_([a-zA-Z_][a-zA-Z0-9_]*)\s+(.+?)(?=\n_|$)', re.DOTALL)

        # 数值模式
        self.number_pattern = re.compile(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?')

    def parse(self, cif_content: str) -> CrystalStructure:
        """解析 CIF 内容"""
        # 提取所有标签
        tags = {}
        for match in self.tag_pattern.finditer(cif_content):
            tag_name = match.group(1)
            tag_value = match.group(2).strip().strip('"\'')
            tags[tag_name] = tag_value

        # 提取材料信息
        material_name = tags.get('entry_id', 'Unknown')
        formula = tags.get('chemical_formula_sum', 'Unknown')

        # 提取空间群
        space_group_number = self._parse_int(tags.get('space_group_IT_number'))
        space_group_symbol = tags.get('space_group_name_H-M_alt', '')

        # 提取晶格参数
        lattice = self._extract_lattice(tags)

        # 提取原子位置
        atoms = self._extract_atoms(tags, cif_content)

        # 计算体积和密度
        volume = self._calculate_volume(lattice) if lattice else None
        density = self._calculate_density(formula, volume) if volume else None

        return CrystalStructure(
            material_name=material_name,
            formula=formula,
            space_group_number=space_group_number,
            space_group_symbol=space_group_symbol,
            lattice=lattice,
            atoms=atoms,
            volume=volume,
            density=density
        )

    def _parse_int(self, value: str) -> Optional[int]:
        """解析整数"""
        if not value:
            return None
        try:
            return int(float(value))
        except Exception:
            return None

    def _parse_float(self, value: str) -> Optional[float]:
        """解析浮点数"""
        if not value:
            return None
        try:
            return float(value)
        except Exception:
            return None

    def _extract_lattice(self, tags: Dict) -> Optional[LatticeParameters]:
        """提取晶格参数"""
        try:
            a = self._parse_float(tags.get('cell_length_a'))
            b = self._parse_float(tags.get('cell_length_b'))
            c = self._parse_float(tags.get('cell_length_c'))
            alpha = self._parse_float(tags.get('cell_angle_alpha'))
            beta = self._parse_float(tags.get('cell_angle_beta'))
            gamma = self._parse_float(tags.get('cell_angle_gamma'))

            if all([a, b, c, alpha, beta, gamma]):
                return LatticeParameters(a=a, b=b, c=c, alpha=alpha, beta=beta, gamma=gamma)
        except Exception:
            pass

        return None

    def _extract_atoms(self, tags: Dict, cif_content: str) -> List[AtomPosition]:
        """提取原子位置"""
        atoms = []

        # 查找 atom_site 循环
        loop_match = re.search(r'loop_\s+(_atom_site_[^\n]+(?:\n_atom_site_[^\n]+)*)', cif_content)
        if not loop_match:
            return atoms

        loop_content = loop_match.group(1)

        # 解析列名
        columns = re.findall(r'_atom_site_(\w+)', loop_content)
        if not columns:
            return atoms

        # 解析数据行
        lines = loop_content.split('\n')[1:]  # 跳过列名
        for line in lines:
            values = line.split()
            if len(values) < len(columns):
                continue

            row = dict(zip(columns, values))

            try:
                element = row.get('label', row.get('type_symbol', ''))
                # 清理元素符号 (移除数字)
                element = re.sub(r'\d+', '', element)

                x = float(row.get('fract_x', 0))
                y = float(row.get('fract_y', 0))
                z = float(row.get('fract_z', 0))
                occupancy = float(row.get('occupancy', 1.0))
                u_iso = float(row.get('U_iso_or_equiv', row.get('B_iso_or_equiv', 0.0)))

                atoms.append(AtomPosition(
                    element=element,
                    x=x,
                    y=y,
                    z=z,
                    occupancy=occupancy,
                    u_iso=u_iso
                ))
            except Exception:
                continue

        return atoms

    def _calculate_volume(self, lattice: LatticeParameters) -> float:
        """计算晶胞体积"""
        import math

        a, b, c = lattice.a, lattice.b, lattice.c
        alpha = math.radians(lattice.alpha)
        beta = math.radians(lattice.beta)
        gamma = math.radians(lattice.gamma)

        volume = a * b * c * math.sqrt(
            1 - math.cos(alpha)**2 - math.cos(beta)**2 - math.cos(gamma)**2 +
            2 * math.cos(alpha) * math.cos(beta) * math.cos(gamma)
        )

        return volume

    def _calculate_density(self, formula: str, volume: float) -> Optional[float]:
        """计算密度 (简化版)"""
        # 原子量 (简化字典)
        atomic_weights = {
            'H': 1.008, 'He': 4.003,
            'Li': 6.941, 'Be': 9.012, 'B': 10.81, 'C': 12.01, 'N': 14.01, 'O': 16.00,
            'Na': 22.99, 'Mg': 24.31, 'Al': 26.98, 'Si': 28.09, 'P': 30.97, 'S': 32.07,
            'K': 39.10, 'Ca': 40.08, 'Ti': 47.87, 'Fe': 55.85, 'Co': 58.93, 'Ni': 58.69,
            'Cu': 63.55, 'Zn': 65.38, 'Ga': 69.72, 'Ge': 72.64, 'As': 74.92, 'Se': 78.96,
            'Rb': 85.47, 'Sr': 87.62, 'Zr': 91.22, 'Nb': 92.91, 'Mo': 95.96, 'Ag': 107.87,
            'Cd': 112.41, 'In': 114.82, 'Sn': 118.71, 'Sb': 121.76, 'I': 126.90,
            'Cs': 132.91, 'Ba': 137.33, 'La': 138.91, 'W': 183.84, 'Pt': 195.08,
            'Au': 196.97, 'Pb': 207.2, 'Bi': 208.98,
        }

        # 解析化学式 (简化)
        total_weight = 0.0
        matches = re.findall(r'([A-Z][a-z]?)(\d*)', formula)
        for element, count in matches:
            if element in atomic_weights:
                count = int(count) if count else 1
                total_weight += atomic_weights[element] * count

        if total_weight > 0 and volume > 0:
            # 密度 = (分子量 / 阿伏伽德罗常数) / 体积 * 10^24 (转换为 g/cm³)
            density = (total_weight / volume) * 0.6022
            return round(density, 2)

        return None

    def parse_file(self, cif_path: str) -> CrystalStructure:
        """从文件解析 CIF"""
        with open(cif_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return self.parse(content)


# ============================================================================
# 3. 从文本提取晶体结构
# ============================================================================

class TextStructureExtractor:
    """从文本中提取晶体结构信息"""

    def __init__(self):
        # 晶系关键词
        self.crystal_systems = {
            'cubic': ['cubic', 'isometric', '立方'],
            'tetragonal': ['tetragonal', '四方'],
            'orthorhombic': ['orthorhombic', '正交'],
            'monoclinic': ['monoclinic', '单斜'],
            'triclinic': ['triclinic', '三斜'],
            'hexagonal': ['hexagonal', '六方'],
            'rhombohedral': ['rhombohedral', 'trigonal', '三方', '菱形'],
        }

        # 常见结构类型
        self.structure_types = [
            'perovskite', 'spinel', 'wurtzite', 'zinc blende', 'rock salt',
            'fluorite', 'rutile', 'anatase', 'brookite',
            '钙钛矿', '尖晶石', '纤锌矿', '闪锌矿', '岩盐', '萤石', '金红石',
        ]

        # 晶格参数模式
        self.lattice_pattern = re.compile(
            r'(?:a\s*=\s*|lattice\s+parameter\s+a\s*[:=]\s*)(\d+(?:\.\d+)?)\s*(?:Å|angstrom|A)',
            re.IGNORECASE
        )

    def extract(self, text: str) -> Optional[CrystalStructure]:
        """从文本中提取晶体结构"""
        # 1. 识别晶系
        crystal_system = self._find_crystal_system(text)

        # 2. 识别结构类型
        structure_type = self._find_structure_type(text)

        # 3. 提取晶格参数
        lattice_params = self._extract_lattice_from_text(text)

        # 4. 提取空间群
        space_group = self._extract_space_group(text)

        # 5. 提取材料名称
        material = self._extract_material_name(text)

        if not any([crystal_system, structure_type, lattice_params, space_group]):
            return None

        return CrystalStructure(
            material_name=material or 'Unknown',
            formula=material or 'Unknown',
            space_group_symbol=space_group,
            lattice=LatticeParameters(**lattice_params) if lattice_params else None
        )

    def _find_crystal_system(self, text: str) -> Optional[str]:
        """查找晶系"""
        text_lower = text.lower()
        for system, keywords in self.crystal_systems.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return system
        return None

    def _find_structure_type(self, text: str) -> Optional[str]:
        """查找结构类型"""
        text_lower = text.lower()
        for structure in self.structure_types:
            if structure.lower() in text_lower:
                return structure
        return None

    def _extract_lattice_from_text(self, text: str) -> Optional[Dict]:
        """从文本提取晶格参数"""
        params = {}

        # 提取 a, b, c
        for param in ['a', 'b', 'c']:
            pattern = re.compile(rf'{param}\s*=\s*(\d+(?:\.\d+)?)\s*(?:Å|angstrom|A)', re.IGNORECASE)
            match = pattern.search(text)
            if match:
                params[param] = float(match.group(1))

        # 提取角度
        for param, default in [('alpha', 90), ('beta', 90), ('gamma', 90)]:
            pattern = re.compile(rf'{param}\s*=\s*(\d+(?:\.\d+)?)\s*°', re.IGNORECASE)
            match = pattern.search(text)
            params[param] = float(match.group(1)) if match else default

        if len(params) >= 3:  # 至少需要 a, b, c
            return params
        return None

    def _extract_space_group(self, text: str) -> Optional[str]:
        """提取空间群"""
        # 空间群符号模式
        patterns = [
            r'space\s+group\s*[:=]\s*([A-Z][a-z]?\s*\d+[a-z]?)',
            r'space\s+group\s*[:=]\s*(\d+)',
            r'([A-Z][a-z]?\s*\d+[a-z]?)\s+structure',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_material_name(self, text: str) -> Optional[str]:
        """提取材料名称"""
        # 化学式模式
        formula_pattern = re.compile(r'\b([A-Z][a-z]?\d*)+\b')
        match = formula_pattern.search(text)
        if match:
            return match.group(0)

        # 材料名称模式
        material_pattern = re.compile(r'(?:material|compound|sample)\s*[:=]?\s*([A-Za-z0-9\s\-]+?)(?:,|\.|$)')
        match = material_pattern.search(text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None


# ============================================================================
# 4. 主函数
# ============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("Crystal Structure Extractor - 晶体结构提取器")
    print("=" * 60)

    # 1. 测试 CIF 解析
    print("\n[1/3] 测试 CIF 解析...")

    # 示例 CIF 内容 (SiO2)
    cif_example = """
data_SiO2
_entry_id 'SiO2'
_chemical_formula_sum 'SiO2'
_space_group_IT_number 183
_space_group_name_H-M_alt 'P6_3/mmc'

_cell_length_a 4.91
_cell_length_b 4.91
_cell_length_c 5.41
_cell_angle_alpha 90
_cell_angle_beta 90
_cell_angle_gamma 120

loop_
_atom_site_label
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
Si Si 0.333 0.667 0.000
O O 0.333 0.667 0.305
"""

    cif_parser = CIFParser()
    structure = cif_parser.parse(cif_example)

    print(f"材料：{structure.material_name}")
    print(f"化学式：{structure.formula}")
    print(f"空间群：{structure.space_group_number} ({structure.space_group_symbol})")
    print(f"晶系：{structure.lattice.crystal_system if structure.lattice else 'Unknown'}")
    if structure.lattice:
        print(f"晶格参数：a={structure.lattice.a}Å, b={structure.lattice.b}Å, c={structure.lattice.c}Å")
    else:
        print("晶格参数：未提取到")
    print(f"体积：{structure.volume:.2f} Å³" if structure.volume else "体积：未计算")
    print(f"密度：{structure.density:.2f} g/cm³" if structure.density else "密度：未计算")
    print(f"原子数：{len(structure.atoms)}")

    # 2. 测试文本提取
    print("\n[2/3] 测试文本提取...")

    text_examples = [
        "LiFePO4 crystallizes in the orthorhombic system with space group Pnma. "
        "The lattice parameters are a = 10.33 Å, b = 6.01 Å, and c = 4.69 Å.",

        "The cubic perovskite structure of BaTiO3 has a lattice parameter a = 4.00 Å "
        "and space group Pm-3m.",

        "二氧化钛 (TiO2) 采用金红石结构，四方晶系，a = 4.59 Å, c = 2.96 Å。",
    ]

    text_extractor = TextStructureExtractor()

    for text in text_examples:
        print(f"\n文本：{text[:80]}...")
        structure = text_extractor.extract(text)
        if structure:
            print(f"  晶系：{structure.lattice.crystal_system if structure.lattice else 'Unknown'}")
            print(f"  结构类型：{text_extractor._find_structure_type(text)}")
            if structure.lattice:
                print(f"  晶格参数：a={structure.lattice.a}Å")

    # 3. 保存为 JSON
    print("\n[3/3] 保存结构化数据...")

    output_data = structure.to_dict()
    output_path = Path("data/crystal-structure-example.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"保存到 {output_path}")

    print("\n" + "=" * 60)
    print("晶体结构提取器准备完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
