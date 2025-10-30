# BackTester - 投資回測系統

![CI](https://github.com/YOUR_USERNAME/BackTester/workflows/CI/badge.svg)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 用數據說話，驗證你的投資理論

## 專案簡介

你是否常聽到這些說法？
- 「投資台積電好」
- 「0050 比較穩」
- 「QQQ 才是王道」

**但誰說的比較準呢？**

BackTester 是一個投資回測系統，讓你可以用歷史數據驗證不同投資標的的實際表現。
只需選擇標的、設定投資策略，就能看到如果你在過去 X 年投資，現在會有多少報酬。

## 功能特色

- **多標的比較**：同時回測多個股票或 ETF，一目了然誰表現更好
- **靈活策略**：支援單筆投資、定期定額等不同投資方式
- **完整指標**：提供報酬率、最大回撤、夏普比率等專業財務指標
- **視覺化呈現**：圖表化顯示投資組合價值變化與績效比較
- **全球市場**：支援美股、台股等主要市場
- **型別安全**：Backend (Pydantic) + Frontend (TypeScript) 雙重型別保護
- **高測試覆蓋率**：核心業務邏輯 100% 測試覆蓋

## 技術架構

### Backend (Python + FastAPI)

- **框架**: FastAPI + Pydantic（型別安全、自動文件生成）
- **架構模式**: Clean Architecture（分層設計）
  - `domain/`: Pure functions（零依賴，100% 可測試）
  - `infrastructure/`: Side effects（yfinance, cache）
  - `application/`: 組合層（業務服務）
  - `api/`: HTTP 層（RESTful API）
- **資料來源**: yfinance（隔離在 infrastructure 層）
- **資料處理**: pandas, numpy（僅用於計算層）
- **測試框架**: pytest + coverage（目標 90%+ 覆蓋率）

### Frontend (React + TypeScript)

- **框架**: React 18 + TypeScript（型別安全）
- **狀態管理**: TanStack Query (React Query)（自動處理 loading/error/cache）
- **樣式系統**: Tailwind CSS（實用優先）
- **圖表庫**: Recharts（React 原生圖表）
- **建置工具**: Vite（極速開發體驗）

### 架構特點

```
使用者輸入
    ↓
API Layer (FastAPI routes)
    ↓
Application Layer (業務服務)
    ↓
    ├─→ Infrastructure Layer (取得股票資料) [Side Effect]
    └─→ Domain Layer (回測計算) [Pure Function]
            ↓
        返回結果
```

**為什麼選擇這個架構？**

1. **Pure Functions 優先**：核心業務邏輯（回測計算、財務指標）都是 pure function，容易測試、容易理解
2. **分層隔離**：Side effects（API 呼叫）與業務邏輯完全分離
3. **型別安全**：Backend (Pydantic) + Frontend (TypeScript) 消除大部分 runtime 錯誤
4. **可測試性**：分層設計讓每一層都能獨立測試
5. **可維護性**：清晰的職責劃分，易於擴展和修改

## 專案結構

```
BackTester/
│
├── backend/
│   ├── domain/              # 核心業務邏輯 (Pure Functions, 零依賴)
│   │   ├── __init__.py
│   │   ├── models.py       # 不可變資料結構 (@dataclass(frozen=True))
│   │   ├── calculations.py # 財務計算 (CAGR, Sharpe, MDD, etc.)
│   │   └── backtest.py     # 回測邏輯 (單筆/定期定額)
│   │
│   ├── infrastructure/     # 外部依賴 (Side Effects)
│   │   ├── __init__.py
│   │   ├── yfinance_adapter.py  # Yahoo Finance API 封裝
│   │   └── cache.py        # 快取機制
│   │
│   ├── application/        # 應用服務層 (組合 domain + infrastructure)
│   │   ├── __init__.py
│   │   └── backtest_service.py
│   │
│   ├── api/               # HTTP 介面層
│   │   ├── __init__.py
│   │   ├── routes.py      # API 路由定義
│   │   ├── schemas.py     # Request/Response Pydantic models
│   │   └── dependencies.py # 依賴注入
│   │
│   ├── tests/             # 分層測試
│   │   ├── domain/       # Unit tests (最快，不需要 mock)
│   │   ├── infrastructure/ # Integration tests (真實 API 呼叫)
│   │   ├── application/  # Service tests (mock infrastructure)
│   │   └── api/          # E2E tests (完整流程)
│   │
│   ├── main.py           # FastAPI 應用進入點
│   └── requirements.txt  # Python 依賴套件
│
├── frontend/
│   ├── src/
│   │   ├── types/        # TypeScript 型別定義
│   │   ├── api/          # API client (axios)
│   │   ├── hooks/        # React Query hooks
│   │   ├── components/   # React 元件
│   │   │   ├── StockSelector.tsx
│   │   │   ├── BacktestForm.tsx
│   │   │   ├── ResultsTable.tsx
│   │   │   └── PerformanceChart.tsx
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── PLAN.md              # 完整實作計畫
├── CLAUDE.md            # 技術文件與架構說明
└── README.md            # 本文件
```

## 開發流程

本專案使用 **pre-commit hooks** 和 **GitHub Actions CI** 確保程式碼品質。

### Pre-commit Hooks（本地防護）

安裝後，每次 `git commit` 都會自動執行以下檢查：

1. **格式化**：自動修正程式碼格式（ruff format, prettier）
2. **Lint**：檢查程式碼風格（ruff, eslint）
3. **型別檢查**：mypy + tsc（確保型別安全）
4. **安全掃描**：bandit（檢查常見安全漏洞）
5. **快速測試**：pytest unit tests（只跑 domain layer）

**安裝步驟：**

```bash
# Backend
cd backend
pip install -r requirements.txt
pre-commit install

# Frontend
cd frontend
npm install

# 測試 pre-commit（手動執行）
cd ..
pre-commit run --all-files
```

**首次 commit 會較慢**（需下載 hooks），之後只檢查變更的檔案（5-10 秒）。

### GitHub Actions CI（遠端防護）

推送程式碼或建立 PR 時，會自動執行完整的 CI pipeline：

| Job | 內容 | 時間 |
|-----|------|------|
| **lint-python** | ruff check | ~30s |
| **lint-frontend** | eslint + prettier | ~30s |
| **security** | bandit 安全掃描 | ~45s |
| **typecheck** | mypy + tsc --noEmit | ~45s |
| **test-backend** | pytest 完整測試 | ~1-2m |
| **test-frontend** | vitest | ~30s |
| **build-frontend** | npm run build | ~45s |

所有 jobs **平行執行**，總時間約 2-3 分鐘。

### 開發建議流程

```bash
# 1. 建立功能分支
git checkout -b feature/your-feature

# 2. 開發（pre-commit 會在 commit 時自動檢查）
git add .
git commit -m "feat: add new feature"
# → 自動執行 pre-commit hooks
# → 如果格式有問題會自動修正並要求重新 commit

# 3. 推送到遠端
git push origin feature/your-feature

# 4. 建立 Pull Request
# → GitHub Actions 會自動執行完整 CI
# → 所有檢查通過後才能 merge

# 5. Merge 到 main
# → 再次執行 CI 確保 main 分支品質
```

### 繞過 Pre-commit（不建議）

```bash
# 緊急情況下可以跳過 pre-commit
git commit --no-verify -m "emergency fix"

# 但 CI 還是會執行，無法繞過
```

---

## 快速開始

### 環境需求

- **Python**: 3.10+
- **Node.js**: 18+
- **現代瀏覽器**: Chrome, Firefox, Safari, Edge

### Backend 安裝與啟動

```bash
# 1. 進入 backend 目錄
cd backend

# 2. 建立虛擬環境
python -m venv venv

# 3. 啟動虛擬環境
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 4. 安裝依賴套件
pip install -r requirements.txt

# 5. 執行測試（確保一切正常）
pytest tests/ --cov=backend --cov-report=term-missing

# 6. 啟動開發伺服器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend 服務現在運行在：**
- API 服務：http://localhost:8000
- 自動文件：http://localhost:8000/docs（Swagger UI）
- 替代文件：http://localhost:8000/redoc

### Frontend 安裝與啟動

```bash
# 1. 進入 frontend 目錄
cd frontend

# 2. 安裝依賴套件
npm install

# 3. 啟動開發伺服器
npm run dev
```

**Frontend 應用現在運行在：**
- 前端應用：http://localhost:5173

### 開發模式

**Backend 熱重載：**
- `--reload` 參數讓 uvicorn 自動偵測檔案變更並重啟

**Frontend 熱更新：**
- Vite 提供極速的 HMR（Hot Module Replacement）

## 使用方式

### 基本流程

1. **選擇投資標的**
   - 在搜尋框輸入股票代碼或名稱
   - 或點擊快速新增按鈕（台積電、0050、QQQ）
   - 可同時選擇多個標的進行比較（最多 10 個）

2. **設定回測參數**
   - 選擇起始日期與結束日期（建議至少 1 年）
   - 選擇投資策略：
     - **單筆投資**：一次性投入所有資金
     - **定期定額**：每月固定金額投入（每月第一個交易日）
   - 輸入投資金額（必須大於 0）

3. **執行回測**
   - 點擊「開始回測」按鈕
   - 系統會自動計算並顯示結果
   - Loading 動畫顯示處理進度

4. **查看結果**
   - **比較表格**：各標的詳細指標一覽
   - **價值走勢圖**：投資組合價值隨時間變化
   - **報酬率比較圖**：直觀比較各標的表現
   - **風險分析**：波動率、最大回撤、夏普比率

### 股票代碼格式

- **台股**：需加上 `.TW` 或 `.TWO` 後綴
  - 台積電：`2330.TW`
  - 0050：`0050.TW`
  - 聯發科：`2454.TW`
  - 台灣大：`3045.TW`

- **美股**：直接使用股票代碼
  - 蘋果：`AAPL`
  - 特斯拉：`TSLA`
  - QQQ：`QQQ`（那斯達克 100 ETF）
  - SPY：`SPY`（S&P 500 ETF）
  - VOO：`VOO`（S&P 500 ETF）

## 使用範例

### 範例 1：比較台灣三大 ETF

**設定**：
- 標的：`0050.TW`、`0056.TW`、`006208.TW`
- 期間：2018-01-01 至 2024-12-31（7 年）
- 策略：每月定期定額 10,000 元

**可能結果**：
- **0050**：總投入 84 萬，最終價值 120 萬（+42.8%，年化 5.2%）
- **0056**：總投入 84 萬，最終價值 105 萬（+25.0%，年化 3.3%）
- **006208**：總投入 84 萬，最終價值 98 萬（+16.7%，年化 2.3%）

**結論**：0050（台灣 50）長期表現最佳

### 範例 2：台積電 vs QQQ

**設定**：
- 標的：`2330.TW`、`QQQ`
- 期間：2020-01-01 至 2024-12-31（5 年）
- 策略：單筆投資 100,000 元

**可能結果**：
- **台積電**：最終價值 185,000 元（+85%，年化 13.1%）
- **QQQ**：最終價值 220,000 元（+120%，年化 17.1%）

**風險分析**：
- 台積電波動率：30.5%，最大回撤：-35.2%
- QQQ 波動率：25.8%，最大回撤：-28.5%

**結論**：QQQ 報酬較高，但台積電風險也較高

### 範例 3：分散投資組合

**設定**：
- 標的：`SPY`、`QQQ`、`VTI`、`BND`
- 期間：2015-01-01 至 2024-12-31（10 年）
- 策略：每月定期定額 5,000 元（每支）

**用途**：比較不同資產配置的長期表現

## API 文件

### 自動生成文檔

FastAPI 會自動生成互動式 API 文件：

- **Swagger UI**: http://localhost:8000/docs
  - 可直接在瀏覽器測試 API
  - 查看請求/回應格式
  - 自動型別驗證

- **ReDoc**: http://localhost:8000/redoc
  - 更適合閱讀的文檔格式
  - 完整的 schema 定義

### 主要端點

```
GET  /api/stocks/search?q={query}     # 搜尋股票
POST /api/backtest                     # 執行回測
GET  /api/stocks/{symbol}              # 取得股票資訊
GET  /health                           # 健康檢查
```

### 範例請求

```bash
# 執行回測
curl -X POST "http://localhost:8000/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "stocks": ["2330.TW", "QQQ"],
    "start_date": "2020-01-01",
    "end_date": "2024-12-31",
    "strategy": "dca",
    "investment": {
      "amount": 10000,
      "frequency": "monthly"
    }
  }'
