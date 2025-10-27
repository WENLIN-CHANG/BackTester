# CLAUDE.md - BackTester 技術文件

## 最重要的指導原則：

- DO NOT OVERDESIGN! DO NOT OVERENGINEER!
- 不要過度設計！不要過度工程化！

## 在開始任何任務之前

- 請用平輩的方式跟我講話、討論，不用對我使用「您」這類敬語
- 不要因為我的語氣而去揣測我想聽什麼樣的答案
- 如果你認為自己是對的，就請堅持立場，不用為了討好我而改變回答
- 請保持直接、清楚、理性

### 重要！請善用 MCP 工具！

- 如果要呼叫函式庫但不確定使用方式，請使用 `context7` MCP 工具取得最新的文件和程式碼範例。

## 專案概述

**專案名稱**: BackTester - 投資回測系統
**專案目標**: 建立一個**正式級**、**可維護**、**高品質**的投資回測工具
**主要使用者**: 個人投資者、理財新手、投資愛好者

**核心特色：**
- ✅ Clean Architecture（分層架構）
- ✅ Pure Functions 優先（domain layer 100% pure）
- ✅ 型別安全（Pydantic + TypeScript）
- ✅ 100% 測試覆蓋率（domain layer）
- ✅ TDD 開發流程

---

## 技術棧

### Backend (Python 3.10+)

| 類別 | 技術 | 版本 | 用途 |
|------|------|------|------|
| **框架** | FastAPI | 0.104+ | Web 框架，自動文件生成 |
| **型別驗證** | Pydantic | 2.5+ | Request/Response 驗證 |
| **資料來源** | yfinance | 0.2+ | Yahoo Finance API |
| **資料處理** | pandas | 2.1+ | 時間序列處理 |
| **數值計算** | numpy | 1.26+ | 財務計算 |
| **測試** | pytest | 7.4+ | 測試框架 |
| **覆蓋率** | pytest-cov | 4.1+ | 測試覆蓋率報告 |
| **型別檢查** | mypy | 1.7+ | 靜態型別檢查 |

### Frontend (Node.js 18+)

| 類別 | 技術 | 版本 | 用途 |
|------|------|------|------|
| **框架** | React | 18+ | UI 框架 |
| **型別系統** | TypeScript | 5+ | 型別安全 |
| **建置工具** | Vite | 5+ | 開發伺服器與建置 |
| **狀態管理** | TanStack Query | 5+ | 伺服器狀態管理 |
| **HTTP Client** | axios | 1.6+ | API 呼叫 |
| **圖表** | Recharts | 2.10+ | 資料視覺化 |
| **樣式** | Tailwind CSS | 3+ | CSS 框架 |

---

## 專案結構

### 完整目錄結構

