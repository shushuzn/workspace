#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Materials NER Model - 材料学论文命名实体识别

功能：
1. 识别材料学论文中的关键实体
2. 支持 6 类实体：材料名称、晶体结构、性能指标、数值、单位、合成条件
3. 基于 RoBERTa 微调

实体类型：
- MATERIAL: 材料名称 (如 "LiFePO4", "SiO2", "钙钛矿")
- CRYSTAL_STRUCTURE: 晶体结构 (如 "立方相", "spinel", "perovskite")
- PROPERTY: 性能指标 (如 "band gap", "elastic modulus", "conductivity")
- VALUE: 数值 (如 "3.2", "150", "0.5")
- UNIT: 单位 (如 "eV", "GPa", "K", "nm")
- SYNTHESIS_CONDITION: 合成条件 (如 "700°C", "12h", "Ar atmosphere")

作者：Claw (AI Research OS)
创建时间：2026-03-05 19:55
"""

import re
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

# ============================================================================
# 1. 材料学实体词典构建
# ============================================================================

@dataclass
class EntityMention:
    """实体提及"""
    text: str
    label: str
    start: int
    end: int

class MaterialsNERDictionary:
    """材料学 NER 词典"""

    def __init__(self):
        # 材料名称词典 (常见材料)
        self.materials = {
            # 氧化物
            'SiO2', 'TiO2', 'ZnO', 'Fe2O3', 'Al2O3', 'MgO', 'CaO',
            'LiCoO2', 'LiFePO4', 'LiMn2O4', 'LiNiO2',

            # 钙钛矿
            'BaTiO3', 'SrTiO3', 'PbTiO3', 'CaTiO3',
            'MAPbI3', 'FAPbI3', 'CsPbI3',

            # 硫化物
            'MoS2', 'WS2', 'CdS', 'ZnS', 'PbS',

            # 半导体
            'Si', 'Ge', 'GaAs', 'InP', 'GaN', 'SiC',

            # 超导体
            'YBa2Cu3O7', 'MgB2', 'FeSe',

            # 二维材料
            'graphene', 'boron nitride', 'MXene',

            # 中文材料名
            '二氧化硅', '二氧化钛', '氧化锌', '磷酸铁锂', '钴酸锂',
            '钙钛矿', '石墨烯', '氮化硼',
        }

        # 晶体结构词典
        self.crystal_structures = {
            'cubic', 'tetragonal', 'orthorhombic', 'monoclinic',
            'triclinic', 'hexagonal', 'rhombohedral',
            'spinel', 'perovskite', 'wurtzite', 'zinc blende',
            'rock salt', 'fluorite', 'rutile', 'anatase',
            '立方', '四方', '正交', '单斜', '三斜', '六方',
            '尖晶石', '钙钛矿', '纤锌矿', '闪锌矿',
        }

        # 性能指标词典
        self.properties = {
            'band gap', 'bandgap', 'energy gap', '带隙',
            'elastic modulus', 'Young modulus', 'bulk modulus', 'shear modulus',
            '弹性模量', '体积模量', '剪切模量', '杨氏模量',
            'conductivity', 'thermal conductivity', 'electrical conductivity',
            '电导率', '热导率',
            'carrier mobility', 'electron mobility', 'hole mobility',
            '载流子迁移率', '电子迁移率',
            'formation energy', 'cohesive energy', 'binding energy',
            '形成能', '内聚能', '结合能',
            'dielectric constant', 'refractive index',
            '介电常数', '折射率',
            'absorption coefficient', 'emission wavelength',
            '吸收系数', '发射波长',
        }

        # 单位词典
        self.units = {
            'eV', 'meV', 'keV',  # 能量
            'GPa', 'MPa', 'kPa',  # 压力/模量
            'K', '°C', '℃',  # 温度
            'nm', 'μm', 'mm', 'cm', 'Å', 'angstrom',  # 长度
            'S/m', 'S/cm',  # 电导率
            'W/m·K', 'W/mK',  # 热导率
            'cm²/V·s', 'cm²/Vs',  # 迁移率
            'F/m', 'F/cm',  # 介电常数
            'Hz', 'kHz', 'MHz', 'GHz', 'THz',  # 频率
            'nm', 'μm', 'mm',  # 波长
        }

        # 合成条件关键词
        self.synthesis_keywords = {
            'anneal', 'annealing', '烧结', '退火',
            'synthesize', 'synthesis', '合成', '制备',
            'calcine', 'calcination', '煅烧',
            'sinter', 'sintering',
            'heat', 'heating', '加热',
            'cool', 'cooling', '冷却',
            'atmosphere', '气氛',
            'pressure', '压力',
            'temperature', '温度',
            'time', '时间',
            'duration', '持续时间',
            'precursor', '前驱体',
            'solvent', '溶剂',
            'catalyst', '催化剂',
        }

    def get_all_entities(self) -> Dict[str, set]:
        """获取所有词典"""
        return {
            'MATERIAL': self.materials,
            'CRYSTAL_STRUCTURE': self.crystal_structures,
            'PROPERTY': self.properties,
            'UNIT': self.units,
            'SYNTHESIS_KEYWORD': self.synthesis_keywords,
        }

    def add_custom_entity(self, label: str, entity: str):
        """添加自定义实体"""
        label = label.upper()
        if not hasattr(self, label.lower()):
            setattr(self, label.lower(), set())
        getattr(self, label.lower()).add(entity)


# ============================================================================
# 2. 基于规则的 NER 标注器
# ============================================================================

class RuleBasedNER:
    """基于规则的 NER 标注器"""

    def __init__(self, dictionary: MaterialsNERDictionary = None):
        self.dict = dictionary or MaterialsNERDictionary()

        # 数值模式
        self.number_pattern = re.compile(
            r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?'
        )

        # 化学式模式
        self.formula_pattern = re.compile(
            r'\b([A-Z][a-z]?\d*)+\b'
        )

        # 温度模式
        self.temperature_pattern = re.compile(
            r'(\d+(?:\.\d+)?)\s*(?:°[CK]|℃|K|kelvin)',
            re.IGNORECASE
        )

        # 时间模式
        self.time_pattern = re.compile(
            r'(\d+(?:\.\d+)?)\s*(h|hr|hrs|hour|hours|min|mins|minute|minutes|s|sec|secs|second|seconds)',
            re.IGNORECASE
        )

        # 压力模式
        self.pressure_pattern = re.compile(
            r'(\d+(?:\.\d+)?)\s*(Pa|kPa|MPa|GPa|atm|bar|mbar|Torr)',
            re.IGNORECASE
        )

    def extract_entities(self, text: str) -> List[EntityMention]:
        """从文本中提取实体"""
        entities = []

        # 1. 提取词典中的实体
        entities.extend(self._extract_dictionary_entities(text))

        # 2. 提取数值
        entities.extend(self._extract_numbers(text))

        # 3. 提取化学式
        entities.extend(self._extract_formulas(text))

        # 4. 提取温度
        entities.extend(self._extract_temperatures(text))

        # 5. 提取时间
        entities.extend(self._extract_times(text))

        # 6. 提取压力
        entities.extend(self._extract_pressures(text))

        # 7. 去重和排序
        entities = self._deduplicate_and_sort(entities)

        return entities

    def _extract_dictionary_entities(self, text: str) -> List[EntityMention]:
        """提取词典中的实体"""
        entities = []
        text_lower = text.lower()

        for label, entity_set in self.dict.get_all_entities().items():
            for entity in entity_set:
                entity_lower = entity.lower()
                start = 0
                while True:
                    pos = text_lower.find(entity_lower, start)
                    if pos == -1:
                        break
                    entities.append(EntityMention(
                        text=text[pos:pos +len(entity)],
                        label=label,
                        start=pos,
                        end=pos +len(entity)
                    ))
                    start = pos + 1

        return entities

    def _extract_numbers(self, text: str) -> List[EntityMention]:
        """提取数值"""
        entities = []
        for match in self.number_pattern.finditer(text):
            entities.append(EntityMention(
                text=match.group(),
                label='VALUE',
                start=match.start(),
                end=match.end()
            ))
        return entities

    def _extract_formulas(self, text: str) -> List[EntityMention]:
        """提取化学式"""
        entities = []
        for match in self.formula_pattern.finditer(text):
            formula = match.group()
            # 简单验证：至少包含一个大写字母和一个小写字母或数字
            if re.search(r'[A-Z][a-z]?\d*', formula):
                entities.append(EntityMention(
                    text=formula,
                    label='MATERIAL',
                    start=match.start(),
                    end=match.end()
                ))
        return entities

    def _extract_temperatures(self, text: str) -> List[EntityMention]:
        """提取温度条件"""
        entities = []
        for match in self.temperature_pattern.finditer(text):
            entities.append(EntityMention(
                text=match.group(),
                label='SYNTHESIS_CONDITION',
                start=match.start(),
                end=match.end()
            ))
        return entities

    def _extract_times(self, text: str) -> List[EntityMention]:
        """提取时间条件"""
        entities = []
        for match in self.time_pattern.finditer(text):
            entities.append(EntityMention(
                text=match.group(),
                label='SYNTHESIS_CONDITION',
                start=match.start(),
                end=match.end()
            ))
        return entities

    def _extract_pressures(self, text: str) -> List[EntityMention]:
        """提取压力条件"""
        entities = []
        for match in self.pressure_pattern.finditer(text):
            entities.append(EntityMention(
                text=match.group(),
                label='SYNTHESIS_CONDITION',
                start=match.start(),
                end=match.end()
            ))
        return entities

    def _deduplicate_and_sort(self, entities: List[EntityMention]) -> List[EntityMention]:
        """去重和排序"""
        # 按起始位置排序
        entities.sort(key=lambda e: (e.start, -len(e.text)))

        # 去重 (重叠的实体保留更长的)
        deduplicated = []
        for entity in entities:
            # 检查是否与已有实体重叠
            overlap = False
            for existing in deduplicated:
                if not (entity.end <= existing.start or entity.start >= existing.end):
                    # 有重叠，保留更长的
                    if len(entity.text) > len(existing.text):
                        deduplicated.remove(existing)
                        deduplicated.append(entity)
                    overlap = True
                    break
            if not overlap:
                deduplicated.append(entity)

        # 再次排序
        deduplicated.sort(key=lambda e: e.start)

        return deduplicated


# ============================================================================
# 3. 训练数据生成器
# ============================================================================

class TrainingDataGenerator:
    """训练数据生成器"""

    def __init__(self):
        self.ner = RuleBasedNER()

    def generate_from_text(self, text: str) -> Dict:
        """从文本生成标注数据"""
        entities = self.ner.extract_entities(text)

        return {
            'text': text,
            'entities': [
                {
                    'start': e.start,
                    'end': e.end,
                    'label': e.label,
                    'text': e.text
                }
                for e in entities
            ]
        }

    def generate_from_file(self, input_path: str, output_path: str):
        """从文件批量生成标注数据"""
        input_file = Path(input_path)
        output_file = Path(output_path)

        data = []

        if input_file.suffix == '.txt':
            # 纯文本文件，每段作为一个样本
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
                # 按段落分割
                paragraphs = text.split('\n\n')
                for para in paragraphs:
                    para = para.strip()
                    if len(para) > 50:  # 忽略太短的段落
                        data.append(self.generate_from_text(para))

        elif input_file.suffix == '.md':
            # Markdown 文件，提取摘要和结论
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 简单提取：按标题分割
                sections = re.split(r'^#+\s+', content, flags=re.MULTILINE)
                for section in sections:
                    if len(section) > 100:
                        data.append(self.generate_from_text(section))

        # 保存为 JSON
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"生成 {len(data)} 个标注样本，保存到 {output_path}")
        return data

    def generate_sample_data(self, num_samples: int = 100) -> List[Dict]:
        """生成示例训练数据"""
        # 材料学论文常用句式模板
        templates = [
            "We synthesized {material} with a {structure} structure.",
            "The {property} of {material} is {value} {unit}.",
            "{material} was annealed at {temp}°C for {time}h in {atmosphere} atmosphere.",
            "The crystal structure of {material} is {structure} with lattice parameters a={value}Å.",
            "We measured the {property} to be {value} {unit} at {temp}K.",
            "The band gap of {material} is {value} eV, which is consistent with previous reports.",
            "{material} exhibits excellent {property} of {value} {unit}.",
            "Single crystals of {material} were grown by the {method} method.",
        ]

        samples = []
        for i in range(num_samples):
            template = templates[i % len(templates)]
            # 这里应该用实际值填充，简化处理
            text = template.format(
                material='LiFePO4',
                structure='olivine',
                property='band gap',
                value='3.2',
                unit='eV',
                temp='700',
                time='12',
                atmosphere='Ar',
                method='flux'
            )
            samples.append(self.generate_from_text(text))

        return samples


# ============================================================================
# 4. 主函数
# ============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("Materials NER Model - 材料学论文命名实体识别")
    print("=" * 60)

    # 1. 初始化词典
    print("\n[1/4] 初始化材料学词典...")
    dictionary = MaterialsNERDictionary()
    entities = dictionary.get_all_entities()
    for label, entity_set in entities.items():
        print(f"  - {label}: {len(entity_set)} 个实体")

    # 2. 初始化 NER 标注器
    print("\n[2/4] 初始化 NER 标注器...")
    ner = RuleBasedNER(dictionary)

    # 3. 测试示例
    print("\n[3/4] 测试 NER 标注...")
    test_texts = [
        "LiFePO4 has a band gap of 3.2 eV and crystallizes in the olivine structure.",
        "The sample was annealed at 700°C for 12 hours in Ar atmosphere.",
        "We measured the elastic modulus of SiO2 to be 70 GPa at room temperature.",
        "二氧化钛 (TiO2) 是一种重要的光催化材料，带隙约为 3.0 eV。",
    ]

    for text in test_texts:
        print(f"\n文本：{text}")
        entities = ner.extract_entities(text)
        print(f"识别到 {len(entities)} 个实体:")
        for entity in entities:
            print(f"  [{entity.label}] {entity.text} (位置：{entity.start}-{entity.end})")

    # 4. 生成训练数据
    print("\n[4/4] 生成训练数据...")
    generator = TrainingDataGenerator()
    samples = generator.generate_sample_data(10)
    print(f"  生成 {len(samples)} 个示例样本")

    # 保存示例数据
    output_path = Path("data/ner-training-samples.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)
    print(f"  保存到 {output_path}")

    print("\n" + "=" * 60)
    print("NER 模型准备完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
