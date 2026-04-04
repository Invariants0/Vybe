import { BarChart3, Brain, DollarSign, Route, ShieldCheck } from 'lucide-react';

export function InnovationsGrid() {
  const innovations = [
    {
      title: 'AI-Powered Slug Generation',
      text: 'Generate readable, context-aware links instead of random strings. Better branding, better recall.',
      icon: <Brain className="w-8 h-8" />,
    },
    {
      title: 'Granular Conditional Redirects',
      text: 'Route users dynamically based on device, location, or timing.',
      icon: <Route className="w-8 h-8" />,
    },
    {
      title: 'Decoupled Analytics & SSO',
      text: 'Instant redirects with async analytics and secure access control.',
      icon: <BarChart3 className="w-8 h-8" />,
    },
    {
      title: 'Domain Isolation & Security',
      text: 'Isolated domains, password protection, expiry control, and QR codes.',
      icon: <ShieldCheck className="w-8 h-8" />,
    },
    {
      title: 'Monetization & Affiliate',
      text: 'Track performance and revenue directly from your links.',
      icon: <DollarSign className="w-8 h-8" />,
    },
  ];

  return (
    <section id="features" className="py-24 bg-vybe-primary border-b-2 border-vybe-black px-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-16">
          <h2 className="text-5xl font-heading font-extrabold">Features that scale.</h2>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {innovations.map((inv) => (
            <div
              key={inv.title}
              className="bg-vybe-light border-2 border-vybe-black p-8 shadow-[8px_8px_0px_0px_#0a1f0c] group hover:-translate-y-2 hover:shadow-[12px_12px_0px_0px_#0a1f0c] transition-all duration-300"
            >
              <div className="w-16 h-16 bg-vybe-accent border-2 border-vybe-black flex items-center justify-center mb-6 group-hover:bg-vybe-primary transition-colors shadow-[4px_4px_0px_0px_#0a1f0c]">
                {inv.icon}
              </div>
              <h3 className="text-2xl font-heading font-extrabold mb-4">{inv.title}</h3>
              <p className="font-medium text-vybe-dark/80 text-lg leading-relaxed">{inv.text}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
