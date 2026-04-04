import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowUpRight, Link as LinkIcon, MousePointerClick, TrendingUp } from "lucide-react";
import Link from "next/link";

export default function DashboardOverview() {
  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
            <h2 className="text-3xl font-bold tracking-tight">Overview</h2>
            <p className="text-neutral-400 mt-1">Welcome back. Here's what's happening with your links.</p>
        </div>
        <Link href="/dashboard/links">
            <Button className="rounded-full">Create Link</Button>
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="bg-neutral-950 border-neutral-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">Total Clicks</CardTitle>
            <MousePointerClick className="h-4 w-4 text-neutral-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">12,482</div>
            <p className="text-xs text-green-400 mt-1 flex items-center">
              <TrendingUp className="w-3 h-3 mr-1" /> +14% from last month
            </p>
          </CardContent>
        </Card>
        <Card className="bg-neutral-950 border-neutral-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">Active Links</CardTitle>
            <LinkIcon className="h-4 w-4 text-neutral-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">42</div>
            <p className="text-xs text-neutral-500 mt-1">
              3 created this week
            </p>
          </CardContent>
        </Card>
        <Card className="bg-neutral-950 border-neutral-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">Avg. CTR</CardTitle>
            <BarChart3 className="h-4 w-4 text-neutral-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">4.2%</div>
            <p className="text-xs text-green-400 mt-1 flex items-center">
              <TrendingUp className="w-3 h-3 mr-1" /> +0.8% from last month
            </p>
          </CardContent>
        </Card>
      </div>

      <div>
        <h3 className="text-xl font-semibold mb-4">Recent Links</h3>
        <div className="rounded-xl border border-neutral-900 bg-neutral-950 overflow-hidden">
            <table className="w-full text-sm text-left">
                <thead className="text-xs text-neutral-500 bg-neutral-900/50 border-b border-neutral-900">
                    <tr>
                        <th className="px-6 py-3 font-medium">Short Link</th>
                        <th className="px-6 py-3 font-medium">Original URL</th>
                        <th className="px-6 py-3 font-medium">Clicks</th>
                        <th className="px-6 py-3 font-medium">Created</th>
                        <th className="px-6 py-3 font-medium text-right">Actions</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-neutral-900">
                    {[
                        { short: 'vybe.link/launch', orig: 'https://example.com/product/launch-2026', clicks: 4231, date: '2d ago' },
                        { short: 'vybe.link/docs', orig: 'https://docs.example.com/v2/getting-started', clicks: 892, date: '5d ago' },
                        { short: 'vybe.link/twitter-promo', orig: 'https://example.com/promo?ref=twitter', clicks: 124, date: '1w ago' },
                    ].map((link, i) => (
                        <tr key={i} className="hover:bg-neutral-900/30 transition-colors">
                            <td className="px-6 py-4 font-mono text-cyan-400">{link.short}</td>
                            <td className="px-6 py-4 text-neutral-400 truncate max-w-[200px]">{link.orig}</td>
                            <td className="px-6 py-4">{link.clicks.toLocaleString()}</td>
                            <td className="px-6 py-4 text-neutral-500">{link.date}</td>
                            <td className="px-6 py-4 text-right">
                                <Button variant="ghost" size="sm" className="h-8 text-neutral-400 hover:text-white">
                                    Details <ArrowUpRight className="w-3 h-3 ml-1" />
                                </Button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
      </div>
    </div>
  );
}

function BarChart3(props: any) {
    return <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/></svg>
}
