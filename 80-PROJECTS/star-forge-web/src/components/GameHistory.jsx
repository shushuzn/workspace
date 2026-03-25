import { useState, useEffect } from 'react';
import { useGame } from '../store/GameContext';
import { formatNumber, formatTime } from '../utils/format';
import styles from './GameHistory.module.css';

export default function GameHistory() {
  const { state } = useGame();
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const interval = setInterval(() => {
      const history = JSON.parse(localStorage.getItem('starforge_history') || '[]');
      setEvents(history.slice(0, 20));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const getEventIcon = (type) => {
    switch (type) {
      case 'click': return '👆';
      case 'building': return '🏗️';
      case 'upgrade': return '⬆️';
      case 'prestige': return '🌟';
      case 'milestone': return '🎯';
      default: return '⚡';
    }
  };

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>📊 Recent Events</h3>
      {events.length === 0 ? (
        <div className={styles.empty}>No events yet...</div>
      ) : (
        <div className={styles.list}>
          {events.map((e, i) => (
            <div key={i} className={styles.event}>
              <span className={styles.icon}>{getEventIcon(e.type)}</span>
              <span className={styles.desc}>{e.message}</span>
              <span className={styles.time}>{formatTime(e.time)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
