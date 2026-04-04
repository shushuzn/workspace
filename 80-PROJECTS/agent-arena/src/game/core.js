/**
 * Agent Arena - 游戏核心引擎
 * 包含所有游戏逻辑和状态管理
 */

// ============================================
// 常量定义
// ============================================

export const RARITIES = {
  COMMON: { id: 'common', name: '普通', color: 'var(--rarity-common)', multiplier: 1 },
  RARE: { id: 'rare', name: '稀有', color: 'var(--rarity-rare)', multiplier: 1.5 },
  EPIC: { id: 'epic', name: '史诗', color: 'var(--rarity-epic)', multiplier: 2 },
  LEGENDARY: { id: 'legendary', name: '传说', color: 'var(--rarity-legendary)', multiplier: 3 }
};

export const STATS = {
  INTELLIGENCE: { id: 'intelligence', name: '智力', emoji: '🧠', color: 'var(--stat-intelligence)' },
  SPEED: { id: 'speed', name: '速度', emoji: '⚡', color: 'var(--stat-speed)' },
  CREATIVITY: { id: 'creativity', name: '创造力', emoji: '💡', color: 'var(--stat-creativity)' },
  ENDURANCE: { id: 'endurance', name: '耐力', emoji: '💪', color: 'var(--stat-endurance)' }
};

export const TRAINING_TYPES = {
  STUDY: { id: 'study', name: '读书', emoji: '📚', stat: 'intelligence', cost: 100, gain: 5 },
  RUN: { id: 'run', name: '跑步', emoji: '🏃', stat: 'speed', cost: 100, gain: 5 },
  BRAINSTORM: { id: 'brainstorm', name: '头脑风暴', emoji: '💭', stat: 'creativity', cost: 100, gain: 5 },
  MEDITATE: { id: 'meditate', name: '冥想', emoji: '🧘', stat: 'endurance', cost: 100, gain: 5 }
};

export const BATTLE_MODES = {
  ARENA: { id: 'arena', name: '竞技场', emoji: '⚔️', reward: 500, difficulty: 1 },
  TOURNAMENT: { id: 'tournament', name: '锦标赛', emoji: '🏆', reward: 2000, difficulty: 2 },
  BOSS: { id: 'boss', name: 'Boss战', emoji: '👹', reward: 5000, difficulty: 3 }
};

export const EVOLUTION_STAGES = ['普通', '进阶', '精英', '传说', '神话'];

// Agent 名字库
const FIRST_NAMES = ['Nova', 'Cipher', 'Pulse', 'Nexus', 'Flux', 'Apex', 'Void', 'Zenith', 'Echo', 'Byte', 'Node', 'Spark', 'Core', 'Loop', 'Wave'];
const LAST_NAMES = ['Alpha', 'Prime', 'Ultra', 'Hyper', 'Omega', 'Delta', 'Sigma', 'Theta', 'Kappa', 'Gamma', 'Neo', 'Meta', 'Crypto', 'Data', 'Pixel'];

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

export function generateAgentName() {
  return `${randomChoice(FIRST_NAMES)} ${randomChoice(LAST_NAMES)}`;
}

export function generateStats(rarity) {
  const base = rarity === 'legendary' ? 30 : rarity === 'epic' ? 20 : rarity === 'rare' ? 15 : 10;
  const variance = 10;
  return {
    intelligence: base + randomInt(0, variance),
    speed: base + randomInt(0, variance),
    creativity: base + randomInt(0, variance),
    endurance: base + randomInt(0, variance)
  };
}

export function formatNumber(num) {
  if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
  if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
  if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
  if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
  return Math.floor(num).toString();
}

// ============================================
// Agent 生成
// ============================================

export function createAgent(overrides = {}) {
  const rarity = overrides.rarity || randomChoice(Object.keys(RARITIES)).toLowerCase();
  const baseStats = generateStats(rarity);
  
  return {
    id: generateId(),
    name: generateAgentName(),
    avatar: randomChoice(['🤖', '🦊', '🐉', '🦅', '🦁', '🐺', '🦅', '🐲', '🦉', '�豹']),
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
    createdAt: Date.now(),
    ...overrides
  };
}

function generateSkills(rarity) {
  const skillPool = [
    { id: 'quick-attack', name: '快攻', effect: { stat: 'speed', bonus: 0.1 }, emoji: '⚡', unlocked: false },
    { id: 'power-hit', name: '重击', effect: { stat: 'intelligence', bonus: 0.15 }, emoji: '💥', unlocked: false },
    { id: 'critical-eye', name: '致命打击', effect: { critChance: 0.1 }, emoji: '🎯', unlocked: false },
    { id: 'endure', name: '坚韧', effect: { stat: 'endurance', bonus: 0.1 }, emoji: '🛡️', unlocked: false },
    { id: 'creative-surge', name: '创意爆发', effect: { stat: 'creativity', bonus: 0.15 }, emoji: '💡', unlocked: false },
    { id: 'first-strike', name: '先发制人', effect: { firstStrike: true }, emoji: '🔥', unlocked: false }
  ];

  const unlockCount = rarity === 'legendary' ? 4 : rarity === 'epic' ? 3 : rarity === 'rare' ? 2 : 1;
  
  return skillPool
    .sort(() => Math.random() - 0.5)
    .slice(0, unlockCount)
    .map(s => ({ ...s, unlocked: true }));
}