```
BackTester/
│
├── backend/                        # Python FastAPI 後端
│   │
│   ├── domain/                     # 🔵 核心業務邏輯層 (Pure Functions)
│   │   ├── __init__.py
│   │   ├── models.py              # 不可變資料結構 (@dataclass(frozen=True))
│   │   ├── calculations.py        # 財務指標計算 (pure functions)
│   │   └── backtest.py            # 回測邏輯 (pure functions)
│   │
│   ├── infrastructure/             # 🟡 基礎設施層 (Side Effects)
│   │   ├── __init__.py
│   │   ├── yfinance_adapter.py   # Yahoo Finance API 封裝
│   │   └── cache.py              # 快取機制（可選）
│   │
│   ├── application/                # 🟢 應用服務層 (Orchestration)
│   │   ├── __init__.py
│   │   └── backtest_service.py   # 組合 domain + infrastructure
│   │
│   ├── api/                        # 🟣 HTTP 介面層
│   │   ├── __init__.py
│   │   ├── routes.py              # API 路由定義
│   │   ├── schemas.py             # Pydantic Request/Response models
│   │   └── dependencies.py        # FastAPI 依賴注入
│   │
│   ├── tests/                      # 測試（分層）
│   │   ├── domain/                # Unit tests (最快，100% 覆蓋)
│   │   │   ├── test_calculations.py
│   │   │   └── test_backtest.py
│   │   ├── infrastructure/        # Integration tests (真實 API)
│   │   │   └── test_yfinance_adapter.py
│   │   ├── application/           # Service tests (mocked)
│   │   │   └── test_backtest_service.py
│   │   └── api/                   # E2E tests
│   │       └── test_routes.py
│   │
│   ├── main.py                    # FastAPI 應用進入點
│   └── requirements.txt           # Python 依賴
│
├── frontend/                       # React + TypeScript 前端
│   ├── src/
│   │   ├── types/                 # TypeScript 型別定義
│   │   │   └── index.ts          # 所有介面定義
│   │   │
│   │   ├── api/                   # API 層
│   │   │   └── client.ts          # axios client
│   │   │
│   │   ├── hooks/                 # React hooks
│   │   │   └── useBacktest.ts    # React Query mutation
│   │   │
│   │   ├── components/            # React 元件
│   │   │   ├── StockSelector.tsx # 標的選擇
│   │   │   ├── BacktestForm.tsx  # 回測表單
│   │   │   ├── ResultsTable.tsx  # 結果表格
│   │   │   └── PerformanceChart.tsx # 績效圖表
│   │   │
│   │   ├── App.tsx               # 主應用
│   │   └── main.tsx              # 進入點
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── PLAN.md                        # 實作計畫（詳細分 phase）
├── CLAUDE.md                      # 本文件
└── README.md                      # 使用者文件
```

---

## 架構設計

### Clean Architecture 分層

```
┌─────────────────────────────────────────────────────────┐
│                     API Layer                           │
│  ┌────────────────────────────────────────────────┐    │
│  │  FastAPI routes, HTTP handlers                 │    │
│  │  Pydantic schemas (validation)                 │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                          ↓ 呼叫
┌─────────────────────────────────────────────────────────┐
│                Application Layer                        │
│  ┌────────────────────────────────────────────────┐    │
│  │  BacktestService (組合 domain + infra)        │    │
│  │  錯誤處理、多標的處理                          │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
        ↓ 取得資料                    ↓ 執行計算
┌──────────────────────┐    ┌──────────────────────────┐
│ Infrastructure Layer │    │     Domain Layer         │
│  ┌────────────────┐  │    │  ┌────────────────────┐ │
│  │ YFinanceAdapter│  │    │  │ Pure Functions     │ │
│  │ (Side Effects) │  │    │  │ calculations.py    │ │
│  │                │  │    │  │ backtest.py        │ │
│  │ - API 呼叫     │  │    │  │                    │ │
│  │ - 快取         │  │    │  │ - 零依賴          │ │
│  └────────────────┘  │    │  │ - 零 side effect  │ │
└──────────────────────┘    │  └────────────────────┘ │
                            └──────────────────────────┘
```

### 依賴方向

```
API → Application → Domain
                    ↑
                    └── Infrastructure
```

**關鍵原則：**
- **Domain 層不依賴任何其他層**（零外部依賴）
- Infrastructure 依賴 Domain（使用 Domain 的資料結構）
- Application 依賴 Domain + Infrastructure
- API 依賴 Application

### 資料流程

```
1. 使用者請求
   ↓
2. API Layer 接收（FastAPI route）
   ↓
3. Pydantic 驗證 request
   ↓
4. Application Layer 協調
   ↓
5. Infrastructure Layer 取得股票資料（side effect）
   ↓
6. Domain Layer 執行回測計算（pure function）
   ↓
7. Application Layer 組裝結果
   ↓
8. API Layer 返回 response
```

---

## 核心功能設計

### 1. Domain Layer（核心業務邏輯）

#### 1.1 資料結構 (`domain/models.py`)

**設計原則：**
- 使用 `@dataclass(frozen=True)` 確保 immutability
- 所有型別都有明確定義
- 在 `__post_init__` 中驗證資料

**核心資料結構：**

