<script>
  import { gameStore } from '../stores/gameStore.js';
  import AgentCard from './AgentCard.svelte';
  
  let selectedAgent = null;
  let training = false;
  let trainingProgress = 0;
  let trainingResult = null;
  
  $: state = $gameStore;
  $: if (state.selectedAgentId && !selectedAgent) {
    selectedAgent = state.agents.find(a => a.id === state.selectedAgentId);
  }
  
  function selectAgent(agent) {
    selectedAgent = agent;
    gameStore.update(s => ({ ...s, selectedAgentId: agent.id }));
    trainingResult = null;
  }
  
  function startTraining() {
    if (!selectedAgent || training) return;
    
    const cost = getTrainingCost(selectedAgent.level);
    if (state.coins < cost) {
      if (typeof gameStore.notify === 'function') {
        gameStore.notify({ message: '金币不足!', type: 'error' });
      }
      return;
    }
    
    gameStore.update(s => ({ ...s, coins: s.coins - cost }));
    
    training = true;
    trainingProgress = 0;
    trainingResult = null;
    
    const duration = 3000;
    const interval = 100;
    const steps = duration / interval;
    let step = 0;
    
    const timer = setInterval(() => {
      step++;
      trainingProgress = (step / steps) * 100;
      
      if (step >= steps) {
        clearInterval(timer);
        completeTraining();
      }
    }, interval);
  }
  
  function getTrainingCost(level) {
    return Math.floor(100 * Math.pow(1.5, level - 1));
  }
  
  function completeTraining() {
    training = false;
    
    const statIndex = Math.floor(Math.random() * 4);
    const statNames = ['intelligence', 'speed', 'creativity', 'endurance'];
    const statName = statNames[statIndex];
    const gain = Math.floor(5 + Math.random() * 10);
    
    const updatedAgent = {
      ...selectedAgent,
      stats: {
        ...selectedAgent.stats,
        [statName]: selectedAgent.stats[statName] + gain
      }
    };
    
    gameStore.updateAgent(updatedAgent);
    selectedAgent = updatedAgent;
    
    const levelUpChance = 0.3;
    if (Math.random() < levelUpChance) {
      const levelUpAgent = {
        ...updatedAgent,
        level: updatedAgent.level + 1,
        exp: 0,
        stats: {
          intelligence: Math.floor(updatedAgent.stats.intelligence * 1.1),
          speed: Math.floor(updatedAgent.stats.speed * 1.1),
          creativity: Math.floor(updatedAgent.stats.creativity * 1.1),
          endurance: Math.floor(updatedAgent.stats.endurance * 1.1)
        }
      };
      gameStore.updateAgent(levelUpAgent);
      selectedAgent = levelUpAgent;
      
      trainingResult = {
        stat: statName,
        gain,
        levelUp: true,
        message: `💪 ${gain}点, 🎉 升级了!`
      };
    } else {
      trainingResult = {
        stat: statName,
        gain,
        levelUp: false,
        message: `💪 ${statName} +${gain}点`
      };
    }
    
    if (typeof gameStore.notify === 'function') {
      gameStore.notify({ message: trainingResult.message, type: trainingResult.levelUp ? 'success' : 'info' });
    }
  }
  
  function getStatIcon(stat) {
    const icons = { intelligence: '🧠', speed: '⚡', creativity: '💡', endurance: '💪' };
    return icons[stat] || '⭐';
  }
  
  $: cost = selectedAgent ? getTrainingCost(selectedAgent.level) : 0;
  $: canAfford = state.coins >= cost;
</script>

