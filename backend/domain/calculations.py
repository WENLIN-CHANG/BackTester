"""
Financial calculations - Pure functions only

All functions in this module are pure:
- Same input always produces same output
- No side effects
- No external state dependencies

This makes them easy to test and reason about.
"""

from typing import List
from domain.models import BacktestResult, Comparison, PerformerInfo


def calculate_cagr(initial: float, final: float, years: float) -> float:
    """
    Calculate Compound Annual Growth Rate (CAGR)

    Formula: (final / initial) ^ (1 / years) - 1

    Args:
        initial: Initial investment value
        final: Final investment value
        years: Investment period in years

    Returns:
        CAGR as decimal (e.g., 0.15 = 15%)

    Raises:
        ValueError: If initial <= 0 or years <= 0
    """
    if initial <= 0:
        raise ValueError(f"Initial value must be positive, got {initial}")
    if years <= 0:
        raise ValueError(f"Years must be positive, got {years}")

    # Handle complete loss
    if final == 0:
        return -1.0

    return (final / initial) ** (1 / years) - 1


def calculate_max_drawdown(values: List[float]) -> float:
    """
    Calculate maximum drawdown (peak to trough decline)

    Args:
        values: List of portfolio values over time

    Returns:
        Maximum drawdown as negative decimal (e.g., -0.2 = -20%)
        Returns 0 if no drawdown occurred

    Raises:
        ValueError: If values list is empty
    """
    if not values:
        raise ValueError("Values list cannot be empty")

    if len(values) == 1:
        return 0.0

    peak = values[0]
    max_dd = 0.0

    for value in values:
        # Update peak if we reach a new high
        if value > peak:
            peak = value

        # Calculate drawdown from peak
        if peak > 0:  # Avoid division by zero
            drawdown = (value - peak) / peak
            max_dd = min(max_dd, drawdown)

    return max_dd


def calculate_volatility(returns: List[float]) -> float:
    """
    Calculate annualized volatility (standard deviation of returns)

    Args:
        returns: List of daily returns as decimals

    Returns:
        Annualized volatility (standard deviation * sqrt(252))

    Raises:
        ValueError: If returns list is empty
    """
    if not returns:
        raise ValueError("Returns list cannot be empty")

    if len(returns) == 1:
        return 0.0

    # Calculate mean
    mean = sum(returns) / len(returns)

    # Calculate variance
    squared_diffs = [(r - mean) ** 2 for r in returns]
    variance = sum(squared_diffs) / (len(returns) - 1)  # Sample variance

    # Standard deviation
    std_dev = variance**0.5

    # Annualize (252 trading days per year)
    annualized_volatility = std_dev * (252**0.5)

    return annualized_volatility


def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe Ratio (risk-adjusted return)

    Formula: (annual_return - risk_free_rate) / volatility

    Args:
        returns: List of daily returns as decimals
        risk_free_rate: Annual risk-free rate (default: 2%)

    Returns:
        Sharpe ratio (higher is better)
        Returns 0 if volatility is 0

    Raises:
        ValueError: If returns list is empty
    """
    if not returns:
        raise ValueError("Returns list cannot be empty")

    # Calculate annualized return
    mean_daily_return = sum(returns) / len(returns)
    annual_return = mean_daily_return * 252

    # Calculate volatility
    volatility = calculate_volatility(returns)

    # Avoid division by zero
    if volatility == 0:
        return 0.0

    return (annual_return - risk_free_rate) / volatility


def calculate_comparison(results: List[BacktestResult]) -> Comparison:
    """
    Compare multiple backtest results to find best performers

    Args:
        results: List of backtest results to compare

    Returns:
        Comparison object with best performers in each category

    Raises:
        ValueError: If results list is empty
    """
    if not results:
        raise ValueError("Results list cannot be empty")

    # Find best in each category
    best_return = max(results, key=lambda r: r.total_return)
    best_sharpe = max(results, key=lambda r: r.sharpe_ratio)
    lowest_risk = min(results, key=lambda r: r.volatility)
    best_cagr = max(results, key=lambda r: r.cagr)

    # Find overall best and worst performers (by total return)
    best_performer_result = max(results, key=lambda r: r.total_return)
    worst_performer_result = min(results, key=lambda r: r.total_return)

    # Calculate average return
    average_return = sum(r.total_return for r in results) / len(results)

    # Calculate total invested (sum of all investments)
    total_invested = sum(r.total_invested for r in results)

    return Comparison(
        best_return=best_return.symbol,
        best_sharpe=best_sharpe.symbol,
        lowest_risk=lowest_risk.symbol,
        best_cagr=best_cagr.symbol,
        best_performer=PerformerInfo(
            symbol=best_performer_result.symbol,
            total_return=best_performer_result.total_return,
        ),
        worst_performer=PerformerInfo(
            symbol=worst_performer_result.symbol,
            total_return=worst_performer_result.total_return,
        ),
        average_return=average_return,
        total_invested=total_invested,
    )
