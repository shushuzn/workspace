import { useState, useEffect, useMemo, useCallback, memo } from 'react';
import { useGame } from '../store/GameContext';
import { useSaveLoad } from '../hooks/useSaveLoad';
import ResourceDisplay from './ResourceDisplay';
import BuildingPanel from './BuildingPanel';
import UpgradePanel from './UpgradePanel';
import PrestigePanel from './PrestigePanel';
import StatsPanel from './StatsPanel';
import AchievementToast from './AchievementToast';
import QuestToast from './QuestToast';
import SettingsPanel from './SettingsPanel';
import SaveLoadPanel from './SaveLoadPanel';
import QuestPanel from './QuestPanel';
import DailyRewards from './DailyRewards';
import Tutorial from './Tutorial';
import Leaderboard from './Leaderboard';
import Milestone from './Milestone';
import SeasonPanel from './SeasonPanel';
import ProgressBar from './ProgressBar';
import styles from './GameBoard.module.css';

// 生成点击粒子效果
const generateClickParticles = (x, y, count = 8) => {
  return Array.from({ length: count }, (_, i) => {
    const angle = (Math.PI * 2 * i) / count + Math.random() * 0.5;
    const speed = 50 + Math.random() * 100;
    return {
      id: `${Date.now()}-${i}`,
      x,
      y,
      endX: x + Math.cos(angle) * speed,
      endY: y + Math.sin(angle) * speed,
      size: 3 + Math.random() * 4,
      delay: Math.random() * 0.1,
    };
  });
};

// 优化的粒子生成 - 使用useMemo避免重复计算
const generateParticles = () => 
  Array.from({ length: 12 }, (_, i) => ({
    id: i,
    left: `${5 + Math.random() * 90}%`,
    delay: `${Math.random() * 8}s`,
    size: 2 + Math.random() * 4,
    duration: 6 + Math.random() * 6,
  }));

// 日冕光线角度 - 预计算
const CORONA_RAYS = [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345];