// ============================================
// 游戏状态管理
// ============================================

class GameState {
  constructor() {
    this.listeners = new Set();
    this.state = this.getInitialState();
  }

  getInitialState() {
    return {
      coins: 1000,
      gems: 10,
      agents: [],
      currentAgentId: null,
      activeTab: 'agents',
      battleLog: [],
      dailyQuests: this.generateDailyQuests(),
      achievements: [],
      settings: {
        soundEnabled: true,
        musicEnabled: true,
        theme: 'dark'
      },
      stats: {
        totalBattles: 0,
        totalWins: 0,
        totalCoinsEarned: 0,
        playTime: 0,
        startTime: Date.now()
      },
      lastSaveTime: Date.now()
    };
  }

  generateDailyQuests() {
    return [
      { id: 'q1', name: '首胜', description: '赢得一场战斗', target: 1, progress: 0, reward: { coins: 500 }, completed: false },
      { id: 'q2', name: '训练达人', description: '训练10次', target: 10, progress: 0, reward: { coins: 300 }, completed: false },
      { id: 'q3', name: '收藏家', description: '拥有3个Agent', target: 3, progress: 0, reward: { gems: 5 }, completed: false },
      { id: 'q4', name: '连胜', description: '连续赢得3场战斗', target: 3, progress: 0, reward: { coins: 1000 }, completed: false }
    ];
  }

  updateQuestProgress(questId, amount = 1) {
    this.update(state => {
      const quests = state.dailyQuests.map(q => {
        if (q.id !== questId || q.completed) return q;
        const progress = Math.min(q.progress + amount, q.target);
        return { ...q, progress, completed: progress >= q.target };
      });
      return { dailyQuests: quests };
    });
  }

  addExp(agentId, amount) {
    this.updateAgent(agentId, agent => {
      if (!agent) return agent;
      const exp = (agent.exp || 0) + amount;
      const expToLevel = agent.expToLevel || 100;
      if (exp >= expToLevel) {
        return {
          ...agent,
          exp: exp - expToLevel,
          level: (agent.level || 1) + 1,
          expToLevel: Math.floor(expToLevel * 1.5)
        };
      }
      return { ...agent, exp };
    });
  }

