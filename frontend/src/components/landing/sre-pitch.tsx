import { Button } from '@/components/ui';
import { Activity, AlertTriangle, ArrowRight, ServerCrash } from 'lucide-react';
import Link from 'next/link';

export function SREDashboardPitch() {
  return (
    <section
      id="sre"
      className="py-24 bg-vybe-dark text-vybe-light border-b-2 border-vybe-black px-6 overflow-hidden relative"
    >
      <div className="absolute top-0 right-0 w-1/2 h-full bg-vybe-darkgray/50 -skew-x-12 translate-x-32 border-l-2 border-vybe-black" />

      <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-16 items-center relative z-10">
        <div>
          <div className="inline-flex items-center gap-2 bg-vybe-black px-4 py-2 border-2 border-vybe-accent text-vybe-accent font-bold text-sm mb-8 shadow-[4px_4px_0px_0px_#c8e6c9]">
            🔥 DIFFERENTIATOR
          </div>
          <h2 className="text-5xl md:text-6xl font-heading font-extrabold mb-6 leading-tight">
            Built for production.
            <br />
            Tested under chaos.
          </h2>
          <p className="text-xl text-vybe-light/80 font-medium mb-10 max-w-lg">
            Simulate load, trigger failures, and observe your system in real time. Because hope is
            not a strategy.
          </p>
          <Link href="/admin">
            <Button variant="primary" size="lg">
              Explore SRE Tools <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </Link>
        </div>

        {/* Dashboard Preview */}
        <Link href="/admin" className="block group">
          <div className="bg-vybe-black border-2 border-vybe-accent p-6 shadow-[12px_12px_0px_0px_#c8e6c9] group-hover:shadow-[16px_16px_0px_0px_#c8e6c9] group-hover:-translate-y-2 transition-all duration-300">
            <div className="flex items-center justify-between border-b-2 border-vybe-darkgray pb-4 mb-6">
              <div className="flex items-center gap-3">
                <Activity className="text-vybe-accent w-6 h-6" />
                <span className="font-mono font-bold text-lg">SYSTEM_STATUS: DEGRADED</span>
              </div>
              <div className="flex gap-2">
                <div className="w-3 h-3 bg-vybe-primary rounded-full animate-pulse" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-vybe-darkgray border-2 border-vybe-black p-4">
                <div className="text-vybe-light/50 font-mono text-sm mb-1">LATENCY (P99)</div>
                <div className="text-3xl font-bold text-vybe-primary">842ms</div>
              </div>
              <div className="bg-vybe-darkgray border-2 border-vybe-black p-4">
                <div className="text-vybe-light/50 font-mono text-sm mb-1">ERROR RATE</div>
                <div className="text-3xl font-bold text-[#ff5f57]">4.2%</div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="font-mono text-sm text-vybe-accent mb-2">CHAOS_CONTROLS</div>
              <div className="flex gap-4">
                <button
                  type="button"
                  className="flex-1 bg-[#ff5f57]/10 border-2 border-[#ff5f57] text-[#ff5f57] py-2 font-bold hover:bg-[#ff5f57] hover:text-vybe-light transition-colors flex items-center justify-center gap-2"
                >
                  <ServerCrash className="w-4 h-4" /> KILL API
                </button>
                <button
                  type="button"
                  className="flex-1 bg-vybe-primary/10 border-2 border-vybe-primary text-vybe-primary py-2 font-bold hover:bg-vybe-primary hover:text-vybe-black transition-colors flex items-center justify-center gap-2"
                >
                  <AlertTriangle className="w-4 h-4" /> SPIKE TRAFFIC
                </button>
              </div>
            </div>

            <div className="mt-6 border-t-2 border-vybe-darkgray pt-4">
              <div className="font-mono text-xs text-vybe-light/50 space-y-2">
                <div>[12:01:42] WARN: Traffic spike detected (+400%)</div>
                <div className="text-vybe-primary">
                  [12:01:45] ALERT: Latency threshold exceeded
                </div>
                <div className="text-[#ff5f57]">[12:01:48] ERROR: Redis connection timeout</div>
                <div className="text-vybe-accent">
                  [12:02:10] INFO: Auto-scaling triggered. System recovering...
                </div>
              </div>
            </div>
          </div>
        </Link>
      </div>
    </section>
  );
}