```

更多細節請參考 [PLAN.md](PLAN.md) 和 [CLAUDE.md](CLAUDE.md)。

## 財務指標說明

| 指標 | 說明 | 計算公式 | 解讀 |
|------|------|----------|------|
| **總報酬率** | 投資期間的總收益百分比 | `(最終價值 - 總投入) / 總投入 × 100%` | 越高越好 |
| **年化報酬率 (CAGR)** | 複合年均成長率 | `(final/initial)^(1/years) - 1` | 反映長期平均報酬 |
| **最大回撤 (MDD)** | 從最高點到最低點的最大跌幅 | `min((current - peak) / peak)` | 數值越小（負越多）風險越高 |
| **波動率** | 價格波動程度（年化標準差） | `std(daily_returns) × √252` | 數值越大風險越高 |
| **夏普比率** | 風險調整後報酬 | `(return - risk_free_rate) / volatility` | > 1 為佳，越高越好 |

**夏普比率解讀：**
- < 0：報酬低於無風險利率，不值得投資
- 0-1：報酬勉強高於無風險利率
- 1-2：良好的風險調整後報酬
- 2-3：優秀的投資標的
- \> 3：極佳（但罕見）

## 注意事項

### 1. 資料來源

- 本系統使用 **Yahoo Finance** 數據
- 資料可能有延遲或不準確
- 台股資料需確保使用 `.TW` 或 `.TWO` 後綴
- 並非所有股票都有完整歷史資料

### 2. 回測限制

- **歷史績效不代表未來表現**（這很重要！）
- 未考慮交易成本（手續費、稅金）
- 未考慮滑價（實際成交價可能與收盤價不同）
- 未考慮匯率變動（跨國投資）
- 未考慮股息配息（可能影響報酬率）

### 3. 使用建議

- 回測期間建議**至少 1 年**以上（最好 3-5 年）
- 定期定額需至少 3 個月才有統計意義
- 可搭配不同策略多次測試
- 結果僅供**參考**，不構成投資建議
- 投資前請諮詢專業財務顧問

### 4. 技術限制

- 同時回測標的上限：10 個
- 資料範圍：取決於 Yahoo Finance 提供的資料
- API 速率限制：避免短時間大量請求

## 常見問題

**Q: 為什麼找不到我的股票？**

A: 請確認：
1. 股票代碼格式正確（台股需加 `.TW` 或 `.TWO`）
2. 該股票在 Yahoo Finance 有資料
3. 嘗試使用完整股票代碼
4. 某些較小型股票可能無資料

**Q: 定期定額是在每月哪一天投入？**

A: 系統使用**每月第一個交易日**的收盤價計算購買。這是標準做法，因為：
- 大部分定期定額實際上是月初扣款
- 簡化計算邏輯
- 容易重現結果

**Q: 可以回測多久以前的數據？**

A: 取決於 Yahoo Finance 提供的歷史數據範圍：
- 美股通常可回測 20+ 年
- 台股通常可回測 10-15 年
- ETF 取決於成立時間

**Q: 計算結果為何與實際投資有差異？**

A: 可能原因：
1. 回測未計入交易手續費、稅金
2. 未考慮配息再投入
3. 使用收盤價，實際可能無法買到該價格
4. 資料來源可能有誤差
5. 時間點選擇不同

**Q: 如何提高測試覆蓋率？**

A: 本專案採用 TDD（測試驅動開發）：
```bash
# 執行測試並查看覆蓋率
pytest tests/ --cov=backend --cov-report=html

