# BackTester 實作計畫 v2.0

> "Show me your data structures, and I won't need to see your code." - Linus Torvalds

## 專案概述

BackTester 是一個**正式級**的投資回測系統，採用 Clean Architecture 設計原則，目標是：
- **高品質程式碼**：Pure functions + 100% 測試覆蓋率
- **型別安全**：Backend (Pydantic) + Frontend (TypeScript)
- **可維護性**：清晰的分層架構，職責分明
- **可擴展性**：易於新增功能和策略

## 核心原則

### 1. 資料結構優先 (Data Structures First)

在寫任何實作之前，**先定義所有資料結構**。好的資料結構讓程式碼變簡單。

**原則：**
- 所有資料結構使用 immutable types（Python: `@dataclass(frozen=True)`）
- 明確的型別定義（不使用 `Dict[str, Any]` 這種模糊型別）
- Backend 與 Frontend 的資料結構一致

### 2. 分層架構 (Layered Architecture)

```
┌─────────────────────────────────────┐
│         API Layer (HTTP)            │  ← FastAPI routes
├─────────────────────────────────────┤
│    Application Layer (Services)     │  ← 組合 domain + infrastructure
├─────────────────────────────────────┤
│   │                             │   │
│   │   Domain Layer              │   │  ← Pure functions (核心邏輯)
│   │   (Pure Functions)          │   │
│   │                             │   │
├───┼─────────────────────────────┼───┤
│   │  Infrastructure Layer       │   │  ← Side effects (API calls)
│   │  (Side Effects)             │   │
│   └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

**職責劃分：**
- **Domain**: 核心業務邏輯，100% pure functions，零外部依賴
- **Infrastructure**: 所有 side effects（yfinance, cache, database）
- **Application**: 組合 domain + infrastructure，協調層
- **API**: HTTP 介面，處理請求/回應

### 3. 測試驅動開發 (TDD)

**TDD 循環：**
1. **Red**: 先寫測試（必定失敗）
2. **Green**: 寫最簡單的實作讓測試通過
3. **Refactor**: 重構程式碼（保持測試通過）
4. **Repeat**: 重複以上步驟

**測試金字塔：**
```
         /\
        /  \       E2E Tests (5%)
       /----\
      /      \     Integration Tests (15%)
     /--------\
    /          \   Unit Tests (80%)
   /------------\
```

**為什麼這樣分配？**
- Unit tests 最快、最穩定、最容易維護
- Integration tests 確保組件能協同工作
- E2E tests 確保整體流程正確

---

## Phase 1: 資料結構定義 (Day 1)

### 目標
定義專案中所有的資料結構，Backend 和 Frontend 都要定義清楚。

### 1.1 Backend Domain Models

**檔案：`backend/domain/models.py`**

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal

# ============ 基礎資料結構 ============

@dataclass(frozen=True)
class StockPrice:
    """
    單一時間點的股票價格

    Immutable: frozen=True 確保資料不會被修改
    """
    date: datetime
    close: float

    def __post_init__(self):
        """驗證資料"""
        if self.close <= 0:
            raise ValueError(f"Price must be positive, got {self.close}")


@dataclass(frozen=True)
class PortfolioSnapshot:
    """
    投資組合在某個時間點的快照

    記錄：日期、價值、持有股數、累積投入金額
    """
    date: datetime
    value: float
    shares: float
    cumulative_invested: float

    def __post_init__(self):
        """驗證資料"""
        if self.value < 0:
            raise ValueError("Value cannot be negative")
        if self.shares < 0:
            raise ValueError("Shares cannot be negative")
        if self.cumulative_invested < 0:
            raise ValueError("Cumulative invested cannot be negative")


# ============ 回測結果 ============

StrategyType = Literal["lump_sum", "dca"]

@dataclass(frozen=True)
class BacktestResult:
    """
    單一標的的回測結果

    包含所有財務指標和投資組合歷史
    """
    # 基本資訊
    symbol: str
    name: str
    strategy: StrategyType

    # 報酬指標
    total_return: float  # 總報酬率 (%)
    cagr: float         # 年化報酬率 (%)

    # 風險指標
    max_drawdown: float  # 最大回撤 (%)
    volatility: float    # 波動率 (%)
    sharpe_ratio: float  # 夏普比率

    # 投資組合資訊
    final_value: float
    total_invested: float
    history: List[PortfolioSnapshot]

    def roi_percentage(self) -> float:
        """投資報酬率（百分比）"""
        return (self.final_value - self.total_invested) / self.total_invested * 100


@dataclass(frozen=True)
class Comparison:
    """
    多個標的的比較結果
    """
    best_performer: str      # 報酬率最高
    highest_return: float    # 最高報酬率
    lowest_risk: str         # 風險最低（波動率）
    best_sharpe: str         # 最佳夏普比率


# ============ 投資參數 ============

@dataclass(frozen=True)
class InvestmentParams:
    """投資參數"""
    amount: float
    frequency: Literal["monthly"] = "monthly"

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("Amount must be positive")


@dataclass(frozen=True)
class BacktestParams:
    """回測參數"""
    symbols: List[str]
    start_date: datetime
    end_date: datetime
    strategy: StrategyType
    investment: InvestmentParams

    def __post_init__(self):
        if not self.symbols:
            raise ValueError("At least one symbol required")
        if len(self.symbols) > 10:
            raise ValueError("Maximum 10 symbols allowed")
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")


# ============ 錯誤類別 ============

class DomainError(Exception):
    """Domain layer 的基礎錯誤類別"""
    pass

class InvalidDataError(DomainError):
    """無效的資料"""
    pass

class CalculationError(DomainError):
    """計算錯誤"""
    pass
```

**為什麼這樣設計？**
1. **Immutable (`frozen=True`)**：資料不會被意外修改
2. **Validation (`__post_init__`)**：確保資料合法
3. **Type hints**：IDE 會提供自動完成和型別檢查
4. **清楚的命名**：看名字就知道用途

### 1.2 API Schemas (Pydantic)

**檔案：`backend/api/schemas.py`**

