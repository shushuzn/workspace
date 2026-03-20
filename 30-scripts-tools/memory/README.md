# Dual-layer Memory System

AI Agent 双层记忆架构 - 短期工作记忆 + 长期归档记忆

## 架构

```
┌─────────────────────────────────────┐
│         Working Memory              │
│    (短期上下文 - 当前任务相关)       │
│    - Token: <5000                   │
│    - 生命周期: 当前会话             │
│    - LRU 淘汰策略                    │
└─────────────────────────────────────┘
                ↓ 遗忘/归档
┌─────────────────────────────────────┐
│         Archive Memory              │
│    (长期记忆 - 重要信息)            │
│    - SQLite 持久化                  │
│    - 向量检索（简化版：关键词）      │
│    - 自动遗忘机制                   │
└─────────────────────────────────────┘
```

## 核心特性

| 特性 | 描述 |
|------|------|
| **ImportanceScorer** | 3维度评分（频率/反馈/独特性） |
| **ForgettingMechanism** | 模仿人脑遗忘曲线，半衰期保护 |
| **SessionBridge** | 跨Session继承偏好+决策+项目状态 |
| **自动分层** | importance≥0.7 → 直接归档 |

## 安装

```bash
# 已在 30-scripts-tools/memory/ 中
cd 30-scripts-tools
```

## 使用方法

### Python API

```python
from memory import DualLayerMemory

# 初始化
memory = DualLayerMemory(token_budget=5000)

# 添加记忆（自动分层）
memory.add("我更喜欢简洁的代码风格", "preference")
memory.add("决定使用向量数据库方案", "decision")

# 获取上下文
context = memory.get_context()

# 搜索
results = memory.search("数据库", top_k=5)

# 跨Session继承
essential = memory.bridge_to("new_session_20260320")
```

### CLI

```bash
# 添加记忆
py memory/cli.py add "我想要蓝色主题" --type preference

# 列出当前记忆
py memory/cli.py list

# 搜索
py memory/cli.py search "蓝色"

# 统计
py memory/cli.py stats

# 压缩
py memory/cli.py compress

# 跨Session导出
py memory/cli.py bridge --session new_session_001
```

### Importance Scorer

```python
from memory import ImportanceScorer

scorer = ImportanceScorer()

# 计算重要性
score = scorer.calculate("我更喜欢简洁代码", "preference", {})
# 返回: 0.0 - 1.0

# 批量评分
items = [
    {"content": "A", "type": "preference", "metadata": {}},
    {"content": "B", "type": "conversation", "metadata": {}},
]
ranked = scorer.rank_items(items, top_k=10)
```

### Forgetting Mechanism

```python
from memory import ForgettingMechanism

fm = ForgettingMechanism()

# 计算衰减
decay = fm.calculate_decay(0.7, 7)  # 7天后的重要性

# 判断是否遗忘
should_forget = fm.should_forget(0.2, "conversation", 30)

# 建议保留时间
retention = fm.suggest_retention(0.7, "preference")
# {"recommended_retention_days": 56, ...}
```

### Session Bridge

```python
from memory import SessionBridge

bridge = SessionBridge()

# 导出essential信息
essential = bridge.export_essential(working, archive, "new_session_id")

# 保存到文件
bridge.save_essential(essential, "path/to/essential.json")

# 导入到新session
items = bridge.import_essential(essential)
```

## 文件结构

```
memory/
├── __init__.py              # 模块导出
├── models.py                # 数据模型
├── dual_layer_memory.py    # 主控制器
├── working_memory.py       # 短期记忆
├── archive_memory.py       # 长期存储 (SQLite)
├── importance_scorer.py    # 重要性评分
├── forgetting_mechanism.py # 遗忘曲线
├── session_bridge.py       # 跨Session继承
├── cli.py                  # 命令行工具
├── test_memory.py          # 测试套件
└── README.md              # 本文档
```

## 测试

```bash
cd memory
py test_memory.py
```

## 配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `token_budget` | 5000 | 工作记忆token上限 |
| `half_life_days` | 7 | 遗忘半衰期 |
| `archive_threshold` | 0.3 | 归档阈值 |
| `delete_threshold` | 0.1 | 删除阈值 |

## 评分权重

- **操作频率**: 30%
- **用户反馈**: 40%
- **独特性**: 30%

---

**版本**: 1.0.0  
**创建时间**: 2026-03-20