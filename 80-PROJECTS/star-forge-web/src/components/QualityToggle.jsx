import { useQuality } from '../store/QualityContext';
import styles from './QualityToggle.module.css';

export default function QualityToggle({ collapsed = false }) {
  const { quality, changeQuality } = useQuality();

  const qualityOptions = [
    { value: 'low', label: collapsed ? '低' : '🔋 低', full: '低画质' },
    { value: 'medium', label: collapsed ? '中' : '⚖️ 中', full: '中画质' },
    { value: 'high', label: collapsed ? '高' : '🎨 高', full: '高画质' },
  ];

  return (
    <div className={`${styles.container} ${collapsed ? styles.collapsed : ''}`}>
      {collapsed ? (
        <div className={styles.buttons}>
          {qualityOptions.map((option) => (
            <button
              key={option.value}
              className={`${styles.btn} ${quality === option.value ? styles.active : ''}`}
              onClick={() => changeQuality(option.value)}
              title={option.full}
            >
              {option.label}
            </button>
          ))}
        </div>
      ) : (
        <div className={styles.buttons}>
          {qualityOptions.map((option) => (
            <button
              key={option.value}
              className={`${styles.btn} ${quality === option.value ? styles.active : ''}`}
              onClick={() => changeQuality(option.value)}
              title={option.full}
            >
              {option.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