```python
@dataclass(frozen=True)
class StockPrice:
    """單一時間點的股票價格"""
    date: datetime
    close: float

@dataclass(frozen=True)
class PortfolioSnapshot:
    """投資組合快照"""
    date: datetime
    value: float
    shares: float
    cumulative_invested: float

@dataclass(frozen=True)
class BacktestResult:
    """完整的回測結果"""
    symbol: str
    name: str
    strategy: Literal["lump_sum", "dca"]

    # 報酬指標
    total_return: float
    cagr: float

    # 風險指標
    max_drawdown: float
    volatility: float
    sharpe_ratio: float

    # 投資組合
    final_value: float
    total_invested: float
    history: List[PortfolioSnapshot]
```

#### 1.2 財務計算 (`domain/calculations.py`)

**所有函數都是 pure functions：**
- 相同輸入永遠產生相同輸出
- 沒有 side effects
- 不依賴外部狀態
- 容易測試

**主要函數：**

```python
def calculate_cagr(initial: float, final: float, years: float) -> float:
    """年化報酬率 (Compound Annual Growth Rate)"""
    return (final / initial) ** (1 / years) - 1

def calculate_max_drawdown(values: List[float]) -> float:
    """最大回撤 (Maximum Drawdown)"""
    peak = values[0]
    max_dd = 0.0
    for value in values:
        if value > peak:
            peak = value
        dd = (value - peak) / peak
        max_dd = min(max_dd, dd)
    return max_dd

def calculate_volatility(returns: List[float]) -> float:
    """波動率（年化標準差）"""
    std_dev = std(returns)
    return std_dev * (252 ** 0.5)

def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """夏普比率"""
    annual_return = mean(returns) * 252
    volatility = calculate_volatility(returns)
    return (annual_return - risk_free_rate) / volatility if volatility > 0 else 0
```

#### 1.3 回測邏輯 (`domain/backtest.py`)

**單筆投資回測：**
```python
def backtest_lump_sum(
    prices: List[StockPrice],
    initial_amount: float,
    symbol: str = "",
    name: str = ""
) -> BacktestResult:
    """
    Pure function: 單筆投資回測

    邏輯：
    1. 在第一天買入：shares = amount / price[0]
    2. 每天計算價值：value = shares * price
    3. 計算所有財務指標
    4. 返回 BacktestResult
    """
    shares = initial_amount / prices[0].close

    history = [
        PortfolioSnapshot(
            date=p.date,
            value=shares * p.close,
            shares=shares,
            cumulative_invested=initial_amount
        )
        for p in prices
    ]

    # 計算指標...
    return BacktestResult(...)
```

**定期定額回測：**
```python
def backtest_dca(
    prices: List[StockPrice],
    monthly_amount: float,
    symbol: str = "",
    name: str = ""
) -> BacktestResult:
    """
    Pure function: 定期定額回測

    邏輯：
    1. 每月第一個交易日買入
    2. 累積總股數
    3. 計算每日價值
    4. 計算所有財務指標
    """
    total_shares = 0.0
    total_invested = 0.0
    last_month = None

    for price in prices:
        current_month = (price.date.year, price.date.month)
        if current_month != last_month:
            # 每月買入
            total_shares += monthly_amount / price.close
            total_invested += monthly_amount
            last_month = current_month

        # 記錄快照...

    return BacktestResult(...)
```

### 2. Infrastructure Layer（基礎設施）

#### 2.1 yfinance Adapter (`infrastructure/yfinance_adapter.py`)

**職責：**
- 隔離所有 yfinance 相關的 side effects
- 將 pandas DataFrame 轉換為 domain models
- 錯誤處理與資料驗證

**關鍵設計：**
```python
class YFinanceAdapter:
    def get_stock_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[StockPrice]:
        """
        從 Yahoo Finance 取得資料

        Returns: List[StockPrice] (domain model)
        Raises: StockDataError
        """
        # 1. 呼叫 yfinance API (side effect)
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)

        # 2. 轉換為 domain model
        prices = [
            StockPrice(
                date=date.to_pydatetime(),
                close=float(row['Close'])
            )
            for date, row in df.iterrows()
        ]

        # 3. 驗證資料
        if len(prices) < 10:
            raise StockDataError(f"Insufficient data for {symbol}")

        return prices
```

