# Agent Arena — AI 对手系统实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 AI 驱动的竞技场对手生成机制，每次挑战生成有叙事感的独特对手。

**Architecture:** 独立 `arenaStore` 管理竞技场状态和历史记录；`aiOpponentService.js` 调用 MiniMax API 生成叙事；6 阶段状态机驱动 UI 流程；与 `gameStore` 解耦，通过 `addCoins`/`updateAgent` 交互。

**Tech Stack:** Svelte 5 stores + MiniMax API + localStorage

---

## 文件结构

```
src/stores/
  arenaStore.js           # 竞技场状态（writable store，管辖 arena_history）

src/services/
  aiOpponentService.js   # AI 对手叙事生成

src/components/
  ArenaPanel.svelte      # 竞技场主面板（状态机）
  OpponentReveal.svelte  # 对手亮相动画
  BattleResult.svelte    # 战斗结果展示
  ArenaHistory.svelte     # 历史记录面板

src/
  App.svelte             # 添加竞技场 tab 入口
  Home.svelte            # 首页添加竞技场快捷入口
```

---

## Task 1: arenaStore.js

**Files:**
- Create: `80-PROJECTS/agent-arena/src/stores/arenaStore.js`

- [ ] **Step 1: 写 store 实现**

```javascript
import { writable, get } from 'svelte/store';

const ARENA_HISTORY_KEY = 'arena_history';
const MAX_HISTORY = 20;

function loadHistory() {
  try {
    const raw = localStorage.getItem(ARENA_HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveHistory(history) {
  try {
    localStorage.setItem(ARENA_HISTORY_KEY, JSON.stringify(history));
  } catch (e) {
    console.warn('Failed to save arena history:', e);
  }
}

function createArenaStore() {
  const { subscribe, set, update } = writable({
    stage: 'STAGE_SELECT',  // 'STAGE_SELECT' | 'STAGE_LOADING' | 'STAGE_REVEAL' | 'STAGE_BATTLE' | 'STAGE_RESULT' | 'STAGE_HISTORY'
    currentOpponent: null,
    selectedArenaAgentId: null,
    history: loadHistory(),
  });

  return {
    subscribe,

    // 设置当前阶段
    setStage: (stage) => update(s => ({ ...s, stage })),

    // 设置出战 Agent
    setSelectedAgent: (id) => update(s => ({ ...s, selectedArenaAgentId: id })),

    // 设置当前对手
    setCurrentOpponent: (opponent) => update(s => ({ ...s, currentOpponent: opponent })),

    // 推进到下一阶段
    nextStage: () => {
      const stages = ['STAGE_SELECT', 'STAGE_LOADING', 'STAGE_REVEAL', 'STAGE_BATTLE', 'STAGE_RESULT'];
      update(s => {
        const idx = stages.indexOf(s.stage);
        return { ...s, stage: stages[Math.min(idx + 1, stages.length - 1)] };
      });
    },

    // 记录对手到历史
    addToHistory: (opponent) => {
      update(s => {
        const newHistory = [opponent, ...s.history].slice(0, MAX_HISTORY);
        saveHistory(newHistory);
        return { ...s, history: newHistory };
      });
    },

    // 加载历史记录
    loadHistory: () => {
      const history = loadHistory();
      update(s => ({ ...s, history }));
    },

    // 重置到初始状态
    reset: () => update(s => ({
      ...s,
      stage: 'STAGE_SELECT',
      currentOpponent: null,
      selectedArenaAgentId: null,
    )),

    getState: () => get({ subscribe }),
  };
}

export const arenaStore = createArenaStore();
```

- [ ] **Step 2: 提交**

```bash
git add src/stores/arenaStore.js
git commit -m "feat(arena): add arenaStore with stage machine and history persistence"
```

---

## Task 2: aiOpponentService.js

**Files:**
- Create: `80-PROJECTS/agent-arena/src/services/aiOpponentService.js`
- Note: API key 从 `import.meta.env.VITE_MINIMAX_API_KEY` 读取（项目根目录 `.env` 文件）

- [ ] **Step 1: 写 AI 服务**

```javascript
const API_URL = 'https://api.minimaxi.com/v1/chat/completions';

const SYSTEM_PROMPT = `你是一个游戏叙事设计师。请为玩家的竞技场对手生成简短信息。

