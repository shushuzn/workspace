import { useGame } from '../store/GameContext';
import { formatNumber, formatPercent } from '../utils/format';
import styles from './PrestigePanel.module.css';

export default function PrestigePanel() {
  const { state, prestige, eternityPointsForPrestige } = useGame();

  const canPrestige = eternityPointsForPrestige >= 1;
  const nextFactorBonus = formatPercent(eternityPointsForPrestige * 0.1);

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Prestige</h2>

      <div className={styles.currentStats}>
        <div className={styles.statRow}>
          <span className={styles.statLabel}>Current Factor</span>
          <span className={styles.statValue}>x{state.eternityFactor}</span>
        </div>
        <div className={styles.statRow}>
          <span className={styles.statLabel}>Eternity Points</span>
          <span className={styles.statValue}>❂ {formatNumber(state.eternityPoints)}</span>
        </div>
        <div className={styles.statRow}>
          <span className={styles.statLabel}>Total Prestiges</span>
          <span className={styles.statValue}>{state.totalPrestiges}</span>
        </div>
      </div>

      <div className={styles.divider}></div>

      <div className={styles.prestigePreview}>
        <div className={styles.previewLabel}>Next Prestige</div>
        <div className={styles.previewValue}>
          +{formatNumber(eternityPointsForPrestige)} ❂
        </div>
        <div className={styles.previewEffect}>
          +{nextFactorBonus} production forever
        </div>
      </div>

      <button
        className={`${styles.prestigeButton} ${canPrestige ? styles.available : ''}`}
        onClick={prestige}
        disabled={!canPrestige}
      >
        {canPrestige ? 'Ascend' : `Need ${formatNumber(Math.max(1, 1 - eternityPointsForPrestige))} more EP`}
      </button>

      {!canPrestige && (
        <div className={styles.hint}>
          Earn {formatNumber(Math.pow(eternityPointsForPrestige + 1, 2) * 1e6 - state.totalEnergyEarned)} more total energy to prestige
        </div>
      )}
    </div>
  );
}
