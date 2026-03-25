import { useState, useEffect } from 'react';
import { useGame } from '../store/GameContext';
import styles from './LuckySpin.module.css';

const PRIZES = [
  { id: 1, name: '100 Energy', type: 'energy', value: 100, weight: 30 },
  { id: 2, name: '500 Energy', type: 'energy', value: 500, weight: 25 },
  { id: 3, name: '1K Energy', type: 'energy', value: 1000, weight: 20 },
  { id: 4, name: '+1 Click Power', type: 'click', value: 1, weight: 10 },
  { id: 5, name: '+5% Efficiency', type: 'efficiency', value: 0.05, weight: 8 },
  { id: 6, name: '5K Energy', type: 'energy', value: 5000, weight: 5 },
  { id: 7, name: 'x2 Multiplier', type: 'multiplier', value: 2, weight: 2 },
];

export default function LuckySpin() {
  const { state } = useGame();
  const [spins, setSpins] = useState(() => parseInt(localStorage.getItem('starforge_spins') || '3'));
  const [spinning, setSpinning] = useState(false);
  const [result, setResult] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    localStorage.setItem('starforge_spins', spins.toString());
  }, [spins]);

  const getRandomPrize = () => {
    const totalWeight = PRIZES.reduce((sum, p) => sum + p.weight, 0);
    let random = Math.random() * totalWeight;
    for (const prize of PRIZES) {
      random -= prize.weight;
      if (random <= 0) return prize;
    }
    return PRIZES[0];
  };

  const spin = () => {
    if (spins <= 0 || spinning) return;
    setSpins(s => s - 1);
    setSpinning(true);
    const prize = getRandomPrize();
    setTimeout(() => {
      setResult(prize);
      setSpinning(false);
    }, 2000);
  };

  if (!showModal) return (
    <button className={styles.trigger} onClick={() => setShowModal(true)}>
      🎰 免费抽奖 ({spins})
    </button>
  );

  return (
    <div className={styles.modal}>
      <div className={styles.backdrop} onClick={() => setShowModal(false)} />
      <div className={styles.content}>
        <button className={styles.close} onClick={() => setShowModal(false)}>×</button>
        <h2 className={styles.title}>🎰 Lucky Spin</h2>
        <p className={styles.spins}>剩余次数: {spins}</p>

        <div className={`${styles.wheel} ${spinning ? styles.spinning : ''}`}>
          <div className={styles.pointer}>▼</div>
          {PRIZES.map((p, i) => (
            <div key={p.id} className={styles.segment} style={{ '--i': i, '--total': PRIZES.length }}>
              {p.name}
            </div>
          ))}
        </div>

        <button className={styles.spinBtn} onClick={spin} disabled={spins <= 0 || spinning}>
          {spins <= 0 ? '次数用完' : spinning ? '抽奖中...' : '开始抽奖'}
        </button>

        {result && (
          <div className={styles.result}>
            恭喜获得: <strong>{result.name}</strong>
          </div>
        )}
      </div>
    </div>
  );
}
