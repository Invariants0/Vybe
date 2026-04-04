"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

const data = [
  { name: 'Mon', clicks: 4000, unique: 2400 },
  { name: 'Tue', clicks: 3000, unique: 1398 },
  { name: 'Wed', clicks: 2000, unique: 9800 },
  { name: 'Thu', clicks: 2780, unique: 3908 },
  { name: 'Fri', clicks: 1890, unique: 4800 },
  { name: 'Sat', clicks: 2390, unique: 3800 },
  { name: 'Sun', clicks: 3490, unique: 4300 },
];

export default function AnalyticsPage() {
  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Analytics</h2>
        <p className="text-neutral-400 mt-1">Deep dive into your link performance and audience.</p>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="mb-8">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="locations">Locations</TabsTrigger>
          <TabsTrigger value="devices">Devices</TabsTrigger>
          <TabsTrigger value="referrers">Referrers</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="space-y-8">
            <Card className="bg-neutral-950 border-neutral-900">
                <CardHeader>
                    <CardTitle>Traffic Overview</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="h-[400px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="colorClicks" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
                                <XAxis dataKey="name" stroke="#525252" tick={{fill: '#a3a3a3'}} axisLine={false} tickLine={false} />
                                <YAxis stroke="#525252" tick={{fill: '#a3a3a3'}} axisLine={false} tickLine={false} />
                                <Tooltip 
                                    contentStyle={{ backgroundColor: '#0a0a0a', borderColor: '#262626', borderRadius: '8px' }}
                                    itemStyle={{ color: '#e5e5e5' }}
                                />
                                <Area type="monotone" dataKey="clicks" stroke="#06b6d4" strokeWidth={2} fillOpacity={1} fill="url(#colorClicks)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </CardContent>
            </Card>

            <div className="grid md:grid-cols-2 gap-8">
                <Card className="bg-neutral-950 border-neutral-900">
                    <CardHeader>
                        <CardTitle>Top Links</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {[
                                { link: 'vybe.link/launch', clicks: 4231, percent: 65 },
                                { link: 'vybe.link/docs', clicks: 892, percent: 20 },
                                { link: 'vybe.link/twitter-promo', clicks: 124, percent: 5 },
                            ].map((item, i) => (
                                <div key={i}>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="font-mono text-cyan-400">{item.link}</span>
                                        <span className="text-neutral-400">{item.clicks.toLocaleString()}</span>
                                    </div>
                                    <div className="h-2 bg-neutral-900 rounded-full overflow-hidden">
                                        <div className="h-full bg-white" style={{ width: `${item.percent}%` }} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                <Card className="bg-neutral-950 border-neutral-900">
                    <CardHeader>
                        <CardTitle>Top Referrers</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {[
                                { name: 'Twitter', clicks: 2100, percent: 45 },
                                { name: 'Direct', clicks: 1500, percent: 35 },
                                { name: 'Google', clicks: 800, percent: 15 },
                            ].map((item, i) => (
                                <div key={i}>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-white">{item.name}</span>
                                        <span className="text-neutral-400">{item.clicks.toLocaleString()}</span>
                                    </div>
                                    <div className="h-2 bg-neutral-900 rounded-full overflow-hidden">
                                        <div className="h-full bg-neutral-500" style={{ width: `${item.percent}%` }} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </TabsContent>
        <TabsContent value="locations">
            <Card className="bg-neutral-950 border-neutral-900">
                <CardContent className="p-12 text-center text-neutral-500">
                    Geo Map Visualization Placeholder
                </CardContent>
            </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
