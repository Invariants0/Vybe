'use client';
import { Navbar } from '@/components/shared';
import { Button } from '@/components/ui';
import {
  ArrowUpRight,
  Copy,
  Globe,
  Link as LinkIcon,
  MoreVertical,
  MousePointerClick,
} from 'lucide-react';
import { Suspense, lazy } from 'react';

// Lazy load charts
const TrafficChart = lazy(() =>
  import('@/components/analytics/traffic-chart').then((mod) => ({ default: mod.TrafficChart }))
);
const GeoChart = lazy(() =>
  import('@/components/analytics/geo-chart').then((mod) => ({ default: mod.GeoChart }))
);

const trafficData = [
  { name: 'Mon', clicks: 4000 },
  { name: 'Tue', clicks: 3000 },
  { name: 'Wed', clicks: 5000 },
  { name: 'Thu', clicks: 2780 },
  { name: 'Fri', clicks: 8900 },
  { name: 'Sat', clicks: 2390 },
  { name: 'Sun', clicks: 3490 },
];

const geoData = [
  { name: 'US', value: 400 },
  { name: 'UK', value: 300 },
  { name: 'DE', value: 300 },
  { name: 'IN', value: 200 },
];

function ChartSkeleton() {
  return <div className="w-full h-full bg-vybe-gray animate-pulse rounded" />;
}

export default function Dashboard() {
  return (
    <main className="min-h-screen flex flex-col bg-vybe-light">
      <Navbar />
      <div className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <h1 className="text-4xl font-heading font-extrabold">Dashboard</h1>
          <div className="flex w-full md:w-auto gap-2">
            <div className="flex-1 md:w-64 flex items-center px-4 bg-vybe-light border-2 border-vybe-black shadow-[4px_4px_0px_0px_#333333]">
              <LinkIcon className="w-4 h-4 text-vybe-black/50 mr-2" />
              <input
                type="url"
                placeholder="Shorten a new link..."
                className="w-full bg-transparent py-2 outline-none font-medium"
              />
            </div>
            <Button variant="primary">Create</Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { label: 'Total Clicks', value: '124,592', icon: MousePointerClick, trend: '+12.5%' },
            { label: 'Unique Visitors', value: '84,201', icon: Globe, trend: '+5.2%' },
            { label: 'Avg. CTR', value: '24.8%', icon: ArrowUpRight, trend: '+2.1%' },
          ].map((stat) => (
            <div
              key={stat.label}
              className="bg-vybe-light border-2 border-vybe-black p-6 shadow-[8px_8px_0px_0px_#333333]"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="p-2 bg-vybe-primary border-2 border-vybe-black shadow-[2px_2px_0px_0px_#333333]">
                  <stat.icon className="w-5 h-5" />
                </div>
                <span className="font-bold text-sm bg-vybe-accent px-2 py-1 border-2 border-vybe-black">
                  {stat.trend}
                </span>
              </div>
              <div className="text-vybe-black/70 font-bold mb-1">{stat.label}</div>
              <div className="text-4xl font-extrabold">{stat.value}</div>
            </div>
          ))}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-vybe-light border-2 border-vybe-black p-6 shadow-[8px_8px_0px_0px_#333333]">
            <h3 className="text-xl font-heading font-bold mb-6">Traffic Overview</h3>
            <div className="h-72">
              <Suspense fallback={<ChartSkeleton />}>
                <TrafficChart data={trafficData} />
              </Suspense>
            </div>
          </div>
          <div className="bg-vybe-light border-2 border-vybe-black p-6 shadow-[8px_8px_0px_0px_#333333]">
            <h3 className="text-xl font-heading font-bold mb-6">Top Locations</h3>
            <div className="h-72">
              <Suspense fallback={<ChartSkeleton />}>
                <GeoChart data={geoData} />
              </Suspense>
            </div>
          </div>
        </div>

        {/* Links Table */}
        <div className="bg-vybe-light border-2 border-vybe-black shadow-[8px_8px_0px_0px_#333333] overflow-hidden">
          <div className="p-6 border-b-2 border-vybe-black flex justify-between items-center bg-vybe-gray">
            <h3 className="text-xl font-heading font-bold">Recent Links</h3>
            <Button variant="ghost" size="sm">
              View All
            </Button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b-2 border-vybe-black bg-vybe-light">
                  <th className="p-4 font-bold">Short Link</th>
                  <th className="p-4 font-bold">Original URL</th>
                  <th className="p-4 font-bold">Clicks</th>
                  <th className="p-4 font-bold">Status</th>
                  <th className="p-4 font-bold" />
                </tr>
              </thead>
              <tbody>
                {[
                  {
                    short: 'vybe.link/launch',
                    orig: 'https://example.com/campaign-2026',
                    clicks: '45.2k',
                    status: 'Active',
                  },
                  {
                    short: 'vybe.link/docs',
                    orig: 'https://docs.example.com/v2',
                    clicks: '12.8k',
                    status: 'Active',
                  },
                  {
                    short: 'vybe.link/promo',
                    orig: 'https://example.com/special-offer',
                    clicks: '8.4k',
                    status: 'Expired',
                  },
                ].map((link) => (
                  <tr
                    key={link.short}
                    className="border-b-2 border-vybe-black hover:bg-vybe-gray transition-colors"
                  >
                    <td className="p-4 font-bold text-vybe-primary flex items-center gap-2">
                      {link.short}{' '}
                      <Copy className="w-4 h-4 cursor-pointer text-vybe-black hover:text-vybe-primary" />
                    </td>
                    <td className="p-4 text-vybe-black/70 truncate max-w-xs">{link.orig}</td>
                    <td className="p-4 font-bold">{link.clicks}</td>
                    <td className="p-4">
                      <span
                        className={`px-2 py-1 text-xs font-bold border-2 border-vybe-black ${link.status === 'Active' ? 'bg-vybe-accent' : 'bg-vybe-darkgray'}`}
                      >
                        {link.status}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <button
                        type="button"
                        className="p-2 hover:bg-vybe-darkgray border-2 border-transparent hover:border-vybe-black transition-all"
                      >
                        <MoreVertical className="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  );
}