格式（严格按此格式返回，每行一个字段）：
名字: [角色名]
性格: [从列表选择：鲁莽/狡猾/坚韧/均衡/狂暴/冷静]
故事: [1-2句背景故事，要有趣]

要求：
- 名字要有科幻/赛博朋克风格，2-4个字
- 性格标签从给定列表中选一个
- 故事内容要有趣味性，可以提及过去的战绩、名声或特点
- 不要编造具体的战力数值`;

export async function generateOpponentNarrative() {
  const apiKey = import.meta.env.VITE_MINIMAX_API_KEY;

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
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

    const name = text.match(/名字:\s*(.+)/)?.[1]?.trim() || '';
    const personality = text.match(/性格:\s*(.+)/)?.[1]?.trim() || '';
    const backstory = text.match(/故事:\s*(.+)/)?.[1]?.trim() || '';

    if (!name || !personality) throw new Error('Invalid AI response format');

    return { name, personality, backstory };
  } catch (err) {
    console.warn('AI opponent generation failed, using fallback:', err);
    return {
      name: '暗影猎手',
      personality: '均衡',
      backstory: '一个穿梭于暗网的神秘竞技者，据说曾在暗网深处击败过无数对手。'
    };
  }
}
```

- [ ] **Step 2: 提交**

```bash
git add src/services/aiOpponentService.js
git commit -m "feat(arena): add aiOpponentService with MiniMax API and fallback"
```

---

## Task 3: OpponentReveal.svelte

**Files:**
- Create: `80-PROJECTS/agent-arena/src/components/OpponentReveal.svelte`

- [ ] **Step 1: 写组件**

```svelte
<script>
  export let opponent;

  // 性格标签颜色映射
  const personalityColors = {
    '鲁莽': '#ef4444',
    '狡猾': '#a855f7',
    '坚韧': '#10b981',
    '均衡': '#6b7280',
    '狂暴': '#dc2626',
    '冷静': '#3b82f6',
  };

  $: personalityColor = personalityColors[opponent.personality] || '#6b7280';
  $: rarityColor = {
    common: '#9ca3af',
    uncommon: '#10b981',
    rare: '#3b82f6',
    epic: '#a855f7',
  }[opponent.rarity] || '#9ca3af';

  // 用于进度条显示，标准化到 0-100
  const MAX_STAT = 100;
  $: getBarWidth = (stat) => Math.min(stat, MAX_STAT);
</script>

<div class="reveal-container">
  <!-- 头像 -->
  <div class="avatar-section">
    <div class="avatar-frame" style="border-color: {rarityColor}">
      <span class="avatar-emoji">{opponent.avatar}</span>
    </div>
    <div class="rarity-badge" style="background: {rarityColor}20; color: {rarityColor}">
      {opponent.rarity.toUpperCase()}
    </div>
  </div>

  <!-- 名字 -->
  <h2 class="opponent-name">{opponent.name}</h2>

  <!-- 性格标签 -->
  <div class="personality-chip" style="background: {personalityColor}20; border-color: {personalityColor}">
    {opponent.personality}
  </div>

  <!-- 背景故事 -->
  <p class="backstory">{opponent.backstory}</p>

  <!-- 属性条 -->
  <div class="stats-section">
    <div class="stat-bar">
      <span class="stat-label">🧠 智力</span>
      <div class="bar-bg">
        <div class="bar-fill" style="width: {getBarWidth(opponent.stats.intelligence)}%"></div>
      </div>
      <span class="stat-value">{opponent.stats.intelligence}</span>
    </div>
    <div class="stat-bar">
      <span class="stat-label">⚡ 速度</span>
      <div class="bar-bg">
        <div class="bar-fill" style="width: {getBarWidth(opponent.stats.speed)}%"></div>
      </div>
      <span class="stat-value">{opponent.stats.speed}</span>
    </div>
    <div class="stat-bar">
      <span class="stat-label">💡 创造力</span>
      <div class="bar-bg">
        <div class="bar-fill" style="width: {getBarWidth(opponent.stats.creativity)}%"></div>
      </div>
      <span class="stat-value">{opponent.stats.creativity}</span>
    </div>
    <div class="stat-bar">
      <span class="stat-label">💪 耐力</span>
      <div class="bar-bg">
        <div class="bar-fill" style="width: {getBarWidth(opponent.stats.endurance)}%"></div>
      </div>
      <span class="stat-value">{opponent.stats.endurance}</span>
    </div>
  </div>

  <!-- 战力 -->
  <div class="power-display">
    <span class="power-label">战力</span>
    <span class="power-value" style="color: {rarityColor}">{opponent.power}</span>
  </div>
</div>

<style>
  .reveal-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.5rem;
    gap: 1rem;
  }

  .avatar-section {
    position: relative;
    margin-bottom: 0.5rem;
  }

  .avatar-frame {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    border: 4px solid;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255,255,255,0.05);
  }

  .avatar-emoji {
    font-size: 3rem;
  }

  .rarity-badge {
    position: absolute;
    bottom: -4px;
    left: 50%;
    transform: translateX(-50%);
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.05em;
  }

  .opponent-name {
    font-size: 1.75rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .personality-chip {
    padding: 4px 14px;
    border-radius: 20px;
    border: 1.5px solid;
    font-size: 0.8rem;
    font-weight: 600;
  }

  .backstory {
    text-align: center;
    color: #a0a0a0;
    font-size: 0.9rem;
    line-height: 1.5;
    max-width: 280px;
    padding: 0.5rem;
  }

  .stats-section {
    width: 100%;
    max-width: 300px;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }

  .stat-bar {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .stat-label {
    font-size: 0.75rem;
    width: 70px;
    flex-shrink: 0;
  }

  .bar-bg {
    flex: 1;
    height: 6px;
    background: rgba(255,255,255,0.1);
    border-radius: 3px;
    overflow: hidden;
  }

  .bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea, #764ba2);
    border-radius: 3px;
    transition: width 0.5s ease;
  }

  .stat-value {
    font-size: 0.75rem;
    width: 30px;
    text-align: right;
    color: #a0a0a0;
  }

  .power-display {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.5rem;
    padding: 0.5rem 1.5rem;
    background: rgba(255,255,255,0.05);
    border-radius: 20px;
  }

  .power-label {
    font-size: 0.85rem;
    color: #a0a0a0;
  }

  .power-value {
    font-size: 1.25rem;
    font-weight: 800;
  }
</style>
```

