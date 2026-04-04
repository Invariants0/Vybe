import { Button } from '@/components/ui';

export function FinalCTA() {
  return (
    <section className="py-32 bg-vybe-primary border-b-2 border-vybe-black px-6 text-center" style={{
      backgroundImage: 'radial-gradient(#0a1f0c 2px, transparent 2px)',
      backgroundSize: '32px 32px',
    }}>
      <div className="max-w-4xl mx-auto bg-vybe-light border-2 border-vybe-black p-12 md:p-20 shadow-[16px_16px_0px_0px_#0a1f0c]">
        <h2 className="text-5xl md:text-7xl font-heading font-extrabold mb-8 tracking-tighter text-vybe-black">
          Ready to scale?
        </h2>
        <p className="text-xl md:text-2xl font-medium mb-12 max-w-2xl mx-auto text-vybe-dark/80">
          Join thousands of developers building production-ready link systems with VYBE.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-6">
          <Button variant="dark" size="lg" className="text-xl px-12 py-6">
            Try Demo
          </Button>
          <a href="https://github.com/Invariants0/Vybe" target="_blank" rel="noopener noreferrer">
            <Button variant="secondary" size="lg" className="text-xl px-12 py-6 w-full">
              View Documentation
            </Button>
          </a>
        </div>
      </div>
    </section>
  );
}
