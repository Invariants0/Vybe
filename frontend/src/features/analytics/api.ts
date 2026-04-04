import { apiClient } from '@/lib/api-client';
import type { Analytics } from './types';

export const analyticsApi = {
  async getAnalytics(linkId?: string): Promise<Analytics> {
    const endpoint = linkId ? `/analytics/${linkId}` : '/analytics';
    const { data } = await apiClient.get(endpoint);
    return data;
  },
};
