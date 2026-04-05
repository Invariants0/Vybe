'use client';

import { Button } from '@/components/ui';
import Link from 'next/link';
import { useState } from 'react';
import { linksApi } from '@/features/links/api';

export function HeroShortener() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleShorten = async () => {
    if (!url.trim()) return;
    let finalUrl = url.trim();
    if (!/^https?:\/\//i.test(finalUrl)) {
      finalUrl = `https://${finalUrl}`;
    }
    try {
      setLoading(true);
      setError(null);
      const link = await linksApi.create({ original_url: finalUrl, user_id: 1 });
      setResult(`${window.location.origin}/${link.short_code}`);
      setUrl('');
    } catch {
      setError('Failed to shorten URL');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section
      id="product"
      className="relative border-b-2 border-vybe-black bg-vybe-primary overflow-hidden"
      style={{
        backgroundImage: 'radial-gradient(#0a1f0c 2px, transparent 2px)',
        backgroundSize: '32px 32px',
        backgroundColor: 'var(--color-vybe-primary)',
      }}
    >
      <div className="absolute inset-0 bg-vybe-primary/80" />
      <div className="relative max-w-7xl mx-auto px-6 py-24 md:py-32 grid lg:grid-cols-2 gap-12 items-center">
        {/* Left Column */}
        <div className="space-y-8">
          <div className="inline-flex items-center gap-2 bg-vybe-light px-4 py-2 rounded-full border-2 border-vybe-black font-bold text-sm shadow-[2px_2px_0px_0px_#0a1f0c]">
            <span className="flex h-2 w-2 rounded-full bg-vybe-dark animate-pulse" />
            NEW: AI Content Assistant 2.0
          </div>

          <h1 className="text-5xl md:text-7xl font-heading font-extrabold tracking-tighter leading-[1.1] min-h-[200px] md:min-h-[280px]">
            Links that <br />
            <span
              className="text-transparent"
              style={{ WebkitTextStroke: '2px var(--color-vybe-black)' }}
            >
              think
            </span>
            , adapt,
            <br />
            and scale.
          </h1>

          <p className="text-xl md:text-2xl font-medium max-w-lg">
            More than a shortener — a production-ready link system.
          </p>

          {/* Shortener Input */}
          <form
            className="bg-vybe-light p-2 border-2 border-vybe-black shadow-[8px_8px_0px_0px_#0a1f0c] flex flex-col sm:flex-row gap-2 max-w-xl"
            onSubmit={(e) => {
              e.preventDefault();
              handleShorten();
            }}
          >
            <div className="flex-1 flex items-center px-4 bg-vybe-gray border-2 border-transparent focus-within:border-vybe-black transition-colors">
              <svg
                className="w-5 h-5 text-vybe-dark/50 mr-2"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                role="img"
                aria-label="Link icon"
              >
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
              </svg>
              <input
                type="text"
                placeholder="Paste your long URL here..."
                className="w-full bg-transparent py-4 outline-none font-medium placeholder:text-vybe-dark/50"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
              />
            </div>
            <Button variant="dark" size="lg" className="shrink-0" type="submit" disabled={loading}>
              {loading ? '...' : 'Shorten →'}
            </Button>
          </form>

          {result && (
            <div className="bg-vybe-light p-4 border-2 border-vybe-black shadow-[4px_4px_0px_0px_#0a1f0c] max-w-xl">
              <p className="text-sm font-bold text-vybe-dark/70 mb-1">Your shortened link:</p>
              <div className="flex items-center gap-3">
                <a
                  href={result}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-lg font-extrabold text-vybe-primary hover:underline"
                >
                  {result}
                </a>
                <button
                  type="button"
                  className="px-3 py-1 text-sm font-bold border-2 border-vybe-black bg-vybe-gray hover:bg-vybe-accent transition-colors"
                  onClick={() => {
                    navigator.clipboard.writeText(result);
                  }}
                >
                  Copy
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-100 border-2 border-red-400 text-red-700 px-4 py-2 font-bold max-w-xl">
              {error}
            </div>
          )}

          {/* Inline Features */}
          <div className="flex flex-wrap gap-3 pt-4">
            {['AI Slugs', 'Smart Routing', 'Analytics', 'Secure Links'].map((feat) => (
              <span
                key={feat}
                className="inline-flex items-center gap-1.5 px-3 py-1 bg-vybe-light border-2 border-vybe-black text-sm font-bold shadow-[2px_2px_0px_0px_#0a1f0c]"
              >
                {feat}
              </span>
            ))}
          </div>
        </div>

        {/* Right Column - Browser Mockup */}
        <Link href="/dashboard" className="relative block group cursor-pointer min-h-[600px]">
          <div className="bg-vybe-light border-2 border-vybe-black rounded-2xl shadow-[12px_12px_0px_0px_#0a1f0c] group-hover:shadow-[16px_16px_0px_0px_#0a1f0c] group-hover:-translate-y-2 transition-all duration-300 overflow-hidden h-full">
            {/* Browser Header */}
            <div className="bg-vybe-black px-4 py-3 flex items-center gap-2 h-12">
              <div className="w-3 h-3 rounded-full bg-[#ff5f57]" />
              <div className="w-3 h-3 rounded-full bg-[#febc2e]" />
              <div className="w-3 h-3 rounded-full bg-[#28c840]" />
              <div className="ml-4 bg-vybe-darkgray text-vybe-light/50 text-xs px-4 py-1 rounded-full font-mono flex-1 text-center truncate">
                vybe.link/dashboard
              </div>
            </div>
            {/* Browser Content */}
            <div className="p-6 bg-vybe-gray grid gap-4 min-h-[550px]">
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
                {[40, 70, 45, 90, 65, 100, 80].map((h) => (
                  <div
                    key={h}
                    className="flex-1 bg-vybe-primary border-2 border-vybe-black relative group/bar transition-all hover:bg-vybe-accent"
                    style={{ height: `${h}%` }}
                  >
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
