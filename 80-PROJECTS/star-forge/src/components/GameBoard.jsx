import { useState, useEffect } from 'react';
import { useGame } from '../store/GameContext';
import { useLanguage } from '../i18n/LanguageContext';
import { useSaveLoad } from '../hooks/useSaveLoad';
import ResourceDisplay from './ResourceDisplay';
import TabPanel from './TabPanel';
import AchievementToast from './AchievementToast';
import styles from './GameBoard.module.css';

export default function GameBoard() {
  const { click, state } = useGame();
  const { t } = useLanguage();
  const { saveGame, loadGame, exportSave, importSave, resetGame, autoSaveEnabled, setAutoSaveEnabled, selectSaveFolder } = useSaveLoad();
  const [showStats, setShowStats] = useState(false);
  const [clickEffects, setClickEffects] = useState([]);
  const [offlineInfo, setOfflineInfo] = useState(null);

  useEffect(() => {
    loadGame();
  }, [loadGame]);

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

  const handleClick = (e) => {
    click();

    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const id = Date.now() + Math.random();

    setClickEffects(prev => [...prev, { id, x, y }]);
    setTimeout(() => {
      setClickEffects(prev => prev.filter(e => e.id !== id));
    }, 600);
  };

  const handleReset = () => {
    if (window.confirm(t('game.confirmReset'))) {
      resetGame();
    }
  };

  return (
    <div className={styles.game}>
      <AchievementToast />

      {offlineInfo && (
        <div className={styles.offlineBanner}>
          {t('game.welcomeBack')} {offlineInfo.earnings.toFixed(0)} {t('game.energyWhileAway')} ({Math.floor(offlineInfo.time / 3600)}h {Math.floor((offlineInfo.time % 3600) / 60)}m)
          <button onClick={() => setOfflineInfo(null)} className={styles.dismissBtn}>×</button>
        </div>
      )}

      <header className={styles.header}>
        <h1 className={styles.title}>{t('app.title')}</h1>
        <div className={styles.headerActions}>
          <button onClick={saveGame} className={styles.headerBtn}>{t('game.save')}</button>
          <button onClick={exportSave} className={styles.headerBtn}>{t('game.export')}</button>
          <input 
            type="file" 
            id="importSave" 
            accept=".json" 
            onChange={(e) => e.target.files[0] && importSave(e.target.files[0])} 
            style={{ display: 'none' }} 
          />
          <label htmlFor="importSave" className={styles.headerBtn}>{t('game.import')}</label>
          <button onClick={() => setAutoSaveEnabled(!autoSaveEnabled)} className={`${styles.headerBtn} ${autoSaveEnabled ? styles.active : ''}`}>
            {autoSaveEnabled ? '📍' : '⚪'} {t('game.autoOn')}
          </button>
          <button onClick={() => setShowStats(!showStats)} className={`${styles.headerBtn} ${showStats ? styles.active : ''}`}>
            📊 {showStats ? t('game.hideStats') : t('game.showStats')}
          </button>
          <button onClick={handleReset} className={styles.headerBtn + ' ' + styles.danger}>{t('game.reset')}</button>
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.leftColumn}>
          <div className={styles.clickArea} onClick={handleClick}>
            <div className={styles.sun}>
              <div className={styles.sunGlow}></div>
              <div className={styles.sunCore}></div>
              <div className={styles.sunRing}></div>
              <div className={styles.sunRing2}></div>
            </div>
            <div className={styles.clickHint}>{t('game.clickToHarvest')}</div>

            {clickEffects.map(effect => (
              <div
                key={effect.id}
                className={styles.clickEffect}
                style={{ left: effect.x, top: effect.y }}
              >
                +{state.clickPower}
              </div>
            ))}
          </div>

          <ResourceDisplay />
        </div>

        <div className={styles.rightColumn}>
          <TabPanel showStats={showStats} />
        </div>
      </main>
    </div>
  );
}
