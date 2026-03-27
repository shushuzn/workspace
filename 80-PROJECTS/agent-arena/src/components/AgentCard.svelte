<script>
  import { RARITIES, EVOLUTION_STAGES } from '../game/constants.js';
  import { getRarityStyle, getEvolutionStage } from '../game/agentFactory.js';
  
  export let agent;
  export let selected = false;
  export let compact = false;
  
  $: style = getRarityStyle(agent.rarity);
  $: evolutionStage = getEvolutionStage(agent.level);
  $: evolutionLabel = EVOLUTION_STAGES[evolutionStage];
</script>

<div 
  class="agent-card" 
  class:selected 
  class:compact
  style="
    --rarity-color: {style.color};
    --rarity-bg: {style.bg};
    --rarity-border: {style.border};
  "
>
  <div class="avatar-container">
    <span class="avatar">{agent.avatar}</span>
    {#if selected}
      <span class="selected-badge">✓</span>
    {/if}
  </div>
  
  <div class="info">
    <div class="name-row">
      <span class="name">{agent.name}</span>
      <span class="level">Lv.{agent.level}</span>
    </div>
    
    <div class="rarity">
      <span class="rarity-tag" style="color: {style.color}; border-color: {style.border}">
        {style.name}
      </span>
      <span class="evolution">{evolutionLabel}</span>
    </div>
    
    {#if !compact}
      <div class="stats">
        <div class="stat">
          <span class="stat-emoji">🧠</span>
          <span class="stat-value">{agent.stats.intelligence}</span>
        </div>
        <div class="stat">
          <span class="stat-emoji">⚡</span>
          <span class="stat-value">{agent.stats.speed}</span>
        </div>
        <div class="stat">
          <span class="stat-emoji">💡</span>
          <span class="stat-value">{agent.stats.creativity}</span>
        </div>
        <div class="stat">
          <span class="stat-emoji">💪</span>
          <span class="stat-value">{agent.stats.endurance}</span>
        </div>
      </div>
      
      <div class="power">
        <span class="power-label">战力</span>
        <span class="power-value">{Math.floor(agent.power)}</span>
      </div>
    {:else}
      <div class="compact-power">
        ⚔️ {Math.floor(agent.power)}
      </div>
    {/if}
  </div>
</div>

<style>
  .agent-card {
    background: var(--rarity-bg);
    border: 2px solid var(--rarity-border);
    border-radius: 1rem;
    padding: 1rem;
    transition: all 0.2s;
  }

  .agent-card.compact {
    padding: 0.75rem;
  }

  .agent-card.selected {
    box-shadow: 0 0 20px var(--rarity-color);
  }

  .agent-card:hover {
    transform: translateY(-2px);
  }

  .avatar-container {
    position: relative;
    width: 64px;
    height: 64px;
    margin: 0 auto 0.75rem;
  }

  .compact .avatar-container {
    width: 40px;
    height: 40px;
    margin-bottom: 0.5rem;
  }

  .avatar {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50%;
    border: 2px solid var(--rarity-color);
  }

  .compact .avatar {
    font-size: 1.5rem;
  }

  .selected-badge {
    position: absolute;
    bottom: -4px;
    right: -4px;
    width: 20px;
    height: 20px;
    background: #10b981;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: bold;
    border: 2px solid #0f0f23;
  }

  .info {
    text-align: center;
  }

  .name-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .name {
    font-weight: 700;
    font-size: 0.95rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .compact .name {
    font-size: 0.75rem;
  }

  .level {
    font-size: 0.75rem;
    color: #667eea;
    font-weight: 600;
  }

  .compact .level {
    font-size: 0.65rem;
  }

  .rarity {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
  }

  .rarity-tag {
    font-size: 0.7rem;
    padding: 0.2rem 0.5rem;
    border: 1px solid;
    border-radius: 0.5rem;
    font-weight: 600;
  }

  .compact .rarity-tag {
    font-size: 0.6rem;
    padding: 0.15rem 0.35rem;
  }

  .evolution {
    font-size: 0.7rem;
    color: #a0a0a0;
  }

  .compact .evolution {
    display: none;
  }

  .stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.25rem;
    margin-bottom: 0.75rem;
  }

  .stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0.35rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 0.5rem;
  }

  .stat-emoji {
    font-size: 0.8rem;
  }

  .stat-value {
    font-size: 0.75rem;
    font-weight: 600;
  }

  .power {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    background: rgba(102, 126, 234, 0.2);
    border-radius: 0.5rem;
  }

  .power-label {
    font-size: 0.8rem;
    color: #a0a0a0;
  }

  .power-value {
    font-size: 1.1rem;
    font-weight: 700;
    color: #667eea;
  }

  .compact-power {
    font-size: 0.75rem;
    color: #667eea;
    font-weight: 600;
  }
</style>
