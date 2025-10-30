"""
Backtest Service - Application layer

Orchestrates domain logic and infrastructure:
- Uses infrastructure to fetch data (side effects)
- Uses domain layer to perform calculations (pure functions)
- Handles errors and coordinates multiple operations
"""

from datetime import datetime
from typing import Literal

from domain import backtest as backtest_logic
from domain.calculations import calculate_comparison
from domain.models import BacktestResult, Comparison
from infrastructure.yfinance_adapter import StockDataError, YFinanceAdapter


class BacktestService:
    """
    Service for running backtests

    This class coordinates between infrastructure (data fetching)
    and domain (business logic).
    """

    def __init__(self, data_adapter: YFinanceAdapter):
        """
        Initialize service with data adapter

        Args:
            data_adapter: Adapter for fetching stock data
        """
        self.data_adapter = data_adapter

    def run_backtest(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        strategy: Literal["lump_sum", "dca"],
        amount: float,
    ) -> BacktestResult:
        """
        Run backtest for a single stock

        Args:
            symbol: Stock ticker symbol
            start_date: Backtest start date
            end_date: Backtest end date
            strategy: Investment strategy ("lump_sum" or "dca")
            amount: Investment amount (initial for lump_sum, monthly for dca)

        Returns:
            BacktestResult with all metrics

        Raises:
            StockDataError: If stock data cannot be fetched
            ValueError: If parameters are invalid
        """
        # Fetch data (side effect - infrastructure layer)
        prices, stock_name = self.data_adapter.get_stock_data(symbol, start_date, end_date)

        # Run backtest (pure function - domain layer)
        if strategy == "lump_sum":
            result = backtest_logic.backtest_lump_sum(
                prices=prices,
                initial_amount=amount,
                symbol=symbol,
                name=stock_name,
            )
        elif strategy == "dca":
            result = backtest_logic.backtest_dca(
                prices=prices,
                monthly_amount=amount,
                symbol=symbol,
                name=stock_name,
            )
        else:
            raise ValueError(f"Invalid strategy: {strategy}")

        return result

    def run_multiple_backtests(
        self,
        symbols: list[str],
        start_date: datetime,
        end_date: datetime,
        strategy: Literal["lump_sum", "dca"],
        amount: float,
    ) -> tuple[list[BacktestResult], Comparison]:
        """
        Run backtests for multiple stocks and compare results

        Args:
            symbols: List of stock ticker symbols
            start_date: Backtest start date
            end_date: Backtest end date
            strategy: Investment strategy
            amount: Investment amount

        Returns:
            Tuple of (results, comparison):
            - results: List of BacktestResult (one per successful symbol)
            - comparison: Comparison of all results

        Raises:
            ValueError: If no symbols provided or all symbols fail
        """
        if not symbols:
            raise ValueError("At least one symbol is required")

        results: list[BacktestResult] = []
        errors: list[tuple[str, str]] = []

        # Run backtest for each symbol
        for symbol in symbols:
            try:
                result = self.run_backtest(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    strategy=strategy,
                    amount=amount,
                )
                results.append(result)
            except StockDataError as e:
                # Collect error but continue with other symbols
                errors.append((symbol, str(e)))
                continue
            except Exception as e:
                # Unexpected errors
                errors.append((symbol, f"Unexpected error: {e!s}"))
                continue

        # Check if we have any successful results
        if not results:
            error_details = "; ".join([f"{sym}: {err}" for sym, err in errors])
            raise ValueError(f"All symbols failed: {error_details}")

        # Calculate comparison (pure function - domain layer)
        comparison = calculate_comparison(results)

        return results, comparison
