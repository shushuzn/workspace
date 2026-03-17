#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Synthesis Condition Extractor - 合成条件提取器

功能：
1. 从论文中提取材料合成条件
2. 支持多种合成方法 (固相法、溶胶 - 凝胶、水热、CVD 等)
3. 提取温度、时间、气氛、前驱体等关键参数
4. 构建反应路径

作者：Claw (AI Research OS)
创建时间：2026-03-05 22:25
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

class SynthesisMethod(Enum):
    """合成方法"""
    SOLID_STATE = "solid-state"  # 固相法
    SOL_GEL = "sol-gel"  # 溶胶 - 凝胶
    HYDROTHERMAL = "hydrothermal"  # 水热法
    SOLVOTHERMAL = "solvothermal"  # 溶剂热法
    CVD = "cvd"  # 化学气相沉积
    PVD = "pvd"  # 物理气相沉积
    COPRECIPITATION = "coprecipitation"  # 共沉淀
    MELTING = "melting"  # 熔融法
    ELECTROSPINNING = "electrospinning"  # 静电纺丝
    BALL_MILLING = "ball-milling"  # 球磨法
    UNKNOWN = "unknown"


@dataclass
class TemperatureCondition:
    """温度条件"""
    value: float
    unit: str  # °C, K
    stage: Optional[str] = None  # 加热阶段 (如 "calcination", "sintering")
    ramp_rate: Optional[float] = None  # 升温速率 (°C/min)
    holding_time: Optional[float] = None  # 保温时间 (hours)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TimeCondition:
    """时间条件"""
    value: float
    unit: str  # min, h, d
    stage: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AtmosphereCondition:
    """气氛条件"""
    gas: str  # air, N2, Ar, O2, H2, vacuum
    flow_rate: Optional[float] = None  # mL/min
    pressure: Optional[float] = None  # atm, Pa
    purity: Optional[str] = None  # 99.999%
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Precursor:
    """前驱体"""
    name: str
    formula: Optional[str] = None
    amount: Optional[float] = None
    unit: Optional[str] = None  # g, mol, mL
    molar_ratio: Optional[float] = None
    supplier: Optional[str] = None
    purity: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SynthesisStep:
    """合成步骤"""
    step_number: int
    description: str
    method: SynthesisMethod
    temperature: Optional[TemperatureCondition] = None
    time: Optional[TimeCondition] = None
    atmosphere: Optional[AtmosphereCondition] = None
    precursors: List[Precursor] = field(default_factory=list)
    products: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['method'] = self.method.value
        return result


@dataclass
class SynthesisRecipe:
    """合成配方"""
    material_name: str
    material_formula: Optional[str] = None
    method: SynthesisMethod = SynthesisMethod.UNKNOWN
    steps: List[SynthesisStep] = field(default_factory=list)
    overall_conditions: Dict = field(default_factory=dict)
    yield_: Optional[float] = None  # 产率 (%)
    purity: Optional[str] = None
    reference: Optional[str] = None  # 论文引用
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['method'] = self.method.value
        result['steps'] = [step.to_dict() for step in self.steps]
        return result


# ============================================================================
# 2. 合成方法检测器
# ============================================================================

class MethodDetector:
    """合成方法检测器"""
    
    METHOD_KEYWORDS = {
        SynthesisMethod.SOLID_STATE: [
            'solid-state', 'solid state', 'ceramic method', 'conventional method',
            '固相法', '固相反应', '陶瓷法'
        ],
        SynthesisMethod.SOL_GEL: [
            'sol-gel', 'sol gel', 'sol-gel method',
            '溶胶 - 凝胶', '溶胶凝胶法'
        ],
        SynthesisMethod.HYDROTHERMAL: [
            'hydrothermal', 'hydrothermal method', 'hydrothermal synthesis',
            '水热法', '水热合成'
        ],
        SynthesisMethod.SOLVOTHERMAL: [
            'solvothermal', 'solvothermal method',
            '溶剂热法', '溶剂热合成'
        ],
        SynthesisMethod.CVD: [
            'chemical vapor deposition', 'CVD', 'MOCVD', 'PECVD',
            '化学气相沉积'
        ],
        SynthesisMethod.PVD: [
            'physical vapor deposition', 'PVD', 'sputtering', 'evaporation',
            '物理气相沉积', '溅射'
        ],
        SynthesisMethod.COPRECIPITATION: [
            'coprecipitation', 'co-precipitation', 'precipitation method',
            '共沉淀法', '沉淀法'
        ],
        SynthesisMethod.MELTING: [
            'melting', 'melt', 'flux method', 'crystal growth',
            '熔融法', '助熔剂法'
        ],
        SynthesisMethod.BALL_MILLING: [
            'ball milling', 'mechanochemical', 'mechanical alloying',
            '球磨法', '机械合金化'
        ],
    }
    
    @classmethod
    def detect_method(cls, text: str) -> SynthesisMethod:
        """从文本中检测合成方法"""
        text_lower = text.lower()
        
        for method, keywords in cls.METHOD_KEYWORDS.items():
            if any(kw.lower() in text_lower for kw in keywords):
                return method
        
        return SynthesisMethod.UNKNOWN


