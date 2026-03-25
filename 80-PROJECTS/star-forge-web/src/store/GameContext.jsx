import { createContext, useContext, useReducer, useCallback, useRef, useMemo, useEffect } from 'react';
import { BUILDINGS, TIERS, getBuildingProduction, getBuildingCost } from '../data/buildings';
import { UPGRADES, getUpgradeEffect } from '../data/upgrades';
import { ACHIEVEMENTS, checkAchievements } from '../data/achievements';
import { QUESTS, applyQuestReward } from '../data/quests';

const GameContext = createContext(null);

const initialState = {
  // Resources
  energy: 0,
  totalEnergyEarned: 0,
  eternityPoints: 0,
  totalEternityEarned: 0,

  // Buildings
  buildings: BUILDINGS.reduce((acc, b) => ({ ...acc, [b.id]: 0 }), {}),

  // Upgrades
  purchasedUpgrades: [],
  clickPower: 1,

  // Prestige
  totalPrestiges: 0,
  eternityFactor: 0,

  // Stats
  totalClicks: 0,
  totalPlayTime: 0,
  gameStartTime: Date.now(),
  lastSaveTime: Date.now(),

  // Achievements
  achievements: [],

  // Achievements to show
  newAchievements: [],

  // Building efficiency bonuses
  buildingEfficiency: BUILDINGS.reduce((acc, b) => ({ ...acc, [b.id]: 0 }), {}),
  buildingCostReduction: BUILDINGS.reduce((acc, b) => ({ ...acc, [b.id]: 0 }), {}),
  globalEfficiency: 0,
  globalMultiplier: 1,
  autoClickPower: 0,
  autoClickUpgrades: 0,
  offlineRate: 1,

  // Tiers
  unlockedTiers: [1],

  // Calculated values
  energyPerSecond: 0,

  // Quests
  completedQuests: [],

  // Combo system
  comboCount: 0,
  comboMultiplier: 1,
  lastClickTime: 0,
  maxCombo: 0,

  // Milestones
  reachedMilestones: [],

  // First purchase bonuses
  firstPurchaseBonus: false,
};

function calculateEternityPoints(totalEnergyEarned) {
  return Math.floor(Math.sqrt(totalEnergyEarned / 1e6));
}

function calculateEnergyPerSecond(state) {
  let total = 0;
  const prestigeMultiplier = 1 + state.eternityFactor * 0.1;

  for (const building of BUILDINGS) {
    // Skip buildings from locked tiers
    if (!state.unlockedTiers.includes(building.tier)) continue;

    const owned = state.buildings[building.id];
    if (owned > 0) {
      const efficiencyBonus = state.buildingEfficiency[building.id] || 0;
      const costReduction = state.buildingCostReduction[building.id] || 0;
      const production = getBuildingProduction(building, owned, efficiencyBonus);
      const withPrestige = production * prestigeMultiplier;
      const withGlobal = withPrestige * (1 + state.globalEfficiency);
      const withMultiplier = withGlobal * state.globalMultiplier;
      total += withMultiplier * (1 - costReduction);
    }
  }
  return total;
}

function applyAchievementRewards(state, newAchievementIds) {
  let newState = { ...state };

  for (const achId of newAchievementIds) {
    const achievement = ACHIEVEMENTS.find(a => a.id === achId);
    if (!achievement || !achievement.reward) continue;

    switch (achievement.reward.type) {
      case 'click_power':
        newState.clickPower = (newState.clickPower || 1) + achievement.reward.value;
        break;
      case 'global_efficiency':
        newState.globalEfficiency = (newState.globalEfficiency || 0) + achievement.reward.value;
        break;
      case 'global_multiplier':
        newState.globalMultiplier = (newState.globalMultiplier || 1) * achievement.reward.value;
        break;
      case 'eternity_factor':
        newState.eternityFactor = (newState.eternityFactor || 0) + achievement.reward.value;
        break;
      case 'auto_click_power':
        newState.autoClickPower = (newState.autoClickPower || 1) * achievement.reward.value;
        break;
      case 'offline_rate':
        newState.offlineRate = (newState.offlineRate || 1) + achievement.reward.value;
        break;
    }
  }

  return newState;
}

