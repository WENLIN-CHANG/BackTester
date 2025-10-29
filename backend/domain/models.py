"""
Domain Models - Immutable data structures

All models are frozen dataclasses to ensure immutability.
No external dependencies allowed in this layer.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal


@dataclass(frozen=True)
class StockPrice:
    """Single point in time stock price data"""

    date: datetime
    close: float

    def __post_init__(self) -> None:
        """Validate data on initialization"""
        if self.close <= 0:
            raise ValueError(f"Price must be positive, got {self.close}")


@dataclass(frozen=True)
class PortfolioSnapshot:
    """Portfolio state at a specific point in time"""

    date: datetime
    value: float  # Current portfolio value
    shares: float  # Total shares held
    cumulative_invested: float  # Total amount invested so far

    def __post_init__(self) -> None:
        """Validate data on initialization"""
        if self.value < 0:
            raise ValueError(f"Portfolio value cannot be negative, got {self.value}")
        if self.shares < 0:
            raise ValueError(f"Shares cannot be negative, got {self.shares}")
        if self.cumulative_invested < 0:
            raise ValueError(
                f"Cumulative invested cannot be negative, got {self.cumulative_invested}"
            )


@dataclass(frozen=True)
class BacktestResult:
    """Complete backtest result with all metrics"""

    # Basic info
    symbol: str
    name: str
    strategy: Literal["lump_sum", "dca"]

    # Return metrics
    total_return: float  # Total return as percentage (e.g., 0.5 = 50%)
    cagr: float  # Compound Annual Growth Rate

    # Risk metrics
    max_drawdown: float  # Maximum drawdown as negative percentage
    volatility: float  # Annualized volatility
    sharpe_ratio: float  # Risk-adjusted return

    # Portfolio summary
    final_value: float
    total_invested: float

    # Historical data
    history: List[PortfolioSnapshot]

    def __post_init__(self) -> None:
        """Validate data on initialization"""
        # Note: symbol and name can be empty strings (for unnamed backtests)
        if self.strategy not in ("lump_sum", "dca"):
            raise ValueError(f"Invalid strategy: {self.strategy}")
        if self.final_value < 0:
            raise ValueError(f"Final value cannot be negative, got {self.final_value}")
        if self.total_invested <= 0:
            raise ValueError(
                f"Total invested must be positive, got {self.total_invested}"
            )
        if not self.history:
            raise ValueError("History cannot be empty")
        if self.max_drawdown > 0:
            raise ValueError(
                f"Max drawdown must be negative or zero, got {self.max_drawdown}"
            )


@dataclass(frozen=True)
class PerformerInfo:
    """Information about a performer in comparison"""

    symbol: str
    total_return: float

    def __post_init__(self) -> None:
        """Validate data on initialization"""
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")


@dataclass(frozen=True)
class Comparison:
    """Comparison metrics across multiple backtests"""

    # Simple comparisons (symbol only)
    best_return: str  # Symbol with best total return
    best_sharpe: str  # Symbol with best Sharpe ratio
    lowest_risk: str  # Symbol with lowest volatility
    best_cagr: str  # Symbol with best CAGR

    # Detailed comparisons
    best_performer: PerformerInfo  # Best performer with details
    worst_performer: PerformerInfo  # Worst performer with details
    average_return: float  # Average return across all stocks
    total_invested: float  # Total amount invested

    def __post_init__(self) -> None:
        """Validate data on initialization"""
        if not all([self.best_return, self.best_sharpe, self.lowest_risk, self.best_cagr]):
            raise ValueError("All comparison fields must be non-empty")
        if self.total_invested <= 0:
            raise ValueError("Total invested must be positive")
