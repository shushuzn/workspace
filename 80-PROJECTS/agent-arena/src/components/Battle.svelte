<script>
  import { gameStore } from '../stores/gameStore.js';
  import { BATTLE_LEVELS } from '../game/constants.js';
  import { createAgent, calculatePower } from '../game/agentFactory.js';
  import AgentCard from './AgentCard.svelte';
  
  let selectedLevel = 0;
  let battleState = 'idle';
  let playerAgent = null;
  let enemyAgent = null;
  let battleLog = [];
  let battleResult = null;
  let battleReward = 0;
  let isAutoBattle = false;
  
  $: state = $gameStore;
  $: player = state.agents.find(a => a.id === state.selectedAgentId);
  $: currentLevel = BATTLE_LEVELS[selectedLevel];
  
  function startBattle() {
    if (!player) {
      if (typeof gameStore.notify === 'function') {
        gameStore.notify({ message: '请先选择一个Agent!', type: 'error' });
      }
      return;
    }

    battleState = 'preparing';
    playerAgent = { ...player };
    battleLog = [];

    const enemyRarity = getEnemyRarity(selectedLevel);
    enemyAgent = createAgent({ rarity: enemyRarity });

    enemyAgent.level = Math.max(1, player.level - 2 + Math.floor(Math.random() * 5));
    const levelMultiplier = 1 + (enemyAgent.level - 1) * 0.1;
    enemyAgent.stats = {
      intelligence: Math.floor(enemyAgent.stats.intelligence * levelMultiplier * currentLevel.multiplier),
      speed: Math.floor(enemyAgent.stats.speed * levelMultiplier * currentLevel.multiplier),
      creativity: Math.floor(enemyAgent.stats.creativity * levelMultiplier * currentLevel.multiplier),
      endurance: Math.floor(enemyAgent.stats.endurance * levelMultiplier * currentLevel.multiplier)
    };
    enemyAgent.power = calculatePower(enemyAgent.stats);
    playerAgent.power = calculatePower(playerAgent.stats);

    setTimeout(() => {
      battleState = 'fighting';
      runBattle();
    }, 1500);
  }

  function startAutoBattle() {
    isAutoBattle = true;
    battleState = 'preparing';
    battleLog = [];

    const rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic'];
    const rarity1 = rarities[Math.floor(Math.random() * rarities.length)];
    const rarity2 = rarities[Math.floor(Math.random() * rarities.length)];

    playerAgent = createAgent({ rarity: rarity1, autoName: true });
    enemyAgent = createAgent({ rarity: rarity2, autoName: true });

    playerAgent.level = Math.floor(Math.random() * 20) + 1;
    enemyAgent.level = Math.floor(Math.random() * 20) + 1;

    playerAgent.power = calculatePower(playerAgent.stats);
    enemyAgent.power = calculatePower(enemyAgent.stats);

    setTimeout(() => {
      battleState = 'fighting';
      runAutoBattle();
    }, 1500);
  }

  let autoBattleTimer = null;

  function stopAutoBattle() {
    isAutoBattle = false;
    if (autoBattleTimer) {
      clearTimeout(autoBattleTimer);
      autoBattleTimer = null;
    }
    resetBattle();
  }

  async function runAutoBattle() {
    const playerPower = playerAgent.power;
    const enemyPower = enemyAgent.power;

    let playerHP = playerPower * 10;
    let enemyHP = enemyPower * 10;
    const playerSpeed = playerAgent.stats.speed;
    const enemySpeed = enemyAgent.stats.speed;

    let round = 0;
    const maxRounds = 20;

    while (playerHP > 0 && enemyHP > 0 && round < maxRounds) {
      if (!isAutoBattle) break;
      round++;
      await new Promise(resolve => setTimeout(resolve, 600));

      const playerFirst = playerSpeed > enemySpeed ? true : (playerSpeed === enemySpeed ? Math.random() > 0.5 : false);

      if (playerFirst) {
        const damage1 = Math.floor((playerPower * 0.8 + Math.random() * playerPower * 0.4) * (1 - enemyAgent.stats.endurance / 500));
        enemyHP = Math.max(0, enemyHP - damage1);
        battleLog = [...battleLog, { round, attacker: 'player', damage: damage1, targetHP: enemyHP, message: `🤖 ${playerAgent.name} 造成 ${damage1} 点伤害!` }];

        if (enemyHP <= 0) break;
        await new Promise(resolve => setTimeout(resolve, 400));

        const damage2 = Math.floor((enemyPower * 0.8 + Math.random() * enemyPower * 0.4) * (1 - playerAgent.stats.endurance / 500));
        playerHP = Math.max(0, playerHP - damage2);
        battleLog = [...battleLog, { round, attacker: 'enemy', damage: damage2, targetHP: playerHP, message: `🤖 ${enemyAgent.name} 造成 ${damage2} 点伤害!` }];
      } else {
        const damage1 = Math.floor((enemyPower * 0.8 + Math.random() * enemyPower * 0.4) * (1 - playerAgent.stats.endurance / 500));
        playerHP = Math.max(0, playerHP - damage1);
        battleLog = [...battleLog, { round, attacker: 'enemy', damage: damage1, targetHP: playerHP, message: `🤖 ${enemyAgent.name} 造成 ${damage1} 点伤害!` }];

        if (playerHP <= 0) break;
        await new Promise(resolve => setTimeout(resolve, 400));

        const damage2 = Math.floor((playerPower * 0.8 + Math.random() * playerPower * 0.4) * (1 - enemyAgent.stats.endurance / 500));
        enemyHP = Math.max(0, enemyHP - damage2);
        battleLog = [...battleLog, { round, attacker: 'player', damage: damage2, targetHP: enemyHP, message: `🤖 ${playerAgent.name} 造成 ${damage2} 点伤害!` }];
      }
    }

    await new Promise(resolve => setTimeout(resolve, 500));

    const playerWon = playerHP > 0;
    battleResult = playerWon ? 'win' : 'lose';

    battleLog = [...battleLog, { round: round + 1, message: playerWon ? `🏆 ${playerAgent.name} 获胜!` : `🏆 ${enemyAgent.name} 获胜!` }];

    battleState = 'result';

    if (isAutoBattle) {
      autoBattleTimer = setTimeout(() => startAutoBattle(), 3000);
    }
  }
  
  function getEnemyRarity(level) {
    const rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary'];
    return rarities[Math.min(level, rarities.length - 1)];
  }
  
  async function runBattle() {
    const playerPower = playerAgent.power;
    const enemyPower = enemyAgent.power;
    
    let playerHP = playerPower * 10;
    let enemyHP = enemyPower * 10;
    const playerSpeed = playerAgent.stats.speed;
    const enemySpeed = enemyAgent.stats.speed;
    
    let round = 0;
    const maxRounds = 20;
    
    while (playerHP > 0 && enemyHP > 0 && round < maxRounds) {
      round++;
      await new Promise(resolve => setTimeout(resolve, 600));
      
      const playerFirst = playerSpeed > enemySpeed ? true : (playerSpeed === enemySpeed ? Math.random() > 0.5 : false);
      
      if (playerFirst) {
        const damage1 = Math.floor((playerPower * 0.8 + Math.random() * playerPower * 0.4) * (1 - enemyAgent.stats.endurance / 500));
        enemyHP = Math.max(0, enemyHP - damage1);
        battleLog = [...battleLog, { round, attacker: 'player', damage: damage1, targetHP: enemyHP, message: `🎯 你的Agent造成 ${damage1} 点伤害!` }];
        
        if (enemyHP <= 0) break;
        await new Promise(resolve => setTimeout(resolve, 400));
        
        const damage2 = Math.floor((enemyPower * 0.8 + Math.random() * enemyPower * 0.4) * (1 - playerAgent.stats.endurance / 500));
        playerHP = Math.max(0, playerHP - damage2);
        battleLog = [...battleLog, { round, attacker: 'enemy', damage: damage2, targetHP: playerHP, message: `⚔️ 敌人造成 ${damage2} 点伤害!` }];
      } else {
        const damage1 = Math.floor((enemyPower * 0.8 + Math.random() * enemyPower * 0.4) * (1 - playerAgent.stats.endurance / 500));
        playerHP = Math.max(0, playerHP - damage1);
        battleLog = [...battleLog, { round, attacker: 'enemy', damage: damage1, targetHP: playerHP, message: `⚔️ 敌人造成 ${damage1} 点伤害!` }];
        
        if (playerHP <= 0) break;
        await new Promise(resolve => setTimeout(resolve, 400));
        
        const damage2 = Math.floor((playerPower * 0.8 + Math.random() * playerPower * 0.4) * (1 - enemyAgent.stats.endurance / 500));
        enemyHP = Math.max(0, enemyHP - damage2);
        battleLog = [...battleLog, { round, attacker: 'player', damage: damage2, targetHP: enemyHP, message: `🎯 你的Agent造成 ${damage2} 点伤害!` }];
      }
    }
    
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const playerWon = playerHP > 0;
    battleResult = playerWon ? 'win' : 'lose';
    
    if (playerWon) {
      battleReward = Math.floor(currentLevel.reward * (1 + player.level * 0.1));
      gameStore.update(state => ({
        ...state,
        coins: state.coins + battleReward,
        stats: { ...state.stats, totalBattles: (state.stats.totalBattles || 0) + 1, totalWins: (state.stats.totalWins || 0) + 1 }
      }));
      battleLog = [...battleLog, { round: round + 1, message: `🏆 胜利! 获得 ${battleReward} 金币!` }];
      if (typeof gameStore.notify === 'function') {
        gameStore.notify({ message: `🏆 胜利! +${battleReward}金币`, type: 'success' });
      }
    } else {
      gameStore.update(state => ({
        ...state,
        stats: { ...state.stats, totalBattles: (state.stats.totalBattles || 0) + 1 }
      }));
      battleLog = [...battleLog, { round: round + 1, message: `💀 失败...再来一次吧!` }];
    }
    
    battleState = 'result';
  }
  
  function resetBattle() {
    battleState = 'idle';
    playerAgent = null;
    enemyAgent = null;
    battleLog = [];
    battleResult = null;
    battleReward = 0;
  }
