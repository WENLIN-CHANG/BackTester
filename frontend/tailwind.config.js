/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Neubrutalism 核心色彩（salary_bee 風格）
        "brutal-yellow": "#fbbf24", // Amber-400，salary_bee 的主黃色
        "brutal-blue": "#2563eb", // Blue-600，salary_bee 的次要色
        "bright-cyan": "#00E5FF",
        "electric-purple": "#D946EF",
        "brutal-black": "#000000",
        "brutal-white": "#FFFFFF",
        "brutal-gray": "#F5F5F5",

        // 保留原有語義化顏色（更新為 salary_bee 版本）
        primary: {
          50: "#fffbeb",
          100: "#fef3c7",
          500: "#fbbf24", // Amber-400，salary_bee 的黃色
          600: "#f59e0b", // Amber-500
          700: "#d97706", // Amber-600
        },
        success: {
          50: "#f0fdf4",
          500: "#10B981", // 保持原有的綠色
          700: "#047857",
        },
        danger: {
          50: "#fef2f2",
          500: "#EF4444", // 保持原有的紅色
          700: "#DC2626",
        },
        warning: {
          500: "#F59E0B",
        },
      },
      boxShadow: {
        // Neubrutalism 粗黑陰影系統（salary_bee 風格，更大）
        "brutal-sm": "2px 2px 0px #000000",
        "brutal-md": "4px 4px 0px #000000",
        "brutal-lg": "8px 8px 0px #000000",
        "brutal-xl": "12px 12px 0px #000000",

        // 互動效果陰影
        "brutal-hover": "6px 6px 0px #000000",
        "brutal-active": "2px 2px 0px #000000",

        // 彩色陰影（用於特殊情況）
        "brutal-danger": "8px 8px 0px #EF4444",
        "brutal-success": "8px 8px 0px #10B981",
      },
      borderWidth: {
        3: "3px",
        4: "4px", // salary_bee 使用 4px
        5: "5px",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["Roboto Mono", "Courier New", "monospace"],
      },
      animation: {
        "spin-reverse": "spin 1s linear infinite reverse",
      },
    },
  },
  plugins: [],
};
