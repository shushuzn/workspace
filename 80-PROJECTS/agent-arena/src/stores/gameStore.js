import { writable, derived, get } from 'svelte/store';
import { calculatePower, createAgent, evolveAgent } from '../game/agentFactory.js';

// Initial state - matches game.js structure
const initialState = {
  coins: 1000,
  gems: 10,
  agents: [],
  selectedAgentId: null,
  activeTab: 'home',
  battleLog: [],
  stats: {
    totalBattles: 0,
    totalWins: 0,
    totalCoinsEarned: 0,
    playTime: 0,
    startTime: Date.now()
  },
  settings: {
    soundEnabled: true,
    musicEnabled: true
  },
  notifications: [],
  showModal: null,
  modalData: null
};

// Create the store
function createGameStore() {
  const { subscribe, set, update } = writable({ ...initialState });

  // Notification store
  const notifications = writable([]);

  function addNotification(message, type = 'info') {
    const id = Date.now();
    notifications.update(n => [...n, { id, message, type }]);
    setTimeout(() => {
      notifications.update(n => n.filter(item => item.id !== id));
    }, 3000);
  }

  return {
    subscribe,
    set,
    update,

    // Notifications
    notifications: { subscribe: notifications.subscribe },
    notify: (message, type = 'info') => {
      if (typeof message === 'object' && message.message) {
        addNotification(message.message, message.type || 'info');
      } else {
        addNotification(message, type);
      }
    },

    // Get entire state
    getState: () => get({ subscribe }),

    // Set entire state (for import)
    setState: (data) => set({ ...initialState, ...data }),

    // Add a new agent
    addAgent: (agent) => {
      update(state => ({
        ...state,
        agents: [...state.agents, agent]
      }));
    },

    // Remove an agent by ID
    removeAgent: (id) => {
      update(state => ({
        ...state,
        agents: state.agents.filter(a => a.id !== id)
      }));
    },

    // Select an agent
    selectAgent: (id) => {
      update(state => ({
        ...state,
        selectedAgentId: id
      }));
    },

    // Update a specific agent
    updateAgent: (id, updates) => {
      update(state => ({
        ...state,
        agents: state.agents.map(agent =>
          agent.id === id ? { ...agent, ...updates } : agent
        )
      }));
    },

    // Add XP to an agent, handle level-ups, call evolveAgent on level-up
    addAgentXP: (agentId, amount) => {
      const state = get({ subscribe });
      const agent = state.agents.find(a => a.id === agentId);
      if (!agent) return { leveledUp: false, newLevel: 0 };

      // Use exp field (consistent with agentFactory.createAgent)
      let currentExp = agent.exp ?? agent.xp ?? 0;
      let currentLevel = agent.level || 1;
      let leveledUp = false;

      currentExp += amount;

      // Level threshold: 100 * 1.5^(level-1)
      const levelThreshold = () => Math.floor(100 * Math.pow(1.5, currentLevel - 1));

      while (currentExp >= levelThreshold()) {
        currentExp -= levelThreshold();
        currentLevel++;
        leveledUp = true;
      }

      const updates = { exp: currentExp, level: currentLevel };

      if (leveledUp) {
        // Call evolveAgent from agentFactory to get proper stat bonuses
        const evolved = evolveAgent({ ...agent, level: currentLevel, exp: currentExp });
        if (evolved) {
          updates.stats = evolved.stats;
          updates.power = evolved.power;
        }
      }

      update(state => ({
        ...state,
        agents: state.agents.map(a =>
          a.id === agentId ? { ...a, ...updates } : a
        )
      }));

      return { leveledUp, newLevel: currentLevel };
    },

    // Battle against AI opponent (by level)
    battleAI: (agentId, opponentLevel) => {
      const state = get({ subscribe });
      const agent = state.agents.find(a => a.id === agentId);
      if (!agent) return { success: false, error: '没有选中的Agent' };

      // Generate AI opponent stats
      const aiStats = {
        intelligence: opponentLevel * 10,
        speed: opponentLevel * 10,
        creativity: opponentLevel * 10,
        endurance: opponentLevel * 10
      };

      // AI rarity scales with level
      const aiRarity = opponentLevel > 50 ? 'epic' : opponentLevel > 25 ? 'rare' : 'uncommon';

      const aiAgent = {
        ...createAgent({ rarity: aiRarity }),
        name: `挑战者 Lv.${opponentLevel}`,
        stats: aiStats,
        power: calculatePower(aiStats),
        level: opponentLevel
      };

      let playerPower = calculatePower(agent.stats);
      let aiPower = calculatePower(aiStats);

      // Add ±20% randomness
      playerPower *= 0.8 + Math.random() * 0.4;
      aiPower *= 0.8 + Math.random() * 0.4;

      const roll = Math.random() * (playerPower + aiPower);
      const playerWins = roll < playerPower;

      const reward = Math.floor(100 * opponentLevel * (playerWins ? 1 : 0.1));

      // Update agent XP on win
      if (playerWins) {
        const xpGain = 30 * opponentLevel;
        const xpResult = gameStore.addAgentXP(agentId, xpGain);
      }

      update(s => ({
        ...s,
        coins: s.coins + reward,
        stats: {
          ...s.stats,
          totalBattles: (s.stats.totalBattles || 0) + 1,
          totalWins: (s.stats.totalWins || 0) + (playerWins ? 1 : 0)
        }
      }));

      return {
        success: true,
        playerWins,
        opponent: aiAgent,
        playerPower: Math.floor(playerPower),
        aiPower: Math.floor(aiPower),
        reward,
        timestamp: Date.now()
      };
    },

    // Spend coins (returns false if not enough)
    spendCoins: (amount) => {
      const state = get({ subscribe });
      if (state.coins < amount) return false;
      update(s => ({ ...s, coins: s.coins - amount }));
      return true;
    },

    // Add coins
    addCoins: (amount) => {
      update(state => ({ ...state, coins: state.coins + amount }));
    },

    // Spend gems (returns false if not enough)
    spendGems: (amount) => {
      const state = get({ subscribe });
      if (state.gems < amount) return false;
      update(s => ({ ...s, gems: s.gems - amount }));
      return true;
    },

    // Add gems
    addGems: (amount) => {
      update(state => ({ ...state, gems: state.gems + amount }));
    },

    // Set active tab
    setTab: (tab) => {
      update(state => ({ ...state, activeTab: tab }));
    }
  };
}

export const gameStore = createGameStore();

// Derived stores for convenience
export const selectedAgent = derived(
  gameStore,
  $game => $game.agents.find(a => a.id === $game.selectedAgentId) || null
);

export const agentPower = derived(
  selectedAgent,
  $agent => {
    if (!$agent) return 0;
    const { intelligence, speed, creativity, endurance } = $agent.stats;
    // Power formula matches agentFactory.calculatePower: I*1.5 + S*1.2 + C*1.0 + E*1.8
    return Math.floor((intelligence * 1.5 + speed * 1.2 + creativity * 1.0 + endurance * 1.8) * (1 + $agent.level * 0.1));
  }
);

export const winRate = derived(
  gameStore,
  $game => {
    const stats = $game.stats || {};
    const total = stats.totalBattles || 0;
    if (total === 0) return 0;
    return Math.round((stats.totalWins || 0) / total * 100);
  }
);
