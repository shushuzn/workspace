# intentkit 集成指南

**Integrating Belief Probes with intentkit**

日期：2026-03-07  
作者：Claw (OpenClaw)  
版本：v0.1.0

---

## 📋 概述

本指南介绍如何将信念探针早退机制集成到 intentkit 框架中，实现基于意图 - 信念对齐度的动态早退决策。

**集成目标:**
- 保持 intentkit 原有架构
- 添加信念探针支持
- 实现早退决策层
- 最小化代码改动

---

## 🏗️ 集成架构

```
intentkit/
├── intentkit/
│   ├── intents/
│   │   ├── base.py              # 原基础意图类
│   │   └── enhanced.py          # NEW: 增强意图类
│   ├── agents/
│   │   ├── executor.py          # 原执行器
│   │   └── belief_executor.py   # NEW: 信念感知执行器
│   └── probes/                  # NEW: 信念探针模块
│       ├── __init__.py
│       ├── loader.py            # 探针加载器
│       └── alignment.py         # 对齐度计算器
└── examples/
    └── belief_integration/      # NEW: 集成示例
```

---

## 🔧 集成步骤

### 步骤 1: 安装依赖

```bash
# 进入 intentkit 目录
cd intentkit

# 安装额外依赖
pip install numpy scikit-learn
```

### 步骤 2: 复制信念探针模块

```bash
# 复制探针模块到 intentkit
cp -r ../intent-belief-integration/ belief_integration/

# 复制信念探针文件 (24 层)
cp -r belief-probes-v2/ intentkit/probes/
```

### 步骤 3: 修改意图基类

**文件:** `intentkit/intents/base.py`

```python
# 在文件顶部添加导入
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

# 添加信念配置类
class BeliefConfig(BaseModel):
    """信念探针配置"""
    confidence_threshold: float = 0.8
    min_consecutive_layers: int = 3
    early_exit_enabled: bool = True
    min_layers: int = 5
    max_layers: int = 24

# 修改 Intent 类
class Intent(BaseModel):
    # ... 原有字段 ...
    
    # 新增信念配置
    belief_config: Optional[BeliefConfig] = Field(
        default=None,
        description="信念探针配置"
    )
    
    # 新增执行结果
    execution_result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="执行结果"
    )
```

### 步骤 4: 创建信念感知执行器

**文件:** `intentkit/agents/belief_executor.py`

```python
"""
信念感知执行器 - 支持早退决策
"""

import pickle
import numpy as np
from pathlib import Path
from typing import Callable, Awaitable, Dict, Any

from ..intents.base import Intent, BeliefConfig


class BeliefProbe:
    """信念探针包装器"""
    
    def __init__(self, probe_path: str):
        with open(probe_path, 'rb') as f:
            self.probe = pickle.load(f)
    
    def predict_confidence(self, activation: np.ndarray) -> float:
        if activation.ndim == 1:
            activation = activation.reshape(1, -1)
        proba = self.probe.predict_proba(activation)[0]
        return float(proba[1])


class BeliefAwareExecutor:
    """信念感知执行器"""
    
    def __init__(self, probes_dir: str = "probes"):
        self.probes = []
        self._load_probes(probes_dir)
    
    def _load_probes(self, probes_dir: str):
        """加载 24 层信念探针"""
        base_path = Path(__file__).parent / probes_dir
        
        for layer_idx in range(1, 25):
            probe_path = base_path / f"probe_layer_{layer_idx}.pkl"
            if probe_path.exists():
                self.probes.append(BeliefProbe(str(probe_path)))
            else:
                raise FileNotFoundError(f"探针文件不存在：{probe_path}")
        
        print(f"[BeliefExecutor] 已加载 {len(self.probes)} 层信念探针")
    
    async def execute(
        self,
        intent: Intent,
        get_activation_fn: Callable[[int], np.ndarray]
    ) -> Dict[str, Any]:
        """执行意图并支持早退"""
        
        config = intent.belief_config
        
        # 如果不启用早退，使用原执行器
        if not config or not config.early_exit_enabled:
            return await self._execute_original(intent)
        
        # 早退执行
        consecutive_high = 0
        
        for layer_idx in range(1, config.max_layers + 1):
            # 获取该层激活
            activation = get_activation_fn(layer_idx)
            
            # 信念探针检测
            confidence = self.probes[layer_idx - 1].predict_confidence(activation)
            
            # 检查早退条件
            if confidence >= config.confidence_threshold:
                consecutive_high += 1
                
                if (consecutive_high >= config.min_consecutive_layers and 
                    layer_idx >= config.min_layers):
                    
                    return {
                        "exit_type": "early_exit",
                        "layers_used": layer_idx,
                        "final_confidence": confidence,
                        "success": True
                    }
            else:
                consecutive_high = 0
        
        # 使用全部层
        return {
            "exit_type": "full_model",
            "layers_used": 24,
            "success": True
        }
    
    async def _execute_original(self, intent: Intent) -> Dict[str, Any]:
        """调用原有执行器"""
        # TODO: 调用 intentkit 原有执行逻辑
        return {
            "exit_type": "full_model",
            "layers_used": 24,
            "success": True
        }
```

### 步骤 5: 创建对齐度计算器

**文件:** `intentkit/probes/alignment.py`

