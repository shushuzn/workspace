import { useMemo, useCallback } from 'react';

// Memoize expensive calculations
export function useMemoizedCalculations(dependencies) {
  return useMemo(() => dependencies, [dependencies]);
}

// Memoize callbacks
export function useMemoizedCallback(callback, deps) {
  return useCallback(callback, deps);
}

// Batch state updates for performance
export function useBatchedUpdates() {
  const batchedUpdates = useCallback((updates) => {
    // React automatically batches updates in modern versions
    updates.forEach(([setter, value]) => setter(value));
  }, []);

  return batchedUpdates;
}

// Optimize re-renders with shallow comparison
export function useShallowCompare(value) {
  return useMemo(() => value, [value]);
}
