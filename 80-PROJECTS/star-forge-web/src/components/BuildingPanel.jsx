import { useMemo, memo } from 'react';
import { useGame, BUILDINGS, TIERS, getBuildingCost, getBuildingProduction } from '../store/GameContext';
import { useSeason } from '../store/SeasonContext';
import { formatNumber } from '../utils/format';
import styles from './BuildingPanel.module.css';

const BuildingItem = memo(function BuildingItem({ building, owned, efficiencyBonus, costReduction, prestigeMultiplier, globalEfficiency, globalMultiplier, energy, onBuy, autoBuyRate }) {
  const cost = Math.floor(getBuildingCost(building, owned, prestigeMultiplier, costReduction));
  const production = getBuildingProduction(building, 1, efficiencyBonus) * prestigeMultiplier * (1 + globalEfficiency) * globalMultiplier;
  const totalProduction = getBuildingProduction(building, owned, efficiencyBonus) * prestigeMultiplier * (1 + globalEfficiency) * globalMultiplier;
  const canAfford = energy >= cost;

  return (
    <div
      className={`${styles.building} ${canAfford ? styles.affordable : ''}`}
      onClick={() => canAfford && onBuy(building.id)}
    >
      <div className={styles.buildingIcon}>{building.emoji}</div>
      <div className={styles.buildingInfo}>
        <div className={styles.buildingName}>{building.name}</div>
        <div className={styles.buildingOwned}>
          ×{owned}
          {autoBuyRate > 0 && <span className={styles.autoBuyRate}> ⚡+{autoBuyRate}/s</span>}
        </div>
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
});

export default memo(function BuildingPanel() {
  const { state, buyBuilding, unlockTier } = useGame();
  const season = useSeason();

  const handleBuy = (buildingId) => {
    buyBuilding(buildingId);
    // TODO: ch1_upgrade_10 is better triggered from UpgradePanel when upgrade is purchased
    season?.setTaskProgress('ch1_upgrade_10', 1);
  };

  const buildingsByTier = useMemo(() => {
    const result = {};
    for (const tier of TIERS) {
      result[tier.id] = BUILDINGS.filter(b => b.tier === tier.id);
    }
    return result;
  }, []);

  const prestigeMultiplier = 1 + state.eternityFactor * 0.1;

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
                {buildings.map((building) => (
                  <BuildingItem
                    key={building.id}
                    building={building}
                    owned={state.buildings[building.id] || 0}
                    efficiencyBonus={state.buildingEfficiency[building.id] || 0}
                    costReduction={state.buildingCostReduction[building.id] || 0}
                    prestigeMultiplier={prestigeMultiplier}
                    globalEfficiency={state.globalEfficiency}
                    globalMultiplier={state.globalMultiplier}
                    energy={state.energy}
                    onBuy={handleBuy}
                    autoBuyRate={state.autoBuyBuildings?.[building.id] || 0}
                  />
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
});
