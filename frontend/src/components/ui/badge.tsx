import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral';
}

export const Badge: React.FC<BadgeProps> = ({ children, className, variant = 'neutral', ...props }) => {
  const styles = {
    success: 'bg-emerald-950/80 text-emerald-400 border-emerald-800/60',
    warning: 'bg-amber-950/80 text-amber-400 border-amber-800/60',
    error: 'bg-rose-950/80 text-rose-400 border-rose-800/60',
    info: 'bg-sky-950/80 text-sky-400 border-sky-800/60',
    neutral: 'bg-slate-800/80 text-slate-300 border-slate-700',
  };

  return (
    <span
      className={twMerge(
        clsx('inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border shadow-inner', styles[variant], className)
      )}
      {...props}
    >
      {children}
    </span>
  );
};
