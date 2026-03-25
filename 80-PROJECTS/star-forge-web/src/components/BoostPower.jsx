import { useState, useEffect } from 'react';
import { useGame } from '../store/GameContext';
import styles from './BoostPower.module.css';

const BOOSTS = [
  { id: '2x_click', name: '2x Click Power', duration: 60, cost: 1000, effect: () => {} },
  { id: '2x_production', name: '2x Production', duration: 120, cost: 5000, effect: () => {} },
  { id: 'free_upgrades', name: 'Free Upgrades', duration: 30, cost: 10000, effect: () => {} },
];

export default function BoostPower() {
  const { state } = useGame();
  const [activeBoosts, setActiveBoosts] = useState([]);

  const canAfford = (cost) => state.energy >= cost;

  const activateBoost = (boost) => {
    if (!canAfford(boost.cost)) return;
    const newBoost = { ...boost, endTime: Date.now() + boost.duration * 1000 };
    setActiveBoosts(prev => [...prev, newBoost]);
  };

  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      setActiveBoosts(prev => prev.filter(b => b.endTime > now));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>⚡ Power Boosts</h3>
      
      {activeBoosts.length > 0 && (
        <div className={styles.active}>
          <div className={styles.activeTitle}>Active Boosts:</div>
          {activeBoosts.map((b, i) => (
            <div key={i} className={styles.activeItem}>
              <span>{b.name}</span>
              <span>{Math.ceil((b.endTime - Date.now()) / 1000)}s</span>
            </div>
          ))}
        </div>
      )}

      <div className={styles.list}>
        {BOOSTS.map(boost => (
          <button
            key={boost.id}
            className={`${styles.boostBtn} ${canAfford(boost.cost) ? '' : styles.disabled}`}
            onClick={() => activateBoost(boost)}
          >
            <div className={styles.boostName}>{boost.name}</div>
            <div className={styles.boostDuration}>{boost.duration}s</div>
            <div className={styles.boostCost}>⚡ {boost.cost}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
