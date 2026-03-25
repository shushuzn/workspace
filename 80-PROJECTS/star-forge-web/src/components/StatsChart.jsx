import { useState, useEffect } from 'react';
import { useGame } from '../store/GameContext';
import styles from './StatsChart.module.css';

export default function StatsChart() {
  const { state } = useGame();
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const interval = setInterval(() => {
      setHistory(prev => {
        const newHistory = [...prev, {
          time: Date.now(),
          energy: state.energy,
          cps: state.energyPerSecond
        }];
        return newHistory.slice(-20);
      });
    }, 5000);
    return () => clearInterval(interval);
  }, [state.energyPerSecond]);

  const maxEnergy = Math.max(...history.map(h => h.energy), 1);

  return (
    <div className={styles.chart}>
      <h3 className={styles.title}>Production History</h3>
      <div className={styles.graph}>
        {history.length === 0 ? (
          <div className={styles.empty}>Collecting data...</div>
        ) : (
          history.map((h, i) => (
            <div
              key={i}
              className={styles.bar}
              style={{ height: `${(h.energy / maxEnergy) * 100}%` }}
              title={`${h.energy.toFixed(0)} energy`}
            />
          ))
        )}
      </div>
      <div className={styles.stats}>
        <span>Current: {state.energy.toFixed(0)}</span>
        <span>CPS: {state.energyPerSecond.toFixed(1)}</span>
      </div>
    </div>
  );
}
