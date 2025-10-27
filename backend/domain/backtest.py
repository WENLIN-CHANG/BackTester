"""
Backtest logic - Pure functions only

All backtest functions are pure:
- Same input always produces same output
- No side effects (no API calls, no file I/O)
- Easy to test and reason about
"""

from typing import List
from domain.models import StockPrice, PortfolioSnapshot, BacktestResult
from domain.calculations import (
    calculate_cagr,
    calculate_max_drawdown,
    calculate_volatility,
    calculate_sharpe_ratio,
)


def backtest_lump_sum(
    prices: List[StockPrice],
    initial_amount: float,
    symbol: str = "",
    name: str = "",
) -> BacktestResult:
    """
    Backtest lump sum investment strategy

    Strategy: Invest all money at once on day 1, then hold.

    Args:
        prices: List of historical stock prices
        initial_amount: Amount to invest on day 1
        symbol: Stock symbol (optional)
        name: Stock name (optional)

    Returns:
        BacktestResult with all metrics calculated

    Raises:
        ValueError: If prices is empty or initial_amount <= 0
    """
    # Validate inputs
    if not prices:
        raise ValueError("Prices list cannot be empty")
    if initial_amount <= 0:
        raise ValueError(f"Initial amount must be positive, got {initial_amount}")

    # Buy all shares on day 1
    first_price = prices[0].close
    shares = initial_amount / first_price

    # Build portfolio history
    history: List[PortfolioSnapshot] = []
    for price in prices:
        snapshot = PortfolioSnapshot(
            date=price.date,
            value=shares * price.close,
            shares=shares,
            cumulative_invested=initial_amount,
        )
        history.append(snapshot)

    # Calculate metrics
    final_value = history[-1].value
    total_return = (final_value - initial_amount) / initial_amount

    # Calculate CAGR
    years = (prices[-1].date - prices[0].date).days / 365.25
    if years <= 0:
        years = 1.0 / 252  # Minimum 1 trading day
    cagr = calculate_cagr(initial_amount, final_value, years)

    # Calculate max drawdown
    values = [snapshot.value for snapshot in history]
    max_dd = calculate_max_drawdown(values)

    # Calculate daily returns for volatility and Sharpe
    returns: List[float] = []
    for i in range(1, len(values)):
        if values[i - 1] > 0:
            daily_return = (values[i] - values[i - 1]) / values[i - 1]
            returns.append(daily_return)

    # Handle edge case: only 1 data point
    if not returns:
        volatility = 0.0
        sharpe_ratio = 0.0
    else:
        volatility = calculate_volatility(returns)
        sharpe_ratio = calculate_sharpe_ratio(returns)

    return BacktestResult(
        symbol=symbol,
        name=name,
        strategy="lump_sum",
        total_return=total_return,
        cagr=cagr,
        max_drawdown=max_dd,
        volatility=volatility,
        sharpe_ratio=sharpe_ratio,
        final_value=final_value,
        total_invested=initial_amount,
        history=history,
    )


def backtest_dca(
    prices: List[StockPrice],
    monthly_amount: float,
    symbol: str = "",
    name: str = "",
) -> BacktestResult:
    """
    Backtest dollar-cost averaging (DCA) strategy

    Strategy: Invest a fixed amount every month on the first trading day.

    Args:
        prices: List of historical stock prices
        monthly_amount: Amount to invest each month
        symbol: Stock symbol (optional)
        name: Stock name (optional)

    Returns:
        BacktestResult with all metrics calculated

    Raises:
        ValueError: If prices is empty or monthly_amount <= 0
    """
    # Validate inputs
    if not prices:
        raise ValueError("Prices list cannot be empty")
    if monthly_amount <= 0:
        raise ValueError(f"Monthly amount must be positive, got {monthly_amount}")

    # Track investment state
    total_shares = 0.0
    total_invested = 0.0
    last_month = None

    # Build portfolio history
    history: List[PortfolioSnapshot] = []

    for price in prices:
        current_month = (price.date.year, price.date.month)

        # Invest on first trading day of each month
        if current_month != last_month:
            # Buy shares
            shares_bought = monthly_amount / price.close
            total_shares += shares_bought
            total_invested += monthly_amount
            last_month = current_month

        # Record snapshot
        snapshot = PortfolioSnapshot(
            date=price.date,
            value=total_shares * price.close,
            shares=total_shares,
            cumulative_invested=total_invested,
        )
        history.append(snapshot)

    # Calculate metrics
    final_value = history[-1].value
    total_return = (final_value - total_invested) / total_invested

    # Calculate CAGR
    years = (prices[-1].date - prices[0].date).days / 365.25
    if years <= 0:
        years = 1.0 / 252  # Minimum 1 trading day
    cagr = calculate_cagr(total_invested, final_value, years)

    # Calculate max drawdown
    values = [snapshot.value for snapshot in history]
    max_dd = calculate_max_drawdown(values)

    # Calculate daily returns for volatility and Sharpe
    returns: List[float] = []
    for i in range(1, len(values)):
        if values[i - 1] > 0:
            daily_return = (values[i] - values[i - 1]) / values[i - 1]
            returns.append(daily_return)

    # Handle edge case: only 1 data point
    if not returns:
        volatility = 0.0
        sharpe_ratio = 0.0
    else:
        volatility = calculate_volatility(returns)
        sharpe_ratio = calculate_sharpe_ratio(returns)

    return BacktestResult(
        symbol=symbol,
        name=name,
        strategy="dca",
        total_return=total_return,
        cagr=cagr,
        max_drawdown=max_dd,
        volatility=volatility,
        sharpe_ratio=sharpe_ratio,
        final_value=final_value,
        total_invested=total_invested,
        history=history,
    )
