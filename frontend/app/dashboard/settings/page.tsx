"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function SettingsPage() {
  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Settings</h2>
        <p className="text-neutral-400 mt-1">Manage your account settings and preferences.</p>
      </div>

      <div className="space-y-8">
        <Card className="bg-neutral-950 border-neutral-900">
            <CardHeader>
                <CardTitle>Profile</CardTitle>
                <CardDescription>Update your personal information.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="space-y-2">
                    <Label htmlFor="name">Name</Label>
                    <Input id="name" defaultValue="Developer" className="bg-black border-neutral-800" />
                </div>
                <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input id="email" type="email" defaultValue="info@gmail.com" className="bg-black border-neutral-800" disabled />
                </div>
                <Button>Save Changes</Button>
            </CardContent>
        </Card>

        <Card className="bg-neutral-950 border-neutral-900">
            <CardHeader>
                <CardTitle>Custom Domains</CardTitle>
                <CardDescription>Connect your own domain for branded links.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="rounded-lg border border-neutral-800 bg-black p-4 flex items-center justify-between">
                    <div>
                        <div className="font-medium">vybe.link</div>
                        <div className="text-xs text-green-400 mt-1">Active (Default)</div>
                    </div>
                </div>
                <div className="flex gap-2">
                    <Input placeholder="link.yourdomain.com" className="bg-black border-neutral-800" />
                    <Button variant="outline">Add Domain</Button>
                </div>
            </CardContent>
        </Card>

        <Card className="bg-neutral-950 border-neutral-900">
            <CardHeader>
                <CardTitle>API Keys</CardTitle>
                <CardDescription>Manage API keys for programmatic access.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="rounded-lg border border-neutral-800 bg-black p-4 flex items-center justify-between">
                    <div>
                        <div className="font-mono text-sm text-neutral-400">vybe_live_*******************</div>
                        <div className="text-xs text-neutral-500 mt-1">Created 2 days ago</div>
                    </div>
                    <Button variant="ghost" size="sm" className="text-red-400 hover:text-red-300 hover:bg-red-500/10">Revoke</Button>
                </div>
                <Button variant="outline">Generate New Key</Button>
            </CardContent>
        </Card>
      </div>
    </div>
  );
}
