import { useCallback, useEffect, useState } from 'react';
import { useGame } from '../store/GameContext';

export function useSaveLoad() {
  const { state, loadState } = useGame();
  const [lastSave, setLastSave] = useState(null);
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true);
  const [lastAutoSave, setLastAutoSave] = useState(null);
  const [backupCount, setBackupCount] = useState(0);
  const [saveFolder, setSaveFolder] = useState(null);

  // Enhanced save function with backup
  const saveGame = useCallback(() => {
    const saveData = {
      ...state,
      lastSaveTime: Date.now(),
      version: '1.0.0',
    };
    
    // Save to main storage
    localStorage.setItem('starforge_save', JSON.stringify(saveData));
    
    // Create backup
    const backups = JSON.parse(localStorage.getItem('starforge_backups') || '[]');
    backups.push({
      timestamp: Date.now(),
      data: saveData,
    });
    
    // Keep only last 5 backups
    const trimmedBackups = backups.slice(-5);
    localStorage.setItem('starforge_backups', JSON.stringify(trimmedBackups));
    setBackupCount(trimmedBackups.length);
    
    setLastSave(new Date());
    console.log('Game saved with backup', trimmedBackups.length);
  }, [state]);

  const loadGame = useCallback(() => {
    const savedData = localStorage.getItem('starforge_save');
    if (savedData) {
      try {
        const saved = JSON.parse(savedData);
        loadState(saved);
        return true;
      } catch (e) {
        console.warn('Failed to load save:', e);
        // Try to load from backup
        const backups = JSON.parse(localStorage.getItem('starforge_backups') || '[]');
        if (backups.length > 0) {
          const latestBackup = backups[backups.length - 1];
          try {
            loadState(latestBackup.data);
            console.log('Loaded from backup');
            return true;
          } catch (backupError) {
            console.warn('Failed to load from backup:', backupError);
          }
        }
        return false;
      }
    }
    return false;
  }, [loadState]);

  const exportSave = useCallback(() => {
    const saveData = {
      ...state,
      lastSaveTime: Date.now(),
      version: '1.0.0',
    };
    const blob = new Blob([JSON.stringify(saveData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `starforge_save_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [state]);

  const importSave = useCallback((file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const saved = JSON.parse(e.target.result);
        loadState(saved);
        saveGame(); // Save imported data
        return true;
      } catch (err) {
        console.warn('Failed to import save:', err);
        return false;
      }
    };
    reader.readAsText(file);
  }, [loadState, saveGame]);

  const resetGame = useCallback(() => {
    if (window.confirm('Are you sure you want to reset all progress? This cannot be undone.')) {
      localStorage.removeItem('starforge_save');
      localStorage.removeItem('starforge_backups');
      localStorage.removeItem('starforge_offline');
      window.location.reload();
    }
  }, []);

  // Load backups
  const loadBackup = useCallback((backupIndex) => {
    const backups = JSON.parse(localStorage.getItem('starforge_backups') || '[]');
    if (backups[backupIndex]) {
      try {
        loadState(backups[backupIndex].data);
        saveGame(); // Save loaded backup as current
        return true;
      } catch (e) {
        console.warn('Failed to load backup:', e);
        return false;
      }
    }
    return false;
  }, [loadState, saveGame]);

  // Get backups
  const getBackups = useCallback(() => {
    return JSON.parse(localStorage.getItem('starforge_backups') || '[]');
  }, []);

  // Open file dialog for save folder
  const selectSaveFolder = useCallback(() => {
    // In browser environment, we can only suggest the user to create a folder
    // and manually manage save files
    const folderName = 'StarForgeSaves';
    const message = `请在您喜欢的位置创建一个名为 "${folderName}" 的文件夹，然后使用导出功能将存档保存到该文件夹中。\n\n这样您就可以在文件夹中管理游戏存档了。`;
    alert(message);
    setSaveFolder(folderName);
  }, []);

  // Auto save functionality
  useEffect(() => {
    if (!autoSaveEnabled) return;

    const autoSaveInterval = setInterval(() => {
      saveGame();
      setLastAutoSave(new Date());
      console.log('Auto saved game at', new Date().toLocaleTimeString());
    }, 30000); // 30 seconds auto save

    return () => clearInterval(autoSaveInterval);
  }, [autoSaveEnabled, saveGame]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        saveGame();
      }
      if (e.ctrlKey && e.key === 'a') {
        e.preventDefault();
        setAutoSaveEnabled(!autoSaveEnabled);
      }
      if (e.ctrlKey && e.key === 'f') {
        e.preventDefault();
        selectSaveFolder();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [saveGame, autoSaveEnabled, setAutoSaveEnabled, selectSaveFolder]);

  return {
    saveGame,
    loadGame,
    exportSave,
    importSave,
    resetGame,
    loadBackup,
    getBackups,
    selectSaveFolder,
    lastSave,
    autoSaveEnabled,
    setAutoSaveEnabled,
    lastAutoSave,
    backupCount,
    saveFolder,
  };
}
