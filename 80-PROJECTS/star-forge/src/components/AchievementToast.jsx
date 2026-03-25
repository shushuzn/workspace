import { useEffect } from 'react';
import { useGame, ACHIEVEMENTS } from '../store/GameContext';
import styles from './AchievementToast.module.css';

export default function AchievementToast() {
  const { state, clearNewAchievements } = useGame();

  useEffect(() => {
    if (state.newAchievements.length > 0) {
      const timer = setTimeout(() => {
        clearNewAchievements();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [state.newAchievements, clearNewAchievements]);

  if (state.newAchievements.length === 0) return null;

  return (
    <div className={styles.container}>
      {state.newAchievements.map((id) => {
        const achievement = ACHIEVEMENTS.find(a => a.id === id);
        if (!achievement) return null;
        return (
          <div key={id} className={styles.toast}>
            <div className={styles.icon}>🏆</div>
            <div className={styles.info}>
              <div className={styles.name}>{achievement.name}</div>
              <div className={styles.desc}>{achievement.description}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
