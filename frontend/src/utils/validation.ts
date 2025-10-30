import { LIMITS, VALIDATION_REGEX } from "@/constants";

// Stock Symbol
export function isValidStockSymbol(symbol: string): boolean {
  if (!symbol || symbol.trim().length === 0) {
    return false;
  }
  return VALIDATION_REGEX.STOCK_SYMBOL.test(symbol.trim());
}

export function isTaiwanStock(symbol: string): boolean {
  return VALIDATION_REGEX.TAIWAN_STOCK.test(symbol.trim());
}

export function isUSStock(symbol: string): boolean {
  return VALIDATION_REGEX.US_STOCK.test(symbol.trim());
}

export function normalizeStockSymbol(symbol: string): string {
  return symbol.trim().toUpperCase();
}

// Date
export function isValidDateString(dateStr: string): boolean {
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
  if (!dateRegex.test(dateStr)) {
    return false;
  }
  const date = new Date(dateStr);
  return !isNaN(date.getTime());
}

export function isValidDateRange(startDate: string, endDate: string): boolean {
  if (!isValidDateString(startDate) || !isValidDateString(endDate)) {
    return false;
  }
  const start = new Date(startDate);
  const end = new Date(endDate);
  return end > start;
}

export function isNotFutureDate(dateStr: string): boolean {
  if (!isValidDateString(dateStr)) {
    return false;
  }
  const date = new Date(dateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return date <= today;
}

// Amount
export function isValidAmount(amount: number): boolean {
  return (
    !isNaN(amount) &&
    isFinite(amount) &&
    amount >= LIMITS.MIN_INVESTMENT &&
    amount <= LIMITS.MAX_INVESTMENT
  );
}

export function isValidAmountStep(amount: number): boolean {
  return amount % LIMITS.MIN_INVESTMENT_STEP === 0;
}

// Stock List
export function isValidStockList(stocks: string[]): boolean {
  if (!Array.isArray(stocks)) {
    return false;
  }
  if (stocks.length < LIMITS.MIN_STOCKS || stocks.length > LIMITS.MAX_STOCKS) {
    return false;
  }
  return stocks.every((stock) => isValidStockSymbol(stock));
}

export function removeDuplicateStocks(stocks: string[]): string[] {
  return [...new Set(stocks.map(normalizeStockSymbol))];
}

// Error Messages
export function getStockSymbolError(symbol: string): string {
  if (!symbol || symbol.trim().length === 0) {
    return "股票代碼不能為空";
  }
  if (!isValidStockSymbol(symbol)) {
    return "股票代碼格式錯誤（例如：AAPL 或 2330.TW）";
  }
  return "";
}

export function getDateRangeError(startDate: string, endDate: string): string {
  if (!isValidDateString(startDate)) {
    return "開始日期格式錯誤";
  }
  if (!isValidDateString(endDate)) {
    return "結束日期格式錯誤";
  }
  if (!isValidDateRange(startDate, endDate)) {
    return "結束日期必須晚於開始日期";
  }
  if (!isNotFutureDate(endDate)) {
    return "結束日期不能是未來";
  }
  return "";
}

export function getAmountError(amount: number): string {
  if (isNaN(amount) || !isFinite(amount)) {
    return "請輸入有效的金額";
  }
  if (amount < LIMITS.MIN_INVESTMENT) {
    return `投資金額最少為 ${LIMITS.MIN_INVESTMENT.toLocaleString()} 元`;
  }
  if (amount > LIMITS.MAX_INVESTMENT) {
    return `投資金額最多為 ${LIMITS.MAX_INVESTMENT.toLocaleString()} 元`;
  }
  if (!isValidAmountStep(amount)) {
    return `投資金額必須是 ${LIMITS.MIN_INVESTMENT_STEP} 的倍數`;
  }
  return "";
}