### 3. Application Layer（應用服務）

#### 3.1 Backtest Service (`application/backtest_service.py`)

**職責：**
- 組合 domain 和 infrastructure 層
- 處理多個標的的回測
- 錯誤處理與資料協調

**關鍵邏輯：**
```python
class BacktestService:
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
        1. 從 infrastructure 取得資料
        2. 呼叫 domain 層執行計算
        3. 返回結果
        """
        # 1. Side effect: 取得資料
        prices = self.data_adapter.get_stock_data(symbol, start_date, end_date)

        # 2. Pure function: 執行回測
        if strategy == "lump_sum":
            result = backtest_logic.backtest_lump_sum(prices, amount, symbol, name)
        elif strategy == "dca":
            result = backtest_logic.backtest_dca(prices, amount, symbol, name)

        return result

    def run_multiple_backtests(...) -> tuple[List[BacktestResult], Comparison]:
        """執行多標的回測並比較"""
        results = []
        for symbol in symbols:
            try:
                result = self.run_backtest(...)
                results.append(result)
            except StockDataError:
                # 部分失敗處理
                pass

        comparison = backtest_logic.calculate_comparison(results)
        return results, comparison
```

### 4. API Layer（HTTP 介面）

#### 4.1 Pydantic Schemas (`api/schemas.py`)

**Request/Response 驗證：**
```python
class BacktestRequest(BaseModel):
    stocks: List[str] = Field(..., min_items=1, max_items=10)
    start_date: date
    end_date: date
    strategy: Literal["lump_sum", "dca"]
    investment: InvestmentParamsSchema

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

class BacktestResponse(BaseModel):
    results: List[BacktestResultSchema]
    comparison: ComparisonSchema
```

#### 4.2 FastAPI Routes (`api/routes.py`)

**API 端點：**
```python
@router.post("/backtest", response_model=BacktestResponse)
async def backtest(
    request: BacktestRequest,
    service: BacktestService = Depends(get_backtest_service)
):
    """執行回測"""
    try:
        results, comparison = service.run_multiple_backtests(
            symbols=request.stocks,
            start_date=request.start_date,
            end_date=request.end_date,
            strategy=request.strategy,
            amount=request.investment.amount
        )

        return BacktestResponse(
            results=[convert_to_schema(r) for r in results],
            comparison=convert_to_schema(comparison)
        )

    except StockDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## 測試策略

### 測試金字塔

```
         ┌────────┐
        ╱          ╲       5%  E2E Tests
       ╱────────────╲      (慢、脆弱)
      ╱              ╲
     ╱────────────────╲    15% Integration Tests
    ╱                  ╲   (中等速度)
   ╱────────────────────╲
  ╱                      ╲ 80% Unit Tests
 ╱________________________╲ (快、穩定)
```

### 1. Unit Tests (Domain Layer)

**目標：100% 覆蓋率**

**特點：**
- 最快（純函數，無 I/O）
- 最穩定（無外部依賴）
- 最容易維護

**範例：**
```python
# tests/domain/test_calculations.py

def test_calculate_cagr_returns_correct_value():
    # Given
    initial = 100000
    final = 150000
    years = 3

    # When
    result = calculate_cagr(initial, final, years)

    # Then
    assert abs(result - 0.1447) < 0.001  # ~14.47%

def test_calculate_max_drawdown_with_drawdown():
    # Given
    values = [100, 120, 80, 100]  # Peak: 120, Trough: 80

    # When
    result = calculate_max_drawdown(values)

    # Then
    expected = (80 - 120) / 120  # -33.33%
    assert abs(result - expected) < 0.0001
```

### 2. Integration Tests (Infrastructure Layer)

**目標：80%+ 覆蓋率**

**特點：**
- 測試真實的 API 呼叫
- 需要網路連線
- 可能因為外部服務問題而失敗

**範例：**
```python
# tests/infrastructure/test_yfinance_adapter.py

