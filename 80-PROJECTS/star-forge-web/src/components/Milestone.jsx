import { useState, useEffect } from 'react';
import { useGame } from '../store/GameContext';
import styles from './Milestone.module.css';

const MILESTONES = [
  { energy: 100, reward: 'click_power', value: 1, name: '初学者', desc: '累计获得100能量' },
  { energy: 1000, reward: 'global_efficiency', value: 0.1, name: '探索者', desc: '累计获得1,000能量' },
  { energy: 10000, reward: 'global_multiplier', value: 1.2, name: '冒险家', desc: '累计获得10,000能量' },
  { energy: 100000, reward: 'click_power', value: 10, name: '星际旅行者', desc: '累计获得100,000能量' },
  { energy: 1000000, reward: 'global_efficiency', value: 0.5, name: '银河探险家', desc: '累计获得1,000,000能量' },
  { energy: 10000000, reward: 'global_multiplier', value: 2, name: '宇宙征服者', desc: '累计获得10,000,000能量' },
  { energy: 100000000, reward: 'click_power', value: 100, name: '维度行者', desc: '累计获得100,000,000能量' },
  { energy: 1000000000, reward: 'global_efficiency', value: 1, name: '时空旅者', desc: '累计获得1,000,000,000能量' },
  { energy: 10000000000, reward: 'global_multiplier', value: 5, name: '多元宇宙大师', desc: '累计获得10,000,000,000能量' },
  { energy: 100000000000, reward: 'click_power', value: 1000, name: '创世者', desc: '累计获得100,000,000,000能量' },
];

export default function Milestone() {
  const { state, completeQuest } = useGame();
  const [showMilestone, setShowMilestone] = useState(null);
  const [reachedMilestones, setReachedMilestones] = useState([]);

  useEffect(() => {
    const saved = localStorage.getItem('starforge-milestones');
    if (saved) {
      setReachedMilestones(JSON.parse(saved));
    }
  }, []);

  useEffect(() => {
    const totalEnergy = state.totalEnergyEarned;
    for (const milestone of MILESTONES) {
      if (totalEnergy >= milestone.energy && !reachedMilestones.includes(milestone.energy)) {
        setShowMilestone(milestone);
        const newReached = [...reachedMilestones, milestone.energy];
        setReachedMilestones(newReached);
        localStorage.setItem('starforge-milestones', JSON.stringify(newReached));
        break;
      }
    }
  }, [state.totalEnergyEarned]);

  useEffect(() => {
    if (showMilestone) {
      const timer = setTimeout(() => setShowMilestone(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [showMilestone]);

  if (!showMilestone) return null;

  return (
    <div className={styles.milestoneToast}>
      <div className={styles.icon}>🏆</div>
      <div className={styles.content}>
        <div className={styles.title}>里程碑达成！</div>
        <div className={styles.name}>{showMilestone.name}</div>
        <div className={styles.desc}>{showMilestone.desc}</div>
        <div className={styles.reward}>
          奖励: {showMilestone.reward === 'click_power' && `+${showMilestone.value} 点击力`}
          {showMilestone.reward === 'global_efficiency' && `+${showMilestone.value * 100}% 全局效率`}
          {showMilestone.reward === 'global_multiplier' && `x${showMilestone.value} 倍率`}
        </div>
      </div>
    </div>
  );
}
