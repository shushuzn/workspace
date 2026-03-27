# Agent Arena — AI 对手系统设计文档

## 概述

为 `agent-arena` 设计 AI 驱动的竞技场对手生成机制。每次玩家挑战竞技场时，用 AI 生成一个有名字、背景故事、性格标签的独特对手，让对战有叙事感和新鲜感。

**核心原则**：
- AI 生成叙事，玩家每次对战都有独特对手
- 叙事内容影响属性（性格 → 属性偏向）
- 竞技公平性由难度系数保证
- 对手历史记录展示，增加沉浸感

---

## 对手生成流程

### Step 1: 计算基准战力

从玩家已拥有的 Agent 中，取平均战力，乘以难度系数：

```
难度系数范围: 0.8 ~ 1.2
随机波动: ±10%
```

### Step 2: 性格标签抽取

从预设列表中随机选择，或由 AI 生成时一同产出：

| 性格 | 属性修正 |
|------|---------|
| 鲁莽 | speed +30%, intelligence -10% |
| 狡猾 | intelligence +25%, endurance -10% |
| 坚韧 | endurance +30%, creativity -10% |
| 均衡 | 无修正 |
| 狂暴 | all.stats +15%, endurance -20% |
| 冷静 | intelligence +15%, speed -10% |

### Step 3: AI 生成叙事

调用 AI 生成名字 + 背景故事 + 性格标签。

**Prompt 模板：**

```
你是一个游戏叙事设计师。请为玩家的竞技场对手生成简短信息。

格式（严格按此格式返回，每行一个字段）：
名字: [角色名]
性格: [从列表选择：鲁莽/狡猾/坚韧/均衡/狂暴/冷静]
故事: [1-2句背景故事，要有趣]

要求：
- 名字要有科幻/赛博朋克风格，2-4个字
- 性格标签从给定列表中选一个
- 故事内容要有趣味性，可以提及过去的战绩、名声或特点
- 不要编造具体的战力数值
```

**示例输出：**
```
名字: 噬光者
性格: 狂暴
故事: 曾以一己之力摧毁了第7区的防御网络，如今带着残破的机甲游荡于暗网深处。
```

### Step 4: 构建对手 Agent

```javascript
interface ArenaOpponent {
  id: string;
  name: string;
  backstory: string;      // AI 生成
  personality: string;     // 性格标签
  rarity: string;
  stats: { intelligence, speed, creativity, endurance };
  power: number;
  avatar: string;
  seed: number;          // 重现用随机种子
  result: 'win' | 'lose' | null;
  rewards: { xp: number, currency: number };
  createdAt: number;
}
```

---

## 竞技场流程

### UI 状态机

```
STAGE_SELECT   → 选择出战 Agent
STAGE_LOADING  → AI 生成对手（加载动画）
STAGE_REVEAL   → 对手亮相（显示名字/故事/属性）
STAGE_BATTLE   → 战斗动画（自动结算，3-5秒）
STAGE_RESULT   → 胜负 + 奖励展示
STAGE_HISTORY  → 历史对手记录（可选）
```

### 各阶段显示内容

**STAGE_LOADING：**
- 对手名字动画（打字机效果）
- "正在召唤对手..." 提示

**STAGE_REVEAL：**
- 对手头像（大尺寸）
- 对手名字（标题）
- 性格标签（chip 样式）
- 背景故事（1-2句，渐入效果）
- 战力对比条（玩家 vs 对手）

**STAGE_RESULT：**
- 胜负文案（动态生成）
- 获得奖励：经验 + 星尘币
- 「再来一局」和「返回」按钮

---

## 奖励机制

| 结果 | 经验 | 星尘币 |
|------|------|-------|
| 胜利 | 50 * 难度系数 | 20 * 难度系数 |
| 失败 | 10 | 5 |

---

## 数据持久化

```
localStorage key: "arena_history"
格式: ArenaOpponent[]（最近20条）
```

---

## 组件改动范围

### 新增文件

```
src/components/
  ArenaPanel.jsx          # 竞技场主面板（状态机）
  ArenaPanel.svelte
  OpponentReveal.jsx      # 对手亮相动画
  OpponentReveal.svelte
  BattleResult.jsx         # 战斗结果展示
  BattleResult.svelte

src/stores/
  arenaStore.js            # 竞技场状态（writable store）

src/services/
  aiOpponentService.js    # AI 对手生成服务
```

### 修改文件

```
src/App.svelte             # 添加 ArenaPanel 路由/入口
src/components/Home.svelte  # 添加「竞技场」入口按钮
src/stores/gameStore.js    # 添加 arenaHistory 字段
```

---

## AI 服务实现

```javascript
// src/services/aiOpponentService.js
import { ANTHROPIC_API_KEY } from '../config';

const SYSTEM_PROMPT = `你是一个游戏叙事设计师...`; // 见上文

export async function generateOpponent(difficulty = 1.0) {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
      'content-type': 'application/json',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 200,
      system: SYSTEM_PROMPT,
      messages: [{
        role: 'user',
        content: '生成一个竞技场对手的叙事信息。'
      }]
    })
  });

  const data = await response.json();
  const text = data.content[0].text;

  // 解析输出
  const name = text.match(/名字:\s*(.+)/)?.[1] || '未知对手';
  const personality = text.match(/性格:\s*(.+)/)?.[1] || '均衡';
  const backstory = text.match(/故事:\s*(.+)/)?.[1] || '一个神秘的竞技者。';

  return { name, personality, backstory };
}
```

---

## 后续扩展方向

- **对手记忆系统**：同一个对手可以被多次召唤，胜率影响其「名声值」
- **剧情事件**：某些对手携带特殊剧情flag，击败后解锁支线故事
- **PVP 模式**：真实玩家对真实玩家，用对接匹配
- **观战系统**：围观他人对战，下注预测
