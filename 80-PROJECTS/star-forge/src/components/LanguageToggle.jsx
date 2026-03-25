import { useLanguage } from '../i18n/LanguageContext';
import styles from './LanguageToggle.module.css';

export default function LanguageToggle() {
  const { language, toggleLanguage } = useLanguage();

  return (
    <button 
      className={styles.toggle}
      onClick={toggleLanguage}
      title={language === 'en' ? '切换到中文' : 'Switch to English'}
      aria-label={language === 'en' ? '切换到中文' : 'Switch to English'}
    >
      <span className={styles.icon}>🌐</span>
      <span className={styles.label}>{language === 'en' ? '中文' : 'EN'}</span>
    </button>
  );
}
