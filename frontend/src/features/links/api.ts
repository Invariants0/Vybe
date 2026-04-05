import { apiClient } from '@/lib/api-client';
import { createLinkSchema, linkSchema } from './schema';
import type { CreateLink, Link } from './types';

export const linksApi = {
  async getAll(): Promise<Link[]> {
    const { data } = await apiClient.get('/links');
    return data.map((link: unknown) => linkSchema.parse(link));
  },

  async getById(id: number): Promise<Link> {
    const { data } = await apiClient.get(`/links/${id}`);
    return linkSchema.parse(data);
  },

  async create(payload: CreateLink): Promise<Link> {
    const validated = createLinkSchema.parse(payload);
    const { data } = await apiClient.post('/links', validated);
    return linkSchema.parse(data);
  },

  async update(id: number, updates: Partial<Link>): Promise<Link> {
    const { data } = await apiClient.patch(`/links/${id}`, updates);
    return linkSchema.parse(data);
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/links/${id}`);
  },
};
