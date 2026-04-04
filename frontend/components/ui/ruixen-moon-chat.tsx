"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
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
} from "lucide-react";
import { ShaderAnimation } from "./shader-animation";
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
    <div className="relative w-full min-h-screen flex flex-col items-center justify-center overflow-hidden bg-black">
      <div className="absolute inset-0 z-0">
        <ShaderAnimation />
      </div>
      
      {/* Overlay to ensure readability */}
      <div className="absolute inset-0 bg-black/20 z-1" />
      
      {/* Centered Title */}
      <div className="relative z-10 flex-1 w-full flex flex-col items-center justify-center px-4 pt-20">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-6xl sm:text-8xl font-bold text-white tracking-tighter mb-8">
            Links that do <span className="text-cyan-400">more</span>.
          </h1>
          <p className="mt-6 text-xl sm:text-2xl text-neutral-300 max-w-3xl mx-auto leading-relaxed">
            Vybe turns every URL into an intelligent, observable system — built for scale, control, and real-world production.
          </p>
        </div>
      </div>

      {/* Input Box Section */}
      <div className="relative z-10 w-full max-w-4xl mb-[10vh] px-4">
        {!shortened ? (
          <div className="relative bg-black/40 backdrop-blur-3xl rounded-3xl border border-white/10 shadow-[0_0_50px_-12px_rgba(0,255,255,0.3)] overflow-hidden transition-all duration-500 hover:border-white/20">
            <div className="flex items-center px-6 py-4 border-b border-white/5 bg-white/5">
                <LinkIcon className="w-5 h-5 text-cyan-400 mr-3" />
                <span className="text-sm font-medium text-neutral-200">Create intelligent link</span>
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
                "bg-transparent text-white text-xl sm:text-2xl",
                "focus-visible:ring-0 focus-visible:ring-offset-0",
                "placeholder:text-neutral-500 min-h-[100px]",
                error && "text-red-400"
              )}
              style={{ overflow: "hidden" }}
            />
            {error && (
              <div className="px-6 pb-4 text-sm text-red-500 animate-in fade-in slide-in-from-top-1">
                {error}
              </div>
            )}

            {/* Footer Buttons */}
            <div className="flex items-center justify-between p-6 bg-white/5 border-t border-white/5">
              <div className="flex gap-4 items-center overflow-x-auto no-scrollbar">
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-mono text-neutral-400 uppercase tracking-wider whitespace-nowrap">
                   <div className="w-1 h-1 rounded-full bg-cyan-400" />
                   AI Slugs
                </div>
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-mono text-neutral-400 uppercase tracking-wider whitespace-nowrap">
                   <div className="w-1 h-1 rounded-full bg-cyan-400" />
                   Smart Routing
                </div>
              </div>

              <div className="flex items-center gap-2 ml-auto">
                <Button
                  onClick={handleShorten}
                  disabled={!url.trim()}
                  size="lg"
                  className={cn(
                    "flex items-center gap-2 px-8 py-6 rounded-2xl transition-all font-bold text-lg shadow-xl",
                    url.trim() ? "bg-cyan-500 text-black hover:bg-cyan-400 hover:scale-[1.02]" : "bg-neutral-800 text-neutral-500 cursor-not-allowed"
                  )}
                >
                  <span>Shorten</span>
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </div>
            </div>
          </div>
        ) : (
          <div className="relative bg-black/40 backdrop-blur-3xl rounded-3xl border border-cyan-500/30 shadow-[0_0_50px_-12px_rgba(0,255,255,0.5)] overflow-hidden animate-in fade-in zoom-in-95 duration-500">
             <div className="flex items-center px-6 py-4 border-b border-cyan-500/20 bg-cyan-500/10">
                <div className="w-2 h-2 rounded-full bg-cyan-400 mr-3 animate-pulse" />
                <span className="text-sm font-medium text-cyan-300">Link created successfully</span>
            </div>
            <div className="p-8 sm:p-12">
                <div className="flex flex-col sm:flex-row items-center justify-between gap-8">
                    <div className="flex-1 w-full space-y-2">
                        <p className="text-sm text-neutral-500 truncate max-w-md">{url}</p>
                        <div className="flex items-center gap-3">
                            <span className="text-3xl sm:text-5xl font-bold text-white tracking-tighter">vybe.link/<span className="text-cyan-400">xyz123</span></span>
                        </div>
                    </div>
                    <div className="flex items-center gap-3 w-full sm:w-auto">
                        <Button 
                          variant="outline" 
                          size="lg"
                          onClick={() => {
                            navigator.clipboard.writeText("vybe.link/xyz123");
                          }}
                          className="flex-1 sm:flex-none rounded-2xl border-white/10 bg-white/5 hover:bg-white/10 text-white h-14 px-6"
                        >
                            <Copy className="w-5 h-5 mr-2" />
                            Copy
                        </Button>
                        <Button variant="outline" size="icon" className="rounded-2xl border-white/10 bg-white/5 hover:bg-white/10 text-white h-14 w-14">
                            <QrCode className="w-6 h-6" />
                        </Button>
                    </div>
                </div>
            </div>
            <div className="flex items-center justify-between p-6 bg-white/5 border-t border-white/5">
                <Button variant="ghost" className="text-neutral-400 hover:text-white text-base" onClick={() => {setUrl(""); setShortened(false);}}>
                    Create another
                </Button>
                <Button variant="link" className="text-cyan-400 hover:text-cyan-300 text-base font-bold">
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

interface QuickActionProps {
  icon: React.ReactNode;
  label: string;
}

function QuickAction({ icon, label }: QuickActionProps) {
  return (
    <button className="flex items-center gap-3 rounded-2xl border border-white/5 bg-white/5 px-6 py-3 text-neutral-300 backdrop-blur-md transition-all hover:bg-white/10 hover:border-white/20 hover:scale-105 active:scale-95 group">
      <span className="text-cyan-400 transition-transform group-hover:scale-110">{icon}</span>
      <span className="text-sm font-semibold tracking-wide uppercase">{label}</span>
    </button>
  );
}
