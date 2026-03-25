import { useGame, BUILDINGS, TIERS, getBuildingCost, getBuildingProduction } from '../store/GameContext';
import { formatNumber } from '../utils/format';
import styles from './BuildingPanel.module.css';

export default function BuildingPanel() {
  const { state, buyBuilding, unlockTier } = useGame();

  const buildingsByTier = {};
  for (const tier of TIERS) {
    buildingsByTier[tier.id] = BUILDINGS.filter(b => b.tier === tier.id);
  }

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Buildings</h2>

      {Object.entries(buildingsByTier).map(([tierId, buildings]) => {
        const tier = TIERS.find(t => t.id === parseInt(tierId));
        const isUnlocked = state.unlockedTiers.includes(parseInt(tierId));

        return (
          <div key={tierId} className={styles.tierSection}>
            <div className={styles.tierHeader} style={{ borderColor: tier.color }}>
              <span className={styles.tierName} style={{ color: tier.color }}>
                {tier.name}
              </span>
              {!isUnlocked && (
                <button
                  className={styles.unlockBtn}
                  style={{ borderColor: tier.color, color: tier.color }}
                  onClick={() => unlockTier(parseInt(tierId))}
                  disabled={state.energy < tier.unlockCost}
                >
                  Unlock ⚡ {formatNumber(tier.unlockCost)}
                </button>
              )}
              {isUnlocked && tier.id > 1 && (
                <span className={styles.unlocked} style={{ color: tier.color }}>✓</span>
              )}
            </div>

            {isUnlocked && (
              <div className={styles.list}>
                {buildings.map((building) => {
                  const owned = state.buildings[building.id] || 0;
                  const efficiencyBonus = state.buildingEfficiency[building.id] || 0;
                  const costReduction = state.buildingCostReduction[building.id] || 0;
                  const prestigeMultiplier = 1 + state.eternityFactor * 0.1;
                  const cost = Math.floor(
                    getBuildingCost(building, owned, prestigeMultiplier, costReduction)
                  );
                  const production = getBuildingProduction(building, 1, efficiencyBonus) * prestigeMultiplier * (1 + state.globalEfficiency) * state.globalMultiplier;
                  const totalProduction = getBuildingProduction(building, owned, efficiencyBonus) * prestigeMultiplier * (1 + state.globalEfficiency) * state.globalMultiplier;
                  const canAfford = state.energy >= cost;

                  return (
                    <div
                      key={building.id}
                      className={`${styles.building} ${canAfford ? styles.affordable : ''}`}
                      onClick={() => canAfford && buyBuilding(building.id)}
                    >
                      <div className={styles.buildingIcon}>{building.emoji}</div>

                      <div className={styles.buildingInfo}>
                        <div className={styles.buildingName}>{building.name}</div>
                        <div className={styles.buildingOwned}>×{owned}</div>
                      </div>

                      <div className={styles.buildingStats}>
                        <div className={styles.buildingProduction}>
                          {owned > 0 ? formatNumber(totalProduction) : formatNumber(production)}/s
                        </div>
                        <div className={canAfford ? styles.costAffordable : styles.costExpensive}>
                          ⚡ {formatNumber(cost)}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
