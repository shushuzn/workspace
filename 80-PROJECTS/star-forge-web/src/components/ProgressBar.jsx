import { useState, useEffect } from 'react';
import { useGame } from '../store/GameContext';
import styles from './ProgressBar.module.css';

const TIERS = [
  { id: 1, name: '太阳系', energy: 0, color: '#ffd700' },
  { id: 2, name: '星云', energy: 100000, color: '#ff69b4' },
  { id: 3, name: '星系', energy: 100000000, color: '#9370db' },
  { id: 4, name: '宇宙', energy: 1e14, color: '#00ffff' },
  { id: 5, name: '多元宇宙', energy: 1e18, color: '#ff4500' },
  { id: 6, name: '终极宇宙', energy: 1e22, color: '#ff00ff' },
];

export default function ProgressBar() {
  const { state } = useGame();
  const [currentTier, setCurrentTier] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const totalEnergy = state.totalEnergyEarned;
    let tier = 0;
    let prog = 0;

    for (let i = 0; i < TIERS.length; i++) {
      if (totalEnergy >= TIERS[i].energy) {
        tier = i;
        if (i < TIERS.length - 1) {
          const nextEnergy = TIERS[i + 1].energy;
          const currentEnergy = TIERS[i].energy;
          prog = ((totalEnergy - currentEnergy) / (nextEnergy - currentEnergy)) * 100;
        } else {
          prog = 100;
        }
      }
    }

    setCurrentTier(tier);
    setProgress(Math.min(prog, 100));
  }, [state.totalEnergyEarned]);

  return (
    <div className={styles.progressContainer}>
      <div className={styles.tierInfo}>
        <span className={styles.currentTier} style={{ color: TIERS[currentTier].color }}>
          {TIERS[currentTier].name}
        </span>
        {currentTier < TIERS.length - 1 && (
          <span className={styles.nextTier}>
            → {TIERS[currentTier + 1].name}
          </span>
        )}
      </div>
      <div className={styles.progressBar}>
        <div 
          className={styles.progressFill}
          style={{ 
            width: `${progress}%`,
            background: `linear-gradient(90deg, ${TIERS[currentTier].color}, ${TIERS[Math.min(currentTier + 1, TIERS.length - 1)].color})`
          }}
        />
      </div>
      <div className={styles.tierDots}>
        {TIERS.map((tier, index) => (
          <div 
            key={tier.id}
            className={`${styles.tierDot} ${index <= currentTier ? styles.active : ''}`}
            style={{ backgroundColor: tier.color }}
            title={tier.name}
          />
        ))}
      </div>
    </div>
  );
}
