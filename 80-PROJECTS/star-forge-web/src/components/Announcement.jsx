import { useState, useEffect } from 'react';
import styles from './Announcement.module.css';

export default function Announcement({ message, type = 'info', duration = 5000, onClose }) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(onClose, 300);
    }, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  if (!visible) return null;

  return (
    <div className={`${styles.announcement} ${styles[type]}`}>
      <span className={styles.icon}>
        {type === 'success' && '🎉'}
        {type === 'warning' && '⚠️'}
        {type === 'error' && '❌'}
        {type === 'info' && 'ℹ️'}
      </span>
      <span className={styles.message}>{message}</span>
      <button className={styles.close} onClick={() => { setVisible(false); onClose(); }}>×</button>
    </div>
  );
}
