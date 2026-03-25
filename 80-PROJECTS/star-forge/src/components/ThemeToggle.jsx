import { useTheme } from '../store/ThemeContext';
import { useLanguage } from '../i18n/LanguageContext';
import styles from './ThemeToggle.module.css';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const { t } = useLanguage();

  return (
    <button 
      className={styles.toggle}
      onClick={toggleTheme}
      title={theme === 'dark' ? t('theme.light') : t('theme.dark')}
      aria-label={theme === 'dark' ? t('theme.light') : t('theme.dark')}
    >
      <span className={styles.icon}>
        {theme === 'dark' ? '☀️' : '🌙'}
      </span>
      <span className={styles.label}>
        {theme === 'dark' ? t('theme.light') : t('theme.dark')}
      </span>
    </button>
  );
}
