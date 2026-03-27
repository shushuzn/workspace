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

### Step 1: 计算基准战力 + 难度选择

1. 取玩家所有 Agent 的平均战力
2. 根据平均战力所在区间，自动确定难度系数：

| 平均战力区间 | 难度系数 | 对应稀有度 |
|------------|---------|-----------|
| 0 ~ 500    | 0.8     | common    |
| 500 ~ 1500 | 1.0     | uncommon  |
| 1500 ~ 3000| 1.1     | rare      |
| 3000+      | 1.2     | epic      |

基准战力 = 平均战力 × 难度系数 × (0.95 ~ 1.05 随机波动)

### Step 2: 性格标签

从预设列表中随机选择（AI 生成时也可自行选择）：

| 性格 | 属性修正 |
|------|---------|
| 鲁莽 | speed +30%, intelligence -10% |
| 狡猾 | intelligence +25%, endurance -10% |
| 坚韧 | endurance +30%, creativity -10% |
| 均衡 | 无修正 |
| 狂暴 | all.stats +15%, endurance -20% |
| 冷静 | intelligence +15%, speed -10% |

### Step 3: AI 生成叙事

调用 AI（MiniMax API）生成名字 + 背景故事 + 性格标签。

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
  name: string;           // AI 生成
  backstory: string;       // AI 生成
  personality: string;      // 性格标签
  rarity: string;          // 由难度区间决定（见 Step 1）
  stats: { intelligence, speed, creativity, endurance };
  power: number;           // 计算得出的战力
  avatar: string;          // 从 AVATARS 列表随机选取
  difficulty: number;       // 难度系数
  result: 'win' | 'lose' | null;
  rewards: { xp: number, currency: number };
  createdAt: number;
}
```

属性计算逻辑：
1. 根据 rarity 从 `agentFactory.calculateBaseStats(rarity)` 获取基础属性
2. 应用 personality 对应的属性修正（乘法）
3. 调整总战力到 Step 1 计算的基准战力附近（等比缩放）
4. avatar 用 `agentFactory.getRandomAvatar()` 随机选取

---

## 战斗结算算法

```
playerPower = 玩家出战机甲战力
opponentPower = 对手战力

// 胜负计算：加入 ±15% 随机波动
roll = 1 + (Math.random() * 0.30 - 0.15)  // 0.85 ~ 1.15
adjustedPlayerPower = playerPower * roll

if (adjustedPlayerPower >= opponentPower * 0.9) {
  result = 'win'   // 玩家战力超过对手90%即胜利
} else {
  result = 'lose'
}
```

> **为什么用 90% 阈值？** 略微偏向玩家，保证体验流畅，避免频繁失败挫败感。

---

## 竞技场流程

### UI 状态机

```
STAGE_SELECT   → 选择出战机甲（从玩家已有 Agent 中选，或用当前选中 Agent）
STAGE_LOADING  → AI 生成对手（加载动画）
STAGE_REVEAL   → 对手亮相（显示名字/故事/属性）
STAGE_BATTLE   → 战斗动画（3-5秒自动结算）
STAGE_RESULT   → 胜负 + 奖励展示
STAGE_HISTORY  → 历史对手记录（可从 STAGE_RESULT 或 Home 入口进入）
```

### 出战 Agent 选择

STAGE_SELECT 阶段：
- 如果玩家有多个 Agent，显示列表让玩家选择
- 如果只有一个 Agent，直接使用该 Agent，无需额外操作
- `selectedArenaAgentId` 保存在 `arenaStore` 中

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

**STAGE_BATTLE：**
- 双方头像对战动画（3-5秒）
- 战力数值动态变化效果

**STAGE_RESULT：**
- 胜负文案（动态生成）
- 获得奖励：经验（加给玩家的出战机甲）+ 星尘币
- 奖励到账：调用 `gameStore.addCoins()` 和 `gameStore.addAgentXP(agentId, xp)`
- 「再来一局」和「返回」按钮

**STAGE_HISTORY：**
- 显示最近 20 条 arena_history
- 每条显示：对手名字、性格、胜负结果、获得奖励、时间
- 点击可展开查看完整背景故事

---

## 奖励机制

| 结果 | 经验 | 星尘币 |
|------|------|-------|
| 胜利 | 50 * 难度系数 | 20 * 难度系数 |
| 失败 | 10 | 5 |

奖励到账后，更新 `gameStore` 中的玩家星尘币余额，以及出战机甲的经验值。

---

## 数据持久化

**Arena 历史记录**（独立 localStorage key）：

```
localStorage key: "arena_history"
格式: ArenaOpponent[]（最近20条，按 createdAt 倒序）
```

arenaStore 负责管理 arena_history 的读写，不混入 gameStore。

**arenaStore 状态结构：**

```javascript
{
  currentOpponent: ArenaOpponent | null,
  stage: 'STAGE_SELECT' | 'STAGE_LOADING' | 'STAGE_REVEAL' | 'STAGE_BATTLE' | 'STAGE_RESULT' | 'STAGE_HISTORY',
  selectedArenaAgentId: string | null,
  history: ArenaOpponent[],  // 从 arena_history 加载
}
```

---

## AI 服务实现

```javascript
// src/services/aiOpponentService.js
import { MINIMAX_API_KEY, MINIMAX_API_URL } from '../config';

