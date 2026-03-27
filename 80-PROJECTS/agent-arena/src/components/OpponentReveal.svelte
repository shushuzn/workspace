<script>
  import { arenaStore } from '../stores/arenaStore.js';
  import { selectedAgent, agentPower } from '../stores/gameStore.js';

  // Normalize stat bar display
  const MAX_STAT = 100;
  function getBarWidth(stat) {
    return Math.min((stat / MAX_STAT) * 100, 100);
  }

  // Personality chip colors
  const personalityColors = {
    '鲁莽': '#ff6b6b',
    '狡猾': '#ffd93d',
    '坚韧': '#6bcb77',
    '狂暴': '#ff4757',
    '冷静': '#4ecdc4',
    '均衡': '#a0a0a0'
  };

  // Rarity border colors
  const rarityColors = {
    'common': '#9e9e9e',
    'uncommon': '#4caf50',
    'rare': '#2196f3',
    'epic': '#9c27b0',
    'legendary': '#ff9800',
    'mythic': '#f44336'
  };

  $: opponent = $arenaStore.currentOpponent;
  $: playerAgent = $selectedAgent;
  $: playerPower = $agentPower;
</script>

<!-- Opponent Reveal UI -->
<div class="reveal-container">
  <!-- Opponent Section -->
  <div class="opponent-section">
    <div class="avatar-frame" style="border-color: {rarityColors[opponent?.rarity] || '#9e9e9e'}">
      <span class="avatar-emoji">{opponent?.avatar || '🤖'}</span>
    </div>
    <div class="rarity-badge" style="background: {rarityColors[opponent?.rarity] || '#9e9e9e'}">
      {opponent?.rarity?.toUpperCase() || 'COMMON'}
    </div>
    <h2 class="opponent-name">{opponent?.name || '???'}</h2>
    <div class="personality-chip" style="background: {personalityColors[opponent?.personality] || '#a0a0a0'}">
      {opponent?.personality || '均衡'}
    </div>
    <p class="backstory">{opponent?.backstory || 'No data.'}</p>
  </div>

  <!-- Stats Comparison -->
  <div class="stats-section">
    <div class="stat-row">
      <span class="stat-label">🧠 智力</span>
      <div class="stat-bar-bg">
        <div class="stat-bar-fill player" style="width: {getBarWidth(playerAgent?.stats?.intelligence || 0)}%"></div>
        <div class="stat-bar-fill opponent" style="width: {getBarWidth(opponent?.stats?.intelligence || 0)}%"></div>
      </div>
      <span class="stat-value">{opponent?.stats?.intelligence || 0}</span>
    </div>
    <div class="stat-row">
      <span class="stat-label">⚡ 速度</span>
      <div class="stat-bar-bg">
        <div class="stat-bar-fill player" style="width: {getBarWidth(playerAgent?.stats?.speed || 0)}%"></div>
        <div class="stat-bar-fill opponent" style="width: {getBarWidth(opponent?.stats?.speed || 0)}%"></div>
      </div>
      <span class="stat-value">{opponent?.stats?.speed || 0}</span>
    </div>
    <div class="stat-row">
      <span class="stat-label">💡 创造力</span>
      <div class="stat-bar-bg">
        <div class="stat-bar-fill player" style="width: {getBarWidth(playerAgent?.stats?.creativity || 0)}%"></div>
        <div class="stat-bar-fill opponent" style="width: {getBarWidth(opponent?.stats?.creativity || 0)}%"></div>
      </div>
      <span class="stat-value">{opponent?.stats?.creativity || 0}</span>
    </div>
    <div class="stat-row">
      <span class="stat-label">💪 耐力</span>
      <div class="stat-bar-bg">
        <div class="stat-bar-fill player" style="width: {getBarWidth(playerAgent?.stats?.endurance || 0)}%"></div>
        <div class="stat-bar-fill opponent" style="width: {getBarWidth(opponent?.stats?.endurance || 0)}%"></div>
      </div>
      <span class="stat-value">{opponent?.stats?.endurance || 0}</span>
    </div>
  </div>

  <!-- Power Comparison -->
  <div class="power-compare">
    <div class="power-bar">
      <div
        class="power-player"
        style="width: {playerPower > 0 && (opponent?.power || 0) > 0 ? Math.min(playerPower / (playerPower + (opponent?.power || 0)) * 100, 100) : 50}%"
      >
        <span>你的: {playerPower}</span>
      </div>
      <div
        class="power-opponent"
        style="width: {playerPower > 0 && (opponent?.power || 0) > 0 ? Math.min((opponent?.power || 0) / (playerPower + (opponent?.power || 0)) * 100, 100) : 50}%"
      >
        <span>对手: {opponent?.power || 0}</span>
      </div>
    </div>
  </div>
</div>

<style>
  .reveal-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }

  .opponent-section {
    text-align: center;
  }

  .avatar-frame {
    font-size: 4rem;
    border: 4px solid;
    border-radius: 12px;
    padding: 1rem;
    display: inline-block;
    background: rgba(255, 255, 255, 0.05);
  }

  .rarity-badge {
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.75rem;
    font-weight: bold;
    display: inline-block;
    margin-top: 0.5rem;
  }

  .opponent-name {
    font-size: 1.5rem;
    font-weight: bold;
    margin: 0.5rem 0;
  }

  .personality-chip {
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.875rem;
    display: inline-block;
  }

  .backstory {
    font-size: 0.875rem;
    color: #888;
    margin-top: 0.5rem;
    font-style: italic;
    animation: fadeIn 1s ease-in;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .stats-section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .stat-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .stat-label {
    width: 80px;
    font-size: 0.75rem;
  }

  .stat-bar-bg {
    flex: 1;
    height: 8px;
    background: #333;
    border-radius: 4px;
    position: relative;
    overflow: hidden;
  }

  .stat-bar-fill {
    position: absolute;
    height: 100%;
    border-radius: 4px;
  }

  .stat-bar-fill.player {
    background: #4caf50;
    left: 0;
    top: 0;
  }

  .stat-bar-fill.opponent {
    background: #ff9800;
    right: 0;
    top: 0;
  }

  .stat-value {
    width: 30px;
    text-align: right;
    font-size: 0.75rem;
  }

  .power-compare {
    margin-top: 1rem;
  }

  .power-bar {
    display: flex;
    gap: 0.5rem;
    height: 2rem;
  }

  .power-player {
    background: #4caf50;
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .power-opponent {
    background: #ff9800;
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }
</style>
