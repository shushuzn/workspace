import { useState } from 'react';
import ThemeToggle from './ThemeToggle';
import LanguageToggle from './LanguageToggle';
import QualityToggle from './QualityToggle';
import { useLanguage } from '../i18n/LanguageContext';
import styles from './SettingsPanel.module.css';

export default function SettingsPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const { t } = useLanguage();

  return (
    <div className={styles.container}>
      <button 
        className={styles.toggleBtn}
        onClick={() => setIsOpen(!isOpen)}
        title={t('settings.title')}
      >
        <span className={styles.icon}>⚙️</span>
      </button>

      {isOpen && (
        <div className={styles.panel}>
          <div className={styles.section}>
            <ThemeToggle />
          </div>
          <div className={styles.section}>
            <LanguageToggle />
          </div>
          <div className={styles.section}>
            <QualityToggle />
          </div>
        </div>
      )}
    </div>
  );
}
