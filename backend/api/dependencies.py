"""
API Dependencies - Dependency injection for FastAPI

Provides instances of services and adapters.
"""

from application.backtest_service import BacktestService
from infrastructure.yfinance_adapter import YFinanceAdapter


def get_yfinance_adapter() -> YFinanceAdapter:
    """Get YFinance adapter instance"""
    return YFinanceAdapter()


def get_backtest_service() -> BacktestService:
    """Get backtest service instance with injected adapter"""
    adapter = get_yfinance_adapter()
    return BacktestService(data_adapter=adapter)
