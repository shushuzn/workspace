<script>
  import { gameStore, selectedAgent, agentPower, winRate } from '../stores/gameStore.js';
  import { formatNumber, getRarityStyle } from '../game/agentFactory.js';
  import { RARITIES } from '../game/constants.js';

  $: game = $gameStore;
  $: agent = $selectedAgent;

  $: winRateValue = $winRate;
  $: powerValue = $agentPower;
  $: rarityStyle = agent ? getRarityStyle(agent.rarity) : null;
</script>

<div class="home">
  <!-- 欢迎区域 -->
  <div class="welcome-section">
    <h1>欢迎回来!</h1>
    {#if agent}
      <div class="featured-agent" style="--rarity-color: {rarityStyle.color}">
        <div class="featured-avatar">{agent.avatar}</div>
        <div class="featured-info">
          <h2>{agent.name}</h2>
          <p class="featured-meta">
            <span class="rarity-badge" style="background: {rarityStyle.bg}; color: {rarityStyle.color}">
              {RARITIES[agent.rarity.toUpperCase()]?.name}
            </span>
            <span class="level">Lv.{agent.level}</span>
          </p>
        </div>
        <div class="featured-power">
          <span class="power-label">战力</span>
          <span class="power-num">{formatNumber(powerValue)}</span>
        </div>
      </div>
    {/if}
  </div>

  <!-- 快速操作 -->
  <div class="quick-actions">
    <button class="action-btn battle" on:click={() => gameStore.setTab('battle')}>
      <span class="action-icon">⚔️</span>
      <span class="action-text">战斗</span>
    </button>
    <button class="action-btn training" on:click={() => gameStore.setTab('training')}>
      <span class="action-icon">💪</span>
      <span class="action-text">训练</span>
    </button>
    <button class="action-btn gacha" on:click={() => gameStore.setTab('gacha')}>
      <span class="action-icon">🎰</span>
      <span class="action-text">扭蛋</span>
    </button>
    <button class="btn btn-secondary" on:click={() => gameStore.setTab('arena')}>
      ⚔️ 进入竞技场
    </button>
  </div>

  <!-- 统计数据 -->
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-icon">🏆</div>
      <div class="stat-info">
        <span class="stat-value">{game.stats.totalWins}</span>
        <span class="stat-label">胜利</span>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-icon">⚔️</div>
      <div class="stat-info">
        <span class="stat-value">{game.stats.totalBattles}</span>
        <span class="stat-label">战斗</span>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-icon">📈</div>
      <div class="stat-info">
        <span class="stat-value">{winRateValue}%</span>
        <span class="stat-label">胜率</span>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-icon">🤖</div>
      <div class="stat-info">
        <span class="stat-value">{game.agents.length}</span>
        <span class="stat-label">Agent</span>
      </div>
    </div>
  </div>

  <!-- 每日任务 -->
  <div class="quests-section">
    <h3>📋 每日任务</h3>
    <div class="quests-list">
      {#each game.dailyQuests as quest}
        <div class="quest-item" class:completed={quest.completed}>
          <div class="quest-icon">{quest.icon}</div>
          <div class="quest-info">
            <span class="quest-name">{quest.name}</span>
            <span class="quest-progress">
              {quest.progress}/{quest.target}
            </span>
          </div>
          <div class="quest-reward">
            {#if quest.reward.coins}
              <span>🪙{quest.reward.coins}</span>
            {:else if quest.reward.gems}
              <span>💎{quest.reward.gems}</span>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  </div>

  <!-- 最近战斗 -->
  {#if game.battleLog.length > 0}
    <div class="recent-battles">
      <h3>🗡️ 最近战斗</h3>
      <div class="battle-list">
        {#each game.battleLog.slice(0, 5) as battle}
          <div class="battle-item" class:victory={battle.playerWins}>
            <span class="battle-result">{battle.playerWins ? '胜' : '负'}</span>
            <span class="battle-opponent">vs {battle.opponent?.name || 'AI'}</span>
            <span class="battle-reward">+{battle.reward}🪙</span>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .home {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  /* Welcome Section */
  .welcome-section h1 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: var(--text-secondary);
  }

  .featured-agent {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.25rem;
    background: var(--bg-card);
    border-radius: 1rem;
    border: 1px solid var(--rarity-color, var(--border-color));
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  }

  .featured-avatar {
    font-size: 3rem;
    width: 5rem;
    height: 5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, var(--rarity-color) 0%, rgba(255,255,255,0.1) 100%);
    border-radius: 50%;
    border: 2px solid var(--rarity-color);
  }

  .featured-info {
    flex: 1;
  }

  .featured-info h2 {
    font-size: 1.25rem;
    margin-bottom: 0.25rem;
  }

  .featured-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .rarity-badge {
    padding: 0.15rem 0.5rem;
    border-radius: 1rem;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .level {
    color: var(--text-secondary);
    font-size: 0.85rem;
  }

  .featured-power {
    text-align: center;
  }

  .power-label {
    display: block;
    font-size: 0.7rem;
    color: var(--text-secondary);
  }

  .power-num {
    font-size: 1.25rem;
    font-weight: 700;
    color: #f59e0b;
  }

  /* Quick Actions */
  .quick-actions {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
  }

  .action-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
    color: #fff;
  }

  .action-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  }

  .action-btn.battle:hover {
    border-color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
  }

  .action-btn.training:hover {
    border-color: #10b981;
    background: rgba(16, 185, 129, 0.1);
  }

  .action-btn.gacha:hover {
    border-color: #8b5cf6;
    background: rgba(139, 92, 246, 0.1);
  }

  .action-icon {
    font-size: 1.75rem;
  }

  .action-text {
    font-size: 0.85rem;
    font-weight: 500;
  }

  /* Stats Grid */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }

  .stat-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: var(--bg-card);
    border-radius: 0.75rem;
    border: 1px solid var(--border-color);
  }

  .stat-icon {
    font-size: 1.5rem;
    opacity: 0.8;
  }

  .stat-info {
    display: flex;
    flex-direction: column;
  }

  .stat-value {
    font-size: 1.25rem;
    font-weight: 700;
  }

  .stat-label {
    font-size: 0.75rem;
    color: var(--text-secondary);
  }

  /* Quests Section */
  .quests-section h3 {
    font-size: 1rem;
    margin-bottom: 0.75rem;
  }

  .quests-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .quest-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: var(--bg-card);
    border-radius: 0.75rem;
    border: 1px solid var(--border-color);
  }

  .quest-item.completed {
    opacity: 0.6;
    text-decoration: line-through;
  }

  .quest-icon {
    font-size: 1.25rem;
  }

  .quest-info {
    flex: 1;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .quest-name {
    font-size: 0.9rem;
  }

  .quest-progress {
    font-size: 0.8rem;
    color: var(--text-secondary);
  }

  .quest-reward {
    font-size: 0.8rem;
    padding: 0.25rem 0.5rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 1rem;
  }

  /* Recent Battles */
  .recent-battles h3 {
    font-size: 1rem;
    margin-bottom: 0.75rem;
  }

  .battle-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .battle-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: var(--bg-card);
    border-radius: 0.75rem;
    border-left: 3px solid #ef4444;
  }

  .battle-item.victory {
    border-left-color: #10b981;
  }

  .battle-result {
    font-weight: 700;
    width: 1.5rem;
  }

  .battle-opponent {
    flex: 1;
    font-size: 0.85rem;
  }

  .battle-reward {
    font-size: 0.8rem;
    color: #fbbf24;
  }
</style>
