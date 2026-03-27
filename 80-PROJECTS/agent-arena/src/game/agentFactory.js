import { RARITIES, AVATARS, NAME_PREFIXES, NAME_SUFFIXES } from './constants.js';

// 生成唯一ID
export function generateId() {
  return 'agent_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// 计算属性点
export function calculateBaseStats(rarity) {
  const rarityConfig = RARITIES[rarity.toUpperCase()];
  const basePoints = 20;
  const bonusPoints = Math.floor(basePoints * (rarityConfig?.multiplier || 1));
  
  const total = basePoints + bonusPoints;
  
  return {
    intelligence: Math.floor(total * (0.8 + Math.random() * 0.4)),
    speed: Math.floor(total * (0.8 + Math.random() * 0.4)),
    creativity: Math.floor(total * (0.8 + Math.random() * 0.4)),
    endurance: Math.floor(total * (0.8 + Math.random() * 0.4))
  };
}

// 计算战力
export function calculatePower(stats) {
  return (
    (stats.intelligence || 0) * 1.5 +
    (stats.speed || 0) * 1.2 +
    (stats.creativity || 0) * 1.0 +
    (stats.endurance || 0) * 1.8
  );
}

// 生成Agent名字
function generateName(forced = null) {
  if (forced) return forced;
  
  const prefix = NAME_PREFIXES[Math.floor(Math.random() * NAME_PREFIXES.length)];
  const suffix = NAME_SUFFIXES[Math.floor(Math.random() * NAME_SUFFIXES.length)];
  
  return `${prefix}${suffix}`;
}

// 获取随机头像
export function getRandomAvatar() {
  return AVATARS[Math.floor(Math.random() * AVATARS.length)];
}

// 获取稀有度样式
export function getRarityStyle(rarity) {
  const config = RARITIES[rarity.toUpperCase()];
  if (!config) return RARITIES.COMMON;
  return {
    color: config.color,
    bg: config.bg,
    border: config.border,
    name: config.name
  };
}

// 创建Agent
export function createAgent({ rarity = 'common', name = null, autoName = false } = {}) {
  const id = generateId();
  const stats = calculateBaseStats(rarity);
  const power = calculatePower(stats);
  
  // 如果是自动命名或没有提供名字，生成随机名字
  const finalName = autoName || !name 
    ? generateName(name) 
    : name;
  
  const agent = {
    id,
    name: finalName,
    avatar: getRandomAvatar(),
    rarity,
    level: 1,
    experience: 0,
    stats,
    power,
    createdAt: Date.now(),
    isInTraining: false,
    trainingType: null,
    trainingEndTime: null,
    trainingConfig: null
  };
  
  return agent;
}

// 进化Agent
export function evolveAgent(agent) {
  const currentLevel = agent.level;
  const maxLevel = 100;
  
  if (currentLevel >= maxLevel) {
    return null; // 已经满级
  }
  
  const bonusStats = {
    intelligence: Math.floor(agent.stats.intelligence * 0.2),
    speed: Math.floor(agent.stats.speed * 0.2),
    creativity: Math.floor(agent.stats.creativity * 0.2),
    endurance: Math.floor(agent.stats.endurance * 0.2)
  };
  
  const evolvedStats = {
    intelligence: agent.stats.intelligence + bonusStats.intelligence,
    speed: agent.stats.speed + bonusStats.speed,
    creativity: agent.stats.creativity + bonusStats.creativity,
    endurance: agent.stats.endurance + bonusStats.endurance
  };
  
  return {
    ...agent,
    level: agent.level + 1,
    stats: evolvedStats,
    power: calculatePower(evolvedStats),
    experience: 0
  };
}

// 获取进化阶段
export function getEvolutionStage(level) {
  if (level < 20) return 1;
  if (level < 40) return 2;
  if (level < 60) return 3;
  if (level < 80) return 4;
  return 5;
}

// 经验条计算
export function getExpProgress(currentExp, level) {
  const expNeeded = Math.floor(100 * Math.pow(1.5, level - 1));
  return {
    current: currentExp,
    needed: expNeeded,
    percentage: Math.min(100, (currentExp / expNeeded) * 100)
  };
}

// 稀有度概率
export function getGachaOdds(type = 'single') {
  const odds = {
    common: 50,
    uncommon: 30,
    rare: 15,
    epic: 4,
    legendary: 0.9,
    mythic: 0.1
  };
  
  if (type === 'ten') {
    odds.common = 45;
    odds.rare = 20;
  } else if (type === 'legend') {
    odds.legendary = 30;
    odds.epic = 40;
    odds.rare = 25;
    odds.uncommon = 5;
  }
  
  return odds;
}

// 选择扭蛋结果
export function selectGachaRarity(type = 'single') {
  const odds = getGachaOdds(type);
  const rand = Math.random() * 100;
  let cumulative = 0;
  
  for (const [rarity, chance] of Object.entries(odds)) {
    cumulative += chance;
    if (rand < cumulative) {
      return rarity;
    }
  }
  
  return 'common';
}
