import { useState, useEffect } from 'react';
import { useGame } from '../store/GameContext';
import { DAILY_REWARDS } from '../data/quests';
import { formatNumber } from '../utils/format';
import styles from './DailyRewards.module.css';

export default function DailyRewards() {
  const { state, loadState } = useGame();
  const [showModal, setShowModal] = useState(false);
  const [streak, setStreak] = useState(1);
  const [lastClaim, setLastClaim] = useState(null);
  const [canClaim, setCanClaim] = useState(false);

  useEffect(() => {
    // Check if can claim today
    const lastClaimTime = localStorage.getItem('starforge_last_daily_claim');
    const savedStreak = parseInt(localStorage.getItem('starforge_daily_streak') || '1');
    
    if (lastClaimTime) {
      const lastDate = new Date(parseInt(lastClaimTime));
      const now = new Date();
      const daysDiff = Math.floor((now - lastDate) / (1000 * 60 * 60 * 24));
      
      if (daysDiff === 0) {
        setCanClaim(false);
        setLastClaim(lastDate);
        setStreak(savedStreak);
      } else if (daysDiff === 1) {
        setCanClaim(true);
        setStreak(savedStreak);
      } else {
        // Streak broken
        setCanClaim(true);
        setStreak(1);
        localStorage.setItem('starforge_daily_streak', '1');
      }
    } else {
      setCanClaim(true);
    }

    // Show modal on first visit or if can claim
    if (canClaim || !lastClaimTime) {
      setShowModal(true);
    }
  }, []);

  const claimReward = () => {
    const dayIndex = Math.min(streak - 1, DAILY_REWARDS.length - 1);
    const reward = DAILY_REWARDS[dayIndex];
    
    // Apply reward based on type
    switch (reward.type) {
      case 'energy':
        // Would need to dispatch action to add energy
        break;
      case 'click_power':
        // Would need to dispatch action to add click power
        break;
      case 'global_efficiency':
        // Would need to dispatch action to add efficiency
        break;
      case 'global_multiplier':
        // Would need to dispatch action to add multiplier
        break;
    }

    localStorage.setItem('starforge_last_daily_claim', Date.now().toString());
    localStorage.setItem('starforge_daily_streak', (streak + 1).toString());
    
    setLastClaim(new Date());
    setStreak(streak + 1);
    setCanClaim(false);
    setShowModal(false);
  };

  const getCurrentReward = () => {
    const dayIndex = Math.min(streak - 1, DAILY_REWARDS.length - 1);
    return DAILY_REWARDS[dayIndex];
  };

  const getRewardText = (reward) => {
    switch (reward.type) {
      case 'energy':
        return `⚡ ${formatNumber(reward.value)}`;
      case 'click_power':
        return `+${reward.value} Click Power`;
      case 'global_efficiency':
        return `+${(reward.value * 100).toFixed(0)}% Efficiency`;
      case 'global_multiplier':
        return `×${reward.value} Multiplier`;
      default:
        return 'Reward';
    }
  };

  if (!showModal) return null;

  return (
    <div className={styles.modal}>
      <div className={styles.modalBackdrop} onClick={() => setShowModal(false)} />
      <div className={styles.modalContent}>
        <div className={styles.header}>
          <h2 className={styles.title}>🎁 Daily Reward</h2>
          <p className={styles.streak}>Day {streak} Streak 🔥</p>
        </div>

        <div className={styles.rewardCard}>
          <div className={styles.rewardDay}>Day {streak}</div>
          <div className={styles.rewardName}>{getCurrentReward().name}</div>
          <div className={styles.rewardValue}>{getRewardText(getCurrentReward())}</div>
        </div>

        <div className={styles.calendar}>
          {DAILY_REWARDS.slice(0, 7).map((reward, index) => (
            <div 
              key={index}
              className={`${styles.calendarDay} ${index < streak - 1 ? styles.claimed : ''} ${index === streak - 1 ? styles.current : ''}`}
            >
              <span className={styles.dayNumber}>{reward.day}</span>
              <span className={styles.dayIcon}>
                {index < streak - 1 ? '✓' : '?'}
              </span>
            </div>
          ))}
        </div>

        <button 
          className={styles.claimButton}
          onClick={claimReward}
          disabled={!canClaim}
        >
          {canClaim ? 'Claim Reward' : 'Come Back Tomorrow'}
        </button>
      </div>
    </div>
  );
}
