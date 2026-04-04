import { HeroShortener } from "@/components/ui/ruixen-moon-chat";
import { CyberneticBentoGrid } from "@/components/ui/cybernetic-bento-grid";
import { Footer } from "@/components/ui/footer-section";
import { MiniNavbar } from "@/components/ui/mini-navbar";
import SREDashboardSection from "@/components/ui/portfolio-hero-with-paper-shaders";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-background text-foreground selection:bg-primary/30">
      <MiniNavbar />
      
      {/* Hero Section */}
      <HeroShortener />

      {/* Modern Innovation Strip */}
      <section className="py-24 px-6 bg-white/40 backdrop-blur-sm relative overflow-hidden border-y border-border/20">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-5xl h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent" />
        <div className="max-w-5xl mx-auto text-center space-y-8 relative z-10">
          <p className="text-3xl sm:text-5xl font-bold tracking-tighter leading-tight text-foreground">
            URL shorteners are <span className="text-secondary">evolving</span>. 
            From simple redirects to intelligent infrastructure.
          </p>
          <p className="text-lg text-muted-foreground font-bold uppercase tracking-[0.2em]">
            Vybe is the protocol for the next generation of links.
          </p>
        </div>
      </section>

      {/* Features Section (Bento Grid) */}
      <section id="features" className="bg-background py-20">
        <div className="max-w-7xl mx-auto px-6 mb-16">
            <h2 className="text-4xl sm:text-6xl font-bold tracking-tighter text-foreground">
                Engineered for <span className="text-secondary">Scale</span>.
            </h2>
        </div>
        <CyberneticBentoGrid />
      </section>

      {/* New SRE Dashboard Section */}
      <SREDashboardSection />

      {/* Final CTA */}
      <section className="py-40 px-6 bg-white/40 backdrop-blur-xl text-center relative overflow-hidden border-t border-border/20">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,192,203,0.1),transparent_70%)]" />
        <div className="max-w-4xl mx-auto relative z-10">
            <h2 className="text-5xl sm:text-8xl font-bold text-foreground mb-10 tracking-tighter">
                Ready to <span className="text-primary">Vybe</span>?
            </h2>
            <p className="text-xl sm:text-2xl text-muted-foreground mb-12 max-w-2xl mx-auto leading-relaxed">
                Join the infrastructure-first link management platform. Built for developers, trusted by production.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
                <button className="w-full sm:w-auto bg-primary text-primary-foreground font-bold px-12 py-5 rounded-2xl text-xl transition-all hover:bg-primary/90 hover:scale-105 active:scale-95 shadow-xl">
                    Get Started Now
                </button>
                <button className="w-full sm:w-auto bg-white/60 border border-border/40 text-foreground font-bold px-12 py-5 rounded-2xl text-xl transition-all hover:bg-white/80 hover:border-border/60">
                    View Docs
                </button>
            </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}
