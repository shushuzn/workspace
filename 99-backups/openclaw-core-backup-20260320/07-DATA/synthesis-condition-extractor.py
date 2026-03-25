#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Synthesis Condition Extractor - 合成条件提取器

功能：
1. 从论文/文本中提取材料合成条件
2. 识别温度、时间、气氛、压力等参数
3. 提取前驱体和反应路径
4. 结构化输出合成流程

作者：Claw (AI Research OS)
创建时间：2026-03-05 20:35
"""

import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum


# ============================================================================
# 1. 数据结构定义
# ============================================================================

class AtmosphereType(Enum):
    """气氛类型"""
    INERT = "inert"  # 惰性
    OXIDIZING = "oxidizing"  # 氧化
    REDUCING = "reducing"  # 还原
    VACUUM = "vacuum"  # 真空
    AIR = "air"  # 空气
    OTHER = "other"  # 其他


@dataclass
class SynthesisStep:
    """合成步骤"""
    step_number: int
    operation: str  # 操作类型 (mix, heat, cool, grind, etc.)
    temperature: Optional[float] = None  # 温度 (°C)
    time: Optional[float] = None  # 时间 (小时)
    atmosphere: Optional[str] = None  # 气氛
    atmosphere_type: Optional[AtmosphereType] = None
    pressure: Optional[float] = None  # 压力 (atm)
    heating_rate: Optional[float] = None  # 升温速率 (°C/min)
    cooling_method: Optional[str] = None  # 冷却方式
    description: str = ""

    def to_dict(self) -> Dict:
        result = asdict(self)
        if self.atmosphere_type:
            result['atmosphere_type'] = self.atmosphere_type.value
        return result


@dataclass
class Precursor:
    """前驱体"""
    name: str
    formula: Optional[str] = None
    amount: Optional[float] = None
    unit: Optional[str] = None
    molar_ratio: Optional[float] = None
    purity: Optional[str] = None
    supplier: Optional[str] = None


@dataclass
class SynthesisCondition:
    """合成条件"""
    material_name: str
    target_formula: Optional[str] = None
    method: Optional[str] = None  # 合成方法
    precursors: List[Precursor] = field(default_factory=list)
    steps: List[SynthesisStep] = field(default_factory=list)
    total_time: Optional[float] = None  # 总时间 (小时)
    max_temperature: Optional[float] = None  # 最高温度 (°C)
    yield_percent: Optional[float] = None  # 产率
    notes: Optional[str] = None

    def to_dict(self) -> Dict:
        result = {
            'material_name': self.material_name,
            'target_formula': self.target_formula,
            'method': self.method,
            'precursors': [asdict(p) for p in self.precursors],
            'steps': [s.to_dict() for s in self.steps],
            'total_time': self.total_time,
            'max_temperature': self.max_temperature,
            'yield_percent': self.yield_percent,
            'notes': self.notes,
        }
        return result


# ============================================================================
# 2. 合成条件提取器
# ============================================================================

class SynthesisConditionExtractor:
    """合成条件提取器"""

    def __init__(self):
        # 合成方法关键词
        self.synthesis_methods = {
            'solid-state reaction': '固相反应',
            'sol-gel': '溶胶 - 凝胶',
            'hydrothermal': '水热法',
            'solvothermal': '溶剂热法',
            'co-precipitation': '共沉淀',
            'chemical vapor deposition': '化学气相沉积',
            'CVD': '化学气相沉积',
            'pulsed laser deposition': '脉冲激光沉积',
            'PLD': '脉冲激光沉积',
            'sputtering': '溅射',
            'spin coating': '旋涂',
            'electrospinning': '静电纺丝',
            'ball milling': '球磨',
            'flux method': '助熔剂法',
            'ceramic method': '陶瓷法',
        }

        # 操作类型关键词
        self.operation_keywords = {
            'mix': ['mix', 'mixed', 'mixing', 'blend', 'stir', '搅拌', '混合'],
            'heat': ['heat', 'heated', 'heating', 'anneal', 'calcine', 'sinter', '加热', '烧结', '退火', '煅烧'],
            'cool': ['cool', 'cooled', 'cooling', 'quench', '冷却', '淬火'],
            'grind': ['grind', 'ground', 'grinding', 'mill', 'ball mill', '研磨', '球磨'],
            'dry': ['dry', 'dried', 'drying', 'evaporate', '干燥', '蒸发'],
            'wash': ['wash', 'washed', 'washing', 'rinse', '清洗', '洗涤'],
            'filter': ['filter', 'filtered', 'filtration', '过滤'],
            'centrifuge': ['centrifuge', 'centrifuged', 'centrifugation', '离心'],
        }

        # 气氛映射
        self.atmosphere_map = {
            'argon': AtmosphereType.INERT,
            'ar': AtmosphereType.INERT,
            'nitrogen': AtmosphereType.INERT,
            'n2': AtmosphereType.INERT,
            'helium': AtmosphereType.INERT,
            'he': AtmosphereType.INERT,
            'air': AtmosphereType.AIR,
            'oxygen': AtmosphereType.OXIDIZING,
            'o2': AtmosphereType.OXIDIZING,
            'hydrogen': AtmosphereType.REDUCING,
            'h2': AtmosphereType.REDUCING,
            'forming gas': AtmosphereType.REDUCING,
            'vacuum': AtmosphereType.VACUUM,
        }

        # 温度模式
        self.temperature_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:°C|℃|C)\s*(?:for|at|in)?',
            r'(\d+(?:\.\d+)?)\s*(?:K|kelvin)\s*(?:for|at|in)?',
            r'heated\s+to\s+(\d+(?:\.\d+)?)\s*(?:°C|℃|C)?',
            r'annealed\s+at\s+(\d+(?:\.\d+)?)\s*(?:°C|℃|C)?',
            r'calcined\s+at\s+(\d+(?:\.\d+)?)\s*(?:°C|℃|C)?',
            r'sintered\s+at\s+(\d+(?:\.\d+)?)\s*(?:°C|℃|C)?',
            r'温度\s*(?:为 | 升至)\s*(\d+(?:\.\d+)?)\s*(?:°C|℃)?',
        ]

        # 时间模式
        self.time_patterns = [
            r'for\s+(\d+(?:\.\d+)?)\s*(h|hr|hrs|hour|hours)',
            r'for\s+(\d+(?:\.\d+)?)\s*(min|mins|minute|minutes)',
            r'(\d+(?:\.\d+)?)\s*(h|hr|hrs|hour|hours)\s*(?:at|at\s+\d+°C)',
            r'(\d+(?:\.\d+)?)\s*(min|mins|minute|minutes)\s*(?:at|at\s+\d+°C)',
            r'时间\s*(?:为 | 保持)\s*(\d+(?:\.\d+)?)\s*(?:小时|h|分钟|min)',
        ]

        # 气氛模式
        self.atmosphere_patterns = [
            r'in\s+(air|argon|nitrogen|oxygen|hydrogen|vacuum|Ar|N2|O2|H2)\s*(?:atmosphere|flow|gas)?',
            r'under\s+(air|argon|nitrogen|oxygen|hydrogen|vacuum|Ar|N2|O2|H2)\s*(?:atmosphere|flow|gas)?',
            r'(?:空气 | 氩气 | 氮气 | 氧气 | 氢气 | 真空)\s*(?:气氛 | 中)?',
        ]

        # 升温速率模式
        self.heating_rate_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:°C/min|°C/h|K/min|K/h)\s*(?:heating|rate|to)',
            r'heating\s+rate\s+of\s+(\d+(?:\.\d+)?)\s*(?:°C/min|°C/h|K/min|K/h)',
            r'升温速率\s*(?:为)\s*(\d+(?:\.\d+)?)\s*(?:°C/min|°C/h)',
        ]

        # 前驱体模式
        self.precursor_patterns = [
            r'precursor[s]?\s*[:=]?\s*([A-Za-z0-9\s,()]+?)(?:\.|,|was|were)',
            r'starting\s+material[s]?\s*[:=]?\s*([A-Za-z0-9\s,()]+?)(?:\.|,|was)',
            r'using\s+([A-Za-z0-9\s,()]+?)\s+as\s+(?:precursor|starting\s+material)',
        ]

    def extract(self, text: str) -> List[SynthesisCondition]:
        """从文本中提取合成条件"""
        conditions = []

        # 1. 识别合成方法
        method = self._extract_method(text)

        # 2. 提取前驱体
        precursors = self._extract_precursors(text)

        # 3. 提取合成步骤
        steps = self._extract_steps(text)

        # 4. 提取材料名称
        material = self._extract_material(text)

        # 5. 计算总体参数
        total_time = self._calculate_total_time(steps)
        max_temp = self._calculate_max_temperature(steps)

        if steps or method or precursors:
            conditions.append(SynthesisCondition(
                material_name=material,
                target_formula=material,
                method=method,
                precursors=precursors,
                steps=steps,
                total_time=total_time,
                max_temperature=max_temp
            ))

        return conditions

    def _extract_method(self, text: str) -> Optional[str]:
        """提取合成方法"""
        text_lower = text.lower()

        for method_en, method_cn in self.synthesis_methods.items():
            if method_en.lower() in text_lower or method_cn in text:
                return f"{method_en} ({method_cn})"

        return None

    def _extract_precursors(self, text: str) -> List[Precursor]:
        """提取前驱体"""
        precursors = []

        # 化学式模式
        formula_pattern = re.compile(r'\b([A-Z][a-z]?\d*(?:\s*·\s*\d*[A-Za-z0-9]+)*)\b')

        for pattern in self.precursor_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                precursor_text = match.group(1)
                # 提取化学式
                formulas = formula_pattern.findall(precursor_text)
                for formula in formulas:
                    if len(formula) > 1:  # 忽略单字母
                        precursors.append(Precursor(
                            name=formula,
                            formula=formula
                        ))

        return precursors

    def _extract_steps(self, text: str) -> List[SynthesisStep]:
        """提取合成步骤"""
        steps = []

        # 分割句子
        sentences = re.split(r'[.。]', text)

        step_num = 0
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue

            # 识别操作类型
            operation = self._identify_operation(sentence)
            if not operation:
                continue

            step_num += 1

            # 提取温度
            temp = self._extract_temperature(sentence)

            # 提取时间
            time = self._extract_time(sentence)

            # 提取气氛
            atmosphere, atm_type = self._extract_atmosphere(sentence)

            # 提取升温速率
            heating_rate = self._extract_heating_rate(sentence)

            # 提取冷却方式
            cooling = self._extract_cooling(sentence)

            steps.append(SynthesisStep(
                step_number=step_num,
                operation=operation,
                temperature=temp,
                time=time,
                atmosphere=atmosphere,
                atmosphere_type=atm_type,
                heating_rate=heating_rate,
                cooling_method=cooling,
                description=sentence[:200]
            ))

        return steps

    def _identify_operation(self, text: str) -> Optional[str]:
        """识别操作类型"""
        text_lower = text.lower()

        for operation, keywords in self.operation_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return operation

        return None

    def _extract_temperature(self, text: str) -> Optional[float]:
        """提取温度"""
        for pattern in self.temperature_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                # 如果是 K，转换为°C
                if 'K' in match.group(0) and 'kelvin' not in match.group(0).lower():
                    value = value - 273.15
                return round(value, 1)
        return None

    def _extract_time(self, text: str) -> Optional[float]:
        """提取时间 (转换为小时)"""
        for pattern in self.time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                unit = match.group(2).lower()

                if 'min' in unit:
                    value = value / 60  # 转换为小时

                return round(value, 2)
        return None

    def _extract_atmosphere(self, text: str) -> Tuple[Optional[str], Optional[AtmosphereType]]:
        """提取气氛"""
        for pattern in self.atmosphere_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                gas = match.group(1).lower()
                atm_type = self.atmosphere_map.get(gas, AtmosphereType.OTHER)
                return gas, atm_type
        return None, None

    def _extract_heating_rate(self, text: str) -> Optional[float]:
        """提取升温速率"""
        for pattern in self.heating_rate_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_cooling(self, text: str) -> Optional[str]:
        """提取冷却方式"""
        cooling_keywords = ['furnace cool', 'air cool', 'quench', 'slow cool', 'rapid cool']
        text_lower = text.lower()

        for keyword in cooling_keywords:
            if keyword in text_lower:
                return keyword

        return None

    def _extract_material(self, text: str) -> Optional[str]:
        """提取材料名称"""
        # 化学式模式
        formula_pattern = re.compile(r'\b([A-Z][a-z]?\d*)+\b')
        match = formula_pattern.search(text)
        if match:
            return match.group(0)
        return None

    def _calculate_total_time(self, steps: List[SynthesisStep]) -> Optional[float]:
        """计算总时间"""
        total = sum(s.time for s in steps if s.time)
        return round(total, 2) if total > 0 else None

    def _calculate_max_temperature(self, steps: List[SynthesisStep]) -> Optional[float]:
        """计算最高温度"""
        temps = [s.temperature for s in steps if s.temperature]
        return max(temps) if temps else None


# ============================================================================
# 3. 主函数
# ============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("Synthesis Condition Extractor - 合成条件提取器")
    print("=" * 60)

    # 1. 测试提取
    print("\n[1/3] 测试合成条件提取...")

    extractor = SynthesisConditionExtractor()

    test_texts = [
        # 英文示例
        "LiFePO4 was synthesized by solid-state reaction. "
        "The precursors Li2CO3, FeC2O4·2H2O, and NH4H2PO4 were mixed and ball-milled for 12 hours. "
        "The mixture was heated to 700°C for 12 hours in argon atmosphere, "
        "then furnace-cooled to room temperature.",

        # 水热法示例
        "TiO2 nanoparticles were prepared by hydrothermal method. "
        "Titanium isopropoxide was dissolved in ethanol and stirred for 2 hours. "
        "The solution was heated at 180°C for 24 hours in a Teflon-lined autoclave.",

        # 溶胶 - 凝胶法示例
        "BaTiO3 was synthesized via sol-gel process. "
        "Barium acetate and titanium isopropoxide were mixed with molar ratio 1:1. "
        "The gel was dried at 80°C and calcined at 800°C for 4 hours in air.",

        # 中文示例
        "采用固相反应法合成 LiCoO2。将 Li2CO3 和 Co3O4 按化学计量比混合，"
        "在 900°C 下烧结 24 小时，气氛为氧气。自然冷却至室温。",
    ]

    all_conditions = []

    for i, text in enumerate(test_texts, 1):
        print(f"\n示例 {i}: {text[:80]}...")
        conditions = extractor.extract(text)

        for cond in conditions:
            print(f"  材料：{cond.material_name}")
            print(f"  方法：{cond.method}")
            print(f"  前驱体：{len(cond.precursors)} 个")
            for p in cond.precursors[:3]:
                print(f"    - {p.name}")
            print(f"  步骤：{len(cond.steps)} 个")
            for step in cond.steps[:3]:
                print(f"    步骤{step.step_number}: {step.operation}")
                if step.temperature:
                    print(f"      温度：{step.temperature}°C")
                if step.time:
                    print(f"      时间：{step.time}h")
                if step.atmosphere:
                    print(f"      气氛：{step.atmosphere}")

            if cond.max_temperature:
                print(f"  最高温度：{cond.max_temperature}°C")
            if cond.total_time:
                print(f"  总时间：{cond.total_time}h")

        all_conditions.extend(conditions)

    # 2. 保存为 JSON
    print("\n[2/3] 保存结构化数据...")

    output_data = [cond.to_dict() for cond in all_conditions]
    output_path = Path("data/synthesis-condition-examples.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"保存 {len(output_data)} 条合成条件到 {output_path}")

    # 3. 统计
    print("\n[3/3] 统计信息...")
    print(f"  总合成条件：{len(all_conditions)}")
    print(f"  总步骤数：{sum(len(c.steps) for c in all_conditions)}")
    print(f"  总前驱体数：{sum(len(c.precursors) for c in all_conditions)}")

    methods = {}
    for cond in all_conditions:
        if cond.method:
            method_short = cond.method.split(' ')[0]
            methods[method_short] = methods.get(method_short, 0) + 1

    print(f"  合成方法分布：{methods}")

    print("\n" + "=" * 60)
    print("合成条件提取器准备完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
