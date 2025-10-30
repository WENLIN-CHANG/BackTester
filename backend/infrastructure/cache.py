"""
Simple File-Based Cache for Stock Data

Caches Yahoo Finance API responses to avoid rate limiting.
Uses JSON files stored in .cache/ directory with 24-hour TTL.
"""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, cast


class StockCache:
    """Simple file-based cache for stock data"""

    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 24):
        """
        Initialize cache

        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live in hours (default: 24)
        """
        self.cache_dir = Path(cache_dir)
        self.ttl = timedelta(hours=ttl_hours)

        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_key(self, symbol: str, start_date: str, end_date: str) -> str:
        """
        Generate cache key from parameters

        Args:
            symbol: Stock symbol
            start_date: Start date string
            end_date: End date string

        Returns:
            Cache key (hashed)
        """
        key_str = f"{symbol}_{start_date}_{end_date}"
        # Use hash to avoid filesystem issues with special characters
        # MD5 is used for cache key generation, not security
        return hashlib.md5(key_str.encode(), usedforsecurity=False).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get full path to cache file"""
        return self.cache_dir / f"{cache_key}.json"

    def get(self, symbol: str, start_date: datetime, end_date: datetime) -> dict[str, Any] | None:
        """
        Retrieve cached data if available and not expired

        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date

        Returns:
            Cached data dict or None if not found/expired
        """
        try:
            cache_key = self._get_cache_key(
                symbol, start_date.date().isoformat(), end_date.date().isoformat()
            )
            cache_path = self._get_cache_path(cache_key)

            # Check if cache file exists
            if not cache_path.exists():
                return None

            # Read cache file
            with open(cache_path, encoding="utf-8") as f:
                cached_data = json.load(f)

            # Check expiration
            cached_time = datetime.fromisoformat(cached_data["cached_at"])
            if datetime.now() - cached_time > self.ttl:
                # Cache expired, delete file
                cache_path.unlink()
                return None

            return cast(dict[str, Any], cached_data["data"])

        except Exception:
            # If any error occurs, treat as cache miss
            return None

    def set(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        data: dict[str, Any],
    ) -> None:
        """
        Store data in cache

        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
            data: Data to cache
        """
        try:
            cache_key = self._get_cache_key(
                symbol, start_date.date().isoformat(), end_date.date().isoformat()
            )
            cache_path = self._get_cache_path(cache_key)

            # Prepare cache entry
            cache_entry = {"cached_at": datetime.now().isoformat(), "data": data}

            # Write to file
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_entry, f, ensure_ascii=False, indent=2)

        except Exception:
            # Silently fail - caching is optional
            pass

    def clear_expired(self) -> int:
        """
        Remove all expired cache files

        Returns:
            Number of files removed
        """
        removed = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, encoding="utf-8") as f:
                        cached_data = json.load(f)

                    cached_time = datetime.fromisoformat(cached_data["cached_at"])
                    if datetime.now() - cached_time > self.ttl:
                        cache_file.unlink()
                        removed += 1
                except Exception:
                    # If file is corrupted, delete it
                    cache_file.unlink()
                    removed += 1
        except Exception:
            pass

        return removed

    def clear_all(self) -> int:
        """
        Remove all cache files

        Returns:
            Number of files removed
        """
        removed = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                removed += 1
        except Exception:
            pass

        return removed
