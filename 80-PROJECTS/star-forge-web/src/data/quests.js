// Quest system with milestones and rewards

export const QUESTS = [
  // Tier 1 - Beginning
  { id: 'q_first_click', name: 'First Light', description: 'Click the sun for the first time', tier: 1, target: 1, reward: { type: 'energy', value: 100 } },
  { id: 'q_100_energy', name: 'Spark of Life', description: 'Reach 100 total energy', tier: 1, target: 100, reward: { type: 'click_power', value: 1 } },
  { id: 'q_first_building', name: 'Foundation', description: 'Purchase your first building', tier: 1, target: 1, reward: { type: 'energy', value: 500 } },
  { id: 'q_1k_energy', name: 'Rising Star', description: 'Reach 1,000 total energy', tier: 1, target: 1000, reward: { type: 'global_efficiency', value: 0.1 } },
  { id: 'q_10_buildings', name: 'Growing Empire', description: 'Own 10 of any building', tier: 1, target: 10, reward: { type: 'energy', value: 2000 } },
  { id: 'q_10k_energy', name: 'Cosmic Fire', description: 'Reach 10,000 total energy', tier: 1, target: 10000, reward: { type: 'click_power', value: 10 } },
  { id: 'q_100_clicks', name: 'Dedicated', description: 'Click 100 times', tier: 1, target: 100, reward: { type: 'energy', value: 5000 } },

  // Tier 2 - Expansion
  { id: 'q_100k_energy', name: 'Stellar Power', description: 'Reach 100,000 total energy', tier: 2, target: 100000, reward: { type: 'global_efficiency', value: 0.15 } },
  { id: 'q_100_buildings', name: 'Industrialist', description: 'Own 100 of any building', tier: 2, target: 100, reward: { type: 'global_multiplier', value: 1.5 } },
  { id: 'q_1m_energy', name: 'Millionaire', description: 'Reach 1,000,000 total energy', tier: 2, target: 1000000, reward: { type: 'click_power', value: 100 } },
  { id: 'q_first_prestige', name: 'Ascension', description: 'Prestige for the first time', tier: 2, target: 1, reward: { type: 'eternity_factor', value: 0.1 } },
  { id: 'q_1_ep', name: 'Eternal Beginning', description: 'Earn 1 Eternity Point', tier: 2, target: 1, reward: { type: 'global_efficiency', value: 0.2 } },
  { id: 'q_10m_energy', name: 'Supernova', description: 'Reach 10,000,000 total energy', tier: 2, target: 10000000, reward: { type: 'global_multiplier', value: 2 } },

  // Tier 3 - Domination
  { id: 'q_100m_energy', name: 'Galactic Empire', description: 'Reach 100,000,000 total energy', tier: 3, target: 100000000, reward: { type: 'click_power', value: 1000 } },
  { id: 'q_1b_energy', name: 'Cosmic Emperor', description: 'Reach 1,000,000,000 total energy', tier: 3, target: 1000000000, reward: { type: 'global_multiplier', value: 3 } },
  { id: 'q_10_prestiges', name: 'Eternal Journey', description: 'Prestige 10 times', tier: 3, target: 10, reward: { type: 'eternity_factor', value: 0.5 } },
  { id: 'q_1k_ep', name: 'Infinity', description: 'Earn 1,000 Eternity Points', tier: 3, target: 1000, reward: { type: 'global_multiplier', value: 5 } },
  { id: 'q_1t_energy', name: 'Hypernova', description: 'Reach 1e12 total energy', tier: 3, target: 1000000000000, reward: { type: 'global_efficiency', value: 1 } },

  // Tier 4 - Transcendence
  { id: 'q_1q_energy', name: 'Big Bang', description: 'Reach 1e15 total energy', tier: 4, target: 1000000000000000, reward: { type: 'global_multiplier', value: 10 } },
  { id: 'q_100_prestiges', name: 'Transcendent', description: 'Prestige 100 times', tier: 4, target: 100, reward: { type: 'eternity_factor', value: 1 } },
  { id: 'q_1s_energy', name: 'Singularity', description: 'Reach 1e18 total energy', tier: 4, target: 1000000000000000000, reward: { type: 'global_multiplier', value: 25 } },
  { id: 'q_10k_ep', name: 'Immortal', description: 'Earn 10,000 Eternity Points', tier: 4, target: 10000, reward: { type: 'global_multiplier', value: 50 } },
  { id: 'q_tier5', name: 'Multiverse Master', description: 'Unlock Tier 5 Multiverse', tier: 4, target: 1, reward: { type: 'global_efficiency', value: 5 } },
];

export const DAILY_REWARDS = [
  { day: 1, name: 'Welcome Bonus', type: 'energy', value: 100 },
  { day: 2, name: 'Double Click', type: 'click_power', value: 2 },
  { day: 3, name: 'Efficiency Boost', type: 'global_efficiency', value: 0.1 },
  { day: 4, name: 'Power Surge', type: 'global_multiplier', value: 1.5 },
  { day: 5, name: 'Energy Rush', type: 'energy', value: 10000 },
  { day: 6, name: 'Click Master', type: 'click_power', value: 10 },
  { day: 7, name: 'Weekly Reward', type: 'global_multiplier', value: 2 },
];

export function checkQuestProgress(state, quest) {
  switch (quest.id) {
    // Click quests
    case 'q_first_click':
      return state.totalClicks || 0;
    case 'q_100_clicks':
      return state.totalClicks || 0;

    // Energy quests
    case 'q_100_energy':
    case 'q_1k_energy':
    case 'q_10k_energy':
    case 'q_100k_energy':
    case 'q_1m_energy':
    case 'q_10m_energy':
    case 'q_100m_energy':
    case 'q_1b_energy':
    case 'q_1t_energy':
    case 'q_1q_energy':
    case 'q_1s_energy':
      return state.totalEnergyEarned || 0;

    // Building quests
    case 'q_first_building':
    case 'q_10_buildings':
    case 'q_100_buildings':
      const maxBuildings = Math.max(0, ...Object.values(state.buildings || {}));
      return maxBuildings;

    // Prestige quests
    case 'q_first_prestige':
    case 'q_10_prestiges':
    case 'q_100_prestiges':
      return state.totalPrestiges || 0;

    // Eternity Point quests
    case 'q_1_ep':
    case 'q_1k_ep':
    case 'q_10k_ep':
      return state.eternityPoints || 0;

    // Tier unlock quests
    case 'q_tier5':
      return state.unlockedTiers?.includes(5) ? 1 : 0;

    default:
      return 0;
  }
}

export function applyQuestReward(state, reward) {
  let newState = { ...state };

  switch (reward.type) {
    case 'energy':
      newState.energy = (newState.energy || 0) + reward.value;
      newState.totalEnergyEarned = (newState.totalEnergyEarned || 0) + reward.value;
      break;
    case 'click_power':
      newState.clickPower = (newState.clickPower || 1) + reward.value;
      break;
    case 'global_efficiency':
      newState.globalEfficiency = (newState.globalEfficiency || 0) + reward.value;
      break;
    case 'global_multiplier':
      newState.globalMultiplier = (newState.globalMultiplier || 1) * reward.value;
      break;
    case 'eternity_factor':
      newState.eternityFactor = (newState.eternityFactor || 0) + reward.value;
      break;
  }

  return newState;
}