# 開啟 HTML 報告
open htmlcov/index.html
```

**Q: 前端如何連接到 Backend？**

A: 預設配置：
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- CORS 已設定允許 localhost

如需修改，請編輯：
- Backend: `main.py` 的 CORS 設定
- Frontend: `src/api/client.ts` 的 `baseURL`

## 開發文件

詳細的開發文件請參考：

- **[PLAN.md](PLAN.md)**：完整的實作計畫、階段任務、時程規劃
- **[CLAUDE.md](CLAUDE.md)**：技術細節、架構設計、開發指引

## 測試與品質保證

### Backend 測試

```bash
# 執行所有測試
pytest tests/

# 執行特定層級測試
pytest tests/domain/          # 最快（pure functions）
pytest tests/infrastructure/  # 需要網路
pytest tests/application/
pytest tests/api/

# 查看覆蓋率
pytest tests/ --cov=backend --cov-report=term-missing

# 產生 HTML 覆蓋率報告
pytest tests/ --cov=backend --cov-report=html
```

### Frontend 測試

```bash
# 執行測試
npm run test

# 查看覆蓋率
npm run test -- --coverage

# 型別檢查
npm run type-check
```

### 程式碼品質

```bash
# Python linting & formatting (使用 ruff 取代 black + flake8)
cd backend
ruff check .           # 檢查程式碼風格
ruff format .          # 自動格式化
mypy .                 # 型別檢查
bandit -c .bandit -r . # 安全掃描

