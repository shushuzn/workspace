// src/store/SeasonContext.jsx
import { createContext, useContext, useReducer, useCallback, useMemo, useEffect, useRef } from 'react';
import {
  SEASON_TASKS,
  SEASON_REWARDS,
  getSeasonTimeRange,
  getCurrentSeasonId,
  calcChapterProgress,
  SEASON_CONFIG,
} from '../data/seasonConfig';

const SeasonContext = createContext(null);

const STORAGE_KEY = 'starforge_season';
const ACCOUNT_KEY = 'starforge_account';

// 初始状态（空赛季）
function createInitialSeasonState(seasonId) {
  const { startTime, endTime } = getSeasonTimeRange(seasonId);
  return {
    seasonId,
    chapter: 1, // 当前章节
    tasks: SEASON_TASKS.map(t => ({ ...t, progress: 0, claimed: false })),
    rewards: SEASON_REWARDS.map(r => ({ ...r, claimed: false })),
    startTime,
    endTime,
    lastSaved: Date.now(),
  };
}

// 防抖持久化 hook
function useDebouncedPersistence(stateRef, key) {
  const dirtyRef = useRef(false);
  const timerRef = useRef(null);

  const flush = useCallback(() => {
    if (!dirtyRef.current) return;
    try {
      localStorage.setItem(key, JSON.stringify(stateRef.current));
      dirtyRef.current = false;
    } catch (e) {
      console.error('Season save failed:', e);
    }
  }, [stateRef, key]);

  const markDirty = useCallback(() => {
    dirtyRef.current = true;
  }, []);

  // 5秒防抖定时器
  useEffect(() => {
    timerRef.current = setInterval(flush, 5000);
    return () => clearInterval(timerRef.current);
  }, [flush]);

  // 页面卸载时 flush
  useEffect(() => {
    const handleBeforeUnload = () => flush();
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [flush]);

  return { markDirty, flush };
}

function seasonReducer(state, action) {
  switch (action.type) {
    case 'LOAD': {
      return action.state;
    }

    case 'TASK_PROGRESS': {
      // 更新某个任务的进度（累加，不减少）
      const { taskId, delta } = action;
      const tasks = state.tasks.map(t =>
        t.id === taskId
          ? { ...t, progress: Math.min(t.target, t.progress + delta) }
          : t
      );
      return { ...state, tasks };
    }

    case 'TASK_SET': {
      // 直接设置任务进度（用于初始化或特殊覆盖）
      const { taskId, value } = action;
      const tasks = state.tasks.map(t =>
        t.id === taskId ? { ...t, progress: Math.min(t.target, value) } : t
      );
      return { ...state, tasks };
    }

    case 'CLAIM_REWARD': {
      const { rewardId } = action;
      const rewards = state.rewards.map(r =>
        r.id === rewardId ? { ...r, claimed: true } : r
      );
      return { ...state, rewards };
    }

    case 'CHECK_CHAPTER_UNLOCK': {
      // 检查是否解锁下一章节
      const nextChapter = state.chapter + 1;
      if (nextChapter > 3) return state;

      const threshold = SEASON_CONFIG.chapterUnlockThresholds[nextChapter];
      const prevProgress = calcChapterProgress(state.tasks, state.chapter);
      if (prevProgress >= threshold) {
        return { ...state, chapter: nextChapter };
      }
      return state;
    }

    case 'RESET_NEW_SEASON': {
      const { seasonId } = action;
      return createInitialSeasonState(seasonId);
    }

    default:
      return state;
  }
}

export function SeasonProvider({ children }) {
  const [state, dispatch] = useReducer(seasonReducer, null);

  // 防抖 refs
  const stateRef = useRef(state);
  stateRef.current = state;
  const { markDirty, flush } = useDebouncedPersistence(stateRef, STORAGE_KEY);

  // === 赛季初始化 ===
  useEffect(() => {
    const currentId = getCurrentSeasonId();
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.seasonId === currentId) {
          dispatch({ type: 'LOAD', state: parsed });
          return;
        }
        // 赛季不匹配，开启新赛季（旧数据丢弃）
      }
    } catch (e) {
      console.warn('Failed to load season:', e);
    }
    // 初始化新赛季
    dispatch({ type: 'RESET_NEW_SEASON', seasonId: currentId });
  }, []);

  // === 赛季结束后自动重置 ===
  useEffect(() => {
    if (!state) return;
    if (Date.now() > state.endTime) {
      const newId = getCurrentSeasonId();
      dispatch({ type: 'RESET_NEW_SEASON', seasonId: newId });
    }
  }, [state]);

  // === 任务进度更新（所有任务共享此入口） ===
  const updateTaskProgress = useCallback((taskId, delta) => {
    dispatch({ type: 'TASK_PROGRESS', taskId, delta });
    markDirty();
  }, [markDirty]);

  const setTaskProgress = useCallback((taskId, value) => {
    dispatch({ type: 'TASK_SET', taskId, value });
    markDirty();
  }, [markDirty]);

  const claimReward = useCallback((rewardId) => {
    dispatch({ type: 'CLAIM_REWARD', rewardId });
    markDirty();
    flush(); // 领奖立即持久化
  }, [markDirty, flush]);

  const checkChapterUnlock = useCallback(() => {
    dispatch({ type: 'CHECK_CHAPTER_UNLOCK' });
    markDirty();
  }, [markDirty]);

  // === 章节进度 ===
  const getChapterProgress = useCallback((chapter) => {
    if (!state) return 0;
    return calcChapterProgress(state.tasks, chapter);
  }, [state]);

  // === 赛季剩余天数 ===
  const daysLeft = useMemo(() => {
    if (!state) return 0;
    const msLeft = state.endTime - Date.now();
    return Math.max(0, Math.ceil(msLeft / (1000 * 60 * 60 * 24)));
  }, [state]);

  // === premiumOwned 账号级权益 ===
  const getPremiumOwned = useCallback(() => {
    try {
      const account = JSON.parse(localStorage.getItem(ACCOUNT_KEY) || '{}');
      return account.premiumOwned || false;
    } catch { return false; }
  }, []);

  const setPremiumOwned = useCallback((owned) => {
    try {
      const account = JSON.parse(localStorage.getItem(ACCOUNT_KEY) || '{}');
      account.premiumOwned = owned;
      localStorage.setItem(ACCOUNT_KEY, JSON.stringify(account));
    } catch (e) {
      console.error('Failed to save premiumOwned:', e);
    }
  }, []);

  const value = useMemo(() => ({
    state,
    updateTaskProgress,
    setTaskProgress,
    claimReward,
    checkChapterUnlock,
    getChapterProgress,
    daysLeft,
    getPremiumOwned,
    setPremiumOwned,
    flush,
  }), [state, updateTaskProgress, setTaskProgress, claimReward, checkChapterUnlock, getChapterProgress, daysLeft, getPremiumOwned, setPremiumOwned, flush]);

  return (
    <SeasonContext.Provider value={value}>
      {children}
    </SeasonContext.Provider>
  );
}

export function useSeason() {
  const context = useContext(SeasonContext);
  if (!context) throw new Error('useSeason must be used within SeasonProvider');
  return context;
}
