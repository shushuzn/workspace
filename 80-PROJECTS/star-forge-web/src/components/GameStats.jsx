import { useMemo } from 'react';
import { useGame } from '../store/GameContext';
import { ACHIEVEMENTS } from '../data/achievements';
import { BUILDINGS, TIERS } from '../data/buildings';
import styles from './GameStats.module.css';

export default function GameStats() {
  const { state } = useGame();

  const stats = useMemo(() => {
    const totalBuildings = Object.values(state.buildings || {}).reduce((a, b) => a + b, 0);
    const ownedBuildings = Object.values(state.buildings || {}).filter(b => b > 0).length;
    const totalTiers = state.unlockedTiers?.length || 1;
    const achievementsEarned = state.achievements?.length || 0;
    const achievementsTotal = ACHIEVEMENTS.length;
    const upgradesPurchased = state.purchasedUpgrades?.length || 0;
    
    const playTimeHours = Math.floor(state.totalPlayTime / 3600);
    const playTimeMinutes = Math.floor((state.totalPlayTime % 3600) / 60);
    
    return {
      totalBuildings,
      ownedBuildings,
      totalTiers,
      achievementsEarned,
      achievementsTotal,
      upgradesPurchased,
      playTimeHours,
      playTimeMinutes,
    };
  }, [state]);

  const tierProgress = useMemo(() => {
    return TIERS.map(tier => ({
      ...tier,
      unlocked: state.unlockedTiers?.includes(tier.id),
    }));
  }, [state.unlockedTiers]);

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>📊 游戏统计</h2>
      
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>⚡ 能量</h3>
        <div className={styles.statsGrid}>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>当前能量</span>
            <span className={styles.statValue}>{Math.floor(state.energy || 0).toLocaleString()}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>累计能量</span>
            <span className={styles.statValue}>{Math.floor(state.totalEnergyEarned || 0).toLocaleString()}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>能量/秒</span>
            <span className={styles.statValue}>{(state.energyPerSecond || 0).toFixed(1)}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>点击力</span>
            <span className={styles.statValue}>{(state.clickPower || 1).toLocaleString()}</span>
          </div>
        </div>
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>🏗️ 建筑</h3>
        <div className={styles.statsGrid}>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>拥有建筑</span>
            <span className={styles.statValue}>{stats.ownedBuildings} / {BUILDINGS.length}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>总建筑数</span>
            <span className={styles.statValue}>{stats.totalBuildings.toLocaleString()}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>已解锁时代</span>
            <span className={styles.statValue}>{stats.totalTiers} / {TIERS.length}</span>
          </div>
        </div>
        
        <div className={styles.tierList}>
          {tierProgress.map(tier => (
            <div key={tier.id} className={`${styles.tierItem} ${tier.unlocked ? styles.unlocked : styles.locked}`}>
              <span className={styles.tierDot} style={{ background: tier.color }}></span>
              <span className={styles.tierName}>{tier.name}</span>
              {tier.unlocked && <span className={styles.tierBadge}>✓</span>}
            </div>
          ))}
        </div>
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>🏆 成就 & 升级</h3>
        <div className={styles.statsGrid}>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>成就</span>
            <span className={styles.statValue}>{stats.achievementsEarned} / {stats.achievementsTotal}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>升级</span>
            <span className={styles.statValue}>{stats.upgradesPurchased}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>总点击</span>
            <span className={styles.statValue}>{(state.totalClicks || 0).toLocaleString()}</span>
          </div>
        </div>
        
        <div className={styles.progressBar}>
          <div 
            className={styles.progressFill} 
            style={{ width: `${(stats.achievementsEarned / stats.achievementsTotal) * 100}%` }}
          />
        </div>
        <span className={styles.progressText}>
          成就完成 {((stats.achievementsEarned / stats.achievementsTotal) * 100).toFixed(1)}%
        </span>
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>⭐ 转生</h3>
        <div className={styles.statsGrid}>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>转生次数</span>
            <span className={styles.statValue}>{state.totalPrestiges || 0}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>永恒点数</span>
            <span className={styles.statValue}>{(state.eternityPoints || 0).toLocaleString()}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statLabel}>永恒因子</span>
            <span className={styles.statValue}>{(state.eternityFactor || 0).toFixed(2)}</span>
          </div>
        </div>
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>⏱️ 游戏时间</h3>
        <div className={styles.playTime}>
          <span className={styles.timeValue}>
            {stats.playTimeHours}h {stats.playTimeMinutes}m
          </span>
          <span className={styles.timeLabel}>游戏时长</span>
        </div>
      </div>

      {state.maxCombo > 1 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>🔥 连击记录</h3>
          <div className={styles.comboStats}>
            <div className={styles.comboItem}>
              <span className={styles.comboValue}>{state.maxCombo}x</span>
              <span className={styles.comboLabel}>最高连击</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