- [ ] **Step 2: 提交**

```bash
git add src/components/OpponentReveal.svelte
git commit -m "feat(arena): add OpponentReveal component with personality/stats display"
```

---

## Task 4: BattleResult.svelte

**Files:**
- Create: `80-PROJECTS/agent-arena/src/components/BattleResult.svelte`

- [ ] **Step 1: 写组件**

```svelte
<script>
  import { arenaStore } from '../stores/arenaStore.js';
  import { gameStore } from '../stores/gameStore.js';

  export let opponent;
  export let result;  // 'win' | 'lose'
  export let rewards; // { xp, currency }
  export let playerAgentId;
  export let onPlayAgain;
  export let onBack;

  function handlePlayAgain() {
    arenaStore.reset();
    onPlayAgain?.();
  }

  function handleBack() {
    arenaStore.reset();
    onBack?.();
  }

  $: resultText = result === 'win' ? '胜利！' : '失败';
  $: resultEmoji = result === 'win' ? '🏆' : '💀';
  $: resultColor = result === 'win' ? '#10b981' : '#ef4444';
</script>

<div class="result-container">
  <div class="result-header">
    <span class="result-emoji">{resultEmoji}</span>
    <h2 class="result-title" style="color: {resultColor}">{resultText}</h2>
  </div>

  <div class="opponent-summary">
    <span class="avatar">{opponent.avatar}</span>
    <span class="name">{opponent.name}</span>
    <span class="personality">{opponent.personality}</span>
  </div>

  <!-- 奖励 -->
  <div class="rewards-section">
    <h3>获得奖励</h3>
    <div class="reward-row">
      <span class="reward-icon">✨</span>
      <span class="reward-label">经验</span>
      <span class="reward-value">+{rewards.xp}</span>
    </div>
    <div class="reward-row">
      <span class="reward-icon">🪙</span>
      <span class="reward-label">星尘币</span>
      <span class="reward-value">+{rewards.currency}</span>
    </div>
  </div>

  <!-- 按钮 -->
  <div class="action-buttons">
    <button class="btn btn-primary" on:click={handlePlayAgain}>
      再来一局
    </button>
    <button class="btn btn-secondary" on:click={handleBack}>
      返回
    </button>
  </div>
</div>

<style>
  .result-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
    gap: 1.5rem;
  }

  .result-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }

  .result-emoji {
    font-size: 4rem;
  }

  .result-title {
    font-size: 2rem;
    font-weight: 800;
  }

  .opponent-summary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.25rem;
    background: rgba(255,255,255,0.05);
    border-radius: 20px;
  }

  .avatar {
    font-size: 1.5rem;
  }

  .name {
    font-weight: 600;
  }

  .personality {
    font-size: 0.8rem;
    color: #a0a0a0;
    padding: 2px 8px;
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
  }

  .rewards-section {
    width: 100%;
    max-width: 280px;
    background: rgba(255,255,255,0.05);
    border-radius: 1rem;
    padding: 1rem;
  }

  .rewards-section h3 {
    font-size: 0.85rem;
    color: #a0a0a0;
    margin-bottom: 0.75rem;
  }

  .reward-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0;
  }

  .reward-icon {
    font-size: 1.25rem;
  }

  .reward-label {
    flex: 1;
    font-size: 0.9rem;
  }

  .reward-value {
    font-weight: 700;
    color: #f0c040;
  }

  .action-buttons {
    display: flex;
    gap: 0.75rem;
    width: 100%;
    max-width: 280px;
  }

  .btn {
    flex: 1;
    padding: 0.75rem;
    border: none;
    border-radius: 0.5rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
  }

  .btn-secondary {
    background: rgba(255,255,255,0.1);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.2);
  }
</style>
```

