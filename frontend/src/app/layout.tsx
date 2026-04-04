import type { Metadata } from 'next';
import { Space_Grotesk, Inter } from 'next/font/google';
import './globals.css';

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-space-grotesk',
  display: 'block',
  preload: true,
  fallback: ['Arial', 'sans-serif'],
  adjustFontFallback: true,
  weight: ['400', '700'],
});

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'block',
  preload: true,
  fallback: ['Arial', 'sans-serif'],
  adjustFontFallback: true,
  weight: ['400', '500', '600', '700'],
});

export const metadata: Metadata = {
  title: 'VYBE - Production-Ready Link System',
  description: 'More than a shortener — a production-ready link system.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${spaceGrotesk.variable} ${inter.variable}`}>
      <head>
        <link rel="dns-prefetch" href="https://fonts.googleapis.com" />
        <link rel="dns-prefetch" href="https://fonts.gstatic.com" />
        <style dangerouslySetInnerHTML={{__html: `
          .font-heading{font-family:Arial,sans-serif;font-weight:800}
          .font-body{font-family:Arial,sans-serif}
          .bg-vybe-primary{background-color:#87ceeb}
          .bg-vybe-light{background-color:#f7f9fa}
          .bg-vybe-black{background-color:#333}
          .text-vybe-black{color:#333}
          .border-vybe-black{border-color:#333}
          h1{min-height:200px}
          @media(min-width:768px){h1{min-height:280px}}
        `}} />
      </head>
      <body className="font-body bg-vybe-light text-vybe-black antialiased selection:bg-vybe-accent selection:text-vybe-black">
        {children}
      </body>
    </html>
  );
}
