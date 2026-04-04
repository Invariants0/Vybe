export interface Analytics {
  totalClicks: number;
  uniqueVisitors: number;
  avgCTR: number;
  topLocations: Array<{
    country: string;
    clicks: number;
  }>;
  trafficData: Array<{
    date: string;
    clicks: number;
  }>;
}
