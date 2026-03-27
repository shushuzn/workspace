// src/components/SeasonPanel.jsx
import { useState, useMemo, memo } from 'react';
import { useSeason } from '../store/SeasonContext';
import SeasonChapterProgress from './SeasonChapterProgress';
import SeasonTaskItem from './SeasonTaskItem';
import styles from './SeasonPanel.module.css';

const CHAPTER_NAMES = {
  1: '第1章「星辰苏醒」',
  2: '第2章「星际征途」',
  3: '第3章「宇宙主宰」',
};

const SeasonPanel = memo(function SeasonPanel() {
  const { state, daysLeft, claimReward, getChapterProgress, getPremiumOwned, setPremiumOwned } = useSeason();
  const [activeTab, setActiveTab] = useState('tasks'); // 'tasks' | 'rewards'
  const premiumOwned = getPremiumOwned();

  if (!state) return null;

  // 各章节进度
  const chapterProgress = {
    1: getChapterProgress(1),
    2: getChapterProgress(2),
    3: getChapterProgress(3),
  };

  // 章节状态
  const getChapterStatus = (ch) => {
    if (ch < state.chapter) return 'completed';
    if (ch === state.chapter) return 'active';
    return 'locked';
  };

  // 按章节筛选任务
  const tasksByChapter = useMemo(() => ({
    1: state.tasks.filter(t => t.chapter === 1),
    2: state.tasks.filter(t => t.chapter === 2),
    3: state.tasks.filter(t => t.chapter === 3),
  }), [state.tasks]);

  // 按章节筛选奖励
  const rewardsByChapter = useMemo(() => ({
    1: state.rewards.filter(r => r.chapter === 1),
    2: state.rewards.filter(r => r.chapter === 2),
    3: state.rewards.filter(r => r.chapter === 3),
  }), [state.rewards]);

  const currentChapterTasks = tasksByChapter[state.chapter] || [];
  const currentChapterRewards = rewardsByChapter[state.chapter] || [];

  const handleBuyPremium = () => {
    setPremiumOwned(true);
  };

  return (
    <div className={styles.panel}>
      {/* 头部 */}
      <div className={styles.header}>
        <div className={styles.seasonTitle}>赛季 {state.seasonId}</div>
        <div className={styles.daysLeft}>剩余 {daysLeft} 天</div>
      </div>

      {/* 章节进度 */}
      <div className={styles.chapters}>
        {[1, 2, 3].map(ch => (
          <SeasonChapterProgress
            key={ch}
            chapter={ch}
            name={CHAPTER_NAMES[ch]}
            progress={chapterProgress[ch]}
            status={getChapterStatus(ch)}
          />
        ))}
      </div>

      {/* Tab 切换 */}
      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${activeTab === 'tasks' ? styles.tabActive : ''}`}
          onClick={() => setActiveTab('tasks')}
        >
          任务
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'rewards' ? styles.tabActive : ''}`}
          onClick={() => setActiveTab('rewards')}
        >
          奖励
        </button>
      </div>

      {/* 内容区 */}
      <div className={styles.content}>
        {activeTab === 'tasks' && (
          <div className={styles.taskList}>
            {currentChapterTasks.map(task => (
              <SeasonTaskItem key={task.id} task={task} />
            ))}
          </div>
        )}

        {activeTab === 'rewards' && (
          <div className={styles.rewardList}>
            {/* 免费奖励 */}
            <div className={styles.rewardSection}>
              <div className={styles.rewardSectionTitle}>免费奖励</div>
              {currentChapterRewards
                .filter(r => r.tier === 'free')
                .map(reward => (
                  <div key={reward.id} className={styles.rewardItem}>
                    <div className={styles.rewardInfo}>
                      <div className={styles.rewardName}>{reward.name}</div>
                      <div className={styles.rewardDesc}>{reward.description}</div>
                    </div>
                    {reward.claimed ? (
                      <span className={styles.rewardClaimed}>已领取</span>
                    ) : chapterProgress[state.chapter] >= reward.unlockAt ? (
                      <button
                        className={styles.claimBtn}
                        onClick={() => claimReward(reward.id)}
                      >
                        可领取!
                      </button>
                    ) : (
                      <span className={styles.rewardLocked}>
                        🔒 [{chapterProgress[state.chapter]}/{reward.unlockAt}]
                      </span>
                    )}
                  </div>
                ))}
            </div>

            {/* 高级奖励 */}
            <div className={styles.rewardSection}>
              <div className={styles.rewardSectionTitle}>高级奖励</div>
              {!premiumOwned && (
                <div className={styles.premiumBanner}>
                  <button
                    className={styles.buyPremiumBtn}
                    onClick={handleBuyPremium}
                  >
                    购买高级通行证 - 5000 星尘
                  </button>
                </div>
              )}
              {currentChapterRewards
                .filter(r => r.tier === 'premium')
                .map(reward => (
                  <div
                    key={reward.id}
                    className={`${styles.rewardItem} ${!premiumOwned ? styles.rewardItemLocked : ''}`}
                  >
                    <div className={styles.rewardInfo}>
                      <div className={styles.rewardName}>{reward.name}</div>
                      <div className={styles.rewardDesc}>{reward.description}</div>
                    </div>
                    {!premiumOwned ? (
                      <span className={styles.rewardLocked}>🔒 需高级通行证</span>
                    ) : reward.claimed ? (
                      <span className={styles.rewardClaimed}>已领取</span>
                    ) : chapterProgress[state.chapter] >= reward.unlockAt ? (
                      <button
                        className={styles.claimBtn}
                        onClick={() => claimReward(reward.id)}
                      >
                        可领取!
                      </button>
                    ) : (
                      <span className={styles.rewardLocked}>
                        🔒 [{chapterProgress[state.chapter]}/{reward.unlockAt}]
                      </span>
                    )}
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

export default SeasonPanel;