function gameReducer(state, action) {
  switch (action.type) {
    case 'CLICK': {
      const now = Date.now();
      const timeSinceLastClick = now - state.lastClickTime;
      
      // Combo system: resets after 500ms of inactivity
      let newComboCount = state.comboCount;
      let newComboMultiplier = state.comboMultiplier;
      let newMaxCombo = state.maxCombo;
      
      if (timeSinceLastClick < 500) {
        newComboCount = state.comboCount + 1;
        newComboMultiplier = Math.min(1 + newComboCount * 0.1, 5); // Max 5x multiplier
        newMaxCombo = Math.max(state.maxCombo, newComboCount);
      } else {
        newComboCount = 1;
        newComboMultiplier = 1;
      }
      
      const clickValue = state.clickPower * newComboMultiplier;
      return {
        ...state,
        energy: state.energy + clickValue,
        totalEnergyEarned: state.totalEnergyEarned + clickValue,
        totalClicks: state.totalClicks + 1,
        comboCount: newComboCount,
        comboMultiplier: newComboMultiplier,
        lastClickTime: now,
        maxCombo: newMaxCombo,
      };
    }

    case 'TICK': {
      const energyPerSecond = calculateEnergyPerSecond(state);
      let gained = energyPerSecond * action.deltaTime;

      // Add auto-clicker
      if (state.autoClickPower > 0) {
        gained += state.autoClickPower * state.clickPower * action.deltaTime;
      }

      return {
        ...state,
        energy: state.energy + gained,
        totalEnergyEarned: state.totalEnergyEarned + gained,
        totalPlayTime: state.totalPlayTime + action.deltaTime,
        energyPerSecond: energyPerSecond,
      };
    }

    case 'BUY_BUILDING': {
      const building = BUILDINGS.find(b => b.id === action.buildingId);
      if (!building) return state;
      if (!state.unlockedTiers.includes(building.tier)) return state;

      const costReduction = state.buildingCostReduction[building.id] || 0;
      const prestigeMultiplier = 1 + state.eternityFactor * 0.1;
      const cost = getBuildingCost(building, state.buildings[building.id], prestigeMultiplier, costReduction);

      if (state.energy < cost) return state;

      return {
        ...state,
        energy: state.energy - cost,
        buildings: {
          ...state.buildings,
          [action.buildingId]: state.buildings[action.buildingId] + 1,
        },
      };
    }

    case 'BUY_UPGRADE': {
      const upgrade = UPGRADES.find(u => u.id === action.upgradeId);
      if (!upgrade) return state;
      if (state.purchasedUpgrades.includes(upgrade.id)) return state;
      if (state.energy < upgrade.cost) return state;

      const newState = {
        ...state,
        energy: state.energy - upgrade.cost,
        purchasedUpgrades: [...state.purchasedUpgrades, upgrade.id],
      };

      // Apply upgrade effects
      switch (upgrade.effect.type) {
        case 'efficiency':
          newState.buildingEfficiency = {
            ...newState.buildingEfficiency,
            [upgrade.buildingId]: (newState.buildingEfficiency[upgrade.buildingId] || 0) + upgrade.effect.value,
          };
          break;
        case 'cost_reduction':
          newState.buildingCostReduction = {
            ...newState.buildingCostReduction,
            [upgrade.buildingId]: (newState.buildingCostReduction[upgrade.buildingId] || 0) + upgrade.effect.value,
          };
          break;
        case 'global_efficiency':
          newState.globalEfficiency = (newState.globalEfficiency || 0) + upgrade.effect.value;
          break;
        case 'global_multiplier':
          newState.globalMultiplier = (newState.globalMultiplier || 1) * upgrade.effect.value;
          break;
        case 'click_power':
          newState.clickPower = (newState.clickPower || 1) + upgrade.effect.value;
          break;
        case 'auto_click':
          newState.autoClickPower = (newState.autoClickPower || 0) + upgrade.effect.value;
          newState.autoClickUpgrades = (newState.autoClickUpgrades || 0) + 1;
          break;
        case 'offline_rate':
          newState.offlineRate = (newState.offlineRate || 1) + upgrade.effect.value;
          break;
      }

      return newState;
    }

    case 'UNLOCK_TIER': {
      const tierId = action.tierId;
      const tier = TIERS.find(t => t.id === tierId);
      if (!tier) return state;
      if (state.unlockedTiers.includes(tierId)) return state;
      if (state.energy < tier.unlockCost) return state;

      return {
        ...state,
        energy: state.energy - tier.unlockCost,
        unlockedTiers: [...state.unlockedTiers, tierId],
      };
    }

    case 'PRESTIGE': {
      const newEternityPoints = calculateEternityPoints(state.totalEnergyEarned);
      if (newEternityPoints < 1) return state;

      return {
        ...state,
        energy: 0,
        totalEnergyEarned: 0,
        buildings: BUILDINGS.reduce((acc, b) => ({ ...acc, [b.id]: 0 }), {}),
        purchasedUpgrades: [],
        clickPower: 1,
        buildingEfficiency: BUILDINGS.reduce((acc, b) => ({ ...acc, [b.id]: 0 }), {}),
        buildingCostReduction: BUILDINGS.reduce((acc, b) => ({ ...acc, [b.id]: 0 }), {}),
        globalEfficiency: 0,
        globalMultiplier: 1,
        autoClickPower: 0,
        autoClickUpgrades: 0,
        unlockedTiers: [1],
        eternityPoints: state.eternityPoints + newEternityPoints,
        totalEternityEarned: state.totalEternityEarned + newEternityPoints,
        totalPrestiges: state.totalPrestiges + 1,
        eternityFactor: state.eternityFactor + newEternityPoints,
        energyPerSecond: 0,
      };
    }

    case 'LOAD_STATE': {
      const loaded = {
        ...action.state,
        lastSaveTime: Date.now(),
        newAchievements: [],
        // Ensure all buildings exist
        buildings: { ...initialState.buildings, ...action.state.buildings },
        buildingEfficiency: { ...initialState.buildingEfficiency, ...action.state.buildingEfficiency },
        buildingCostReduction: { ...initialState.buildingCostReduction, ...action.state.buildingCostReduction },
        unlockedTiers: action.state.unlockedTiers || [1],
        globalMultiplier: action.state.globalMultiplier || 1,
        autoClickPower: action.state.autoClickPower || 0,
        autoClickUpgrades: action.state.autoClickUpgrades || 0,
        offlineRate: action.state.offlineRate || 1,
        completedQuests: action.state.completedQuests || [],
      };
      return loaded;
    }

    case 'UPDATE_TIME': {
      return {
        ...state,
        totalPlayTime: state.totalPlayTime + action.deltaTime,
        lastSaveTime: Date.now(),
      };
    }

    case 'CHECK_ACHIEVEMENTS': {
      const computedState = {
        ...state,
        energyPerSecond: calculateEnergyPerSecond(state),
      };
      const newAchievementIds = checkAchievements(computedState, state.achievements);
      if (newAchievementIds.length === 0) return state;

      let newState = {
        ...state,
        achievements: [...state.achievements, ...newAchievementIds],
        newAchievements: newAchievementIds,
      };

      // Apply achievement rewards
      newState = applyAchievementRewards(newState, newAchievementIds);

      return newState;
    }

    case 'CLEAR_NEW_ACHIEVEMENTS': {
      return {
        ...state,
        newAchievements: [],
      };
    }

    case 'COMPLETE_QUEST': {
      const questId = action.questId;
      if (state.completedQuests.includes(questId)) return state;
      
      let newState = {
        ...state,
        completedQuests: [...state.completedQuests, questId],
      };

      // Apply quest reward
      const quest = QUESTS.find(q => q.id === questId);
      if (quest) {
        newState = applyQuestReward(newState, quest.reward);
      }

      return newState;
    }

    default:
      return state;
  }
}

