"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const AnimatedNavLink = ({ href, children }: { href: string; children: React.ReactNode }) => {
  const defaultTextColor = 'text-muted-foreground';
  const hoverTextColor = 'text-foreground';
  const textSizeClass = 'text-sm font-bold';

  return (
    <Link href={href} className={`group relative inline-block overflow-hidden h-5 flex items-center ${textSizeClass}`}>
      <div className="flex flex-col transition-transform duration-300 ease-out transform group-hover:-translate-y-1/2">
        <span className={defaultTextColor}>{children}</span>
        <span className={hoverTextColor}>{children}</span>
      </div>
    </Link>
  );
};

export function MiniNavbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [headerShapeClass, setHeaderShapeClass] = useState('rounded-full');
  const shapeTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pathname = usePathname();

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  useEffect(() => {
    if (shapeTimeoutRef.current) {
      clearTimeout(shapeTimeoutRef.current);
    }

    if (isOpen) {
      setHeaderShapeClass('rounded-2xl');
    } else {
      shapeTimeoutRef.current = setTimeout(() => {
        setHeaderShapeClass('rounded-full');
      }, 300);
    }

    return () => {
      if (shapeTimeoutRef.current) {
        clearTimeout(shapeTimeoutRef.current);
      }
    };
  }, [isOpen]);

  const navLinksData = [
    { label: 'Product', href: '#product' },
    { label: 'Features', href: '#features' },
    { label: 'SRE Dashboard', href: '/admin' },
  ];

  return (
    <header className={`fixed top-6 left-1/2 transform -translate-x-1/2 z-50
                       flex flex-col items-center
                       px-6 py-3 backdrop-blur-xl
                       ${headerShapeClass}
                       border border-border/40 bg-white/60
                       w-[calc(100%-2rem)] sm:w-auto
                       transition-[border-radius,background-color] duration-300 ease-in-out shadow-lg`}>

      <div className="flex items-center justify-between w-full gap-x-8">
        <Link href="/" className="flex items-center gap-2">
           <div className="w-6 h-6 rounded bg-foreground flex items-center justify-center text-background font-bold text-xs">V</div>
           <span className="text-foreground font-bold tracking-tight hidden sm:block">Vybe</span>
        </Link>

        <nav className="hidden sm:flex items-center space-x-6">
          {navLinksData.map((link) => (
            <AnimatedNavLink key={link.href} href={link.href}>
              {link.label}
            </AnimatedNavLink>
          ))}
        </nav>

        <div className="hidden sm:flex items-center gap-3">
          <Link href="/auth" className="text-sm font-bold text-muted-foreground hover:text-foreground transition-colors">
            Log in
          </Link>
          <Link href="/auth" className="px-4 py-1.5 text-sm font-bold text-background bg-foreground rounded-full hover:bg-foreground/90 transition-colors shadow-md">
            Sign up
          </Link>
        </div>

        <button className="sm:hidden flex items-center justify-center w-8 h-8 text-muted-foreground focus:outline-none" onClick={toggleMenu}>
          {isOpen ? (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
          )}
        </button>
      </div>

      <div className={`sm:hidden flex flex-col items-center w-full transition-all ease-in-out duration-300 overflow-hidden
                       ${isOpen ? 'max-h-[400px] opacity-100 pt-6 pb-2' : 'max-h-0 opacity-0 pt-0 pointer-events-none'}`}>
        <nav className="flex flex-col items-center space-y-4 w-full">
          {navLinksData.map((link) => (
            <Link key={link.href} href={link.href} className="text-muted-foreground hover:text-foreground transition-colors w-full text-center font-bold" onClick={() => setIsOpen(false)}>
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="flex flex-col items-center space-y-3 mt-6 w-full pt-6 border-t border-border/20">
          <Link href="/auth" className="w-full text-center py-2 text-muted-foreground hover:text-foreground font-bold" onClick={() => setIsOpen(false)}>
            Log in
          </Link>
          <Link href="/auth" className="w-full text-center py-2 bg-foreground text-background rounded-full font-bold shadow-md" onClick={() => setIsOpen(false)}>
            Sign up
          </Link>
        </div>
      </div>
    </header>
  );
}
