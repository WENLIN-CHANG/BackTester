/**
 * Type Definitions for BackTester Frontend
 *
 * All TypeScript types used across the application.
 * These should match the backend API schemas.
 */

// ============================================================================
// Enums & Literals
// ============================================================================

export type Strategy = 'lump_sum' | 'dca';

// ============================================================================
// Request Types
// ============================================================================

export interface InvestmentParams {
  amount: number;
}

export interface BacktestRequest {
  stocks: string[];
  start_date: string;  // YYYY-MM-DD
  end_date: string;    // YYYY-MM-DD
  strategy: Strategy;
  investment: InvestmentParams;
}

// ============================================================================
// Response Types
// ============================================================================

export interface PortfolioSnapshot {
  date: string;
  value: number;
  shares: number;
  cumulative_invested: number;
}

export interface BacktestResult {
  symbol: string;
  name: string;
  strategy: Strategy;

  // Return metrics
  total_return: number;      // e.g., 0.25 = 25%
  cagr: number;             // Compound Annual Growth Rate

  // Risk metrics
  max_drawdown: number;     // e.g., -0.15 = -15%
  volatility: number;       // Annualized volatility
  sharpe_ratio: number;     // Risk-adjusted return

  // Portfolio summary
  final_value: number;
  total_invested: number;

  // Historical data
  history: PortfolioSnapshot[];
}

export interface ComparisonResult {
  best_return: string;      // Symbol with best total return
  best_sharpe: string;      // Symbol with best Sharpe ratio
  lowest_risk: string;      // Symbol with lowest volatility
  best_cagr: string;        // Symbol with best CAGR
}

export interface BacktestResponse {
  results: BacktestResult[];
  comparison: ComparisonResult;
}

// ============================================================================
// Error Types
// ============================================================================

export interface ApiError {
  detail: string;
}

// ============================================================================
// Form Types
// ============================================================================

export interface BacktestFormData {
  stocks: string[];
  start_date: string;
  end_date: string;
  strategy: Strategy;
  amount: number;
}

// ============================================================================
// UI State Types
// ============================================================================

export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
  retry?: () => void;
}
