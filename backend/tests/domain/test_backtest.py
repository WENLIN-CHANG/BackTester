"""
Tests for domain/backtest.py

Testing backtest logic with TDD approach.
Goal: 100% coverage for domain layer.
"""

import pytest
from datetime import datetime, timedelta
from domain.backtest import backtest_lump_sum, backtest_dca
from domain.models import StockPrice, BacktestResult


class TestBacktestLumpSum:
    """Test lump sum investment backtest"""

    @pytest.fixture
    def simple_prices(self) -> list[StockPrice]:
        """Simple price data: $100 → $150 over 1 year"""
        base_date = datetime(2024, 1, 1)
        return [
            StockPrice(date=base_date + timedelta(days=i), close=100.0 + i * 0.2)
            for i in range(252)  # 252 trading days
        ]

    @pytest.fixture
    def volatile_prices(self) -> list[StockPrice]:
        """Volatile price data with drawdowns"""
        base_date = datetime(2024, 1, 1)
        # Pattern: up, down, up, down
        prices = []
        price = 100.0
        for i in range(252):
            if i % 10 < 5:
                price *= 1.01  # Up 1%
            else:
                price *= 0.99  # Down 1%
            prices.append(StockPrice(date=base_date + timedelta(days=i), close=price))
        return prices

    def test_basic_lump_sum_positive_return(self, simple_prices: list[StockPrice]) -> None:
        # Given
        initial_amount = 100000.0

        # When
        result = backtest_lump_sum(
            prices=simple_prices,
            initial_amount=initial_amount,
            symbol="TEST",
            name="Test Stock",
        )

        # Then
        assert result.symbol == "TEST"
        assert result.name == "Test Stock"
        assert result.strategy == "lump_sum"
        assert result.total_invested == initial_amount
        assert result.final_value > initial_amount  # Made profit
        assert result.total_return > 0  # Positive return
        assert result.cagr > 0  # Positive CAGR
        assert len(result.history) == 252  # One snapshot per day

    def test_calculates_correct_shares(self, simple_prices: list[StockPrice]) -> None:
        # Given
        initial_amount = 100000.0
        first_price = simple_prices[0].close

        # When
        result = backtest_lump_sum(
            prices=simple_prices, initial_amount=initial_amount, symbol="TEST"
        )

        # Then
        expected_shares = initial_amount / first_price
        assert abs(result.history[0].shares - expected_shares) < 0.01

    def test_portfolio_value_changes_with_price(
        self, simple_prices: list[StockPrice]
    ) -> None:
        # Given
        initial_amount = 100000.0

        # When
        result = backtest_lump_sum(
            prices=simple_prices, initial_amount=initial_amount, symbol="TEST"
        )

        # Then: Value should increase as price increases
        first_value = result.history[0].value
        last_value = result.history[-1].value
        assert last_value > first_value

    def test_shares_remain_constant(self, simple_prices: list[StockPrice]) -> None:
        # Given
        initial_amount = 100000.0

        # When
        result = backtest_lump_sum(
            prices=simple_prices, initial_amount=initial_amount, symbol="TEST"
        )

        # Then: Shares should never change (buy and hold)
        shares = [snapshot.shares for snapshot in result.history]
        assert all(abs(s - shares[0]) < 0.01 for s in shares)

    def test_max_drawdown_with_volatile_prices(
        self, volatile_prices: list[StockPrice]
    ) -> None:
        # Given
        initial_amount = 100000.0

        # When
        result = backtest_lump_sum(
            prices=volatile_prices, initial_amount=initial_amount, symbol="TEST"
        )

        # Then: Should have negative max drawdown (there were declines)
        assert result.max_drawdown < 0

    def test_volatility_positive(self, simple_prices: list[StockPrice]) -> None:
        # Given
        initial_amount = 100000.0

        # When
        result = backtest_lump_sum(
            prices=simple_prices, initial_amount=initial_amount, symbol="TEST"
        )

        # Then: Volatility should be positive
        assert result.volatility >= 0

    def test_raises_on_empty_prices(self) -> None:
        # Given
        prices: list[StockPrice] = []

        # When/Then
        with pytest.raises(ValueError, match="Prices list cannot be empty"):
            backtest_lump_sum(prices=prices, initial_amount=100000.0, symbol="TEST")

    def test_raises_on_zero_amount(self, simple_prices: list[StockPrice]) -> None:
        # Given
        initial_amount = 0.0

        # When/Then
        with pytest.raises(ValueError, match="Initial amount must be positive"):
            backtest_lump_sum(
                prices=simple_prices, initial_amount=initial_amount, symbol="TEST"
            )

    def test_raises_on_negative_amount(self, simple_prices: list[StockPrice]) -> None:
        # Given
        initial_amount = -100000.0

        # When/Then
        with pytest.raises(ValueError, match="Initial amount must be positive"):
            backtest_lump_sum(
                prices=simple_prices, initial_amount=initial_amount, symbol="TEST"
            )

    def test_default_symbol_and_name(self, simple_prices: list[StockPrice]) -> None:
        # Given
        initial_amount = 100000.0

        # When
        result = backtest_lump_sum(prices=simple_prices, initial_amount=initial_amount)

        # Then: Should use default values
        assert result.symbol == ""
        assert result.name == ""


