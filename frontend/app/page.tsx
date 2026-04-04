import { HeroShortener } from "@/components/ui/ruixen-moon-chat";
import { CyberneticBentoGrid } from "@/components/ui/cybernetic-bento-grid";
import { Footer } from "@/components/ui/footer-section";
import { MiniNavbar } from "@/components/ui/mini-navbar";
import SREDashboardSection from "@/components/ui/portfolio-hero-with-paper-shaders";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-black text-white selection:bg-cyan-500/30">
      <MiniNavbar />
      
      {/* Hero Section with new Shader */}
      <HeroShortener />

      {/* Modern Innovation Strip */}
      <section className="py-24 px-6 bg-black relative overflow-hidden border-y border-white/5">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-5xl h-px bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent" />
        <div className="max-w-5xl mx-auto text-center space-y-8 relative z-10">
          <p className="text-3xl sm:text-5xl font-bold tracking-tighter leading-tight text-white">
            URL shorteners are <span className="text-cyan-400">evolving</span>. 
            From simple redirects to intelligent infrastructure.
          </p>
          <p className="text-lg text-neutral-400 font-mono uppercase tracking-[0.2em]">
            Vybe is the protocol for the next generation of links.
          </p>
        </div>
      </section>

      {/* Features Section (Bento Grid) */}
      <section id="features" className="bg-black py-20">
        <div className="max-w-7xl mx-auto px-6 mb-16">
            <h2 className="text-4xl sm:text-6xl font-bold tracking-tighter text-white">
                Engineered for <span className="text-cyan-400">Scale</span>.
            </h2>
        </div>
        <CyberneticBentoGrid />
      </section>

      {/* New SRE Dashboard Section with Paper Shaders */}
      <SREDashboardSection />

      {/* Final CTA */}
      <section className="py-40 px-6 bg-black text-center relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,255,255,0.08),transparent_70%)]" />
        <div className="max-w-4xl mx-auto relative z-10">
            <h2 className="text-5xl sm:text-8xl font-bold text-white mb-10 tracking-tighter">
                Ready to <span className="text-cyan-400">Vybe</span>?
            </h2>
            <p className="text-xl sm:text-2xl text-neutral-400 mb-12 max-w-2xl mx-auto leading-relaxed">
                Join the infrastructure-first link management platform. Built for developers, trusted by production.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
                <button className="w-full sm:w-auto bg-cyan-500 text-black font-bold px-12 py-5 rounded-2xl text-xl transition-all hover:bg-cyan-400 hover:scale-105 active:scale-95 shadow-[0_0_30px_-5px_rgba(0,255,255,0.5)]">
                    Get Started Now
                </button>
                <button className="w-full sm:w-auto bg-white/5 border border-white/10 text-white font-bold px-12 py-5 rounded-2xl text-xl transition-all hover:bg-white/10 hover:border-white/20">
                    View Docs
                </button>
            </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}
