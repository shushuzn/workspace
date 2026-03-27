<script>
  import { onMount } from 'svelte';
  import { arenaStore } from '../stores/arenaStore.js';
  import { gameStore, selectedAgent } from '../stores/gameStore.js';
  import { generateOpponentNarrative } from '../services/aiOpponentService.js';
  import { calculateBaseStats, getRandomAvatar } from '../game/agentFactory.js';
  import OpponentReveal from './OpponentReveal.svelte';
  import BattleResult from './BattleResult.svelte';
  import ArenaHistory from './ArenaHistory.svelte';

  // Timer for battle animation
  let battleAnimationTimer = null;

  // Reactive state from stores
  $: stage = $arenaStore.stage;
  $: opponent = $arenaStore.currentOpponent;
  $: playerAgent = $selectedAgent;

  /**
   * Calculate average power across all agents
   * Uses the same power formula as agentFactory.calculatePower
   */
  function getAveragePower() {
    const agents = $gameStore.agents;
    if (!agents || agents.length === 0) return 0;

    const powers = agents.map(a => {
      const { intelligence, speed, creativity, endurance } = a.stats;
      // Power formula matches agentFactory.calculatePower
      return Math.floor(
        (intelligence * 2 + speed * 1.5 + creativity * 1.8 + endurance * 1.2) *
        (1 + a.level * 0.1)
      );
    });
    return powers.reduce((sum, p) => sum + p, 0) / powers.length;
  }

  /**
   * Get difficulty tier based on average power
   * From spec:
   * - avgPower 0-500: difficulty 0.8 (common)
   * - avgPower 500-1500: difficulty 1.0 (uncommon)
   * - avgPower 1500-3000: difficulty 1.1 (rare)
   * - avgPower 3000+: difficulty 1.2 (epic)
   */
  function getDifficultyTier(avgPower) {
    if (avgPower < 500) return { difficulty: 0.8, rarity: 'common' };
    if (avgPower < 1500) return { difficulty: 1.0, rarity: 'uncommon' };
    if (avgPower < 3000) return { difficulty: 1.1, rarity: 'rare' };
    return { difficulty: 1.2, rarity: 'epic' };
  }

  /**
   * Calculate opponent power with slight random variation
   */
  function calculateOpponentPower(playerAvgPower, difficulty) {
    // Slight roll for variety: 0.95 ~ 1.05
    const roll = 0.95 + Math.random() * 0.10;
    return Math.floor(playerAvgPower * difficulty * roll);
  }

  /**
   * Start the battle - generates opponent and transitions to reveal stage
   */
  function startBattle() {
    arenaStore.setStage('STAGE_LOADING');

    const playerAvg = getAveragePower();
    const { difficulty, rarity } = getDifficultyTier(playerAvg);

    generateOpponentNarrative().then(narrative => {
      // Build opponent with stats from agentFactory methods
      const baseStats = calculateBaseStats(rarity);
      const avatar = getRandomAvatar();

      // Apply personality modifiers
      const personality = narrative.personality;
      const personalityModifiers = {
        '鲁莽': { speed: 1.3, intelligence: 0.9 },
        '狡猾': { intelligence: 1.25, endurance: 0.9 },
        '坚韧': { endurance: 1.3, creativity: 0.9 },
        '狂暴': { all: 1.15, endurance: 0.8 },
        '冷静': { intelligence: 1.15, speed: 0.9 },
        '均衡': {}
      };

      // Apply modifiers to stats BEFORE scaling
      const mod = personalityModifiers[personality] || personalityModifiers['均衡'];
      let stats = { ...baseStats };

      if (mod.all) {
        Object.keys(stats).forEach(k => stats[k] = Math.floor(stats[k] * mod.all));
      }
      if (mod.speed) stats.speed = Math.floor(stats.speed * mod.speed);
      if (mod.intelligence) stats.intelligence = Math.floor(stats.intelligence * mod.intelligence);
      if (mod.endurance) stats.endurance = Math.floor(stats.endurance * mod.endurance);
      if (mod.creativity) stats.creativity = Math.floor(stats.creativity * mod.creativity);

      // Scale stats to match target power
      const targetPower = calculateOpponentPower(playerAvg, difficulty);
      const currentPower = Math.floor(
        stats.intelligence * 2 + stats.speed * 1.5 + stats.creativity * 1.8 + stats.endurance * 1.2
      );
      const scale = targetPower / currentPower;
      Object.keys(stats).forEach(k => stats[k] = Math.floor(stats[k] * scale));

      const fullOpponent = {
        id: `opponent_${Date.now()}`,
        name: narrative.name,
        backstory: narrative.backstory,
        personality,
        rarity,
        stats,
        power: targetPower,
        avatar,
        difficulty,
        result: null,
        rewards: null,
        createdAt: Date.now()
      };

      arenaStore.setCurrentOpponent(fullOpponent);
      arenaStore.setStage('STAGE_REVEAL');
    });
  }

  /**
   * Begin the battle animation - auto-resolves after 3-5 seconds
   */
  function beginBattleAnimation() {
    arenaStore.setStage('STAGE_BATTLE');

    // 3-5 second battle animation
    const duration = 3000 + Math.random() * 2000;
    battleAnimationTimer = setTimeout(() => {
      resolveBattle();
    }, duration);
  }

  /**
   * Resolve the battle - calculate winner with ±15% roll
   * Battle algorithm: roll = 1 + (Math.random() * 0.30 - 0.15)
   * Win condition: adjustedPlayerPower >= opponentPower * 0.9
   */
  function resolveBattle() {
    const player = playerAgent;
    const opp = opponent;

    if (!player || !opp) {
      arenaStore.setStage('STAGE_RESULT');
      return;
    }

    // Calculate player power with level bonus
    const playerPower = Math.floor(
      (player.stats.intelligence * 2 + player.stats.speed * 1.5 +
       player.stats.creativity * 1.8 + player.stats.endurance * 1.2) *
      (1 + player.level * 0.1)
    );
    const opponentPower = opp.power;

    // Battle algorithm with ±15% roll
    const roll = 1 + (Math.random() * 0.30 - 0.15); // 0.85 ~ 1.15
    const adjustedPlayerPower = playerPower * roll;

    const result = adjustedPlayerPower >= opponentPower * 0.9 ? 'win' : 'lose';
    const rewards = result === 'win'
      ? { xp: Math.floor(50 * opp.difficulty), coins: Math.floor(20 * opp.difficulty) }
      : { xp: 10, coins: 5 };

    // Update opponent with result
    const updatedOpponent = { ...opp, result, rewards };
    arenaStore.setCurrentOpponent(updatedOpponent);
    arenaStore.addToHistory(updatedOpponent);
    arenaStore.setStage('STAGE_RESULT');
  }

  /**
   * Select an agent for arena battle
   */
  function selectAgentForArena(agentId) {
    arenaStore.setSelectedAgent(agentId);
    gameStore.selectAgent(agentId);
  }

  /**
   * Navigate to history view
   */
  function goToHistory() {
    arenaStore.setStage('STAGE_HISTORY');
  }

  // Cleanup timer on component destroy
  onMount(() => {
    return () => {
      if (battleAnimationTimer) {
        clearTimeout(battleAnimationTimer);
      }
    };
  });
