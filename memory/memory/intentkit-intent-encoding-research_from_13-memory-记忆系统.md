# intentkit 意图编码机制研究

**日期:** 2026-03-07  
**来源:** GitHub - crestalnetwork/intentkit  
**Stars:** 6.5k | **Forks:** 699 | **License:** MIT

---

## 📦 项目概述

**IntentKit** 是一个开源的、自托管的云端代理集群框架，用于管理协作式 AI 代理团队。

**核心定位:**
- **Cloud-Native** (云原生) vs Local-First (本地优先)
- 多代理协作系统
- 可扩展技能系统
- Web3/区块链集成可选

**技术栈:**
- Python 92% (核心逻辑)
- TypeScript 7.4% (前端)
- Go 0.4% (集成服务)

---

## 🏗️ 架构分析

### 目录结构

```
intentkit/
├── agent_docs/        # 代理文档和配置
├── app/              # 主应用入口
├── docs/             # 用户文档
├── frontend/         # React 前端
├── integrations/     # 第三方集成
│   └── telegram/     # Telegram 机器人
├── intentkit/        # 核心库
│   ├── agents/       # 代理定义
│   ├── skills/       # 技能实现
│   ├── intents/      # 意图定义 ⭐
│   └── utils/        # 工具函数
├── scripts/          # 部署和运维脚本
└── tests/            # 测试用例
```

### 核心模块

#### 1. 意图模块 (intents/)

**职责:**
- 定义意图 schema
- 意图解析和验证
- 意图 - 代理映射

**关键文件:**
```
intents/
├── __init__.py       # 意图注册
├── base.py          # 基础意图类
├── schema.py        # 意图 schema 定义
└── parser.py        # 意图解析器
```

**意图定义示例:**
```python
from intentkit.intents.base import Intent

class SearchIntent(Intent):
    """搜索意图"""
    name: str = "search"
    description: str = "搜索信息"
    parameters: dict = {
        "query": {"type": "string", "required": True},
        "source": {"type": "string", "required": False}
    }
    
    async def execute(self, agent):
        return await agent.search(self.parameters["query"])
```

#### 2. 代理模块 (agents/)

**职责:**
- 代理定义和配置
- 代理间通信
- 任务分配和协调

**关键文件:**
```
agents/
├── __init__.py       # 代理注册
├── base.py          # 基础代理类
├── coordinator.py   # 协调器
└── worker.py        # 工作代理
```

#### 3. 技能模块 (skills/)

**职责:**
- 技能定义和注册
- 技能执行引擎
- 技能组合和编排

**关键文件:**
```
skills/
├── __init__.py       # 技能注册
├── base.py          # 基础技能类
├── web_search.py    # Web 搜索技能
├── crypto.py        # 加密货币技能
└── social.py        # 社交媒体技能
```

---

## 💡 意图编码机制

### 意图生命周期

```
用户输入
    ↓
意图解析 (parser.py)
    ↓
意图验证 (schema.py)
    ↓
意图 - 代理映射
    ↓
代理执行
    ↓
结果返回
```

### 意图 Schema

**核心组件:**
1. **意图名称** - 唯一标识符
2. **描述** - 自然语言描述
4. **参数定义** - JSON Schema 格式
5. **执行方法** - async execute 方法

**示例:**
```python
{
    "name": "search",
    "description": "搜索信息",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "source": {"type": "string"}
        },
        "required": ["query"]
    },
    "success_criteria": {
        "type": "object",
        "properties": {
            "results_found": {"type": "boolean"},
            "confidence": {"type": "number"}
        }
    }
}
```

### 意图 - 信念对齐

**intentkit 的意图定义与信念探针的关联:**

| intentkit 组件 | 信念探针组件 | 整合点 |
|---------------|-------------|--------|
| 意图 Schema | 信念检测目标 | 定义"成功"标准 |
| 意图验证 | 置信度阈值 | 验证置信度 |
| 成功标准 | 早退条件 | 意图达成度评估 |
| 代理执行 | 模型推理 | 信念检测执行 |

---

## 🔗 与创意 3 验证整合方案

### 架构层次

