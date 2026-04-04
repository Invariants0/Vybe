"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import Link from "next/link";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  Link as LinkIcon,
  ArrowRight,
  Copy,
  QrCode,
  Settings2,
  BarChart3,
  Globe,
  ShieldCheck,
  LayoutDashboard,
} from "lucide-react";
import { urlSchema } from "@/lib/validations/auth";

interface AutoResizeProps {
  minHeight: number;
  maxHeight?: number;
}

function useAutoResizeTextarea({ minHeight, maxHeight }: AutoResizeProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(
    (reset?: boolean) => {
      const textarea = textareaRef.current;
      if (!textarea) return;

      if (reset) {
        textarea.style.height = `${minHeight}px`;
        return;
      }

      textarea.style.height = `${minHeight}px`; // reset first
      const newHeight = Math.max(
        minHeight,
        Math.min(textarea.scrollHeight, maxHeight ?? Infinity)
      );
      textarea.style.height = `${newHeight}px`;
    },
    [minHeight, maxHeight]
  );

  useEffect(() => {
    if (textareaRef.current) textareaRef.current.style.height = `${minHeight}px`;
  }, [minHeight]);

  return { textareaRef, adjustHeight };
}

interface QuickActionProps {
  icon: React.ReactNode;
  label: string;
}

function QuickAction({ icon, label }: QuickActionProps) {
  return (
    <button className="flex items-center gap-3 rounded-2xl border border-border/20 bg-white/40 px-6 py-3 text-foreground/80 backdrop-blur-md transition-all hover:bg-white/60 hover:border-border/40 hover:scale-105 active:scale-95 group shadow-sm">
      <span className="text-secondary transition-transform group-hover:scale-110">{icon}</span>
      <span className="text-xs font-bold tracking-widest uppercase">{label}</span>
    </button>
  );
}