function GameBoardInner({ click, state, offlineInfo, onDismissOffline }) {
  const { saveGame, exportSave, resetGame } = useSaveLoad();
  const [showStats, setShowStats] = useState(false);
  const [showLeaderboard, setShowLeaderboard] = useState(false);
  const [activeTab, setActiveTab] = useState('buildings');
  const [clickEffects, setClickEffects] = useState([]);
  const [clickParticles, setClickParticles] = useState([]);
  const [sunShake, setSunShake] = useState(false);
  const [sunFlash, setSunFlash] = useState(false);
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');
  
  // 优化的粒子状态
  const particles = useMemo(() => generateParticles(), []);

  // 优化的连击显示计算
  const comboDisplay = useMemo(() => 
    state.comboMultiplier > 1 
      ? `🔥 ${state.comboCount}x Combo! (+${((state.comboMultiplier - 1) * 100).toFixed(0)}%)`
      : null,
    [state.comboMultiplier, state.comboCount]
  );

  // 优化的能量计算
  const energyPerSec = useMemo(() => {
    const base = state.energyPerSecond || 0;
    const auto = (state.autoClickPower || 0) * (state.clickPower || 1);
    return base + auto;
  }, [state.energyPerSecond, state.autoClickPower, state.clickPower]);

  // 优化的点击效果数值
  const clickValue = useMemo(() => 
    Math.floor((state.clickPower || 1) * (state.comboMultiplier || 1)),
    [state.clickPower, state.comboMultiplier]
  );

  // 连击等级样式
  const comboStyle = useMemo(() => {
    if (state.comboMultiplier >= 4) return styles.comboMax;
    if (state.comboMultiplier >= 3) return styles.comboHigh;
    if (state.comboMultiplier >= 2) return styles.comboMedium;
    return '';
  }, [state.comboMultiplier]);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = useCallback(() => 
    setTheme(prev => prev === 'dark' ? 'light' : 'dark'),
  []);

  // 优化的点击处理 - 增强版
  const handleClick = useCallback((e) => {
    click();
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const id = Date.now();
    
    // 添加数字飘字效果
    setClickEffects(prev => {
      const newEffects = [...prev, { id, x, y, value: clickValue, combo: state.comboMultiplier }];
      return newEffects.slice(-8);
    });
    
    // 添加粒子爆炸效果
    const particles = generateClickParticles(x, y, 6 + Math.floor(state.comboMultiplier * 2));
    setClickParticles(prev => [...prev, ...particles].slice(-30));
    
    // 太阳闪烁效果
    setSunFlash(true);
    setTimeout(() => setSunFlash(false), 150);
    
    // 太阳抖动效果（高连击时）
    if (state.comboMultiplier >= 2) {
      setSunShake(true);
      setTimeout(() => setSunShake(false), 200);
    }
    
    // 清理效果
    setTimeout(() => 
      setClickEffects(prev => prev.filter(ef => ef.id !== id)), 
    800);
    
    setTimeout(() => {
      setClickParticles(prev => prev.filter(p => !particles.find(mp => mp.id === p.id)));
    }, 600);
  }, [click, clickValue, state.comboMultiplier]);

  // 优化的标签切换
  const handleTabChange = useCallback((tab) => {
    setActiveTab(tab);
  }, []);

  // 优化的面板组件
  const renderPanel = useMemo(() => {
    switch (activeTab) {
      case 'buildings': return <><ProgressBar /><BuildingPanel /></>;
      case 'upgrades': return <><ProgressBar /><UpgradePanel /></>;
      case 'prestige': return <><ProgressBar /><PrestigePanel /></>;
      case 'quests': return <><ProgressBar /><QuestPanel /></>;
      case 'season': return <><ProgressBar /><SeasonPanel /></>;
      default: return null;
    }
  }, [activeTab]);

  return (
    <div className={styles.game}>
      {/* 多层动态星空背景 */}
      <div className={styles.starfield}>
        <div className={styles.starLayer1} />
        <div className={styles.starLayer2} />
        <div className={styles.starLayer3} />
      </div>

      <AchievementToast />
      <QuestToast />

      {offlineInfo && (
        <div className={styles.offlineBanner}>
          <span>Welcome back! +{offlineInfo.earnings.toFixed(0)} energy ({Math.floor(offlineInfo.time / 3600)}h {Math.floor((offlineInfo.time % 3600) / 60)}m offline)</span>
          <button onClick={onDismissOffline} className={styles.dismissBtn}>×</button>
        </div>
      )}

      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <h1 className={styles.title}>⚡ Star Forge</h1>
          <ResourceDisplay />
        </div>
        <div className={styles.headerRight}>
          <SaveLoadPanel />
          <SettingsPanel />
          <button onClick={() => setShowStats(true)} className={styles.btn}>Stats</button>
          <button onClick={() => setShowLeaderboard(true)} className={styles.btn}>🏆</button>
          <button onClick={resetGame} className={`${styles.btn} ${styles.danger}`}>Reset</button>
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.clickSection}>
          <div className={styles.clickArea} onClick={handleClick}>
            <div className={styles.ambientParticles}>
              {particles.map(p => (
                <div
                  key={p.id}
                  className={styles.particle}
                  style={{
                    left: p.left,
                    bottom: '10%',
                    width: p.size,
                    height: p.size,
                    animationDelay: p.delay,
                    animationDuration: p.duration,
                  }}
                />
              ))}
            </div>
            <div className={`${styles.sunContainer} ${sunShake ? styles.sunShake : ''}`}>
              {/* 太阳外层光晕 */}
              <div className={styles.sunAura} />
              <div className={styles.sunAura2} />
              <div className={styles.sunAura3} />

              {/* 能量流动环 */}
              <div className={styles.energyRing} />
              <div className={styles.energyRing2} />

              <div className={styles.sunOrbit1}>
                <div className={styles.orbitPlanet}></div>
              </div>
              <div className={styles.sunOrbit2}>
                <div className={styles.orbitPlanet2}></div>
              </div>

              {/* 日冕外层发光 */}
              <div className={styles.coronaGlow} />

              <div className={`${styles.sunCorona} ${sunFlash ? styles.sunCoronaFlash : ''}`}>
                {CORONA_RAYS.map((angle, i) => (
                  <div
                    key={i}
                    className={styles.coronaRay}
                    style={{ transform: `rotate(${angle}deg) translateY(-35px)` }}
                  />
                ))}
              </div>
              <div className={`${styles.sun} ${sunFlash ? styles.sunFlash : ''}`}>
                <div className={styles.sunCore}></div>
              </div>
            </div>
            <div className={styles.clickHint}>点击太阳收获能量</div>
            
            {/* 点击粒子效果 */}
            {clickParticles.map(particle => (
              <div
                key={particle.id}
                className={styles.clickParticle}
                style={{
                  left: particle.x,
                  top: particle.y,
                  width: particle.size,
                  height: particle.size,
                  '--end-x': `${particle.endX - particle.x}px`,
                  '--end-y': `${particle.endY - particle.y}px`,
                }}
              />
            ))}
            
            {/* 点击数字飘字 */}
            {clickEffects.map(effect => (
              <div 
                key={effect.id} 
                className={`${styles.clickEffect} ${effect.combo >= 3 ? styles.clickEffectBig : ''}`} 
                style={{ left: effect.x, top: effect.y }}
              >
                +{effect.value}
              </div>
            ))}
          </div>
          {comboDisplay && (
            <div className={`${styles.comboDisplay} ${comboStyle}`}>{comboDisplay}</div>
          )}
          <div className={styles.energyPerSec}>+{energyPerSec.toFixed(1)}/s</div>
          <div className={styles.tipsSection}>
            <div className={styles.tipItem}>💡 快速点击太阳累积连击，最多5倍加成！</div>
          </div>
        </div>

        <div className={styles.rightSection}>
          <div className={styles.tabs}>
            {['buildings', 'upgrades', 'prestige', 'quests', 'season'].map(tab => (
              <button
                key={tab}
                className={`${styles.tab} ${activeTab === tab ? styles.active : ''}`}
                onClick={() => handleTabChange(tab)}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
          <div className={styles.tabContent}>
            {renderPanel}
          </div>
        </div>
      </main>

      {showStats && (
        <div className={styles.modal}>
          <div className={styles.modalBackdrop} onClick={() => setShowStats(false)} />
          <div className={styles.modalContent}>
            <button className={styles.modalClose} onClick={() => setShowStats(false)}>×</button>
            <StatsPanel />
          </div>
        </div>
      )}
      <DailyRewards />
      <Tutorial />
      <Milestone />
      {showLeaderboard && <Leaderboard onClose={() => setShowLeaderboard(false)} />}
    </div>
  );
}

// 使用 memo 优化组件，避免不必要的重渲染
const MemoizedGameBoard = memo(GameBoardInner);

export default function GameBoard() {
  const { click, state } = useGame();
  const [offlineInfo, setOfflineInfo] = useState(null);

  useEffect(() => {
    const offlineData = localStorage.getItem('starforge_offline');
    if (offlineData) {
      try {
        const { earnings, time } = JSON.parse(offlineData);
        setOfflineInfo({ earnings, time });
        localStorage.removeItem('starforge_offline');
      } catch (e) {}
    }
  }, []);

  const handleDismissOffline = useCallback(() => {
    setOfflineInfo(null);
  }, []);

  return (
    <MemoizedGameBoard 
      click={click}
      state={state}
      offlineInfo={offlineInfo}
      onDismissOffline={handleDismissOffline}
    />
  );
}
