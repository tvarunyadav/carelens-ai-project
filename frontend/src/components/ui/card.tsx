import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export const Card: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => {
  return (
    <div
      className={twMerge(clsx('glass-panel rounded-xl p-6 shadow-xl border border-slate-800/80', className))}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => {
  return <div className={twMerge(clsx('mb-4 pb-3 border-b border-slate-800/60', className))} {...props}>{children}</div>;
};

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ className, children, ...props }) => {
  return <h3 className={twMerge(clsx('text-lg font-semibold text-slate-100 flex items-center gap-2', className))} {...props}>{children}</h3>;
};

export const CardDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({ className, children, ...props }) => {
  return <p className={twMerge(clsx('text-xs text-slate-400 mt-1', className))} {...props}>{children}</p>;
};
