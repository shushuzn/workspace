<script>
  import { onMount } from 'svelte';
  import { arenaStore } from '../stores/arenaStore.js';
  import { gameStore, selectedAgent } from '../stores/gameStore.js';
  import {
    createTournamentSession,
    createArenaMatch,
    startTournament,
    recordMatchResult,
    getLeaderboard,
    getEloRank,
    formatEloChange
  } from '../game/tournament.js';

  // Tournament state
  let tournament = null;
  let currentView = 'lobby'; // 'lobby' | 'bracket' | 'live' | 'finished'
  let selectedTournamentAgentId = null;
  let liveMatchIndex = -1;
  let battleLog = [];
  let playerHP = 0;
  let enemyHP = 0;
  let playerPower = 0;
  let enemyPower = 0;
  let battleResult = null;
  let battleRound = 0;
  let battleTimer = null;

  $: game = $gameStore;
  $: playerAgent = game.agents.find(a => a.id === selectedTournamentAgentId) || null;
  $: eloRank = playerAgent ? getEloRank(playerAgent.elo || 1000) : null;

  function createNewTournament() {
    tournament = createTournamentSession({
      name: '🏆 联赛杯',
      maxParticipants: 8,
      prize: { coins: 50000, gems: 100 },
      registrationDeadline: Date.now() + 300000, // 5 min for demo
      startTime: Date.now() + 300000
    });
    currentView = 'lobby';
    selectedTournamentAgentId = null;
    liveMatchIndex = -1;
    battleLog = [];
  }

  function registerAgent() {
    if (!playerAgent || !tournament) return;
    const existing = tournament.participants.find(p => p.agentId === playerAgent.id);
    if (existing) return;
    const elo = playerAgent.elo || 1000;
    tournament = {
      ...tournament,
      participants: [
        ...tournament.participants,
        {
          agentId: playerAgent.id,
          agentName: playerAgent.name,
          ownerId: 'local',
          elo,
          registeredAt: Date.now(),
          agent: playerAgent
        }
      ]
    };
  }

  function unregisterAgent(agentId) {
    if (!tournament) return;
    tournament = {
      ...tournament,
      participants: tournament.participants.filter(p => p.agentId !== agentId)
    };
  }

  function selectAgent(agentId) {
    selectedTournamentAgentId = agentId;
    gameStore.selectAgent(agentId);
  }

  function beginTournament() {
    if (!tournament || tournament.participants.length < 2) return;
    tournament = startTournament(tournament);
    currentView = 'bracket';
  }

  function startMatch(index) {
    if (!tournament) return;
    liveMatchIndex = index;
    currentView = 'live';
    const match = tournament.matches[index];
    if (!match) return;

    // Calculate HP
    playerPower = Math.floor(
      (match.player1Agent?.stats?.intelligence * 1.5 || 50) +
      (match.player1Agent?.stats?.speed * 1.2 || 40) +
      (match.player1Agent?.stats?.creativity * 1.0 || 30) +
      (match.player1Agent?.stats?.endurance * 1.8 || 60)
    );
    enemyPower = Math.floor(
      (match.player2Agent?.stats?.intelligence * 1.5 || 50) +
      (match.player2Agent?.stats?.speed * 1.2 || 40) +
      (match.player2Agent?.stats?.creativity * 1.0 || 30) +
      (match.player2Agent?.stats?.endurance * 1.8 || 60)
    );
    playerHP = playerPower * 10;
    enemyHP = enemyPower * 10;
    battleLog = [];
    battleResult = null;
    battleRound = 0;
    runBattle();
  }

  async function runBattle() {
    if (liveMatchIndex < 0) return;
    const match = tournament.matches[liveMatchIndex];
    if (!match) return;

    const p1Speed = match.player1Agent?.stats?.speed || 50;
    const p2Speed = match.player2Agent?.stats?.speed || 50;

    while (playerHP > 0 && enemyHP > 0 && battleRound < 20) {
      battleRound++;
      await new Promise(r => setTimeout(r, 600));

      const playerFirst = p1Speed > p2Speed || (p1Speed === p2Speed && Math.random() > 0.5);

      if (playerFirst) {
        const dmg = Math.floor((playerPower * 0.8 + Math.random() * playerPower * 0.4) * (1 - (match.player2Agent?.stats?.endurance || 50) / 500));
        enemyHP = Math.max(0, enemyHP - dmg);
        battleLog = [...battleLog, { attacker: match.player1Name, damage: dmg, target: match.player2Name, hp: enemyHP }];
        if (enemyHP <= 0) break;
        await new Promise(r => setTimeout(r, 400));
        const dmg2 = Math.floor((enemyPower * 0.8 + Math.random() * enemyPower * 0.4) * (1 - (match.player1Agent?.stats?.endurance || 50) / 500));
        playerHP = Math.max(0, playerHP - dmg2);
        battleLog = [...battleLog, { attacker: match.player2Name, damage: dmg2, target: match.player1Name, hp: playerHP }];
      } else {
        const dmg = Math.floor((enemyPower * 0.8 + Math.random() * enemyPower * 0.4) * (1 - (match.player1Agent?.stats?.endurance || 50) / 500));
        playerHP = Math.max(0, playerHP - dmg);
        battleLog = [...battleLog, { attacker: match.player2Name, damage: dmg, target: match.player1Name, hp: playerHP }];
        if (playerHP <= 0) break;
        await new Promise(r => setTimeout(r, 400));
        const dmg2 = Math.floor((playerPower * 0.8 + Math.random() * playerPower * 0.4) * (1 - (match.player2Agent?.stats?.endurance || 50) / 500));
        enemyHP = Math.max(0, enemyHP - dmg2);
        battleLog = [...battleLog, { attacker: match.player1Name, damage: dmg2, target: match.player2Name, hp: enemyHP }];
      }
    }

    await new Promise(r => setTimeout(r, 500));

    const playerWon = playerHP > 0;
    const winnerId = playerWon ? match.player1Id : match.player2Id;
    battleResult = playerWon ? 'win' : 'lose';

    tournament = recordMatchResult(tournament, match.id, winnerId, playerWon ? 1 : 0, playerWon ? 0 : 1);
    currentView = 'finished';
  }

  function nextMatch() {
    if (!tournament) return;
    const nextPending = tournament.matches.findIndex(m => m.status === 'pending');
    if (nextPending >= 0) {
      liveMatchIndex = nextPending;
      const match = tournament.matches[liveMatchIndex];
      currentView = 'live';
      // Recalculate for new match
      playerPower = Math.floor(
        (match.player1Agent?.stats?.intelligence * 1.5 || 50) +
        (match.player1Agent?.stats?.speed * 1.2 || 40) +
        (match.player1Agent?.stats?.creativity * 1.0 || 30) +
        (match.player1Agent?.stats?.endurance * 1.8 || 60)
      );
      enemyPower = Math.floor(
        (match.player2Agent?.stats?.intelligence * 1.5 || 50) +
        (match.player2Agent?.stats?.speed * 1.2 || 40) +
        (match.player2Agent?.stats?.creativity * 1.0 || 30) +
        (match.player2Agent?.stats?.endurance * 1.8 || 60)
      );
      playerHP = playerPower * 10;
      enemyHP = enemyPower * 10;
      battleLog = [];
      battleResult = null;
      battleRound = 0;
      runBattle();
    } else {
      currentView = 'finished';
    }
  }

  function backToLobby() {
    currentView = 'lobby';
    liveMatchIndex = -1;
    tournament = null;
    battleLog = [];
    battleResult = null;
  }

  // Auto-create tournament on mount
  onMount(() => {
    createNewTournament();
  });

  // Rarity color
  function rarityColor(r) {
    const colors = { common: '#9ca3af', uncommon: '#10b981', rare: '#3b82f6', epic: '#a855f7', legendary: '#f59e0b' };
    return colors[r] || colors.common;
  }
