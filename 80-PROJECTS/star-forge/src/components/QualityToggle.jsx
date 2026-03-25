import { useQuality } from '../store/QualityContext';
import { useLanguage } from '../i18n/LanguageContext';
import styles from './QualityToggle.module.css';

export default function QualityToggle() {
  const { quality, changeQuality } = useQuality();
  const { t } = useLanguage();

  const qualityOptions = [
    { value: 'low', label: t('quality.low'), icon: '🔋' },
    { value: 'medium', label: t('quality.medium'), icon: '⚖️' },
    { value: 'high', label: t('quality.high'), icon: '🎨' },
  ];

  return (
    <div className={styles.container}>
      <span className={styles.label}>{t('quality.title')}</span>
      <div className={styles.buttons}>
        {qualityOptions.map((option) => (
          <button
            key={option.value}
            className={`${styles.btn} ${quality === option.value ? styles.active : ''}`}
            onClick={() => changeQuality(option.value)}
            title={`${option.label}${t('quality.title')}`}
          >
            <span className={styles.icon}>{option.icon}</span>
            <span className={styles.labelText}>{option.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
