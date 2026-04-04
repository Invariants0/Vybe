'use client';
import React from 'react';
import type { ComponentProps, ReactNode } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { FacebookIcon, InstagramIcon, LinkedinIcon, YoutubeIcon } from 'lucide-react';

interface FooterLink {
	title: string;
	href: string;
	icon?: React.ComponentType<{ className?: string }>;
}

interface FooterSection {
	label: string;
	links: FooterLink[];
}

const footerLinks: FooterSection[] = [
	{
		label: 'Product',
		links: [
			{ title: 'Features', href: '#features' },
			{ title: 'Dashboard', href: '/dashboard' },
			{ title: 'Docs', href: '/docs' },
		],
	},
	{
		label: 'Company',
		links: [
			{ title: 'About', href: '/about' },
			{ title: 'GitHub', href: 'https://github.com' },
		],
	},
	{
		label: 'Legal',
		links: [
			{ title: 'Privacy', href: '/privacy' },
			{ title: 'Terms', href: '/terms' },
		],
	},
	{
		label: 'Social Links',
		links: [
			{ title: 'Facebook', href: '#', icon: FacebookIcon },
			{ title: 'Instagram', href: '#', icon: InstagramIcon },
			{ title: 'Youtube', href: '#', icon: YoutubeIcon },
			{ title: 'LinkedIn', href: '#', icon: LinkedinIcon },
		],
	},
];

export function Footer() {
	return (
		<footer className="relative w-full border-t border-border/20 bg-white/40 backdrop-blur-md px-6 py-12 lg:py-16">
			<div className="absolute top-0 right-1/2 left-1/2 h-px w-1/3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/20 blur" />

			<div className="max-w-6xl mx-auto grid w-full gap-8 xl:grid-cols-3 xl:gap-8">
				<AnimatedContainer className="space-y-4">
                    <div className="flex items-center gap-2">
					    <div className="w-8 h-8 rounded-lg bg-foreground flex items-center justify-center text-background font-bold">V</div>
                        <span className="text-xl font-bold text-foreground tracking-tight">Vybe</span>
                    </div>
					<p className="text-muted-foreground mt-8 text-sm md:mt-0 max-w-xs font-medium">
						Create, control, and scale your links with intelligence and reliability.
					</p>
                    <p className="text-muted-foreground/60 text-xs mt-4 font-bold">
						© {new Date().getFullYear()} Vybe. All rights reserved.
					</p>
				</AnimatedContainer>

				<div className="mt-10 grid grid-cols-2 gap-8 md:grid-cols-4 xl:col-span-2 xl:mt-0">
					{footerLinks.map((section, index) => (
						<AnimatedContainer key={section.label} delay={0.1 + index * 0.1}>
							<div className="mb-10 md:mb-0">
								<h3 className="text-sm font-bold text-foreground">{section.label}</h3>
								<ul className="text-muted-foreground mt-4 space-y-2 text-sm font-medium">
									{section.links.map((link) => (
										<li key={link.title}>
											<a
												href={link.href}
												className="hover:text-foreground inline-flex items-center transition-all duration-300"
											>
												{link.icon && <link.icon className="me-2 size-4" />}
												{link.title}
											</a>
										</li>
									))}
								</ul>
							</div>
						</AnimatedContainer>
					))}
				</div>
			</div>
		</footer>
	);
};

type ViewAnimationProps = {
	delay?: number;
	className?: ComponentProps<typeof motion.div>['className'];
	children: ReactNode;
};

function AnimatedContainer({ className, delay = 0.1, children }: ViewAnimationProps) {
	const shouldReduceMotion = useReducedMotion();

	if (shouldReduceMotion) {
		return <div className={className}>{children}</div>;
	}

	return (
		<motion.div
			initial={{ translateY: 8, opacity: 0 }}
			whileInView={{ translateY: 0, opacity: 1 }}
			viewport={{ once: true }}
			transition={{ delay, duration: 0.5 }}
			className={className}
		>
			{children}
		</motion.div>
	);
};
