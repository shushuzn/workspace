import { useState, useEffect } from 'react';
import styles from './Loading.module.css';

export default function Loading() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(timer);
          return 100;
        }
        return prev + Math.random() * 15;
      });
    }, 200);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className={styles.loading}>
      <div className={styles.content}>
        <div className={styles.icon}>⚡</div>
        <h1 className={styles.title}>Star Forge</h1>
        <p className={styles.subtitle}>星之熔炉</p>
        
        <div className={styles.progressContainer}>
          <div className={styles.progressBar}>
            <div 
              className={styles.progressFill} 
              style={{ width: `${Math.min(progress, 100)}%` }}
            />
          </div>
          <span className={styles.progressText}>
            {Math.min(Math.floor(progress), 100)}%
          </span>
        </div>
        
        <div className={styles.tips}>
          <p>💡 提示：快速点击太阳可以累积连击，获得更高加成！</p>
        </div>
      </div>
    </div>
  );
}