```python
from pydantic import BaseModel, Field, validator
from datetime import date
from typing import List, Literal

# ============ Request Models ============

class InvestmentParamsSchema(BaseModel):
    """投資參數"""
    amount: float = Field(..., gt=0, description="投資金額（必須大於 0）")
    frequency: Literal["monthly"] = Field("monthly", description="投資頻率")


class BacktestRequest(BaseModel):
    """回測請求"""
    stocks: List[str] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="股票代碼列表（1-10 個）"
    )
    start_date: date = Field(..., description="起始日期")
    end_date: date = Field(..., description="結束日期")
    strategy: Literal["lump_sum", "dca"] = Field(..., description="投資策略")
    investment: InvestmentParamsSchema

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        """驗證結束日期必須晚於起始日期"""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

    @validator('stocks')
    def validate_symbols(cls, v):
        """驗證股票代碼格式"""
        for symbol in v:
            if not symbol or not symbol.strip():
                raise ValueError('Stock symbol cannot be empty')
        return [s.strip().upper() for s in v]

    class Config:
        schema_extra = {
            "example": {
                "stocks": ["2330.TW", "QQQ"],
                "start_date": "2020-01-01",
                "end_date": "2024-12-31",
                "strategy": "dca",
                "investment": {
                    "amount": 10000,
                    "frequency": "monthly"
                }
            }
        }


# ============ Response Models ============

class PortfolioSnapshotSchema(BaseModel):
    """投資組合快照"""
    date: str  # ISO format
    value: float
    shares: float
    cumulative_invested: float


class BacktestResultSchema(BaseModel):
    """單一標的回測結果"""
    symbol: str
    name: str
    strategy: str

    total_return: float
    cagr: float
    max_drawdown: float
    volatility: float
    sharpe_ratio: float

    final_value: float
    total_invested: float
    history: List[PortfolioSnapshotSchema]


class ComparisonSchema(BaseModel):
    """比較結果"""
    best_performer: str
    highest_return: float
    lowest_risk: str
    best_sharpe: str


class BacktestResponse(BaseModel):
    """回測回應"""
    results: List[BacktestResultSchema]
    comparison: ComparisonSchema

    class Config:
        schema_extra = {
            "example": {
                "results": [
                    {
                        "symbol": "2330.TW",
                        "name": "台積電",
                        "strategy": "dca",
                        "total_return": 85.5,
                        "cagr": 16.5,
                        "max_drawdown": -28.3,
                        "volatility": 22.1,
                        "sharpe_ratio": 0.75,
                        "final_value": 185000,
                        "total_invested": 100000,
                        "history": []
                    }
                ],
                "comparison": {
                    "best_performer": "QQQ",
                    "highest_return": 120.5,
                    "lowest_risk": "SPY",
                    "best_sharpe": "QQQ"
                }
            }
        }


class StockSearchResult(BaseModel):
    """股票搜尋結果"""
    symbol: str
    name: str
    exchange: str

    class Config:
        schema_extra = {
            "example": {
                "symbol": "2330.TW",
                "name": "台積電",
                "exchange": "TWO"
            }
        }


class ErrorResponse(BaseModel):
    """錯誤回應"""
    detail: str
    error_code: str = ""
```

### 1.3 Frontend Types

**檔案：`frontend/src/types/index.ts`**

```typescript
// ============ Domain Types ============

export interface StockPrice {
  date: string;  // ISO format
  close: number;
}

export interface PortfolioSnapshot {
  date: string;
  value: number;
  shares: number;
  cumulativeInvested: number;
}

export interface BacktestResult {
  symbol: string;
  name: string;
  strategy: Strategy;

  // 報酬指標
  totalReturn: number;
  cagr: number;

  // 風險指標
  maxDrawdown: number;
  volatility: number;
  sharpeRatio: number;

  // 投資組合
  finalValue: number;
  totalInvested: number;
  history: PortfolioSnapshot[];
}

export interface Comparison {
  bestPerformer: string;
  highestReturn: number;
  lowestRisk: string;
  bestSharpe: string;
}

// ============ API Types ============

export type Strategy = 'lump_sum' | 'dca';
export type Frequency = 'monthly';

export interface InvestmentParams {
  amount: number;
  frequency: Frequency;
}

export interface BacktestParams {
  stocks: string[];
  startDate: string;  // YYYY-MM-DD
  endDate: string;    // YYYY-MM-DD
  strategy: Strategy;
  investment: InvestmentParams;
}

export interface BacktestResponse {
  results: BacktestResult[];
  comparison: Comparison;
}

export interface StockSearchResult {
  symbol: string;
  name: string;
  exchange: string;
}

export interface ApiError {
  detail: string;
  errorCode?: string;
}

// ============ UI State Types ============

export interface FormState {
  selectedStocks: string[];
  startDate: string;
  endDate: string;
  strategy: Strategy;
  amount: number;
  frequency: Frequency;
}

export interface UIState {
  isLoading: boolean;
  error: string | null;
  results: BacktestResult[] | null;
}
```

### 1.4 測試資料 Fixtures

**檔案：`backend/tests/conftest.py`**

```python
import pytest
from datetime import datetime
from backend.domain.models import StockPrice, PortfolioSnapshot

@pytest.fixture
def sample_prices():
    """測試用的股票價格資料"""
    return [
        StockPrice(date=datetime(2024, 1, 1), close=100.0),
        StockPrice(date=datetime(2024, 1, 2), close=102.0),
        StockPrice(date=datetime(2024, 1, 3), close=98.0),
        StockPrice(date=datetime(2024, 1, 4), close=105.0),
        StockPrice(date=datetime(2024, 1, 5), close=103.0),
    ]

@pytest.fixture
def sample_snapshots():
    """測試用的投資組合快照"""
    return [
        PortfolioSnapshot(
            date=datetime(2024, 1, 1),
            value=10000,
            shares=100,
            cumulative_invested=10000
        ),
        PortfolioSnapshot(
            date=datetime(2024, 1, 2),
            value=10200,
            shares=100,
            cumulative_invested=10000
        ),
    ]
```

### 交付物（Day 1）

- [ ] `backend/domain/models.py` - 所有 domain models
- [ ] `backend/api/schemas.py` - 所有 Pydantic schemas
- [ ] `frontend/src/types/index.ts` - 所有 TypeScript types
- [ ] `backend/tests/conftest.py` - 測試 fixtures
- [ ] 所有型別定義都通過型別檢查（`mypy` + `tsc`）

---

## Phase 2: Domain Layer - Pure Functions (Day 2-3)

### 目標
實作所有核心業務邏輯，**100% pure functions**，零外部依賴。

### 2.1 財務計算

**檔案：`backend/domain/calculations.py`**