# ============================================================================
# 3. 条件提取器
# ============================================================================

class ConditionExtractor:
    """条件提取器"""
    
    # 温度模式
    TEMPERATURE_PATTERNS = [
        # "heated at 800 °C"
        r'(?:heated|calcined|sintered|annealed|fired)\s+(?:at|to)\s+(\d+(?:\.\d+)?)\s*(°C|℃|C|K)',
        
        # "temperature of 800 °C"
        r'temperature\s+(?:of|at)\s+(\d+(?:\.\d+)?)\s*(°C|℃|C|K)',
        
        # "800 °C for 2 hours"
        r'(\d+(?:\.\d+)?)\s*(°C|℃|C|K)\s+(?:for)\s+(\d+(?:\.\d+)?)\s*(min|h|hours?|days?)',
        
        # "ramped to 800 °C at 5 °C/min"
        r'ramped\s+(?:to|up)\s+(\d+(?:\.\d+)?)\s*(°C|℃|C)\s+(?:at|with)\s+(\d+(?:\.\d+)?)\s*(°C/min|K/min)',
        
        # 中文："在 800°C 下煅烧"
        r'(?:在|于)\s*(\d+(?:\.\d+)?)\s*(°C|℃|K)\s*(?:下)?\s*(?:煅烧 | 烧结 | 加热 | 退火)',
    ]
    
    # 时间模式
    TIME_PATTERNS = [
        # "for 2 hours"
        r'for\s+(\d+(?:\.\d+)?)\s*(min|h|hours?|days?)',
        
        # "2 h", "30 min"
        r'(\d+(?:\.\d+)?)\s*(min|h|hours?|days?)',
        
        # 中文："保温 2 小时"
        r'(?:保温 | 保持|恒温)\s*(\d+(?:\.\d+)?)\s*(小时 | 分钟 | 天|h|min)',
    ]
    
    # 气氛模式
    ATMOSPHERE_PATTERNS = [
        # "in air", "under N2 atmosphere"
        r'(?:in|under)\s+(air|N2|N₂|Ar|Ar 气 | O2|O₂|H2|H₂|nitrogen|argon|oxygen|hydrogen|vacuum)\s*(?:atmosphere|flow|gas)?',
        
        # "flowing Ar (50 mL/min)"
        r'flowing\s+(N2|Ar|O2|H2|air)\s*\((\d+(?:\.\d+)?)\s*(mL/min|sccm)\)',
        
        # "under vacuum (10^-3 Pa)"
        r'under\s+vacuum\s*\((\d+(?:[eE][+-]?\d+)?(?:\.\d+)?)\s*(Pa|Torr|mbar|atm)\)',
        
        # 中文："在氮气气氛下"
        r'(?:在|于)\s*(氮气 | 氩气 | 氧气 | 氢气 | 空气 | 真空)\s*(?:气氛 | 环境 | 下)',
    ]
    
    # 前驱体模式
    PRECURSOR_PATTERNS = [
        # "Li2CO3 (99.9%, Sigma-Aldrich)"
        r'([A-Z][a-z]?\d*(?:\s*[+\-]?\d*)?)\s*\((\d+(?:\.\d+)?)\s*%,\s*([^)]+)\)',
        
        # "0.5 g of Li2CO3"
        r'(\d+(?:\.\d+)?)\s*(g|mg|mol|mmol|mL)\s+(?:of\s+)?([A-Z][a-z]?\d*(?:\s*[+\-]?\d*)?)',
        
        # "Li2CO3 and FePO4 were mixed"
        r'([A-Z][a-z]?\d*(?:\s*[+\-]?\d*)?)\s+and\s+([A-Z][a-z]?\d*(?:\s*[+\-]?\d*)?)\s+(?:were|was)\s+(?:mixed|dissolved)',
        
        # 中文："碳酸锂 (99.9%，阿拉丁)"
        r'([\u4e00-\u9fa5]+)\s*\((\d+(?:\.\d+)?)\s*%，\s*([^)]+)\)',
    ]
    
    # 摩尔比模式
    MOLAR_RATIO_PATTERNS = [
        # "molar ratio of 1:1"
        r'molar\s+ratio\s+(?:of)?\s*(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)',
        
        # "Li:Fe:P = 1:1:1"
        r'([A-Z][a-z]?)\s*:\s*([A-Z][a-z]?)\s*:\s*([A-Z][a-z]?)\s*=\s*(\d+)\s*:\s*(\d+)\s*:\s*(\d+)',
    ]
    
    @classmethod
    def extract_temperature(cls, text: str, stage: Optional[str] = None) -> Optional[TemperatureCondition]:
        """提取温度条件"""
        for pattern in cls.TEMPERATURE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                value = float(groups[0])
                unit = groups[1]
                
                # 标准化单位
                if unit.lower() in ['c', '℃', '°c']:
                    unit = '°C'
                
                # 检查是否有升温速率
                ramp_rate = None
                ramp_match = re.search(r'at\s+(\d+(?:\.\d+)?)\s*(°C/min|K/min)', text, re.IGNORECASE)
                if ramp_match:
                    ramp_rate = float(ramp_match.group(1))
                
                # 检查是否有保温时间
                holding_time = None
                time_match = re.search(r'for\s+(\d+(?:\.\d+)?)\s*(min|h|hours?)', text, re.IGNORECASE)
                if time_match:
                    holding_time = float(time_match.group(1))
                    if 'h' in time_match.group(2).lower():
                        holding_time *= 60  # 转换为分钟
                
                return TemperatureCondition(
                    value=value,
                    unit=unit,
                    stage=stage,
                    ramp_rate=ramp_rate,
                    holding_time=holding_time
                )
        
        return None
    
    @classmethod
    def extract_time(cls, text: str, stage: Optional[str] = None) -> Optional[TimeCondition]:
        """提取时间条件"""
        for pattern in cls.TIME_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                unit = match.group(2).lower()
                
                # 标准化单位
                if 'hour' in unit or unit == 'h':
                    unit = 'h'
                elif 'min' in unit:
                    unit = 'min'
                elif 'day' in unit:
                    unit = 'd'
                
                return TimeCondition(
                    value=value,
                    unit=unit,
                    stage=stage
                )
        
        return None
    
    @classmethod
    def extract_atmosphere(cls, text: str) -> Optional[AtmosphereCondition]:
        """提取气氛条件"""
        for pattern in cls.ATMOSPHERE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                gas = groups[0].lower()
                
                # 标准化气体名称
                gas_map = {
                    'n2': 'N2', 'nitrogen': 'N2', '氮气': 'N2',
                    'ar': 'Ar', 'argon': 'Ar', '氩气': 'Ar',
                    'o2': 'O2', 'oxygen': 'O2', '氧气': 'O2',
                    'h2': 'H2', 'hydrogen': 'H2', '氢气': 'H2',
                    'air': 'air', '空气': 'air',
                    'vacuum': 'vacuum', '真空': 'vacuum',
                }
                gas = gas_map.get(gas, gas)
                
                # 检查是否有流速
                flow_rate = None
                if len(groups) > 1 and groups[1]:
                    flow_rate = float(groups[1])
                
                # 检查是否有压力
                pressure = None
                pressure_match = re.search(r'\((\d+(?:[eE][+-]?\d+)?)\s*(Pa|Torr|mbar|atm)\)', text)
                if pressure_match:
                    pressure = float(pressure_match.group(1))
                
                return AtmosphereCondition(
                    gas=gas,
                    flow_rate=flow_rate,
                    pressure=pressure
                )
        
        return None
    
    @classmethod
    def extract_precursors(cls, text: str) -> List[Precursor]:
        """提取前驱体"""
        precursors = []
        
        for pattern in cls.PRECURSOR_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                groups = match.groups()
                
                if len(groups) == 3 and '%' in text[match.start():match.end()]:
                    # 纯度和供应商模式
                    precursors.append(Precursor(
                        name=groups[2],
                        purity=groups[1] + '%',
                        supplier=groups[2]
                    ))
                elif len(groups) >= 2:
                    # 量和化学式模式
                    try:
                        amount = float(groups[0])
                        unit = groups[1]
                        name = groups[2] if len(groups) > 2 else None
                        
                        precursors.append(Precursor(
                            name=name,
                            amount=amount,
                            unit=unit
                        ))
                    except (ValueError, IndexError):
                        continue
        
        return precursors


