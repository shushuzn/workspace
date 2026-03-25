import { useState, useEffect } from 'react';
import { useGame } from '../store/GameContext';
import { formatNumber } from '../utils/format';
import styles from './DailyChallenge.module.css';

const CHALLENGES = [
  { id: 'click_100', name: 'Click Master', target: 100, type: 'clicks', reward: { type: 'energy', value: 500 }, emoji: '👆' },
  { id: 'click_1000', name: 'Click Champion', target: 1000, type: 'clicks', reward: { type: 'energy', value: 5000 }, emoji: '🔥' },
  { id: 'earn_10k', name: 'Energy Hunter', target: 10000, type: 'energy', reward: { type: 'click_power', value: 5 }, emoji: '⚡' },
  { id: 'earn_100k', name: 'Power Generator', target: 100000, type: 'energy', reward: { type: 'global_efficiency', value: 0.1 }, emoji: '💫' },
  { id: 'cps_10', name: 'Passive Pro', target: 10, type: 'cps', reward: { type: 'energy', value: 1000 }, emoji: '🔄' },
  { id: 'buy_5', name: 'Builder', target: 5, type: 'buildings', reward: { type: 'energy', value: 2000 }, emoji: '🏗️' },
];

export default function DailyChallenge() {
  const { state } = useGame();
  const [challenge, setChallenge] = useState(null);
  const [showComplete, setShowComplete] = useState(false);

  useEffect(() => {
    const today = new Date().toDateString();
    const savedDate = localStorage.getItem('starforge_challenge_date');
    const savedChallengeId = localStorage.getItem('starforge_challenge_id');
    const completedChallenges = JSON.parse(localStorage.getItem('starforge_challenge_completed') || '[]');

    if (savedDate === today && savedChallengeId) {
      const ch = CHALLENGES.find(c => c.id === savedChallengeId);
      if (ch && !completedChallenges.includes(savedChallengeId)) {
        setChallenge(ch);
      }
    } else {
      const randomChallenge = CHALLENGES[Math.floor(Math.random() * CHALLENGES.length)];
      localStorage.setItem('starforge_challenge_date', today);
      localStorage.setItem('starforge_challenge_id', randomChallenge.id);
      setChallenge(randomChallenge);
    }
  }, []);

  useEffect(() => {
    if (!challenge) return;
    const completedChallenges = JSON.parse(localStorage.getItem('starforge_challenge_completed') || '[]');
    if (completedChallenges.includes(challenge.id)) return;

    let current = 0;
    switch (challenge.type) {
      case 'clicks': current = state.totalClicks; break;
      case 'energy': current = state.totalEnergyEarned; break;
      case 'cps': current = state.energyPerSecond; break;
      case 'buildings': current = Object.values(state.buildings).reduce((a, b) => a + b, 0); break;
    }

    if (current >= challenge.target && !showComplete) {
      setShowComplete(true);
      const completed = [...completedChallenges, challenge.id];
      localStorage.setItem('starforge_challenge_completed', JSON.stringify(completed));
    }
  }, [state, challenge, showComplete]);

  if (!challenge) return null;

  let current = 0;
  switch (challenge.type) {
    case 'clicks': current = state.totalClicks; break;
    case 'energy': current = state.totalEnergyEarned; break;
    case 'cps': current = state.energyPerSecond; break;
    case 'buildings': current = Object.values(state.buildings).reduce((a, b) => a + b, 0); break;
  }
  const progress = Math.min(current / challenge.target, 1);
  const completed = current >= challenge.target;

  return (
    <div className={styles.challenge}>
      <div className={styles.header}>
        <span className={styles.emoji}>{challenge.emoji}</span>
        <span className={styles.name}>Daily: {challenge.name}</span>
      </div>
      <div className={styles.progress}>
        <div className={styles.progressBar}>
          <div className={styles.progressFill} style={{ width: `${progress * 100}%` }} />
        </div>
        <div className={styles.progressText}>
          {formatNumber(current)} / {formatNumber(challenge.target)}
        </div>
      </div>
      <div className={styles.reward}>
        Reward: {challenge.reward.type === 'energy' ? `+${formatNumber(challenge.reward.value)} Energy` :
                 challenge.reward.type === 'click_power' ? `+${challenge.reward.value} Click Power` :
                 `+${challenge.reward.value * 100}% Efficiency`}
      </div>
      {completed && <div className={styles.completed}>✓ Completed!</div>}
    </div>
  );
}
