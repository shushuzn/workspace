import { useGame } from '../store/GameContext';
import { useLanguage } from '../i18n/LanguageContext';
import { formatNumber, formatPercent } from '../utils/format';
import styles from './PrestigePanel.module.css';

export default function PrestigePanel() {
  const { state, prestige, eternityPointsForPrestige } = useGame();
  const { t } = useLanguage();

  const canPrestige = eternityPointsForPrestige >= 1;
  const nextFactorBonus = formatPercent(eternityPointsForPrestige * 0.1);

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>{t('prestige.title')}</h2>

      <div className={styles.currentStats}>
        <div className={styles.statRow}>
          <span className={styles.statLabel}>{t('prestige.currentFactor')}</span>
          <span className={styles.statValue}>x{state.eternityFactor}</span>
        </div>
        <div className={styles.statRow}>
          <span className={styles.statLabel}>{t('prestige.eternityPoints')}</span>
          <span className={styles.statValue}>❂ {formatNumber(state.eternityPoints)}</span>
        </div>
        <div className={styles.statRow}>
          <span className={styles.statLabel}>{t('prestige.totalPrestiges')}</span>
          <span className={styles.statValue}>{state.totalPrestiges}</span>
        </div>
      </div>

      <div className={styles.divider}></div>

      <div className={styles.prestigePreview}>
        <div className={styles.previewLabel}>{t('prestige.nextPrestige')}</div>
        <div className={styles.previewValue}>
          +{formatNumber(eternityPointsForPrestige)} ❂
        </div>
        <div className={styles.previewEffect}>
          +{nextFactorBonus} {t('prestige.productionForever')}
        </div>
      </div>

      <button
        className={`${styles.prestigeButton} ${canPrestige ? styles.available : ''}`}
        onClick={prestige}
        disabled={!canPrestige}
      >
        {canPrestige ? t('prestige.ascend') : `${t('prestige.needMore')} ${formatNumber(Math.max(1, 1 - eternityPointsForPrestige))} ${t('prestige.moreEP')}`}
      </button>

      {!canPrestige && (
        <div className={styles.hint}>
          {t('prestige.earnMore')} {formatNumber(Math.pow(eternityPointsForPrestige + 1, 2) * 1e6 - state.totalEnergyEarned)} {t('prestige.moreTotalEnergy')}
        </div>
      )}
    </div>
  );
}
