import { HeroShortener } from '@/components/landing/hero-shortener';
import { Footer } from '@/components/shared/footer';
import { Navbar } from '@/components/shared/navbar';
import { Suspense, lazy } from 'react';

// Lazy load below-the-fold sections
const SocialProofMarquee = lazy(() =>
  import('@/components/landing/social-proof').then((m) => ({ default: m.SocialProofMarquee }))
);
const ComparisonSection = lazy(() =>
  import('@/components/landing/comparison').then((m) => ({ default: m.ComparisonSection }))
);
const InnovationsGrid = lazy(() =>
  import('@/components/landing/innovations').then((m) => ({ default: m.InnovationsGrid }))
);
const HowItWorks = lazy(() =>
  import('@/components/landing/how-it-works').then((m) => ({ default: m.HowItWorks }))
);
const SREDashboardPitch = lazy(() =>
  import('@/components/landing/sre-pitch').then((m) => ({ default: m.SREDashboardPitch }))
);
const FinalCTA = lazy(() =>
  import('@/components/landing/final-cta').then((m) => ({ default: m.FinalCTA }))
);

function SectionSkeleton() {
  return <div className="w-full h-96 bg-vybe-gray animate-pulse" />;
}

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col">
      <Navbar />
      <HeroShortener />
      <Suspense fallback={<SectionSkeleton />}>
        <SocialProofMarquee />
      </Suspense>
      <Suspense fallback={<SectionSkeleton />}>
        <InnovationsGrid />
      </Suspense>
      <Suspense fallback={<SectionSkeleton />}>
        <ComparisonSection />
      </Suspense>
      <Suspense fallback={<SectionSkeleton />}>
        <HowItWorks />
      </Suspense>
      <Suspense fallback={<SectionSkeleton />}>
        <SREDashboardPitch />
      </Suspense>
      <Suspense fallback={<SectionSkeleton />}>
        <FinalCTA />
      </Suspense>
      <Footer />
    </main>
  );
}