export function GameProvider({ children }) {
  const [state, dispatch] = useReducer(gameReducer, initialState);

  const click = useCallback(() => dispatch({ type: 'CLICK' }), []);
  const tick = useCallback((deltaTime) => dispatch({ type: 'TICK', deltaTime }), []);
  const buyBuilding = useCallback((buildingId) => dispatch({ type: 'BUY_BUILDING', buildingId }), []);
  const buyUpgrade = useCallback((upgradeId) => dispatch({ type: 'BUY_UPGRADE', upgradeId }), []);
  const unlockTier = useCallback((tierId) => dispatch({ type: 'UNLOCK_TIER', tierId }), []);
  const prestige = useCallback(() => dispatch({ type: 'PRESTIGE' }), []);
  const loadState = useCallback((savedState) => dispatch({ type: 'LOAD_STATE', state: savedState }), []);
  const updateTime = useCallback((deltaTime) => dispatch({ type: 'UPDATE_TIME', deltaTime }), []);
  const checkAchievements = useCallback(() => dispatch({ type: 'CHECK_ACHIEVEMENTS' }), []);
  const clearNewAchievements = useCallback(() => dispatch({ type: 'CLEAR_NEW_ACHIEVEMENTS' }), []);
  const completeQuest = useCallback((questId) => dispatch({ type: 'COMPLETE_QUEST', questId }), []);

  // Memoize expensive calculations - only recalculate when relevant state changes
  const energyPerSecond = useMemo(() => calculateEnergyPerSecond(state), [
    state.buildings,
    state.buildingEfficiency,
    state.buildingCostReduction,
    state.globalEfficiency,
    state.globalMultiplier,
    state.eternityFactor,
    state.unlockedTiers
  ]);

  const eternityPointsForPrestige = useMemo(() => calculateEternityPoints(state.totalEnergyEarned), [state.totalEnergyEarned]);

  // Memoize value object to prevent unnecessary re-renders
  const value = useMemo(() => ({
    state,
    click,
    tick,
    buyBuilding,
    buyUpgrade,
    unlockTier,
    prestige,
    loadState,
    updateTime,
    checkAchievements,
    clearNewAchievements,
    completeQuest,
    energyPerSecond,
    eternityPointsForPrestige,
  }), [state, click, tick, buyBuilding, buyUpgrade, unlockTier, prestige, loadState, updateTime, checkAchievements, clearNewAchievements, completeQuest, energyPerSecond, eternityPointsForPrestige]);

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
}

export function useGame() {
  const context = useContext(GameContext);
  if (!context) {
    throw new Error('useGame must be used within a GameProvider');
  }
  return context;
}

export { BUILDINGS, TIERS, UPGRADES, ACHIEVEMENTS, getBuildingCost, getBuildingProduction };
