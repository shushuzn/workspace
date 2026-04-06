/**
 * Agent Arena — Battle Analytics
 * Tracks and serializes battle statistics for analysis and RL training.
 */

import { get } from 'svelte/store';
import { gameStore } from '../stores/gameStore.js';

const MAX_HISTORY = 200;

function createBattleAnalytics() {
  const store = gameStore;

  function recordBattle(result) {
    const entry = {
      id: Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
      timestamp: result.timestamp || Date.now(),
      type: result.playerWins !== undefined ? 'ai' : 'pvp',
      winnerId: result.winner?.id ?? result.playerWins ? result.opponent?.id : null,
      winnerName: result.winner?.name ?? result.opponent?.name ?? 'unknown',
      loserId: result.loser?.id ?? null,
      loserName: result.loser?.name ?? null,
      attackerPower: result.attackerPower ?? result.playerPower ?? 0,
      defenderPower: result.defenderPower ?? result.aiPower ?? 0,
      reward: result.reward ?? 0,
      skillsUsed: [],
      turnsElapsed: result.turns ?? 1,
    };

    store.update(state => ({
      ...state,
      battleAnalytics: {
        history: [entry, ...(state.battleAnalytics?.history ?? [])].slice(0, MAX_HISTORY),
        totalBattles: (state.battleAnalytics?.totalBattles ?? 0) + 1,
        totalWins: (state.battleAnalytics?.totalWins ?? 0) + (result.playerWins ? 1 : result.winner ? 1 : 0),
        totalLosses: (state.battleAnalytics?.totalLosses ?? 0) + (result.playerWins === false ? 1 : 0),
        skillFrequency: state.battleAnalytics?.skillFrequency ?? {},
        powerHistory: [...(state.battleAnalytics?.powerHistory ?? []), entry.attackerPower + entry.defenderPower].slice(-100),
      },
    }));

    return entry;
  }

  function getStats() {
    const state = get(store);
    const a = state.battleAnalytics ?? {};
    const history = a.history ?? [];

    // Win rate by agent
    const agentStats = {};
    for (const e of history) {
      if (!e.winnerId && !e.loserId) continue;
      for (const [id, name] of [[e.winnerId, e.winnerName], [e.loserId, e.loserName]]) {
        if (!id) continue;
        if (!agentStats[id]) agentStats[id] = { id, name, wins: 0, losses: 0, totalPower: 0, battles: 0 };
        if (id === e.winnerId) agentStats[id].wins++;
        else agentStats[id].losses++;
        agentStats[id].totalPower += id === e.winnerId ? e.attackerPower : e.defenderPower;
        agentStats[id].battles++;
      }
    }

    // Skill frequency
    const skillFreq = a.skillFrequency ?? {};

    // Average battle length
    const avgTurns = history.length
      ? history.reduce((s, e) => s + (e.turnsElapsed ?? 1), 0) / history.length
      : 0;

    return {
      total: a.totalBattles ?? 0,
      wins: a.totalWins ?? 0,
      losses: a.totalLosses ?? 0,
      winRate: a.totalBattles ? ((a.totalWins ?? 0) / a.totalBattles * 100).toFixed(1) + '%' : '—',
      avgTurns: avgTurns.toFixed(1),
      skillFrequency: skillFreq,
      agentStats: Object.values(agentStats).sort((a, b) => b.wins - a.wins),
      recentHistory: history.slice(0, 20),
    };
  }

  function exportCSV() {
    const state = get(store);
    const history = state.battleAnalytics?.history ?? [];
    if (!history.length) return '';

    const headers = ['id', 'timestamp', 'type', 'winnerId', 'winnerName', 'loserId', 'loserName', 'attackerPower', 'defenderPower', 'reward', 'turns'];
    const rows = history.map(e => headers.map(h => JSON.stringify(e[h] ?? '')).join(','));
    return [headers.join(','), ...rows].join('\n');
  }

  function toJSON() {
    const state = get(store);
    return state.battleAnalytics ?? { history: [], totalBattles: 0, totalWins: 0, totalLosses: 0 };
  }

  return { recordBattle, getStats, exportCSV, toJSON };
}

export const battleAnalytics = createBattleAnalytics();