</script>

<div class="arena-panel">
  {#if stage === 'STAGE_SELECT'}
    <div class="stage-select">
      <h2>选择出战Agent</h2>
      <p class="subtitle">选择一个Agent进行竞技场挑战</p>

      <div class="agent-list">
        {#each $gameStore.agents as agent (agent.id)}
          <div
            class="agent-card"
            class:selected={$arenaStore.selectedArenaAgentId === agent.id}
            on:click={() => selectAgentForArena(agent.id)}
            on:keypress={(e) => e.key === 'Enter' && selectAgentForArena(agent.id)}
            role="button"
            tabindex="0"
          >
            <span class="agent-avatar">{agent.avatar}</span>
            <div class="agent-info">
              <span class="agent-name">{agent.name}</span>
              <span class="agent-level">Lv.{agent.level}</span>
            </div>
          </div>
        {/each}
      </div>

      <div class="actions">
        <button class="btn-secondary" on:click={goToHistory}>历史记录</button>
        <button
          class="btn-primary"
          disabled={!$arenaStore.selectedArenaAgentId}
          on:click={startBattle}
        >
          开始挑战
        </button>
      </div>
    </div>

  {:else if stage === 'STAGE_LOADING'}
    <div class="stage-loading">
      <div class="loading-text">正在召唤对手...</div>
      <div class="loading-name">{opponent?.name || '???'}</div>
    </div>

  {:else if stage === 'STAGE_REVEAL'}
    <div class="stage-reveal">
      <OpponentReveal />
      <div class="reveal-actions">
        <button class="btn-primary" on:click={beginBattleAnimation}>开始战斗</button>
      </div>
    </div>

  {:else if stage === 'STAGE_BATTLE'}
    <div class="stage-battle">
      <div class="battle-animation">
        <span class="player-avatar">{playerAgent?.avatar || '🤖'}</span>
        <span class="vs">VS</span>
        <span class="opponent-avatar">{opponent?.avatar || '🤖'}</span>
      </div>
      <div class="battle-text">战斗进行中...</div>
    </div>

  {:else if stage === 'STAGE_RESULT'}
    <BattleResult result={opponent?.result || 'lose'} opponent={opponent} />

  {:else if stage === 'STAGE_HISTORY'}
    <ArenaHistory />
  {/if}
</div>

<style>
  .arena-panel {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  /* STAGE_SELECT */
  .stage-select {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    height: 100%;
  }

  .stage-select h2 {
    margin: 0;
    text-align: center;
  }

  .subtitle {
    text-align: center;
    color: #888;
    margin: 0;
    font-size: 0.875rem;
  }

  .agent-list {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .agent-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: #1a1a1a;
    border-radius: 8px;
    cursor: pointer;
    border: 2px solid transparent;
    transition: border-color 0.2s;
  }

  .agent-card:hover {
    border-color: #333;
  }

  .agent-card.selected {
    border-color: #4caf50;
  }

  .agent-avatar {
    font-size: 2rem;
  }

  .agent-info {
    display: flex;
    flex-direction: column;
  }

  .agent-name {
    font-weight: bold;
  }

  .agent-level {
    font-size: 0.75rem;
    color: #888;
  }

  .actions {
    display: flex;
    gap: 0.5rem;
    padding-top: 1rem;
  }

  .actions button {
    flex: 1;
  }

  /* STAGE_LOADING */
  .stage-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 1rem;
  }

  .loading-text {
    font-size: 1.25rem;
    color: #888;
  }

  .loading-name {
    font-size: 2rem;
    font-weight: bold;
    animation: pulse 1s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  /* STAGE_REVEAL */
  .stage-reveal {
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  .reveal-actions {
    padding: 1rem;
  }

  .reveal-actions button {
    width: 100%;
  }

  /* STAGE_BATTLE */
  .stage-battle {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 2rem;
  }

  .battle-animation {
    display: flex;
    align-items: center;
    gap: 2rem;
    font-size: 3rem;
  }

  .player-avatar,
  .opponent-avatar {
    animation: bounce 0.5s infinite alternate;
  }

  .opponent-avatar {
    animation-delay: 0.25s;
  }

  @keyframes bounce {
    from { transform: translateY(0); }
    to { transform: translateY(-10px); }
  }

  .vs {
    font-size: 1.5rem;
    color: #888;
  }

  .battle-text {
    color: #888;
  }

  /* Buttons */
  .btn-primary {
    background: #4caf50;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-primary:hover:not(:disabled) {
    background: #45a049;
  }

  .btn-primary:disabled {
    background: #333;
    color: #666;
    cursor: not-allowed;
  }

  .btn-secondary {
    background: #333;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-secondary:hover {
    background: #444;
  }
</style>
