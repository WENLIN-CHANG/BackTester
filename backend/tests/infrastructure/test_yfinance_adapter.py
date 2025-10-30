"""
Tests for infrastructure/yfinance_adapter.py

These are integration tests that make real API calls to Yahoo Finance.
Mark with @pytest.mark.integration to allow selective execution.
"""

from datetime import datetime, timedelta

import pytest

from domain.models import StockPrice
from infrastructure.yfinance_adapter import StockDataError, YFinanceAdapter


@pytest.mark.integration
class TestYFinanceAdapter:
    """Integration tests for Yahoo Finance adapter"""

    @pytest.fixture
    def adapter(self) -> YFinanceAdapter:
        """Create adapter instance"""
        return YFinanceAdapter()

    @pytest.fixture
    def recent_date_range(self) -> tuple[datetime, datetime]:
        """Get recent date range for testing - use fixed historical dates to avoid rate limits"""
        # Use fixed date range (2024-01-01 to 2024-06-30)
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 6, 30)
        return start_date, end_date

    def test_fetches_valid_stock_data(
        self, adapter: YFinanceAdapter, recent_date_range: tuple[datetime, datetime]
    ) -> None:
        # Given
        symbol = "AAPL"
        start_date, end_date = recent_date_range

        # When
        prices, stock_name = adapter.get_stock_data(symbol, start_date, end_date)

        # Then
        assert len(prices) > 100  # Should have many trading days
        assert all(isinstance(p, StockPrice) for p in prices)
        assert all(p.close > 0 for p in prices)
        assert stock_name  # Should have a name
        assert "Apple" in stock_name or stock_name == "AAPL"

    def test_prices_are_chronological(
        self, adapter: YFinanceAdapter, recent_date_range: tuple[datetime, datetime]
    ) -> None:
        # Given
        symbol = "MSFT"
        start_date, end_date = recent_date_range

        # When
        prices, _ = adapter.get_stock_data(symbol, start_date, end_date)

        # Then: Dates should be in order
        dates = [p.date for p in prices]
        assert dates == sorted(dates)

    def test_handles_taiwan_stock(self, adapter: YFinanceAdapter) -> None:
        # Given: Taiwan stock (requires .TW suffix)
        symbol = "2330.TW"  # TSMC
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)

        # When
        prices, stock_name = adapter.get_stock_data(symbol, start_date, end_date)

        # Then
        assert len(prices) > 50
        assert all(p.close > 0 for p in prices)
        assert stock_name  # Should have name

    def test_raises_on_invalid_symbol(
        self, adapter: YFinanceAdapter, recent_date_range: tuple[datetime, datetime]
    ) -> None:
        # Given
        symbol = "INVALID_SYMBOL_12345"
        start_date, end_date = recent_date_range

        # When/Then
        with pytest.raises(StockDataError):
            adapter.get_stock_data(symbol, start_date, end_date)

    def test_raises_on_insufficient_data(self, adapter: YFinanceAdapter) -> None:
        # Given: Very short date range
        end_date = datetime(2024, 1, 5)
        start_date = datetime(2024, 1, 1)
        symbol = "AAPL"

        # When/Then: Should raise due to insufficient data
        with pytest.raises(StockDataError, match="Insufficient data"):
            adapter.get_stock_data(symbol, start_date, end_date)

    def test_handles_weekend_dates(
        self, adapter: YFinanceAdapter, recent_date_range: tuple[datetime, datetime]
    ) -> None:
        # Given: Dates that might include weekends
        symbol = "GOOGL"
        start_date, end_date = recent_date_range

        # When
        prices, _ = adapter.get_stock_data(symbol, start_date, end_date)

        # Then: Should still work (yfinance handles weekends)
        assert len(prices) > 100

    def test_get_stock_name(self, adapter: YFinanceAdapter) -> None:
        # Given
        symbol = "AAPL"

        # When
        name = adapter.get_stock_name(symbol)

        # Then
        assert name
        assert "Apple" in name or name == "AAPL"

    def test_get_stock_name_invalid_symbol(self, adapter: YFinanceAdapter) -> None:
        # Given
        symbol = "INVALID_12345"

        # When/Then
        with pytest.raises(StockDataError):
            adapter.get_stock_name(symbol)

    def test_returns_consistent_data_types(
        self, adapter: YFinanceAdapter, recent_date_range: tuple[datetime, datetime]
    ) -> None:
        # Given
        symbol = "NVDA"
        start_date, end_date = recent_date_range

        # When
        prices, stock_name = adapter.get_stock_data(symbol, start_date, end_date)

        # Then: All types should be correct
        assert isinstance(prices, list)
        assert isinstance(stock_name, str)
        for price in prices:
            assert isinstance(price, StockPrice)
            assert isinstance(price.date, datetime)
            assert isinstance(price.close, float)

    def test_handles_multiple_requests(
        self, adapter: YFinanceAdapter, recent_date_range: tuple[datetime, datetime]
    ) -> None:
        # Given
        symbols = ["AAPL", "MSFT", "GOOGL"]
        start_date, end_date = recent_date_range

        # When: Make multiple requests
        results = []
        for symbol in symbols:
            prices, name = adapter.get_stock_data(symbol, start_date, end_date)
            results.append((symbol, prices, name))

        # Then: All should succeed
        assert len(results) == 3
        for _symbol, prices, name in results:
            assert len(prices) > 100
            assert name