</script>

<div class="battle-container">
  <div class="battle-header">
    <h2>⚔️ 战斗竞技场</h2>
    <p>选择难度,挑战强敌!</p>
  </div>
  
  {#if battleState === 'idle'}
    <div class="level-selection">
      <h3>选择难度</h3>
      <div class="levels-grid">
        {#each BATTLE_LEVELS as level, i}
          <button class="level-card" class:selected={selectedLevel === i} on:click={() => selectedLevel = i}>
            <span class="level-name">{level.name}</span>
            <span class="level-req">需要 Lv.{level.level}+</span>
            <span class="level-multiplier">x{level.multiplier}</span>
            <span class="level-reward">🪙 {level.reward}</span>
          </button>
        {/each}
      </div>
    </div>
    
    {#if player}
      <div class="preview-section">
        <h3>你的Agent</h3>
        <AgentCard agent={player} />
      </div>
      <button class="start-btn" on:click={startBattle}>开始战斗</button>
    {:else}
      <div class="no-agent"><p>请先在首页选择一个Agent出战!</p></div>
    {/if}

    <div class="auto-battle-section">
      {#if isAutoBattle}
        <button class="auto-battle-btn stop" on:click={stopAutoBattle}>⏹ 停止观战</button>
      {:else}
        <button class="auto-battle-btn" on:click={startAutoBattle}>🤖 AI vs AI 自动战斗</button>
        <p class="auto-battle-hint">观看两个AI随机Agent自动对战</p>
      {/if}
    </div>
    
  {:else if battleState === 'preparing'}
    <div class="preparing">
      <div class="vs-container">
        <div class="player-side">
          {#if playerAgent}<AgentCard agent={playerAgent} />{/if}
        </div>
        <div class="vs-text">VS</div>
        <div class="enemy-side preparing-enemy">
          <div class="loading-avatar">?</div>
          <p>敌人准备中...</p>
        </div>
      </div>
    </div>
    
  {:else if battleState === 'fighting'}
    <div class="battle-arena">
      <div class="fighters">
        <div class="fighter player-fighter"><h4>你的Agent</h4><AgentCard agent={playerAgent} /></div>
        <div class="fighter enemy-fighter"><h4>敌人</h4><AgentCard agent={enemyAgent} /></div>
      </div>
      <div class="battle-log">
        {#each battleLog as entry}
          <div class="log-entry {entry.attacker || ''}">
            <span class="round">回合{entry.round}</span>
            <span class="message">{entry.message}</span>
          </div>
        {/each}
      </div>
    </div>
    
  {:else if battleState === 'result'}
    <div class="result-screen {battleResult}">
      <h2 class="result-title">{battleResult === 'win' ? '🏆 胜利!' : '💀 失败'}</h2>
      <div class="fighters">
        <div class="fighter"><h4>你的Agent</h4><AgentCard agent={playerAgent} /></div>
        <div class="fighter"><h4>敌人</h4><AgentCard agent={enemyAgent} /></div>
      </div>
      {#if battleResult === 'win'}
        <div class="reward-display"><span>获得奖励:</span><span class="reward-amount">🪙 {battleReward}</span></div>
      {/if}
      <button class="start-btn" on:click={resetBattle}>再来一局</button>
    </div>
  {/if}
</div>

<style>
  .battle-container { display: flex; flex-direction: column; gap: 1.5rem; }
  .battle-header { text-align: center; padding: 1rem; background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%); border-radius: 1rem; border: 1px solid rgba(239, 68, 68, 0.3); }
  .battle-header h2 { font-size: 1.25rem; margin-bottom: 0.25rem; }
  .battle-header p { font-size: 0.85rem; color: #a0a0a0; }
  .level-selection h3 { font-size: 0.9rem; color: #a0a0a0; margin-bottom: 0.75rem; }
  .levels-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; }
  .level-card { display: flex; flex-direction: column; align-items: center; padding: 1rem; background: rgba(255, 255, 255, 0.05); border: 2px solid rgba(255, 255, 255, 0.1); border-radius: 1rem; cursor: pointer; transition: all 0.2s; }
  .level-card:hover { border-color: #667eea; }
  .level-card.selected { border-color: #667eea; background: rgba(102, 126, 234, 0.2); }
  .level-name { font-weight: 700; font-size: 1rem; margin-bottom: 0.25rem; }
  .level-req { font-size: 0.7rem; color: #a0a0a0; }
  .level-multiplier { font-size: 0.85rem; color: #ef4444; font-weight: 600; margin: 0.25rem 0; }
  .level-reward { font-size: 0.8rem; color: #f59e0b; }
  .preview-section h3 { font-size: 0.9rem; color: #a0a0a0; margin-bottom: 0.75rem; }
  .no-agent { text-align: center; padding: 2rem; background: rgba(255, 255, 255, 0.05); border-radius: 1rem; color: #a0a0a0; }
  .start-btn { width: 100%; padding: 1rem; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); border: none; border-radius: 1rem; color: #fff; font-weight: 700; font-size: 1.1rem; cursor: pointer; transition: all 0.2s; }
  .start-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4); }
  .preparing { text-align: center; }
  .vs-container { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
  .player-side, .enemy-side { flex: 1; }
  .vs-text { font-size: 2rem; font-weight: 700; color: #667eea; }
  .loading-avatar { width: 80px; height: 80px; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; background: rgba(255, 255, 255, 0.1); border-radius: 50%; border: 2px dashed #667eea; animation: pulse 1s infinite; }
  @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
  .battle-arena { display: flex; flex-direction: column; gap: 1rem; }
  .fighters { display: flex; gap: 1rem; }
  .fighter { flex: 1; text-align: center; }
  .fighter h4 { font-size: 0.85rem; color: #a0a0a0; margin-bottom: 0.5rem; }
  .battle-log { max-height: 200px; overflow-y: auto; background: rgba(0, 0, 0, 0.3); border-radius: 1rem; padding: 1rem; }
  .log-entry { padding: 0.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1); font-size: 0.85rem; }
  .log-entry:last-child { border-bottom: none; }
  .log-entry .round { display: inline-block; width: 60px; color: #a0a0a0; font-size: 0.75rem; }
  .log-entry.player .message { color: #10b981; }
  .log-entry.enemy .message { color: #ef4444; }
  .result-screen { text-align: center; }
  .result-title { font-size: 2rem; margin-bottom: 1rem; }
  .result-screen.win .result-title { color: #10b981; }
  .result-screen.lose .result-title { color: #ef4444; }
  .reward-display { display: flex; justify-content: center; gap: 0.5rem; padding: 1rem; background: rgba(245, 158, 11, 0.2); border-radius: 1rem; margin: 1rem 0; font-size: 1.1rem; }
  .reward-amount { color: #f59e0b; font-weight: 700; }
  .auto-battle-section { margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.1); text-align: center; }
  .auto-battle-btn { width: 100%; padding: 0.75rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; border-radius: 0.75rem; color: #fff; font-weight: 600; font-size: 1rem; cursor: pointer; transition: all 0.2s; }
  .auto-battle-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }
  .auto-battle-btn.stop { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
  .auto-battle-hint { font-size: 0.75rem; color: #a0a0a0; margin-top: 0.5rem; }
</style>
