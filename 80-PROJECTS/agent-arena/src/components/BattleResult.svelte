<script>
  import { onMount } from 'svelte';
  import { arenaStore } from '../stores/arenaStore.js';
  import { gameStore, selectedAgent } from '../stores/gameStore.js';

  export let result = 'win'; // 'win' | 'lose'
  export let opponent = null;

  onMount(() => {
    // Apply coin reward
    gameStore.addCoins(rewards.coins);

    // Apply XP to selected agent using addAgentXP for proper level-up handling
    if ($selectedAgent) {
      gameStore.addAgentXP($selectedAgent.id, rewards.xp);
    }
  });

  $: difficulty = opponent?.difficulty || 1.0;
  $: rewards = result === 'win'
    ? { xp: Math.floor(50 * difficulty), coins: Math.floor(20 * difficulty) }
    : { xp: 10, coins: 5 };
  $: isWin = result === 'win';

  function playAgain() {
    arenaStore.reset();
    arenaStore.setStage('STAGE_SELECT');
  }

  function goHome() {
    arenaStore.reset();
    // Navigate back to home
    gameStore.setTab('home');
  }
</script>

<div class="result-container">
  <div class="result-banner {isWin ? 'win' : 'lose'}">
    <h1>{isWin ? '🎉 胜利!' : '😢 失败'}</h1>
    <p class="result-subtitle">
      {isWin
        ? `你击败了 ${opponent?.name || '对手'}!`
        : `${opponent?.name || '对手'} 战胜了你`}
    </p>
  </div>

  <div class="rewards-panel">
    <h2>获得奖励</h2>
    <div class="rewards-grid">
      <div class="reward-item">
        <span class="reward-icon">⚡</span>
        <span class="reward-label">经验</span>
        <span class="reward-value">+{rewards.xp}</span>
      </div>
      <div class="reward-item">
        <span class="reward-icon">🪙</span>
        <span class="reward-label">星尘币</span>
        <span class="reward-value">+{rewards.coins}</span>
      </div>
    </div>
  </div>

  <div class="actions">
    <button class="btn-primary" on:click={playAgain}>
      再来一局
    </button>
    <button class="btn-secondary" on:click={goHome}>
      返回
    </button>
  </div>
</div>

<style>
  .result-container { display: flex; flex-direction: column; gap: 1.5rem; padding: 1rem; text-align: center; }
  .result-banner { padding: 2rem; border-radius: 12px; }
  .result-banner.win { background: linear-gradient(135deg, #4caf50, #2e7d32); color: white; }
  .result-banner.lose { background: linear-gradient(135deg, #f44336, #c62828); color: white; }
  .result-banner h1 { font-size: 2rem; margin: 0; }
  .result-subtitle { margin: 0.5rem 0 0; opacity: 0.9; }
  .rewards-panel { background: #1a1a1a; border-radius: 8px; padding: 1rem; }
  .rewards-panel h2 { margin: 0 0 1rem; font-size: 1rem; color: #888; }
  .rewards-grid { display: flex; justify-content: center; gap: 2rem; }
  .reward-item { display: flex; flex-direction: column; align-items: center; gap: 0.25rem; }
  .reward-icon { font-size: 1.5rem; }
  .reward-label { font-size: 0.75rem; color: #888; }
  .reward-value { font-size: 1.25rem; font-weight: bold; color: #4caf50; }
  .actions { display: flex; flex-direction: column; gap: 0.75rem; }
  .btn-primary { background: #4caf50; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; font-size: 1rem; cursor: pointer; }
  .btn-secondary { background: #333; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; font-size: 1rem; cursor: pointer; }
  .btn-primary:hover { background: #45a049; }
  .btn-secondary:hover { background: #444; }
</style>
