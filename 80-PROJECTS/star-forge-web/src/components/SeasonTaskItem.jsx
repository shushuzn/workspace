// src/components/SeasonTaskItem.jsx
import { memo } from 'react';
import styles from './SeasonPanel.module.css';

const SeasonTaskItem = memo(function SeasonTaskItem({ task }) {
  const done = task.progress >= task.target;
  const typeIcon = task.type === 'auto' ? '⚡' : '🎯';

  return (
    <div className={`${styles.taskItem} ${done ? styles.taskDone : ''}`}>
      <div className={styles.taskIcon}>{typeIcon}</div>
      <div className={styles.taskInfo}>
        <div className={styles.taskTitle}>{task.title}</div>
        <div className={styles.taskDesc}>{task.description}</div>
      </div>
      <div className={styles.taskProgress}>
        {done ? (
          <span className={styles.taskDoneTag}>已完成</span>
        ) : (
          <span className={styles.taskProgressText}>
            [{task.progress}/{task.target}]
          </span>
        )}
      </div>
    </div>
  );
});

export default SeasonTaskItem;
