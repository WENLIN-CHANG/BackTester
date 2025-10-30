"""
Tests for domain/calculations.py

Following TDD: Write tests first, then implementation.
Goal: 100% coverage for domain layer.
"""

from datetime import datetime

import pytest

from domain.calculations import (
    calculate_cagr,
    calculate_comparison,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_volatility,
)
from domain.models import BacktestResult, PortfolioSnapshot


class TestCalculateCAGR:
    """Test CAGR (Compound Annual Growth Rate) calculation"""

    def test_positive_return_over_3_years(self) -> None:
        # Given
        initial = 100000.0
        final = 150000.0
        years = 3.0

        # When
        result = calculate_cagr(initial, final, years)

        # Then
        # (150000/100000)^(1/3) - 1 = 0.1447 (14.47%)
        assert abs(result - 0.1447) < 0.001

    def test_negative_return(self) -> None:
        # Given: Lost 50% over 2 years
        initial = 100000.0
        final = 50000.0
        years = 2.0

        # When
        result = calculate_cagr(initial, final, years)

        # Then: Negative CAGR
        assert result < 0
        assert abs(result - (-0.2929)) < 0.001

    def test_no_return(self) -> None:
        # Given: No change
        initial = 100000.0
        final = 100000.0
        years = 5.0

        # When
        result = calculate_cagr(initial, final, years)

        # Then
        assert abs(result) < 1e-10  # Close to zero

    def test_complete_loss(self) -> None:
        # Given: Lost everything
        initial = 100000.0
        final = 0.0
        years = 1.0

        # When
        result = calculate_cagr(initial, final, years)

        # Then: -100% return
        assert result == -1.0

    def test_raises_on_zero_initial(self) -> None:
        # Given
        initial = 0.0
        final = 100000.0
        years = 1.0

        # When/Then
        with pytest.raises(ValueError, match="Initial value must be positive"):
            calculate_cagr(initial, final, years)

    def test_raises_on_negative_initial(self) -> None:
        # Given
        initial = -100000.0
        final = 150000.0
        years = 1.0

        # When/Then
        with pytest.raises(ValueError, match="Initial value must be positive"):
            calculate_cagr(initial, final, years)

    def test_raises_on_zero_years(self) -> None:
        # Given
        initial = 100000.0
        final = 150000.0
        years = 0.0

        # When/Then
        with pytest.raises(ValueError, match="Years must be positive"):
            calculate_cagr(initial, final, years)

    def test_raises_on_negative_years(self) -> None:
        # Given
        initial = 100000.0
        final = 150000.0
        years = -1.0

        # When/Then
        with pytest.raises(ValueError, match="Years must be positive"):
            calculate_cagr(initial, final, years)


class TestCalculateMaxDrawdown:
    """Test Maximum Drawdown calculation"""

    def test_no_drawdown(self) -> None:
        # Given: Always increasing
        values = [100.0, 110.0, 120.0, 130.0]

        # When
        result = calculate_max_drawdown(values)

        # Then
        assert abs(result) < 1e-10  # Close to zero

    def test_simple_drawdown(self) -> None:
        # Given: Peak 120, trough 80
        values = [100.0, 120.0, 80.0, 100.0]

        # When
        result = calculate_max_drawdown(values)

        # Then: (80 - 120) / 120 = -33.33%
        expected = (80.0 - 120.0) / 120.0
        assert abs(result - expected) < 0.0001

    def test_multiple_drawdowns(self) -> None:
        # Given: Two drawdowns, second one larger
        values = [100.0, 120.0, 100.0, 150.0, 90.0]

        # When
        result = calculate_max_drawdown(values)

        # Then: (90 - 150) / 150 = -40%
        expected = (90.0 - 150.0) / 150.0
        assert abs(result - expected) < 0.0001

    def test_continuous_decline(self) -> None:
        # Given: Continuous decline
        values = [100.0, 80.0, 60.0, 40.0]

        # When
        result = calculate_max_drawdown(values)

        # Then: (40 - 100) / 100 = -60%
        expected = (40.0 - 100.0) / 100.0
        assert abs(result - expected) < 0.0001

    def test_single_value(self) -> None:
        # Given
        values = [100.0]

        # When
        result = calculate_max_drawdown(values)

        # Then: No drawdown possible
        assert abs(result) < 1e-10  # Close to zero

    def test_raises_on_empty_list(self) -> None:
        # Given
        values: list[float] = []

        # When/Then
        with pytest.raises(ValueError, match="Values list cannot be empty"):
            calculate_max_drawdown(values)


class TestCalculateVolatility:
    """Test annualized volatility calculation"""

    def test_zero_volatility(self) -> None:
        # Given: No variation
        returns = [0.01] * 252  # 252 trading days, constant return

        # When
        result = calculate_volatility(returns)

        # Then: Zero volatility
        assert abs(result) < 1e-10  # Close to zero

    def test_positive_volatility(self) -> None:
        # Given: Some variation
        returns = [0.01, -0.01, 0.02, -0.02, 0.01]

        # When
        result = calculate_volatility(returns)

        # Then: Positive volatility
        assert result > 0

    def test_annualization_factor(self) -> None:
        # Given: Daily returns
        daily_std = 0.01
        # Returns that produce std of ~0.01
        returns = [0.01, -0.01, 0.01, -0.01] * 63  # 252 days

        # When
        result = calculate_volatility(returns)

        # Then: Should be annualized (multiplied by sqrt(252))
        assert result > daily_std  # Annualized should be larger

    def test_raises_on_empty_list(self) -> None:
        # Given
        returns: list[float] = []

        # When/Then
        with pytest.raises(ValueError, match="Returns list cannot be empty"):
            calculate_volatility(returns)

    def test_single_return(self) -> None:
        # Given
        returns = [0.01]

        # When
        result = calculate_volatility(returns)

        # Then: Zero volatility (need at least 2 points for variance)
        assert abs(result) < 1e-10  # Close to zero


