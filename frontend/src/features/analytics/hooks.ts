import { useEffect } from 'react';
import { useAnalyticsStore } from './store';
import { analyticsApi } from './api';

export function useAnalytics(linkId?: string) {
  const { analytics, setAnalytics, setLoading, setError } = useAnalyticsStore();

  useEffect(() => {
    fetchAnalytics();
  }, [linkId]);

  const fetchAnalytics = async () => {
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
  };

  return {
    analytics,
    fetchAnalytics,
  };
}
