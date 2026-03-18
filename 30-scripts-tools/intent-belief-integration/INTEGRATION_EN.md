# Integration Guide

**Integrating Belief Probes with intentkit**

Date: 2026-03-07  
Author: Claw (@OpenClaw)  
Version: v0.1.0

---

## Overview

This guide shows how to integrate belief probe early exit mechanism into intentkit framework.

**Integration Goals:**
- Maintain intentkit architecture
- Add belief probe support
- Implement early exit decision layer
- Minimal code changes

---

## Architecture

```
intentkit/
├── intentkit/
│   ├── intents/
│   │   ├── base.py              # Original base intent
│   │   └── enhanced.py          # NEW: Enhanced intent
│   ├── agents/
│   │   ├── executor.py          # Original executor
│   │   └── belief_executor.py   # NEW: Belief-aware executor
│   └── probes/                  # NEW: Belief probes module
│       ├── __init__.py
│       ├── loader.py            # Probe loader
│       └── alignment.py         # Alignment calculator
└── examples/
    └── belief_integration/      # NEW: Integration examples
```

---

## Integration Steps

### Step 1: Install Dependencies

```bash
cd intentkit
pip install numpy scikit-learn
```

### Step 2: Copy Belief Integration Module

```bash
# Copy integration module
cp -r belief_integration/ intentkit/

# Copy probe files (24 layers)
cp -r belief-probes-v2/ intentkit/probes/
```

### Step 3: Modify Intent Base Class

**File:** `intentkit/intents/base.py`

```python
# Add imports at top
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

# Add BeliefConfig class
class BeliefConfig(BaseModel):
    """Belief probe configuration"""
    confidence_threshold: float = 0.8
    min_consecutive_layers: int = 3
    early_exit_enabled: bool = True
    min_layers: int = 5
    max_layers: int = 24

# Modify Intent class
class Intent(BaseModel):
    # ... existing fields ...
    
    # NEW: Belief configuration
    belief_config: Optional[BeliefConfig] = Field(
        default=None,
        description="Belief probe configuration"
    )
    
    # NEW: Execution result
    execution_result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Execution result"
    )
```

### Step 4: Create Belief-Aware Executor

**File:** `intentkit/agents/belief_executor.py`

```python
"""
Belief-Aware Executor with Early Exit Logic
"""

import pickle
import numpy as np
from pathlib import Path
from typing import Callable, Awaitable, Dict, Any

from ..intents.base import Intent, BeliefConfig


class BeliefProbe:
    """Belief probe wrapper"""
    
    def __init__(self, probe_path: str):
        with open(probe_path, 'rb') as f:
            self.probe = pickle.load(f)
    
    def predict_confidence(self, activation: np.ndarray) -> float:
        if activation.ndim == 1:
            activation = activation.reshape(1, -1)
        proba = self.probe.predict_proba(activation)[0]
        return float(proba[1])


class BeliefAwareExecutor:
    """Belief-aware executor"""
    
    def __init__(self, probes_dir: str = "probes"):
        self.probes = []
        self._load_probes(probes_dir)
    
    def _load_probes(self, probes_dir: str):
        """Load 24-layer belief probes"""
        base_path = Path(__file__).parent / probes_dir
        
        for layer_idx in range(1, 25):
            probe_path = base_path / f"probe_layer_{layer_idx}.pkl"
            if probe_path.exists():
                self.probes.append(BeliefProbe(str(probe_path)))
            else:
                raise FileNotFoundError(f"Probe not found: {probe_path}")
        
        print(f"[BeliefExecutor] Loaded {len(self.probes)} layers")
    
    async def execute(
        self,
        intent: Intent,
        get_activation_fn: Callable[[int], np.ndarray]
    ) -> Dict[str, Any]:
        """Execute intent with early exit support"""
        
        config = intent.belief_config
        
        # If early exit disabled, use original executor
        if not config or not config.early_exit_enabled:
            return await self._execute_original(intent)
        
        # Early exit execution
        consecutive_high = 0
        
        for layer_idx in range(1, config.max_layers + 1):
            activation = get_activation_fn(layer_idx)
            confidence = self.probes[layer_idx - 1].predict_confidence(activation)
            
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
        
        return {
            "exit_type": "full_model",
            "layers_used": 24,
            "success": True
        }
    
    async def _execute_original(self, intent: Intent) -> Dict[str, Any]:
        """Call original executor"""
        # TODO: Call intentkit original execution logic
        return {
            "exit_type": "full_model",
            "layers_used": 24,
            "success": True
        }
```