- [ ] **Step 2: 提交**

```bash
git add src/components/BattleResult.svelte
git commit -m "feat(arena): add BattleResult component with rewards display"
```

---

## Task 5: ArenaHistory.svelte

**Files:**
- Create: `80-PROJECTS/agent-arena/src/components/ArenaHistory.svelte`

- [ ] **Step 1: 写组件**

```svelte
<script>
  import { arenaStore } from '../stores/arenaStore.js';

  $: history = $arenaStore.history;

  function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  function getResultColor(result) {
    return result === 'win' ? '#10b981' : '#ef4444';
  }
</script>

<div class="history-container">
  <h2 class="history-title">⚔️ 对战记录</h2>

  {#if history.length === 0}
    <div class="empty-state">
      <p>暂无对战记录</p>
      <p class="hint">去挑战竞技场吧！</p>
    </div>
  {:else}
    <div class="history-list">
      {#each history as record (record.id)}
        <div class="history-item">
          <div class="item-left">
            <span class="avatar">{record.avatar}</span>
            <div class="info">
              <span class="name">{record.name}</span>
              <span class="personality">{record.personality}</span>
            </div>
          </div>
          <div class="item-right">
            <div
              class="result-badge"
              style="background: {getResultColor(record.result)}20; color: {getResultColor(record.result)}"
            >
              {record.result === 'win' ? '胜' : '负'}
            </div>
            <div class="rewards-mini">
              <span>+{record.rewards.xp} XP</span>
              <span>+{record.rewards.currency} 🪙</span>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .history-container {
    padding: 1rem;
  }

  .history-title {
    font-size: 1.1rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
  }

  .empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #6b7280;
  }

  .hint {
    font-size: 0.85rem;
    margin-top: 0.5rem;
  }

  .history-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .history-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem;
    background: rgba(255,255,255,0.04);
    border-radius: 0.75rem;
    border: 1px solid rgba(255,255,255,0.06);
  }

  .item-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .avatar {
    font-size: 1.75rem;
  }

  .info {
    display: flex;
    flex-direction: column;
  }

  .name {
    font-weight: 600;
    font-size: 0.9rem;
  }

  .personality {
    font-size: 0.75rem;
    color: #6b7280;
  }

  .item-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.25rem;
  }

  .result-badge {
    padding: 2px 10px;
    border-radius: 10px;
    font-size: 0.75rem;
    font-weight: 700;
  }

  .rewards-mini {
    display: flex;
    gap: 0.5rem;
    font-size: 0.7rem;
    color: #a0a0a0;
  }
</style>
```