```python
from typing import List
from backend.domain.models import CalculationError

def calculate_daily_returns(values: List[float]) -> List[float]:
    """
    計算每日報酬率

    Returns: 日報酬率列表（長度 = len(values) - 1）
    """
    if len(values) < 2:
        return []

    returns = []
    for i in range(1, len(values)):
        if values[i-1] == 0:
            raise CalculationError("Cannot calculate return from zero value")
        daily_return = (values[i] - values[i-1]) / values[i-1]
        returns.append(daily_return)

    return returns


def calculate_total_return(initial_value: float, final_value: float) -> float:
    """
    總報酬率 (%)

    Formula: (final - initial) / initial * 100
    """
    if initial_value <= 0:
        raise CalculationError("Initial value must be positive")

    return (final_value - initial_value) / initial_value * 100


def calculate_cagr(
    initial_value: float,
    final_value: float,
    years: float
) -> float:
    """
    年化報酬率 (CAGR - Compound Annual Growth Rate)

    Formula: (final / initial) ^ (1 / years) - 1

    Args:
        initial_value: 初始投資金額
        final_value: 最終價值
        years: 投資年數

    Returns:
        年化報酬率（小數，如 0.15 表示 15%）
    """
    if initial_value <= 0:
        raise CalculationError("Initial value must be positive")
    if final_value < 0:
        raise CalculationError("Final value cannot be negative")
    if years <= 0:
        raise CalculationError("Years must be positive")

    if final_value == 0:
        return -1.0  # 完全虧損

    return (final_value / initial_value) ** (1 / years) - 1


def calculate_max_drawdown(values: List[float]) -> float:
    """
    最大回撤 (Maximum Drawdown)

    Formula: min((current - peak) / peak)

    Returns:
        最大回撤百分比（負數，如 -0.283 表示 -28.3%）
    """
    if not values:
        return 0.0

    peak = values[0]
    max_dd = 0.0

    for value in values:
        if value > peak:
            peak = value

        if peak > 0:
            drawdown = (value - peak) / peak
            max_dd = min(max_dd, drawdown)

    return max_dd


def calculate_volatility(returns: List[float]) -> float:
    """
    波動率 (Volatility) - 年化標準差

    Formula: std(daily_returns) * sqrt(252)

    252 = 一年的交易日數

    Returns:
        年化波動率（小數，如 0.25 表示 25%）
    """
    if len(returns) < 2:
        return 0.0

    # 計算平均值
    mean = sum(returns) / len(returns)

    # 計算變異數
    variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)

    # 標準差
    std_dev = variance ** 0.5

    # 年化
    return std_dev * (252 ** 0.5)


def calculate_sharpe_ratio(
    returns: List[float],
    risk_free_rate: float = 0.02
) -> float:
    """
    夏普比率 (Sharpe Ratio)

    Formula: (annual_return - risk_free_rate) / volatility

    Args:
        returns: 日報酬率列表
        risk_free_rate: 無風險利率（預設 2%）

    Returns:
        夏普比率（無單位）
    """
    if len(returns) < 2:
        return 0.0

    # 年化報酬率
    mean_daily_return = sum(returns) / len(returns)
    annual_return = mean_daily_return * 252

    # 波動率
    volatility = calculate_volatility(returns)

    if volatility == 0:
        return 0.0

    # 夏普比率
    return (annual_return - risk_free_rate) / volatility
```

### 2.2 回測邏輯

**檔案：`backend/domain/backtest.py`**

```python
from typing import List
from datetime import datetime
from backend.domain.models import (
    StockPrice,
    PortfolioSnapshot,
    BacktestResult,
    Comparison,
    InvalidDataError
)
from backend.domain import calculations

def backtest_lump_sum(
    prices: List[StockPrice],
    initial_amount: float,
    symbol: str = "",
    name: str = ""
) -> BacktestResult:
    """
    單筆投資回測

    Pure function:
    - 輸入：價格歷史 + 投資金額
    - 輸出：完整的回測結果
    - 零 side effect

    邏輯：
    1. 在第一天以收盤價買入
    2. 計算每天的投資組合價值
    3. 計算所有財務指標
    """
    if not prices:
        raise InvalidDataError("Price list cannot be empty")
    if initial_amount <= 0:
        raise InvalidDataError("Initial amount must be positive")

    # 1. 計算購買股數
    shares = initial_amount / prices[0].close

    # 2. 計算每日投資組合價值
    history = [
        PortfolioSnapshot(
            date=price.date,
            value=shares * price.close,
            shares=shares,
            cumulative_invested=initial_amount
        )
        for price in prices
    ]

    # 3. 計算財務指標
    values = [h.value for h in history]
    returns = calculations.calculate_daily_returns(values)

    years = (prices[-1].date - prices[0].date).days / 365.25

    return BacktestResult(
        symbol=symbol,
        name=name,
        strategy="lump_sum",
        total_return=calculations.calculate_total_return(values[0], values[-1]),
        cagr=calculations.calculate_cagr(values[0], values[-1], years),
        max_drawdown=calculations.calculate_max_drawdown(values),
        volatility=calculations.calculate_volatility(returns),
        sharpe_ratio=calculations.calculate_sharpe_ratio(returns),
        final_value=values[-1],
        total_invested=initial_amount,
        history=history
    )


def backtest_dca(
    prices: List[StockPrice],
    monthly_amount: float,
    symbol: str = "",
    name: str = ""
) -> BacktestResult:
    """
    定期定額回測

    Pure function:
    - 輸入：價格歷史 + 每月投入金額
    - 輸出：完整的回測結果

    邏輯：
    1. 每月第一個交易日以收盤價買入
    2. 累積總股數
    3. 計算每日投資組合價值
    4. 計算所有財務指標
    """
    if not prices:
        raise InvalidDataError("Price list cannot be empty")
    if monthly_amount <= 0:
        raise InvalidDataError("Monthly amount must be positive")

    history = []
    total_shares = 0.0
    total_invested = 0.0
    last_month = None

    # 遍歷所有價格資料
    for price in prices:
        # 檢查是否是新的月份（每月第一個交易日）
        current_month = (price.date.year, price.date.month)

        if current_month != last_month:
            # 執行買入
            shares_to_buy = monthly_amount / price.close
            total_shares += shares_to_buy
            total_invested += monthly_amount
            last_month = current_month

        # 記錄當日快照
        history.append(
            PortfolioSnapshot(
                date=price.date,
                value=total_shares * price.close,
                shares=total_shares,
                cumulative_invested=total_invested
            )
        )

    # 計算財務指標
    values = [h.value for h in history]
    returns = calculations.calculate_daily_returns(values)

    years = (prices[-1].date - prices[0].date).days / 365.25

    return BacktestResult(
        symbol=symbol,
        name=name,
        strategy="dca",
        total_return=calculations.calculate_total_return(total_invested, values[-1]),
        cagr=calculations.calculate_cagr(total_invested, values[-1], years),
        max_drawdown=calculations.calculate_max_drawdown(values),
        volatility=calculations.calculate_volatility(returns),
        sharpe_ratio=calculations.calculate_sharpe_ratio(returns),
        final_value=values[-1],
        total_invested=total_invested,
        history=history
    )


def calculate_comparison(results: List[BacktestResult]) -> Comparison:
    """
    比較多個回測結果

    Pure function: 找出最佳表現者
    """
    if not results:
        raise InvalidDataError("Results list cannot be empty")

    # 找出最佳表現者
    best_performer = max(results, key=lambda r: r.total_return)
    lowest_risk = min(results, key=lambda r: r.volatility)
    best_sharpe = max(results, key=lambda r: r.sharpe_ratio)

    return Comparison(
        best_performer=best_performer.symbol,
        highest_return=best_performer.total_return,
        lowest_risk=lowest_risk.symbol,
        best_sharpe=best_sharpe.symbol
    )
```

### 2.3 單元測試

**檔案：`backend/tests/domain/test_calculations.py`**

