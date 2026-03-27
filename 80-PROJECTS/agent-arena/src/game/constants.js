// 稀有度配置
export const RARITIES = {
  COMMON: {
    id: 'common',
    name: '普通',
    color: '#9ca3af',
    bg: 'rgba(156, 163, 175, 0.2)',
    border: '#4b5563',
    multiplier: 1,
    probability: 50
  },
  UNCOMMON: {
    id: 'uncommon',
    name: '优秀',
    color: '#10b981',
    bg: 'rgba(16, 185, 129, 0.2)',
    border: '#059669',
    multiplier: 1.2,
    probability: 30
  },
  RARE: {
    id: 'rare',
    name: '稀有',
    color: '#3b82f6',
    bg: 'rgba(59, 130, 246, 0.2)',
    border: '#2563eb',
    multiplier: 1.5,
    probability: 15
  },
  EPIC: {
    id: 'epic',
    name: '史诗',
    color: '#a855f7',
    bg: 'rgba(168, 85, 247, 0.2)',
    border: '#9333ea',
    multiplier: 2,
    probability: 4,
    probabilityText: '4%'
  },
  LEGENDARY: {
    id: 'legendary',
    name: '传说',
    color: '#f59e0b',
    bg: 'rgba(245, 158, 11, 0.2)',
    border: '#d97706',
    multiplier: 3,
    probability: 0.9
  },
  MYTHIC: {
    id: 'mythic',
    name: '神话',
    color: '#ef4444',
    bg: 'rgba(239, 68, 68, 0.2)',
    border: '#dc2626',
    multiplier: 5,
    probability: 0.1
  }
};

// 属性配置
export const STATS = {
  intelligence: {
    id: 'intelligence',
    name: '智力',
    emoji: '🧠',
    color: '#8b5cf6'
  },
  speed: {
    id: 'speed',
    name: '速度',
    emoji: '⚡',
    color: '#06b6d4'
  },
  creativity: {
    id: 'creativity',
    name: '创造力',
    emoji: '💡',
    color: '#f59e0b'
  },
  endurance: {
    id: 'endurance',
    name: '耐力',
    emoji: '💪',
    color: '#10b981'
  }
};

// 进化阶段
export const EVOLUTION_STAGES = {
  1: '🌱 幼年期',
  2: '🌿 成长期',
  3: '🌳 成熟期',
  4: '⭐ 觉醒期',
  5: '👑 完全体'
};

// 训练类型
export const TRAINING_TYPES = {
  intelligence: {
    id: 'intelligence',
    name: '智力训练',
    stat: 'intelligence',
    emoji: '🧠',
    duration: 30000,
    cost: 50,
    gain: 5
  },
  speed: {
    id: 'speed',
    name: '速度训练',
    stat: 'speed',
    emoji: '⚡',
    duration: 30000,
    cost: 50,
    gain: 5
  },
  creativity: {
    id: 'creativity',
    name: '创造力训练',
    stat: 'creativity',
    emoji: '💡',
    duration: 30000,
    cost: 50,
    gain: 5
  },
  endurance: {
    id: 'endurance',
    name: '耐力训练',
    stat: 'endurance',
    emoji: '💪',
    duration: 30000,
    cost: 50,
    gain: 5
  }
};

// Agent头像
export const AVATARS = [
  '🤖', '🦊', '🐉', '🦄', '🐱', '🐶', '🦁', '🐻',
  '🦊', '🐰', '🐼', '🐨', '🦋', '🐙', '🦚', '🦜',
  '🤡', '🦸', '🧙', '🧚', '🧛', '🧜', '🦢', '🦩',
  '🌟', '⭐', '🌙', '☀️', '🌈', '⚡', '🔥', '💎',
  '🎭', '🎪', '🎨', '🎯', '🎲', '🎮', '🕹️', '🤖'
];

// Agent名字前缀
export const NAME_PREFIXES = [
  '闪电', '烈焰', '冰霜', '疾风', '雷霆', '星光', '月光', '太阳',
  '钢铁', '风暴', '深海', '苍穹', '暗影', '光明', '神秘', '永恒',
  '元素', '精灵', '龙', '凤凰', '独角兽', '狮子', '狼', '熊',
  '智慧', '勇气', '力量', '速度', '技巧', '神秘', '魔法', '科技'
];

// Agent名字后缀
export const NAME_SUFFIXES = [
  '使者', '守护者', '战士', '法师', '刺客', '猎人', '骑士', '游侠',
  '大师', '王者', '领主', '王子', '公主', '英雄', '传奇', '神话',
  '之魂', '之心', '之眼', '之翼', '之爪', '之牙', '之鳞', '之羽',
  '一号', '二号', '三号', 'Alpha', 'Beta', 'Omega', 'Prime', 'Zero'
];

// 扭蛋配置
export const GACHA_CONFIG = {
  single: {
    cost: 100,
    pulls: 1,
    guaranteed: null
  },
  ten: {
    cost: 900,
    pulls: 10,
    guaranteed: 'rare'
  },
  premium: {
    cost: 10,
    pulls: 1,
    currency: 'gems',
    guaranteed: 'epic'
  },
  legend: {
    cost: 50,
    pulls: 1,
    currency: 'gems',
    guaranteed: 'legendary'
  }
};

// 战斗难度配置
export const BATTLE_LEVELS = [
  { level: 1, name: '新手', multiplier: 1, reward: 100 },
  { level: 5, name: '初级', multiplier: 1.5, reward: 200 },
  { level: 10, name: '中级', multiplier: 2, reward: 400 },
  { level: 20, name: '高级', multiplier: 3, reward: 800 },
  { level: 50, name: '大师', multiplier: 5, reward: 2000 },
  { level: 100, name: '传说', multiplier: 10, reward: 5000 }
];

// 格式化数字
export function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return Math.floor(num).toString();
}