```python
"""
意图 - 信念对齐度计算
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AlignmentResult:
    """对齐度计算结果"""
    alignment_score: float
    intent_achievement: float
    belief_confidence: float
    efficiency: float
    weights: Dict[str, float]


class AlignmentCalculator:
    """对齐度计算器"""
    
    DEFAULT_WEIGHTS = {
        "intent": 0.5,
        "belief": 0.3,
        "efficiency": 0.2
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
    
    def calculate(
        self,
        intent_achieved: bool,
        belief_confidence: float,
        layers_used: int,
        total_layers: int = 24
    ) -> AlignmentResult:
        """计算对齐度"""
        intent_score = 1.0 if intent_achieved else 0.0
        efficiency = 1 - (layers_used / total_layers)
        
        alignment = (
            self.weights["intent"] * intent_score +
            self.weights["belief"] * belief_confidence +
            self.weights["efficiency"] * efficiency
        )
        
        return AlignmentResult(
            alignment_score=alignment,
            intent_achievement=intent_score,
            belief_confidence=belief_confidence,
            efficiency=efficiency,
            weights=self.weights
        )
```

### 步骤 6: 修改主执行流程

**文件:** `intentkit/agents/executor.py`

```python
# 在文件顶部添加导入
from .belief_executor import BeliefAwareExecutor
from ..probes.alignment import AlignmentCalculator

# 在执行器类中添加
class AgentExecutor:
    def __init__(self):
        self.belief_executor = BeliefAwareExecutor()
        self.alignment_calculator = AlignmentCalculator()
    
    async def execute_intent(self, intent: Intent) -> Dict[str, Any]:
        """执行意图"""
        
        # 定义激活获取函数
        def get_activation(layer_idx: int) -> np.ndarray:
            # TODO: 从模型获取实际激活
            pass
        
        # 使用信念感知执行器
        result = await self.belief_executor.execute(
            intent,
            get_activation
        )
        
        # 计算对齐度
        alignment = self.alignment_calculator.calculate(
            intent_achieved=result["success"],
            belief_confidence=result.get("final_confidence", 0.0),
            layers_used=result["layers_used"]
        )
        
        # 更新执行结果
        result["alignment_score"] = alignment.alignment_score
        result["efficiency"] = alignment.efficiency
        
        return result
```

---

## 📝 使用示例

### 基础示例

```python
from intentkit.intents.base import Intent, BeliefConfig
from intentkit.agents.executor import AgentExecutor

# 创建带信念配置的意图
intent = Intent(
    name="search",
    description="搜索信息",
    belief_config=BeliefConfig(
        confidence_threshold=0.8,
        min_consecutive_layers=3,
        min_layers=5
    )
)

# 执行
executor = AgentExecutor()
result = await executor.execute_intent(intent)

print(f"使用层数：{result['layers_used']}/24")
print(f"对齐度：{result['alignment_score']:.4f}")
```

### 高级示例

```python
# 为不同类型意图配置不同阈值
search_intent = Intent(
    name="search",
    belief_config=BeliefConfig(
        confidence_threshold=0.75,  # 搜索可以降低阈值
        min_layers=3
    )
)

math_intent = Intent(
    name="math",
    belief_config=BeliefConfig(
        confidence_threshold=0.9,   # 数学需要更高置信度
        min_layers=10
    )
)

creative_intent = Intent(
    name="creative",
    belief_config=BeliefConfig(
        confidence_threshold=0.7,   # 创意可以降低阈值
        min_layers=2
    )
)
```

---

## 🧪 测试

### 单元测试

```python
import pytest
from intentkit.probes.alignment import AlignmentCalculator

def test_alignment_calculation():
    calculator = AlignmentCalculator()
    
    result = calculator.calculate(
        intent_achieved=True,
        belief_confidence=0.92,
        layers_used=12
    )
    
    assert result.alignment_score > 0.8
    assert result.efficiency == 0.5  # 12/24 = 0.5

def test_batch_calculation():
    calculator = AlignmentCalculator()
    
    executions = [
        {"intent_achieved": True, "belief_confidence": 0.92, "layers_used": 12},
        {"intent_achieved": True, "belief_confidence": 0.95, "layers_used": 24},
    ]
    
    stats = calculator.calculate_batch(executions)
    assert stats["count"] == 2
    assert 0.8 < stats["avg_alignment"] < 0.95
```

---

## 📊 性能优化

### 探针缓存

```python
class CachedBeliefExecutor(BeliefAwareExecutor):
    """带缓存的信念执行器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}
    
    def predict_confidence(self, layer_idx: int, activation: np.ndarray) -> float:
        # 使用激活的哈希作为缓存键
        cache_key = hash(activation.tobytes())
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        confidence = self.probes[layer_idx - 1].predict_confidence(activation)
        self._cache[cache_key] = confidence
        return confidence
```

### 批量预测

```python
def predict_batch(self, activations: np.ndarray) -> np.ndarray:
    """批量预测置信度"""
    return self.probe.predict_proba(activations)[:, 1]
```

---

## 🔍 故障排查

### 常见问题

**Q: 探针文件找不到**
```
FileNotFoundError: 探针文件不存在：probes/probe_layer_1.pkl
```
**A:** 确保探针文件已复制到正确目录

**Q: 早退不触发**
**A:** 检查配置：
- `confidence_threshold` 是否过高
- `min_consecutive_layers` 是否过大
- `min_layers` 是否过大

**Q: 对齐度计算错误**
**A:** 检查输入值范围：
- `belief_confidence` 应在 0-1 之间
- `layers_used` 应在 1-24 之间

---

## 📚 参考

- [intentkit 官方文档](https://github.com/crestalnetwork/intentkit)
- [信念探针原始实现](../../30-scripts/intent-belief-integration/)
- [intentkit 研究笔记](../../memory/intentkit-intent-encoding-research.md)

---

*Claw @ OpenClaw*
