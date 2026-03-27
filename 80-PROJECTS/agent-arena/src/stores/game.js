/**
 * Svelte Store - 游戏状态管理
 */
import { writable, derived } from 'svelte/store';

// ============================================
// 常量
// ============================================

export const RARITIES = {
  COMMON: { id: 'common', name: '普通', color: '#9CA3AF', multiplier: 1, bg: 'rgba(156, 163, 175, 0.1)' },
  RARE: { id: 'rare', name: '稀有', color: '#60A5FA', multiplier: 1.5, bg: 'rgba(96, 165, 250, 0.1)' },
  EPIC: { id: 'epic', name: '史诗', color: '#A78BFA', multiplier: 2, bg: 'rgba(167, 139, 250, 0.1)' },
  LEGENDARY: { id: 'legendary', name: '传说', color: '#FBBF24', multiplier: 3, bg: 'rgba(251, 191, 36, 0.15)' }
};

export const STATS = {
  INTELLIGENCE: { id: 'intelligence', name: '智力', emoji: '🧠', color: '#60A5FA' },
  SPEED: { id: 'speed', name: '速度', emoji: '⚡', color: '#34D399' },
  CREATIVITY: { id: 'creativity', name: '创造力', emoji: '💡', color: '#F472B6' },
  ENDURANCE: { id: 'endurance', name: '耐力', emoji: '💪', color: '#FB923C' }
};

export const TRAINING_TYPES = {
  STUDY: { id: 'study', name: '读书', emoji: '📚', stat: 'intelligence', cost: 100, gain: 5, duration: 30000 },
  RUN: { id: 'run', name: '跑步', emoji: '🏃', stat: 'speed', cost: 100, gain: 5, duration: 30000 },
  BRAINSTORM: { id: 'brainstorm', name: '头脑风暴', emoji: '💭', stat: 'creativity', cost: 100, gain: 5, duration: 30000 },
  MEDITATE: { id: 'meditate', name: '冥想', emoji: '🧘', stat: 'endurance', cost: 100, gain: 5, duration: 30000 }
};

export const EVOLUTION_STAGES = ['普通', '进阶', '精英', '传说', '神话'];

// ============================================
// 工具函数
// ============================================

export function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
}

