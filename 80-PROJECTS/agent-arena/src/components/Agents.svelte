<script>
  import { gameStore, selectedAgent } from '../stores/gameStore.js';
  import { formatNumber, calculatePower, getRarityStyle } from '../game/agentFactory.js';
  import { RARITIES, STATS, EVOLUTION_STAGES } from '../game/constants.js';
  import { createAgent } from '../game/agentFactory.js';

  let showCreateModal = false;
  let selectedRarity = 'common';
  let customName = '';
  let selectedAgentForDetails = null;

  $: game = $gameStore;
  $: agent = $selectedAgent;

  $: sortedAgents = [...game.agents].sort((a, b) => {
    const powerA = calculatePower(a);
    const powerB = calculatePower(b);
    return powerB - powerA;
  });

  function selectAgent(id) {
    gameStore.selectAgent(id);
  }

  function createNewAgent() {
    const cost = selectedRarity === 'rare' ? 500 : selectedRarity === 'epic' ? 2000 : selectedRarity === 'legendary' ? 10000 : 0;
    
    if (cost > 0 && !gameStore.spendCoins(cost)) {
      gameStore.notify('金币不足!', 'error');
      return;
    }

    const newAgent = createAgent({
      rarity: selectedRarity,
      name: customName.trim() || undefined
    });

    gameStore.addAgent(newAgent);
    gameStore.selectAgent(newAgent.id);
    gameStore.notify(`成功创建 ${newAgent.name}!`);
    
    showCreateModal = false;
    customName = '';
    selectedRarity = 'common';
  }

  function deleteAgent(id) {
    if (game.agents.length <= 1) {
      gameStore.notify('至少需要保留一个Agent!', 'error');
      return;
    }
    gameStore.removeAgent(id);
    gameStore.notify('Agent已删除');
    selectedAgentForDetails = null;
  }

  function viewDetails(agent) {
    selectedAgentForDetails = agent;
  }

  $: selectedStyle = selectedAgentForDetails ? getRarityStyle(selectedAgentForDetails.rarity) : null;
</script>

