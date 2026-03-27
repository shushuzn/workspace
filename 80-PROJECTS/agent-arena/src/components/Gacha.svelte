<script>
  import { gameStore } from '../stores/gameStore.js';
  import { createAgent, selectGachaRarity } from '../game/agentFactory.js';
  import { GACHA_CONFIG } from '../game/constants.js';
  import AgentCard from './AgentCard.svelte';
  
  let pulling = false;
  let result = null;
  let showResult = false;
  let lastResults = [];
  
  const gachaOptions = [
    {
      id: 'single',
      name: '单抽',
      icon: '🎰',
      ...GACHA_CONFIG.single,
      description: '普通扭蛋'
    },
    {
      id: 'ten',
      name: '十连抽',
      icon: '🎯',
      ...GACHA_CONFIG.ten,
      description: '必得稀有以上',
      highlight: true
    },
    {
      id: 'premium',
      name: '钻石单抽',
      icon: '💎',
      ...GACHA_CONFIG.premium,
      description: '必得史诗以上'
    },
    {
      id: 'legend',
      name: '传说召唤',
      icon: '👑',
      ...GACHA_CONFIG.legend,
      description: '必得传说!'
    }
  ];
  
  function pull(type) {
    if (pulling) return;
    
    const config = gachaOptions.find(g => g.id === type);
    if (!config) return;
    
    const currency = config.currency || 'coins';
    if (gameStore.getState().coins < config.cost && currency === 'coins') {
      if (typeof gameStore.notify === 'function') {
        gameStore.notify({ message: '金币不足!', type: 'error' });
      }
      return;
    }
    if (gameStore.getState().gems < config.cost && currency === 'gems') {
      if (typeof gameStore.notify === 'function') {
        gameStore.notify({ message: '钻石不足!', type: 'error' });
      }
      return;
    }
    
    pulling = true;
    showResult = false;
    
    // 扣除货币
    if (currency === 'coins') {
      gameStore.update(state => ({
        ...state,
        coins: state.coins - config.cost
      }));
    } else {
      gameStore.update(state => ({
        ...state,
        gems: state.gems - config.cost
      }));
    }
    
    // 生成结果
    setTimeout(() => {
      const count = config.pulls;
      const results = [];
      
      for (let i = 0; i < count; i++) {
        const rarity = type === 'ten' 
          ? (i === 9 ? 'rare' : selectGachaRarity(type))
          : selectGachaRarity(type);
        
        const agent = createAgent({ rarity });
        results.push(agent);
        gameStore.addAgent(agent);
      }
      
      lastResults = results;
      result = results[0];
      showResult = true;
      pulling = false;
      
      // 稀有度提示
      const highestRarity = results.reduce((max, r) => {
        const order = ['common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic'];
        return order.indexOf(r.rarity) > order.indexOf(max.rarity) ? r : max;
      });
      
      if (['epic', 'legendary', 'mythic'].includes(highestRarity.rarity)) {
        if (typeof gameStore.notify === 'function') {
          gameStore.notify({ 
            message: `🎉 恭喜获得 ${highestRarity.name}!`, 
            type: 'success' 
          });
        }
      }
    }, 500);
  }
  
  function closeResult() {
    showResult = false;
    result = null;
  }
  
  function canAfford(option) {
    const currency = option.currency || 'coins';
    const state = gameStore.getState();
    if (currency === 'coins') {
      return state.coins >= option.cost;
    }
    return state.gems >= option.cost;
  }
  
  $: state = $gameStore;
</script>