- [ ] **Step 2: 提交**

```bash
git add src/components/ArenaHistory.svelte
git commit -m "feat(arena): add ArenaHistory component for viewing past opponents"
```

---

## Task 6: ArenaPanel.svelte（核心状态机）

**Files:**
- Create: `80-PROJECTS/agent-arena/src/components/ArenaPanel.svelte`

- [ ] **Step 1: 写 ArenaPanel — STAGE_SELECT**

```svelte
<script>
  import { arenaStore } from '../stores/arenaStore.js';
  import { gameStore } from '../stores/gameStore.js';
  import OpponentReveal from './OpponentReveal.svelte';
  import BattleResult from './BattleResult.svelte';
  import ArenaHistory from './ArenaHistory.svelte';
  import { generateOpponentNarrative } from '../services/aiOpponentService.js';
  import { AVATARS, RARITIES } from '../game/constants.js';
  import { calculatePower } from '../game/agentFactory.js';

  // 难度区间配置
  // avgPower >= 3000 时取 epic
  const DIFFICULTY_TIERS = [
    { maxPower: 500, difficulty: 0.8, rarity: 'common' },
    { maxPower: 1500, difficulty: 1.0, rarity: 'uncommon' },
    { maxPower: 3000, difficulty: 1.1, rarity: 'rare' },
    { maxPower: Infinity, difficulty: 1.2, rarity: 'epic' },
  ];

  // 性格属性修正表
  const PERSONALITY_MODIFIERS = {
    '鲁莽':   { speed: 1.3, intelligence: 0.9 },
    '狡猾':   { intelligence: 1.25, endurance: 0.9 },
    '坚韧':   { endurance: 1.3, creativity: 0.9 },
    '均衡':   {},
    '狂暴':   { intelligence: 1.15, speed: 1.15, creativity: 1.15, endurance: 0.8 },
    '冷静':   { intelligence: 1.15, speed: 0.9 },
  };

  let isGenerating = false;

  // 战斗结算
  function resolveBattle(playerPower, opponentPower) {
    const roll = 1 + (Math.random() * 0.30 - 0.15); // 0.85 ~ 1.15
    const adjustedPlayerPower = playerPower * roll;
    return adjustedPlayerPower >= opponentPower * 0.9 ? 'win' : 'lose';
  }

  // 生成对手
  async function generateOpponent() {
    arenaStore.setStage('STAGE_LOADING');
    isGenerating = true;

    try {
      // 1. 计算平均战力 + 难度
      const state = gameStore.getState();
      const agents = state.agents;
      if (!agents.length) return;

      const avgPower = agents.reduce((sum, a) => sum + calculatePower(a.stats), 0) / agents.length;

      const tier = DIFFICULTY_TIERS.find(t => avgPower < t.maxPower);
      const difficulty = tier.difficulty;
      const rarity = tier.rarity;
      const basePower = Math.floor(avgPower * difficulty * (0.95 + Math.random() * 0.10));

      // 2. AI 生成叙事
      const narrative = await generateOpponentNarrative();

      // 3. 构建属性（先有基础值，再应用性格修正，最后缩放到 basePower 附近）
      const rarityMult = RARITIES[rarity.toUpperCase()]?.multiplier || 1;
      const baseStats = {
        intelligence: Math.floor((20 + Math.random() * 15) * rarityMult),
        speed: Math.floor((20 + Math.random() * 15) * rarityMult),
        creativity: Math.floor((20 + Math.random() * 15) * rarityMult),
        endurance: Math.floor((20 + Math.random() * 15) * rarityMult),
      };

      const modifiers = PERSONALITY_MODIFIERS[narrative.personality] || {};
      const stats = { ...baseStats };
      for (const [stat, mod] of Object.entries(modifiers)) {
        stats[stat] = Math.floor(stats[stat] * mod);
      }

      // 等比缩放到 basePower
      const currentPower = calculatePower(stats);
      const scale = basePower / currentPower;
      for (const stat of ['intelligence', 'speed', 'creativity', 'endurance']) {
        stats[stat] = Math.floor(stats[stat] * scale);
      }

      const opponent = {
        id: 'opp_' + Date.now(),
        name: narrative.name,
        backstory: narrative.backstory,
        personality: narrative.personality,
        rarity,
        stats,
        power: basePower,
        avatar: AVATARS[Math.floor(Math.random() * AVATARS.length)],
        difficulty,
        result: null,
        rewards: null,
        createdAt: Date.now(),
      };

      arenaStore.setCurrentOpponent(opponent);
      arenaStore.setStage('STAGE_REVEAL');
    } finally {
      isGenerating = false;
    }
  }

  // 开始战斗
  function startBattle() {
    arenaStore.setStage('STAGE_BATTLE');

    const state = gameStore.getState();
    const arenaState = arenaStore.getState();
    const playerAgent = state.agents.find(a => a.id === arenaState.selectedArenaAgentId) || state.agents[0];
    const opponent = arenaState.currentOpponent;

    const playerPower = calculatePower(playerAgent.stats);
    const result = resolveBattle(playerPower, opponent.power);

    const rewards = {
      xp: result === 'win' ? Math.floor(50 * opponent.difficulty) : 10,
      currency: result === 'win' ? Math.floor(20 * opponent.difficulty) : 5,
    };

    // 更新对手结果
    const finalOpponent = { ...opponent, result, rewards };

    // 发放奖励
    gameStore.addCoins(rewards.currency);
    // 注意：addAgentXP 如不存在，见 Task 7
    const gameState = gameStore.getState();
    if (gameState.addAgentXP) {
      gameState.addAgentXP(playerAgent.id, rewards.xp);
    }

    // 记录到历史
    arenaStore.addToHistory(finalOpponent);

    // 动画 3 秒后显示结果
    setTimeout(() => {
      arenaStore.setCurrentOpponent(finalOpponent);
      arenaStore.setStage('STAGE_RESULT');
    }, 3000);
  }

  function selectAgent(id) {
    arenaStore.setSelectedAgent(id);
  }

  function handleBack() {
    arenaStore.reset();
  }

  $: arenaState = $arenaStore;
  $: gameState = $gameStore;
  $: stage = arenaState.stage;
  $: opponent = arenaState.currentOpponent;

  // 默认选中第一个 agent
  $: if (gameState.agents.length && !arenaState.selectedArenaAgentId) {
    arenaStore.setSelectedAgent(gameState.agents[0].id);
  }
</script>

<div class="arena-panel">
  {#if stage === 'STAGE_SELECT'}
    <div class="stage-select">
      <h2 class="panel-title">⚔️ 竞技场挑战</h2>
      <p class="select-hint">选择出战机甲</p>

      <div class="agent-picker">
        {#each gameState.agents as agent}
          <button
            class="agent-option"
            class:selected={agent.id === arenaState.selectedArenaAgentId}
            on:click={() => selectAgent(agent.id)}
          >
            <span class="agent-avatar">{agent.avatar}</span>
            <div class="agent-info">
              <span class="agent-name">{agent.name}</span>
              <span class="agent-power">⚡ {calculatePower(agent.stats)}</span>
            </div>
            {#if agent.id === arenaState.selectedArenaAgentId}
              <span class="check">✓</span>
            {/if}
          </button>
        {/each}
      </div>

      <button class="btn-challenge" on:click={generateOpponent} disabled={isGenerating}>
        {isGenerating ? '正在召唤...' : '开始挑战'}
      </button>
    </div>

  {:else if stage === 'STAGE_LOADING'}
    <div class="stage-loading">
      <div class="loading-animation">
        <span class="loading-icon">⚔️</span>
        <div class="loading-ring"></div>
      </div>
      <p class="loading-text">正在召唤对手...</p>
      <p class="loading-subtext">AI 正在生成独特对手</p>
    </div>

  {:else if stage === 'STAGE_REVEAL'}
    <div class="stage-reveal">
      <OpponentReveal {opponent} />

      <!-- 战力对比 -->
      {@const playerAgent = gameState.agents.find(a => a.id === arenaState.selectedArenaAgentId) || gameState.agents[0]}
      {@const playerPower = calculatePower(playerAgent?.stats || {})}
      <div class="power-compare">
        <div class="power-player">
          <span class="power-label">你的战力</span>
          <span class="power-num">{playerPower}</span>
        </div>
        <span class="vs">VS</span>
        <div class="power-opponent">
          <span class="power-label">对手战力</span>
          <span class="power-num">{opponent.power}</span>
        </div>
      </div>

      <button class="btn-challenge" on:click={startBattle}>
        开始战斗
      </button>
    </div>

  {:else if stage === 'STAGE_BATTLE'}
    <div class="stage-battle">
      <div class="battle-animation">
        <span class="battle-icon">{playerAgent?.avatar || '🤖'}</span>
        <div class="battle-vs">⚔️</div>
        <span class="battle-icon">{opponent.avatar}</span>
      </div>
      <p class="battle-text">战斗进行中...</p>
    </div>

  {:else if stage === 'STAGE_RESULT'}
    <BattleResult
      {opponent}
      result={opponent.result}
      rewards={opponent.rewards}
      playerAgentId={arenaState.selectedArenaAgentId}
      onPlayAgain={generateOpponent}
      onBack={handleBack}
    />

  {:else if stage === 'STAGE_HISTORY'}
    <ArenaHistory />
  {/if}

  <!-- 历史入口 -->
  <button class="history-btn" on:click={() => arenaStore.setStage('STAGE_HISTORY')}>
    📜 历史
  </button>
</div>

<style>
  .arena-panel {
    position: relative;
    min-height: 400px;
  }

  .panel-title {
    text-align: center;
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
  }

  /* STAGE_SELECT */
  .stage-select {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .select-hint {
    color: #6b7280;
    font-size: 0.9rem;
  }

  .agent-picker {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .agent-option {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: rgba(255,255,255,0.05);
    border: 2px solid transparent;
    border-radius: 0.75rem;
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
    color: #fff;
  }

  .agent-option.selected {
    border-color: #667eea;
    background: rgba(102,126,234,0.15);
  }

  .agent-avatar {
    font-size: 1.75rem;
  }

  .agent-info {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .agent-name {
    font-weight: 600;
    font-size: 0.9rem;
  }

  .agent-power {
    font-size: 0.8rem;
    color: #a0a0a0;
  }

  .check {
    color: #667eea;
    font-weight: 700;
  }

  .btn-challenge {
    width: 100%;
    max-width: 280px;
    padding: 0.85rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    border: none;
    border-radius: 0.75rem;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    margin-top: 0.5rem;
    transition: all 0.2s;
  }

  .btn-challenge:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102,126,234,0.4);
  }

  .btn-challenge:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  /* STAGE_LOADING */
  .stage-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 350px;
    gap: 1rem;
  }

  .loading-animation {
    position: relative;
    width: 80px;
    height: 80px;
  }

  .loading-icon {
    font-size: 3rem;
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: pulse 1s ease-in-out infinite;
  }

  .loading-ring {
    position: absolute;
    inset: 0;
    border: 3px solid rgba(102,126,234,0.3);
    border-top-color: #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
  }

  .loading-text {
    font-size: 1.1rem;
    font-weight: 600;
  }

  .loading-subtext {
    font-size: 0.85rem;
    color: #6b7280;
  }

  /* STAGE_REVEAL */
  .stage-reveal {
    padding: 0.5rem;
  }

  .power-compare {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    padding: 1rem;
    margin: 0.5rem 0;
  }

  .power-player, .power-opponent {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
  }

  .power-label {
    font-size: 0.75rem;
    color: #6b7280;
  }

  .power-num {
    font-size: 1.5rem;
    font-weight: 800;
  }

  .vs {
    font-size: 1rem;
    font-weight: 700;
    color: #6b7280;
  }

  /* STAGE_BATTLE */
  .stage-battle {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 350px;
    gap: 1.5rem;
  }

  .battle-animation {
    display: flex;
    align-items: center;
    gap: 2rem;
  }

  .battle-icon {
    font-size: 4rem;
    animation: bounce 0.5s ease-in-out infinite alternate;
  }

  .battle-vs {
    font-size: 2.5rem;
    animation: flash 0.3s ease-in-out infinite alternate;
  }

  @keyframes bounce {
    from { transform: translateY(0); }
    to { transform: translateY(-10px); }
  }

  @keyframes flash {
    from { opacity: 0.5; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1.1); }
  }

  .battle-text {
    font-size: 1.1rem;
    color: #a0a0a0;
    animation: blink 1s ease-in-out infinite;
  }

  @keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  /* History button */
  .history-btn {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    padding: 4px 10px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px;
    color: #a0a0a0;
    font-size: 0.75rem;
    cursor: pointer;
  }
</style>
```

