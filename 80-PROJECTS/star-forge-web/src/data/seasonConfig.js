// src/data/seasonConfig.js

export const SEASON_CONFIG = {
  seasonDurationDays: 30,
  // 每章节解锁进度阈值(%)：第一章0%（自动解锁），第二章50%，第三章80%
  chapterUnlockThresholds: [0, 50, 80],
};

// 任务点数定义
export const TASK_POINT_VALUES = {
  // 第1章
  'ch1_build_5': 20,
  'ch1_produce_10000': 15,
  'ch1_upgrade_10': 15,
  // 第2章
  'ch2_click_500': 20,
  'ch2_use_item_10': 15,
  'ch2_daily_5': 15,
  // 第3章
  'ch3_prestige': 30,
  'ch3_achievement_100': 15,
  'ch3_reach_ch3': 15,
};

// 任务定义（不含 progress/claimed，运行时由 SeasonContext 注入）
export const SEASON_TASKS = [
  // === 第1章「星辰苏醒」===
  {
    id: 'ch1_build_5',
    chapter: 1,
    type: 'auto',
    tags: ['build', 'construction'],
    title: '建造5个不同建筑',
    description: '累计建造5种不同的建筑',
    target: 5,
    points: TASK_POINT_VALUES['ch1_build_5'],
  },
  {
    id: 'ch1_produce_10000',
    chapter: 1,
    type: 'auto',
    tags: ['produce'],
    title: '累计生产10000资源',
    description: '累计产生10000点能量',
    target: 10000,
    points: TASK_POINT_VALUES['ch1_produce_10000'],
  },
  {
    id: 'ch1_upgrade_10',
    chapter: 1,
    type: 'manual',
    tags: ['build', 'upgrade'],
    title: '建筑升到10级',
    description: '将任意建筑升级到10级',
    target: 1,
    points: TASK_POINT_VALUES['ch1_upgrade_10'],
  },
  // === 第2章「星际征途」===
  {
    id: 'ch2_click_500',
    chapter: 2,
    type: 'manual',
    tags: ['click'],
    title: '累计点击500次',
    description: '累计点击500次',
    target: 500,
    points: TASK_POINT_VALUES['ch2_click_500'],
  },
  {
    id: 'ch2_use_item_10',
    chapter: 2,
    type: 'manual',
    tags: ['use-item'],
    title: '使用加速道具10次',
    description: '使用10次加速道具',
    target: 10,
    points: TASK_POINT_VALUES['ch2_use_item_10'],
  },
  {
    id: 'ch2_daily_5',
    chapter: 2,
    type: 'auto',
    tags: ['daily'],
    title: '完成5次每日挑战',
    description: '累计完成5次每日挑战',
    target: 5,
    points: TASK_POINT_VALUES['ch2_daily_5'],
  },
  // === 第3章「宇宙主宰」===
  {
    id: 'ch3_prestige',
    chapter: 3,
    type: 'manual',
    tags: ['prestige'],
    title: '完成一次声望重置',
    description: '进行一次声望重置',
    target: 1,
    points: TASK_POINT_VALUES['ch3_prestige'],
  },
  {
    id: 'ch3_achievement_100',
    chapter: 3,
    type: 'auto',
    tags: ['achievement'],
    title: '收集100颗成就星',
    description: '累计获得100个成就',
    target: 100,
    points: TASK_POINT_VALUES['ch3_achievement_100'],
  },
  {
    id: 'ch3_reach_ch3',
    chapter: 3,
    type: 'auto',
    tags: ['progress'],
    title: '赛季达到第3章',
    description: '解锁并进入第3章',
    target: 1,
    points: TASK_POINT_VALUES['ch3_reach_ch3'],
  },
];

