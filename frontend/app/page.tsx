import { HeroShortener } from "@/components/ui/ruixen-moon-chat";
import { CyberneticBentoGrid } from "@/components/ui/cybernetic-bento-grid";
import { Footer } from "@/components/ui/footer-section";
import { MiniNavbar } from "@/components/ui/mini-navbar";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-black text-white selection:bg-cyan-500/30">
      <MiniNavbar />
      
      {/* Hero Section */}
      <HeroShortener />

      {/* Shift Section */}
      <section className="py-24 px-6 border-t border-neutral-900 bg-black relative overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-3xl h-px bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent" />
        <div className="max-w-4xl mx-auto text-center space-y-8 relative z-10">
          <p className="text-2xl sm:text-4xl font-medium leading-relaxed text-neutral-200">
            Modern innovations for URL shorteners are shifting from simple redirection to intelligent link management and self-hosted privacy.
          </p>
          <p className="text-lg text-cyan-400 font-mono">
            Vybe is built around this shift — combining intelligent behavior with production-grade reliability.
          </p>
        </div>
      </section>

      {/* Innovations Section (Bento Grid) */}
      <section id="features" className="bg-neutral-950 border-t border-neutral-900">
        <CyberneticBentoGrid />
      </section>

      {/* Why Vybe Section */}
      <section className="py-32 px-6 bg-black border-t border-neutral-900 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(0,255,255,0.05),transparent_50%)]" />
        <div className="max-w-4xl mx-auto relative z-10">
          <h2 className="text-4xl sm:text-5xl font-bold text-white mb-8 text-center">
            Not just smarter links — production-ready systems.
          </h2>
          <div className="bg-neutral-900/50 border border-neutral-800 rounded-2xl p-8 sm:p-12 backdrop-blur-sm">
            <p className="text-xl text-neutral-300 mb-8 leading-relaxed">
              Vybe isn't just a URL shortener. It's built with the same principles used in real-world production systems: observability, scalability, and resilience.
            </p>
            <ul className="space-y-4 text-neutral-400">
              <li className="flex items-center gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                Real-time analytics and system visibility
              </li>
              <li className="flex items-center gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                Load-tested architecture (100–500 users)
              </li>
              <li className="flex items-center gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                Failure simulation and recovery
              </li>
              <li className="flex items-center gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                Structured logging and alerting
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* Interactive Demo Section (Placeholder for now) */}
      <section className="py-24 px-6 bg-neutral-950 border-t border-neutral-900 text-center">
         <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">See your links in action.</h2>
            <p className="text-neutral-400 mb-12">From creation to analytics — every interaction is tracked, measured, and optimized.</p>
            <div className="aspect-video bg-black rounded-2xl border border-neutral-800 flex items-center justify-center relative overflow-hidden group">
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#4f4f4f2e_1px,transparent_1px),linear-gradient(to_bottom,#4f4f4f2e_1px,transparent_1px)] bg-[size:14px_24px]"></div>
                <div className="relative z-10 text-neutral-500 font-mono text-sm flex flex-col items-center">
                    <svg className="w-12 h-12 mb-4 opacity-50 group-hover:opacity-100 transition-opacity" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Interactive Demo Simulation
                </div>
            </div>
         </div>
      </section>

      {/* Feature Snapshot Strip */}
      <section className="py-12 border-y border-neutral-900 bg-black overflow-hidden">
        <div className="flex gap-8 items-center justify-center flex-wrap px-6 text-sm font-mono text-neutral-500">
            <span>Smart Slugs</span>
            <span className="w-1 h-1 rounded-full bg-neutral-800" />
            <span>QR Codes</span>
            <span className="w-1 h-1 rounded-full bg-neutral-800" />
            <span>Link Expiry</span>
            <span className="w-1 h-1 rounded-full bg-neutral-800" />
            <span>Password Protection</span>
            <span className="w-1 h-1 rounded-full bg-neutral-800" />
            <span>Analytics Dashboard</span>
            <span className="w-1 h-1 rounded-full bg-neutral-800" />
            <span>Device Routing</span>
        </div>
      </section>

      {/* Production Engineering Section */}
      <section className="py-32 px-6 bg-neutral-950 border-b border-neutral-900 relative overflow-hidden">
         <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1/2 h-full bg-[radial-gradient(ellipse_at_right,rgba(255,0,0,0.05),transparent_70%)]" />
         <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-16 items-center relative z-10">
            <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-mono mb-6">
                    <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                    SRE Dashboard
                </div>
                <h2 className="text-4xl sm:text-5xl font-bold text-white mb-6">Built to survive production.</h2>
                <p className="text-lg text-neutral-400 mb-8">
                    Vybe isn't just functional — it's tested under real-world stress conditions.
                </p>
                <ul className="space-y-4 text-neutral-300">
                    <li className="flex items-center gap-3">
                        <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                        Simulate 500+ concurrent users
                    </li>
                    <li className="flex items-center gap-3">
                        <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                        Monitor latency, traffic, and errors
                    </li>
                    <li className="flex items-center gap-3">
                        <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                        Trigger failures and observe recovery
                    </li>
                    <li className="flex items-center gap-3">
                        <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                        Built-in observability dashboard
                    </li>
                </ul>
                <div className="mt-10">
                    <Link href="/admin">
                        <Button variant="outline" className="border-red-500/30 text-red-400 hover:bg-red-500/10 hover:text-red-300">
                            View Engineering Dashboard
                        </Button>
                    </Link>
                </div>
            </div>
            <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-tr from-red-500/10 to-transparent rounded-2xl blur-2xl" />
                <div className="bg-black border border-neutral-800 rounded-2xl p-6 relative z-10 shadow-2xl">
                    <div className="flex items-center justify-between mb-6 pb-4 border-b border-neutral-800">
                        <div className="text-sm font-mono text-neutral-400">System Status</div>
                        <div className="text-xs text-green-400 bg-green-400/10 px-2 py-1 rounded">Healthy</div>
                    </div>
                    <div className="space-y-4">
                        <div>
                            <div className="flex justify-between text-xs mb-1">
                                <span className="text-neutral-500">Traffic (req/s)</span>
                                <span className="text-white">428</span>
                            </div>
                            <div className="h-2 bg-neutral-900 rounded-full overflow-hidden">
                                <div className="h-full bg-cyan-400 w-[60%]" />
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-xs mb-1">
                                <span className="text-neutral-500">Latency (p99)</span>
                                <span className="text-white">42ms</span>
                            </div>
                            <div className="h-2 bg-neutral-900 rounded-full overflow-hidden">
                                <div className="h-full bg-green-400 w-[30%]" />
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-xs mb-1">
                                <span className="text-neutral-500">Error Rate</span>
                                <span className="text-white">0.01%</span>
                            </div>
                            <div className="h-2 bg-neutral-900 rounded-full overflow-hidden">
                                <div className="h-full bg-red-400 w-[2%]" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
         </div>
      </section>

      {/* Final CTA */}
      <section className="py-32 px-6 bg-black text-center relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.05),transparent_50%)]" />
        <div className="max-w-3xl mx-auto relative z-10">
            <h2 className="text-4xl sm:text-6xl font-bold text-white mb-6 tracking-tight">
                Start building smarter links today.
            </h2>
            <p className="text-xl text-neutral-400 mb-10">
                Create, control, and scale your links with intelligence and reliability.
            </p>
            <div className="flex items-center justify-center gap-4">
                <Link href="/auth">
                    <Button size="lg" className="rounded-full px-8 text-base">Get Started</Button>
                </Link>
                <Link href="/dashboard">
                    <Button size="lg" variant="outline" className="rounded-full px-8 text-base">View Dashboard</Button>
                </Link>
            </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}
