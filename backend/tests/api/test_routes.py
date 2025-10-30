"""
API Layer Tests - FastAPI Routes

E2E tests using TestClient.
Mocks the service layer to avoid real API calls and calculations.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from api.dependencies import get_backtest_service
from domain.models import BacktestResult, Comparison, PerformerInfo, PortfolioSnapshot
from infrastructure.yfinance_adapter import StockDataError
from main import app

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_service():
    """Mock BacktestService"""
    mock = Mock()
    # Override dependency
    app.dependency_overrides[get_backtest_service] = lambda: mock
    yield mock
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def sample_result():
    """Sample BacktestResult for mocking"""
    return BacktestResult(
        symbol="TEST",
        name="Test Stock",
        strategy="lump_sum",
        total_return=0.25,
        cagr=0.15,
        max_drawdown=-0.10,
        volatility=0.20,
        sharpe_ratio=1.5,
        final_value=12500.0,
        total_invested=10000.0,
        history=[
            PortfolioSnapshot(
                date=datetime(2024, 1, i),
                value=10000.0 + i * 100,
                shares=100.0,
                cumulative_invested=10000.0,
            )
            for i in range(1, 11)
        ],
    )


@pytest.fixture
def sample_comparison():
    """Sample Comparison for mocking"""
    return Comparison(
        best_return="TEST",
        best_sharpe="TEST",
        lowest_risk="TEST",
        best_cagr="TEST",
        best_performer=PerformerInfo(symbol="TEST", total_return=0.25),
        worst_performer=PerformerInfo(symbol="TEST", total_return=0.25),
        average_return=0.25,
        total_invested=10000.0,
    )


# ============================================================================
# Tests: POST /api/backtest
# ============================================================================


class TestBacktestEndpoint:
    """Tests for /api/backtest endpoint"""

    def test_success_single_stock(self, client, mock_service, sample_result, sample_comparison):
        """Should return 200 and correct response for valid request"""
        # Given
        mock_service.run_multiple_backtests.return_value = ([sample_result], sample_comparison)

        # When
        response = client.post(
            "/api/backtest",
            json={
                "stocks": ["TEST"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "strategy": "lump_sum",
                "investment": {"amount": 10000.0},
            },
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "comparison" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["symbol"] == "TEST"
        assert data["results"][0]["strategy"] == "lump_sum"
        assert data["comparison"]["best_return"] == "TEST"

    def test_success_multiple_stocks(self, client, mock_service, sample_comparison):
        """Should handle multiple stocks"""
        # Given
        result1 = BacktestResult(
            symbol="AAPL",
            name="Apple",
            strategy="lump_sum",
            total_return=0.30,
            cagr=0.20,
            max_drawdown=-0.15,
            volatility=0.25,
            sharpe_ratio=1.8,
            final_value=13000.0,
            total_invested=10000.0,
            history=[
                PortfolioSnapshot(
                    date=datetime(2024, 1, 1),
                    value=10000.0,
                    shares=100.0,
                    cumulative_invested=10000.0,
                )
            ],
        )
        result2 = BacktestResult(
            symbol="GOOGL",
            name="Google",
            strategy="lump_sum",
            total_return=0.25,
            cagr=0.18,
            max_drawdown=-0.12,
            volatility=0.22,
            sharpe_ratio=1.6,
            final_value=12500.0,
            total_invested=10000.0,
            history=[
                PortfolioSnapshot(
                    date=datetime(2024, 1, 1),
                    value=10000.0,
                    shares=50.0,
                    cumulative_invested=10000.0,
                )
            ],
        )
        mock_service.run_multiple_backtests.return_value = ([result1, result2], sample_comparison)

        # When
        response = client.post(
            "/api/backtest",
            json={
                "stocks": ["AAPL", "GOOGL"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "strategy": "lump_sum",
                "investment": {"amount": 10000.0},
            },
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2
        assert data["results"][0]["symbol"] == "AAPL"
        assert data["results"][1]["symbol"] == "GOOGL"

    def test_dca_strategy(self, client, mock_service, sample_result, sample_comparison):
        """Should work with DCA strategy"""
        # Given
        dca_result = BacktestResult(
            symbol="TEST",
            name="Test Stock",
            strategy="dca",
            total_return=0.20,
            cagr=0.12,
            max_drawdown=-0.08,
            volatility=0.18,
            sharpe_ratio=1.3,
            final_value=15000.0,
            total_invested=12000.0,
            history=[
                PortfolioSnapshot(
                    date=datetime(2024, 1, 1),
                    value=1000.0,
                    shares=10.0,
                    cumulative_invested=1000.0,
                )
            ],
        )
        mock_service.run_multiple_backtests.return_value = ([dca_result], sample_comparison)

        # When
        response = client.post(
            "/api/backtest",
            json={
                "stocks": ["TEST"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "strategy": "dca",
                "investment": {"amount": 1000.0},
            },
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["results"][0]["strategy"] == "dca"


# ============================================================================
# Tests: Validation Errors (422)
# ============================================================================


class TestValidationErrors:
    """Tests for Pydantic validation errors"""

    def test_end_date_before_start_date(self, client):
        """Should return 422 when end_date is before start_date"""
        # When
        response = client.post(
            "/api/backtest",
            json={
                "stocks": ["TEST"],
                "start_date": "2024-12-31",
                "end_date": "2024-01-01",  # Before start_date
                "strategy": "lump_sum",
                "investment": {"amount": 10000.0},
            },
        )

        # Then
        assert response.status_code == 422
        assert "end_date must be after start_date" in response.text

    def test_empty_stocks_list(self, client):
        """Should return 422 when stocks list is empty"""
        # When
        response = client.post(
            "/api/backtest",
            json={
                "stocks": [],  # Empty list
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "strategy": "lump_sum",
                "investment": {"amount": 10000.0},
            },
        )

        # Then
        assert response.status_code == 422

    def test_too_many_stocks(self, client):
        """Should return 422 when more than 10 stocks"""
        # When
        response = client.post(
            "/api/backtest",
            json={
                "stocks": [f"STOCK{i}" for i in range(11)],  # 11 stocks
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "strategy": "lump_sum",
                "investment": {"amount": 10000.0},
            },
        )

        # Then
        assert response.status_code == 422

    def test_negative_investment_amount(self, client):
        """Should return 422 when investment amount is negative"""
        # When
        response = client.post(
            "/api/backtest",
            json={
                "stocks": ["TEST"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "strategy": "lump_sum",
                "investment": {"amount": -1000.0},  # Negative
            },
        )

        # Then
        assert response.status_code == 422

    def test_zero_investment_amount(self, client):
        """Should return 422 when investment amount is zero"""
        # When
        response = client.post(
            "/api/backtest",
            json={
                "stocks": ["TEST"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "strategy": "lump_sum",
                "investment": {"amount": 0},  # Zero
            },
        )

        # Then
        assert response.status_code == 422

    def test_invalid_strategy(self, client):
        """Should return 422 when strategy is invalid"""
        # When
        response = client.post(
            "/api/backtest",
            json={
                "stocks": ["TEST"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "strategy": "invalid_strategy",  # Invalid
                "investment": {"amount": 10000.0},
            },
        )

        # Then
        assert response.status_code == 422

    def test_empty_stock_symbol(self, client):
        """Should return 422 when stock symbol is empty string"""
        # When
        response = client.post(
            "/api/backtest",
            json={
                "stocks": [""],  # Empty string
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "strategy": "lump_sum",
                "investment": {"amount": 10000.0},
            },
        )

        # Then
        assert response.status_code == 422

    def test_missing_required_fields(self, client):
        """Should return 422 when required fields are missing"""
        # When
        response = client.post(
            "/api/backtest",
            json={
                "stocks": ["TEST"],
                # Missing dates, strategy, investment
            },
        )

        # Then
        assert response.status_code == 422


# ============================================================================
# Tests: Business Logic Errors (404, 500)
# ============================================================================


class TestBusinessErrors:
    """Tests for business logic errors"""

    def test_stock_not_found(self, client, mock_service):
        """Should return 404 when stock data not found"""
        # Given
        mock_service.run_multiple_backtests.side_effect = StockDataError("Stock not found")

        # When
        response = client.post(
            "/api/backtest",
            json={
                "stocks": ["INVALID"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "strategy": "lump_sum",
                "investment": {"amount": 10000.0},
            },
        )

        # Then
        assert response.status_code == 404
        assert "Stock not found" in response.text

    def test_value_error_returns_400(self, client, mock_service):
        """Should return 400 for ValueError"""
        # Given
        mock_service.run_multiple_backtests.side_effect = ValueError("Invalid parameters")

        # When
        response = client.post(
            "/api/backtest",
            json={
                "stocks": ["TEST"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "strategy": "lump_sum",
                "investment": {"amount": 10000.0},
            },
        )

        # Then
        assert response.status_code == 400
        assert "Invalid parameters" in response.text

    def test_unexpected_error_returns_500(self, client, mock_service):
        """Should return 500 for unexpected errors"""
        # Given
        mock_service.run_multiple_backtests.side_effect = Exception("Unexpected error")

        # When
        response = client.post(
            "/api/backtest",
            json={
                "stocks": ["TEST"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "strategy": "lump_sum",
                "investment": {"amount": 10000.0},
            },
        )

        # Then
        assert response.status_code == 500
        assert "Internal server error" in response.text


# ============================================================================
# Tests: Health Check
# ============================================================================


class TestHealthCheck:
    """Tests for /api/health endpoint"""

    def test_health_check_returns_ok(self, client):
        """Should return 200 and status ok"""
        # When
        response = client.get("/api/health")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data


# ============================================================================
# Tests: Root Endpoint
# ============================================================================


class TestRootEndpoint:
    """Tests for / endpoint"""

    def test_root_returns_api_info(self, client):
        """Should return API information"""
        # When
        response = client.get("/")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "BackTester API"
        assert data["status"] == "running"
        assert "docs" in data
        assert "health" in data
