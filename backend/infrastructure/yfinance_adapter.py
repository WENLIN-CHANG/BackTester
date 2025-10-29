"""
yfinance Adapter - Isolate all external API calls

This layer contains all side effects:
- API calls to Yahoo Finance
- Data transformation from pandas to domain models
- Error handling for external services
- Caching to avoid rate limiting
"""

from datetime import datetime
from typing import List, Optional
import yfinance as yf
import requests
from domain.models import StockPrice
from infrastructure.cache import StockCache


class StockDataError(Exception):
    """Raised when stock data cannot be fetched or is invalid"""

    pass


class YFinanceAdapter:
    """Adapter for Yahoo Finance API using yfinance library with caching"""

    def __init__(self, cache_enabled: bool = True, cache_ttl_hours: int = 24):
        """
        Initialize adapter

        Args:
            cache_enabled: Whether to enable caching (default: True)
            cache_ttl_hours: Cache time-to-live in hours (default: 24)
        """
        self.cache_enabled = cache_enabled
        if cache_enabled:
            self.cache = StockCache(ttl_hours=cache_ttl_hours)
        else:
            self.cache = None

        # Setup requests session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def _fetch_with_requests(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Optional[tuple[List[StockPrice], str]]:
        """
        Fetch data directly using requests library (bypass yfinance)

        This is a workaround for yfinance library issues.

        Args:
            symbol: Stock ticker symbol
            start_date: Start date
            end_date: End date

        Returns:
            Tuple of (prices, stock_name) or None if failed
        """
        try:
            url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + symbol
            params = {
                'period1': int(start_date.timestamp()),
                'period2': int(end_date.timestamp()),
                'interval': '1d'
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            result = data['chart']['result'][0]

            # Extract stock metadata
            meta = result.get('meta', {})
            stock_name = meta.get('longName') or meta.get('shortName') or symbol

            # Extract price data
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            closes = quotes['close']

            # Convert to StockPrice objects
            prices = []
            for i, timestamp in enumerate(timestamps):
                if closes[i] is not None:  # Skip days with no data
                    prices.append(StockPrice(
                        date=datetime.fromtimestamp(timestamp),
                        close=float(closes[i])
                    ))

            if len(prices) < 10:
                return None

            return prices, stock_name

        except Exception:
            # If requests method fails, return None (will fallback to yfinance)
            return None

    def get_stock_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> tuple[List[StockPrice], str]:
        """
        Fetch stock price data from Yahoo Finance (with caching)

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL", "2330.TW")
            start_date: Start date for historical data
            end_date: End date for historical data

        Returns:
            Tuple of (prices, stock_name):
            - prices: List of StockPrice objects
            - stock_name: Full name of the stock

        Raises:
            StockDataError: If data cannot be fetched or is invalid
        """
        # Try to get from cache first
        if self.cache_enabled and self.cache:
            cached_data = self.cache.get(symbol, start_date, end_date)
            if cached_data is not None:
                # Reconstruct StockPrice objects from cached data
                prices = [
                    StockPrice(
                        date=datetime.fromisoformat(p["date"]), close=p["close"]
                    )
                    for p in cached_data["prices"]
                ]
                return prices, cached_data["stock_name"]

        # Try to fetch using requests first (more reliable)
        result = self._fetch_with_requests(symbol, start_date, end_date)
        if result is not None:
            prices, stock_name = result

            # Store in cache before returning
            if self.cache_enabled and self.cache:
                cache_data = {
                    "prices": [
                        {"date": p.date.isoformat(), "close": p.close} for p in prices
                    ],
                    "stock_name": stock_name,
                }
                self.cache.set(symbol, start_date, end_date, cache_data)

            return prices, stock_name

        # Fallback to yfinance if requests method fails
        try:
            # Fetch data from Yahoo Finance
            ticker = yf.Ticker(symbol)

            # Get historical prices
            df = ticker.history(start=start_date, end=end_date)

            # Check if data is empty
            if df.empty:
                raise StockDataError(
                    f"No data available for {symbol} between {start_date.date()} and {end_date.date()}"
                )

            # Get stock name
            try:
                stock_info = ticker.info
                stock_name = stock_info.get("longName") or stock_info.get(
                    "shortName"
                ) or symbol
            except Exception:
                # If info fetch fails, just use symbol
                stock_name = symbol

            # Convert to domain models
            prices: List[StockPrice] = []
            for date, row in df.iterrows():
                try:
                    price = StockPrice(
                        date=date.to_pydatetime(),
                        close=float(row["Close"]),
                    )
                    prices.append(price)
                except (KeyError, ValueError, TypeError) as e:
                    # Skip invalid rows
                    continue

            # Validate we have sufficient data
            if len(prices) < 10:
                raise StockDataError(
                    f"Insufficient data for {symbol}: only {len(prices)} trading days found"
                )

            # Store in cache before returning
            if self.cache_enabled and self.cache:
                cache_data = {
                    "prices": [
                        {"date": p.date.isoformat(), "close": p.close} for p in prices
                    ],
                    "stock_name": stock_name,
                }
                self.cache.set(symbol, start_date, end_date, cache_data)

            return prices, stock_name

        except StockDataError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            # Catch all other errors and wrap them
            raise StockDataError(
                f"Failed to fetch data for {symbol}: {str(e)}"
            ) from e

    def get_stock_name(self, symbol: str) -> str:
        """
        Get full stock name from symbol

        Args:
            symbol: Stock ticker symbol

        Returns:
            Full stock name

        Raises:
            StockDataError: If stock info cannot be fetched
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info.get("longName") or info.get("shortName") or symbol
        except Exception as e:
            raise StockDataError(
                f"Failed to fetch stock name for {symbol}: {str(e)}"
            ) from e
