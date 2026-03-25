import { useState, useEffect, useRef } from 'react';
import { useGame } from '../store/GameContext';
import styles from './ComboBar.module.css';

export default function ComboBar() {
  const { state } = useGame();
  const [combo, setCombo] = useState(0);
  const [comboMultiplier, setComboMultiplier] = useState(1);
  const lastClickRef = useRef(Date.now());

  useEffect(() => {
    const handleClick = () => {
      const now = Date.now();
      if (now - lastClickRef.current < 500) {
        setCombo(c => {
          const newCombo = c + 1;
          setComboMultiplier(Math.min(1 + newCombo * 0.1, 5));
          return newCombo;
        });
      } else {
        setCombo(0);
        setComboMultiplier(1);
      }
      lastClickRef.current = now;
    };

    window.addEventListener('click', handleClick);
    return () => window.removeEventListener('click', handleClick);
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      if (Date.now() - lastClickRef.current > 2000) {
        setCombo(0);
        setComboMultiplier(1);
      }
    }, 500);
    return () => clearInterval(timer);
  }, []);

  if (combo < 3) return null;

  return (
    <div className={styles.container}>
      <div className={styles.combo}>
        <span className={styles.icon}>🔥</span>
        <span className={styles.count}>{combo}x Combo!</span>
        <span className={styles.multiplier}>×{comboMultiplier.toFixed(1)}</span>
      </div>
      <div className={styles.bar}>
        <div className={styles.fill} style={{ width: `${Math.min((Date.now() - lastClickRef.current) / 2000 * 100, 100)}%` }} />
      </div>
    </div>
  );
}
