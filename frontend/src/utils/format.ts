import { format as formatDate } from 'date-fns';
import { FORMAT_CONFIG } from '@/constants';

// Percentage
export function formatPercent(value: number, decimals: number = FORMAT_CONFIG.PERCENTAGE_DECIMALS): string {
  const sign = value > 0 ? '+' : '';
  const percentage = (value * 100).toFixed(decimals);
  return `${sign}${percentage}%`;
}

export function formatPercentNoSign(value: number, decimals: number = FORMAT_CONFIG.PERCENTAGE_DECIMALS): string {
  const percentage = (value * 100).toFixed(decimals);
  return `${percentage}%`;
}

// Currency
export function formatCurrency(
  value: number,
  currency: string = FORMAT_CONFIG.CURRENCY,
  locale: string = FORMAT_CONFIG.LOCALE
): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: FORMAT_CONFIG.CURRENCY_DECIMALS,
    maximumFractionDigits: FORMAT_CONFIG.CURRENCY_DECIMALS,
  }).format(value);
}

export function formatNumber(value: number, decimals: number = 0): string {
  return new Intl.NumberFormat(FORMAT_CONFIG.LOCALE, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

// Date
export function formatDateString(date: string | Date, formatStr: string = 'yyyy/MM/dd'): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return formatDate(dateObj, formatStr);
}

export function formatDateChinese(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return formatDate(dateObj, 'yyyy年M月d日');
}

// Metrics
export function formatSharpeRatio(value: number): string {
  return value.toFixed(2);
}

export function formatVolatility(value: number): string {
  return formatPercentNoSign(value);
}

// Compact
export function formatCompact(value: number): string {
  return new Intl.NumberFormat(FORMAT_CONFIG.LOCALE, {
    notation: 'compact',
    compactDisplay: 'short',
    maximumFractionDigits: 1,
  }).format(value);
}
