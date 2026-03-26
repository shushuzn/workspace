import { useMemo, memo } from 'react';
import { useGame } from '../store/GameContext';
import { QUESTS, checkQuestProgress } from '../data/quests';
import { formatNumber } from '../utils/format';
import styles from './QuestPanel.module.css';

const QuestItem = memo(function QuestItem({ quest, progress, isComplete, onClaim, completed }) {
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
    <div className={styles.questItem}>
      <div className={styles.questItemInfo}>
        <span className={styles.questItemName}>{quest.name}</span>
        <span className={styles.questItemTarget}>
          {formatNumber(progress)} / {formatNumber(quest.target)}
        </span>
      </div>
      <div className={styles.questItemReward}>{getRewardText(quest.reward)}</div>
    </div>
  );
});

export default memo(function QuestPanel() {
  const { state, completeQuest } = useGame();

  const completedSet = useMemo(() => new Set(state.completedQuests || []), [state.completedQuests]);

  const { activeQuests, currentQuest, questProgressMap } = useMemo(() => {
    const active = QUESTS.filter(q => !completedSet.has(q.id));
    const progressMap = {};
    for (const quest of active) {
      progressMap[quest.id] = checkQuestProgress(state, quest);
    }
    return { activeQuests: active, currentQuest: active[0], questProgressMap: progressMap };
  }, [completedSet, state]);

  const currentProgress = currentQuest ? questProgressMap[currentQuest.id] : 0;
  const isCurrentComplete = currentQuest && currentProgress >= currentQuest.target;

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
          <span>{completedSet.size}/{QUESTS.length}</span>
        </div>
        <div className={styles.progressTrack}>
          <div
            className={styles.progressFill}
            style={{ width: `${(completedSet.size / QUESTS.length) * 100}%` }}
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
                style={{ width: `${Math.min(currentProgress / currentQuest.target * 100, 100)}%` }}
              />
            </div>
            <div className={styles.questProgressText}>
              {formatNumber(currentProgress)} / {formatNumber(currentQuest.target)}
            </div>
          </div>
          {isCurrentComplete && !completedSet.has(currentQuest.id) && (
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
          <QuestItem
            key={quest.id}
            quest={quest}
            progress={questProgressMap[quest.id] || 0}
            isComplete={questProgressMap[quest.id] >= quest.target}
            completed={completedSet.has(quest.id)}
          />
        ))}
      </div>
    </div>
  );
});
