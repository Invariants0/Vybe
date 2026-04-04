import React from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'dark';
  size?: 'sm' | 'md' | 'lg';
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', ...props }, ref) => {
    const baseStyles = "inline-flex items-center justify-center font-bold transition-all duration-200 border-2 border-vybe-black";
    
    const variants = {
      primary: "bg-vybe-primary text-vybe-black hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none",
      secondary: "bg-vybe-light text-vybe-black hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none",
      dark: "bg-vybe-black text-vybe-light hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none",
      ghost: "border-transparent bg-transparent hover:bg-vybe-gray shadow-none hover:shadow-none hover:translate-x-0 hover:translate-y-0",
    };

    const sizes = {
      sm: "px-4 py-2 text-sm shadow-[2px_2px_0px_0px_#0a1f0c]",
      md: "px-6 py-3 text-base shadow-[4px_4px_0px_0px_#0a1f0c]",
      lg: "px-8 py-4 text-lg shadow-[8px_8px_0px_0px_#0a1f0c]",
    };

    const shadowClass = variant === 'ghost' ? 'shadow-none' : sizes[size];

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], shadowClass, className)}
        {...props}
      />
    );
  }
);
Button.displayName = 'Button';