```python
import pytest
from backend.domain import calculations
from backend.domain.models import CalculationError

class TestCalculateDailyReturns:
    def test_returns_empty_list_for_single_value(self):
        assert calculations.calculate_daily_returns([100]) == []

    def test_calculates_correct_returns(self):
        values = [100, 110, 105, 115]
        returns = calculations.calculate_daily_returns(values)

        assert len(returns) == 3
        assert abs(returns[0] - 0.10) < 0.0001  # +10%
        assert abs(returns[1] - (-0.0455)) < 0.0001  # -4.55%
        assert abs(returns[2] - 0.0952) < 0.0001  # +9.52%

    def test_raises_on_zero_value(self):
        with pytest.raises(CalculationError):
            calculations.calculate_daily_returns([100, 0, 110])


class TestCalculateTotalReturn:
    def test_returns_correct_percentage(self):
        result = calculations.calculate_total_return(100, 150)
        assert abs(result - 50.0) < 0.0001

    def test_handles_negative_return(self):
        result = calculations.calculate_total_return(100, 80)
        assert abs(result - (-20.0)) < 0.0001

    def test_raises_on_invalid_initial_value(self):
        with pytest.raises(CalculationError):
            calculations.calculate_total_return(0, 150)


class TestCalculateCAGR:
    def test_returns_correct_value(self):
        # $100k → $150k in 3 years
        result = calculations.calculate_cagr(100000, 150000, 3)
        assert abs(result - 0.1447) < 0.001  # ~14.47%

    def test_handles_complete_loss(self):
        result = calculations.calculate_cagr(100000, 0, 3)
        assert result == -1.0

    def test_raises_on_invalid_inputs(self):
        with pytest.raises(CalculationError):
            calculations.calculate_cagr(-100, 150000, 3)

        with pytest.raises(CalculationError):
            calculations.calculate_cagr(100000, 150000, -3)


class TestCalculateMaxDrawdown:
    def test_returns_zero_for_empty_list(self):
        assert calculations.calculate_max_drawdown([]) == 0.0

    def test_returns_zero_for_no_drawdown(self):
        values = [100, 110, 120, 130]
        assert calculations.calculate_max_drawdown(values) == 0.0

    def test_calculates_correct_drawdown(self):
        values = [100, 120, 80, 100]
        # Peak: 120, Trough: 80
        # Drawdown: (80 - 120) / 120 = -0.3333
        result = calculations.calculate_max_drawdown(values)
        assert abs(result - (-0.3333)) < 0.0001


class TestCalculateVolatility:
    def test_returns_zero_for_insufficient_data(self):
        assert calculations.calculate_volatility([]) == 0.0
        assert calculations.calculate_volatility([0.01]) == 0.0

    def test_calculates_correct_volatility(self):
        # 模擬日報酬率：1%, -1%, 2%, -2%
        returns = [0.01, -0.01, 0.02, -0.02]
        volatility = calculations.calculate_volatility(returns)

        # 年化波動率應該約為 0.025 * sqrt(252) ≈ 0.397
        assert 0.35 < volatility < 0.45


class TestCalculateSharpeRatio:
    def test_returns_zero_for_insufficient_data(self):
        assert calculations.calculate_sharpe_ratio([]) == 0.0

    def test_calculates_correct_ratio(self):
        # 模擬穩定正報酬
        returns = [0.001] * 252  # 每天 0.1%
        sharpe = calculations.calculate_sharpe_ratio(returns)

        # 年化報酬 ~25.2%, 無風險利率 2%
        # 波動率接近 0（因為報酬很穩定）
        # 夏普比率應該很高
        assert sharpe > 10

    def test_returns_zero_for_zero_volatility(self):
        returns = [0.0] * 252
        assert calculations.calculate_sharpe_ratio(returns) == 0.0
```

**檔案：`backend/tests/domain/test_backtest.py`**

```python
import pytest
from datetime import datetime
from backend.domain import backtest
from backend.domain.models import StockPrice, InvalidDataError

@pytest.fixture
def sample_prices():
    """測試用的價格資料"""
    return [
        StockPrice(date=datetime(2024, 1, 1), close=100.0),
        StockPrice(date=datetime(2024, 2, 1), close=110.0),
        StockPrice(date=datetime(2024, 3, 1), close=105.0),
        StockPrice(date=datetime(2024, 4, 1), close=115.0),
    ]


class TestBacktestLumpSum:
    def test_calculates_correct_portfolio_value(self, sample_prices):
        result = backtest.backtest_lump_sum(
            prices=sample_prices,
            initial_amount=10000,
            symbol="TEST",
            name="Test Stock"
        )

        # 買入股數 = 10000 / 100 = 100 股
        assert abs(result.history[0].shares - 100) < 0.01

        # 第一天價值 = 100 * 100 = 10000
        assert abs(result.history[0].value - 10000) < 0.01

        # 第二天價值 = 100 * 110 = 11000
        assert abs(result.history[1].value - 11000) < 0.01

        # 最終價值 = 100 * 115 = 11500
        assert abs(result.final_value - 11500) < 0.01

    def test_calculates_correct_return(self, sample_prices):
        result = backtest.backtest_lump_sum(
            prices=sample_prices,
            initial_amount=10000
        )

        # 總報酬率 = (11500 - 10000) / 10000 * 100 = 15%
        assert abs(result.total_return - 15.0) < 0.1

    def test_raises_on_empty_prices(self):
        with pytest.raises(InvalidDataError):
            backtest.backtest_lump_sum(prices=[], initial_amount=10000)

    def test_raises_on_invalid_amount(self, sample_prices):
        with pytest.raises(InvalidDataError):
            backtest.backtest_lump_sum(prices=sample_prices, initial_amount=-100)


class TestBacktestDCA:
    def test_buys_every_month(self, sample_prices):
        result = backtest.backtest_dca(
            prices=sample_prices,
            monthly_amount=1000,
            symbol="TEST"
        )

        # 每月買入一次，共 4 次
        assert abs(result.total_invested - 4000) < 0.01

        # 第一個月：1000 / 100 = 10 股
        # 第二個月：1000 / 110 = 9.09 股
        # 第三個月：1000 / 105 = 9.52 股
        # 第四個月：1000 / 115 = 8.70 股
        # 總計：37.31 股
        expected_shares = 1000/100 + 1000/110 + 1000/105 + 1000/115
        assert abs(result.history[-1].shares - expected_shares) < 0.01

    def test_calculates_correct_final_value(self, sample_prices):
        result = backtest.backtest_dca(
            prices=sample_prices,
            monthly_amount=1000
        )

        # 最終價值 = 總股數 * 最終價格
        expected_value = result.history[-1].shares * 115
        assert abs(result.final_value - expected_value) < 0.01

    def test_raises_on_empty_prices(self):
        with pytest.raises(InvalidDataError):
            backtest.backtest_dca(prices=[], monthly_amount=1000)


class TestCalculateComparison:
    def test_identifies_best_performer(self):
        from backend.domain.models import BacktestResult, PortfolioSnapshot

        results = [
            BacktestResult(
                symbol="A", name="Stock A", strategy="lump_sum",
                total_return=50.0, cagr=10.0,
                max_drawdown=-20.0, volatility=15.0, sharpe_ratio=0.8,
                final_value=150000, total_invested=100000, history=[]
            ),
            BacktestResult(
                symbol="B", name="Stock B", strategy="lump_sum",
                total_return=80.0, cagr=15.0,  # 最高報酬
                max_drawdown=-25.0, volatility=20.0, sharpe_ratio=0.9,
                final_value=180000, total_invested=100000, history=[]
            ),
            BacktestResult(
                symbol="C", name="Stock C", strategy="lump_sum",
                total_return=30.0, cagr=7.0,
                max_drawdown=-10.0, volatility=10.0, sharpe_ratio=0.7,  # 最低風險
                final_value=130000, total_invested=100000, history=[]
            ),
        ]

        comparison = backtest.calculate_comparison(results)

        assert comparison.best_performer == "B"
        assert comparison.lowest_risk == "C"
        assert comparison.best_sharpe == "B"
```

