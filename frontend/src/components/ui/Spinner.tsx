import type { HTMLAttributes } from 'react';
import { clsx } from 'clsx';

type SpinnerSize = 'sm' | 'md' | 'lg';

interface SpinnerProps extends HTMLAttributes<HTMLDivElement> {
  size?: SpinnerSize;
}

const sizeStyles: Record<SpinnerSize, string> = {
  sm: 'w-4 h-4 border-2',
  md: 'w-8 h-8 border-3',
  lg: 'w-12 h-12 border-4',
};

export function Spinner({ size = 'md', className, ...props }: SpinnerProps) {
  return (
    <div
      className={clsx('flex items-center justify-center', className)}
      {...props}
    >
      <div
        className={clsx(
          'animate-spin rounded-full border-primary-600 border-t-transparent',
          sizeStyles[size]
        )}
      />
    </div>
  );
}
