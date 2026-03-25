import { useState } from 'react';
import { useGame, ACHIEVEMENTS } from '../store/GameContext';
import styles from './Achievements.module.css';

export default function Achievements() {
  const { state } = useGame();
  const [filter, setFilter] = useState('all');

  const earned = state.achievements || [];
  const filtered = ACHIEVEMENTS.filter(a => {
    if (filter === 'earned') return earned.includes(a.id);
    if (filter === 'locked') return !earned.includes(a.id);
    return true;
  });

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>🏆 Achievements</h2>
        <div className={styles.progress}>{earned.length} / {ACHIEVEMENTS.length}</div>
      </div>

      <div className={styles.filters}>
        {['all', 'earned', 'locked'].map(f => (
          <button
            key={f}
            className={`${styles.filterBtn} ${filter === f ? styles.active : ''}`}
            onClick={() => setFilter(f)}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      <div className={styles.grid}>
        {filtered.map(ach => {
          const isEarned = earned.includes(ach.id);
          return (
            <div key={ach.id} className={`${styles.card} ${isEarned ? styles.earned : ''}`}>
              <div className={styles.icon}>{isEarned ? '🏆' : '🔒'}</div>
              <div className={styles.info}>
                <div className={styles.name}>{ach.name}</div>
                <div className={styles.desc}>{ach.description}</div>
                {ach.reward && isEarned && (
                  <div className={styles.reward}>
                    +{ach.reward.type === 'click_power' ? `${ach.reward.value} Click` :
                      ach.reward.type === 'global_efficiency' ? `${ach.reward.value * 100}% Eff` :
                      ach.reward.type === 'global_multiplier' ? `×${ach.reward.value}` : 'Reward'}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
