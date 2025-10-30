/**
 * Constants for BackTester Frontend
 *
 * All magic numbers, API endpoints, error messages, and default values.
 */

// ============================================================================
// API Configuration
// ============================================================================

export const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

export const API_ENDPOINTS = {
  BACKTEST: "/api/backtest",
  HEALTH: "/api/health",
} as const;

// ============================================================================
// Application Limits
// ============================================================================

export const LIMITS = {
  MAX_STOCKS: 10,
  MIN_STOCKS: 1,
  MIN_INVESTMENT: 1000,
  MAX_INVESTMENT: 100_000_000,
  MIN_INVESTMENT_STEP: 100,
} as const;

// ============================================================================
// Error Messages
// ============================================================================

export const ERROR_MESSAGES = {
  // Network errors
  NETWORK_ERROR: "網路連線失敗，請檢查網路設定",
  TIMEOUT_ERROR: "請求逾時，請稍後再試",

  // API errors
  INVALID_STOCK: "找不到股票資料，請確認股票代碼是否正確",
  INSUFFICIENT_DATA: "資料不足，請調整日期範圍（至少需要 6 個月資料）",
  SERVER_ERROR: "伺服器錯誤，請稍後再試",

  // Validation errors
  INVALID_DATE_RANGE: "結束日期必須晚於開始日期",
  INVALID_STOCK_COUNT: `請選擇 ${LIMITS.MIN_STOCKS} 到 ${LIMITS.MAX_STOCKS} 檔股票`,
  INVALID_AMOUNT: `投資金額必須介於 ${LIMITS.MIN_INVESTMENT.toLocaleString()} 到 ${LIMITS.MAX_INVESTMENT.toLocaleString()} 元之間`,
  EMPTY_STOCK_SYMBOL: "股票代碼不能為空",
  INVALID_STOCK_FORMAT: "股票代碼格式錯誤（例如：AAPL 或 2330.TW）",
} as const;

// ============================================================================
// Default Values
// ============================================================================

export const DEFAULT_VALUES = {
  STRATEGY: "lump_sum" as const,
  INVESTMENT_AMOUNT: 10000,
  STOCKS: [""] as string[],

  // Default date range: 2 years ago to 1 year ago (ensure historical data)
  get START_DATE() {
    const date = new Date();
    date.setFullYear(date.getFullYear() - 2);
    return date.toISOString().split("T")[0];
  },

  get END_DATE() {
    const date = new Date();
    date.setFullYear(date.getFullYear() - 1);
    return date.toISOString().split("T")[0];
  },
} as const;

// ============================================================================
// Chart Configuration (Neubrutalism Colors)
// ============================================================================

export const CHART_COLORS = [
  "#FFEB3B", // Neon Yellow
  "#00E5FF", // Bright Cyan
  "#D946EF", // Electric Purple
  "#10B981", // Success Green
  "#F59E0B", // Warning Orange
  "#EC4899", // Hot Pink
  "#EF4444", // Danger Red
  "#14B8A6", // Teal
  "#8B5CF6", // Purple
  "#06B6D4", // Cyan
] as const;

// ============================================================================
// Format Configuration
// ============================================================================

export const FORMAT_CONFIG = {
  PERCENTAGE_DECIMALS: 2,
  CURRENCY_DECIMALS: 0,
  LOCALE: "zh-TW",
  CURRENCY: "TWD",
} as const;

// ============================================================================
// Validation Regex
// ============================================================================

export const VALIDATION_REGEX = {
  // Stock symbol: uppercase letters, numbers, and dots
  STOCK_SYMBOL: /^[A-Z0-9.]+$/,

  // Taiwan stock: 4 digits + .TW or .TWO
  TAIWAN_STOCK: /^\d{4}\.(TW|TWO)$/,

  // US stock: 1-5 uppercase letters
  US_STOCK: /^[A-Z]{1,5}$/,
} as const;
