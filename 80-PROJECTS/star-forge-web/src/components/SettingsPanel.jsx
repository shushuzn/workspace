import { useState } from 'react';
import QualityToggle from './QualityToggle';
import LanguageToggle from './LanguageToggle';
import ThemeToggle from './ThemeToggle';
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
            <span className={styles.sectionLabel}>{t('settings.theme')}</span>
            <ThemeToggle collapsed />
          </div>
          <div className={styles.divider} />
          <div className={styles.section}>
            <span className={styles.sectionLabel}>{t('settings.language')}</span>
            <LanguageToggle collapsed />
          </div>
          <div className={styles.divider} />
          <div className={styles.section}>
            <span className={styles.sectionLabel}>{t('settings.quality')}</span>
            <QualityToggle collapsed />
          </div>
        </div>
      )}
    </div>
  );
}
