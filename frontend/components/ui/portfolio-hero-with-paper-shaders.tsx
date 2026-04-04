"use client"

import { Dithering } from "@paper-design/shaders-react"
import { useState } from "react"
import { Shield, Activity, Zap, Lock } from "lucide-react"

export default function SREDashboardSection() {
  const [isDarkMode] = useState(true)

  return (
    <div className="relative min-h-[800px] overflow-hidden flex flex-col md:flex-row border-y border-white/10 bg-black">
      <div
        className={`w-full md:w-1/2 p-12 md:p-24 flex flex-col justify-center relative z-10 bg-black text-white`}
      >
        {/* Header */}
        <div className="mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-mono mb-6">
            <span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
            SRE INFRASTRUCTURE
          </div>
          <h2 className="text-5xl md:text-7xl font-bold tracking-tighter mb-8 leading-none">
            Built to <span className="text-cyan-400">survive</span> production.
          </h2>
          <p className="text-xl text-neutral-400 max-w-md font-medium leading-relaxed">
            Vybe isn't just functional — it's tested under extreme stress conditions to ensure 99.99% reliability.
          </p>
        </div>

        {/* Experience Section as System Stats */}
        <div className="space-y-6 font-mono text-sm">
          <div className="flex items-center group transition-colors hover:text-cyan-400">
            <Shield className="w-5 h-5 mr-4 text-cyan-500" />
            <span className="w-32 text-neutral-500">Security</span>
            <span className="mx-2">Domain Isolation</span>
            <span className="ml-auto text-neutral-500 text-xs">ACTIVE</span>
          </div>
          <div className="flex items-center group transition-colors hover:text-cyan-400">
            <Activity className="w-5 h-5 mr-4 text-cyan-500" />
            <span className="w-32 text-neutral-500">Load</span>
            <span className="mx-2">500+ Req/sec</span>
            <span className="ml-auto text-neutral-500 text-xs">STABLE</span>
          </div>
          <div className="flex items-center group transition-colors hover:text-cyan-400">
            <Zap className="w-5 h-5 mr-4 text-cyan-500" />
            <span className="w-32 text-neutral-500">Latency</span>
            <span className="mx-2">P99 @ 42ms</span>
            <span className="ml-auto text-neutral-500 text-xs">OPTIMAL</span>
          </div>
          <div className="flex items-center group transition-colors hover:text-cyan-400">
            <Lock className="w-5 h-5 mr-4 text-cyan-500" />
            <span className="w-32 text-neutral-500">Auth</span>
            <span className="mx-2">Zero Trust</span>
            <span className="ml-auto text-neutral-500 text-xs">ENFORCED</span>
          </div>
        </div>

        {/* Footer Links Section */}
        <div className="mt-16 pt-8 border-t border-white/5">
          <div className="flex space-x-8 text-xs font-mono text-neutral-500 uppercase tracking-widest">
            <span className="hover:text-cyan-400 cursor-pointer transition-colors">Documentation</span>
            <span className="hover:text-cyan-400 cursor-pointer transition-colors">Status Page</span>
            <span className="hover:text-cyan-400 cursor-pointer transition-colors">SLA</span>
          </div>
        </div>
      </div>

      <div className="w-full md:w-1/2 relative min-h-[400px] md:min-h-full bg-neutral-900/20">
        <Dithering
          style={{ height: "100%", width: "100%" }}
          colorBack={isDarkMode ? "hsl(0, 0%, 0%)" : "hsl(0, 0%, 95%)"}
          colorFront={isDarkMode ? "hsl(180, 100%, 50%)" : "hsl(220, 100%, 70%)"}
          shape="cat"
          type="4x4"
          pxSize={4}
          offsetX={0}
          offsetY={0}
          scale={0.9}
          rotation={0}
          speed={0.15}
        />
        {/* Abstract stats overlay */}
        <div className="absolute bottom-12 right-12 bg-black/80 backdrop-blur-xl border border-white/10 p-6 rounded-2xl font-mono text-[10px] text-cyan-400/80 space-y-2 max-w-[200px]">
            <div className="flex justify-between"><span>CPU_USAGE</span><span>24.2%</span></div>
            <div className="flex justify-between"><span>MEM_BUFFER</span><span>128MB</span></div>
            <div className="flex justify-between"><span>NET_TRAFFIC</span><span>1.2GB/s</span></div>
            <div className="w-full h-1 bg-white/5 mt-4 rounded-full overflow-hidden">
                <div className="h-full bg-cyan-500 w-2/3 animate-pulse" />
            </div>
        </div>
      </div>
    </div>
  )
}
