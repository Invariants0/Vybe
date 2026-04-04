import { useCallback, useEffect } from 'react';
import { analyticsApi } from './api';
import { useAnalyticsStore } from './store';

export function useAnalytics(linkId?: string) {
  const { analytics, setAnalytics, setLoading, setError } = useAnalyticsStore();

  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      const data = await analyticsApi.getAnalytics(linkId);
      setAnalytics(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics');
    } finally {
      setLoading(false);
    }
  }, [linkId, setAnalytics, setError, setLoading]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  return {
    analytics,
    fetchAnalytics,
  };
}
