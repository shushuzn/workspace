# Cross-Project Identity System — 设计文档

## 概述

在 `agent-arena`、`ai-roundtable` 两个项目之间建立轻量级的"叙事身份共享"机制。玩家在 `agent-arena` 中创建的 Agent，可以作为"跨世界身份"出现在圆桌讨论中，提供统一的叙事体验。

**star-forge-web 联动（Phase 3）**：已从本版本移除，需要单独设计。核心障碍是 `agent-arena` 和 `star-forge-web` 的 localStorage 完全隔离，无法跨项目传递事件。详见"Phase 3 待研究问题"章节。

**核心原则：**
- 两个项目的数据模型完全独立，不做强制统一
- 只共享 Agent 的**叙事属性**（名字、背景故事、稀有度）
- 跨场景的影响力通过"身份层"（identity layer）传递
- 实现成本低，不破坏现有项目结构

---

## 身份层数据模型

### 存储位置

```
localStorage key: "starforge_identities"
```

### 数据结构

```typescript
interface CrossProjectIdentity {
  id: string;                    // 来自 agent-arena 的 Agent ID（格式：agent_xxx）
  name: string;                  // Agent 名字，如"噬光者"
  backstory: string;              // Agent 背景故事（AI 生成的那段叙事）
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary' | 'mythic';
  avatar: string;                // 头像标识符

  // 跨场景影响力计数
  arenaWins: number;            // 在竞技场获胜次数（仅 agent-arena 写入）
  roundtableUses: number;       // 在圆桌被选为发言者次数

  // 元数据
  createdAt: number;              // 创建时间戳
  lastUsed: number;              // 最后一次使用时间戳
}

interface IdentityState {
  identities: CrossProjectIdentity[];
}
```

### 身份同步规则

| 事件 | 触发时机 | 更新内容 |
|------|---------|---------|
| `arena_match_end` | 竞技场对战结算后 | `arenaWins++`（如胜利） |
| `roundtable_session_end` | 圆桌讨论结束后 | `roundtableUses++`（使用的身份） |

---

## 各场景集成

### 1. agent-arena（身份来源）

**改动范围：** 仅添加身份同步逻辑，不改动现有数据结构。

```javascript
// 伪代码示例
function onArenaMatchEnd(result, agent) {
  // 原有逻辑：更新 agent 状态、经验等

  // 新增：同步到身份层
  const identity = getOrCreateIdentity(agent);
  if (result === 'win') {
    identity.arenaWins++;
  }
  saveIdentity(identity);
}
```

**身份何时创建：** 当玩家在 agent-arena 中**首次创建 Agent** 时，同步创建一条 identity 记录。

**Agent 详情页新增入口：** 可以在 Arena 的 Agent 详情页查看"跨世界身份"状态（显示圆桌使用次数、赛季奖励解锁情况）。

---

### 2. ai-roundtable（身份消费）

**改动范围：** 新增身份选择界面，不改动讨论逻辑核心。

**身份选择 UI（讨论开始前）：**

```
┌─────────────────────────────────────┐
│  选择你的发言身份                     │
│  ─────────────────────────────────  │
│                                     │
│  ○ 噬光者  [epic]  圆桌使用: 7次   │
│    "曾以一己之力摧毁了第7区..."      │
│                                     │
│  ○ 影舞者  [rare]   圆桌使用: 3次   │
│    "穿梭于暗网的冷面杀手..."         │
│                                     │
│  ○ 新身份（无跨世界身份）           │
│                                     │
│        [ 开始讨论 ]                  │
└─────────────────────────────────────┘
```

**身份对圆桌的影响：**

| 身份稀有度 | 发言温度 | 解锁特殊发言词缀 |
|-----------|---------|----------------|
| common/uncommon | 0.8（偏保守） | 无 |
| rare | 1.0（标准） | 稀有感措辞 |
| epic | 1.2（更自信） | 史诗级措辞 |
| legendary/mythic | 1.5（激进） | 传说级措辞 + 特殊开场白 |

> 稀有度影响的是发言风格参数（temperature），不影响讨论内容本身。内容仍然由 AI 正常生成。

**无身份模式：** 如果玩家没有创建过 Agent，或者不想使用身份，选择"新身份"模式，即用预设的 6 种人格直接讨论（现有逻辑不变）。

---

## 身份生命周期管理

### Agent 删除场景

当 `agent-arena` 中某个 Agent 被删除时，身份层采用**软删除 + 保留叙事**策略：

```typescript
// identityStore.js 新增方法
function retireIdentity(agentId: string) {
  const state = loadIdentityState();
  const identity = state.identities.find(i => i.id === agentId);

  if (!identity) return;

  // 软删除：不移除，标记状态
  identity.status = 'retired';        // 'active' | 'retired'
  identity.retiredAt = Date.now();

  // arenaWins 保留——这些成就是真实发生的
  // roundtableUses 保留——圆桌里的发言记录依然有效

  saveIdentityState(state);
}
```

**读取规则：**
- `getActiveIdentities()` 只返回 `status !== 'retired'` 的身份
- 圆桌选择列表**不显示**已退役身份（避免困惑）

### 空状态处理

| 场景 | 无身份时的处理 |
|------|-------------|
| ai-roundtable | 显示"新身份（无跨世界身份）"选项，走现有 6 人格逻辑 |
| agent-arena 详情页 | 如关联 identity 已退役，显示"该身份已退役，竞技记录保留" |

---

## Phase 3 待研究问题

star-forge-web 联动因架构原因暂不纳入本版本：

1. **跨项目 localStorage 隔离**：`agent-arena` 和 `star-forge-web` 各有独立的 localStorage 命名空间，`arenaMatchEnd` 事件无法传递到 star-forge 的奖励系统

2. **赛季奖励 reducer 不兼容**：`SeasonContext.jsx` 的 `CLAIM_REWARD` reducer 按章节进度解锁，不支持按 `arenaWins` 计数解锁的奖励类型

3. **`arenaWins` 是 lifetime 而非赛季内计数**：如果要在赛季奖励中使用，需要在 `identityStore` 中记录每个赛季的胜场快照

**可行的简化方案**（未来探索）：
- 用 shared storage（同一域名下的 localStorage 或 postMessage API）实现跨项目事件通知
- 或者 star-forge 的身份奖励只在赛季结算时检查一次（不再实时联动）

---

## 文件改动范围

### 新增文件

```
src/shared/
  identityStore.js      # 身份层 localStorage 读写封装
```

### agent-arena 改动

```
src/game/gameStore.js          # 新增：onArenaMatchEnd 钩子，同步身份层
src/components/AgentCard.jsx  # 新增：跨世界身份状态徽章
```

### ai-roundtable 改动

```
index.js                        # 新增：讨论前身份选择流程
```

---

## 优先级

1. **Phase 1（身份层基础）：** `identityStore.js` + agent-arena 对战结算同步
2. **Phase 2（圆桌身份消费）：** ai-roundtable 身份选择 UI + 稀有度发言风格

---

## 后续扩展方向

- **身份成长叙事：** 当某个身份的 `arenaWins` 或 `roundtableUses` 达到特定阈值时，解锁更长的背景故事（由 AI 生成）
- **PVP 身份展示：** 在 agent-arena 的对手遇到拥有特殊身份的玩家时，对手 AI 会提及玩家的名声
- **star-forge 联动：** 见"Phase 3 待研究问题"
