import { Github, Linkedin, Twitter, Zap } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-vybe-dark text-vybe-light pt-24 pb-12 px-6 border-t-2 border-vybe-black">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
        <div className="col-span-1 md:col-span-2">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-10 h-10 bg-vybe-light flex items-center justify-center border-2 border-vybe-black shadow-[4px_4px_0px_0px_#4caf50]">
              <Zap className="text-vybe-black w-6 h-6 fill-current" />
            </div>
            <span className="font-heading font-extrabold text-3xl tracking-tighter">VYBE</span>
          </div>
          <p className="text-vybe-light/70 font-medium max-w-sm text-lg">
            Built for the internet. Designed for production.
          </p>
        </div>

        <div>
          <h4 className="font-heading font-bold text-xl mb-6 text-vybe-primary">Product</h4>
          <ul className="space-y-4 font-medium text-vybe-light/80">
            <li>
              <a
                href="#features"
                className="hover:text-vybe-light hover:underline decoration-2 underline-offset-4"
              >
                Features
              </a>
            </li>
            <li>
              <a
                href="#analytics"
                className="hover:text-vybe-light hover:underline decoration-2 underline-offset-4"
              >
                Analytics
              </a>
            </li>
            <li>
              <a
                href="#sre"
                className="hover:text-vybe-light hover:underline decoration-2 underline-offset-4"
              >
                SRE Dashboard
              </a>
            </li>
            <li>
              <a
                href="/dashboard"
                className="hover:text-vybe-light hover:underline decoration-2 underline-offset-4"
              >
                API Docs
              </a>
            </li>
          </ul>
        </div>

        <div>
          <h4 className="font-heading font-bold text-xl mb-6 text-vybe-primary">Company</h4>
          <ul className="space-y-4 font-medium text-vybe-light/80">
            <li>
              <a
                href="/"
                className="hover:text-vybe-light hover:underline decoration-2 underline-offset-4"
              >
                About
              </a>
            </li>
            <li>
              <a
                href="/"
                className="hover:text-vybe-light hover:underline decoration-2 underline-offset-4"
              >
                Blog
              </a>
            </li>
            <li>
              <a
                href="/"
                className="hover:text-vybe-light hover:underline decoration-2 underline-offset-4"
              >
                Careers
              </a>
            </li>
            <li>
              <a
                href="/"
                className="hover:text-vybe-light hover:underline decoration-2 underline-offset-4"
              >
                Contact
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center pt-8 border-t-2 border-vybe-darkgray gap-6">
        <div className="text-vybe-light/50 font-medium">
          © {new Date().getFullYear()} VYBE Inc. All rights reserved.
        </div>
        <div className="flex gap-4">
          {[
            { Icon: Twitter, name: 'Twitter', href: 'https://twitter.com' },
            { Icon: Github, name: 'Github', href: 'https://github.com' },
            { Icon: Linkedin, name: 'LinkedIn', href: 'https://linkedin.com' },
          ].map((social) => (
            <a
              key={social.name}
              href={social.href}
              aria-label={social.name}
              className="w-10 h-10 bg-vybe-darkgray border-2 border-vybe-light/20 flex items-center justify-center hover:bg-vybe-primary hover:border-vybe-black hover:text-vybe-black transition-all shadow-none hover:shadow-[4px_4px_0px_0px_#0a1f0c] hover:-translate-y-1"
            >
              <social.Icon className="w-5 h-5" />
            </a>
          ))}
        </div>
      </div>
    </footer>
  );
}
