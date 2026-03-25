import { useGame } from '../store/GameContext';
import styles from './StatsPanel.module.css';

export default function StatsPanel() {
  const { state, energyPerSecond } = useGame();

  const formatNumber = (num) => {
    if (num >= 1e30) return num.toExponential(2);
    if (num >= 1e15) return (num / 1e15).toFixed(2) + 'Q';
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return Math.floor(num).toLocaleString();
  };

  const formatTime = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return `${h}h ${m}m ${s}s`;
  };

  const playTime = Math.floor((Date.now() - state.gameStartTime) / 1000);

  return (
    <div className={styles.statsPanel}>
      <h2 className={styles.title}>📊 游戏统计</h2>
      
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>⚡ 能量统计</h3>
        <div className={styles.statsGrid}>
          <div className={styles.statItem}>
            <span className={styles.label}>当前能量</span>
            <span className={styles.value}>{formatNumber(state.energy)}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.label}>每秒产出</span>
            <span className={styles.value}>{formatNumber(energyPerSecond)}/s</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.label}>累计获得</span>
            <span className={styles.value}>{formatNumber(state.totalEnergyEarned)}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.label}>点击加成</span>
            <span className={styles.value}>{formatNumber(state.clickPower)}</span>
          </div>
        </div>
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>🎯 玩法统计</h3>
        <div className={styles.statsGrid}>
          <div className={styles.statItem}>
            <span className={styles.label}>总点击数</span>
            <span className={styles.value}>{formatNumber(state.totalClicks)}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.label}>最高连击</span>
            <span className={styles.value}>{state.maxCombo}x</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.label}>当前连击</span>
            <span className={styles.value}>{state.comboCount}x</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.label}>连击倍率</span>
            <span className={styles.value}>x{state.comboMultiplier.toFixed(1)}</span>
          </div>
        </div>
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>🏗️ 建筑统计</h3>
        <div className={styles.statsGrid}>
          <div className={styles.statItem}>
            <span className={styles.label}>已解锁阶层</span>
            <span className={styles.value}>{state.unlockedTiers.length}/6</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.label}>永恒点数</span>
            <span className={styles.value}>{state.eternityPoints}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.label}>转生次数</span>
            <span className={styles.value}>{state.totalPrestiges}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.label}>永恒因子</span>
            <span className={styles.value}>{state.eternityFactor.toFixed(1)}</span>
          </div>
        </div>
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>⏱️ 时间统计</h3>
        <div className={styles.statsGrid}>
          <div className={styles.statItem}>
            <span className={styles.label}>游戏时长</span>
            <span className={styles.value}>{formatTime(playTime)}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.label}>离线收益</span>
            <span className={styles.value}>x{state.offlineRate.toFixed(1)}</span>
          </div>
        </div>
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>🏆 成就统计</h3>
        <div className={styles.statsGrid}>
          <div className={styles.statItem}>
            <span className={styles.label}>已获成就</span>
            <span className={styles.value}>{state.achievements.length}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.label}>已完成任务</span>
            <span className={styles.value}>{state.completedQuests.length}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