# TypeScript linting & formatting
cd frontend
npm run lint           # ESLint 檢查
npx prettier --check "src/**/*.{ts,tsx,css,json}"  # 格式檢查
npx tsc --noEmit       # 型別檢查

# 或使用 pre-commit 一次執行所有檢查
pre-commit run --all-files
```

## 部署建議

### 開發環境

如上述「快速開始」章節。

### 生產環境

**Backend:**
```bash
# 使用 Gunicorn + Uvicorn workers
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

**Frontend:**
```bash
# 建置生產版本
npm run build

# 產出在 dist/ 目錄
# 使用 Nginx 或其他靜態伺服器提供服務
```

**環境變數:**
```env
# .env
CORS_ORIGINS=https://yourdomain.com
CACHE_EXPIRY=3600
LOG_LEVEL=INFO
```

## 未來規劃

### Phase 2 功能
- [ ] 配息再投入選項
- [ ] 支援加密貨幣回測
- [ ] 價值平均法策略
- [ ] 風險指標儀表板
- [ ] 匯出 PDF 報告

### Phase 3 功能
- [ ] 使用者帳號系統
- [ ] 儲存回測歷史記錄
- [ ] 分享回測結果（產生連結）
- [ ] 投資組合追蹤（監控實際投資）
- [ ] Email 通知（價格提醒）

### Phase 4 功能
- [ ] 投資組合優化（效率前緣）
- [ ] 自動再平衡策略
- [ ] 機器學習預測（僅供參考）
- [ ] 社群分享與討論功能
- [ ] 多語言支援

## 貢獻指南

歡迎提出 Issue 或 Pull Request！

**開發前請：**
1. 閱讀 [CLAUDE.md](CLAUDE.md) 了解專案架構
2. 確保所有測試通過
3. 遵循 Clean Architecture 原則
4. Domain layer 必須是 pure functions
5. 新增功能必須包含測試

**提交 PR 前檢查清單：**
- [ ] 所有測試通過（`pytest` + `npm test`）
- [ ] 測試覆蓋率 > 90%
- [ ] 無 linting 錯誤
- [ ] 更新相關文件
- [ ] Commit message 清楚描述變更

## 授權

本專案採用 **MIT** 授權條款。

## 免責聲明

本系統提供的回測結果僅供**教育與研究用途**，不構成任何投資建議。

**重要提醒：**
- 投資有風險，過去績效不代表未來表現
- 使用者應自行評估投資風險
- 建議諮詢專業財務顧問
- 本系統開發者不對任何投資損失負責
