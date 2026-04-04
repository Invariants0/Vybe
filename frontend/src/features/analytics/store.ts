import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { Analytics } from './types';

interface AnalyticsStore {
  analytics: Analytics | null;
  isLoading: boolean;
  error: string | null;
  setAnalytics: (analytics: Analytics) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAnalyticsStore = create<AnalyticsStore>()(
  devtools((set) => ({
    analytics: null,
    isLoading: false,
    error: null,
    setAnalytics: (analytics) => set({ analytics }),
    setLoading: (isLoading) => set({ isLoading }),
    setError: (error) => set({ error }),
  }))
);