  getState() {
    return this.state;
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notify() {
    this.listeners.forEach(listener => listener(this.state));
  }

  update(updater) {
    this.state = updater(this.state);
    this.notify();
  }

  // ============================================
  // Agent 操作
  // ============================================

  addAgent(agent) {
    this.update(state => ({
      ...state,
      agents: [...state.agents, agent],
      currentAgentId: state.currentAgentId || agent.id
    }));
  }

  updateAgent(agentId, updates) {
    this.update(state => ({
      ...state,
      agents: state.agents.map(a => a.id === agentId ? { ...a, ...updates } : a)
    }));
  }

  removeAgent(agentId) {
    this.update(state => {
      const newAgents = state.agents.filter(a => a.id !== agentId);
      return {
        ...state,
        agents: newAgents,
        currentAgentId: state.currentAgentId === agentId 
          ? (newAgents[0]?.id || null) 
          : state.currentAgentId
      };
    });
  }

  getCurrentAgent() {
    return this.state.agents.find(a => a.id === this.state.currentAgentId);
  }

  // ============================================
  // 资源操作
  // ============================================

  addCoins(amount) {
    this.update(state => ({
      ...state,
      coins: state.coins + amount,
      stats: {
        ...state.stats,
        totalCoinsEarned: state.stats.totalCoinsEarned + amount
      }
    }));
  }

  spendCoins(amount) {
    if (this.state.coins < amount) return false;
    this.update(state => ({ ...state, coins: state.coins - amount }));
    return true;
  }

  addGems(amount) {
    this.update(state => ({ ...state, gems: state.gems + amount }));
  }

  spendGems(amount) {
    if (this.state.gems < amount) return false;
    this.update(state => ({ ...state, gems: state.gems - amount }));
    return true;
  }

  // ============================================
  // 训练系统
  // ============================================

  startTraining(agentId, trainingType) {
    const training = Object.values(TRAINING_TYPES).find(t => t.id === trainingType);
    if (!training) return false;
    
    if (!this.spendCoins(training.cost)) return false;

    this.updateAgent(agentId, {
      isInTraining: true,
      trainingType: trainingType,
      trainingStartTime: Date.now(),
      trainingEndTime: Date.now() + 30000 // 30秒训练
    });

    return true;
  }

  completeTraining(agentId) {
    const agent = this.state.agents.find(a => a.id === agentId);
    if (!agent || !agent.isInTraining) return null;

    const training = Object.values(TRAINING_TYPES).find(t => t.id === agent.trainingType);
    if (!training) return null;

    if (Date.now() < agent.trainingEndTime) return null;

    const statGain = training.gain * RARITIES[agent.rarity.toUpperCase()]?.multiplier || 1;

    this.updateAgent(agentId, {
      isInTraining: false,
      trainingType: null,
      trainingStartTime: null,
      trainingEndTime: null,
      stats: {
        ...agent.stats,
        [training.stat]: agent.stats[training.stat] + statGain
      }
    });

    // 更新每日任务
    this.updateQuestProgress('q2', 1);

    return { stat: training.stat, gain: statGain };
  }

  // ============================================
  // 战斗系统
  // ============================================

  calculatePower(agent) {
    const rarityMult = RARITIES[agent.rarity.toUpperCase()]?.multiplier || 1;
    const stageMult = 1 + agent.evolutionStage * 0.25;
    const levelMult = 1 + (agent.level - 1) * 0.1;

    let stats = { ...agent.stats };
    
    // 计算技能加成
    agent.skills?.forEach(skill => {
      if (skill.unlocked && skill.effect.stat) {
        stats[skill.effect.stat] *= (1 + (skill.effect.bonus || 0));
      }
    });

    const total = stats.intelligence + stats.speed + stats.creativity + stats.endurance;
    return Math.floor(total * rarityMult * stageMult * levelMult);
  }

  battle(attackerId, defenderId) {
    const attacker = this.state.agents.find(a => a.id === attackerId);
    const defender = this.state.agents.find(a => a.id === defenderId);

    if (!attacker || !defender) return { success: false, error: 'Agent不存在' };

    let attackerPower = this.calculatePower(attacker);
    let defenderPower = this.calculatePower(defender);

    // 先发制人技能
    if (attacker.skills?.some(s => s.id === 'first-strike' && s.unlocked)) {
      defenderPower *= 0.9;
    }
    if (defender.skills?.some(s => s.id === 'first-strike' && s.unlocked)) {
      attackerPower *= 0.9;
    }

    // 致命打击暴击
    let critBonus = 1;
    if (attacker.skills?.some(s => s.id === 'critical-eye' && s.unlocked)) {
      if (Math.random() < 0.1) critBonus = 1.5;
    }

    attackerPower *= critBonus;

    // 计算结果
    const roll = Math.random() * (attackerPower + defenderPower);
    const attackerWins = roll < attackerPower;

    const result = {
      success: true,
      winner: attackerWins ? attacker : defender,
      loser: attackerWins ? defender : attacker,
      attackerPower,
      defenderPower,
      timestamp: Date.now()
    };

    // 更新 Agent 状态
    this.updateAgent(result.winner.id, { 
      wins: result.winner.wins + 1,
      totalEarned: result.winner.totalEarned + 250
    });
    this.updateAgent(result.loser.id, { losses: result.loser.losses + 1 });

    // 添加经验
    this.addExp(result.winner.id, 50);
    if (attackerWins) {
      this.addExp(result.loser.id, 20);
    }

    // 奖励
    this.addCoins(250);

    // 更新统计
    this.update(state => ({
      ...state,
      stats: {
        ...state.stats,
        totalBattles: state.stats.totalBattles + 1,
        totalWins: state.stats.totalWins + (attackerWins ? 1 : 0)
      },
      battleLog: [result, ...state.battleLog].slice(0, 50)
    }));

    // 更新每日任务
    this.updateQuestProgress('q1', 1);

    return result;
  }

  battleAI(opponentLevel) {
    const agent = this.getCurrentAgent();
    if (!agent) return { success: false, error: '没有选中的Agent' };

    // 生成AI对手
    const aiStats = {
      intelligence: opponentLevel * 10,
      speed: opponentLevel * 10,
      creativity: opponentLevel * 10,
      endurance: opponentLevel * 10
    };

    const aiAgent = {
      ...createAgent({ 
        rarity: opponentLevel > 20 ? 'epic' : opponentLevel > 10 ? 'rare' : 'common',
        stats: aiStats
      }),
      name: `挑战者 Lv.${opponentLevel}`
    };

    let playerPower = this.calculatePower(agent);
    let aiPower = this.calculatePower(aiAgent);

    // 添加随机性 (±20%)
    playerPower *= 0.8 + Math.random() * 0.4;
    aiPower *= 0.8 + Math.random() * 0.4;

    const roll = Math.random() * (playerPower + aiPower);
    const playerWins = roll < playerPower;

    const reward = Math.floor(100 * opponentLevel * (playerWins ? 1 : 0.1));

    const result = {
      success: true,
      playerWins,
      opponent: aiAgent,
      playerPower: Math.floor(playerPower),
      aiPower: Math.floor(aiPower),
      reward,
      timestamp: Date.now()
    };

    this.addCoins(reward);
    
    if (playerWins) {
      this.addExp(agent.id, 30 * opponentLevel);
      this.updateQuestProgress('q1', 1);
    }

    this.update(state => ({
      ...state,
      stats: {
        ...state.stats,
        totalBattles: state.stats.totalBattles + 1,
        totalWins: state.stats.totalWins + (playerWins ? 1 : 0)
      }
    }));

    return result;
  }
}
