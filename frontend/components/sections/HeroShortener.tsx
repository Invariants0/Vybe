"use client";

import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { ArrowRight, Link as LinkIcon, Zap } from 'lucide-react';

export function HeroShortener() {
  return (
    <section id="product" className="relative border-b-2 border-vybe-black bg-vybe-primary overflow-hidden" style={{
      backgroundImage: 'radial-gradient(#0a1f0c 2px, transparent 2px)',
      backgroundSize: '32px 32px',
      backgroundColor: 'var(--color-vybe-primary)'
    }}>
      <div className="absolute inset-0 bg-vybe-primary/80"></div>
      <div className="relative max-w-7xl mx-auto px-6 py-24 md:py-32 grid lg:grid-cols-2 gap-12 items-center">
        
        {/* Left Column */}
        <div className="space-y-8">
          <div className="inline-flex items-center gap-2 bg-vybe-light px-4 py-2 rounded-full border-2 border-vybe-black font-bold text-sm shadow-[2px_2px_0px_0px_#0a1f0c]">
            <span className="flex h-2 w-2 rounded-full bg-vybe-dark animate-pulse"></span>
            NEW: AI Content Assistant 2.0
          </div>
          
          <h1 className="text-6xl md:text-8xl font-heading font-extrabold tracking-tighter leading-[1.1]">
            Links that <br/>
            <span className="text-transparent" style={{ WebkitTextStroke: '2px var(--color-vybe-black)' }}>think</span>, adapt,<br/>
            and scale.
          </h1>
          
          <p className="text-xl md:text-2xl font-medium max-w-lg">
            More than a shortener — a production-ready link system.
          </p>

          {/* Shortener Input */}
          <div className="bg-vybe-light p-2 border-2 border-vybe-black shadow-[8px_8px_0px_0px_#0a1f0c] flex flex-col sm:flex-row gap-2 max-w-xl">
            <div className="flex-1 flex items-center px-4 bg-vybe-gray border-2 border-transparent focus-within:border-vybe-black transition-colors">
              <LinkIcon className="w-5 h-5 text-vybe-dark/50 mr-2" />
              <input 
                type="url" 
                placeholder="Paste your long URL here..." 
                className="w-full bg-transparent py-4 outline-none font-medium placeholder:text-vybe-dark/50"
              />
            </div>
            <Button variant="dark" size="lg" className="shrink-0">
              Shorten <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </div>

          {/* Inline Features */}
          <div className="flex flex-wrap gap-3 pt-4">
            {['AI Slugs', 'Smart Routing', 'Analytics', 'Secure Links'].map((feat) => (
              <button key={feat} className="inline-flex items-center gap-1.5 px-3 py-1 bg-vybe-light border-2 border-vybe-black text-sm font-bold shadow-[2px_2px_0px_0px_#0a1f0c] hover:-translate-y-1 hover:shadow-[4px_4px_0px_0px_#0a1f0c] transition-all cursor-pointer">
                <Zap className="w-3 h-3" /> {feat}
              </button>
            ))}
          </div>
        </div>

        {/* Right Column - Browser Mockup */}
        <Link href="/dashboard" className="relative block group cursor-pointer">
          <div className="bg-vybe-light border-2 border-vybe-black rounded-2xl shadow-[12px_12px_0px_0px_#0a1f0c] group-hover:shadow-[16px_16px_0px_0px_#0a1f0c] group-hover:-translate-y-2 transition-all duration-300 overflow-hidden">
            {/* Browser Header */}
            <div className="bg-vybe-black px-4 py-3 flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-[#ff5f57]"></div>
              <div className="w-3 h-3 rounded-full bg-[#febc2e]"></div>
              <div className="w-3 h-3 rounded-full bg-[#28c840]"></div>
              <div className="ml-4 bg-vybe-darkgray text-vybe-light/50 text-xs px-4 py-1 rounded-full font-mono flex-1 text-center truncate">
                vybe.link/dashboard
              </div>
            </div>
            {/* Browser Content */}
            <div className="p-6 bg-vybe-gray grid gap-4">
              <div className="flex justify-between items-end">
                <div>
                  <h3 className="font-heading font-bold text-xl">Total Clicks</h3>
                  <div className="text-4xl font-extrabold mt-1">124,592</div>
                </div>
                <div className="bg-vybe-accent px-3 py-1 border-2 border-vybe-black font-bold text-sm shadow-[2px_2px_0px_0px_#0a1f0c]">
                  +24% this week
                </div>
              </div>
              
              {/* Fake Chart */}
              <div className="h-48 border-2 border-vybe-black bg-vybe-light p-4 flex items-end gap-2 shadow-[4px_4px_0px_0px_#0a1f0c]">
                {[40, 70, 45, 90, 65, 100, 80].map((h, i) => (
                  <div key={i} className="flex-1 bg-vybe-primary border-2 border-vybe-black relative group/bar transition-all hover:bg-vybe-accent" style={{ height: `${h}%` }}>
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-vybe-black text-vybe-light text-xs px-2 py-1 opacity-0 group-hover/bar:opacity-100 transition-opacity whitespace-nowrap z-10">
                      {h * 123} clicks
                    </div>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-2 gap-4 mt-2">
                <div className="bg-vybe-light border-2 border-vybe-black p-4 shadow-[4px_4px_0px_0px_#0a1f0c]">
                  <div className="text-sm font-bold text-vybe-dark/70">Top Location</div>
                  <div className="text-lg font-extrabold">United States</div>
                </div>
                <div className="bg-vybe-light border-2 border-vybe-black p-4 shadow-[4px_4px_0px_0px_#0a1f0c]">
                  <div className="text-sm font-bold text-vybe-dark/70">Active Links</div>
                  <div className="text-lg font-extrabold">1,402</div>
                </div>
              </div>
            </div>
          </div>
        </Link>

      </div>
    </section>
  );
}
