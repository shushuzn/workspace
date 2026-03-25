// Comprehensive achievements with bonuses

export const ACHIEVEMENTS = [
  // ============ ENERGY MILESTONES ============
  { id: 'e_100', name: 'Spark', description: 'Reach 100 energy', category: 'energy', condition: (state) => state.totalEnergyEarned >= 100, reward: { type: 'click_power', value: 1 } },
  { id: 'e_1k', name: 'Ember', description: 'Reach 1,000 energy', category: 'energy', condition: (state) => state.totalEnergyEarned >= 1e3, reward: { type: 'global_efficiency', value: 0.05 } },
  { id: 'e_10k', name: 'Flame', description: 'Reach 10,000 energy', category: 'energy', condition: (state) => state.totalEnergyEarned >= 1e4, reward: { type: 'global_efficiency', value: 0.05 } },
  { id: 'e_100k', name: 'Fire', description: 'Reach 100,000 energy', category: 'energy', condition: (state) => state.totalEnergyEarned >= 1e5, reward: { type: 'global_efficiency', value: 0.1 } },
  { id: 'e_1m', name: 'Blaze', description: 'Reach 1,000,000 energy', category: 'energy', condition: (state) => state.totalEnergyEarned >= 1e6, reward: { type: 'click_power', value: 10 } },
  { id: 'e_10m', name: 'Inferno', description: 'Reach 10,000,000 energy', category: 'energy', condition: (state) => state.totalEnergyEarned >= 1e7, reward: { type: 'global_efficiency', value: 0.15 } },
  { id: 'e_100m', name: 'Wildfire', description: 'Reach 100,000,000 energy', category: 'energy', condition: (state) => state.totalEnergyEarned >= 1e8, reward: { type: 'global_efficiency', value: 0.2 } },
  { id: 'e_1b', name: 'Supernova', description: 'Reach 1,000,000,000 energy', category: 'energy', condition: (state) => state.totalEnergyEarned >= 1e9, reward: { type: 'click_power', value: 100 } },
  { id: 'e_1t', name: 'Hypernova', description: 'Reach 1e12 energy', category: 'energy', condition: (state) => state.totalEnergyEarned >= 1e12, reward: { type: 'global_efficiency', value: 0.5 } },
  { id: 'e_1q', name: 'Big Bang', description: 'Reach 1e15 energy', category: 'energy', condition: (state) => state.totalEnergyEarned >= 1e15, reward: { type: 'global_multiplier', value: 2 } },
  { id: 'e_1s', name: 'Singularity', description: 'Reach 1e18 energy', category: 'energy', condition: (state) => state.totalEnergyEarned >= 1e18, reward: { type: 'global_multiplier', value: 3 } },
  { id: 'e_1sx', name: 'Infinity', description: 'Reach 1e21 energy', category: 'energy', condition: (state) => state.totalEnergyEarned >= 1e21, reward: { type: 'global_multiplier', value: 5 } },

  // ============ BUILDING MILESTONES ============
  { id: 'b_first', name: 'First Steps', description: 'Own 1 of any building', category: 'building', condition: (state) => Object.values(state.buildings).some(b => b >= 1), reward: { type: 'global_efficiency', value: 0.02 } },
  { id: 'b_10', name: 'Collector', description: 'Own 10 of any building', category: 'building', condition: (state) => Object.values(state.buildings).some(b => b >= 10), reward: { type: 'global_efficiency', value: 0.05 } },
  { id: 'b_50', name: 'Hoarder', description: 'Own 50 of any building', category: 'building', condition: (state) => Object.values(state.buildings).some(b => b >= 50), reward: { type: 'global_efficiency', value: 0.1 } },
  { id: 'b_100', name: 'Magnate', description: 'Own 100 of any building', category: 'building', condition: (state) => Object.values(state.buildings).some(b => b >= 100), reward: { type: 'click_power', value: 50 } },
  { id: 'b_500', name: 'Tycoon', description: 'Own 500 of any building', category: 'building', condition: (state) => Object.values(state.buildings).some(b => b >= 500), reward: { type: 'global_efficiency', value: 0.25 } },
  { id: 'b_1000', name: 'Industrialist', description: 'Own 1,000 of any building', category: 'building', condition: (state) => Object.values(state.buildings).some(b => b >= 1000), reward: { type: 'global_multiplier', value: 1.5 } },
  { id: 'b_5000', name: 'Baron', description: 'Own 5,000 of any building', category: 'building', condition: (state) => Object.values(state.buildings).some(b => b >= 5000), reward: { type: 'global_multiplier', value: 2 } },

  // ============ PRODUCTION MILESTONES ============
  { id: 'p_1', name: 'Self-sustaining', description: 'Reach 1 E/s', category: 'production', condition: (state) => state.energyPerSecond >= 1, reward: { type: 'global_efficiency', value: 0.05 } },
  { id: 'p_10', name: 'Power Plant', description: 'Reach 10 E/s', category: 'production', condition: (state) => state.energyPerSecond >= 10, reward: { type: 'global_efficiency', value: 0.1 } },
  { id: 'p_100', name: 'Power Station', description: 'Reach 100 E/s', category: 'production', condition: (state) => state.energyPerSecond >= 100, reward: { type: 'click_power', value: 25 } },
  { id: 'p_1k', name: 'Power Grid', description: 'Reach 1,000 E/s', category: 'production', condition: (state) => state.energyPerSecond >= 1e3, reward: { type: 'global_efficiency', value: 0.15 } },
  { id: 'p_10k', name: 'Power Network', description: 'Reach 10,000 E/s', category: 'production', condition: (state) => state.energyPerSecond >= 1e4, reward: { type: 'global_efficiency', value: 0.2 } },
  { id: 'p_100k', name: 'Planetary Grid', description: 'Reach 100,000 E/s', category: 'production', condition: (state) => state.energyPerSecond >= 1e5, reward: { type: 'click_power', value: 250 } },
  { id: 'p_1m', name: 'Stellar Grid', description: 'Reach 1,000,000 E/s', category: 'production', condition: (state) => state.energyPerSecond >= 1e6, reward: { type: 'global_efficiency', value: 0.5 } },
  { id: 'p_1b', name: 'Galactic Grid', description: 'Reach 1e9 E/s', category: 'production', condition: (state) => state.energyPerSecond >= 1e9, reward: { type: 'global_multiplier', value: 2 } },
  { id: 'p_1t', name: 'Cosmic Grid', description: 'Reach 1e12 E/s', category: 'production', condition: (state) => state.energyPerSecond >= 1e12, reward: { type: 'global_multiplier', value: 3 } },
  { id: 'p_1q', name: 'Multiverse Grid', description: 'Reach 1e15 E/s', category: 'production', condition: (state) => state.energyPerSecond >= 1e15, reward: { type: 'global_multiplier', value: 5 } },

  // ============ CLICK MILESTONES ============
  { id: 'c_100', name: 'Clicker', description: 'Click 100 times', category: 'click', condition: (state) => state.totalClicks >= 100, reward: null },
  { id: 'c_1k', name: 'Enthusiast', description: 'Click 1,000 times', category: 'click', condition: (state) => state.totalClicks >= 1000, reward: { type: 'click_power', value: 5 } },
  { id: 'c_10k', name: 'Dedicated Clicker', description: 'Click 10,000 times', category: 'click', condition: (state) => state.totalClicks >= 10000, reward: { type: 'click_power', value: 25 } },
  { id: 'c_100k', name: 'Click Master', description: 'Click 100,000 times', category: 'click', condition: (state) => state.totalClicks >= 100000, reward: { type: 'click_power', value: 100 } },
  { id: 'c_1m', name: 'Click Legend', description: 'Click 1,000,000 times', category: 'click', condition: (state) => state.totalClicks >= 1e6, reward: { type: 'click_power', value: 500 } },

  // ============ PRESTIGE MILESTONES ============
  { id: 'pr_1', name: 'Ascended', description: 'Prestige once', category: 'prestige', condition: (state) => state.totalPrestiges >= 1, reward: { type: 'eternity_factor', value: 0.1 } },
  { id: 'pr_5', name: 'Transcended', description: 'Prestige 5 times', category: 'prestige', condition: (state) => state.totalPrestiges >= 5, reward: { type: 'eternity_factor', value: 0.25 } },
  { id: 'pr_10', name: 'Eternal', description: 'Prestige 10 times', category: 'prestige', condition: (state) => state.totalPrestiges >= 10, reward: { type: 'eternity_factor', value: 0.5 } },
  { id: 'pr_25', name: 'Transcendent', description: 'Prestige 25 times', category: 'prestige', condition: (state) => state.totalPrestiges >= 25, reward: { type: 'global_multiplier', value: 2 } },
  { id: 'pr_50', name: 'Omnipotent', description: 'Prestige 50 times', category: 'prestige', condition: (state) => state.totalPrestiges >= 50, reward: { type: 'global_multiplier', value: 5 } },
  { id: 'pr_100', name: 'Absolute', description: 'Prestige 100 times', category: 'prestige', condition: (state) => state.totalPrestiges >= 100, reward: { type: 'global_multiplier', value: 10 } },

  // ============ TIME MILESTONES ============
  { id: 't_1h', name: 'Patient', description: 'Play for 1 hour', category: 'time', condition: (state) => state.totalPlayTime >= 3600, reward: { type: 'global_efficiency', value: 0.05 } },
  { id: 't_8h', name: 'Dedicated', description: 'Play for 8 hours', category: 'time', condition: (state) => state.totalPlayTime >= 28800, reward: { type: 'global_efficiency', value: 0.1 } },
  { id: 't_24h', name: 'Committed', description: 'Play for 24 hours', category: 'time', condition: (state) => state.totalPlayTime >= 86400, reward: { type: 'click_power', value: 100 } },
  { id: 't_168h', name: 'Obsessed', description: 'Play for 168 hours', category: 'time', condition: (state) => state.totalPlayTime >= 604800, reward: { type: 'global_multiplier', value: 2 } },

  // ============ TIER MILESTONES ============
  { id: 'tier_2', name: 'Nebula Explorer', description: 'Unlock Tier 2 Nebula', category: 'tier', condition: (state) => state.unlockedTiers.includes(2), reward: { type: 'global_efficiency', value: 0.25 } },
  { id: 'tier_3', name: 'Galactic Pioneer', description: 'Unlock Tier 3 Galactic', category: 'tier', condition: (state) => state.unlockedTiers.includes(3), reward: { type: 'global_efficiency', value: 0.5 } },
  { id: 'tier_4', name: 'Cosmic Overlord', description: 'Unlock Tier 4 Cosmic', category: 'tier', condition: (state) => state.unlockedTiers.includes(4), reward: { type: 'global_multiplier', value: 3 } },
  { id: 'tier_5', name: 'Multiverse Master', description: 'Unlock Tier 5 Multiverse', category: 'tier', condition: (state) => state.unlockedTiers.includes(5), reward: { type: 'global_multiplier', value: 5 } },

  // ============ UPGRADE MILESTONES ============
  { id: 'upg_10', name: 'Researcher', description: 'Purchase 10 upgrades', category: 'upgrade', condition: (state) => state.purchasedUpgrades.length >= 10, reward: { type: 'global_efficiency', value: 0.1 } },
  { id: 'upg_25', name: 'Scientist', description: 'Purchase 25 upgrades', category: 'upgrade', condition: (state) => state.purchasedUpgrades.length >= 25, reward: { type: 'global_efficiency', value: 0.15 } },
  { id: 'upg_50', name: 'Genius', description: 'Purchase 50 upgrades', category: 'upgrade', condition: (state) => state.purchasedUpgrades.length >= 50, reward: { type: 'global_efficiency', value: 0.25 } },
  { id: 'upg_100', name: 'Omniscient', description: 'Purchase 100 upgrades', category: 'upgrade', condition: (state) => state.purchasedUpgrades.length >= 100, reward: { type: 'global_multiplier', value: 2 } },

  // ============ AUTO MILESTONES ============
  { id: 'auto_1', name: 'Automation I', description: 'Own 1 auto-clicker upgrade', category: 'auto', condition: (state) => state.autoClickUpgrades >= 1, reward: null },
  { id: 'auto_5', name: 'Automation II', description: 'Own 5 auto-clicker upgrades', category: 'auto', condition: (state) => state.autoClickUpgrades >= 5, reward: { type: 'auto_click_power', value: 1.5 } },
  { id: 'auto_10', name: 'Automation III', description: 'Own 10 auto-clicker upgrades', category: 'auto', condition: (state) => state.autoClickUpgrades >= 10, reward: { type: 'auto_click_power', value: 2 } },

  // ============ MULTIVERSE ACHIEVEMENTS ============
  { id: 'mv_building', name: 'Reality Shaper', description: 'Own a Tier 5 building', category: 'building', condition: (state) => Object.entries(state.buildings).some(([id, count]) => id.startsWith('multiverse') || id.startsWith('omni') || id.startsWith('cosmic_string') || id.startsWith('void') && count >= 1), reward: { type: 'global_multiplier', value: 1.25 } },
  { id: 'mv_all', name: 'Architect', description: 'Own all Tier 5 buildings', category: 'building', condition: (state) => ['multiverse_fabric', 'omniverse_well', 'cosmic_string', 'void_extractor'].every(id => (state.buildings[id] || 0) >= 1), reward: { type: 'global_multiplier', value: 3 } },

  // ============ ETERNITY ACHIEVEMENTS ============
  { id: 'et_100', name: 'Ascension', description: 'Earn 100 Eternity Points', category: 'eternity', condition: (state) => state.eternityPoints >= 100, reward: { type: 'global_efficiency', value: 0.2 } },
  { id: 'et_1000', name: 'Transcendence', description: 'Earn 1,000 Eternity Points', category: 'eternity', condition: (state) => state.eternityPoints >= 1000, reward: { type: 'global_multiplier', value: 2 } },
  { id: 'et_10000', name: 'Immortal', description: 'Earn 10,000 Eternity Points', category: 'eternity', condition: (state) => state.eternityPoints >= 10000, reward: { type: 'global_multiplier', value: 5 } },
];

