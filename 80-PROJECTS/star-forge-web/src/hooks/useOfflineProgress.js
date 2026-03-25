import { useEffect, useRef } from 'react';
import { useGame } from '../store/GameContext';
import { BUILDINGS, getBuildingProduction } from '../data/buildings';

export function useOfflineProgress() {
  const { loadState, state } = useGame();
  const initializedRef = useRef(false);

  useEffect(() => {
    if (initializedRef.current) return;
    initializedRef.current = true;

    const savedData = localStorage.getItem('starforge_save');
    if (!savedData) return;

    try {
      const saved = JSON.parse(savedData);
      const now = Date.now();
      const offlineTime = (now - saved.lastSaveTime) / 1000; // seconds

      if (offlineTime > 60) { // At least 1 minute offline
        // Calculate offline earnings
        const prestigeMultiplier = 1 + (saved.eternityFactor || 0) * 0.1;
        const globalMultiplier = saved.globalMultiplier || 1;
        const offlineRate = saved.offlineRate || 1;
        const unlockedTiers = saved.unlockedTiers || [1];
        let offlineEarnings = 0;

        for (const building of BUILDINGS) {
          // Skip buildings from locked tiers
          if (!unlockedTiers.includes(building.tier)) continue;

          const owned = saved.buildings?.[building.id] || 0;
          if (owned > 0) {
            const efficiencyBonus = saved.buildingEfficiency?.[building.id] || 0;
            const production = getBuildingProduction(building, owned, efficiencyBonus);
            const withPrestige = production * prestigeMultiplier;
            const withGlobal = withPrestige * (1 + (saved.globalEfficiency || 0));
            const withMultiplier = withGlobal * globalMultiplier;
            // Cap offline time at 24 hours
            const cappedTime = Math.min(offlineTime, 86400);
            offlineEarnings += withMultiplier * cappedTime * offlineRate;
          }
        }

        const updatedState = {
          ...saved,
          energy: (saved.energy || 0) + offlineEarnings,
          totalEnergyEarned: (saved.totalEnergyEarned || 0) + offlineEarnings,
          totalPlayTime: (saved.totalPlayTime || 0) + offlineTime,
          lastSaveTime: now,
          newAchievements: [],
        };

        loadState(updatedState);

        // Store offline earnings for display
        localStorage.setItem('starforge_offline', JSON.stringify({
          earnings: offlineEarnings,
          time: offlineTime,
        }));
      } else {
        loadState(saved);
      }
    } catch (e) {
      console.warn('Failed to load save:', e);
    }
  }, [loadState]);

  return null;
}