# ============================================================================
# 4. 反应路径构建器
# ============================================================================

class ReactionPathBuilder:
    """反应路径构建器"""
    
    REACTION_KEYWORDS = [
        'reacted', 'reacts', 'reaction',
        'converted', 'converts', 'conversion',
        'transformed', 'transforms', 'transformation',
        'decomposed', 'decomposes', 'decomposition',
        'formed', 'forms', 'formation',
        'produced', 'produces', 'production',
        'yielded', 'yields',
        '生成', '形成', '分解', '转化', '反应'
    ]
    
    @classmethod
    def extract_reaction_steps(cls, text: str) -> List[Dict]:
        """从文本中提取反应步骤"""
        steps = []
        
        # 分割句子
        sentences = re.split(r'[.。]', text)
        
        step_num = 1
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # 检查是否包含反应关键词
            if any(kw in sentence.lower() for kw in cls.REACTION_KEYWORDS):
                steps.append({
                    'step': step_num,
                    'description': sentence,
                })
                step_num += 1
        
        return steps


# ============================================================================
# 5. 合成条件提取器 (主类)
# ============================================================================

class SynthesisConditionExtractor:
    """合成条件提取器 - 整合所有功能"""
    
    def __init__(self):
        self.method_detector = MethodDetector()
        self.condition_extractor = ConditionExtractor()
        self.path_builder = ReactionPathBuilder()
    
    def extract(self, text: str) -> List[SynthesisRecipe]:
        """从文本中提取合成条件"""
        recipes = []
        
        # 1. 检测合成方法
        method = self.method_detector.detect_method(text)
        
        # 2. 提取温度条件
        temperature = self.condition_extractor.extract_temperature(text)
        
        # 3. 提取时间条件
        time_condition = self.condition_extractor.extract_time(text)
        
        # 4. 提取气氛条件
        atmosphere = self.condition_extractor.extract_atmosphere(text)
        
        # 5. 提取前驱体
        precursors = self.condition_extractor.extract_precursors(text)
        
        # 6. 提取反应步骤
        reaction_steps = self.path_builder.extract_reaction_steps(text)
        
        # 7. 构建合成配方
        if method != SynthesisMethod.UNKNOWN or temperature or precursors:
            recipe = SynthesisRecipe(
                material_name=self._extract_material_name(text),
                material_formula=self._extract_material_formula(text),
                method=method,
                steps=self._build_steps(temperature, time_condition, atmosphere, precursors, reaction_steps),
                reference=self._extract_reference(text)
            )
            recipes.append(recipe)
        
        return recipes
    
    def _extract_material_name(self, text: str) -> str:
        """提取材料名称"""
        # 简单实现：查找化学式或材料名
        match = re.search(r'([A-Z][a-z]?\d+(?:\s*[+\-]?\d*)?(?:\s+[A-Z][a-z]?\d+)*)', text)
        return match.group(1) if match else 'Unknown'
    
    def _extract_material_formula(self, text: str) -> Optional[str]:
        """提取材料化学式"""
        # 查找括号中的化学式
        match = re.search(r'\(([A-Z][a-z]?\d+(?:\s*[+\-]?\d*)?(?:\s+[A-Z][a-z]?\d+)*)\)', text)
        return match.group(1) if match else None
    
    def _build_steps(
        self,
        temperature: Optional[TemperatureCondition],
        time_condition: Optional[TimeCondition],
        atmosphere: Optional[AtmosphereCondition],
        precursors: List[Precursor],
        reaction_steps: List[Dict]
    ) -> List[SynthesisStep]:
        """构建合成步骤"""
        steps = []
        
        # 步骤 1: 前驱体准备
        if precursors:
            steps.append(SynthesisStep(
                step_number=1,
                description="前驱体准备",
                method=SynthesisMethod.UNKNOWN,
                precursors=precursors
            ))
        
        # 步骤 2: 合成反应
        if temperature or time_condition or atmosphere:
            step = SynthesisStep(
                step_number=len(steps) + 1,
                description="合成反应",
                method=SynthesisMethod.UNKNOWN,
                temperature=temperature,
                time=time_condition,
                atmosphere=atmosphere
            )
            steps.append(step)
        
        # 添加反应步骤
        for rxn_step in reaction_steps:
            steps.append(SynthesisStep(
                step_number=len(steps) + 1,
                description=rxn_step['description'],
                method=SynthesisMethod.UNKNOWN
            ))
        
        return steps
    
    def _extract_reference(self, text: str) -> Optional[str]:
        """提取参考文献信息"""
        # 简单实现：查找 DOI 或引用格式
        doi_match = re.search(r'10\.\d{4,}/\S+', text)
        if doi_match:
            return f"DOI: {doi_match.group(0)}"
        
        return None


