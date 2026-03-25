import { useState, useEffect } from 'react';
import { useGame } from '../store/GameContext';
import styles from './AutoClicker.module.css';

export default function AutoClicker() {
  const { state, click } = useGame();
  const [enabled, setEnabled] = useState(() => localStorage.getItem('starforge_autoclicker') === 'true');
  const [cps, setCps] = useState(1);

  useEffect(() => {
    localStorage.setItem('starforge_autoclicker', enabled.toString());
  }, [enabled]);

  useEffect(() => {
    if (!enabled) return;
    const interval = setInterval(() => {
      for (let i = 0; i < cps; i++) {
        click();
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [enabled, cps, click]);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.icon}>🤖</span>
        <span className={styles.title}>Auto Clicker</span>
        <button
          className={`${styles.toggle} ${enabled ? styles.active : ''}`}
          onClick={() => setEnabled(!enabled)}
        >
          {enabled ? 'ON' : 'OFF'}
        </button>
      </div>
      {enabled && (
        <div className={styles.control}>
          <span>Speed: {cps}x/s</span>
          <input
            type="range"
            min="1"
            max="20"
            value={cps}
            onChange={(e) => setCps(parseInt(e.target.value))}
          />
        </div>
      )}
    </div>
  );
}
