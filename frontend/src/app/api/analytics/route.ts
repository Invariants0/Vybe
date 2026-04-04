import { NextResponse } from 'next/server';

export async function GET() {
  // Mock analytics data
  const mockAnalytics = {
    totalClicks: 124592,
    uniqueVisitors: 84201,
    avgCTR: 24.8,
    topLocations: [
      { country: 'US', clicks: 45000 },
      { country: 'UK', clicks: 23000 },
      { country: 'DE', clicks: 18000 },
    ],
    trafficData: [
      { date: '2026-03-01', clicks: 4000 },
      { date: '2026-03-02', clicks: 3000 },
      { date: '2026-03-03', clicks: 5000 },
    ],
  };

  return NextResponse.json(mockAnalytics);
}
