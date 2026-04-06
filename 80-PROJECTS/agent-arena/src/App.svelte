<script>
  import { onMount } from 'svelte';
  import { gameStore } from './stores/gameStore.js';
  import { createAgent } from './game/agentFactory.js';
  
  import Gacha from './components/Gacha.svelte';
  import AgentCard from './components/AgentCard.svelte';
  import Battle from './components/Battle.svelte';
  import Training from './components/Training.svelte';
  import Profile from './components/Profile.svelte';
  import ArenaPanel from './components/ArenaPanel.svelte';
  import TournamentTab from './components/TournamentTab.svelte';
  
  let currentTab = 'home';
  let notifications = [];
  
  // 初始化游戏
  onMount(() => {
    const savedGame = localStorage.getItem('agentArena');
    if (savedGame) {
      try {
        const data = JSON.parse(savedGame);
        // 恢复游戏状态
        gameStore.setState({
          ...gameStore.getState(),
          coins: data.coins ?? 500,
          gems: data.gems ?? 10,
          agents: data.agents ?? [],
          selectedAgentId: data.selectedAgentId ?? null,
          dailyQuests: data.dailyQuests ?? gameStore.getState().dailyQuests,
          stats: data.stats ?? { totalBattles: 0, totalWins: 0, totalGachaPulls: 0 }
        });
      } catch (e) {
        console.error('Failed to load save:', e);
        initNewGame();
      }
    } else {
      initNewGame();
    }
    
    // 保存游戏
    const saveInterval = setInterval(() => {
      saveGame();
    }, 30000);
    
    return () => clearInterval(saveInterval);
  });
  
  function initNewGame() {
    const starterAgent = createAgent({ 
      rarity: 'uncommon', 
      name: '初始Agent' 
    });
    
    gameStore.addAgent(starterAgent);
    gameStore.selectAgent(starterAgent.id);
    saveGame();
  }
  
  function saveGame() {
    const state = gameStore.getState();
    const saveData = {
      coins: state.coins,
      gems: state.gems,
      agents: state.agents,
      selectedAgentId: state.selectedAgentId,
      dailyQuests: state.dailyQuests,
      stats: state.stats,
      lastSave: Date.now()
    };
    localStorage.setItem('agentArena', JSON.stringify(saveData));
  }
  
  function addNotification(message, type = 'info') {
    const id = Date.now();
    notifications = [...notifications, { id, message, type }];
    setTimeout(() => {
      notifications = notifications.filter(n => n.id !== id);
    }, 3000);
  }
  
  function handleNotify(event) {
    const { message, type } = event.detail || { message: event, type: 'info' };
    addNotification(message, type);
  }
  
  // 全局监听通知
  gameStore.notify = handleNotify;
  
  $: game = $gameStore;
  $: selectedAgent = game.agents.find(a => a.id === game.selectedAgentId);
  
  const tabs = [
    { id: 'home', icon: '🏠', label: '首页' },
    { id: 'gacha', icon: '🎰', label: '扭蛋' },
    { id: 'battle', icon: '⚔️', label: '战斗' },
    { id: 'training', icon: '💪', label: '训练' },
    { id: 'arena', icon: '⚔️', label: '竞技场' },
    { id: 'tournament', icon: '🏆', label: '联赛' },
    { id: 'profile', icon: '👤', label: '我的' }
  ];
</script>

