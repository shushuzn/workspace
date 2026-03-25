import { useLanguage } from '../i18n/LanguageContext';
import styles from './LanguageToggle.module.css';

export default function LanguageToggle({ collapsed = false }) {
  const { language, toggleLanguage } = useLanguage();

  return (
    <button 
      className={`${styles.toggle} ${collapsed ? styles.collapsed : ''}`}
      onClick={toggleLanguage}
      title={language === 'en' ? '切换到中文' : 'Switch to English'}
    >
      <span className={styles.icon}>🌐</span>
      {!collapsed && <span className={styles.label}>{language === 'en' ? '中文' : 'EN'}</span>}
    </button>
  );
}
