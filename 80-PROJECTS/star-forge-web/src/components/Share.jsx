import { useState } from 'react';
import { useGame } from '../store/GameContext';
import styles from './Share.module.css';

export default function Share() {
  const { state } = useGame();
  const [copied, setCopied] = useState(false);

  const generateShareText = () => {
    return `⚡ Star Forge ⚡
    
🏆 Achievements: ${state.achievements?.length || 0}
🏗️ Buildings: ${Object.values(state.buildings || {}).reduce((a, b) => a + b, 0)}
⭐ Prestiges: ${state.totalPrestiges || 0}
⚡ Total Energy: ${(state.totalEnergyEarned || 0).toLocaleString()}
💫 Eternity Points: ${state.eternityPoints || 0}

Play now: ${window.location.href}`;
  };

  const share = async () => {
    const text = generateShareText();
    if (navigator.share) {
      try {
        await navigator.share({ text });
      } catch (e) {}
    } else {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <button className={styles.btn} onClick={share}>
      {copied ? '✅ Copied!' : '📤 Share'}
    </button>
  );
}