### 執行測試

```bash
# 執行所有 domain tests
pytest backend/tests/domain/ -v

# 查看覆蓋率
pytest backend/tests/domain/ --cov=backend/domain --cov-report=term-missing

# 目標：100% 覆蓋率
```

### 交付物（Day 2-3）

- [ ] `backend/domain/calculations.py` - 所有財務計算函數
- [ ] `backend/domain/backtest.py` - 回測邏輯
- [ ] `backend/tests/domain/test_calculations.py` - 100% 覆蓋率
- [ ] `backend/tests/domain/test_backtest.py` - 100% 覆蓋率
- [ ] 所有測試通過

---

## Phase 3: Infrastructure Layer (Day 4)

### 目標
實作所有 side effects（yfinance API 呼叫、快取機制），完全隔離在 infrastructure 層。

### 3.1 yfinance Adapter

**檔案：`backend/infrastructure/yfinance_adapter.py`**

```python
import yfinance as yf
from datetime import datetime
from typing import List, Optional, Dict
from backend.domain.models import StockPrice

class StockDataError(Exception):
    """股票資料錯誤"""
    pass


class YFinanceAdapter:
    """
    yfinance API 封裝

    隔離所有 yfinance 相關的 side effects
    """

    def get_stock_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[StockPrice]:
        """
        從 Yahoo Finance 取得股票歷史資料

        Args:
            symbol: 股票代碼（如 "2330.TW", "AAPL"）
            start_date: 起始日期
            end_date: 結束日期

        Returns:
            StockPrice 列表（domain model）

        Raises:
            StockDataError: 無法取得資料時
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)

            if df.empty:
                raise StockDataError(
                    f"No data found for {symbol} "
                    f"between {start_date.date()} and {end_date.date()}"
                )

            # 轉換為 domain model
            prices = [
                StockPrice(
                    date=date.to_pydatetime(),
                    close=float(row['Close'])
                )
                for date, row in df.iterrows()
            ]

            # 驗證資料完整性
            if len(prices) < 10:
                raise StockDataError(
                    f"Insufficient data for {symbol}: only {len(prices)} days"
                )

            return prices

        except Exception as e:
            if isinstance(e, StockDataError):
                raise
            raise StockDataError(f"Failed to fetch data for {symbol}: {str(e)}")

    def get_stock_info(self, symbol: str) -> Dict[str, any]:
        """
        取得股票資訊

        Returns:
            包含股票名稱、貨幣、市場等資訊的字典
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'Unknown')
            }
        except Exception as e:
            raise StockDataError(f"Failed to fetch info for {symbol}: {str(e)}")

    def search_stock(self, query: str) -> List[Dict[str, str]]:
        """
        搜尋股票（簡單實作）

        Note: yfinance 沒有原生搜尋功能，這裡只是嘗試直接查詢
        """
        try:
            ticker = yf.Ticker(query.upper())
            info = ticker.info

            if info and 'longName' in info:
                return [{
                    'symbol': query.upper(),
                    'name': info['longName'],
                    'exchange': info.get('exchange', 'Unknown')
                }]
            return []
        except:
            return []
```

### 3.2 快取機制（可選）

**檔案：`backend/infrastructure/cache.py`**

```python
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from functools import wraps

class SimpleCache:
    """
    簡單的記憶體快取

    用於快取 yfinance API 呼叫結果
    """

    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> Optional[Any]:
        """取得快取資料"""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._ttl:
                return value
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any):
        """設定快取資料"""
        self._cache[key] = (value, datetime.now())

    def clear(self):
        """清除所有快取"""
        self._cache.clear()


# 全域快取實例
_cache = SimpleCache(ttl_seconds=3600)


def cached(key_func):
    """
    裝飾器：快取函數結果

    Usage:
        @cached(lambda symbol, start, end: f"{symbol}_{start}_{end}")
        def expensive_function(symbol, start, end):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 產生快取 key
            cache_key = key_func(*args, **kwargs)

            # 嘗試從快取取得
            cached_result = _cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # 執行函數
            result = func(*args, **kwargs)

            # 儲存到快取
            _cache.set(cache_key, result)

            return result
        return wrapper
    return decorator
```

### 3.3 Integration Tests

**檔案：`backend/tests/infrastructure/test_yfinance_adapter.py`**

```python
import pytest
from datetime import datetime
from backend.infrastructure.yfinance_adapter import YFinanceAdapter, StockDataError

@pytest.fixture
def adapter():
    return YFinanceAdapter()


class TestYFinanceAdapter:
    """
    Integration Tests

    這些測試會真實呼叫 Yahoo Finance API
    可能會因為網路問題或 API 限制而失敗
    """

    @pytest.mark.integration
    def test_get_stock_data_returns_valid_data(self, adapter):
        """測試取得美股資料"""
        prices = adapter.get_stock_data(
            symbol="AAPL",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )

        # 應該有資料（約 250 個交易日）
        assert len(prices) > 200

        # 所有價格都是正數
        assert all(p.close > 0 for p in prices)

        # 日期是遞增的
        dates = [p.date for p in prices]
        assert dates == sorted(dates)

    @pytest.mark.integration
    def test_get_taiwan_stock_data(self, adapter):
        """測試取得台股資料"""
        prices = adapter.get_stock_data(
            symbol="2330.TW",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 6, 30)
        )

        assert len(prices) > 100
        assert all(p.close > 0 for p in prices)

    @pytest.mark.integration
    def test_raises_on_invalid_symbol(self, adapter):
        """測試無效的股票代碼"""
        with pytest.raises(StockDataError):
            adapter.get_stock_data(
                symbol="INVALID_SYMBOL_12345",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31)
            )

    @pytest.mark.integration
    def test_raises_on_insufficient_data(self, adapter):
        """測試資料不足的情況"""
        with pytest.raises(StockDataError):
            # 太短的時間範圍
            adapter.get_stock_data(
                symbol="AAPL",
                start_date=datetime(2024, 12, 20),
                end_date=datetime(2024, 12, 21)
            )

    @pytest.mark.integration
    def test_get_stock_info_returns_valid_data(self, adapter):
        """測試取得股票資訊"""
        info = adapter.get_stock_info("AAPL")

        assert info['symbol'] == "AAPL"
        assert 'Apple' in info['name']
        assert info['currency'] in ['USD', 'US']
```