```
┌─────────────────────────────────────────┐
│         intentkit 意图层                 │
│  - 意图定义 (Intent Schema)             │
│  - 成功标准 (Success Criteria)          │
│  - 参数验证 (Parameter Validation)      │
├─────────────────────────────────────────┤
│         信念探针层                       │
│  - 确定性检测 (Confidence Detection)    │
│  - 意图达成度评估 (Intent Achievement)  │
│  - 动态阈值调整 (Dynamic Threshold)     │
├─────────────────────────────────────────┤
│         早退决策层                       │
│  - 意图 - 信念对齐度 (Intent-Belief Alignment)
│  - 早退决策 (Early Exit Decision)       │
│  - 资源分配 (Resource Allocation)       │
├─────────────────────────────────────────┤
│         模型执行层                       │
│  - Qwen3.5-2B + 早退优化                │
│  - 多代理协调 (Multi-Agent Coordination)│
└─────────────────────────────────────────┘
```

### 整合实现步骤

#### 步骤 1: 意图 Schema 扩展

**扩展 intentkit 意图定义，添加信念检测配置:**

```python
class EnhancedIntent(Intent):
    """增强意图 - 支持信念探针"""
    
    # 原有字段
    name: str
    description: str
    parameters: dict
    
    # 新增字段 - 信念探针配置
    belief_config: dict = {
        "confidence_threshold": 0.8,  # 置信度阈值
        "min_layers": 3,              # 最小检测层数
        "early_exit_enabled": True    # 是否启用早退
    }
    
    # 成功标准扩展
    success_criteria: dict = {
        "intent_achieved": {"type": "boolean"},
        "belief_confidence": {"type": "number"},
        "layers_used": {"type": "integer"}
    }
```

#### 步骤 2: 信念探针集成

**在意图执行器中集成信念探针:**

```python
class BeliefAwareExecutor:
    """信念感知执行器"""
    
    def __init__(self, agent, probes):
        self.agent = agent
        self.probes = probes  # 24 层信念探针
    
    async def execute_with_early_exit(self, intent):
        """执行意图并支持早退"""
        
        # 获取意图的置信度配置
        threshold = intent.belief_config["confidence_threshold"]
        min_layers = intent.belief_config["min_layers"]
        
        # 执行并监控信念
        consecutive_high = 0
        layers_used = 0
        
        for layer_idx in range(1, 25):
            # 获取该层激活
            activation = await self.get_layer_activation(layer_idx)
            
            # 信念探针检测
            confidence = self.probes[layer_idx-1].predict_proba([activation])[0][1]
            layers_used = layer_idx
            
            # 检查早退条件
            if confidence >= threshold:
                consecutive_high += 1
                if consecutive_high >= min_layers:
                    # 早退决策
                    return {
                        "result": "early_exit",
                        "layers_used": layers_used,
                        "confidence": confidence
                    }
            else:
                consecutive_high = 0
        
        # 使用全部层
        return {
            "result": "full_model",
            "layers_used": 24,
            "confidence": confidence
        }
```

#### 步骤 3: 意图 - 信念对齐度量化

**设计对齐度评估函数:**

```python
def calculate_alignment(intent, belief_result):
    """计算意图 - 信念对齐度"""
    
    # 1. 意图达成度 (0-1)
    intent_achievement = 1.0 if intent.success_criteria_met else 0.0
    
    # 2. 信念置信度 (0-1)
    belief_confidence = belief_result["confidence"]
    
    # 3. 效率得分 (早退奖励)
    efficiency = 1 - (belief_result["layers_used"] / 24)
    
    # 4. 综合对齐度
    alignment = (
        0.5 * intent_achievement +      # 意图达成 50%
        0.3 * belief_confidence +       # 信念置信 30%
        0.2 * efficiency                # 效率奖励 20%
    )
    
    return {
        "alignment_score": alignment,
        "components": {
            "intent_achievement": intent_achievement,
            "belief_confidence": belief_confidence,
            "efficiency": efficiency
        }
    }
```

---

## 📋 实施计划

### 阶段 1: 基础集成 (1-2 周)

- [ ] 扩展 intentkit 意图 Schema
- [ ] 集成信念探针检测
- [ ] 实现基础早退逻辑
- [ ] 单元测试

### 阶段 2: 优化调整 (2-3 周)

- [ ] 动态阈值调整算法
- [ ] 意图 - 信念对齐度量化
- [ ] 多代理早退协调
- [ ] 性能基准测试

### 阶段 3: 生产部署 (1-2 周)

- [ ] 配置管理优化
- [ ] 监控和日志
- [ ] 文档完善
- [ ] 生产环境部署

---

## 📚 参考资源

- [intentkit GitHub](https://github.com/crestalnetwork/intentkit)
- [intentkit 文档](https://github.com/crestalnetwork/intentkit/tree/main/docs)
- [创意 3 验证笔记](../memory/medium-research-intent-engineering.md)
- [开源 AI 架构研究](../memory/open-source-ai-architecture-research.md)

---

*持续更新中...*