- [ ] **Step 2: 提交**

```bash
git add src/components/ArenaPanel.svelte
git commit -m "feat(arena): add ArenaPanel with full 6-stage state machine"
```

---

## Task 7: gameStore addAgentXP 方法

**Files:**
- Modify: `80-PROJECTS/agent-arena/src/stores/gameStore.js`

- [ ] **Step 1: 添加 addAgentXP 方法**

在 `gameStore` 的 return 对象中添加：

```javascript
// Add experience to an agent (returns true if leveled up)
addAgentXP: (agentId, amount) => {
  update(state => ({
    ...state,
    agents: state.agents.map(agent => {
      if (agent.id !== agentId) return agent;
      const newExp = (agent.experience || 0) + amount;
      const expNeeded = 100 * Math.pow(1.5, agent.level - 1);
      if (newExp >= expNeeded) {
        // Level up
        return {
          ...agent,
          level: agent.level + 1,
          experience: newExp - expNeeded,
          stats: {
            intelligence: agent.stats.intelligence + 2,
            speed: agent.stats.speed + 2,
            creativity: agent.stats.creativity + 2,
            endurance: agent.stats.endurance + 2,
          }
        };
      }
      return { ...agent, experience: newExp };
    })
  }));
},
```

- [ ] **Step 2: 提交**

