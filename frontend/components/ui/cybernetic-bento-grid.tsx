"use client";

import React, { useEffect, useRef } from 'react';
import { cn } from "@/lib/utils";

const BentoItem = ({ className, children }: { className?: string, children: React.ReactNode }) => {
    const itemRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const item = itemRef.current;
        if (!item) return;

        const handleMouseMove = (e: MouseEvent) => {
            const rect = item.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            item.style.setProperty('--mouse-x', `${x}px`);
            item.style.setProperty('--mouse-y', `${y}px`);
        };

        item.addEventListener('mousemove', handleMouseMove);

        return () => {
            item.removeEventListener('mousemove', handleMouseMove);
        };
    }, []);

    return (
        <div 
            ref={itemRef} 
            className={cn(
                "relative overflow-hidden rounded-2xl border border-border/40 bg-white/40 p-6 backdrop-blur-md group shadow-sm transition-all hover:shadow-md hover:border-border/60",
                className
            )}
        >
            <div 
                className="pointer-events-none absolute -inset-px opacity-0 transition duration-300 group-hover:opacity-100"
                style={{
                    background: `radial-gradient(600px circle at var(--mouse-x) var(--mouse-y), rgba(255,192,203,0.1), transparent 40%)`
                }}
            />
            <div className="relative z-10 h-full flex flex-col">
                {children}
            </div>
        </div>
    );
};

export const CyberneticBentoGrid = () => {
    return (
        <div className="w-full max-w-6xl mx-auto z-10 py-12 px-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[220px]">
                <BentoItem className="md:col-span-2 md:row-span-2 flex flex-col justify-between">
                    <div>
                        <h3 className="text-2xl font-bold text-foreground">AI-Powered Slug Generation</h3>
                        <p className="mt-4 text-muted-foreground font-medium leading-relaxed">
                            Generate context-aware, readable, and SEO-friendly URLs instead of random strings. Improve memorability, branding, and trust with every link.
                        </p>
                        <p className="mt-6 text-sm text-secondary font-bold uppercase tracking-wider">No more aB12xK — get meaningful links instantly.</p>
                    </div>
                    <div className="mt-8 flex-1 bg-muted/20 rounded-xl flex items-center justify-center text-muted-foreground border border-border/20 overflow-hidden relative">
                        <div className="absolute inset-0 bg-[linear-gradient(to_right,#88888815_1px,transparent_1px),linear-gradient(to_bottom,#88888815_1px,transparent_1px)] bg-[size:14px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
                        <div className="z-10 flex items-center gap-2 font-bold text-sm">
                            <span className="text-muted-foreground/60">vybe.link/</span>
                            <span className="text-foreground bg-white/60 px-3 py-1.5 rounded-lg shadow-sm">summer-sale-2026</span>
                        </div>
                    </div>
                </BentoItem>
                <BentoItem>
                    <h3 className="text-xl font-bold text-foreground">Conditional Redirects</h3>
                    <p className="mt-3 text-muted-foreground text-sm font-medium">Dynamically route users based on device, location, or timing. Send mobile users to apps, desktop users to web.</p>
                    <p className="mt-4 text-[10px] text-secondary font-bold uppercase tracking-widest">One link. Multiple outcomes.</p>
                </BentoItem>
                <BentoItem>
                    <h3 className="text-xl font-bold text-foreground">Asynchronous Analytics</h3>
                    <p className="mt-3 text-muted-foreground text-sm font-medium">Redirect instantly while analytics are processed asynchronously. Built with scalable architecture.</p>
                    <p className="mt-4 text-[10px] text-secondary font-bold uppercase tracking-widest">Fast redirects. Zero compromise.</p>
                </BentoItem>
                <BentoItem className="md:row-span-2">
                    <h3 className="text-xl font-bold text-foreground">Security First</h3>
                    <p className="mt-3 text-muted-foreground text-sm font-medium">Isolated custom domains, password-protected links, auto-expiration, and QR generation — all designed to prevent misuse and ensure control.</p>
                    <p className="mt-4 text-[10px] text-secondary font-bold uppercase tracking-widest">Every link is secure.</p>
                    <div className="mt-6 flex-1 bg-muted/20 rounded-xl flex items-center justify-center border border-border/20">
                        <svg className="w-16 h-16 text-muted-foreground/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                        </svg>
                    </div>
                </BentoItem>
                <BentoItem className="md:col-span-2">
                    <h3 className="text-xl font-bold text-foreground">Monetization & Tracking</h3>
                    <p className="mt-3 text-muted-foreground text-sm font-medium">Track performance, measure conversions, and monetize clicks directly without relying on external tools or fragmented systems.</p>
                    <p className="mt-4 text-[10px] text-secondary font-bold uppercase tracking-widest">Your links. Your revenue.</p>
                </BentoItem>
            </div>
        </div>
    );
};
