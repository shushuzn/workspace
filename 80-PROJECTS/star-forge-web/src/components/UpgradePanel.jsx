import { useGame, UPGRADES, BUILDINGS } from '../store/GameContext';
import { formatNumber } from '../utils/format';
import styles from './UpgradePanel.module.css';

export default function UpgradePanel() {
  const { state, buyUpgrade } = useGame();

  // Filter available upgrades
  const availableUpgrades = UPGRADES.filter(upgrade => {
    if (state.purchasedUpgrades.includes(upgrade.id)) return false;

    // Check if building tier is unlocked
    if (upgrade.buildingId) {
      const building = BUILDINGS.find(b => b.id === upgrade.buildingId);
      if (building && !state.unlockedTiers.includes(building.tier)) return false;
    }

    // Check if tier requirement is met
    if (upgrade.tier && upgrade.tier > 0 && !state.unlockedTiers.includes(upgrade.tier)) return false;

    return state.energy >= upgrade.cost * 0.1; // Show if can somewhat afford
  }).slice(0, 20); // Limit to 20 visible upgrades

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
        {availableUpgrades.map((upgrade) => {
          const canAfford = state.energy >= upgrade.cost;

          return (
            <div
              key={upgrade.id}
              className={`${styles.upgrade} ${canAfford ? styles.affordable : ''}`}
              onClick={() => canAfford && buyUpgrade(upgrade.id)}
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
        })}
      </div>
    </div>
  );
}