<div class="training-container">
  <div class="training-header">
    <h2>🏋️ 训练中心</h2>
    <p>消耗金币训练,提升属性!</p>
  </div>
  
  <!-- Agent Selection -->
  <div class="agent-select">
    <h3>选择要训练的Agent</h3>
    {#if state.agents.length === 0}
      <div class="empty-state">
        <p>还没有Agent,先去扭蛋召唤吧!</p>
      </div>
    {:else}
      <div class="agent-grid">
        {#each state.agents as agent}
          <div
            class="agent-item"
            class:selected={selectedAgent?.id === agent.id}
            role="button"
            tabindex="0"
            on:click={() => selectAgent(agent)}
            on:keydown={(e) => e.key === 'Enter' && selectAgent(agent)}
          >
            <AgentCard {agent} compact={true} selected={selectedAgent?.id === agent.id} />
          </div>
        {/each}
      </div>
    {/if}
  </div>
  
  {#if selectedAgent}
    <!-- Selected Agent Detail -->
    <div class="selected-detail">
      <h3>训练详情</h3>
      <div class="detail-card">
        <div class="agent-preview">
          <AgentCard agent={selectedAgent} />
        </div>
        
        <div class="training-options">
          <div class="stat-bars">
            {#each ['intelligence', 'speed', 'creativity', 'endurance'] as stat}
              <div class="stat-bar-item">
                <span class="stat-label">{getStatIcon(stat)} {stat}</span>
                <div class="bar-container">
                  <div class="bar-fill" style="width: {Math.min(100, selectedAgent.stats[stat] / 2)}%"></div>
                </div>
                <span class="stat-value">{selectedAgent.stats[stat]}</span>
              </div>
            {/each}
          </div>
          
          <div class="cost-info">
            <span>训练费用:</span>
            <span class="cost-amount">🪙 {cost}</span>
          </div>
          
          {#if training}
            <div class="progress-bar">
              <div class="progress-fill" style="width: {trainingProgress}%"></div>
            </div>
            <p class="training-text">训练中... {Math.floor(trainingProgress)}%</p>
          {:else}
            <button 
              class="train-btn" 
              disabled={!canAfford}
              on:click={startTraining}
            >
              {canAfford ? '开始训练' : '金币不足'}
            </button>
          {/if}
          
          {#if trainingResult}
            <div class="result-box" class:levelup={trainingResult.levelUp}>
              <p>{trainingResult.message}</p>
            </div>
          {/if}
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Training Tips -->
  <div class="tips-section">
    <h3>💡 训练技巧</h3>
    <ul>
      <li>每次训练随机提升一项属性</li>
      <li>有30%概率触发升级,全面提升属性!</li>
      <li>等级越高,训练费用越高</li>
      <li>建议均衡培养各项属性</li>
    </ul>
  </div>
</div>

<style>
  .training-container { display: flex; flex-direction: column; gap: 1.5rem; }
  .training-header { text-align: center; padding: 1rem; background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(102, 126, 234, 0.2) 100%); border-radius: 1rem; border: 1px solid rgba(16, 185, 129, 0.3); }
  .training-header h2 { font-size: 1.25rem; margin-bottom: 0.25rem; }
  .training-header p { font-size: 0.85rem; color: #a0a0a0; }
  
  .agent-select h3 { font-size: 0.9rem; color: #a0a0a0; margin-bottom: 0.75rem; }
  .empty-state { text-align: center; padding: 2rem; background: rgba(255, 255, 255, 0.05); border-radius: 1rem; color: #a0a0a0; }
  .agent-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; }
  .agent-item { cursor: pointer; transition: transform 0.2s; }
  .agent-item:hover { transform: scale(1.02); }
  .agent-item.selected { box-shadow: 0 0 0 2px #667eea; border-radius: 1rem; }
  
  .selected-detail h3 { font-size: 0.9rem; color: #a0a0a0; margin-bottom: 0.75rem; }
  .detail-card { display: flex; gap: 1rem; padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 1rem; }
  .agent-preview { flex: 1; }
  .training-options { flex: 2; display: flex; flex-direction: column; gap: 0.75rem; }
  
  .stat-bars { display: flex; flex-direction: column; gap: 0.5rem; }
  .stat-bar-item { display: flex; align-items: center; gap: 0.5rem; }
  .stat-label { width: 90px; font-size: 0.8rem; }
  .bar-container { flex: 1; height: 8px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden; }
  .bar-fill { height: 100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); transition: width 0.3s; }
  .stat-value { width: 40px; text-align: right; font-size: 0.8rem; font-weight: 600; }
  
  .cost-info { display: flex; justify-content: space-between; padding: 0.5rem; background: rgba(255, 255, 255, 0.05); border-radius: 0.5rem; font-size: 0.9rem; }
  .cost-amount { color: #f59e0b; font-weight: 600; }
  
  .progress-bar { height: 8px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden; }
  .progress-fill { height: 100%; background: linear-gradient(90deg, #10b981 0%, #34d399 100%); transition: width 0.1s; }
  .training-text { text-align: center; font-size: 0.85rem; color: #10b981; }
  
  .train-btn { width: 100%; padding: 0.75rem; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border: none; border-radius: 0.75rem; color: #fff; font-weight: 600; cursor: pointer; transition: all 0.2s; }
  .train-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4); }
  .train-btn:disabled { opacity: 0.5; cursor: not-allowed; }
  
  .result-box { padding: 0.75rem; background: rgba(102, 126, 234, 0.2); border-radius: 0.75rem; text-align: center; font-weight: 600; }
  .result-box.levelup { background: linear-gradient(135deg, rgba(245, 158, 11, 0.3) 0%, rgba(239, 68, 68, 0.3) 100%); border: 1px solid #f59e0b; }
  
  .tips-section { padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 1rem; }
  .tips-section h3 { font-size: 0.9rem; margin-bottom: 0.75rem; color: #a0a0a0; }
  .tips-section ul { list-style: none; display: flex; flex-direction: column; gap: 0.5rem; }
  .tips-section li { font-size: 0.85rem; color: #a0a0a0; padding-left: 1rem; position: relative; }
  .tips-section li::before { content: '•'; position: absolute; left: 0; color: #667eea; }
</style>
