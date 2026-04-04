"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Link as LinkIcon, Sparkles, Copy, QrCode, MoreVertical, Edit2, Trash2, Power } from "lucide-react";

export default function LinksPage() {
  const [url, setUrl] = useState("");

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Links</h2>
        <p className="text-neutral-400 mt-1">Manage, edit, and create new shortened links.</p>
      </div>

      {/* Create Link Bar */}
      <Card className="bg-neutral-950 border-neutral-900">
        <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <LinkIcon className="h-5 w-5 text-neutral-500" />
                    </div>
                    <Input 
                        type="url" 
                        placeholder="Paste long URL here..." 
                        className="pl-10 bg-black border-neutral-800 h-12 text-base"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                    />
                </div>
                <Button className="h-12 px-8 rounded-full flex items-center gap-2 shrink-0">
                    <Sparkles className="w-4 h-4" />
                    Generate Link
                </Button>
            </div>
            <div className="mt-4 flex items-center gap-2 text-sm text-neutral-500">
                <span>Suggested slug:</span>
                <span className="font-mono text-cyan-400 bg-cyan-400/10 px-2 py-0.5 rounded">summer-sale-26</span>
                <button className="hover:text-white transition-colors ml-2 text-xs underline decoration-neutral-700 underline-offset-4">Customize</button>
            </div>
        </CardContent>
      </Card>

      {/* Links Table */}
      <div className="rounded-xl border border-neutral-900 bg-neutral-950 overflow-hidden">
        <div className="p-4 border-b border-neutral-900 flex items-center justify-between bg-black/50">
            <Input placeholder="Search links..." className="max-w-xs bg-black border-neutral-800 h-9" />
            <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" className="h-9 border-neutral-800">Filter</Button>
            </div>
        </div>
        <table className="w-full text-sm text-left">
            <thead className="text-xs text-neutral-500 bg-neutral-900/50 border-b border-neutral-900">
                <tr>
                    <th className="px-6 py-3 font-medium">Link Details</th>
                    <th className="px-6 py-3 font-medium">Performance</th>
                    <th className="px-6 py-3 font-medium">Status</th>
                    <th className="px-6 py-3 font-medium text-right">Actions</th>
                </tr>
            </thead>
            <tbody className="divide-y divide-neutral-900">
                {[
                    { short: 'vybe.link/launch', orig: 'https://example.com/product/launch-2026', clicks: 4231, status: 'Active' },
                    { short: 'vybe.link/docs', orig: 'https://docs.example.com/v2/getting-started', clicks: 892, status: 'Active' },
                    { short: 'vybe.link/twitter-promo', orig: 'https://example.com/promo?ref=twitter', clicks: 124, status: 'Paused' },
                ].map((link, i) => (
                    <tr key={i} className="hover:bg-neutral-900/30 transition-colors group">
                        <td className="px-6 py-4">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-neutral-800 flex items-center justify-center shrink-0">
                                    <img src={`https://www.google.com/s2/favicons?domain=${link.orig}&sz=32`} className="w-4 h-4 opacity-70" alt="" />
                                </div>
                                <div>
                                    <div className="font-mono text-cyan-400 font-medium">{link.short}</div>
                                    <div className="text-neutral-500 text-xs truncate max-w-[300px] mt-0.5">{link.orig}</div>
                                </div>
                            </div>
                        </td>
                        <td className="px-6 py-4">
                            <div className="font-medium">{link.clicks.toLocaleString()} clicks</div>
                            <div className="text-neutral-500 text-xs mt-0.5">Last 30 days</div>
                        </td>
                        <td className="px-6 py-4">
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${link.status === 'Active' ? 'bg-green-500/10 text-green-400' : 'bg-neutral-800 text-neutral-400'}`}>
                                {link.status}
                            </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                            <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                <Button variant="ghost" size="icon" className="h-8 w-8 text-neutral-400 hover:text-white">
                                    <Copy className="w-4 h-4" />
                                </Button>
                                <Button variant="ghost" size="icon" className="h-8 w-8 text-neutral-400 hover:text-white">
                                    <QrCode className="w-4 h-4" />
                                </Button>
                                <Button variant="ghost" size="icon" className="h-8 w-8 text-neutral-400 hover:text-white">
                                    <Edit2 className="w-4 h-4" />
                                </Button>
                                <Button variant="ghost" size="icon" className="h-8 w-8 text-neutral-400 hover:text-red-400">
                                    <Trash2 className="w-4 h-4" />
                                </Button>
                            </div>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
      </div>
    </div>
  );
}
