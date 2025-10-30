import { forwardRef } from "react";
import type { InputHTMLAttributes } from "react";
import { clsx } from "clsx";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-base font-bold uppercase tracking-wide text-brutal-black mb-2">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={clsx(
            // 使用 brutalist-input CSS 類別
            "brutalist-input w-full px-5 py-4",
            // 錯誤狀態覆蓋
            error && "border-danger-500 focus:border-danger-500",
            className,
          )}
          {...props}
        />
        {error && (
          <p className="mt-2 text-xs font-semibold text-danger-500 uppercase">
            {error}
          </p>
        )}
      </div>
    );
  },
);

Input.displayName = "Input";
