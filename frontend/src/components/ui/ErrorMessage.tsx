import type { HTMLAttributes } from 'react';
import { clsx } from 'clsx';

interface ErrorMessageProps extends HTMLAttributes<HTMLDivElement> {
  message: string;
}

export function ErrorMessage({ message, className, ...props }: ErrorMessageProps) {
  return (
    <div
      className={clsx(
        'p-4 rounded-lg bg-danger-50 border border-danger-200',
        className
      )}
      role="alert"
      {...props}
    >
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg
            className="w-5 h-5 text-danger-500"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="ml-3">
          <p className="text-sm font-medium text-danger-800">{message}</p>
        </div>
      </div>
    </div>
  );
}