**執行 integration tests:**
```bash
# 執行 integration tests（會連網）
pytest backend/tests/infrastructure/ -m integration -v

# 跳過 integration tests（CI 環境）
pytest backend/tests/ -m "not integration"
```

### 交付物（Day 4）

- [ ] `backend/infrastructure/yfinance_adapter.py`
- [ ] `backend/infrastructure/cache.py`（可選）
- [ ] `backend/tests/infrastructure/test_yfinance_adapter.py`
- [ ] Integration tests 通過（至少 80% 覆蓋率）

---

## Phase 4: Application Layer (Day 5)

### 目標
組合 domain + infrastructure，實作業務服務層。

### 4.1 Backtest Service

**檔案：`backend/application/backtest_service.py`**

```python
from datetime import datetime
from typing import List
from backend.domain.models import BacktestResult, Comparison
from backend.domain import backtest as backtest_logic
from backend.infrastructure.yfinance_adapter import YFinanceAdapter, StockDataError


class BacktestService:
    """
    回測服務

    職責：
    1. 協調 domain 和 infrastructure 層
    2. 處理多個標的的回測
    3. 錯誤處理與資料驗證
    """

    def __init__(self, data_adapter: YFinanceAdapter):
        self.data_adapter = data_adapter

    def run_backtest(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        strategy: str,
        amount: float
    ) -> BacktestResult:
        """
        執行單一標的回測

        流程：
        1. 取得股票資料（infrastructure）
        2. 執行回測計算（domain）
        3. 返回結果
        """
        # 1. 取得股票資料
        prices = self.data_adapter.get_stock_data(symbol, start_date, end_date)
        stock_info = self._get_stock_name(symbol)

        # 2. 執行回測
        if strategy == "lump_sum":
            result = backtest_logic.backtest_lump_sum(
                prices=prices,
                initial_amount=amount,
                symbol=symbol,
                name=stock_info['name']
            )
        elif strategy == "dca":
            result = backtest_logic.backtest_dca(
                prices=prices,
                monthly_amount=amount,
                symbol=symbol,
                name=stock_info['name']
            )
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        return result

    def run_multiple_backtests(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        strategy: str,
        amount: float
    ) -> tuple[List[BacktestResult], Comparison]:
        """
        執行多個標的回測並比較

        Returns:
            (結果列表, 比較結果)
        """
        results = []
        errors = []

        for symbol in symbols:
            try:
                result = self.run_backtest(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    strategy=strategy,
                    amount=amount
                )
                results.append(result)
            except StockDataError as e:
                errors.append(f"{symbol}: {str(e)}")

        if not results:
            raise StockDataError(
                f"Failed to fetch data for all symbols. Errors: {'; '.join(errors)}"
            )

        # 計算比較結果
        comparison = backtest_logic.calculate_comparison(results)

        return results, comparison

    def _get_stock_name(self, symbol: str) -> dict:
        """取得股票名稱（有錯誤處理）"""
        try:
            return self.data_adapter.get_stock_info(symbol)
        except:
            return {'name': symbol, 'currency': 'USD', 'exchange': 'Unknown'}
```

### 4.2 Application Tests

**檔案：`backend/tests/application/test_backtest_service.py`**

```python
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from backend.application.backtest_service import BacktestService
from backend.domain.models import StockPrice
from backend.infrastructure.yfinance_adapter import StockDataError

@pytest.fixture
def mock_adapter():
    """Mock YFinanceAdapter"""
    adapter = Mock()

    # 模擬 get_stock_data 返回測試資料
    adapter.get_stock_data.return_value = [
        StockPrice(date=datetime(2024, 1, i), close=100.0 + i)
        for i in range(1, 31)
    ]

    # 模擬 get_stock_info
    adapter.get_stock_info.return_value = {
        'symbol': 'TEST',
        'name': 'Test Stock',
        'currency': 'USD',
        'exchange': 'NASDAQ'
    }

    return adapter

@pytest.fixture
def service(mock_adapter):
    return BacktestService(mock_adapter)


class TestBacktestService:
    def test_run_backtest_calls_adapter(self, service, mock_adapter):
        """測試 service 正確呼叫 adapter"""
        service.run_backtest(
            symbol="TEST",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            strategy="lump_sum",
            amount=10000
        )

        # 確認呼叫了 adapter
        mock_adapter.get_stock_data.assert_called_once()
        mock_adapter.get_stock_info.assert_called_once()

    def test_run_backtest_returns_result(self, service):
        """測試 service 返回正確的結果"""
        result = service.run_backtest(
            symbol="TEST",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            strategy="lump_sum",
            amount=10000
        )

        assert result.symbol == "TEST"
        assert result.strategy == "lump_sum"
        assert result.final_value > 0

    def test_run_backtest_handles_dca_strategy(self, service):
        """測試 DCA 策略"""
        result = service.run_backtest(
            symbol="TEST",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            strategy="dca",
            amount=1000
        )

        assert result.strategy == "dca"

    def test_run_backtest_raises_on_invalid_strategy(self, service):
        """測試無效策略"""
        with pytest.raises(ValueError):
            service.run_backtest(
                symbol="TEST",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 1, 31),
                strategy="invalid_strategy",
                amount=10000
            )

    def test_run_multiple_backtests(self, service, mock_adapter):
        """測試多標的回測"""
        results, comparison = service.run_multiple_backtests(
            symbols=["TEST1", "TEST2"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            strategy="lump_sum",
            amount=10000
        )

        assert len(results) == 2
        assert comparison.best_performer in ["TEST1", "TEST2"]

    def test_run_multiple_backtests_handles_partial_failures(self, service, mock_adapter):
        """測試部分標的失敗的情況"""
        # 模擬第一個標的成功，第二個失敗
        def side_effect(symbol, *args, **kwargs):
            if symbol == "FAIL":
                raise StockDataError("Test error")
            return [
                StockPrice(date=datetime(2024, 1, i), close=100.0 + i)
                for i in range(1, 31)
            ]

        mock_adapter.get_stock_data.side_effect = side_effect

        results, comparison = service.run_multiple_backtests(
            symbols=["TEST", "FAIL"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            strategy="lump_sum",
            amount=10000
        )

        # 應該只有一個成功的結果
        assert len(results) == 1
        assert results[0].symbol == "TEST"

    def test_run_multiple_backtests_raises_if_all_fail(self, service, mock_adapter):
        """測試所有標的都失敗"""
        mock_adapter.get_stock_data.side_effect = StockDataError("Test error")

        with pytest.raises(StockDataError):
            service.run_multiple_backtests(
                symbols=["FAIL1", "FAIL2"],
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 1, 31),
                strategy="lump_sum",
                amount=10000
            )
```

