"use client";
import { Navbar } from '@/components/shared';
import { Button } from '@/components/ui';
import { Activity, ServerCrash, AlertTriangle, Terminal, Database, Cpu } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useState, useEffect } from 'react';

const initialData = Array.from({ length: 20 }, (_, i) => ({
  time: i,
  latency: 40 + Math.random() * 20,
  errors: Math.random() > 0.8 ? Math.random() * 5 : 0,
}));

export default function Admin() {
  const [data, setData] = useState(initialData);
  const [status, setStatus] = useState('HEALTHY');
  const [logs, setLogs] = useState<string[]>([
    "[12:00:00] INFO: System initialized successfully.",
    "[12:00:05] INFO: All nodes reporting healthy status."
  ]);

  const addLog = (msg: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`].slice(-8));
  };

  const triggerSpike = () => {
    setStatus('DEGRADED');
    addLog("WARN: Artificial traffic spike initiated.");
    const newData = [...data.slice(1), {
      time: data[data.length - 1].time + 1,
      latency: 300 + Math.random() * 200,
      errors: 10 + Math.random() * 5,
    }];
    setData(newData);
    setTimeout(() => {
      setStatus('HEALTHY');
      addLog("INFO: System recovered from traffic spike.");
    }, 5000);
  };

  const killDB = () => {
    setStatus('OUTAGE');
    addLog("ERROR: Database connection terminated.");
    const newData = [...data.slice(1), {
      time: data[data.length - 1].time + 1,
      latency: 0,
      errors: 100,
    }];
    setData(newData);
    setTimeout(() => {
      setStatus('HEALTHY');
      addLog("INFO: Database connection restored.");
    }, 8000);
  };

  useEffect(() => {
    if (status === 'HEALTHY') {
      const interval = setInterval(() => {
        setData(prev => [...prev.slice(1), {
          time: prev[prev.length - 1].time + 1,
          latency: 40 + Math.random() * 20,
          errors: Math.random() > 0.9 ? Math.random() * 2 : 0,
        }]);
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [status]);

  return (
    <main className="min-h-screen flex flex-col bg-vybe-dark text-vybe-light font-mono">
      <Navbar />
      <div className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-vybe-black border-2 border-vybe-primary p-6 shadow-[8px_8px_0px_0px_#87ceeb]">
          <div>
            <h1 className="text-3xl font-heading font-extrabold text-vybe-primary mb-2">SRE Dashboard</h1>
            <div className="flex items-center gap-3">
              <Activity className={`w-5 h-5 ${status === 'HEALTHY' ? 'text-vybe-accent' : status === 'DEGRADED' ? 'text-vybe-primary' : 'text-[#ef4444]'}`} />
              <span className="font-bold text-lg">SYSTEM_STATUS: {status}</span>
            </div>
          </div>
          <div className="flex gap-4">
            <div className="text-right">
              <div className="text-vybe-light/50 text-sm">ACTIVE NODES</div>
              <div className="text-2xl font-bold">24 / 24</div>
            </div>
            <div className="text-right">
              <div className="text-vybe-light/50 text-sm">UPTIME</div>
              <div className="text-2xl font-bold">99.99%</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Main Metrics */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-vybe-black border-2 border-vybe-darkgray p-6 shadow-[8px_8px_0px_0px_#444444]">
              <h3 className="text-xl font-bold mb-6 flex items-center gap-2"><Activity className="w-5 h-5" /> Latency (ms)</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#444444" />
                    <XAxis dataKey="time" hide />
                    <YAxis stroke="#e5e5e5" />
                    <Tooltip contentStyle={{backgroundColor: '#1a1d23', border: '2px solid #87ceeb'}} />
                    <Line type="monotone" dataKey="latency" stroke="#87ceeb" strokeWidth={3} dot={false} isAnimationActive={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-vybe-black border-2 border-vybe-darkgray p-6 shadow-[8px_8px_0px_0px_#444444]">
              <h3 className="text-xl font-bold mb-6 flex items-center gap-2"><AlertTriangle className="w-5 h-5" /> Error Rate (%)</h3>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#444444" />
                    <XAxis dataKey="time" hide />
                    <YAxis stroke="#e5e5e5" />
                    <Tooltip contentStyle={{backgroundColor: '#1a1d23', border: '2px solid #ef4444'}} />
                    <Line type="step" dataKey="errors" stroke="#ef4444" strokeWidth={3} dot={false} isAnimationActive={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Sidebar Controls & Logs */}
          <div className="space-y-6">
            <div className="bg-vybe-black border-2 border-[#ef4444] p-6 shadow-[8px_8px_0px_0px_#ef4444]">
              <h3 className="text-xl font-bold mb-4 text-[#ef4444] flex items-center gap-2"><Terminal className="w-5 h-5" /> Chaos Controls</h3>
              <p className="text-sm text-vybe-light/70 mb-6">Inject failures to test system resilience and auto-recovery.</p>
              
              <div className="space-y-4">
                <button onClick={triggerSpike} className="w-full bg-vybe-primary/10 border-2 border-vybe-primary text-vybe-primary py-3 font-bold hover:bg-vybe-primary hover:text-vybe-black transition-colors flex items-center justify-center gap-2">
                  <Cpu className="w-5 h-5" /> SPIKE TRAFFIC (10X)
                </button>
                <button onClick={killDB} className="w-full bg-[#ef4444]/10 border-2 border-[#ef4444] text-[#ef4444] py-3 font-bold hover:bg-[#ef4444] hover:text-vybe-light transition-colors flex items-center justify-center gap-2">
                  <Database className="w-5 h-5" /> KILL DATABASE
                </button>
              </div>
            </div>

            <div className="bg-vybe-black border-2 border-vybe-darkgray p-6 shadow-[8px_8px_0px_0px_#444444] h-[400px] flex flex-col">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2"><Terminal className="w-5 h-5" /> Incident Log</h3>
              <div className="flex-1 bg-[#111] border-2 border-vybe-darkgray p-4 overflow-y-auto font-mono text-xs space-y-2">
                {logs.map((log, i) => (
                  <div key={i} className={
                    log.includes('ERROR') ? 'text-[#ef4444]' : 
                    log.includes('WARN') ? 'text-vybe-primary' : 
                    'text-vybe-accent'
                  }>
                    {log}
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>
      </div>
    </main>
  );
}
