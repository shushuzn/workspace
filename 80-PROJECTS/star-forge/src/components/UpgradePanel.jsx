import { useGame, UPGRADES } from '../store/GameContext';
import { useLanguage } from '../i18n/LanguageContext';
import { formatNumber } from '../utils/format';
import styles from './UpgradePanel.module.css';

export default function UpgradePanel() {
  const { state, buyUpgrade } = useGame();
  const { t } = useLanguage();

  const availableUpgrades = UPGRADES.filter(upgrade => {
    if (state.purchasedUpgrades.includes(upgrade.id)) return false;
    return state.energy >= upgrade.cost * 0.5;
  });

  if (availableUpgrades.length === 0) {
    return (
      <div className={styles.container}>
        <h2 className={styles.title}>{t('upgrade.title')}</h2>
        <div className={styles.empty}>{t('upgrade.noAvailable')}</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>{t('upgrade.title')}</h2>
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
                <div className={styles.upgradeName}>{upgrade.name}</div>
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
