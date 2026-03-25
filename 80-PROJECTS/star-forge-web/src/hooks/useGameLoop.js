import { useEffect, useRef, useCallback } from 'react';
import { useGame } from '../store/GameContext';

// 优化的tick率：50ms = 20次/秒，足够平滑且不会太频繁
const TICK_RATE = 50; // ms

export function useGameLoop() {
  const { tick, checkAchievements } = useGame();
  const lastTickRef = useRef(Date.now());
  const achievementCheckRef = useRef(0);
  const frameRef = useRef(null);

  const gameLoop = useCallback(() => {
    const now = Date.now();
    const deltaTime = (now - lastTickRef.current) / 1000;
    lastTickRef.current = now;

    // 执行游戏tick
    tick(deltaTime);

    // 优化：每60个tick检查一次成就（约每3秒），减少不必要的检查
    achievementCheckRef.current += 1;
    if (achievementCheckRef.current >= 60) {
      checkAchievements();
      achievementCheckRef.current = 0;
    }

    // 使用setTimeout而非setInterval以获得更稳定的帧率
    frameRef.current = setTimeout(gameLoop, TICK_RATE);
  }, [tick, checkAchievements]);

  useEffect(() => {
    // 启动游戏循环
    frameRef.current = setTimeout(gameLoop, TICK_RATE);

    return () => {
      // 清理
      if (frameRef.current) {
        clearTimeout(frameRef.current);
      }
    };
  }, [gameLoop]);
}