### 交付物（Day 5）

- [ ] `backend/application/backtest_service.py`
- [ ] `backend/tests/application/test_backtest_service.py`
- [ ] 測試通過（90%+ 覆蓋率）

---

## Phase 5: API Layer (Day 6)

### 目標
實作 FastAPI routes，提供 RESTful API。

### 5.1 Dependencies

**檔案：`backend/api/dependencies.py`**

```python
from backend.application.backtest_service import BacktestService
from backend.infrastructure.yfinance_adapter import YFinanceAdapter

def get_backtest_service() -> BacktestService:
    """
    依賴注入：提供 BacktestService 實例

    FastAPI 會自動呼叫這個函數
    """
    adapter = YFinanceAdapter()
    return BacktestService(adapter)
```

### 5.2 Routes

**檔案：`backend/api/routes.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from backend.api.schemas import (
    BacktestRequest,
    BacktestResponse,
    BacktestResultSchema,
    ComparisonSchema,
    StockSearchResult,
    ErrorResponse
)
from backend.api.dependencies import get_backtest_service
from backend.application.backtest_service import BacktestService
from backend.infrastructure.yfinance_adapter import StockDataError

router = APIRouter(prefix="/api", tags=["backtest"])


@router.post(
    "/backtest",
    response_model=BacktestResponse,
    summary="執行回測",
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def backtest(
    request: BacktestRequest,
    service: BacktestService = Depends(get_backtest_service)
):
    """
    執行回測

    - **stocks**: 股票代碼列表（1-10 個）
    - **start_date**: 起始日期（YYYY-MM-DD）
    - **end_date**: 結束日期（YYYY-MM-DD）
    - **strategy**: 投資策略（lump_sum 或 dca）
    - **investment**: 投資參數
    """
    try:
        # 執行回測
        results, comparison = service.run_multiple_backtests(
            symbols=request.stocks,
            start_date=request.start_date,
            end_date=request.end_date,
            strategy=request.strategy,
            amount=request.investment.amount
        )

        # 轉換為 response schema
        result_schemas = [
            BacktestResultSchema(
                symbol=r.symbol,
                name=r.name,
                strategy=r.strategy,
                total_return=r.total_return,
                cagr=r.cagr,
                max_drawdown=r.max_drawdown,
                volatility=r.volatility,
                sharpe_ratio=r.sharpe_ratio,
                final_value=r.final_value,
                total_invested=r.total_invested,
                history=[
                    {
                        'date': h.date.isoformat(),
                        'value': h.value,
                        'shares': h.shares,
                        'cumulative_invested': h.cumulative_invested
                    }
                    for h in r.history
                ]
            )
            for r in results
        ]

        comparison_schema = ComparisonSchema(
            best_performer=comparison.best_performer,
            highest_return=comparison.highest_return,
            lowest_risk=comparison.lowest_risk,
            best_sharpe=comparison.best_sharpe
        )

        return BacktestResponse(
            results=result_schemas,
            comparison=comparison_schema
        )

    except StockDataError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/stocks/search",
    response_model=list[StockSearchResult],
    summary="搜尋股票"
)
async def search_stocks(
    q: str,
    service: BacktestService = Depends(get_backtest_service)
):
    """
    搜尋股票

    - **q**: 搜尋關鍵字（股票代碼或名稱）
    """
    try:
        results = service.data_adapter.search_stock(q)
        return [
            StockSearchResult(
                symbol=r['symbol'],
                name=r['name'],
                exchange=r['exchange']
            )
            for r in results
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/health", summary="健康檢查")
async def health_check():
    """API 健康檢查"""
    return {"status": "ok"}
```

### 5.3 Main Application

**檔案：`backend/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router

app = FastAPI(
    title="BackTester API",
    description="投資回測系統 API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # 其他可能的前端
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊 router
app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "BackTester API v2.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }
```

### 5.4 API Tests (E2E)

**檔案：`backend/tests/api/test_routes.py`**

```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestHealthCheck:
    def test_health_check_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestBacktestEndpoint:
    def test_backtest_returns_400_for_invalid_dates(self):
        """測試無效日期"""
        response = client.post("/api/backtest", json={
            "stocks": ["AAPL"],
            "start_date": "2024-12-31",
            "end_date": "2024-01-01",  # 結束日期早於起始日期
            "strategy": "lump_sum",
            "investment": {"amount": 10000}
        })

        assert response.status_code == 422  # Pydantic validation error

    def test_backtest_returns_400_for_empty_stocks(self):
        """測試空的股票列表"""
        response = client.post("/api/backtest", json={
            "stocks": [],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "strategy": "lump_sum",
            "investment": {"amount": 10000}
        })

        assert response.status_code == 422

    def test_backtest_returns_400_for_too_many_stocks(self):
        """測試超過 10 個股票"""
        response = client.post("/api/backtest", json={
            "stocks": [f"STOCK{i}" for i in range(11)],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "strategy": "lump_sum",
            "investment": {"amount": 10000}
        })

        assert response.status_code == 422

    @pytest.mark.integration
    def test_backtest_success(self):
        """測試成功的回測（需要網路）"""
        response = client.post("/api/backtest", json={
            "stocks": ["AAPL"],
            "start_date": "2024-01-01",
            "end_date": "2024-06-30",
            "strategy": "lump_sum",
            "investment": {"amount": 10000}
        })

        assert response.status_code == 200
        data = response.json()

        assert "results" in data
        assert "comparison" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["symbol"] == "AAPL"


class TestSearchEndpoint:
    def test_search_requires_query(self):
        """測試搜尋需要 query 參數"""
        response = client.get("/api/stocks/search")
        assert response.status_code == 422

    @pytest.mark.integration
    def test_search_returns_results(self):
        """測試搜尋返回結果（需要網路）"""
        response = client.get("/api/stocks/search?q=AAPL")

        # 可能成功也可能失敗（yfinance 搜尋功能有限）
        assert response.status_code in [200, 500]
```

### 交付物（Day 6）