<div class="gacha-container">
  <div class="gacha-header">
    <h2>🎰 扭蛋中心</h2>
    <p>花费资源召唤新的Agent!</p>
  </div>
  
  <div class="gacha-options">
    {#each gachaOptions as option}
      <button 
        class="gacha-card" 
        class:highlight={option.highlight}
        class:disabled={!canAfford(option) || pulling}
        on:click={() => pull(option.id)}
      >
        <span class="gacha-icon">{option.icon}</span>
        <span class="gacha-name">{option.name}</span>
        <span class="gacha-desc">{option.description}</span>
        <span class="gacha-cost">
          {#if option.currency === 'gems'}
            💎 {option.cost}
          {:else}
            🪙 {option.cost}
          {/if}
        </span>
      </button>
    {/each}
  </div>
  
  <div class="odds-info">
    <h3>📊 概率公示</h3>
    <div class="odds-grid">
      <div class="odds-item" style="--rarity-color: #9ca3af">
        <span>普通</span>
        <span>50%</span>
      </div>
      <div class="odds-item" style="--rarity-color: #10b981">
        <span>优秀</span>
        <span>30%</span>
      </div>
      <div class="odds-item" style="--rarity-color: #3b82f6">
        <span>稀有</span>
        <span>15%</span>
      </div>
      <div class="odds-item" style="--rarity-color: #a855f7">
        <span>史诗</span>
        <span>4%</span>
      </div>
      <div class="odds-item" style="--rarity-color: #f59e0b">
        <span>传说</span>
        <span>0.9%</span>
      </div>
      <div class="odds-item" style="--rarity-color: #ef4444">
        <span>神话</span>
        <span>0.1%</span>
      </div>
    </div>
  </div>
  
  {#if state.agents.length > 0}
    <div class="collection">
      <h3>📁 我的收藏 ({state.agents.length})</h3>
      <div class="collection-grid">
        {#each state.agents.slice(0, 6) as agent}
          <AgentCard {agent} compact={true} />
        {/each}
      </div>
      {#if state.agents.length > 6}
        <p class="more-hint">还有 {state.agents.length - 6} 个Agent...</p>
      {/if}
    </div>
  {/if}
</div>

{#if showResult && result}
  <div class="result-overlay" role="button" tabindex="0" on:click={closeResult} on:keydown={(e) => e.key === 'Enter' && closeResult()}>
    <div class="result-modal" role="dialog" aria-modal="true">
      <h2>🎉 恭喜获得!</h2>
      
      <div class="result-card">
        <AgentCard agent={result} />
      </div>
      
      {#if lastResults.length > 1}
        <div class="all-results">
          <h4>本次十连</h4>
          <div class="results-grid">
            {#each lastResults as agent}
              <div class="result-item {agent.rarity}">
                <span class="result-avatar">{agent.avatar}</span>
                <span class="result-name">{agent.name}</span>
              </div>
            {/each}
          </div>
        </div>
      {/if}
      
      <button class="close-btn" on:click={closeResult}>
        确定
      </button>
    </div>
  </div>
{/if}

<style>
  .gacha-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .gacha-header {
    text-align: center;
    padding: 1rem;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
    border-radius: 1rem;
    border: 1px solid rgba(102, 126, 234, 0.3);
  }

  .gacha-header h2 {
    font-size: 1.25rem;
    margin-bottom: 0.25rem;
  }

  .gacha-header p {
    font-size: 0.85rem;
    color: #a0a0a0;
  }

  .gacha-options {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }

  .gacha-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.05);
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: 1rem;
    cursor: pointer;
    transition: all 0.3s;
  }

  .gacha-card:hover:not(.disabled) {
    transform: translateY(-4px);
    border-color: #667eea;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }

  .gacha-card.highlight {
    border-color: #f59e0b;
    background: rgba(245, 158, 11, 0.1);
  }

  .gacha-card.highlight:hover:not(.disabled) {
    box-shadow: 0 8px 25px rgba(245, 158, 11, 0.3);
  }

  .gacha-card.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .gacha-icon {
    font-size: 2rem;
  }

  .gacha-name {
    font-weight: 700;
    font-size: 1rem;
  }

  .gacha-desc {
    font-size: 0.7rem;
    color: #a0a0a0;
  }

  .gacha-cost {
    font-weight: 600;
    color: #667eea;
  }

  .odds-info {
    padding: 1rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 1rem;
  }

  .odds-info h3 {
    font-size: 0.9rem;
    margin-bottom: 0.75rem;
    color: #a0a0a0;
  }

  .odds-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
  }

  .odds-item {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0.75rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 0.5rem;
    border-left: 3px solid var(--rarity-color);
    font-size: 0.8rem;
  }

  .collection {
    padding: 1rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 1rem;
  }

  .collection h3 {
    font-size: 0.9rem;
    margin-bottom: 0.75rem;
    color: #a0a0a0;
  }

  .collection-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
  }

  .more-hint {
    text-align: center;
    font-size: 0.8rem;
    color: #a0a0a0;
    margin-top: 0.75rem;
  }

  /* Result Modal */
  .result-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeIn 0.3s;
  }

  .result-modal {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 1.5rem;
    padding: 1.5rem;
    max-width: 90%;
    width: 360px;
    text-align: center;
    animation: scaleIn 0.3s;
  }

  .result-modal h2 {
    font-size: 1.25rem;
    margin-bottom: 1rem;
  }

  .result-card {
    margin-bottom: 1rem;
  }

  .all-results {
    margin: 1rem 0;
    padding: 0.75rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 0.75rem;
  }

  .all-results h4 {
    font-size: 0.85rem;
    color: #a0a0a0;
    margin-bottom: 0.5rem;
  }

  .results-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.5rem;
  }

  .result-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0.5rem 0.25rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 0.5rem;
    border: 1px solid transparent;
  }

  .result-item.epic { border-color: #a855f7; }
  .result-item.legendary { border-color: #f59e0b; }
  .result-item.mythic { border-color: #ef4444; }

  .result-avatar {
    font-size: 1.25rem;
  }

  .result-name {
    font-size: 0.6rem;
    color: #a0a0a0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 100%;
  }

  .close-btn {
    width: 100%;
    padding: 0.75rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 0.75rem;
    color: #fff;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .close-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  @keyframes scaleIn {
    from {
      opacity: 0;
      transform: scale(0.8);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }
</style>
