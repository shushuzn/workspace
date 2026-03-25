import { useState } from 'react';
import { useSaveLoad } from '../hooks/useSaveLoad';
import styles from './SaveLoadPanel.module.css';

export default function SaveLoadPanel() {
  const { saveGame, loadGame, exportSave, importSave } = useSaveLoad();
  const [showPanel, setShowPanel] = useState(false);
  const [lastSaved, setLastSaved] = useState(() => {
    const saved = localStorage.getItem('starforge_save');
    if (saved) {
      try {
        const data = JSON.parse(saved);
        return data.lastSaveTime ? new Date(data.lastSaveTime) : null;
      } catch { return null; }
    }
    return null;
  });

  const handleSave = () => {
    saveGame();
    setLastSaved(new Date());
  };

  const handleImport = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      importSave(file)
        .then(() => {
          alert('存档导入成功!');
          window.location.reload();
        })
        .catch(() => alert('导入失败'));
    }
  };

  const formatDate = (date) => {
    if (!date) return '从未';
    const now = new Date();
    const diff = now - date;
    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`;
    return date.toLocaleDateString();
  };

  return (
    <div className={styles.container}>
      <button 
        className={styles.toggleBtn}
        onClick={() => setShowPanel(!showPanel)}
        title="存档"
      >
        <span className={styles.icon}>💾</span>
      </button>

      {showPanel && (
        <div className={styles.panel}>
          <div className={styles.header}>
            <h3>💾 存档管理</h3>
            <button className={styles.closeBtn} onClick={() => setShowPanel(false)}>×</button>
          </div>

          <div className={styles.status}>
            <div className={styles.statusItem}>
              <span className={styles.label}>上次存档:</span>
              <span className={styles.value}>{formatDate(lastSaved)}</span>
            </div>
          </div>

          <div className={styles.actions}>
            <button onClick={handleSave} className={styles.btn}>
              💾 立即存档
            </button>
            <button onClick={exportSave} className={styles.btn}>
              📤 导出存档
            </button>
            <label className={styles.btn}>
              📥 导入存档
              <input
                type="file"
                accept=".json"
                onChange={handleImport}
                style={{ display: 'none' }}
              />
            </label>
          </div>

          <div className={styles.shortcuts}>
            <small>快捷键: Ctrl+S 存档, Ctrl+Shift+E 导出</small>
          </div>
        </div>
      )}
    </div>
  );
}
