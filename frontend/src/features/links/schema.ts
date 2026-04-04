import { z } from 'zod';

export const linkSchema = z.object({
  id: z.string().optional(),
  shortCode: z.string().min(3).max(50),
  originalUrl: z.string().url(),
  title: z.string().optional(),
  clicks: z.number().default(0),
  status: z.enum(['active', 'expired', 'disabled']).default('active'),
  createdAt: z.date().optional(),
  expiresAt: z.date().optional().nullable(),
});

export const createLinkSchema = z.object({
  originalUrl: z.string().url('Please enter a valid URL'),
  customSlug: z.string().min(3).max(50).optional(),
  expiresAt: z.date().optional(),
});
