"use client"

import { Shield, Activity, Zap, Lock, ArrowUpRight } from "lucide-react"
import Link from "next/link"
import { Button } from "./button"

export default function SREDashboardSection() {
  return (
    <div className="relative min-h-[600px] overflow-hidden flex flex-col md:flex-row border-y border-border/20 bg-background">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,192,203,0.05),transparent_70%)]" />
      
      <div
        className={`w-full md:w-1/2 p-12 md:p-24 flex flex-col justify-center relative z-10 bg-white/40 backdrop-blur-md text-foreground`}
      >
        {/* Header */}
        <div className="mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary/10 border border-secondary/20 text-secondary-foreground text-xs font-bold mb-6">
            <span className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
            SRE INFRASTRUCTURE
          </div>
          <h2 className="text-5xl md:text-7xl font-bold tracking-tighter mb-8 leading-none">
            Built to <span className="text-secondary">survive</span> production.
          </h2>
          <p className="text-xl text-muted-foreground max-w-md font-medium leading-relaxed">
            Vybe isn't just functional — it's tested under extreme stress conditions to ensure 99.99% reliability.
          </p>
        </div>

        {/* Experience Section as System Stats */}
        <div className="space-y-6 font-bold text-sm">
          <StatItem icon={<Shield className="w-5 h-5 mr-4 text-secondary" />} label="Security" value="Domain Isolation" status="ACTIVE" />
          <StatItem icon={<Activity className="w-5 h-5 mr-4 text-secondary" />} label="Load" value="500+ Req/sec" status="STABLE" />
          <StatItem icon={<Zap className="w-5 h-5 mr-4 text-secondary" />} label="Latency" value="P99 @ 42ms" status="OPTIMAL" />
          <StatItem icon={<Lock className="w-5 h-5 mr-4 text-secondary" />} label="Auth" value="Zero Trust" status="ENFORCED" />
        </div>

        <div className="mt-12">
            <Link href="/admin">
                <Button variant="outline" size="lg" className="rounded-2xl border-border/40 bg-white/60 hover:bg-white/80 text-foreground font-bold flex items-center gap-2">
                    Enter Dashboard
                    <ArrowUpRight className="w-4 h-4" />
                </Button>
            </Link>
        </div>
      </div>

      <div className="w-full md:w-1/2 relative min-h-[400px] md:min-h-full flex items-center justify-center p-12">
        {/* Abstract Visualization using glassmorphic cards */}
        <div className="relative w-full max-w-md aspect-square">
            <div className="absolute top-0 left-0 w-64 h-64 bg-primary/20 rounded-3xl backdrop-blur-3xl animate-pulse" />
            <div className="absolute bottom-0 right-0 w-64 h-64 bg-secondary/20 rounded-3xl backdrop-blur-3xl animate-pulse [animation-delay:1s]" />
            
            <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-full bg-white/60 backdrop-blur-xl border border-border/40 p-8 rounded-3xl shadow-2xl space-y-6">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-widest text-muted-foreground">System Health</span>
                        <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-1 rounded-full">HEALTHY</span>
                    </div>
                    
                    <div className="space-y-4">
                        <HealthBar label="CPU" percentage={24} />
                        <HealthBar label="Memory" percentage={62} />
                        <HealthBar label="Network" percentage={45} />
                    </div>
                    
                    <div className="pt-4 border-t border-border/20">
                        <div className="flex justify-between items-center text-[10px] font-bold text-muted-foreground">
                            <span>UPTIME</span>
                            <span>99.999%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
  )
}

function StatItem({ icon, label, value, status }: { icon: React.ReactNode, label: string, value: string, status: string }) {
    return (
        <div className="flex items-center group transition-colors hover:text-secondary">
            {icon}
            <span className="w-32 text-muted-foreground">{label}</span>
            <span className="mx-2 text-foreground">{value}</span>
            <span className="ml-auto text-muted-foreground text-[10px] tracking-widest">{status}</span>
        </div>
    )
}

function HealthBar({ label, percentage }: { label: string, percentage: number }) {
    return (
        <div className="space-y-2">
            <div className="flex justify-between text-[10px] font-bold">
                <span>{label}</span>
                <span>{percentage}%</span>
            </div>
            <div className="w-full h-1.5 bg-muted/40 rounded-full overflow-hidden">
                <div className="h-full bg-primary transition-all duration-1000" style={{ width: `${percentage}%` }} />
            </div>
        </div>
    )
}