# ============================================================================
# 6. 主函数
# ============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("Synthesis Condition Extractor - 合成条件提取器")
    print("=" * 60)
    
    # 1. 创建提取器
    print("\n[1/4] 初始化提取器...")
    extractor = SynthesisConditionExtractor()
    
    # 2. 测试提取
    print("\n[2/4] 测试合成条件提取...")
    
    test_texts = [
        # 英文示例
        """
        LiFePO4 was synthesized by solid-state reaction. 
        Li2CO3 (99.9%, Sigma-Aldrich) and FePO4 were mixed in a molar ratio of 1:1.
        The mixture was heated at 800 °C for 12 hours in Ar atmosphere.
        The heating rate was 5 °C/min.
        """,
        
        # 中文示例
        """
        采用溶胶 - 凝胶法制备二氧化钛纳米颗粒。
        将钛酸四丁酯 (99%, 阿拉丁) 溶解在无水乙醇中。
        在 60°C 下搅拌 2 小时，然后在空气中于 500°C 煅烧 3 小时。
        升温速率为 2°C/min。
        """,
        
        # 水热法示例
        """
        ZnO nanorods were synthesized via hydrothermal method.
        Zinc nitrate hexahydrate (0.1 M) and HMTA (0.1 M) were dissolved in deionized water.
        The solution was heated at 90 °C for 6 hours in a Teflon-lined autoclave.
        Products were washed and dried at 60 °C.
        """,
    ]
    
    all_recipes = []
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n示例 {i}:")
        recipes = extractor.extract(text)
        
        for recipe in recipes:
            print(f"  材料：{recipe.material_name}")
            print(f"  方法：{recipe.method.value}")
            print(f"  步骤数：{len(recipe.steps)}")
            
            for step in recipe.steps:
                print(f"    步骤{step.step_number}: {step.description[:50]}...")
                if step.temperature:
                    print(f"      温度：{step.temperature.value} {step.temperature.unit}")
                if step.time:
                    print(f"      时间：{step.time.value} {step.time.unit}")
                if step.atmosphere:
                    print(f"      气氛：{step.atmosphere.gas}")
            
            all_recipes.append(recipe)
    
    # 3. 保存为 JSON
    print("\n[3/4] 保存结构化数据...")
    
    output_data = [recipe.to_dict() for recipe in all_recipes]
    output_path = Path("data/synthesis-condition-examples.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"  保存 {len(output_data)} 个合成配方到 {output_path}")
    
    # 4. 统计信息
    print("\n[4/4] 统计信息...")
    
    method_counts = {}
    for recipe in all_recipes:
        method = recipe.method.value
        method_counts[method] = method_counts.get(method, 0) + 1
    
    print("  合成方法分布:")
    for method, count in method_counts.items():
        print(f"    {method}: {count}")
    
    print("\n" + "=" * 60)
    print("合成条件提取器准备完成！")
    print("=" * 60)
    
    print("\n📌 功能清单:")
    print("  ✅ 合成方法识别 (9 种常见方法)")
    print("  ✅ 温度条件提取 (含升温速率、保温时间)")
    print("  ✅ 时间条件提取")
    print("  ✅ 气氛条件提取 (气体、流速、压力)")
    print("  ✅ 前驱体识别 (化学式、纯度、供应商)")
    print("  ✅ 反应路径构建")
    print("  ✅ 中英文双语支持")


if __name__ == '__main__':
    main()