@pytest.mark.integration
def test_get_stock_data_returns_valid_data():
    # Given
    adapter = YFinanceAdapter()

    # When
    prices = adapter.get_stock_data(
        "AAPL",
        datetime(2024, 1, 1),
        datetime(2024, 6, 30)
    )

    # Then
    assert len(prices) > 100
    assert all(p.close > 0 for p in prices)
    assert all(isinstance(p, StockPrice) for p in prices)
```

### 3. Service Tests (Application Layer)

**目標：90%+ 覆蓋率**

**特點：**
- Mock infrastructure layer
- 測試組合邏輯
- 測試錯誤處理

**範例：**
```python
# tests/application/test_backtest_service.py

def test_run_backtest_calls_adapter(mock_adapter):
    # Given
    service = BacktestService(mock_adapter)

    # When
    service.run_backtest("TEST", start_date, end_date, "lump_sum", 10000)

    # Then
    mock_adapter.get_stock_data.assert_called_once()

def test_run_multiple_backtests_handles_partial_failures(mock_adapter):
    # Given
    mock_adapter.get_stock_data.side_effect = [
        valid_prices,  # 第一個成功
        StockDataError("Failed")  # 第二個失敗
    ]
    service = BacktestService(mock_adapter)

    # When
    results, comparison = service.run_multiple_backtests(
        ["AAPL", "INVALID"],
        start_date, end_date, "lump_sum", 10000
    )

    # Then
    assert len(results) == 1  # 只有一個成功
    assert results[0].symbol == "AAPL"
```

### 4. E2E Tests (API Layer)

**目標：85%+ 覆蓋率**

**特點：**
- 測試完整流程
- 使用 FastAPI TestClient
- 最慢但最接近真實使用情境

**範例：**
```python
# tests/api/test_routes.py

def test_backtest_endpoint_returns_400_for_invalid_dates():
    response = client.post("/api/backtest", json={
        "stocks": ["AAPL"],
        "start_date": "2024-12-31",
        "end_date": "2024-01-01",  # 錯誤：結束早於開始
        "strategy": "lump_sum",
        "investment": {"amount": 10000}
    })

    assert response.status_code == 422  # Pydantic validation error

@pytest.mark.integration
def test_backtest_endpoint_success():
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
    assert len(data["results"]) == 1
```

### 執行測試

```bash
# 執行所有測試
pytest tests/ -v

# 按層級執行
pytest tests/domain/          # Unit tests（最快）
pytest tests/infrastructure/ -m integration  # Integration tests
pytest tests/application/     # Service tests
pytest tests/api/            # E2E tests

# 查看覆蓋率
pytest tests/ --cov=backend --cov-report=html

# 產生 HTML 報告
open htmlcov/index.html

# 跳過 integration tests（CI 環境）
pytest tests/ -m "not integration"
```

---

## 開發工作流程

### TDD 循環

```
1. 寫測試 (Red)
   ↓
2. 寫最簡實作 (Green)
   ↓
3. 重構 (Refactor)
   ↓
4. 重複
```

### 實際範例

**需求：實作 calculate_cagr 函數**

**Step 1: 寫測試（Red）**
```python
def test_calculate_cagr_returns_correct_value():
    result = calculate_cagr(100000, 150000, 3)
    assert abs(result - 0.1447) < 0.001
```

**Step 2: 寫實作（Green）**
```python
def calculate_cagr(initial: float, final: float, years: float) -> float:
    return (final / initial) ** (1 / years) - 1
```

**Step 3: 重構（Refactor）**
```python
def calculate_cagr(initial: float, final: float, years: float) -> float:
    if initial <= 0 or years <= 0:
        raise CalculationError("Invalid input")
    if final == 0:
        return -1.0
    return (final / initial) ** (1 / years) - 1
```

**Step 4: 增加邊界測試**
```python
def test_calculate_cagr_raises_on_invalid_input():
    with pytest.raises(CalculationError):
        calculate_cagr(-100, 150000, 3)

