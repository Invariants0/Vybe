import { Check, X } from 'lucide-react';

export function ComparisonSection() {
  return (
    <section className="py-24 bg-vybe-light border-b-2 border-vybe-black px-6">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-5xl font-heading font-extrabold mb-16 text-center">
          Why switch to VYBE?
        </h2>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Problem Card */}
          <div className="bg-[#f4f4f5] border-2 border-dashed border-gray-400 p-8 md:p-12 rounded-3xl opacity-80">
            <h3 className="text-2xl font-heading font-bold mb-8 text-gray-500">
              Current Shorteners
            </h3>
            <ul className="space-y-6">
              {[
                'Random, unreadable slugs',
                'Basic click counting only',
                'Single destination routing',
                'Shared, vulnerable domains',
                'No production-grade SLAs',
              ].map((item) => (
                <li key={item} className="flex items-start gap-4 text-gray-600 font-medium text-lg">
                  <div className="mt-1 bg-gray-200 p-1 rounded-full">
                    <X className="w-4 h-4" />
                  </div>
                  {item}
                </li>
              ))}
            </ul>
          </div>

          {/* Solution Card */}
          <div className="bg-vybe-primary border-2 border-vybe-black p-8 md:p-12 rounded-3xl shadow-[8px_8px_0px_0px_#0a1f0c]">
            <h3 className="text-3xl font-heading font-extrabold mb-8 text-vybe-black">
              VYBE System
            </h3>
            <ul className="space-y-6">
              {[
                'AI-generated, contextual slugs',
                'Deep analytics & event tracking',
                'Granular conditional routing',
                'Isolated domains & password protection',
                'SRE dashboard & chaos testing',
              ].map((item) => (
                <li key={item} className="flex items-start gap-4 font-bold text-lg text-vybe-black">
                  <div className="mt-1 bg-vybe-black text-vybe-light p-1 rounded-full">
                    <Check className="w-4 h-4" />
                  </div>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
