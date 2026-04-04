import { useEffect } from 'react';
import { linksApi } from './api';
import { useLinksStore } from './store';
import type { CreateLink } from './types';

export function useLinks() {
  const {
    links,
    isLoading,
    error,
    setLinks,
    addLink,
    updateLink,
    deleteLink,
    setLoading,
    setError,
  } = useLinksStore();

  useEffect(() => {
    fetchLinks();
  }, []);

  const fetchLinks = async () => {
    try {
      setLoading(true);
      const data = await linksApi.getAll();
      setLinks(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch links');
    } finally {
      setLoading(false);
    }
  };

  const createLink = async (payload: CreateLink) => {
    try {
      setLoading(true);
      const newLink = await linksApi.create(payload);
      addLink(newLink);
      setError(null);
      return newLink;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create link');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const removeLink = async (id: string) => {
    try {
      setLoading(true);
      await linksApi.delete(id);
      deleteLink(id);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete link');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    links,
    isLoading,
    error,
    fetchLinks,
    createLink,
    updateLink,
    removeLink,
  };
}