def test_calculate_cagr_handles_complete_loss():
    result = calculate_cagr(100000, 0, 3)
    assert result == -1.0
```

---

## 程式碼品質標準

### 1. Pure Function 檢查清單

**✅ 符合 Pure Function：**
```python
def calculate_cagr(initial: float, final: float, years: float) -> float:
    """相同輸入永遠相同輸出，零 side effect"""
    return (final / initial) ** (1 / years) - 1
```

**❌ 不符合 Pure Function：**
```python
# 錯誤 1: 依賴外部狀態
def get_current_price(symbol: str) -> float:
    return yf.Ticker(symbol).info['price']  # 依賴外部 API

# 錯誤 2: 有 side effect
def log_result(result: BacktestResult) -> None:
    print(result)  # I/O 是 side effect

# 錯誤 3: 修改外部狀態
def update_cache(key: str, value: any) -> None:
    global _cache
    _cache[key] = value  # 修改 global state
```

### 2. Immutability 檢查

**✅ Immutable:**
```python
@dataclass(frozen=True)
class StockPrice:
    date: datetime
    close: float

# 無法修改
price = StockPrice(date=..., close=100)
price.close = 200  # ❌ 會拋出錯誤
```

**❌ Mutable (避免):**
```python
class StockPrice:
    def __init__(self, date, close):
        self.date = date
        self.close = close

# 可以修改（不好）
price = StockPrice(date=..., close=100)
price.close = 200  # ✓ 可以修改，但容易出錯
```

### 3. 型別安全

**✅ 明確型別：**
```python
def backtest_lump_sum(
    prices: List[StockPrice],  # 明確
    initial_amount: float       # 明確
) -> BacktestResult:           # 明確
    ...
```

**❌ 模糊型別（避免）：**
```python
def backtest_lump_sum(
    prices: List[Dict[str, Any]],  # 太模糊
    initial_amount: Any             # 不知道是什麼
) -> Dict:                          # 不知道結構
    ...
```

### 4. 函數大小

**✅ 簡短清楚：**
```python
def calculate_cagr(initial: float, final: float, years: float) -> float:
    """單一職責，10 行以內"""
    if initial <= 0 or years <= 0:
        raise CalculationError("Invalid input")
    if final == 0:
        return -1.0
    return (final / initial) ** (1 / years) - 1
```

**❌ 太長（避免）：**
- 超過 30 行 → 考慮拆分
- 超過 3 層縮排 → 重構

---

## 常見問題與解決方案

### 1. yfinance 資料問題

**問題：台股代碼抓不到資料**
```python
# ❌ 錯誤
prices = adapter.get_stock_data("2330", ...)  # 找不到

# ✅ 正確
prices = adapter.get_stock_data("2330.TW", ...)  # 加上 .TW 後綴
```

**問題：資料點數不足**
```python
# 在 yfinance_adapter.py 中驗證
if len(prices) < 10:
    raise StockDataError(f"Insufficient data: only {len(prices)} days")
```

### 2. 測試問題

**問題：Integration tests 太慢**

**解決：**
```python
# 使用 pytest marker
@pytest.mark.integration
def test_real_api_call():
    ...

# CI 環境跳過
pytest tests/ -m "not integration"
```

**問題：測試資料難以準備**

**解決：使用 pytest fixtures**
```python
@pytest.fixture
def sample_prices():
    return [
        StockPrice(date=datetime(2024, 1, i), close=100.0 + i)
        for i in range(1, 31)
    ]
```

### 3. 型別檢查錯誤

**問題：mypy 報錯**
```bash
# 執行型別檢查
mypy backend/

# 常見錯誤
error: Argument 1 to "backtest_lump_sum" has incompatible type "List[Dict[str, Any]]"; expected "List[StockPrice]"
```

**解決：確保型別一致**
```python
# ❌ 錯誤
prices: List[Dict] = get_prices()
result = backtest_lump_sum(prices, ...)

