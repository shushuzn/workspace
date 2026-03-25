import { useState, useCallback } from 'react';
import styles from './ClickParticles.module.css';

export default function ClickParticles({ containerRef }) {
  const [particles, setParticles] = useState([]);

  const createParticles = useCallback((x, y) => {
    const newParticles = [];
    for (let i = 0; i < 8; i++) {
      const angle = (Math.PI * 2 * i) / 8;
      newParticles.push({
        id: Date.now() + i,
        x,
        y,
        vx: Math.cos(angle) * (2 + Math.random() * 3),
        vy: Math.sin(angle) * (2 + Math.random() * 3),
      });
    }
    setParticles(prev => [...prev, ...newParticles]);
    setTimeout(() => {
      setParticles(prev => prev.filter(p => !newParticles.find(np => np.id === p.id)));
    }, 600);
  }, []);

  return (
    <div className={styles.container}>
      {particles.map(p => (
        <div
          key={p.id}
          className={styles.particle}
          style={{
            left: p.x,
            top: p.y,
            '--vx': `${p.vx}px`,
            '--vy': `${p.vy}px`,
          }}
        />
      ))}
    </div>
  );
}
