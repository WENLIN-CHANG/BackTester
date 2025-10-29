"""
API Routes - HTTP endpoints

FastAPI route handlers for the backtest API.
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import List

from api.schemas import BacktestRequest, BacktestResponse, ErrorResponse
from api.dependencies import get_backtest_service
from application.backtest_service import BacktestService
from infrastructure.yfinance_adapter import StockDataError
from domain.models import BacktestResult, Comparison


router = APIRouter(prefix="/api", tags=["backtest"])


def convert_result_to_schema(result: BacktestResult) -> dict:
    """Convert domain BacktestResult to API schema dict"""
    return {
        "symbol": result.symbol,
        "name": result.name,
        "strategy": result.strategy,
        "total_return": result.total_return,
        "cagr": result.cagr,
        "max_drawdown": result.max_drawdown,
        "volatility": result.volatility,
        "sharpe_ratio": result.sharpe_ratio,
        "final_value": result.final_value,
        "total_invested": result.total_invested,
        "history": [
            {
                "date": snapshot.date,
                "value": snapshot.value,
                "shares": snapshot.shares,
                "cumulative_invested": snapshot.cumulative_invested,
            }
            for snapshot in result.history
        ],
    }


def convert_comparison_to_schema(comparison: Comparison) -> dict:
    """Convert domain Comparison to API schema dict"""
    return {
        # Simple comparisons
        "best_return": comparison.best_return,
        "best_sharpe": comparison.best_sharpe,
        "lowest_risk": comparison.lowest_risk,
        "best_cagr": comparison.best_cagr,
        # Detailed comparisons
        "best_performer": {
            "symbol": comparison.best_performer.symbol,
            "total_return": comparison.best_performer.total_return,
        },
        "worst_performer": {
            "symbol": comparison.worst_performer.symbol,
            "total_return": comparison.worst_performer.total_return,
        },
        "average_return": comparison.average_return,
        "total_invested": comparison.total_invested,
    }


@router.post(
    "/backtest",
    response_model=BacktestResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        404: {"model": ErrorResponse, "description": "Stock data not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def backtest(
    request: BacktestRequest,
    service: BacktestService = Depends(get_backtest_service),
) -> BacktestResponse:
    """
    Run backtest for one or more stocks

    Executes a backtest simulation using historical stock data and returns
    performance metrics including returns, risk measures, and comparisons.

    Args:
        request: Backtest parameters including stocks, dates, and strategy
        service: Injected backtest service

    Returns:
        Backtest results and comparison

    Raises:
        HTTPException 400: Invalid parameters
        HTTPException 404: Stock data not available
        HTTPException 500: Internal error
    """
    try:
        # Convert date to datetime
        start_datetime = datetime.combine(request.start_date, datetime.min.time())
        end_datetime = datetime.combine(request.end_date, datetime.max.time())

        # Run backtest
        results, comparison = service.run_multiple_backtests(
            symbols=request.stocks,
            start_date=start_datetime,
            end_date=end_datetime,
            strategy=request.strategy,
            amount=request.investment.amount,
        )

        # Convert to response schema
        response = BacktestResponse(
            results=[convert_result_to_schema(r) for r in results],
            comparison=convert_comparison_to_schema(comparison),
        )

        return response

    except StockDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint

    Returns:
        Status message
    """
    return {"status": "ok", "message": "BackTester API is running"}