</script>

<div class="tournament-tab">
  {#if currentView === 'lobby'}
    <div class="lobby">
      <div class="tournament-header">
        <h2>🏆 {tournament?.name || '联赛杯'}</h2>
        {#if tournament}
          <div class="tournament-meta">
            <span class="badge">最多{tournament.maxParticipants}人</span>
            <span class="badge prize">🪙 {tournament.prize.coins.toLocaleString()} | 💎 {tournament.prize.gems}</span>
          </div>
          <div class="participant-count">
            已报名: {tournament.participants.length} / {tournament.maxParticipants}
          </div>
        {/if}
      </div>

      <!-- Agent Selection -->
      <div class="section">
        <h3>选择参赛Agent</h3>
        <div class="agent-select-grid">
          {#each game.agents as agent (agent.id)}
            {@const isRegistered = tournament?.participants.some(p => p.agentId === agent.id)}
            {@const myElo = getEloRank(agent.elo || 1000)}
            <div
              class="agent-select-card"
              class:selected={selectedTournamentAgentId === agent.id}
              class:registered={isRegistered}
              on:click={() => selectAgent(agent.id)}
              on:keypress={(e) => e.key === 'Enter' && selectAgent(agent.id)}
              role="button"
              tabindex="0"
            >
              <span class="agent-avatar">{agent.avatar || '🤖'}</span>
              <div class="agent-details">
                <span class="agent-name">{agent.name}</span>
                <span class="agent-elo" style="color: {myElo.color}">Elo: {agent.elo || 1000} {myElo.label}</span>
                <span class="agent-level">Lv.{agent.level}</span>
              </div>
              {#if isRegistered}
                <span class="reg-badge">已报名</span>
              {/if}
            </div>
          {/each}
        </div>
      </div>

      <!-- Registered Participants -->
      {#if tournament && tournament.participants.length > 0}
        <div class="section">
          <h3>已报名列表 ({tournament.participants.length})</h3>
          <div class="participant-list">
            {#each tournament.participants.sort((a,b) => b.elo - a.elo) as p, i}
              <div class="participant-row">
                <span class="rank">#{i+1}</span>
                <span class="p-avatar">{p.agent?.avatar || '🤖'}</span>
                <span class="p-name">{p.agentName}</span>
                <span class="p-elo" style="color: {getEloRank(p.elo).color}">{p.elo}</span>
                {#if p.agentId === selectedTournamentAgentId}
                  <button class="unreg-btn" on:click={() => unregisterAgent(p.agentId)}>取消</button>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      {/if}

      <!-- Actions -->
      <div class="lobby-actions">
        <button class="btn-secondary" on:click={createNewTournament}>新建联赛</button>
        {#if selectedTournamentAgentId}
          <button class="btn-primary" on:click={registerAgent} disabled={tournament?.participants.some(p => p.agentId === selectedTournamentAgentId)}>
            报名参赛
          </button>
        {/if}
        {#if tournament && tournament.participants.length >= 2}
          <button class="btn-start" on:click={beginTournament}>
            开赛! ({tournament.participants.length}人)
          </button>
        {/if}
      </div>
    </div>

  {:else if currentView === 'bracket'}
    <div class="bracket">
      <div class="bracket-header">
        <h2>⚔️ 淘汰赛对阵图</h2>
        <button class="btn-secondary sm" on:click={() => currentView = 'lobby'}>← 返回</button>
      </div>

      <div class="matches-grid">
        {#each tournament.matches as match, i}
          <div class="match-card" class:completed={match.status === 'completed'} class:pending={match.status === 'pending'}>
            <div class="match-num">第{i+1}场</div>
            <div class="match-players">
              <div class="player-row" class:winner={match.winnerId === match.player1Id} class:loser={match.winnerId && match.winnerId !== match.player1Id}>
                <span class="pl-avatar">{match.player1Agent?.avatar || '🤖'}</span>
                <span class="pl-name">{match.player1Name}</span>
                <span class="pl-elo">{match.player1Elo}</span>
                {#if match.status === 'completed'}
                  <span class="pl-result" class:win={match.winnerId === match.player1Id}>胜</span>
                {/if}
              </div>
              <div class="vs-divider">VS</div>
              <div class="player-row" class:winner={match.winnerId === match.player2Id} class:loser={match.winnerId && match.winnerId !== match.player2Id}>
                <span class="pl-avatar">{match.player2Agent?.avatar || '🤖'}</span>
                <span class="pl-name">{match.player2Name}</span>
                <span class="pl-elo">{match.player2Elo}</span>
                {#if match.status === 'completed'}
                  <span class="pl-result" class:win={match.winnerId === match.player2Id}>胜</span>
                {/if}
              </div>
            </div>
            {#if match.status === 'pending'}
              <button class="btn-fight" on:click={() => startMatch(i)}>开战</button>
            {/if}
          </div>
        {/each}
      </div>
    </div>

  {:else if currentView === 'live'}
    <div class="live-battle">
      <div class="battle-hud">
        <div class="fighter player-side">
          <div class="fighter-name">{tournament?.matches[liveMatchIndex]?.player1Name}</div>
          <div class="hp-bar">
            <div class="hp-fill player" style="width: {(playerHP/(playerPower*10))*100}%"></div>
          </div>
          <div class="hp-text">HP: {playerHP}/{playerPower*10}</div>
          <div class="fighter-avatar">{tournament?.matches[liveMatchIndex]?.player1Agent?.avatar}</div>
        </div>
        <div class="vs-live">⚔️</div>
        <div class="fighter enemy-side">
          <div class="fighter-name">{tournament?.matches[liveMatchIndex]?.player2Name}</div>
          <div class="hp-bar">
            <div class="hp-fill enemy" style="width: {(enemyHP/(enemyPower*10))*100}%"></div>
          </div>
          <div class="hp-text">HP: {enemyHP}/{enemyPower*10}</div>
          <div class="fighter-avatar">{tournament?.matches[liveMatchIndex]?.player2Agent?.avatar}</div>
        </div>
      </div>
      <div class="battle-log-live">
        {#each battleLog as entry}
          <div class="log-entry">
            <span class="log-name">{entry.attacker}</span>
            <span class="log-dmg">造成 {entry.damage} 伤害 → {entry.target} (HP: {entry.hp})</span>
          </div>
        {/each}
      </div>
    </div>

  {:else if currentView === 'finished'}
    <div class="finished-view">
      <h2 class="result-title" class:win={battleResult === 'win'} class:lose={battleResult === 'lose'}>
        {battleResult === 'win' ? '🏆 胜利!' : '💀 失败'}
      </h2>
      <div class="match-summary">
        <div class="match-players">
          <div class="player-row">
            <span class="pl-avatar">{tournament?.matches[liveMatchIndex]?.player1Agent?.avatar}</span>
            <span class="pl-name">{tournament?.matches[liveMatchIndex]?.player1Name}</span>
          </div>
          <div class="vs-divider">VS</div>
          <div class="player-row">
            <span class="pl-avatar">{tournament?.matches[liveMatchIndex]?.player2Agent?.avatar}</span>
            <span class="pl-name">{tournament?.matches[liveMatchIndex]?.player2Name}</span>
          </div>
        </div>
      </div>
      <div class="battle-log-summary">
        {#each battleLog as entry}
          <div class="log-entry">{entry.attacker} → {entry.damage} dmg → {entry.target} (HP: {entry.hp})</div>
        {/each}
      </div>

      {#if tournament.status !== 'finished'}
        <button class="btn-next" on:click={nextMatch}>下一场 →</button>
      {:else}
        <div class="champion-section">
          <h3>🏆 联赛冠军</h3>
          {#if tournament.standings[0]}
            <div class="champion-card">
              <span class="champ-avatar">{tournament.standings[0].agent?.avatar || '🏆'}</span>
              <div class="champ-info">
                <span class="champ-name">{tournament.standings[0].agentName}</span>
                <span class="champ-elo" style="color: {getEloRank(tournament.standings[0].elo).color}">
                  Elo: {tournament.standings[0].elo} {getEloRank(tournament.standings[0].elo).label}
                </span>
                <span class="champ-record">{tournament.standings[0].wins}胜 {tournament.standings[0].losses}负</span>
              </div>
            </div>
          {/if}
          <h3>📊 最终排名</h3>
          <div class="standings-table">
            {#each tournament.standings as s, i}
              <div class="standing-row" class:champion={i === 0}>
                <span class="srank">#{i+1}</span>
                <span class="savatar">{s.agent?.avatar || '🤖'}</span>
                <span class="sname">{s.agentName}</span>
                <span class="selo" style="color: {getEloRank(s.elo).color}">{s.elo}</span>
                <span class="srecord">{s.wins}W/{s.losses}L</span>
              </div>
            {/each}
          </div>
          <button class="btn-secondary" on:click={backToLobby}>返回大厅</button>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .tournament-tab { height: 100%; display: flex; flex-direction: column; gap: 1rem; }

  /* Lobby */
  .lobby { display: flex; flex-direction: column; gap: 1rem; }
  .tournament-header { text-align: center; background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(168,85,247,0.2)); border-radius: 1rem; padding: 1rem; border: 1px solid rgba(245,158,11,0.3); }
  .tournament-header h2 { margin: 0 0 0.5rem; }
  .tournament-meta { display: flex; justify-content: center; gap: 0.5rem; margin-bottom: 0.5rem; }
  .badge { background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }
  .badge.prize { color: #f59e0b; }
  .participant-count { color: #888; font-size: 0.85rem; }
  .section { background: rgba(255,255,255,0.03); border-radius: 0.75rem; padding: 0.75rem; }
  .section h3 { font-size: 0.85rem; color: #888; margin-bottom: 0.75rem; }
  .agent-select-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; max-height: 200px; overflow-y: auto; }
  .agent-select-card { background: rgba(255,255,255,0.05); border: 2px solid transparent; border-radius: 0.75rem; padding: 0.5rem; display: flex; align-items: center; gap: 0.5rem; cursor: pointer; position: relative; transition: border-color 0.2s; }
  .agent-select-card:hover { border-color: #667eea; }
  .agent-select-card.selected { border-color: #667eea; background: rgba(102,126,234,0.2); }
  .agent-select-card.registered { border-color: #10b981; }
  .agent-avatar { font-size: 1.5rem; }
  .agent-details { display: flex; flex-direction: column; min-width: 0; }
  .agent-name { font-size: 0.8rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .agent-elo { font-size: 0.65rem; }
  .agent-level { font-size: 0.65rem; color: #888; }
  .reg-badge { position: absolute; top: 2px; right: 4px; font-size: 0.6rem; background: #10b981; color: #fff; padding: 1px 4px; border-radius: 3px; }
  .participant-list { display: flex; flex-direction: column; gap: 0.25rem; max-height: 150px; overflow-y: auto; }
  .participant-row { display: flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0.5rem; background: rgba(255,255,255,0.03); border-radius: 0.5rem; font-size: 0.8rem; }
  .rank { width: 20px; color: #888; font-size: 0.7rem; }
  .p-avatar, .pl-avatar { font-size: 1.2rem; }
  .p-name, .pl-name { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .p-elo, .pl-elo { font-size: 0.7rem; color: #888; }
  .unreg-btn { background: rgba(239,68,68,0.3); border: none; border-radius: 4px; color: #ef4444; font-size: 0.65rem; padding: 2px 6px; cursor: pointer; }
  .lobby-actions { display: flex; gap: 0.5rem; justify-content: center; flex-wrap: wrap; }

  /* Bracket */
  .bracket { display: flex; flex-direction: column; gap: 1rem; }
  .bracket-header { display: flex; justify-content: space-between; align-items: center; }
  .bracket-header h2 { margin: 0; }
  .matches-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 0.75rem; }
  .match-card { background: rgba(255,255,255,0.05); border-radius: 0.75rem; padding: 0.75rem; border: 2px solid rgba(255,255,255,0.1); }
  .match-card.completed { border-color: rgba(16,185,129,0.4); }
  .match-card.pending { border-color: rgba(102,126,234,0.4); }
  .match-num { font-size: 0.7rem; color: #888; margin-bottom: 0.5rem; text-align: center; }
  .match-players { display: flex; flex-direction: column; gap: 0.25rem; }
  .player-row { display: flex; align-items: center; gap: 0.4rem; padding: 0.3rem 0.4rem; border-radius: 0.4rem; font-size: 0.8rem; }
  .player-row.winner { background: rgba(16,185,129,0.2); }
  .player-row.loser { opacity: 0.5; }
  .pl-name { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.75rem; }
  .pl-elo { font-size: 0.65rem; color: #888; }
  .pl-result { font-size: 0.6rem; padding: 1px 4px; border-radius: 3px; background: rgba(239,68,68,0.3); color: #ef4444; }
  .pl-result.win { background: rgba(16,185,129,0.3); color: #10b981; }
  .vs-divider { text-align: center; color: #667eea; font-size: 0.7rem; padding: 0.15rem 0; }
  .btn-fight { width: 100%; margin-top: 0.5rem; padding: 0.4rem; background: linear-gradient(135deg, #ef4444, #dc2626); border: none; border-radius: 0.5rem; color: #fff; font-size: 0.8rem; cursor: pointer; font-weight: 700; }
  .btn-fight:hover { opacity: 0.9; }

  /* Live Battle */
  .live-battle { display: flex; flex-direction: column; gap: 1rem; }
  .battle-hud { display: flex; align-items: center; justify-content: space-around; gap: 1rem; padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 1rem; }
  .fighter { display: flex; flex-direction: column; align-items: center; gap: 0.4rem; flex: 1; }
  .fighter-name { font-weight: 700; font-size: 0.85rem; text-align: center; }
  .fighter-avatar { font-size: 2.5rem; }
  .hp-bar { width: 100%; height: 12px; background: rgba(255,255,255,0.1); border-radius: 6px; overflow: hidden; }
  .hp-fill { height: 100%; transition: width 0.3s; border-radius: 6px; }
  .hp-fill.player { background: linear-gradient(90deg, #10b981, #34d399); }
  .hp-fill.enemy { background: linear-gradient(90deg, #ef4444, #f87171); }
  .hp-text { font-size: 0.7rem; color: #888; }
  .vs-live { font-size: 2rem; font-weight: 900; color: #667eea; }
  .battle-log-live { max-height: 200px; overflow-y: auto; background: rgba(0,0,0,0.2); border-radius: 0.75rem; padding: 0.75rem; display: flex; flex-direction: column; gap: 0.3rem; }
  .log-entry { font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 0.25rem; background: rgba(255,255,255,0.03); }
  .log-name { color: #667eea; font-weight: 600; }
  .log-dmg { color: #ef4444; }

  /* Finished */
  .finished-view { display: flex; flex-direction: column; gap: 1rem; }
  .result-title { text-align: center; font-size: 1.5rem; }
  .result-title.win { color: #10b981; }
  .result-title.lose { color: #ef4444; }
  .match-summary { background: rgba(255,255,255,0.03); border-radius: 0.75rem; padding: 0.75rem; }
  .battle-log-summary { background: rgba(0,0,0,0.2); border-radius: 0.75rem; padding: 0.75rem; max-height: 150px; overflow-y: auto; font-size: 0.75rem; }
  .btn-next { width: 100%; padding: 0.75rem; background: linear-gradient(135deg, #667eea, #764ba2); border: none; border-radius: 0.75rem; color: #fff; font-weight: 700; cursor: pointer; }
  .champion-section { display: flex; flex-direction: column; gap: 0.75rem; }
  .champion-section h3 { text-align: center; font-size: 1rem; color: #f59e0b; }
  .champion-card { display: flex; align-items: center; gap: 1rem; background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(168,85,247,0.2)); border: 2px solid rgba(245,158,11,0.4); border-radius: 1rem; padding: 1rem; }
  .champ-avatar { font-size: 3rem; }
  .champ-info { display: flex; flex-direction: column; gap: 0.2rem; }
  .champ-name { font-size: 1.1rem; font-weight: 700; }
  .champ-elo { font-size: 0.85rem; }
  .champ-record { font-size: 0.75rem; color: #888; }
  .standings-table { display: flex; flex-direction: column; gap: 0.25rem; }
  .standing-row { display: flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0.75rem; background: rgba(255,255,255,0.03); border-radius: 0.5rem; font-size: 0.8rem; }
  .standing-row.champion { background: rgba(245,158,11,0.15); border: 1px solid rgba(245,158,11,0.3); }
  .srank { width: 24px; font-size: 0.7rem; color: #888; }
  .savatar { font-size: 1.1rem; }
  .sname { flex: 1; }
  .selo { font-size: 0.7rem; }
  .srecord { font-size: 0.7rem; color: #888; }

  /* Buttons */
  .btn-primary { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; border: none; padding: 0.6rem 1.2rem; border-radius: 0.6rem; cursor: pointer; font-weight: 600; font-size: 0.85rem; }
  .btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
  .btn-secondary { background: rgba(255,255,255,0.1); color: #fff; border: 1px solid rgba(255,255,255,0.2); padding: 0.6rem 1.2rem; border-radius: 0.6rem; cursor: pointer; font-size: 0.85rem; }
  .btn-secondary.sm { padding: 0.4rem 0.8rem; font-size: 0.75rem; }
  .btn-start { background: linear-gradient(135deg, #10b981, #059669); color: #fff; border: none; padding: 0.6rem 1.2rem; border-radius: 0.6rem; cursor: pointer; font-weight: 700; font-size: 0.9rem; }
</style>
