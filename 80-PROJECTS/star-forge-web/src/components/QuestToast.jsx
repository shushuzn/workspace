import { useState, useEffect } from 'react';
import { QUESTS } from '../data/quests';
import styles from './QuestToast.module.css';

export default function QuestToast({ completedQuestId, onClose }) {
  const [visible, setVisible] = useState(true);

  const quest = QUESTS.find(q => q.id === completedQuestId);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(onClose, 300);
    }, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  if (!visible) return null;

  return (
    <div className={styles.toast}>
      <div className={styles.icon}>📜</div>
      <div className={styles.info}>
        <div className={styles.label}>Quest Completed!</div>
        <div className={styles.name}>{quest?.name}</div>
      </div>
    </div>
  );
}
