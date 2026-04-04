import { Navbar } from '@/components/layout/Navbar';
import { HeroShortener } from '@/components/sections/HeroShortener';
import { SocialProofMarquee } from '@/components/sections/SocialProofMarquee';
import { ComparisonSection } from '@/components/sections/ComparisonSection';
import { InnovationsGrid } from '@/components/sections/InnovationsGrid';
import { HowItWorks } from '@/components/sections/HowItWorks';
import { SREDashboardPitch } from '@/components/sections/SREDashboardPitch';
import { FinalCTA } from '@/components/sections/FinalCTA';
import { Footer } from '@/components/sections/Footer';

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col">
      <Navbar />
      <HeroShortener />
      <SocialProofMarquee />
      <InnovationsGrid />
      <ComparisonSection />
      <HowItWorks />
      <SREDashboardPitch />
      <FinalCTA />
      <Footer />
    </main>
  );
}