- [ ] `backend/api/routes.py` - 所有 API 端點
- [ ] `backend/api/dependencies.py` - 依賴注入
- [ ] `backend/main.py` - FastAPI 應用
- [ ] `backend/tests/api/test_routes.py` - E2E 測試
- [ ] Swagger UI 可正常訪問 (http://localhost:8000/docs)

---

## Phase 6: Frontend (Day 7-10)

### 目標
使用 React + TypeScript + Vite 建立前端應用。

### 6.1 專案初始化

```bash
# 建立 React + TypeScript 專案
npm create vite@latest frontend -- --template react-ts

cd frontend

# 安裝依賴
npm install @tanstack/react-query axios recharts
npm install -D tailwindcss postcss autoprefixer
npm install -D @types/node

# 初始化 Tailwind CSS
npx tailwindcss init -p
```

**配置 Tailwind CSS** (`tailwind.config.js`)
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**引入 Tailwind** (`src/index.css`)
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 6.2 API Client

**檔案：`frontend/src/api/client.ts`**

```typescript
import axios from 'axios';
import type { BacktestParams, BacktestResponse, StockSearchResult } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const backtestApi = {
  runBacktest: async (params: BacktestParams): Promise<BacktestResponse> => {
    const { data } = await apiClient.post<BacktestResponse>('/backtest', params);
    return data;
  },

  searchStocks: async (query: string): Promise<StockSearchResult[]> => {
    const { data } = await apiClient.get<StockSearchResult[]>('/stocks/search', {
      params: { q: query },
    });
    return data;
  },
};
```

### 6.3 React Query Hooks

**檔案：`frontend/src/hooks/useBacktest.ts`**

```typescript
import { useMutation } from '@tanstack/react-query';
import { backtestApi } from '../api/client';
import type { BacktestParams } from '../types';

export function useBacktest() {
  return useMutation({
    mutationFn: (params: BacktestParams) => backtestApi.runBacktest(params),
  });
}
```

### 6.4 主要元件

**檔案：`frontend/src/App.tsx`**

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BacktestForm } from './components/BacktestForm';
import { ResultsDisplay } from './components/ResultsDisplay';
import { useState } from 'react';
import type { BacktestResponse } from './types';

const queryClient = new QueryClient();

function App() {
  const [results, setResults] = useState<BacktestResponse | null>(null);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-6 px-4">
            <h1 className="text-3xl font-bold text-gray-900">
              BackTester - 投資回測系統
            </h1>
          </div>
        </header>

        <main className="max-w-7xl mx-auto py-6 px-4">
          <BacktestForm onResults={setResults} />
          {results && <ResultsDisplay results={results} />}
        </main>
      </div>
    </QueryClientProvider>
  );
}

export default App;
```

**其他元件請參考 README.md 中的說明，這裡篇幅有限。**

### 交付物（Day 7-10）

- [ ] Vite + React + TypeScript 專案設置
- [ ] Tailwind CSS 配置
- [ ] API client 與 React Query 整合
- [ ] 主要元件實作
- [ ] 響應式設計
- [ ] 基本的 UI 測試

---

## Phase 7: 測試與品質保證 (Day 11-12)

### 目標
確保所有測試通過，達到目標覆蓋率。

### 測試覆蓋率目標

| 層級 | 目標覆蓋率 | 測試類型 |
|------|-----------|----------|
| Domain | **100%** | Unit tests |
| Infrastructure | **80%+** | Integration tests |
| Application | **90%+** | Mocked unit tests |
| API | **85%+** | E2E tests |

### 執行所有測試

```bash
# Backend 測試
cd backend

# 執行所有測試
pytest tests/ -v

# 查看覆蓋率
pytest tests/ --cov=backend --cov-report=html

# 產生 HTML 報告
open htmlcov/index.html

# Frontend 測試
cd frontend
npm run test -- --coverage
```

### 程式碼品質檢查

```bash
# Python
flake8 backend/
black backend/ --check
mypy backend/

# TypeScript
npm run lint
npm run type-check
```

---

## Phase 8: 文件與部署 (Day 13-14)

### 8.1 文件完善

- [ ] README.md 更新使用說明
- [ ] CLAUDE.md 技術文件完整
- [ ] API 文件（Swagger UI 自動生成）
- [ ] 部署指南

### 8.2 部署準備

**Backend requirements.txt:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
yfinance==0.2.32
pandas==2.1.3
numpy==1.26.2
pytest==7.4.3
pytest-cov==4.1.0
python-dotenv==1.0.0
```

**Frontend package.json scripts:**
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "lint": "eslint . --ext ts,tsx",
    "type-check": "tsc --noEmit"
  }
}
```

---

## 時程總覽

| 天數 | Phase | 主要任務 | 可測試產出 |
|------|-------|----------|-----------|
| Day 1 | Phase 1 | 資料結構定義 | models.py, schemas.py, types.ts 完成 |
| Day 2-3 | Phase 2 | Domain layer 實作 | 100% 測試通過 |
| Day 4 | Phase 3 | Infrastructure layer | Integration tests 通過 |
| Day 5 | Phase 4 | Application layer | Service tests 通過 |
| Day 6 | Phase 5 | API layer | E2E tests 通過 |
| Day 7-10 | Phase 6 | Frontend | UI 可操作 |
| Day 11-12 | Phase 7 | 測試與品質 | 90%+ 覆蓋率 |
| Day 13-14 | Phase 8 | 文件與部署 | 可上線 |

---

## 品質檢查清單

### 架構
- [ ] Domain layer 所有函數都是 pure functions
- [ ] Infrastructure layer 完全隔離 side effects
- [ ] Application layer 正確組合各層
- [ ] API layer 只處理 HTTP 相關邏輯

### 測試
- [ ] Domain layer: 100% 覆蓋率
- [ ] Infrastructure layer: 80%+ 覆蓋率
- [ ] Application layer: 90%+ 覆蓋率
- [ ] API layer: 85%+ 覆蓋率
- [ ] 所有測試通過

### 型別安全
- [ ] Backend: 所有資料結構使用 `@dataclass(frozen=True)`
- [ ] Backend: mypy 檢查通過
- [ ] Frontend: 無任何 `any` type
- [ ] Frontend: tsc 檢查通過

### 文件
- [ ] README.md 完整
- [ ] CLAUDE.md 詳細
- [ ] API 文件（Swagger UI）
- [ ] 程式碼註解清楚

### 功能
- [ ] 單筆投資回測正確
- [ ] 定期定額回測正確
- [ ] 財務指標計算正確
- [ ] 多標的比較正確
- [ ] 錯誤處理完善
- [ ] 前端 UI 響應式

---

## 結語

這份計畫遵循 Clean Architecture 原則，從資料結構定義開始，逐層建構系統。

**核心優勢：**
1. **Pure Functions 優先**：核心邏輯易於測試和理解
2. **分層隔離**：職責清楚，易於維護和擴展
3. **型別安全**：Backend + Frontend 雙重保護
4. **TDD**：測試驅動開發，品質有保證

**與舊版本的差異：**
- ❌ 舊：jQuery + Bootstrap（2015 年技術）
- ✅ 新：React + TypeScript（2025 年標準）

- ❌ 舊：扁平架構（api/services/utils）
- ✅ 新：分層架構（domain/infrastructure/application/api）

- ❌ 舊：`Dict[str, Any]`（無型別）
- ✅ 新：`@dataclass(frozen=True)` + TypeScript（型別安全）

- ❌ 舊：測試為輔
- ✅ 新：TDD，100% 覆蓋率

按照這個計畫執行，可以在 1-2 週內建立一個**正式級**、**可維護**、**高品質**的投資回測系統。

---

**"Good programmers worry about data structures. Bad programmers worry about code."** - Linus Torvalds
