export function HowItWorks() {
  return (
    <section className="py-24 bg-vybe-dark text-vybe-light border-b-2 border-vybe-black px-6 overflow-hidden">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-5xl font-heading font-extrabold mb-20 text-center">How it works</h2>
        
        <div className="relative flex flex-col md:flex-row justify-between items-center md:items-start gap-12 md:gap-4">
          {/* Connecting Line */}
          <div className="hidden md:block absolute top-12 left-0 w-full h-1 bg-vybe-darkgray -z-10"></div>
          
          {[
            { step: 1, title: "Paste URL", desc: "Drop your long, ugly URL into our system.", color: "border-vybe-accent" },
            { step: 2, title: "Configure", desc: "Set rules, passwords, or AI slugs.", color: "border-vybe-primary" },
            { step: 3, title: "Share & Track", desc: "Distribute and watch the analytics roll in.", color: "border-vybe-light" }
          ].map((s) => (
            <div key={s.step} className="flex flex-col items-center text-center max-w-xs bg-vybe-dark group hover:-translate-y-4 transition-transform duration-300">
              <div className={`w-24 h-24 rounded-full border-4 ${s.color} bg-vybe-black flex items-center justify-center text-3xl font-heading font-extrabold mb-6 shadow-[0_0_20px_rgba(255,255,255,0.1)] group-hover:shadow-[0_0_30px_rgba(255,255,255,0.2)] transition-shadow duration-300`}>
                {s.step}
              </div>
              <h3 className="text-2xl font-heading font-bold mb-3">{s.title}</h3>
              <p className="text-vybe-light/70 font-medium">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