# ✅ 正確
prices: List[StockPrice] = get_prices()
result = backtest_lump_sum(prices, ...)
```

### 4. CORS 問題

**問題：前端無法呼叫 API**

**解決：在 main.py 設定 CORS**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 開發檢查清單

### Phase 1: 資料結構定義
- [ ] `domain/models.py` - 所有 @dataclass(frozen=True)
- [ ] `api/schemas.py` - 所有 Pydantic models
- [ ] `frontend/src/types/index.ts` - 所有 TypeScript types
- [ ] mypy 檢查通過
- [ ] tsc 檢查通過

### Phase 2: Domain Layer
- [ ] `domain/calculations.py` - 所有財務計算
- [ ] `domain/backtest.py` - 回測邏輯
- [ ] 所有函數都是 pure functions
- [ ] 100% 測試覆蓋率
- [ ] 所有測試通過

### Phase 3: Infrastructure Layer
- [ ] `infrastructure/yfinance_adapter.py` 實作
- [ ] 所有 side effects 隔離
- [ ] Integration tests 通過
- [ ] 80%+ 覆蓋率

### Phase 4: Application Layer
- [ ] `application/backtest_service.py` 實作
- [ ] 正確組合 domain + infrastructure
- [ ] 錯誤處理完善
- [ ] 90%+ 覆蓋率

### Phase 5: API Layer
- [ ] `api/routes.py` - 所有端點
- [ ] `api/dependencies.py` - 依賴注入
- [ ] `main.py` - FastAPI 設定
- [ ] Swagger UI 可訪問
- [ ] E2E tests 通過

### Phase 6: Frontend
- [ ] Vite + React + TypeScript 設置
- [ ] API client 實作
- [ ] React Query 整合
- [ ] 主要元件實作
- [ ] 響應式設計

### Phase 7: 品質保證
- [ ] 所有測試通過
- [ ] 覆蓋率 > 90%
- [ ] mypy 無錯誤
- [ ] tsc 無錯誤
- [ ] eslint 無錯誤
- [ ] 文件完整

---

## 參考資源

### 官方文件
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [yfinance Documentation](https://pypi.org/project/yfinance/)
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [TanStack Query](https://tanstack.com/query/latest)
- [Recharts](https://recharts.org/)

### 架構設計
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Functional Core, Imperative Shell](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)

### 測試
- [Pytest Documentation](https://docs.pytest.org/)
- [Test-Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [Testing Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

### 財務知識
- [Investopedia - CAGR](https://www.investopedia.com/terms/c/cagr.asp)
- [Investopedia - Sharpe Ratio](https://www.investopedia.com/terms/s/sharperatio.asp)
- [Investopedia - Maximum Drawdown](https://www.investopedia.com/terms/m/maximum-drawdown-mdd.asp)

---

## 結語

這份技術文件定義了 BackTester 專案的完整架構和實作細節。

**關鍵要點：**

1. **Clean Architecture**：分層清楚，職責分明
2. **Pure Functions 優先**：Domain layer 100% pure，易於測試
3. **型別安全**：Backend (Pydantic) + Frontend (TypeScript)
4. **TDD 流程**：測試驅動開發，品質有保證
5. **測試金字塔**：80% unit tests，15% integration，5% E2E

**與傳統架構的差異：**

| 傳統架構 | Clean Architecture |
|---------|-------------------|
| api/services/utils | domain/infrastructure/application/api |
| Dict[str, Any] | @dataclass(frozen=True) + TypeScript |
| 測試為輔 | TDD，100% 覆蓋 |
| jQuery | React + TypeScript |
| 扁平結構 | 分層架構 |

**這個架構的優勢：**
- ✅ 容易測試（pure functions）
- ✅ 容易理解（職責分明）
- ✅ 容易維護（分層清楚）
- ✅ 容易擴展（新增功能不影響核心）
- ✅ 型別安全（減少 runtime 錯誤）

---

**最後更新：2025-01-XX**
**版本：2.0**

*"Show me your data structures, and I won't need to see your code." - Linus Torvalds*
