import { useMemo, memo } from 'react';
import { useGame, UPGRADES, BUILDINGS } from '../store/GameContext';
import { formatNumber } from '../utils/format';
import styles from './UpgradePanel.module.css';

const UpgradeItem = memo(function UpgradeItem({ upgrade, canAfford, onBuy }) {
  return (
    <div
      className={`${styles.upgrade} ${canAfford ? styles.affordable : ''}`}
      onClick={() => canAfford && onBuy(upgrade.id)}
    >
      <div className={styles.upgradeInfo}>
        <div className={styles.upgradeName}>
          {upgrade.buildingId && <span className={styles.upgradeBadge}>⚙</span>}
          {!upgrade.buildingId && <span className={styles.upgradeBadgeGlobal}>★</span>}
          {upgrade.name}
        </div>
        <div className={styles.upgradeDesc}>{upgrade.description}</div>
      </div>
      <div className={styles.upgradeCost}>
        <span className={canAfford ? styles.costAffordable : styles.costExpensive}>
          ⚡ {formatNumber(upgrade.cost)}
        </span>
      </div>
    </div>
  );
});

export default memo(function UpgradePanel() {
  const { state, buyUpgrade } = useGame();

  // Memoize available upgrades calculation
  const availableUpgrades = useMemo(() => {
    const purchased = new Set(state.purchasedUpgrades);
    const unlockedTiers = new Set(state.unlockedTiers);
    return UPGRADES.filter(upgrade => {
      if (purchased.has(upgrade.id)) return false;
      if (upgrade.buildingId) {
        const building = BUILDINGS.find(b => b.id === upgrade.buildingId);
        if (building && !unlockedTiers.has(building.tier)) return false;
      }
      if (upgrade.tier && upgrade.tier > 0 && !unlockedTiers.has(upgrade.tier)) return false;
      return state.energy >= upgrade.cost * 0.1;
    }).slice(0, 20);
  }, [state.purchasedUpgrades, state.unlockedTiers, state.energy]);

  if (availableUpgrades.length === 0) {
    return (
      <div className={styles.container}>
        <h2 className={styles.title}>Upgrades</h2>
        <div className={styles.empty}>No upgrades available</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Upgrades ({state.purchasedUpgrades.length}/{UPGRADES.length})</h2>
      <div className={styles.list}>
        {availableUpgrades.map((upgrade) => (
          <UpgradeItem
            key={upgrade.id}
            upgrade={upgrade}
            canAfford={state.energy >= upgrade.cost}
            onBuy={buyUpgrade}
          />
        ))}
      </div>
    </div>
  );
});