<div class="app">
  <!-- Header -->
  <header class="header">
    <h1 class="title">🎮 Agent Arena</h1>
    <div class="currency">
      <span class="coin">🪙 {game.coins}</span>
      <span class="gem">💎 {game.gems}</span>
    </div>
  </header>

  <!-- Main Content -->
  <main class="main">
    {#if currentTab === 'home'}
      <!-- Home Tab -->
      <div class="home-tab">
        <div class="welcome-section">
          <h2>欢迎来到 Agent Arena!</h2>
          <p>收集、训练、战斗成为最强训练师!</p>
        </div>
        
        <!-- Selected Agent -->
        {#if selectedAgent}
          <div class="selected-agent">
            <h3>当前选中</h3>
            <AgentCard agent={selectedAgent} selected={true} />
          </div>
        {:else}
          <div class="no-agent">
            <p>还没有Agent,快去扭蛋吧!</p>
            <button class="btn btn-primary" on:click={() => currentTab = 'gacha'}>
              去扭蛋
            </button>
          </div>
        {/if}
        
        <!-- Quick Stats -->
        <div class="quick-stats">
          <div class="stat-card">
            <span class="stat-value">{game.agents.length}</span>
            <span class="stat-label">我的Agent</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">{game.stats.totalBattles || 0}</span>
            <span class="stat-label">战斗次数</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">{game.stats.totalWins || 0}</span>
            <span class="stat-label">胜利次数</span>
          </div>
        </div>
        
        <!-- All Agents -->
        {#if game.agents.length > 1}
          <div class="all-agents">
            <h3>所有Agent ({game.agents.length})</h3>
            <div class="agent-grid">
              {#each game.agents as agent}
                <AgentCard 
                  {agent} 
                  selected={agent.id === game.selectedAgentId}
                  compact={true}
                  on:click={() => gameStore.selectAgent(agent.id)}
                />
              {/each}
            </div>
          </div>
        {/if}
        
        <!-- Daily Quests -->
        <div class="quests-section">
          <h3>📋 每日任务</h3>
          {#each game.dailyQuests as quest}
            <div class="quest-item" class:completed={quest.completed}>
              <span class="quest-icon">{quest.icon}</span>
              <div class="quest-info">
                <span class="quest-name">{quest.name}</span>
                <span class="quest-desc">{quest.description}</span>
              </div>
              <div class="quest-progress">
                <span>{quest.progress}/{quest.target}</span>
                {#if quest.completed}
                  <span class="completed-badge">✓</span>
                {:else if quest.reward.coins}
                  <span class="reward">🪙 {quest.reward.coins}</span>
                {:else if quest.reward.gems}
                  <span class="reward">💎 {quest.reward.gems}</span>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      </div>
    
    {:else if currentTab === 'gacha'}
      <Gacha />
    
    {:else if currentTab === 'battle'}
      <Battle />
    
    {:else if currentTab === 'training'}
      <Training />

    {:else if currentTab === 'arena'}
      <ArenaPanel />

    {:else if currentTab === 'tournament'}
      <TournamentTab />

    {:else if currentTab === 'profile'}
      <Profile />
    {/if}
  </main>

  <!-- Bottom Navigation -->
  <nav class="bottom-nav">
    {#each tabs as tab}
      <button 
        class="nav-item" 
        class:active={currentTab === tab.id}
        on:click={() => currentTab = tab.id}
      >
        <span class="nav-icon">{tab.icon}</span>
        <span class="nav-label">{tab.label}</span>
      </button>
    {/each}
  </nav>

  <!-- Notifications -->
  <div class="notifications">
    {#each notifications as notification (notification.id)}
      <div class="notification {notification.type}">
        {notification.message}
      </div>
    {/each}
  </div>
</div>

<style>
  :global(*) {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  :global(body) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    color: #fff;
    min-height: 100vh;
  }

  .app {
    max-width: 480px;
    margin: 0 auto;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: #0f0f23;
  }

  /* Header */
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .title {
    font-size: 1.25rem;
    font-weight: 700;
  }

  .currency {
    display: flex;
    gap: 0.75rem;
  }

  .coin, .gem {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.4rem 0.75rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 1rem;
    font-weight: 600;
    font-size: 0.85rem;
  }

  .gem {
    background: rgba(139, 92, 246, 0.2);
  }

  /* Main */
  .main {
    flex: 1;
    padding: 1rem;
    padding-bottom: 5rem;
    overflow-y: auto;
  }

  /* Home Tab */
  .home-tab {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .welcome-section {
    text-align: center;
    padding: 1.5rem;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
    border-radius: 1rem;
    border: 1px solid rgba(102, 126, 234, 0.3);
  }

  .welcome-section h2 {
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
  }

  .welcome-section p {
    color: #a0a0a0;
    font-size: 0.9rem;
  }

  .selected-agent h3, .all-agents h3, .quests-section h3 {
    font-size: 0.9rem;
    margin-bottom: 0.75rem;
    color: #a0a0a0;
  }

  .no-agent {
    text-align: center;
    padding: 2rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 1rem;
  }

  .no-agent p {
    margin-bottom: 1rem;
    color: #a0a0a0;
  }

  /* Quick Stats */
  .quick-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
  }

  .stat-card {
    text-align: center;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 0.75rem;
  }

  .stat-value {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: #667eea;
  }

  .stat-label {
    font-size: 0.75rem;
    color: #a0a0a0;
  }

  /* Agent Grid */
  .agent-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }

  /* Quests */
  .quest-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 0.75rem;
    margin-bottom: 0.5rem;
  }

  .quest-item.completed {
    opacity: 0.6;
  }

  .quest-icon {
    font-size: 1.5rem;
  }

  .quest-info {
    flex: 1;
  }

  .quest-name {
    display: block;
    font-weight: 600;
    font-size: 0.9rem;
  }

  .quest-desc {
    font-size: 0.75rem;
    color: #a0a0a0;
  }

  .quest-progress {
    text-align: right;
    font-size: 0.85rem;
  }

  .completed-badge {
    color: #10b981;
    font-weight: 700;
  }

  .reward {
    color: #f59e0b;
  }

  /* Bottom Nav */
  .bottom-nav {
    position: fixed;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 480px;
    display: flex;
    justify-content: space-around;
    padding: 0.75rem;
    background: rgba(15, 15, 35, 0.95);
    backdrop-filter: blur(10px);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  .nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    padding: 0.5rem 1rem;
    background: transparent;
    border: none;
    border-radius: 0.75rem;
    cursor: pointer;
    transition: all 0.2s;
    color: #a0a0a0;
  }

  .nav-item.active {
    color: #667eea;
    background: rgba(102, 126, 234, 0.2);
  }

  .nav-icon {
    font-size: 1.25rem;
  }

  .nav-label {
    font-size: 0.7rem;
  }

  /* Notifications */
  .notifications {
    position: fixed;
    top: 4rem;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 480px;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 0 1rem;
    z-index: 1000;
    pointer-events: none;
  }

  .notification {
    padding: 0.75rem 1rem;
    background: rgba(102, 126, 234, 0.9);
    border-radius: 0.5rem;
    text-align: center;
    animation: slideIn 0.3s ease;
  }

  .notification.success {
    background: rgba(16, 185, 129, 0.9);
  }

  .notification.error {
    background: rgba(239, 68, 68, 0.9);
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* Button Styles */
  :global(.btn) {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 0.5rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  :global(.btn-primary) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
  }

  :global(.btn-primary:hover) {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  }

  :global(.btn-secondary) {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  :global(.btn-secondary:hover) {
    background: rgba(255, 255, 255, 0.2);
  }
</style>