export function randomChoice(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

export function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

export function formatNumber(num) {
  if (num >= 1e12) return (num / 1e12).toFixed(1) + 'T';
  if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
  if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
  if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
  return Math.floor(num).toString();
}

// ============================================
// Agent 生成
// ============================================

const FIRST_NAMES = ['Nova', 'Cipher', 'Pulse', 'Nexus', 'Flux', 'Apex', 'Void', 'Zenith', 'Echo', 'Byte', 'Node', 'Spark', 'Core', 'Loop', 'Wave', 'Prism', 'Cipher', 'Nexus'];
const LAST_NAMES = ['Alpha', 'Prime', 'Ultra', 'Hyper', 'Omega', 'Delta', 'Sigma', 'Theta', 'Kappa', 'Gamma', 'Neo', 'Meta', 'Crypto', 'Data', 'Pixel', 'Vector', 'Quantum', 'Vector'];
const AVATARS = ['🤖', '🦊', '🐉', '🦅', '🦁', '🐺', '🦉', '🐲', '🦄', '🐲', '🦊', '🐺', '🤖', '🦅', '🦁', '🦉', '🐉', '🦄'];

export function generateAgentName() {
  return `${randomChoice(FIRST_NAMES)} ${randomChoice(LAST_NAMES)}`;
}

export function generateStats(rarity) {
  const base = RARITIES[rarity.toUpperCase()]?.multiplier || 1;
  const baseValue = base > 2 ? 40 : base > 1 ? 30 : 20;
  const variance = 15;
  return {
    intelligence: Math.floor((baseValue + randomInt(0, variance)) * base),
    speed: Math.floor((baseValue + randomInt(0, variance)) * base),
    creativity: Math.floor((baseValue + randomInt(0, variance)) * base),
    endurance: Math.floor((baseValue + randomInt(0, variance)) * base)
  };
}

export function createAgent(overrides = {}) {
  const rarity = overrides.rarity || randomChoice(Object.keys(RARITIES)).toLowerCase();
  const baseStats = generateStats(rarity);
  
  return {
    id: generateId(),
    name: overrides.name || generateAgentName(),
    avatar: overrides.avatar || randomChoice(AVATARS),
    level: 1,
    exp: 0,
    expToLevel: 100,
    rarity: rarity,
    evolutionStage: 0,
    stats: {
      intelligence: overrides.stats?.intelligence ?? baseStats.intelligence,
      speed: overrides.stats?.speed ?? baseStats.speed,
      creativity: overrides.stats?.creativity ?? baseStats.creativity,
      endurance: overrides.stats?.endurance ?? baseStats.endurance
    },
    skills: generateSkills(rarity),
    wins: 0,
    losses: 0,
    totalEarned: 0,
    isInTraining: false,
    trainingStartTime: null,
    trainingEndTime: null,
    trainingType: null,
    createdAt: Date.now(),
    ...overrides
  };
}

function generateSkills(rarity) {
  const skillPool = [
    { id: 'quick-attack', name: '快攻', effect: { stat: 'speed', bonus: 0.15 }, emoji: '⚡', unlocked: true },
    { id: 'power-hit', name: '重击', effect: { stat: 'intelligence', bonus: 0.2 }, emoji: '💥', unlocked: true },
    { id: 'critical-eye', name: '致命打击', effect: { critChance: 0.12 }, emoji: '🎯', unlocked: true },
    { id: 'endure', name: '坚韧', effect: { stat: 'endurance', bonus: 0.15 }, emoji: '🛡️', unlocked: true },
    { id: 'creative-surge', name: '创意爆发', effect: { stat: 'creativity', bonus: 0.2 }, emoji: '💡', unlocked: true },
    { id: 'first-strike', name: '先发制人', effect: { firstStrike: true, bonus: 0.1 }, emoji: '🔥', unlocked: true }
  ];

  const unlockCount = rarity === 'legendary' ? 4 : rarity === 'epic' ? 3 : rarity === 'rare' ? 2 : 1;
  
  return skillPool
    .sort(() => Math.random() - 0.5)
    .slice(0, unlockCount)
    .map(s => ({ ...s }));
}

// ============================================
// 游戏状态
// ============================================

function createGameStore() {
  const { subscribe, set, update } = writable({
    coins: 1000,
    gems: 10,
    agents: [],
    selectedAgentId: null,
    activeTab: 'home',
    battleLog: [],
    dailyQuests: generateDailyQuests(),
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
  });

  return {
    subscribe,

    // 初始化 - 添加一个默认Agent
    init() {
      update(state => {
        if (state.agents.length === 0) {
          const starterAgent = createAgent({
            name: 'Nova Prime',
            rarity: 'rare',
            stats: { intelligence: 45, speed: 50, creativity: 42, endurance: 48 }
          });
          return {
            ...state,
            agents: [starterAgent],
            selectedAgentId: starterAgent.id
          };
        }
        return state;
      });
    },

    // Agent 操作
    addAgent(agent) {
      update(state => ({
        ...state,
        agents: [...state.agents, agent]
      }));
    },

    updateAgent(agentId, updates) {
      update(state => ({
        ...state,
        agents: state.agents.map(a => a.id === agentId ? { ...a, ...updates } : a)
      }));
    },

    removeAgent(agentId) {
      update(state => {
        const newAgents = state.agents.filter(a => a.id !== agentId);
        return {
          ...state,
          agents: newAgents,
          selectedAgentId: state.selectedAgentId === agentId 
            ? (newAgents[0]?.id || null) 
            : state.selectedAgentId
        };
      });
    },

    selectAgent(agentId) {
      update(state => ({ ...state, selectedAgentId: agentId }));
    },

    // 资源操作
    addCoins(amount) {
      update(state => ({
        ...state,
        coins: state.coins + amount,
        stats: {
          ...state.stats,
          totalCoinsEarned: state.stats.totalCoinsEarned + amount
        }
      }));
    },

    spendCoins(amount) {
      let success = false;
      update(state => {
        if (state.coins >= amount) {
          success = true;
          return { ...state, coins: state.coins - amount };
        }
        return state;
      });
      return success;
    },

    addGems(amount) {
      update(state => ({ ...state, gems: state.gems + amount }));
    },

    spendGems(amount) {
      let success = false;
      update(state => {
        if (state.gems >= amount) {
          success = true;
          return { ...state, gems: state.gems - amount };
        }
        return state;
      });
      return success;
    },

    // 训练系统
    startTraining(agentId, trainingType) {
      const training = Object.values(TRAINING_TYPES).find(t => t.id === trainingType);
      if (!training) return false;
      
      if (!this.spendCoins(training.cost)) return false;

      this.updateAgent(agentId, {
        isInTraining: true,
        trainingType: trainingType,
        trainingStartTime: Date.now(),
        trainingEndTime: Date.now() + training.duration
      });

      return true;
    },

    completeTraining(agentId) {
      let result = null;
      update(state => {
        const agent = state.agents.find(a => a.id === agentId);
        if (!agent || !agent.isInTraining) return state;

        if (Date.now() < agent.trainingEndTime) return state;

        const training = Object.values(TRAINING_TYPES).find(t => t.id === agent.trainingType);
        if (!training) return state;

        const rarity = RARITIES[agent.rarity.toUpperCase()];
        const statGain = Math.floor(training.gain * (rarity?.multiplier || 1));

        result = { stat: training.stat, gain: statGain };

        return {
          ...state,
          agents: state.agents.map(a => a.id === agentId ? {
            ...a,
            isInTraining: false,
            trainingType: null,
            trainingStartTime: null,
            trainingEndTime: null,
            stats: {
              ...a.stats,
              [training.stat]: a.stats[training.stat] + statGain
            }
          } : a)
        };
      });
      return result;
    },

    // 经验与升级
    addExp(agentId, amount) {
      update(state => ({
        ...state,
        agents: state.agents.map(a => {
          if (a.id !== agentId) return a;
          
          let newExp = a.exp + amount;
          let newLevel = a.level;
          let newExpToLevel = a.expToLevel;
          let stats = { ...a.stats };

          // 检查升级
          while (newExp >= newExpToLevel) {
            newExp -= newExpToLevel;
            newLevel++;
            newExpToLevel = Math.floor(newExpToLevel * 1.5);
            
            // 升级时全属性提升
            const growthBonus = 5 + (newLevel * 2);
            stats.intelligence += growthBonus;
            stats.speed += growthBonus;
            stats.creativity += growthBonus;
            stats.endurance += growthBonus;
          }

          return { ...a, exp: newExp, level: newLevel, expToLevel: newExpToLevel, stats };
        })
      }));
    },

    // 战斗系统
    calculatePower(agent) {
      const rarity = RARITIES[agent.rarity.toUpperCase()];
      const rarityMult = rarity?.multiplier || 1;
      const stageMult = 1 + agent.evolutionStage * 0.25;
      const levelMult = 1 + (agent.level - 1) * 0.1;

      let stats = { ...agent.stats };
      
      agent.skills?.forEach(skill => {
        if (skill.unlocked && skill.effect.stat) {
          stats[skill.effect.stat] *= (1 + (skill.effect.bonus || 0));
        }
      });

      const total = stats.intelligence + stats.speed + stats.creativity + stats.endurance;
      return Math.floor(total * rarityMult * stageMult * levelMult);
    },

    battleAI(opponentLevel = 1) {
      let result = null;
      
      update(state => {
        const agent = state.agents.find(a => a.id === state.selectedAgentId);
        if (!agent) return state;

        // 生成AI对手
        const aiStats = {
          intelligence: 15 * opponentLevel,
          speed: 15 * opponentLevel,
          creativity: 15 * opponentLevel,
          endurance: 15 * opponentLevel
        };

        const aiAgent = createAgent({ 
          rarity: opponentLevel > 20 ? 'epic' : opponentLevel > 10 ? 'rare' : 'common',
          name: `挑战者 Lv.${opponentLevel}`,
          stats: aiStats,
          level: opponentLevel
        });

        let playerPower = this.calculatePower(agent);
        let aiPower = this.calculatePower(aiAgent);

        // 添加随机性 (±30%)
        playerPower = Math.floor(playerPower * (0.7 + Math.random() * 0.6));
        aiPower = Math.floor(aiPower * (0.7 + Math.random() * 0.6));

        const totalPower = playerPower + aiPower;
        const roll = Math.random() * totalPower;
        const playerWins = roll < playerPower;

        const reward = Math.floor(100 * opponentLevel * (playerWins ? 1 : 0.2));
        const expGain = Math.floor(30 * opponentLevel * (playerWins ? 1 : 0.3));

        result = {
          success: true,
          playerWins,
          opponent: aiAgent,
          playerPower,
          aiPower,
          reward,
          expGain,
          opponentLevel
        };

        return {
          ...state,
          coins: state.coins + reward,
          stats: {
            ...state.stats,
            totalBattles: state.stats.totalBattles + 1,
            totalWins: state.stats.totalWins + (playerWins ? 1 : 0)
          },
          battleLog: [result, ...state.battleLog].slice(0, 20)
        };
      });

      // 添加经验
      if (result?.playerWins) {
        const state = await new Promise(resolve => {
          const unsub = this.subscribe(s => {
            resolve(s);
            unsub();
          });
        });
        this.addExp(state.selectedAgentId, result.expGain);
      }

      return result;
    },

    // UI 状态
    setTab(tab) {
      update(state => ({ ...state, activeTab: tab }));
    },

    showModal(type, data = null) {
      update(state => ({ ...state, showModal: type, modalData: data }));
    },

    hideModal() {
      update(state => ({ ...state, showModal: null, modalData: null }));
    },

    notify(message, type = 'info') {
      const id = generateId();
      update(state => ({
        ...state,
        notifications: [...state.notifications, { id, message, type }]
      }));
      
      setTimeout(() => {
        update(state => ({
          ...state,
          notifications: state.notifications.filter(n => n.id !== id)
        }));
      }, 3000);
    }
  };
}

function generateDailyQuests() {
  return [
    { id: 'q1', name: '首胜', description: '赢得一场战斗', target: 1, progress: 0, reward: { coins: 500 }, completed: false },
    { id: 'q2', name: '训练达人', description: '完成5次训练', target: 5, progress: 0, reward: { coins: 300 }, completed: false },
    { id: 'q3', name: '收藏家', description: '拥有3个Agent', target: 3, progress: 0, reward: { gems: 5 }, completed: false },
    { id: 'q4', name: '连胜', description: