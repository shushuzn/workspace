import { useMemo, memo } from 'react';
import { useGame } from '../store/GameContext';
import { formatNumber, formatPercent } from '../utils/format';
import styles from './ResourceDisplay.module.css';

export default memo(function ResourceDisplay() {
  const { state, energyPerSecond } = useGame();

  const totalCps = useMemo(() =>
    energyPerSecond + (state.autoClickPower * state.clickPower),
    [energyPerSecond, state.autoClickPower, state.clickPower]
  );

  return (
    <div className={styles.container}>
      <span className={styles.energyValue}>
        ⚡ {formatNumber(state.energy)}
      </span>
      <span className={styles.sep}>|</span>
      <span className={styles.cps}>{formatNumber(totalCps)}/s</span>
      {state.globalMultiplier > 1 && (
        <>
          <span className={styles.sep}>|</span>
          <span className={styles.multiplier}>×{state.globalMultiplier.toFixed(1)}</span>
        </>
      )}
      {state.eternityFactor > 0 && (
        <>
          <span className={styles.sep}>|</span>
          <span className={styles.prestige}>❂ {state.eternityFactor.toFixed(1)}x</span>
        </>
      )}
    </div>
  );
});
