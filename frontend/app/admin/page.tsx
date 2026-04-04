"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Activity, AlertTriangle, Database, ServerCrash, Terminal, Zap } from "lucide-react";
import Link from "next/link";

export default function AdminDashboard() {
  const [users, setUsers] = useState([100]);
  const [isTesting, setIsTesting] = useState(false);
  const [logs, setLogs] = useState<{time: string, msg: string, level: 'info'|'warn'|'error'}[]>([]);
  const [metrics, setMetrics] = useState({
      latency: 42,
      traffic: 120,
      errors: 0.01,
      status: 'Healthy'
  });

  const addLog = (msg: string, level: 'info'|'warn'|'error' = 'info') => {
      const time = new Date().toLocaleTimeString([], { hour12: false });
      setLogs(prev => [{time, msg, level}, ...prev].slice(0, 50));
  };

  const handleStartTest = () => {
      setIsTesting(true);
      addLog(`Started load test with ${users[0]} concurrent users`, 'info');
      
      // Simulate metrics changing
      setMetrics(prev => ({
          ...prev,
          traffic: users[0] * 4.2,
          latency: prev.latency + (users[0] / 10),
      }));
  };

  const handleStopTest = () => {
      setIsTesting(false);
      addLog(`Stopped load test`, 'info');
      setMetrics({
        latency: 42,
        traffic: 120,
        errors: 0.01,
        status: 'Healthy'
    });
  };

  const triggerChaos = (type: string) => {
      addLog(`Chaos event triggered: ${type}`, 'error');
      setMetrics(prev => ({
          ...prev,
          status: 'Degraded',
          errors: prev.errors + 5.2,
          latency: prev.latency + 400
      }));

      setTimeout(() => {
          addLog(`System recovered from: ${type}`, 'info');
          setMetrics(prev => ({
            ...prev,
            status: 'Healthy',
            errors: 0.01,
            latency: 42
        }));
      }, 5000);
  };

  useEffect(() => {
      addLog('Admin dashboard initialized', 'info');
  }, []);

  return (
    <div className="min-h-screen bg-black text-white p-8 font-mono">
      <div className="max-w-7xl mx-auto space-y-8">
        
        <div className="flex items-center justify-between border-b border-neutral-900 pb-6">
            <div>
                <h1 className="text-2xl font-bold flex items-center gap-3">
                    <Terminal className="w-6 h-6 text-red-500" />
                    Production Engineering Dashboard
                </h1>
                <p className="text-neutral-500 mt-2 text-sm">SRE Controls & Live Observability</p>
            </div>
            <div className="flex items-center gap-4">
                <Link href="/dashboard">
                    <Button variant="outline" className="border-neutral-800">Exit Admin</Button>
                </Link>
                <div className={`px-3 py-1.5 rounded-full text-xs font-bold border ${metrics.status === 'Healthy' ? 'bg-green-500/10 border-green-500/20 text-green-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
                    STATUS: {metrics.status.toUpperCase()}
                </div>
            </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
            {/* Left Column: Controls */}
            <div className="space-y-8">
                <Card className="bg-neutral-950 border-neutral-900 rounded-none border-l-2 border-l-cyan-500">
                    <CardHeader>
                        <CardTitle className="text-sm flex items-center gap-2 text-cyan-400">
                            <Zap className="w-4 h-4" /> Load Simulator
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="space-y-4">
                            <div className="flex justify-between text-sm">
                                <span className="text-neutral-400">Concurrent Users</span>
                                <span className="text-white font-bold">{users[0]}</span>
                            </div>
                            <Slider 
                                value={users} 
                                onValueChange={setUsers} 
                                max={1000} 
                                step={50}
                                disabled={isTesting}
                            />
                        </div>
                        {isTesting ? (
                            <Button onClick={handleStopTest} variant="destructive" className="w-full rounded-none font-bold">
                                STOP SIMULATION
                            </Button>
                        ) : (
                            <Button onClick={handleStartTest} className="w-full rounded-none bg-cyan-500 hover:bg-cyan-600 text-black font-bold">
                                START SIMULATION
                            </Button>
                        )}
                    </CardContent>
                </Card>

                <Card className="bg-neutral-950 border-neutral-900 rounded-none border-l-2 border-l-red-500">
                    <CardHeader>
                        <CardTitle className="text-sm flex items-center gap-2 text-red-400">
                            <AlertTriangle className="w-4 h-4" /> Chaos Controls
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        <Button onClick={() => triggerChaos('Kill Container')} variant="outline" className="w-full justify-start border-red-500/30 text-red-400 hover:bg-red-500/10 rounded-none">
                            <ServerCrash className="w-4 h-4 mr-2" /> Kill Container
                        </Button>
                        <Button onClick={() => triggerChaos('Slow DB')} variant="outline" className="w-full justify-start border-orange-500/30 text-orange-400 hover:bg-orange-500/10 rounded-none">
                            <Database className="w-4 h-4 mr-2" /> Simulate Slow DB
                        </Button>
                        <Button onClick={() => triggerChaos('Network Partition')} variant="outline" className="w-full justify-start border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/10 rounded-none">
                            <Activity className="w-4 h-4 mr-2" /> Network Partition
                        </Button>
                    </CardContent>
                </Card>
            </div>

            {/* Middle Column: Metrics */}
            <div className="lg:col-span-2 space-y-8">
                <div className="grid grid-cols-3 gap-4">
                    <div className="bg-neutral-950 border border-neutral-900 p-4">
                        <div className="text-xs text-neutral-500 mb-2">LATENCY (p99)</div>
                        <div className={`text-3xl font-bold ${metrics.latency > 200 ? 'text-red-400' : 'text-white'}`}>
                            {metrics.latency.toFixed(0)}<span className="text-sm text-neutral-500 ml-1">ms</span>
                        </div>
                    </div>
                    <div className="bg-neutral-950 border border-neutral-900 p-4">
                        <div className="text-xs text-neutral-500 mb-2">TRAFFIC</div>
                        <div className="text-3xl font-bold text-white">
                            {metrics.traffic.toFixed(0)}<span className="text-sm text-neutral-500 ml-1">req/s</span>
                        </div>
                    </div>
                    <div className="bg-neutral-950 border border-neutral-900 p-4">
                        <div className="text-xs text-neutral-500 mb-2">ERROR RATE</div>
                        <div className={`text-3xl font-bold ${metrics.errors > 1 ? 'text-red-400' : 'text-white'}`}>
                            {metrics.errors.toFixed(2)}<span className="text-sm text-neutral-500 ml-1">%</span>
                        </div>
                    </div>
                </div>

                <Card className="bg-neutral-950 border-neutral-900 rounded-none">
                    <CardHeader className="border-b border-neutral-900 pb-4">
                        <CardTitle className="text-sm text-neutral-400">Live Structured Logs</CardTitle>
                    </CardHeader>
                    <CardContent className="p-0">
                        <div className="h-[400px] overflow-y-auto p-4 space-y-2 text-xs">
                            {logs.map((log, i) => (
                                <div key={i} className="flex gap-4 border-b border-neutral-900/50 pb-2">
                                    <span className="text-neutral-600 shrink-0">[{log.time}]</span>
                                    <span className={`shrink-0 w-12 ${log.level === 'error' ? 'text-red-400' : log.level === 'warn' ? 'text-yellow-400' : 'text-cyan-400'}`}>
                                        {log.level.toUpperCase()}
                                    </span>
                                    <span className={log.level === 'error' ? 'text-red-200' : 'text-neutral-300'}>
                                        {log.msg}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>

      </div>
    </div>
  );
}