// Pre-group achievements by category for faster checking
const ACHIEVEMENTS_BY_CATEGORY = ACHIEVEMENTS.reduce((acc, ach) => {
  if (!acc[ach.category]) acc[ach.category] = [];
  acc[ach.category].push(ach);
  return acc;
}, {});

// Track which categories need checking based on state changes
const CATEGORY_TRIGGERS = {
  energy: ['totalEnergyEarned'],
  building: ['buildings'],
  production: ['energyPerSecond'],
  click: ['totalClicks'],
  prestige: ['totalPrestiges'],
  time: ['totalPlayTime'],
  tier: ['unlockedTiers'],
  upgrade: ['purchasedUpgrades'],
  auto: ['autoClickUpgrades'],
  eternity: ['eternityPoints'],
};

export function checkAchievements(state, earnedAchievements) {
  const newAchievements = [];
  // Only check achievements in categories that might have changed
  for (const [category, achievements] of Object.entries(ACHIEVEMENTS_BY_CATEGORY)) {
    for (const achievement of achievements) {
      if (!earnedAchievements.includes(achievement.id) && achievement.condition(state)) {
        newAchievements.push(achievement.id);
      }
    }
  }
  return newAchievements;
}

// Optimized check for specific categories (can be called from useEffect with dependencies)
export function checkAchievementsForCategories(state, earnedAchievements, categories) {
  const newAchievements = [];
  for (const category of categories) {
    const achievements = ACHIEVEMENTS_BY_CATEGORY[category] || [];
    for (const achievement of achievements) {
      if (!earnedAchievements.includes(achievement.id) && achievement.condition(state)) {
        newAchievements.push(achievement.id);
      }
    }
  }
  return newAchievements;
}
