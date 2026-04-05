import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { Link } from './types';

interface LinksStore {
  links: Link[];
  isLoading: boolean;
  error: string | null;
  setLinks: (links: Link[]) => void;
  addLink: (link: Link) => void;
  updateLink: (id: number, updates: Partial<Link>) => void;
  deleteLink: (id: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useLinksStore = create<LinksStore>()(
  devtools((set) => ({
    links: [],
    isLoading: false,
    error: null,
    setLinks: (links) => set({ links }),
    addLink: (link) => set((state) => ({ links: [link, ...state.links] })),
    updateLink: (id, updates) =>
      set((state) => ({
        links: state.links.map((link) => (link.id === id ? { ...link, ...updates } : link)),
      })),
    deleteLink: (id) =>
      set((state) => ({
        links: state.links.filter((link) => link.id !== id),
      })),
    setLoading: (isLoading) => set({ isLoading }),
    setError: (error) => set({ error }),
  }))
);
