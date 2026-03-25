// Achievement configurations

export const ACHIEVEMENTS = [
  // Energy milestones
  { id: 'energy_1', name: 'Spark', description: 'Reach 100 energy', condition: (state) => state.totalEnergyEarned >= 100, reward: null },
  { id: 'energy_2', name: 'Flame', description: 'Reach 10,000 energy', condition: (state) => state.totalEnergyEarned >= 10000, reward: null },
  { id: 'energy_3', name: 'Blaze', description: 'Reach 1,000,000 energy', condition: (state) => state.totalEnergyEarned >= 1e6, reward: null },
  { id: 'energy_4', name: 'Inferno', description: 'Reach 1,000,000,000 energy', condition: (state) => state.totalEnergyEarned >= 1e9, reward: null },
  { id: 'energy_5', name: 'Supernova', description: 'Reach 1e12 energy', condition: (state) => state.totalEnergyEarned >= 1e12, reward: null },

  // Building milestones
  { id: 'building_1', name: 'First Steps', description: 'Own 1 of any building', condition: (state) => Object.values(state.buildings).some(b => b >= 1), reward: null },
  { id: 'building_10', name: 'Collector', description: 'Own 10 of any building', condition: (state) => Object.values(state.buildings).some(b => b >= 10), reward: null },
  { id: 'building_50', name: 'Hoarder', description: 'Own 50 of any building', condition: (state) => Object.values(state.buildings).some(b => b >= 50), reward: null },
  { id: 'building_100', name: 'Magnate', description: 'Own 100 of any building', condition: (state) => Object.values(state.buildings).some(b => b >= 100), reward: null },

  // Production milestones
  { id: 'prod_1', name: 'Self-sustaining', description: 'Reach 1 energy per second', condition: (state) => state.energyPerSecond >= 1, reward: null },
  { id: 'prod_10', name: 'Power Plant', description: 'Reach 10 energy per second', condition: (state) => state.energyPerSecond >= 10, reward: null },
  { id: 'prod_100', name: 'Power Station', description: 'Reach 100 energy per second', condition: (state) => state.energyPerSecond >= 100, reward: null },
  { id: 'prod_1000', name: 'Power Grid', description: 'Reach 1,000 energy per second', condition: (state) => state.energyPerSecond >= 1000, reward: null },
  { id: 'prod_1e6', name: 'Cosmic Engine', description: 'Reach 1,000,000 energy per second', condition: (state) => state.energyPerSecond >= 1e6, reward: null },

  // Click milestones
  { id: 'click_1', name: 'Clicker', description: 'Click 100 times', condition: (state) => state.totalClicks >= 100, reward: null },
  { id: 'click_1000', name: 'Dedicated Clicker', description: 'Click 1,000 times', condition: (state) => state.totalClicks >= 1000, reward: null },
  { id: 'click_10000', name: 'Click Master', description: 'Click 10,000 times', condition: (state) => state.totalClicks >= 10000, reward: null },

  // Prestige milestones
  { id: 'prestige_1', name: 'Ascended', description: 'Prestige once', condition: (state) => state.totalPrestiges >= 1, reward: null },
  { id: 'prestige_5', name: 'Transcended', description: 'Prestige 5 times', condition: (state) => state.totalPrestiges >= 5, reward: null },
  { id: 'prestige_10', name: 'Eternal', description: 'Prestige 10 times', condition: (state) => state.totalPrestiges >= 10, reward: null },

  // Time milestones
  { id: 'time_1h', name: 'Patient', description: 'Play for 1 hour', condition: (state) => state.totalPlayTime >= 3600, reward: null },
  { id: 'time_24h', name: 'Dedicated', description: 'Play for 24 hours', condition: (state) => state.totalPlayTime >= 86400, reward: null },
  { id: 'time_168h', name: 'Committed', description: 'Play for 168 hours', condition: (state) => state.totalPlayTime >= 604800, reward: null },
];

export function checkAchievements(state, earnedAchievements) {
  const newAchievements = [];
  for (const achievement of ACHIEVEMENTS) {
    if (!earnedAchievements.includes(achievement.id) && achievement.condition(state)) {
      newAchievements.push(achievement.id);
    }
  }
  return newAchievements;
}
