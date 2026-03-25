import { useGame } from '../store/GameContext';
import { QUESTS, checkQuestProgress } from '../data/quests';
import { formatNumber } from '../utils/format';
import styles from './QuestPanel.module.css';

export default function QuestPanel() {
  const { state, completeQuest } = useGame();

  const completedQuests = state.completedQuests || [];
  const activeQuests = QUESTS.filter(q => !completedQuests.includes(q.id));
  const currentQuest = activeQuests[0];

  const getQuestProgress = (quest) => {
    const progress = checkQuestProgress(state, quest);
    return progress;
  };

  const isQuestComplete = (quest) => {
    return getQuestProgress(quest) >= quest.target;
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

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Quests</h2>
      
      <div className={styles.progressBar}>
        <div className={styles.progressLabel}>
          <span>Progress</span>
          <span>{completedQuests.length}/{QUESTS.length}</span>
        </div>
        <div className={styles.progressTrack}>
          <div 
            className={styles.progressFill}
            style={{ width: `${(completedQuests.length / QUESTS.length) * 100}%` }}
          />
        </div>
      </div>

      {currentQuest ? (
        <div className={styles.currentQuest}>
          <div className={styles.questHeader}>
            <span className={styles.questTier}>Tier {currentQuest.tier}</span>
            <span className={styles.questReward}>{getRewardText(currentQuest.reward)}</span>
          </div>
          <div className={styles.questName}>{currentQuest.name}</div>
          <div className={styles.questDesc}>{currentQuest.description}</div>
          <div className={styles.questProgress}>
            <div className={styles.questProgressTrack}>
              <div 
                className={styles.questProgressFill}
                style={{ width: `${Math.min(getQuestProgress(currentQuest) / currentQuest.target * 100, 100)}%` }}
              />
            </div>
            <div className={styles.questProgressText}>
              {formatNumber(getQuestProgress(currentQuest))} / {formatNumber(currentQuest.target)}
            </div>
          </div>
          {isQuestComplete(currentQuest) && !completedQuests.includes(currentQuest.id) && (
            <button className={styles.claimBtn} onClick={() => completeQuest(currentQuest.id)}>
              Claim Reward!
            </button>
          )}
        </div>
      ) : (
        <div className={styles.allComplete}>
          🎉 All quests completed!
        </div>
      )}

      <div className={styles.questList}>
        <div className={styles.listTitle}>Available Quests</div>
        {activeQuests.slice(1, 6).map((quest) => (
          <div key={quest.id} className={styles.questItem}>
            <div className={styles.questItemInfo}>
              <span className={styles.questItemName}>{quest.name}</span>
              <span className={styles.questItemTarget}>
                {formatNumber(checkQuestProgress(state, quest))} / {formatNumber(quest.target)}
              </span>
            </div>
            <div className={styles.questItemReward}>{getRewardText(quest.reward)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
