import { useState, useEffect } from 'react';
import styles from './Leaderboard.module.css';

export default function Leaderboard({ onClose }) {
  const [scores, setScores] = useState([]);
  const [playerScore, setPlayerScore] = useState(null);

  useEffect(() => {
    // Load scores from localStorage
    const savedScores = localStorage.getItem('starforge_leaderboard');
    if (savedScores) {
      const parsedScores = JSON.parse(savedScores);
      // Sort by total energy earned
      parsedScores.sort((a, b) => b.totalEnergyEarned - a.totalEnergyEarned);
      setScores(parsedScores.slice(0, 100)); // Top 100
    }

    // Get current player score
    const currentSave = localStorage.getItem('starforge_save');
    if (currentSave) {
      const save = JSON.parse(currentSave);
      setPlayerScore({
        name: 'You',
        totalEnergyEarned: save.totalEnergyEarned || 0,
        totalClicks: save.totalClicks || 0,
        totalPrestiges: save.totalPrestiges || 0,
      });
    }
  }, []);

  const submitScore = () => {
    if (!playerScore) return;
    
    const playerName = prompt('Enter your name for the leaderboard:', 'Player');
    if (!playerName) return;

    const newScore = {
      ...playerScore,
      name: playerName,
      date: new Date().toISOString(),
    };

    const savedScores = JSON.parse(localStorage.getItem('starforge_leaderboard') || '[]');
    savedScores.push(newScore);
    savedScores.sort((a, b) => b.totalEnergyEarned - a.totalEnergyEarned);
    localStorage.setItem('starforge_leaderboard', JSON.stringify(savedScores.slice(0, 100)));
    setScores(savedScores.slice(0, 100));
  };

  const formatNumber = (num) => {
    if (num >= 1e15) return (num / 1e15).toFixed(2) + 'Q';
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toFixed(0);
  };

  return (
    <div className={styles.modal}>
      <div className={styles.backdrop} onClick={onClose} />
      <div className={styles.content}>
        <button className={styles.closeBtn} onClick={onClose}>×</button>
        
        <h2 className={styles.title}>🏆 Leaderboard</h2>
        
        {playerScore && (
          <div className={styles.playerScore}>
            <span>Your Best:</span>
            <strong>{formatNumber(playerScore.totalEnergyEarned)}</strong>
            <button className={styles.submitBtn} onClick={submitScore}>
              Submit Score
            </button>
          </div>
        )}

        <div className={styles.table}>
          <div className={styles.header}>
            <span className={styles.rank}>#</span>
            <span className={styles.name}>Player</span>
            <span className={styles.energy}>Energy</span>
            <span className={styles.clicks}>Clicks</span>
          </div>
          
          <div className={styles.list}>
            {scores.length === 0 ? (
              <div className={styles.empty}>No scores yet. Be the first!</div>
            ) : (
              scores.map((score, index) => (
                <div key={index} className={`${styles.row} ${index < 3 ? styles[`rank${index + 1}`] : ''}`}>
                  <span className={styles.rank}>
                    {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : index + 1}
                  </span>
                  <span className={styles.name}>{score.name}</span>
                  <span className={styles.energy}>{formatNumber(score.totalEnergyEarned)}</span>
                  <span className={styles.clicks}>{formatNumber(score.totalClicks)}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
