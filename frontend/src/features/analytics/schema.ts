import { z } from 'zod';

export const analyticsSchema = z.object({
  totalClicks: z.number(),
  uniqueVisitors: z.number(),
  avgCTR: z.number(),
  topLocations: z.array(
    z.object({
      country: z.string(),
      clicks: z.number(),
    })
  ),
  trafficData: z.array(
    z.object({
      date: z.string(),
      clicks: z.number(),
    })
  ),
});
