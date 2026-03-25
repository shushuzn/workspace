import { createContext, useContext, useReducer, useCallback } from 'react';
import { BUILDINGS, getBuildingProduction, getBuildingCost } from '../data/buildings';
import { UPGRADES, getUpgradeEffect } from '../data/upgrades';
import { ACHIEVEMENTS, checkAchievements } from '../data/achievements';

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
};

function calculateEternityPoints(totalEnergyEarned) {
  return Math.floor(Math.sqrt(totalEnergyEarned / 1e6));
}

function calculateEnergyPerSecond(state) {
  let total = 0;
  const prestigeMultiplier = 1 + state.eternityFactor * 0.1;

  for (const building of BUILDINGS) {
    const owned = state.buildings[building.id];
    if (owned > 0) {
      const efficiencyBonus = state.buildingEfficiency[building.id] || 0;
      const costReduction = state.buildingCostReduction[building.id] || 0;
      const production = getBuildingProduction(building, owned, efficiencyBonus);
      const withPrestige = production * prestigeMultiplier;
      const withGlobal = withPrestige * (1 + state.globalEfficiency);
      total += withGlobal * (1 - costReduction);
    }
  }
  return total;
}

function gameReducer(state, action) {
  switch (action.type) {
    case 'CLICK': {
      const clickValue = state.clickPower;
      return {
        ...state,
        energy: state.energy + clickValue,
        totalEnergyEarned: state.totalEnergyEarned + clickValue,
        totalClicks: state.totalClicks + 1,
      };
    }

    case 'TICK': {
      const energyPerSecond = calculateEnergyPerSecond(state);
      const gained = energyPerSecond * action.deltaTime;
      return {
        ...state,
        energy: state.energy + gained,
        totalEnergyEarned: state.totalEnergyEarned + gained,
        totalPlayTime: state.totalPlayTime + action.deltaTime,
      };
    }

    case 'BUY_BUILDING': {
      const building = BUILDINGS.find(b => b.id === action.buildingId);
      if (!building) return state;

      const costReduction = state.buildingCostReduction[building.id] || 0;
      const prestigeMultiplier = 1 + state.eternityFactor * 0.1;
      const cost = getBuildingCost(building, state.buildings[building.id], prestigeMultiplier) * (1 - costReduction);

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
        case 'click_power':
          newState.clickPower = (newState.clickPower || 1) + upgrade.effect.value;
          break;
      }

      return newState;
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
        eternityPoints: state.eternityPoints + newEternityPoints,
        totalEternityEarned: state.totalEternityEarned + newEternityPoints,
        totalPrestiges: state.totalPrestiges + 1,
        eternityFactor: state.eternityFactor + newEternityPoints,
      };
    }

    case 'LOAD_STATE': {
      return {
        ...action.state,
        lastSaveTime: Date.now(),
        newAchievements: [],
      };
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
      const newAchievements = checkAchievements(computedState, state.achievements);
      if (newAchievements.length === 0) return state;
      return {
        ...state,
        achievements: [...state.achievements, ...newAchievements],
        newAchievements,
      };
    }

    case 'CLEAR_NEW_ACHIEVEMENTS': {
      return {
        ...state,
        newAchievements: [],
      };
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
  const prestige = useCallback(() => dispatch({ type: 'PRESTIGE' }), []);
  const loadState = useCallback((savedState) => dispatch({ type: 'LOAD_STATE', state: savedState }), []);
  const updateTime = useCallback((deltaTime) => dispatch({ type: 'UPDATE_TIME', deltaTime }), []);
  const checkAchievements = useCallback(() => dispatch({ type: 'CHECK_ACHIEVEMENTS' }), []);
  const clearNewAchievements = useCallback(() => dispatch({ type: 'CLEAR_NEW_ACHIEVEMENTS' }), []);

  const energyPerSecond = calculateEnergyPerSecond(state);
  const eternityPointsForPrestige = calculateEternityPoints(state.totalEnergyEarned);

  const value = {
    state,
    click,
    tick,
    buyBuilding,
    buyUpgrade,
    prestige,
    loadState,
    updateTime,
    checkAchievements,
    clearNewAchievements,
    energyPerSecond,
    eternityPointsForPrestige,
  };

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
}

export function useGame() {
  const context = useContext(GameContext);
  if (!context) {
    throw new Error('useGame must be used within a GameProvider');
  }
  return context;
}

export { BUILDINGS, UPGRADES, ACHIEVEMENTS, getBuildingCost, getBuildingProduction };
