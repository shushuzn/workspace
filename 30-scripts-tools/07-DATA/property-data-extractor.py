#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Property Data Extractor - 性能数据提取器

功能：
1. 从论文/文本中提取材料性能数据
2. 支持多种性能类型 (带隙、弹性模量、电导率等)
3. 数值归一化和单位转换
4. 结构化输出

作者：Claw (AI Research OS)
创建时间：2026-03-05 20:15
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
class PropertyData:
    """性能数据"""
    material: str
    property_name: str  # 性能名称 (英文)
    property_name_cn: str  # 性能名称 (中文)
    value: float
    unit: str
    unit_standardized: str  # 标准单位
    method: Optional[str] = None  # 测量/计算方法
    temperature: Optional[float] = None  # 温度 (K)
    reference: Optional[str] = None  # 来源

    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# 2. 单位转换
# ============================================================================

class UnitConverter:
    """单位转换器"""

    # 能量单位转换 (到 eV)
    ENERGY_TO_EV = {
        'eV': 1.0,
        'meV': 0.001,
        'keV': 1000.0,
        'J': 6.242e18,
        'kJ/mol': 0.010364,
        'kcal/mol': 0.04336,
        'Ry': 13.606,
        'Hartree': 27.211,
    }

    # 压力/模量单位转换 (到 GPa)
    PRESSURE_TO_GPA = {
        'GPa': 1.0,
        'MPa': 0.001,
        'kPa': 0.000001,
        'Pa': 1e-9,
        'atm': 0.000101325,
        'bar': 0.0001,
        'psi': 6.895e-6,
    }

    # 长度单位转换 (到 Å)
    LENGTH_TO_ANGSTROM = {
        'Å': 1.0,
        'angstrom': 1.0,
        'nm': 10.0,
        'μm': 10000.0,
        'mm': 1e7,
        'cm': 1e8,
        'm': 1e10,
    }

    # 电导率单位转换 (到 S/m)
    CONDUCTIVITY_TO_S_M = {
        'S/m': 1.0,
        'S/cm': 100.0,
        'mS/cm': 0.1,
        'μS/cm': 0.0001,
        'Ω^-1·m^-1': 1.0,
        'Ω^-1·cm^-1': 100.0,
    }

    # 热导率单位转换 (到 W/m·K)
    THERMAL_TO_W_MK = {
        'W/m·K': 1.0,
        'W/mK': 1.0,
        'W/(m·K)': 1.0,
        'mW/cm·K': 10.0,
        'cal/cm·s·K': 418.4,
    }

    # 迁移率单位转换 (到 cm²/V·s)
    MOBILITY_TO_CM2_VS = {
        'cm²/V·s': 1.0,
        'cm²/Vs': 1.0,
        'cm^2/V·s': 1.0,
        'm²/V·s': 10000.0,
    }

    @classmethod
    def convert(cls, value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """转换单位"""
        from_unit = from_unit.strip()
        to_unit = to_unit.strip()

        # 能量转换
        if from_unit in cls.ENERGY_TO_EV and to_unit == 'eV':
            return value * cls.ENERGY_TO_EV[from_unit]

        # 压力转换
        if from_unit in cls.PRESSURE_TO_GPA and to_unit == 'GPa':
            return value * cls.PRESSURE_TO_GPA[from_unit]

        # 长度转换
        if from_unit in cls.LENGTH_TO_ANGSTROM and to_unit == 'Å':
            return value * cls.LENGTH_TO_ANGSTROM[from_unit]

        # 电导率转换
        if from_unit in cls.CONDUCTIVITY_TO_S_M and to_unit == 'S/m':
            return value * cls.CONDUCTIVITY_TO_S_M[from_unit]

        # 热导率转换
        if from_unit in cls.THERMAL_TO_W_MK and to_unit == 'W/m·K':
            return value * cls.THERMAL_TO_W_MK[from_unit]

        # 迁移率转换
        if from_unit in cls.MOBILITY_TO_CM2_VS and to_unit == 'cm²/V·s':
            return value * cls.MOBILITY_TO_CM2_VS[from_unit]

        # 相同单位
        if from_unit.lower() == to_unit.lower():
            return value

        return None


# ============================================================================
# 3. 性能数据提取器
# ============================================================================

class PropertyExtractor:
    """性能数据提取器"""

    def __init__(self):
        # 性能名称映射 (英文 -> 中文)
        self.property_names = {
            'band gap': '带隙',
            'bandgap': '带隙',
            'energy gap': '带隙',
            'elastic modulus': '弹性模量',
            "Young's modulus": '杨氏模量',
            'Young modulus': '杨氏模量',
            'bulk modulus': '体积模量',
            'shear modulus': '剪切模量',
            'thermal conductivity': '热导率',
            'electrical conductivity': '电导率',
            'carrier mobility': '载流子迁移率',
            'electron mobility': '电子迁移率',
            'hole mobility': '空穴迁移率',
            'formation energy': '形成能',
            'cohesive energy': '内聚能',
            'dielectric constant': '介电常数',
            'refractive index': '折射率',
            'absorption coefficient': '吸收系数',
            'emission wavelength': '发射波长',
        }

        # 性能的标准单位
        self.standard_units = {
            'band gap': 'eV',
            'elastic modulus': 'GPa',
            "Young's modulus": 'GPa',
            'bulk modulus': 'GPa',
            'shear modulus': 'GPa',
            'thermal conductivity': 'W/m·K',
            'electrical conductivity': 'S/m',
            'carrier mobility': 'cm²/V·s',
            'formation energy': 'eV',
            'dielectric constant': 'dimensionless',
        }

        # 提取模式
        self.patterns = [
            # "band gap of 3.2 eV"
            r'(?:band\s*gap|bandgap)\s+(?:of|is|:|=)\s*(\d+(?:\.\d+)?)\s*(eV|meV|keV)',

            # "elastic modulus is 70 GPa"
            r'(?:elastic|Young|bulk|shear)\s*modulus\s+(?:is|of|:|=)\s*(\d+(?:\.\d+)?)\s*(GPa|MPa|kPa)',

            # "conductivity of 1000 S/m"
            r'(?:thermal|electrical)?\s*conductivity\s+(?:of|is|:|=)\s*(\d+(?:\.\d+)?)\s*(S/m|S/cm|W/m·K|W/mK)',

            # "mobility of 1500 cm²/V·s"
            r'(?:carrier|electron|hole)\s*mobility\s+(?:of|is|:|=)\s*(\d+(?:\.\d+)?)\s*(cm²/V·s|cm²/Vs|m²/V·s)',

            # "3.2 eV band gap"
            r'(\d+(?:\.\d+)?)\s*(eV|meV|keV)\s+(?:band\s*gap|bandgap)',

            # "70 GPa elastic modulus"
            r'(\d+(?:\.\d+)?)\s*(GPa|MPa)\s+(?:elastic|Young|bulk|shear)\s*modulus',

            # 中文模式："带隙为 3.2 eV"
            r'(?:带隙 | 带隙)\s*(?:为 | 是|:|=)\s*(\d+(?:\.\d+)?)\s*(eV|meV)',

            # 中文模式："弹性模量为 70 GPa"
            r'(?:弹性模量 | 杨氏模量 | 体积模量)\s*(?:为 | 是|:|=)\s*(\d+(?:\.\d+)?)\s*(GPa|MPa)',
        ]

        # 材料名称模式
        self.material_pattern = re.compile(r'\b([A-Z][a-z]?\d*)+\b')

        # 温度模式
        self.temperature_pattern = re.compile(
            r'(?:at|@)\s*(\d+(?:\.\d+)?)\s*(K|°C|℃|room\s*temperature)',
            re.IGNORECASE
        )

        # 方法模式
        self.method_pattern = re.compile(
            r'(?:measured\s*(?:by|using)|calculated\s*(?:by|using)|via)\s+([A-Za-z\s,]+?)(?:\.|,|$)',
            re.IGNORECASE
        )

    def extract(self, text: str) -> List[PropertyData]:
        """从文本中提取性能数据"""
        properties = []

        # 1. 使用正则模式提取
        properties.extend(self._extract_by_patterns(text))

        # 2. 提取材料名称
        for prop in properties:
            if prop.material == 'Unknown':
                prop.material = self._extract_material(text)

        # 3. 提取温度
        for prop in properties:
            prop.temperature = self._extract_temperature(text)

        # 4. 提取方法
        for prop in properties:
            prop.method = self._extract_method(text)

        # 5. 单位标准化
        for prop in properties:
            prop.unit_standardized = self._standardize_unit(prop.property_name, prop.unit)

        return properties

    def _extract_by_patterns(self, text: str) -> List[PropertyData]:
        """使用正则模式提取"""
        properties = []

        for i, pattern in enumerate(self.patterns):
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # 确定性能名称
                prop_name_en, prop_name_cn = self._identify_property(pattern, match, text)

                if prop_name_en:
                    value = float(match.group(1))
                    unit = match.group(2) if len(match.groups()) > 1 else ''

                    properties.append(PropertyData(
                        material='Unknown',
                        property_name=prop_name_en,
                        property_name_cn=prop_name_cn,
                        value=value,
                        unit=unit,
                        unit_standardized=unit
                    ))

        return properties

    def _identify_property(self, pattern: str, match, text: str) -> Tuple[Optional[str], Optional[str]]:
        """识别性能名称"""
        matched_text = match.group(0).lower()

        for en_name, cn_name in self.property_names.items():
            if en_name in matched_text or cn_name in matched_text:
                return en_name, cn_name

        return None, None

    def _extract_material(self, text: str) -> str:
        """提取材料名称"""
        match = self.material_pattern.search(text)
        return match.group(0) if match else 'Unknown'

    def _extract_temperature(self, text: str) -> Optional[float]:
        """提取温度"""
        match = self.temperature_pattern.search(text)
        if match:
            value = float(match.group(1))
            unit = match.group(2).lower()

            if 'room' in unit:
                return 298.15  # 室温
            elif '°c' in unit or '℃' in unit:
                return value + 273.15
            else:
                return value

        return None

    def _extract_method(self, text: str) -> Optional[str]:
        """提取测量/计算方法"""
        match = self.method_pattern.search(text)
        return match.group(1).strip() if match else None

    def _standardize_unit(self, property_name: str, unit: str) -> str:
        """标准化单位"""
        standard = self.standard_units.get(property_name, unit)

        # 尝试转换
        if property_name == 'band gap' and unit in UnitConverter.ENERGY_TO_EV:
            return 'eV'

        return standard


# ============================================================================
# 4. 主函数
# ============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("Property Data Extractor - 性能数据提取器")
    print("=" * 60)

    # 1. 测试提取
    print("\n[1/3] 测试性能数据提取...")

    extractor = PropertyExtractor()

    test_texts = [
        "LiFePO4 has a band gap of 3.2 eV, measured by UV-Vis spectroscopy.",

        "The elastic modulus of SiO2 is 70 GPa at room temperature, calculated using DFT.",

        "We measured the thermal conductivity to be 50 W/m·K at 300K.",

        "The electron mobility of graphene is 15000 cm²/V·s, which is exceptionally high.",

        "二氧化钛的带隙为 3.0 eV，通过光吸收谱测量。",

        "杨氏模量为 110 GPa，室温下测量。",
    ]

    all_properties = []

    for text in test_texts:
        print(f"\n文本：{text[:70]}...")
        properties = extractor.extract(text)

        for prop in properties:
            print(f"  材料：{prop.material}")
            print(f"  性能：{prop.property_name} ({prop.property_name_cn})")
            print(f"  数值：{prop.value} {prop.unit}")
            if prop.temperature:
                print(f"  温度：{prop.temperature} K")
            if prop.method:
                print(f"  方法：{prop.method}")

        all_properties.extend(properties)

    # 2. 单位转换测试
    print("\n[2/3] 测试单位转换...")

    conversions = [
        (1000, 'meV', 'eV'),
        (100, 'GPa', 'GPa'),
        (1000, 'S/cm', 'S/m'),
        (10, 'nm', 'Å'),
    ]

    for value, from_unit, to_unit in conversions:
        converted = UnitConverter.convert(value, from_unit, to_unit)
        print(f"  {value} {from_unit} = {converted} {to_unit}")

    # 3. 保存为 JSON
    print("\n[3/3] 保存结构化数据...")

    output_data = [prop.to_dict() for prop in all_properties]
    output_path = Path("data/property-data-examples.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"保存 {len(output_data)} 条性能数据到 {output_path}")

    print("\n" + "=" * 60)
    print("性能数据提取器准备完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
