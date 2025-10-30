import { forwardRef } from "react";
import type { HTMLAttributes } from "react";
import { clsx } from "clsx";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ title, className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={clsx(
          // Brutalist Card with Tilt
          "brutalist-card brutalist-tilt-1",
          className,
        )}
        {...props}
      >
        {title && (
          <div className="px-8 py-5 border-b-4 border-brutal-black bg-brutal-gray">
            <h3 className="text-2xl font-black uppercase tracking-wide text-brutal-black">
              {title}
            </h3>
          </div>
        )}
        <div className="p-8">{children}</div>
      </div>
    );
  },
);

Card.displayName = "Card";