const SYSTEM_PROMPT = `你是一个游戏叙事设计师...`; // 见上文

export async function generateOpponent(difficulty = 1.0) {
  try {
    const response = await fetch(MINIMAX_API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${MINIMAX_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'MiniMax-M2.7-highspeed',
        max_tokens: 200,
        messages: [{
          role: 'user',
          content: '生成一个竞技场对手的叙事信息。严格按格式返回：\n名字: [角色名]\n性格: [性格]\n故事: [故事]'
        }]
      })
    });

    if (!response.ok) throw new Error(`API error: ${response.status}`);

    const data = await response.json();
    const text = data.choices[0].message.content;

    // 解析输出
    const name = text.match(/名字:\s*(.+)/)?.[1]?.trim() || '暗影猎手';
    const personality = text.match(/性格:\s*(.+)/)?.[1]?.trim() || '均衡';
    const backstory = text.match(/故事:\s*(.+)/)?.[1]?.trim() || '一个穿梭于暗网的神秘竞技者。';

    return { name, personality, backstory };
  } catch (err) {
    // AI 生成失败时返回默认叙事
    console.warn('AI opponent generation failed, using fallback:', err);
    return {
      name: '暗影猎手',
      personality: '均衡',
      backstory: '一个来历不明的竞技者，据说曾在暗网深处击败过无数对手。'
    };
  }
}
```

> **注意**：`config.js` 中需添加 `MINIMAX_API_KEY` 和 `MINIMAX_API_URL`（现有 `agent-arena` 已配置 MiniMax，可复用）。

---

## 组件改动范围

### 新增文件（全部使用 .svelte）

```
src/components/
  ArenaPanel.svelte         # 竞技场主面板（状态机）
  OpponentReveal.svelte     # 对手亮相动画
  BattleResult.svelte       # 战斗结果展示
  ArenaHistory.svelte       # 历史记录面板

src/stores/
  arenaStore.js             # 竞技场状态（writable store，管辖 arena_history）
```

### 修改文件

```
src/App.svelte              # 添加 ArenaPanel 路由/入口（底部导航新增「竞技场」按钮）
src/components/Home.svelte   # 添加「竞技场」入口按钮
src/game/gameStore.js       # 添加 addCoins() 和 addAgentXP() 方法（如不存在）
src/config.js               # 添加 MINIMAX_API_KEY 和 MINIMAX_API_URL（如未配置）
```

---

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| AI API 超时/失败 | 使用 fallback 默认叙事，继续流程 |
| 玩家无 Agent | 提示「需要至少拥有1个 Agent 才能进入竞技场」 |
| localStorage 写入失败 | 静默失败，arena_history 最多丢1条记录 |
| 战斗动画中断（如标签页切换） | 动画完成前关闭 → 状态停留在 STAGE_BATTLE，重新进入时正常显示结果 |

---

## 后续扩展方向

- **对手记忆系统**：同一个对手可以被多次召唤，胜率影响其「名声值」
- **剧情事件**：某些对手携带特殊剧情flag，击败后解锁支线故事
- **PVP 模式**：真实玩家对真实玩家，用对接匹配
- **观战系统**：围观他人对战，下注预测
