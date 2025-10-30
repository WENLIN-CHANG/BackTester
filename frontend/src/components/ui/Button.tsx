import { forwardRef } from "react";
import type { ButtonHTMLAttributes } from "react";
import { clsx } from "clsx";

type ButtonVariant = "primary" | "secondary" | "danger";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
}

const variantStyles: Record<ButtonVariant, string> = {
  primary: "brutalist-button-primary",
  secondary: "brutalist-button-secondary",
  danger: "brutalist-button-secondary bg-danger-500 hover:bg-danger-700",
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "px-6 py-3 text-base",
  md: "px-8 py-4 text-lg",
  lg: "px-10 py-5 text-2xl",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = "primary",
      size = "md",
      loading = false,
      disabled,
      className,
      children,
      ...props
    },
    ref,
  ) => {
    const isDisabled = disabled || loading;

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        className={clsx(
          // 使用 brutalist-button CSS 類別（已包含所有樣式）
          "uppercase tracking-wide rounded-none",
          "focus:outline-none focus:ring-2 focus:ring-brutal-black focus:ring-offset-2",
          variantStyles[variant],
          sizeStyles[size],
          className,
        )}
        {...props}
      >
        {loading ? (
          <span className="inline-flex items-center gap-2">
            <span className="inline-block w-4 h-4 border-4 border-brutal-black border-t-transparent animate-spin" />
            載入中
          </span>
        ) : (
          children
        )}
      </button>
    );
  },
);

Button.displayName = "Button";
