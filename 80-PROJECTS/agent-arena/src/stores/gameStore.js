import { writable, derived, get } from 'svelte/store';

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

    // Add XP to an agent, handle level-ups
    addAgentXP: (agentId, amount) => {
      const state = get({ subscribe });
      const agent = state.agents.find(a => a.id === agentId);
      if (!agent) return { leveledUp: false, newLevel: 0 };

      let currentXP = agent.xp || 0;
      let currentLevel = agent.level || 1;
      let leveledUp = false;

      currentXP += amount;

      // Level threshold: 100 * 1.5^(level-1)
      const levelThreshold = () => Math.floor(100 * Math.pow(1.5, currentLevel - 1));

      while (currentXP >= levelThreshold()) {
        currentXP -= levelThreshold();
        currentLevel++;
        leveledUp = true;
      }

      const updates = { xp: currentXP, level: currentLevel };

      if (leveledUp) {
        updates.stats = {
          intelligence: (agent.stats.intelligence || 0) + 2,
          speed: (agent.stats.speed || 0) + 2,
          creativity: (agent.stats.creativity || 0) + 2,
          endurance: (agent.stats.endurance || 0) + 2,
        };
      }

      update(state => ({
        ...state,
        agents: state.agents.map(a =>
          a.id === agentId ? { ...a, ...updates } : a
        )
      }));

      return { leveledUp, newLevel: currentLevel };
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
    return Math.floor((intelligence * 2 + speed * 1.5 + creativity * 1.8 + endurance * 1.2) * (1 + $agent.level * 0.1));
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
