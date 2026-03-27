// src/components/SeasonChapterProgress.jsx
import { memo } from 'react';
import styles from './SeasonPanel.module.css';

const SeasonChapterProgress = memo(function SeasonChapterProgress({ chapter, name, progress, status }) {
  // status: 'locked' | 'active' | 'completed'
  const statusIcon = {
    locked: '🔒',
    active: '🔄',
    completed: '✅',
  }[status];

  return (
    <div className={`${styles.chapterRow} ${styles[`chapter_${status}`]}`}>
      <div className={styles.chapterHeader}>
        <span className={styles.chapterIcon}>{statusIcon}</span>
        <span className={styles.chapterName}>{name}</span>
        <span className={styles.chapterStatus}>
          {status === 'completed' ? '已完成' : status === 'active' ? '进行中' : '未解锁'}
        </span>
      </div>
      <div className={styles.progressBarContainer}>
        <div
          className={styles.progressBar}
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className={styles.progressText}>{progress}%</div>
    </div>
  );
});

export default SeasonChapterProgress;
