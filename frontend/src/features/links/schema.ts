import { z } from 'zod';

export const linkSchema = z.object({
  id: z.number(),
  user_id: z.number(),
  short_code: z.string(),
  original_url: z.string().url(),
  title: z.string().nullable(),
  is_active: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const createLinkSchema = z.object({
  original_url: z.string().url('Please enter a valid URL'),
  user_id: z.number(),
  title: z.string().optional(),
});
