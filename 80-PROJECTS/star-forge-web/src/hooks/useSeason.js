// src/hooks/useSeason.js
// 监听 GameContext 中的游戏事件，将事件转发给 SeasonContext 更新任务进度
import { useEffect, useRef } from 'react';
import { useGame } from '../store/GameContext';
import { useSeason } from '../store/SeasonContext';
import { SEASON_TASKS } from '../data/seasonConfig';

export function useSeasonBridge() {
  const game = useGame();
  const season = useSeason();
  const prevStateRef = useRef(null);

  useEffect(() => {
    if (!game.state || !season.state) return;
    const gs = game.state;
    const prev = prevStateRef.current || gs;
    prevStateRef.current = gs;

    // === auto 任务追踪 ===

    // ch1_build_5: 建造不同种类建筑数量
    const uniqueBuildings = Object.entries(gs.buildings)
      .filter(([, count]) => count > 0).length;
    const prevUniqueBuildings = Object.entries(prev.buildings)
      .filter(([, count]) => count > 0).length;
    if (uniqueBuildings > prevUniqueBuildings) {
      season.updateTaskProgress('ch1_build_5', uniqueBuildings - prevUniqueBuildings);
    }

    // ch1_produce_10000: 累计总产出
    const totalProd = gs.totalEnergyEarned;
    const prevTotalProd = prev.totalEnergyEarned;
    if (totalProd > prevTotalProd) {
      season.updateTaskProgress('ch1_produce_10000', totalProd - prevTotalProd);
    }

    // ch2_click_500: 累计点击
    if (gs.totalClicks > prev.totalClicks) {
      season.updateTaskProgress('ch2_click_500', gs.totalClicks - prev.totalClicks);
    }

    // ch3_achievement_100: 成就数量
    if (gs.achievements && prev.achievements) {
      if (gs.achievements.length > prev.achievements.length) {
        season.updateTaskProgress('ch3_achievement_100', 1);
      }
    }

    // ch3_prestige: 声望次数
    if (gs.totalPrestiges > prev.totalPrestiges) {
      season.updateTaskProgress('ch3_prestige', 1);
    }

    // ch2_daily_5: 每日挑战（通过 lastDailyClaimDay 变化追踪）
    if (gs.lastDailyClaimDay > prev.lastDailyClaimDay) {
      season.updateTaskProgress('ch2_daily_5', 1);
    }

    // ch1_upgrade_10: 由 BuildingPanel 在升级时手动触发，这里不做自动追踪

    // ch2_use_item_10: 需要道具系统支持，暂时跳过

    // ch3_reach_ch3: 进入第3章（由 checkChapterUnlock 自动更新 chapter）
    if (season.state && season.state.chapter > prev._seasonChapter) {
      season.setTaskProgress('ch3_reach_ch3', 1);
    }

    // === 章节解锁检查 ===
    season.checkChapterUnlock();

  }, [game.state, season]);
}
