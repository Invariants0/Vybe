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
import { ShaderAnimation } from "./shader-lines";

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

import { urlSchema } from "@/lib/validations/auth";

export function HeroShortener() {
  const [url, setUrl] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [shortened, setShortened] = useState(false);
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 48,
    maxHeight: 150,
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
    <div className="relative w-full min-h-[90vh] flex flex-col items-center justify-center overflow-hidden bg-black">
      <ShaderAnimation />
      
      {/* Centered Title */}
      <div className="relative z-10 flex-1 w-full flex flex-col items-center justify-center px-4 pt-20">
        <div className="text-center max-w-3xl mx-auto">
          <h1 className="text-5xl sm:text-7xl font-bold text-white tracking-tight">
            Links that do more than redirect.
          </h1>
          <p className="mt-6 text-xl text-neutral-400 max-w-2xl mx-auto">
            Vybe turns every URL into an intelligent, observable system — built for scale, control, and real-world production.
          </p>
        </div>
      </div>

      {/* Input Box Section */}
      <div className="relative z-10 w-full max-w-3xl mb-[15vh] px-4">
        {!shortened ? (
          <div className="relative bg-black/60 backdrop-blur-xl rounded-2xl border border-neutral-800 shadow-2xl overflow-hidden">
            <div className="flex items-center px-4 py-3 border-b border-neutral-800/50 bg-white/5">
                <LinkIcon className="w-5 h-5 text-neutral-400 mr-3" />
                <span className="text-sm font-medium text-neutral-300">Create new link</span>
            </div>
            <Textarea
              ref={textareaRef}
              value={url}
              onChange={(e) => {
                setUrl(e.target.value);
                if (error) setError(null);
                adjustHeight();
              }}
              placeholder="Paste your long URL here..."
              className={cn(
                "w-full px-4 py-6 resize-none border-none",
                "bg-transparent text-white text-lg",
                "focus-visible:ring-0 focus-visible:ring-offset-0",
                "placeholder:text-neutral-600 min-h-[80px]",
                error && "text-red-400"
              )}
              style={{ overflow: "hidden" }}
            />
            {error && (
              <div className="px-4 pb-2 text-xs text-red-500 animate-in fade-in slide-in-from-top-1">
                {error}
              </div>
            )}

            {/* Footer Buttons */}
            <div className="flex items-center justify-between p-4 bg-black/40 border-t border-neutral-800/50">
              <div className="text-xs text-neutral-500 hidden sm:block">
                AI-generated slugs • Smart routing • Built for production
              </div>

              <div className="flex items-center gap-2 ml-auto">
                <Button
                  onClick={handleShorten}
                  disabled={!url.trim()}
                  className={cn(
                    "flex items-center gap-2 px-6 py-2 rounded-full transition-all font-medium",
                    url.trim() ? "bg-white text-black hover:bg-neutral-200" : "bg-neutral-800 text-neutral-500 cursor-not-allowed"
                  )}
                >
                  <span>Shorten</span>
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        ) : (
          <div className="relative bg-black/60 backdrop-blur-xl rounded-2xl border border-neutral-800 shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
             <div className="flex items-center px-4 py-3 border-b border-neutral-800/50 bg-green-500/10">
                <div className="w-2 h-2 rounded-full bg-green-500 mr-3 animate-pulse" />
                <span className="text-sm font-medium text-green-400">Link created successfully</span>
            </div>
            <div className="p-6 sm:p-8">
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                    <div className="flex-1 w-full">
                        <p className="text-xs text-neutral-500 mb-1 truncate">{url}</p>
                        <div className="flex items-center gap-3">
                            <span className="text-2xl sm:text-3xl font-mono text-white tracking-tight">vybe.link/xyz123</span>
                        </div>
                    </div>
                    <div className="flex items-center gap-2 w-full sm:w-auto">
                        <Button variant="outline" className="flex-1 sm:flex-none rounded-full border-neutral-700 hover:bg-neutral-800">
                            <Copy className="w-4 h-4 mr-2" />
                            Copy
                        </Button>
                        <Button variant="outline" size="icon" className="rounded-full border-neutral-700 hover:bg-neutral-800">
                            <QrCode className="w-4 h-4" />
                        </Button>
                    </div>
                </div>
            </div>
            <div className="flex items-center justify-between p-4 bg-black/40 border-t border-neutral-800/50">
                <Button variant="ghost" className="text-neutral-400 hover:text-white text-sm" onClick={() => {setUrl(""); setShortened(false);}}>
                    Create another
                </Button>
                <Button variant="link" className="text-cyan-400 hover:text-cyan-300 text-sm">
                    View Analytics →
                </Button>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        {!shortened && (
            <div className="flex items-center justify-center flex-wrap gap-3 mt-8">
            <QuickAction icon={<BarChart3 className="w-4 h-4" />} label="Real-time Analytics" />
            <QuickAction icon={<Settings2 className="w-4 h-4" />} label="Smart Routing" />
            <QuickAction icon={<ShieldCheck className="w-4 h-4" />} label="Domain Isolation" />
            <QuickAction icon={<Globe className="w-4 h-4" />} label="Global CDN" />
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
    <div className="flex items-center gap-2 rounded-full border border-neutral-800 bg-black/50 px-4 py-2 text-neutral-400 backdrop-blur-sm">
      {icon}
      <span className="text-xs font-medium">{label}</span>
    </div>
  );
}