### Step 5: Create Alignment Calculator

**File:** `intentkit/probes/alignment.py`

```python
"""
Intent-Belief Alignment Calculator
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AlignmentResult:
    """Alignment calculation result"""
    alignment_score: float
    intent_achievement: float
    belief_confidence: float
    efficiency: float
    weights: Dict[str, float]


class AlignmentCalculator:
    """Alignment calculator"""
    
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
        """Calculate alignment"""
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

### Step 6: Modify Main Execution Flow

**File:** `intentkit/agents/executor.py`

```python
# Add imports at top
from .belief_executor import BeliefAwareExecutor
from ..probes.alignment import AlignmentCalculator

# Add to AgentExecutor class
class AgentExecutor:
    def __init__(self):
        self.belief_executor = BeliefAwareExecutor()
        self.alignment_calculator = AlignmentCalculator()
    
    async def execute_intent(self, intent: Intent) -> Dict[str, Any]:
        """Execute intent"""
        
        def get_activation(layer_idx: int) -> np.ndarray:
            # TODO: Get actual activation from model
            pass
        
        result = await self.belief_executor.execute(intent, get_activation)
        
        alignment = self.alignment_calculator.calculate(
            intent_achieved=result["success"],
            belief_confidence=result.get("final_confidence", 0.0),
            layers_used=result["layers_used"]
        )
        
        result["alignment_score"] = alignment.alignment_score
        result["efficiency"] = alignment.efficiency
        
        return result
```

---

## Usage Examples

### Basic Example

```python
from intentkit.intents.base import Intent, BeliefConfig
from intentkit.agents.executor import AgentExecutor

# Create intent with belief config
intent = Intent(
    name="search",
    description="Search information",
    belief_config=BeliefConfig(
        confidence_threshold=0.8,
        min_consecutive_layers=3,
        min_layers=5
    )
)

# Execute
executor = AgentExecutor()
result = await executor.execute_intent(intent)

print(f"Layers used: {result['layers_used']}/24")
print(f"Alignment: {result['alignment_score']:.4f}")
```

### Advanced Example

```python
# Different thresholds for different intent types
search_intent = Intent(
    name="search",
    belief_config=BeliefConfig(
        confidence_threshold=0.75,  # Lower for search
        min_layers=3
    )
)

math_intent = Intent(
    name="math",
    belief_config=BeliefConfig(
        confidence_threshold=0.9,   # Higher for math
        min_layers=10
    )
)

creative_intent = Intent(
    name="creative",
    belief_config=BeliefConfig(
        confidence_threshold=0.7,   # Lower for creative
        min_layers=2
    )
)
```

---

## Testing

### Unit Tests

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
    assert result.efficiency == 0.5

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

## Performance Optimization

### Probe Caching

```python
class CachedBeliefExecutor(BeliefAwareExecutor):
    """Executor with caching"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}
    
    def predict_confidence(self, layer_idx: int, activation: np.ndarray) -> float:
        cache_key = hash(activation.tobytes())
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        confidence = self.probes[layer_idx - 1].predict_confidence(activation)
        self._cache[cache_key] = confidence
        return confidence
```

### Batch Prediction

```python
def predict_batch(self, activations: np.ndarray) -> np.ndarray:
    """Batch prediction"""
    return self.probe.predict_proba(activations)[:, 1]
```

---

## Troubleshooting

### Common Issues

**Q: Probe files not found**
```
FileNotFoundError: Probe not found: probes/probe_layer_1.pkl
```
**A:** Ensure probe files are copied to correct directory

**Q: Early exit not triggering**
**A:** Check configuration:
- Is `confidence_threshold` too high?
- Is `min_consecutive_layers` too large?
- Is `min_layers` too large?

**Q: Alignment calculation error**
**A:** Check input ranges:
- `belief_confidence` should be 0-1
- `layers_used` should be 1-24

---

## References

- [intentkit Documentation](https://github.com/crestalnetwork/intentkit)
- [Belief Probes Original Implementation](../../30-scripts/intent-belief-integration/)

---

*Claw @ OpenClaw*