class TestBacktestDCA:
    """Test dollar-cost averaging (DCA) backtest"""

    @pytest.fixture
    def monthly_prices(self) -> list[StockPrice]:
        """Price data covering multiple months"""
        base_date = datetime(2024, 1, 1)
        # 12 months of daily data
        return [
            StockPrice(date=base_date + timedelta(days=i), close=100.0 + i * 0.1)
            for i in range(252)
        ]

    @pytest.fixture
    def volatile_monthly_prices(self) -> list[StockPrice]:
        """Volatile price data for testing DCA advantages"""
        base_date = datetime(2024, 1, 1)
        prices = []
        price = 100.0
        for i in range(252):
            # Simulate volatility
            if i % 30 < 15:
                price *= 1.005  # Up 0.5%
            else:
                price *= 0.995  # Down 0.5%
            prices.append(StockPrice(date=base_date + timedelta(days=i), close=price))
        return prices

    def test_basic_dca_positive_return(
        self, monthly_prices: list[StockPrice]
    ) -> None:
        # Given
        monthly_amount = 10000.0

        # When
        result = backtest_dca(
            prices=monthly_prices,
            monthly_amount=monthly_amount,
            symbol="TEST",
            name="Test Stock",
        )

        # Then
        assert result.symbol == "TEST"
        assert result.name == "Test Stock"
        assert result.strategy == "dca"
        assert result.total_invested > monthly_amount  # Invested over multiple months
        assert result.final_value > 0
        assert len(result.history) == 252  # One snapshot per day

    def test_invests_monthly(self, monthly_prices: list[StockPrice]) -> None:
        # Given
        monthly_amount = 10000.0

        # When
        result = backtest_dca(
            prices=monthly_prices, monthly_amount=monthly_amount, symbol="TEST"
        )

        # Then: Should invest once per month
        # 252 days = ~9 months of data (Jan 1 to Sep 8)
        expected_months = 9
        expected_total_invested = monthly_amount * expected_months
        assert result.total_invested == expected_total_invested

    def test_shares_accumulate_over_time(
        self, monthly_prices: list[StockPrice]
    ) -> None:
        # Given
        monthly_amount = 10000.0

        # When
        result = backtest_dca(
            prices=monthly_prices, monthly_amount=monthly_amount, symbol="TEST"
        )

        # Then: Shares should increase (or stay same) over time
        shares_over_time = [snapshot.shares for snapshot in result.history]
        for i in range(1, len(shares_over_time)):
            assert shares_over_time[i] >= shares_over_time[i - 1]

    def test_cumulative_invested_increases(
        self, monthly_prices: list[StockPrice]
    ) -> None:
        # Given
        monthly_amount = 10000.0

        # When
        result = backtest_dca(
            prices=monthly_prices, monthly_amount=monthly_amount, symbol="TEST"
        )

        # Then: Cumulative invested should increase monthly
        cumulative = [snapshot.cumulative_invested for snapshot in result.history]
        # First investment on day 0
        assert cumulative[0] == monthly_amount
        # Should be monotonically increasing
        for i in range(1, len(cumulative)):
            assert cumulative[i] >= cumulative[i - 1]

    def test_first_month_investment(self, monthly_prices: list[StockPrice]) -> None:
        # Given
        monthly_amount = 10000.0

        # When
        result = backtest_dca(
            prices=monthly_prices, monthly_amount=monthly_amount, symbol="TEST"
        )

        # Then: First snapshot should show first investment
        first_snapshot = result.history[0]
        assert first_snapshot.cumulative_invested == monthly_amount
        assert first_snapshot.shares > 0

    def test_dca_handles_volatility(
        self, volatile_monthly_prices: list[StockPrice]
    ) -> None:
        # Given
        monthly_amount = 10000.0

        # When
        result = backtest_dca(
            prices=volatile_monthly_prices,
            monthly_amount=monthly_amount,
            symbol="TEST",
        )

        # Then: Should complete without errors
        assert result.total_invested > 0
        assert result.final_value > 0
        assert result.volatility >= 0

    def test_calculates_metrics(self, monthly_prices: list[StockPrice]) -> None:
        # Given
        monthly_amount = 10000.0

        # When
        result = backtest_dca(
            prices=monthly_prices, monthly_amount=monthly_amount, symbol="TEST"
        )

        # Then: All metrics should be calculated
        assert isinstance(result.total_return, float)
        assert isinstance(result.cagr, float)
        assert isinstance(result.max_drawdown, float)
        assert isinstance(result.volatility, float)
        assert isinstance(result.sharpe_ratio, float)
        assert result.max_drawdown <= 0  # Should be negative or zero

    def test_raises_on_empty_prices(self) -> None:
        # Given
        prices: list[StockPrice] = []

        # When/Then
        with pytest.raises(ValueError, match="Prices list cannot be empty"):
            backtest_dca(prices=prices, monthly_amount=10000.0, symbol="TEST")

    def test_raises_on_zero_amount(self, monthly_prices: list[StockPrice]) -> None:
        # Given
        monthly_amount = 0.0

        # When/Then
        with pytest.raises(ValueError, match="Monthly amount must be positive"):
            backtest_dca(
                prices=monthly_prices, monthly_amount=monthly_amount, symbol="TEST"
            )

    def test_raises_on_negative_amount(
        self, monthly_prices: list[StockPrice]
    ) -> None:
        # Given
        monthly_amount = -10000.0

        # When/Then
        with pytest.raises(ValueError, match="Monthly amount must be positive"):
            backtest_dca(
                prices=monthly_prices, monthly_amount=monthly_amount, symbol="TEST"
            )

    def test_default_symbol_and_name(self, monthly_prices: list[StockPrice]) -> None:
        # Given
        monthly_amount = 10000.0

        # When
        result = backtest_dca(prices=monthly_prices, monthly_amount=monthly_amount)

        # Then: Should use default values
        assert result.symbol == ""
        assert result.name == ""

    def test_single_month_data(self) -> None:
        # Given: Less than a month of data
        base_date = datetime(2024, 1, 1)
        prices = [
            StockPrice(date=base_date + timedelta(days=i), close=100.0)
            for i in range(20)
        ]

        # When
        result = backtest_dca(prices=prices, monthly_amount=10000.0, symbol="TEST")

        # Then: Should invest only once
        assert result.total_invested == 10000.0
