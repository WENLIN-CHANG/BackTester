"""
yfinance Adapter - Isolate all external API calls

This layer contains all side effects:
- API calls to Yahoo Finance
- Data transformation from pandas to domain models
- Error handling for external services
"""

from datetime import datetime
from typing import List
import yfinance as yf
from domain.models import StockPrice


class StockDataError(Exception):
    """Raised when stock data cannot be fetched or is invalid"""

    pass


class YFinanceAdapter:
    """Adapter for Yahoo Finance API using yfinance library"""

    def get_stock_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> tuple[List[StockPrice], str]:
        """
        Fetch stock price data from Yahoo Finance

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
