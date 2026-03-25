import { useState, useEffect } from 'react';
import styles from './HotkeyHint.module.css';

const HOTKEYS = [
  { key: '空格', action: '点击太阳', icon: '☀️' },
  { key: 'B', action: '建筑面板', icon: '🏗️' },
  { key: 'U', action: '升级面板', icon: '⬆️' },
  { key: 'P', action: '转生面板', icon: '🔄' },
  { key: 'Q', action: '任务面板', icon: '📋' },
  { key: 'S', action: '统计面板', icon: '📊' },
  { key: 'T', action: '教程提示', icon: '❓' },
  { key: 'Esc', action: '关闭弹窗', icon: '✖️' },
];

export default function HotkeyHint() {
  const [showHints, setShowHints] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'h' || e.key === 'H') {
        setShowHints(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className={styles.container}>
      <button 
        className={styles.toggleBtn}
        onClick={() => setShowHints(!showHints)}
        title="快捷键 (H)"
      >
        ⌨️
      </button>
      
      {showHints && (
        <div className={styles.hintsPanel}>
          <h3 className={styles.title}>⌨️ 键盘快捷键</h3>
          <div className={styles.hintList}>
            {HOTKEYS.map((hotkey, index) => (
              <div key={index} className={styles.hintItem}>
                <kbd className={styles.key}>{hotkey.key}</kbd>
                <span className={styles.action}>{hotkey.icon} {hotkey.action}</span>
              </div>
            ))}
          </div>
          <div className={styles.footer}>按 H 键切换显示</div>
        </div>
      )}
    </div>
  );
}