export function HeroShortener() {
  const [url, setUrl] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [shortened, setShortened] = useState(false);
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 56,
    maxHeight: 200,
  });

  const handleShorten = () => {
    const result = urlSchema.safeParse({ url: url.trim() });
    if (!result.success) {
      setError(result.error.errors[0].message);
      return;
    }
    
    setError(null);
    setShortened(true);
  };

  return (
    <div className="relative w-full min-h-screen flex flex-col items-center justify-center overflow-hidden bg-background">
      {/* Light Gradient Background */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,192,203,0.15),transparent_50%),radial-gradient(circle_at_bottom_left,rgba(135,206,235,0.15),transparent_50%)] z-0" />
      
      {/* Centered Title */}
      <div className="relative z-10 flex-1 w-full flex flex-col items-center justify-center px-4 pt-20">
        <div className="text-center max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary-foreground text-sm font-semibold mb-8 backdrop-blur-sm">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            INTELLIGENT INFRASTRUCTURE
          </div>
          <h1 className="text-6xl sm:text-8xl font-bold text-foreground tracking-tighter mb-8">
            Links that do <span className="text-secondary">more</span>.
          </h1>
          <p className="mt-6 text-xl sm:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            Vybe turns every URL into an intelligent, observable system — built for scale, control, and real-world production.
          </p>
          <div className="mt-10 flex justify-center gap-4">
            <Link href="/admin">
              <Button size="lg" className="rounded-2xl px-8 py-6 font-bold text-lg bg-foreground text-background hover:bg-foreground/90 transition-all shadow-lg hover:scale-105 active:scale-95 flex items-center gap-2">
                <LayoutDashboard className="w-5 h-5" />
                SRE Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Input Box Section */}
      <div className="relative z-10 w-full max-w-4xl mb-[10vh] px-4">
        {!shortened ? (
          <div className="relative bg-white/60 backdrop-blur-xl rounded-3xl border border-border/40 shadow-xl overflow-hidden transition-all duration-500 hover:border-border/60">
            <div className="flex items-center px-6 py-4 border-b border-border/20 bg-muted/30">
                <LinkIcon className="w-5 h-5 text-secondary mr-3" />
                <span className="text-sm font-medium text-foreground/80">Create intelligent link</span>
            </div>
            <Textarea
              ref={textareaRef}
              value={url}
              onChange={(e) => {
                setUrl(e.target.value);
                if (error) setError(null);
                adjustHeight();
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleShorten();
                }
              }}
              placeholder="Paste your long URL here..."
              className={cn(
                "w-full px-6 py-8 resize-none border-none",
                "bg-transparent text-foreground text-xl sm:text-2xl",
                "focus-visible:ring-0 focus-visible:ring-offset-0",
                "placeholder:text-muted-foreground min-h-[100px]",
                error && "text-destructive"
              )}
              style={{ overflow: "hidden" }}
            />
            {error && (
              <div className="px-6 pb-4 text-sm text-destructive animate-in fade-in slide-in-from-top-1">
                {error}
              </div>
            )}

            {/* Footer Buttons */}
            <div className="flex items-center justify-between p-6 bg-muted/10 border-t border-border/20">
              <div className="flex gap-4 items-center overflow-x-auto no-scrollbar">
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/40 border border-border/40 text-[10px] font-bold text-muted-foreground uppercase tracking-wider whitespace-nowrap">
                   <div className="w-1 h-1 rounded-full bg-secondary" />
                   AI Slugs
                </div>
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/40 border border-border/40 text-[10px] font-bold text-muted-foreground uppercase tracking-wider whitespace-nowrap">
                   <div className="w-1 h-1 rounded-full bg-secondary" />
                   Smart Routing
                </div>
              </div>

              <div className="flex items-center gap-2 ml-auto">
                <Button
                  onClick={handleShorten}
                  disabled={!url.trim()}
                  size="lg"
                  className={cn(
                    "flex items-center gap-2 px-8 py-6 rounded-2xl transition-all font-bold text-lg shadow-lg",
                    url.trim() ? "bg-primary text-primary-foreground hover:bg-primary/90 hover:scale-[1.02]" : "bg-muted text-muted-foreground cursor-not-allowed"
                  )}
                >
                  <span>Shorten</span>
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </div>
            </div>
          </div>
        ) : (
          <div className="relative bg-white/60 backdrop-blur-xl rounded-3xl border border-primary/30 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-500">
             <div className="flex items-center px-6 py-4 border-b border-primary/20 bg-primary/10">
                <div className="w-2 h-2 rounded-full bg-primary mr-3 animate-pulse" />
                <span className="text-sm font-semibold text-primary-foreground">Link created successfully</span>
            </div>
            <div className="p-8 sm:p-12">
                <div className="flex flex-col sm:flex-row items-center justify-between gap-8">
                    <div className="flex-1 w-full space-y-2">
                        <p className="text-sm text-muted-foreground truncate max-w-md">{url}</p>
                        <div className="flex items-center gap-3">
                            <span className="text-3xl sm:text-5xl font-bold text-foreground tracking-tighter">vybe.link/<span className="text-secondary">xyz123</span></span>
                        </div>
                    </div>
                    <div className="flex items-center gap-3 w-full sm:w-auto">
                        <Button 
                          variant="outline" 
                          size="lg"
                          onClick={() => {
                            navigator.clipboard.writeText("vybe.link/xyz123");
                          }}
                          className="flex-1 sm:flex-none rounded-2xl border-border/40 bg-white/40 hover:bg-white/60 text-foreground h-14 px-6"
                        >
                            <Copy className="w-5 h-5 mr-2" />
                            Copy
                        </Button>
                        <Button variant="outline" size="icon" className="rounded-2xl border-border/40 bg-white/40 hover:bg-white/60 text-foreground h-14 w-14">
                            <QrCode className="w-6 h-6" />
                        </Button>
                    </div>
                </div>
            </div>
            <div className="flex items-center justify-between p-6 bg-muted/10 border-t border-border/20">
                <Button variant="ghost" className="text-muted-foreground hover:text-foreground text-base" onClick={() => {setUrl(""); setShortened(false);}}>
                    Create another
                </Button>
                <Button variant="link" className="text-secondary hover:text-secondary/80 text-base font-bold">
                    View Analytics →
                </Button>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        {!shortened && (
            <div className="flex items-center justify-center flex-wrap gap-4 mt-12">
            <QuickAction icon={<BarChart3 className="w-5 h-5" />} label="Real-time Analytics" />
            <QuickAction icon={<Settings2 className="w-5 h-5" />} label="Smart Routing" />
            <QuickAction icon={<ShieldCheck className="w-5 h-5" />} label="Domain Isolation" />
            <QuickAction icon={<Globe className="w-5 h-5" />} label="Global CDN" />
            </div>
        )}
      </div>
    </div>
  );
}