```bash
git add src/stores/gameStore.js
git commit -m "feat(arena): add addAgentXP to gameStore for arena rewards"
```

---

## Task 8: App.svelte 集成

**Files:**
- Modify: `80-PROJECTS/agent-arena/src/App.svelte`

- [ ] **Step 1: 添加 ArenaPanel 导入和 arena tab**

在脚本部分添加：
```javascript
import ArenaPanel from './components/ArenaPanel.svelte';
```

在 tabs 数组中添加：
```javascript
{ id: 'arena', icon: '⚔️', label: '竞技场' }
```

在 currentTab === 'arena' 渲染：
```svelte
{:else if currentTab === 'arena'}
  <ArenaPanel />
```

- [ ] **Step 2: 提交**

```bash
git add src/App.svelte
git commit -m "feat(arena): add arena tab to App.svelte navigation"
```

---

## Task 9: Home.svelte 添加竞技场快捷入口

**Files:**
- Modify: `80-PROJECTS/agent-arena/src/components/Home.svelte`

- [ ] **Step 1: 在首页添加竞技场入口按钮**

在 Home.svelte 的 quick-stats 或单独区域添加：

```svelte
<button class="arena-quick-btn" on:click={() => gameStore.setTab('arena')}>
  ⚔️ 进入竞技场
</button>
```