// 奖励定义
export const SEASON_REWARDS = [
  // === 第1章 ===
  {
    id: 'ch1_free_resource',
    chapter: 1,
    tier: 'free',
    type: 'resource',
    name: '500 游戏货币',
    description: '获得500点能量',
    unlockAt: 30,
    effect: { resourceAmount: 500 },
  },
  {
    id: 'ch1_free_potion',
    chapter: 1,
    tier: 'free',
    type: 'resource',
    name: '经验药水 x3',
    description: '经验药水 x3',
    unlockAt: 50,
    effect: { resourceAmount: 0 },
  },
  {
    id: 'ch1_premium_offline',
    chapter: 1,
    tier: 'premium',
    type: 'buff',
    name: '+5% 离线收益',
    description: '离线收益永久+5%',
    unlockAt: 30,
    effect: { buffId: 'offline_boost_5' },
  },
  {
    id: 'ch1_premium_skin',
    chapter: 1,
    tier: 'premium',
    type: 'skin',
    name: '高级皮肤箱 x1',
    description: '开启获得随机高级皮肤',
    unlockAt: 60,
    effect: { skinId: 'skin_box_premium' },
  },
  // === 第2章 ===
  {
    id: 'ch2_free_resource',
    chapter: 2,
    tier: 'free',
    type: 'resource',
    name: '1000 游戏货币',
    description: '获得1000点能量',
    unlockAt: 30,
    effect: { resourceAmount: 1000 },
  },
  {
    id: 'ch2_free_potion',
    chapter: 2,
    tier: 'free',
    type: 'resource',
    name: '加速药水 x5',
    description: '加速药水 x5',
    unlockAt: 50,
    effect: { resourceAmount: 0 },
  },
  {
    id: 'ch2_premium_click',
    chapter: 2,
    tier: 'premium',
    type: 'buff',
    name: '+10% 点击加成',
    description: '点击产出永久+10%',
    unlockAt: 30,
    effect: { buffId: 'click_boost_10' },
  },
  {
    id: 'ch2_premium_feature',
    chapter: 2,
    tier: 'premium',
    type: 'feature',
    name: '仓库容量+20',
    description: '解锁仓库容量+20',
    unlockAt: 60,
    effect: { featureKey: 'inventory_expand_20' },
  },
  // === 第3章 ===
  {
    id: 'ch3_free_resource',
    chapter: 3,
    tier: 'free',
    type: 'resource',
    name: '2000 游戏货币',
    description: '获得2000点能量',
    unlockAt: 30,
    effect: { resourceAmount: 2000 },
  },
  {
    id: 'ch3_free_frame',
    chapter: 3,
    tier: 'free',
    type: 'skin',
    name: '限定头像框',
    description: '赛季限定头像框',
    unlockAt: 50,
    effect: { skinId: 'avatar_frame_season1' },
  },
  {
    id: 'ch3_premium_ring',
    chapter: 3,
    tier: 'premium',
    type: 'skin',
    name: '星环建筑皮肤',
    description: '赛季专属星环建筑皮肤',
    unlockAt: 40,
    effect: { skinId: 'building_skin_ring' },
  },
  {
    id: 'ch3_premium_title',
    chapter: 3,
    tier: 'premium',
    type: 'skin',
    name: '称号「宇宙主宰」',
    description: '赛季限定称号',
    unlockAt: 70,
    effect: { skinId: 'title_cosmic_ruler' },
  },
];

// 根据赛季 ID 获取赛季时间范围
export function getSeasonTimeRange(seasonId) {
  // seasonId 格式: "2026-04"
  const [year, month] = seasonId.split('-').map(Number);
  const startDate = new Date(Date.UTC(year, month - 1, 1, 0, 0, 0, 0));
  const endDate = new Date(Date.UTC(year, month, 1, 0, 0, 0, 0));
  return {
    startTime: startDate.getTime(),
    endTime: endDate.getTime(),
  };
}

// 获取当前赛季 ID（格式 "YYYY-MM"）
export function getCurrentSeasonId() {
  const now = new Date();
  const year = now.getUTCFullYear();
  const month = String(now.getUTCMonth() + 1).padStart(2, '0');
  return `${year}-${month}`;
}

// 计算章节进度: Σ已完成任务点数 / Σ所有任务点数 * 100
export function calcChapterProgress(tasks, chapter) {
  const chapterTasks = tasks.filter(t => t.chapter === chapter);
  const totalPoints = chapterTasks.reduce((sum, t) => sum + t.points, 0);
  const donePoints = chapterTasks
    .filter(t => t.progress >= t.target)
    .reduce((sum, t) => sum + t.points, 0);
  if (totalPoints === 0) return 0;
  return Math.min(100, Math.round((donePoints / totalPoints) * 100));
}
