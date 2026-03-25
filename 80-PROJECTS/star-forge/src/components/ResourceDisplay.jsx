import { useGame } from '../store/GameContext';
import { useLanguage } from '../i18n/LanguageContext';
import { formatNumber, formatTime, formatPercent } from '../utils/format';
import styles from './ResourceDisplay.module.css';

export default function ResourceDisplay() {
  const { state, energyPerSecond, eternityPointsForPrestige } = useGame();
  const { t } = useLanguage();

  return (
    <div className={styles.container}>
      <div className={styles.primaryResource}>
        <span className={styles.energyIcon}>⚡</span>
        <span className={styles.energyValue}>{formatNumber(state.energy)}</span>
        <span className={styles.energyLabel}>{t('resource.energy')}</span>
      </div>

      <div className={styles.secondaryStats}>
        <div className={styles.stat}>
          <span className={styles.statValue}>{formatNumber(energyPerSecond)}</span>
          <span className={styles.statLabel}>{t('resource.energyPerSecond')}</span>
        </div>

        <div className={styles.divider}></div>

        <div className={styles.stat}>
          <span className={styles.statValue}>{formatNumber(state.totalEnergyEarned)}</span>
          <span className={styles.statLabel}>{t('resource.totalEarned')}</span>
        </div>

        {state.eternityPoints > 0 && (
          <>
            <div className={styles.divider}></div>
            <div className={styles.stat}>
              <span className={styles.eternityIcon}>❂</span>
              <span className={styles.statValue}>{formatNumber(state.eternityPoints)}</span>
              <span className={styles.statLabel}>{t('resource.eternity')}</span>
            </div>
          </>
        )}
      </div>

      {state.eternityFactor > 0 && (
        <div className={styles.prestigeBonus}>
          +{formatPercent(state.eternityFactor * 0.1)} {t('resource.production')} (x{state.eternityFactor} {t('resource.factor')})
        </div>
      )}

      {eternityPointsForPrestige >= 1 && state.eternityFactor === 0 && (
        <div className={styles.prestigeHint}>
          {formatNumber(eternityPointsForPrestige)} {t('resource.eternityAvailable')}
        </div>
      )}

      <div className={styles.timeStats}>
        <span>{t('resource.time')}: {formatTime(state.totalPlayTime)}</span>
        <span className={styles.separator}>|</span>
        <span>{t('resource.clicks')}: {formatNumber(state.totalClicks)}</span>
      </div>
    </div>
  );
}
