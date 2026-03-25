import { useEffect, useRef, useCallback } from 'react';
import { useGame } from '../store/GameContext';

const TICK_RATE = 100; // ms
const SAVE_INTERVAL = 30000; // 30 seconds

export function useGameLoop() {
  const { tick, checkAchievements, state } = useGame();
  const lastTickRef = useRef(Date.now());
  const lastSaveRef = useRef(Date.now());
  const achievementCheckRef = useRef(0);

  const gameLoop = useCallback(() => {
    const now = Date.now();
    const deltaTime = (now - lastTickRef.current) / 1000; // Convert to seconds
    lastTickRef.current = now;

    tick(deltaTime);

    // Check achievements every 60 ticks (6 seconds)
    achievementCheckRef.current += 1;
    if (achievementCheckRef.current >= 60) {
      checkAchievements();
      achievementCheckRef.current = 0;
    }

    // Auto-save
    if (now - lastSaveRef.current >= SAVE_INTERVAL) {
      const saveData = {
        ...state,
        lastSaveTime: now,
      };
      localStorage.setItem('starforge_save', JSON.stringify(saveData));
      lastSaveRef.current = now;
    }
  }, [tick, checkAchievements, state]);

  useEffect(() => {
    const intervalId = setInterval(gameLoop, TICK_RATE);
    return () => clearInterval(intervalId);
  }, [gameLoop]);
}