<div class="agents-page">
  <div class="page-header">
    <h2>🤖 我的Agent</h2>
    <button class="btn btn-primary" on:click={() => showCreateModal = true}>
      ✨ 创建新Agent
    </button>
  </div>

  {#if sortedAgents.length === 0}
    <div class="empty-state">
      <div class="empty-icon">🤖</div>
      <h3>还没有Agent</h3>
      <p>创建你的第一个AI战士开始冒险!</p>
      <button class="btn btn-primary" on:click={() => showCreateModal = true}>
        创建第一个Agent
      </button>
    </div>
  {:else}
    <div class="agents-list">
      {#each sortedAgents as agent (agent.id)}
        {@const power = calculatePower(agent)}
        {@const rarityStyle = getRarityStyle(agent.rarity)}
        {@const isSelected = agent.id === game.selectedAgentId}
        
        <div 
          class="agent-card" 
          class:selected={isSelected}
          style="--rarity-color: {rarityStyle.color}; --rarity-bg: {rarityStyle.bg}; --rarity-border: {rarityStyle.border}"
          on:click={() => selectAgent(agent.id)}
          on:keypress={(e) => e.key === 'Enter' && selectAgent(agent.id)}
          role="button"
          tabindex="0"
        >
          <div class="agent-avatar-wrapper">
            <span class="agent-avatar">{agent.avatar}</span>
            {#if isSelected}
              <span class="selected-badge">✓</span>
            {/if}
          </div>
          
          <div class="agent-main">
            <div class="agent-header">
              <h3 class="agent-name">{agent.name}</h3>
              <span class="rarity-badge">{RARITIES[agent.rarity.toUpperCase()]?.name}</span>
            </div>
            
            <div class="agent-meta">
              <span class="level">Lv.{agent.level}</span>
              <span class="stage">{EVOLUTION_STAGES[agent.evolutionStage]}</span>
            </div>
            
            <div class="agent-stats-mini">
              <span class="stat" title="智力">🧠{agent.stats.intelligence}</span>
              <span class="stat" title="速度">⚡{agent.stats.speed}</span>
              <span class="stat" title="创造力">💡{agent.stats.creativity}</span>
              <span class="stat" title="耐力">💪{agent.stats.endurance}</span>
            </div>
            
            <div class="exp-bar">
              <div class="exp-progress" style="width: {(agent.exp / agent.expToLevel) * 100}%"></div>
            </div>
          </div>
          
          <div class="agent-power-display">
            <span class="power-label">战力</span>
            <span class="power-value">{formatNumber(power)}</span>
          </div>
          
          <div class="agent-actions">
            <button class="action-btn" on:click|stopPropagation={() => viewDetails(agent)}>
              📋
            </button>
            {#if !isSelected}
              <button class="action-btn delete" on:click|stopPropagation={() => deleteAgent(agent.id)}>
                🗑️
              </button>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}

  <!-- Create Modal -->
  {#if showCreateModal}
    <div class="modal-overlay" on:click={() => showCreateModal = false} on:keypress={() => {}}>
      <div class="modal" on:click|stopPropagation on:keypress={() => {}}>
        <h3>创建新Agent</h3>
        
        <div class="input-group">
          <label>名字 (可选)</label>
          <input type="text" bind:value={customName} placeholder="留空随机生成" maxlength="20" />
        </div>
        
        <div class="rarity-selector">
          <label>稀有度</label>
          <div class="rarity-options">
            {#each Object.entries(RARITIES) as [key, rarity]}
              <button 
                class="rarity-option" 
                class:selected={selectedRarity === rarity.id}
                style="--color: {rarity.color}"
                on:click={() => selectedRarity = rarity.id}
              >
                <span class="rarity-name">{rarity.name}</span>
                {#if rarity.id !== 'common'}
                  <span class="rarity-cost">
                    {rarity.id === 'rare' ? '500' : rarity.id === 'epic' ? '2000' : '10000'}🪙
                  </span>
                {/if}
              </button>
            {/each}
          </div>
        </div>
        
        <div class="preview-stats">
          <h4>预估属性</h4>
          <div class="stats-preview">
            <span>🧠 20-40</span>
            <span>⚡ 20-40</span>
            <span>💡 20-40</span>
            <span>💪 20-40</span>
          </div>
          <p class="preview-note">×{RARITIES[selectedRarity.toUpperCase()]?.multiplier || 1} 稀有度加成</p>
        </div>
        
        <div class="modal-actions">
          <button class="btn btn-secondary" on:click={() => showCreateModal = false}>
            取消
          </button>
          <button class="btn btn-primary" on:click={createNewAgent}>
            创建
          </button>
        </div>
      </div>
    </div>
  {/if}

  <!-- Details Modal -->
  {#if selectedAgentForDetails}
    {@const agentDetails = selectedAgentForDetails}
    {@const power = calculatePower(agentDetails)}
    {@const rarityStyle = getRarityStyle(agentDetails.rarity)}
    
    <div class="modal-overlay" on:click={() => selectedAgentForDetails = null} on:keypress={() => {}}>
      <div class="modal details-modal" on:click|stopPropagation on:keypress={() => {}}>
        <div class="details-header" style="--rarity-color: {rarityStyle.color}">
          <span class="details-avatar">{agentDetails.avatar}</span>
          <div class="details-title">
            <h3>{agentDetails.name}</h3>
            <p>
              <span class="rarity-badge">{RARITIES[agentDetails.rarity.toUpperCase()]?.name}</span>
              <span class="level">Lv.{agentDetails.level}</span>
            </p>
          </div>
        </div>
        
        <div class="power-section">
          <span class="power-label">总战力</span>
          <span class="power-value">{formatNumber(power)}</span>
        </div>
        
        <div class="stats-section">
          <h4>属性</h4>
          <div class="stats-grid">
            {#each Object.entries(STATS) as [key, stat]}
              <div class="stat-item" style="--stat-color: {stat.color}">
                <span class="stat-emoji">{stat.emoji}</span>
                <span class="stat-name">{stat.name}</span>
                <span class="stat-value">{agentDetails.stats[stat.id]}</span>
              </div>
            {/each}
          </div>
        </div>
        
        {#if agentDetails.skills && agentDetails.skills.length > 0}
          <div class="skills-section">
            <h4>技能</h4>
            <div class="skills-list">
              {#each agentDetails.skills as skill}
                <div class="skill-item">
                  <span class="skill-emoji">{skill.emoji}</span>
                  <span class="skill-name">{skill.name}</span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
        
        <div class="record-section">
          <h4>战绩</h4>
          <div class="record-stats">
            <span class="wins">胜 {agentDetails.wins}</span>
            <span class="losses">负 {agentDetails.losses}</span>
            <span class="rate">
              胜率 {agentDetails.wins + agentDetails.losses > 0 
                ? Math.round(agentDetails.wins / (agentDetails.wins + agentDetails.losses) * 100) 
                : 0}%
            </span>
          </div>
        </div>
        
        <div class="modal-actions">
          <button class="btn btn-secondary" on:click={() => selectedAgentForDetails = null}>
            关闭
          </button>
          <button class="btn btn-primary" on:click={() => { gameStore.selectAgent(agentDetails.id); selectedAgentForDetails = null; }}>
            选择战斗
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .agents-page {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .page-header h2 {
    font-size: 1.25rem;
  }

  .btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 0.5rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
  }

  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  }

  .btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
    border: 1px solid var(--border-color);
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    text-align: center;
    gap: 1rem;
  }

  .empty-icon {
    font-size: 4rem;
    opacity: 0.5;
  }

  .empty-state h3 {
    font-size: 1.25rem;
  }

  .empty-state p {
    color: var(--text-secondary);
  }

  /* Agent Card */
  .agents-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .agent-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: var(--bg-card);
    border-radius: 0.75rem;
    border: 1px solid var(--rarity-border, var(--border-color));
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .agent-card:hover {
    background: rgba(255, 255, 255, 0.08);
    transform: translateX(4px);
  }

  .agent-card.selected {
    background: var(--rarity-bg);
    border-width: 2px;
  }

  .agent-avatar-wrapper {
    position: relative;
  }

  .agent-avatar {
    font-size: 2.5rem;
    display: block;
  }

  .selected-badge {
    position: absolute;
    bottom: -0.25rem;
    right: -0.25rem;
    background: #10b981;
    color: #fff;
    font-size: 0.7rem;
    width: 1rem;
    height: 1rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .agent-main {
    flex: 1;
    min-width: 0;
  }

  .agent-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
  }

  .agent-name {
    font-size: 0.95rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .rarity-badge {
    font-size: 0.65rem;
    padding: 0.1rem 0.4rem;
    background: var(--rarity-bg);
    color: var(--rarity-color);
    border-radius: 1rem;
    font-weight: 600;
  }

  .agent-meta {
    display: flex;
    gap: 0.5rem;
    font-size: 0.75rem;
    color: var(--text-secondary);
    margin-bottom: 0.25rem;
  }

  .agent-stats-mini {
    display: flex;
    gap: 0.5rem;
    font-size: 0.7rem;
    margin-bottom: 0.25rem;
  }

  .exp-bar {
    height: 3px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    overflow: hidden;
  }

  .exp-progress {
    height: 100%;
    background: linear-gradient(90deg, #667eea, #764ba2);
    border-radius: 2px;
    transition: width 0.3s ease;
  }

  .agent-power-display {
    text-align: center;
    padding: 0 0.5rem;
  }

  .agent-power-display .power-label {
    display: block;
    font-size: 0.6rem;
    color: var(--text-secondary);
  }

  .agent-power-display .power-value {
    font-size: 1rem;
    font-weight: 700;
    color: #f59e0b;
  }

  .agent-actions {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .action-btn {
    background: transparent;
    border: none;
    padding: 0.25rem;
    cursor: pointer;
    font-size: 1rem;
    opacity: 0.6;
    transition: opacity 0.2s;
  }

  .action-btn:hover {
    opacity: 1;
  }

  /* Modal */
  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 1rem;
  }

  .modal {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 1rem;
    padding: 1.5rem;
    width: 100%;
    max-width: 360px;
    border: 1px solid var(--border-color);
  }

  .modal h3 {
    font-size: 1.25rem;
    margin-bottom: 1rem;
    text-align: center;
  }

  .input-group {
    margin-bottom: 1rem;
  }

  .input-group label {
    display: block;
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
  }

  .input-group input {
    width: 100%;
    padding: 0.75rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    color: #fff;
    font-size: 1rem;
  }

  .input-group input:focus {
    outline: none;
    border-color: #667eea;
  }

  .rarity-selector label {
   