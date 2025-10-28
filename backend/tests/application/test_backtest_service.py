"""
Application Layer Tests - BacktestService

Tests the service layer that coordinates domain and infrastructure.
Uses mocks to avoid real API calls.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from application.backtest_service import BacktestService
from infrastructure.yfinance_adapter import StockDataError
from domain.models import StockPrice, BacktestResult, PortfolioSnapshot


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_adapter():
    """Mock YFinanceAdapter"""
    return Mock()


@pytest.fixture
def service(mock_adapter):
    """BacktestService with mocked adapter"""
    return BacktestService(mock_adapter)


@pytest.fixture
def sample_prices():
    """Sample price data for testing"""
    return [
        StockPrice(date=datetime(2024, 1, i), close=100.0 + i)
        for i in range(1, 31)
    ]


@pytest.fixture
def start_date():
    return datetime(2024, 1, 1)


@pytest.fixture
def end_date():
    return datetime(2024, 1, 31)


# ============================================================================
# Tests: run_backtest()
# ============================================================================


class TestRunBacktest:
    """Tests for run_backtest() method"""

    def test_lump_sum_success(
        self, service, mock_adapter, sample_prices, start_date, end_date
    ):
        """Should successfully run lump sum backtest"""
        # Given
        mock_adapter.get_stock_data.return_value = (sample_prices, "Test Stock")

        # When
        result = service.run_backtest(
            symbol="TEST",
            start_date=start_date,
            end_date=end_date,
            strategy="lump_sum",
            amount=10000.0,
        )

        # Then
        assert isinstance(result, BacktestResult)
        assert result.symbol == "TEST"
        assert result.name == "Test Stock"
        assert result.strategy == "lump_sum"
        assert result.total_invested == 10000.0
        assert result.final_value > 0
        mock_adapter.get_stock_data.assert_called_once_with("TEST", start_date, end_date)

    def test_dca_success(
        self, service, mock_adapter, sample_prices, start_date, end_date
    ):
        """Should successfully run DCA backtest"""
        # Given
        mock_adapter.get_stock_data.return_value = (sample_prices, "Test Stock")

        # When
        result = service.run_backtest(
            symbol="TEST",
            start_date=start_date,
            end_date=end_date,
            strategy="dca",
            amount=1000.0,
        )

        # Then
        assert isinstance(result, BacktestResult)
        assert result.strategy == "dca"
        assert result.total_invested >= 1000.0  # At least one month invested

    def test_calls_adapter_with_correct_params(
        self, service, mock_adapter, sample_prices, start_date, end_date
    ):
        """Should call adapter with correct parameters"""
        # Given
        mock_adapter.get_stock_data.return_value = (sample_prices, "Test Stock")

        # When
        service.run_backtest(
            symbol="AAPL",
            start_date=start_date,
            end_date=end_date,
            strategy="lump_sum",
            amount=10000.0,
        )

        # Then
        mock_adapter.get_stock_data.assert_called_once_with("AAPL", start_date, end_date)

    def test_raises_on_stock_data_error(
        self, service, mock_adapter, start_date, end_date
    ):
        """Should propagate StockDataError from adapter"""
        # Given
        mock_adapter.get_stock_data.side_effect = StockDataError("Stock not found")

        # When/Then
        with pytest.raises(StockDataError, match="Stock not found"):
            service.run_backtest(
                symbol="INVALID",
                start_date=start_date,
                end_date=end_date,
                strategy="lump_sum",
                amount=10000.0,
            )

    def test_raises_on_invalid_strategy(
        self, service, mock_adapter, sample_prices, start_date, end_date
    ):
        """Should raise ValueError for invalid strategy"""
        # Given
        mock_adapter.get_stock_data.return_value = (sample_prices, "Test Stock")

        # When/Then
        with pytest.raises(ValueError, match="Invalid strategy"):
            service.run_backtest(
                symbol="TEST",
                start_date=start_date,
                end_date=end_date,
                strategy="invalid_strategy",  # type: ignore
                amount=10000.0,
            )


# ============================================================================
# Tests: run_multiple_backtests()
# ============================================================================


class TestRunMultipleBacktests:
    """Tests for run_multiple_backtests() method"""

    def test_success_with_multiple_symbols(
        self, service, mock_adapter, sample_prices, start_date, end_date
    ):
        """Should successfully run backtests for multiple symbols"""
        # Given
        mock_adapter.get_stock_data.side_effect = [
            (sample_prices, "Stock A"),
            ([StockPrice(date=datetime(2024, 1, i), close=200.0 + i) for i in range(1, 31)], "Stock B"),
        ]

        # When
        results, comparison = service.run_multiple_backtests(
            symbols=["AAPL", "GOOGL"],
            start_date=start_date,
            end_date=end_date,
            strategy="lump_sum",
            amount=10000.0,
        )

        # Then
        assert len(results) == 2
        assert results[0].symbol == "AAPL"
        assert results[0].name == "Stock A"
        assert results[1].symbol == "GOOGL"
        assert results[1].name == "Stock B"
        assert comparison.best_return in ["AAPL", "GOOGL"]
        assert comparison.best_sharpe in ["AAPL", "GOOGL"]
        assert mock_adapter.get_stock_data.call_count == 2

    def test_handles_partial_failures(
        self, service, mock_adapter, sample_prices, start_date, end_date
    ):
        """Should continue with other symbols when one fails"""
        # Given
        mock_adapter.get_stock_data.side_effect = [
            (sample_prices, "Stock A"),
            StockDataError("Stock not found"),  # Second symbol fails
            ([StockPrice(date=datetime(2024, 1, i), close=300.0) for i in range(1, 31)], "Stock C"),
        ]

        # When
        results, comparison = service.run_multiple_backtests(
            symbols=["AAPL", "INVALID", "MSFT"],
            start_date=start_date,
            end_date=end_date,
            strategy="lump_sum",
            amount=10000.0,
        )

        # Then
        assert len(results) == 2  # Only successful ones
        assert results[0].symbol == "AAPL"
        assert results[1].symbol == "MSFT"
        assert comparison.best_return in ["AAPL", "MSFT"]

    def test_raises_when_all_symbols_fail(
        self, service, mock_adapter, start_date, end_date
    ):
        """Should raise ValueError when all symbols fail"""
        # Given
        mock_adapter.get_stock_data.side_effect = [
            StockDataError("Stock 1 not found"),
            StockDataError("Stock 2 not found"),
        ]

        # When/Then
        with pytest.raises(ValueError, match="All symbols failed"):
            service.run_multiple_backtests(
                symbols=["INVALID1", "INVALID2"],
                start_date=start_date,
                end_date=end_date,
                strategy="lump_sum",
                amount=10000.0,
            )

    def test_raises_on_empty_symbols_list(
        self, service, start_date, end_date
    ):
        """Should raise ValueError when no symbols provided"""
        # When/Then
        with pytest.raises(ValueError, match="At least one symbol is required"):
            service.run_multiple_backtests(
                symbols=[],
                start_date=start_date,
                end_date=end_date,
                strategy="lump_sum",
                amount=10000.0,
            )

    def test_handles_unexpected_errors(
        self, service, mock_adapter, sample_prices, start_date, end_date
    ):
        """Should handle unexpected errors and continue with other symbols"""
        # Given
        mock_adapter.get_stock_data.side_effect = [
            (sample_prices, "Stock A"),
            Exception("Unexpected error"),  # Unexpected failure
            ([StockPrice(date=datetime(2024, 1, i), close=300.0) for i in range(1, 31)], "Stock C"),
        ]

        # When
        results, comparison = service.run_multiple_backtests(
            symbols=["AAPL", "PROBLEM", "MSFT"],
            start_date=start_date,
            end_date=end_date,
            strategy="lump_sum",
            amount=10000.0,
        )

        # Then
        assert len(results) == 2  # Only successful ones
        assert results[0].symbol == "AAPL"
        assert results[1].symbol == "MSFT"

    def test_single_symbol_success(
        self, service, mock_adapter, sample_prices, start_date, end_date
    ):
        """Should work with single symbol"""
        # Given
        mock_adapter.get_stock_data.return_value = (sample_prices, "Test Stock")

        # When
        results, comparison = service.run_multiple_backtests(
            symbols=["TEST"],
            start_date=start_date,
            end_date=end_date,
            strategy="lump_sum",
            amount=10000.0,
        )

        # Then
        assert len(results) == 1
        assert results[0].symbol == "TEST"
        # Comparison should have all fields point to the same symbol
        assert comparison.best_return == "TEST"
        assert comparison.best_sharpe == "TEST"
        assert comparison.lowest_risk == "TEST"
        assert comparison.best_cagr == "TEST"

    def test_dca_strategy(
        self, service, mock_adapter, start_date, end_date
    ):
        """Should work with DCA strategy"""
        # Given
        # Create 90 days of data (3 months)
        prices = [
            StockPrice(date=datetime(2024, 1, 1) + __import__('datetime').timedelta(days=i), close=100.0 + i)
            for i in range(90)
        ]
        mock_adapter.get_stock_data.return_value = (prices, "Test Stock")

        # When
        results, comparison = service.run_multiple_backtests(
            symbols=["TEST"],
            start_date=start_date,
            end_date=datetime(2024, 3, 31),
            strategy="dca",
            amount=1000.0,
        )

        # Then
        assert len(results) == 1
        assert results[0].strategy == "dca"
        assert results[0].total_invested >= 3000.0  # 3 months * 1000
