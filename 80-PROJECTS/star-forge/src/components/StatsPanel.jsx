import { useGame } from '../store/GameContext';
import { useLanguage } from '../i18n/LanguageContext';
import { formatNumber, formatTime } from '../utils/format';
import styles from './StatsPanel.module.css';

export default function StatsPanel() {
  const { state } = useGame();
  const { t } = useLanguage();

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>{t('stats.title')}</h2>

      <div className={styles.grid}>
        <div className={styles.stat}>
          <span className={styles.statLabel}>{t('stats.totalEnergyEarned')}</span>
          <span className={styles.statValue}>{formatNumber(state.totalEnergyEarned)}</span>
        </div>

        <div className={styles.stat}>
          <span className={styles.statLabel}>{t('stats.totalClicks')}</span>
          <span className={styles.statValue}>{formatNumber(state.totalClicks)}</span>
        </div>

        <div className={styles.stat}>
          <span className={styles.statLabel}>{t('stats.clickPower')}</span>
          <span className={styles.statValue}>{formatNumber(state.clickPower)}</span>
        </div>

        <div className={styles.stat}>
          <span className={styles.statLabel}>{t('stats.upgradesPurchased')}</span>
          <span className={styles.statValue}>{state.purchasedUpgrades.length}</span>
        </div>

        <div className={styles.stat}>
          <span className={styles.statLabel}>{t('stats.achievements')}</span>
          <span className={styles.statValue}>{state.achievements.length}</span>
        </div>

        <div className={styles.stat}>
          <span className={styles.statLabel}>{t('stats.totalPlayTime')}</span>
          <span className={styles.statValue}>{formatTime(state.totalPlayTime)}</span>
        </div>

        <div className={styles.stat}>
          <span className={styles.statLabel}>{t('stats.eternityPointsEarned')}</span>
          <span className={styles.statValue}>{formatNumber(state.totalEternityEarned)}</span>
        </div>

        <div className={styles.stat}>
          <span className={styles.statLabel}>{t('stats.prestigeCount')}</span>
          <span className={styles.statValue}>{state.totalPrestiges}</span>
        </div>
      </div>
    </div>
  );
}