- [ ] **Step 2: 提交**

```bash
git add src/components/Home.svelte
git commit -m "feat(arena): add arena quick-entry button to Home.svelte"
```

---

## Task 10: .env 配置说明

**Files:**
- Note: 无需创建文件，只添加说明

- [ ] **Step 1: 在项目 README 或 .env.example 中添加说明**

在 `80-PROJECTS/agent-arena/` 根目录创建或更新 `.env.example`：

```
# MiniMax API Key（用于 AI 对手叙事生成）
VITE_MINIMAX_API_KEY=your_api_key_here
```

```bash
git add .env.example
git commit -m "docs(arena): add .env.example with VITE_MINIMAX_API_KEY"
```

---

## 总结

| Task | 文件 | 描述 |
|------|------|------|
| 1 | arenaStore.js | 竞技场状态机 + history 持久化 |
| 2 | aiOpponentService.js | MiniMax API 调用 + fallback |
| 3 | OpponentReveal.svelte | 对手亮相动画 |
| 4 | BattleResult.svelte | 战斗结果展示 |
| 5 | ArenaHistory.svelte | 历史记录面板 |
| 6 | ArenaPanel.svelte | 核心状态机（选择/加载/亮相/战斗/结果/历史） |
| 7 | gameStore.js | 添加 addAgentXP 方法 |
| 8 | App.svelte | 导航添加 arena tab |
| 9 | Home.svelte | 首页添加竞技场快捷入口 |
| 10 | .env.example | API key 配置说明 |
