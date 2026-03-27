import { writable, get } from 'svelte/store';

const ARENA_HISTORY_KEY = 'arena_history';
const MAX_HISTORY = 20;

function loadHistory() {
  try {
    const raw = localStorage.getItem(ARENA_HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveHistory(history) {
  try {
    localStorage.setItem(ARENA_HISTORY_KEY, JSON.stringify(history));
  } catch (e) {
    console.warn('Failed to save arena history:', e);
  }
}

function createArenaStore() {
  const { subscribe, set, update } = writable({
    stage: 'STAGE_SELECT',  // 'STAGE_SELECT' | 'STAGE_LOADING' | 'STAGE_REVEAL' | 'STAGE_BATTLE' | 'STAGE_RESULT' | 'STAGE_HISTORY'
    currentOpponent: null,
    selectedArenaAgentId: null,
    history: loadHistory(),
  });

  return {
    subscribe,

    setStage: (stage) => update(s => ({ ...s, stage })),

    setSelectedAgent: (id) => update(s => ({ ...s, selectedArenaAgentId: id })),

    setCurrentOpponent: (opponent) => update(s => ({ ...s, currentOpponent: opponent })),

    nextStage: () => {
      const stages = ['STAGE_SELECT', 'STAGE_LOADING', 'STAGE_REVEAL', 'STAGE_BATTLE', 'STAGE_RESULT'];
      update(s => {
        const idx = stages.indexOf(s.stage);
        return { ...s, stage: stages[Math.min(idx + 1, stages.length - 1)] };
      });
    },

    addToHistory: (opponent) => {
      update(s => {
        const newHistory = [opponent, ...s.history].slice(0, MAX_HISTORY);
        saveHistory(newHistory);
        return { ...s, history: newHistory };
      });
    },

    loadHistory: () => {
      const history = loadHistory();
      update(s => ({ ...s, history }));
    },

    reset: () => update(s => ({
      ...s,
      stage: 'STAGE_SELECT',
      currentOpponent: null,
      selectedArenaAgentId: null,
    })),

    getState: () => get({ subscribe }),
  };
}

export const arenaStore = createArenaStore();
