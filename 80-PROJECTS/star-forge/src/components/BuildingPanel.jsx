import { useGame, BUILDINGS, getBuildingCost, getBuildingProduction } from '../store/GameContext';
import { useLanguage } from '../i18n/LanguageContext';
import { formatNumber } from '../utils/format';
import styles from './BuildingPanel.module.css';

export default function BuildingPanel() {
  const { state, buyBuilding } = useGame();
  const { t } = useLanguage();

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>{t('building.title')}</h2>
      <div className={styles.list}>
        {BUILDINGS.map((building) => {
          const owned = state.buildings[building.id] || 0;
          const efficiencyBonus = state.buildingEfficiency[building.id] || 0;
          const costReduction = state.buildingCostReduction[building.id] || 0;
          const prestigeMultiplier = 1 + state.eternityFactor * 0.1;
          const cost = Math.floor(
            getBuildingCost(building, owned, prestigeMultiplier) * (1 - costReduction)
          );
          const production = getBuildingProduction(building, 1, efficiencyBonus) * prestigeMultiplier * (1 + state.globalEfficiency);
          const totalProduction = getBuildingProduction(building, owned, efficiencyBonus) * prestigeMultiplier * (1 + state.globalEfficiency);
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
                <div className={styles.buildingOwned}>{t('building.owned')}: {owned}</div>
              </div>

              <div className={styles.buildingStats}>
                <div className={styles.buildingProduction}>
                  {owned > 0 ? formatNumber(totalProduction) : formatNumber(production)}/s
                </div>
                <div className={styles.buildingCost}>
                  <span className={canAfford ? styles.costAffordable : styles.costExpensive}>
                    ⚡ {formatNumber(cost)}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
