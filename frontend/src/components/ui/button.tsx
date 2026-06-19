import { cn } from '@/lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'secondary' | 'outline';
}

export function Button({ className, variant = 'default', ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-brand-300/60 disabled:cursor-not-allowed disabled:opacity-50',
        variant === 'default' && 'bg-white text-slate-950 hover:bg-brand-100',
        variant === 'secondary' && 'bg-white/10 text-white hover:bg-white/15',
        variant === 'outline' && 'border border-white/15 bg-transparent text-white hover:bg-white/10',
        className,
      )}
      {...props}
    />
  );
}