class TestCalculateSharpeRatio:
    """Test Sharpe Ratio calculation"""

    def test_positive_sharpe(self) -> None:
        # Given: Positive returns with some volatility
        returns = [0.001 + (i % 3 - 1) * 0.0001 for i in range(252)]

        # When
        result = calculate_sharpe_ratio(returns, risk_free_rate=0.02)

        # Then: Positive Sharpe ratio (positive excess return)
        assert result > 0

    def test_negative_sharpe(self) -> None:
        # Given: Negative returns with volatility
        returns = [-0.001 + (i % 3 - 1) * 0.0001 for i in range(252)]

        # When
        result = calculate_sharpe_ratio(returns, risk_free_rate=0.02)

        # Then: Negative Sharpe ratio
        assert result < 0

    def test_zero_volatility(self) -> None:
        # Given: Constant returns (zero volatility)
        returns = [0.01] * 252

        # When
        result = calculate_sharpe_ratio(returns, risk_free_rate=0.02)

        # Then: Should handle division by zero gracefully (returns 0)
        assert abs(result) < 1e-10  # Close to zero

    def test_with_different_risk_free_rate(self) -> None:
        # Given: Returns with volatility
        returns = [0.002 + (i % 5 - 2) * 0.0001 for i in range(252)]

        # When
        result_low_rf = calculate_sharpe_ratio(returns, risk_free_rate=0.0)
        result_high_rf = calculate_sharpe_ratio(returns, risk_free_rate=0.5)

        # Then: Higher risk-free rate should lower Sharpe ratio
        assert result_low_rf > result_high_rf

    def test_raises_on_empty_list(self) -> None:
        # Given
        returns: list[float] = []

        # When/Then
        with pytest.raises(ValueError, match="Returns list cannot be empty"):
            calculate_sharpe_ratio(returns)


class TestCalculateComparison:
    """Test comparison calculation across multiple backtests"""

    @pytest.fixture
    def sample_results(self) -> list[BacktestResult]:
        """Create sample backtest results for testing"""
        base_date = datetime(2024, 1, 1)
        history = [
            PortfolioSnapshot(
                date=base_date,
                value=100000.0,
                shares=100.0,
                cumulative_invested=100000.0,
            )
        ]

        return [
            BacktestResult(
                symbol="AAPL",
                name="Apple Inc.",
                strategy="lump_sum",
                total_return=0.5,  # 50%
                cagr=0.15,  # 15%
                max_drawdown=-0.2,
                volatility=0.25,
                sharpe_ratio=1.5,
                final_value=150000.0,
                total_invested=100000.0,
                history=history,
            ),
            BacktestResult(
                symbol="GOOGL",
                name="Alphabet Inc.",
                strategy="lump_sum",
                total_return=0.3,  # 30%
                cagr=0.20,  # 20% - Best CAGR
                max_drawdown=-0.15,
                volatility=0.20,  # Lowest volatility
                sharpe_ratio=2.0,  # Best Sharpe
                final_value=130000.0,
                total_invested=100000.0,
                history=history,
            ),
            BacktestResult(
                symbol="MSFT",
                name="Microsoft Corp.",
                strategy="lump_sum",
                total_return=0.6,  # 60% - Best return
                cagr=0.18,
                max_drawdown=-0.25,
                volatility=0.30,
                sharpe_ratio=1.8,
                final_value=160000.0,
                total_invested=100000.0,
                history=history,
            ),
        ]

    def test_finds_best_return(self, sample_results: list[BacktestResult]) -> None:
        # When
        result = calculate_comparison(sample_results)

        # Then: MSFT has best return (60%)
        assert result.best_return == "MSFT"

    def test_finds_best_sharpe(self, sample_results: list[BacktestResult]) -> None:
        # When
        result = calculate_comparison(sample_results)

        # Then: GOOGL has best Sharpe (2.0)
        assert result.best_sharpe == "GOOGL"

    def test_finds_lowest_risk(self, sample_results: list[BacktestResult]) -> None:
        # When
        result = calculate_comparison(sample_results)

        # Then: GOOGL has lowest volatility (0.20)
        assert result.lowest_risk == "GOOGL"

    def test_finds_best_cagr(self, sample_results: list[BacktestResult]) -> None:
        # When
        result = calculate_comparison(sample_results)

        # Then: GOOGL has best CAGR (20%)
        assert result.best_cagr == "GOOGL"

    def test_single_result(self) -> None:
        # Given
        base_date = datetime(2024, 1, 1)
        history = [
            PortfolioSnapshot(
                date=base_date,
                value=100000.0,
                shares=100.0,
                cumulative_invested=100000.0,
            )
        ]
        single_result = [
            BacktestResult(
                symbol="AAPL",
                name="Apple Inc.",
                strategy="lump_sum",
                total_return=0.5,
                cagr=0.15,
                max_drawdown=-0.2,
                volatility=0.25,
                sharpe_ratio=1.5,
                final_value=150000.0,
                total_invested=100000.0,
                history=history,
            )
        ]

        # When
        result = calculate_comparison(single_result)

        # Then: All comparisons should be AAPL
        assert result.best_return == "AAPL"
        assert result.best_sharpe == "AAPL"
        assert result.lowest_risk == "AAPL"
        assert result.best_cagr == "AAPL"

    def test_raises_on_empty_list(self) -> None:
        # Given
        results: list[BacktestResult] = []

        # When/Then
        with pytest.raises(ValueError, match="Results list cannot be empty"):
            calculate_comparison(results)
