import { lazy, Suspense } from 'react';

// Lazy load heavy components
export const LazyStatsModal = lazy(() => import('../components/StatsPanel'));
export const LazyLeaderboard = lazy(() => import('../components/Leaderboard'));
export const LazyAchievements = lazy(() => import('../components/Achievements'));

// Loading fallback
export function LoadingFallback() {
  return <div style={{ padding: '20px', textAlign: 'center', color: '#888' }}>Loading...</div>;
}

// Lazy wrapper component
export function LazyWrapper({ component: Component, fallback = <LoadingFallback /> }) {
  return (
    <Suspense fallback={fallback}>
      <Component />
    </Suspense>
  );
}
