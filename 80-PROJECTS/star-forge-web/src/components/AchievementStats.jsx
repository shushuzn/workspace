import { useGame } from '../store/GameContext';
import styles from './AchievementStats.module.css';

export default function AchievementStats() {
  const { state } = useGame();
  const achievements = state.achievements?.length || 0;
  const buildings = Object.values(state.buildings || {}).reduce((a, b) => a + b, 0);
  const upgrades = state.purchasedUpgrades?.length || 0;
  const prestige = state.totalPrestiges || 0;

  const stats = [
    { label: 'Achievements', value: achievements, icon: '🏆' },
    { label: 'Buildings', value: buildings, icon: '🏗️' },
    { label: 'Upgrades', value: upgrades, icon: '⬆️' },
    { label: 'Prestiges', value: prestige, icon: '⭐' },
  ];

  return (
    <div className={styles.container}>
      {stats.map((s, i) => (
        <div key={i} className={styles.stat}>
          <span className={styles.icon}>{s.icon}</span>
          <span className={styles.value}>{s.value}</span>
          <span className={styles.label}>{s.label}</span>
        </div>
      ))}
    </div>
  );
}
