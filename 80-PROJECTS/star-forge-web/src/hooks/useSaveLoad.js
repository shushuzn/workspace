import { useCallback, useEffect, useRef } from 'react';
import { useGame } from '../store/GameContext';

export function useSaveLoad() {
  const { state, loadState } = useGame();
  const lastAutoSaveRef = useRef(0);
  const saveGameRef = useRef(null);

  const saveGame = useCallback(() => {
    try {
      const saveData = {
        ...state,
        lastSaveTime: Date.now(),
      };
      localStorage.setItem('starforge_save', JSON.stringify(saveData));
      return true;
    } catch (e) {
      console.error('Failed to save:', e);
      return false;
    }
  }, [state]);

  // 优化：保持ref更新
  saveGameRef.current = saveGame;

  // 自动存档：每30秒一次，限制最小间隔5秒
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      if (now - lastAutoSaveRef.current < 5000) return;
      lastAutoSaveRef.current = now;
      saveGameRef.current?.();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  // 计算离线收益 - 优化版本
  const calculateOfflineEarnings = useCallback((savedState, offlineSeconds) => {
    if (!savedState.energyPerSecond || savedState.energyPerSecond <= 0) return 0;
    
    const offlineRate = savedState.offlineRate || 1;
    const earningsPerSecond = savedState.energyPerSecond * offlineRate;
    const cappedTime = Math.min(offlineSeconds, 8 * 60 * 60); // 最多8小时
    
    return Math.floor(earningsPerSecond * cappedTime * 0.5);
  }, []);

  const loadGame = useCallback(() => {
    try {
      const savedData = localStorage.getItem('starforge_save');
      if (!savedData) return false;
      
      const saved = JSON.parse(savedData);
      loadState(saved);
      
      if (saved.lastSaveTime) {
        const offlineTime = (Date.now() - saved.lastSaveTime) / 1000;
        if (offlineTime > 60) {
          const offlineEarnings = calculateOfflineEarnings(saved, offlineTime);
          if (offlineEarnings > 0) {
            localStorage.setItem('starforge_offline', JSON.stringify({
              earnings: offlineEarnings,
              time: offlineTime
            }));
          }
        }
      }
      return true;
    } catch (e) {
      console.warn('Failed to load save:', e);
      return false;
    }
  }, [loadState, calculateOfflineEarnings]);

  // 优化：导出使用更小的JSON
  const exportSave = useCallback(() => {
    try {
      const saveData = {
        ...state,
        lastSaveTime: Date.now(),
        exportedAt: new Date().toISOString(),
      };
      const blob = new Blob([JSON.stringify(saveData)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `starforge_save_${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      return true;
    } catch (e) {
      console.error('Failed to export:', e);
      return false;
    }
  }, [state]);

  const importSave = useCallback((file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const saved = JSON.parse(e.target.result);
          loadState(saved);
          resolve(true);
        } catch (err) {
          reject(err);
        }
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsText(file);
    });
  }, [loadState]);

  const resetGame = useCallback(() => {
    if (window.confirm('确定要重置所有进度吗？此操作无法撤销。')) {
      localStorage.removeItem('starforge_save');
      localStorage.removeItem('starforge_offline');
      localStorage.removeItem('starforge_autosave');
      localStorage.removeItem('starforge-milestones');
      window.location.reload();
    }
  }, []);

  // 键盘快捷键
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        saveGame();
      }
      if (e.ctrlKey && e.shiftKey && e.key === 'e') {
        e.preventDefault();
        exportSave();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [saveGame, exportSave]);

  return {
    saveGame,
    loadGame,
    exportSave,
    importSave,
    resetGame,
  };
}
