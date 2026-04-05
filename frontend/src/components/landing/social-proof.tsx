export function SocialProofMarquee() {
  const brands = [
    'FAST ROUTING',
    'SECURE LINKS',
    'AI-POWERED',
    'DEEP ANALYTICS',
    'CHAOS TESTED',
    'CUSTOM DOMAINS',
    'PRODUCTION READY',
  ];

  return (
    <div className="bg-vybe-dark border-b-2 border-vybe-black py-6 overflow-hidden flex whitespace-nowrap">
      <div className="animate-marquee flex gap-16 items-center px-8">
        {[0, 1, 2].flatMap((group) =>
          brands.map((brand) => (
            <span
              key={`${group}-${brand}`}
              className="text-vybe-accent/80 font-heading font-extrabold text-2xl tracking-widest"
            >
              {brand}
            </span>
          ))
        )}
      </div>
    </div>
  );
}
