"""
API Schemas - Pydantic models for request/response validation

These models define the HTTP API interface.
"""

from datetime import date, datetime
from typing import List, Literal
from pydantic import BaseModel, Field, field_validator


# Request schemas


class InvestmentParams(BaseModel):
    """Investment amount parameters"""

    amount: float = Field(..., gt=0, description="Investment amount (must be positive)")


class BacktestRequest(BaseModel):
    """Request body for backtest endpoint"""

    stocks: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of stock symbols (1-10 symbols)",
    )
    start_date: date = Field(..., description="Backtest start date")
    end_date: date = Field(..., description="Backtest end date")
    strategy: Literal["lump_sum", "dca"] = Field(
        ..., description="Investment strategy"
    )
    investment: InvestmentParams = Field(..., description="Investment parameters")

    @field_validator("end_date")
    @classmethod
    def end_date_must_be_after_start_date(cls, v: date, info) -> date:
        """Validate end_date is after start_date"""
        if "start_date" in info.data and v <= info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v

    @field_validator("stocks")
    @classmethod
    def stocks_must_not_be_empty(cls, v: List[str]) -> List[str]:
        """Validate stock symbols are not empty"""
        if any(not symbol.strip() for symbol in v):
            raise ValueError("Stock symbols cannot be empty")
        return v


# Response schemas


class PortfolioSnapshotSchema(BaseModel):
    """Portfolio snapshot at a point in time"""

    date: datetime
    value: float
    shares: float
    cumulative_invested: float

    class Config:
        from_attributes = True


class BacktestResultSchema(BaseModel):
    """Backtest result for a single stock"""

    symbol: str
    name: str
    strategy: Literal["lump_sum", "dca"]

    # Return metrics
    total_return: float = Field(..., description="Total return as decimal")
    cagr: float = Field(..., description="Compound annual growth rate")

    # Risk metrics
    max_drawdown: float = Field(..., description="Maximum drawdown (negative)")
    volatility: float = Field(..., description="Annualized volatility")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")

    # Portfolio summary
    final_value: float
    total_invested: float

    # Historical data
    history: List[PortfolioSnapshotSchema]

    class Config:
        from_attributes = True


class ComparisonSchema(BaseModel):
    """Comparison of multiple backtest results"""

    best_return: str = Field(..., description="Symbol with best total return")
    best_sharpe: str = Field(..., description="Symbol with best Sharpe ratio")
    lowest_risk: str = Field(..., description="Symbol with lowest volatility")
    best_cagr: str = Field(..., description="Symbol with best CAGR")

    class Config:
        from_attributes = True


class BacktestResponse(BaseModel):
    """Response body for backtest endpoint"""

    results: List[BacktestResultSchema] = Field(
        ..., description="List of backtest results"
    )
    comparison: ComparisonSchema = Field(..., description="Comparison of results")


class ErrorResponse(BaseModel):
    """Error response"""

    detail: str = Field(..., description="Error message")
