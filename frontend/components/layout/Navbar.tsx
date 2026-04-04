"use client";

import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Zap, Github } from 'lucide-react';

export function Navbar() {
  return (
    <nav className="sticky top-0 z-50 h-20 bg-vybe-primary border-b-2 border-vybe-black flex items-center justify-between px-6 md:px-12">
      <div className="flex items-center gap-2">
        <div className="w-10 h-10 bg-vybe-black flex items-center justify-center">
          <Zap className="text-vybe-primary w-6 h-6 fill-current" />
        </div>
        <span className="font-heading font-extrabold text-2xl tracking-tighter">VYBE</span>
      </div>
      
      <div className="hidden md:flex items-center gap-8 font-bold">
        <Link href="#product" className="hover:underline decoration-2 underline-offset-4">Product</Link>
        <Link href="#features" className="hover:underline decoration-2 underline-offset-4">Features</Link>
        <Link href="#analytics" className="hover:underline decoration-2 underline-offset-4">Analytics</Link>
        <Link href="#sre" className="hover:underline decoration-2 underline-offset-4">SRE Dashboard</Link>
      </div>

      <div className="flex items-center gap-4">
        <a href="https://github.com/Invariants0/Vybe" target="_blank" rel="noopener noreferrer" className="hidden md:flex items-center gap-2 font-bold hover:underline decoration-2 underline-offset-4">
          <Github className="w-5 h-5" /> GitHub
        </a>
        <Button variant="dark">Try Demo</Button>
      </div>
    </nav>
  );
}
