"""
PROFITRC — Centralized Data Cache
Downloads ticker data once per pipeline run and shares across all modules.
"""
import logging
import time
from datetime import date

import pandas as pd
import yfinance as yf

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

logger = logging.getLogger(__name__)


class TickerData:
    """Container for all pre-fetched data for a single ticker."""

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.daily: pd.DataFrame = pd.DataFrame()   # period=6mo, interval=1d
        self.hourly: pd.DataFrame = pd.DataFrame()  # period=60d, interval=1h
        self.info: dict = {}
        self.float_shares: int = 0
        self.rvol: float = 0.0
        self.news_count_48h: int = 0
        self.news_items: list = []
        self._loaded = False

    def load(self) -> "TickerData":
        """Download all data in a single batch."""
        if self._loaded:
            return self

        ticker_obj = yf.Ticker(self.ticker)

        try:
            self.daily = ticker_obj.history(period="6mo", interval="1d", auto_adjust=True)
            if self.daily is None:
                self.daily = pd.DataFrame()
            elif isinstance(self.daily.columns, pd.MultiIndex):
                self.daily.columns = self.daily.columns.get_level_values(0)
            time.sleep(config.REQUEST_DELAY)
        except Exception as e:
            logger.warning("daily fetch(%s): %s", self.ticker, e)
            self.daily = pd.DataFrame()

        try:
            self.hourly = ticker_obj.history(period="60d", interval="1h", auto_adjust=True)
            if self.hourly is None:
                self.hourly = pd.DataFrame()
            elif isinstance(self.hourly.columns, pd.MultiIndex):
                self.hourly.columns = self.hourly.columns.get_level_values(0)
            time.sleep(config.REQUEST_DELAY)
        except Exception as e:
            logger.warning("hourly fetch(%s): %s", self.ticker, e)
            self.hourly = pd.DataFrame()

        try:
            self.info = ticker_obj.info or {}
            self.float_shares = int(
                self.info.get("floatShares") or self.info.get("sharesOutstanding") or 0
            )
            time.sleep(config.REQUEST_DELAY)
        except Exception as e:
            logger.warning("info fetch(%s): %s", self.ticker, e)

        # Compute RVOL from daily data (no extra call)
        if not self.daily.empty and len(self.daily) > config.RVOL_WINDOW:
            avg_vol = float(self.daily["Volume"].iloc[-(config.RVOL_WINDOW + 1):-1].mean())
            today_vol = float(self.daily["Volume"].iloc[-1])
            self.rvol = round(today_vol / avg_vol, 2) if avg_vol > 0 else 0.0

        # News items for sentiment polarity analysis
        try:
            import time as _time
            news = ticker_obj.news or []
            cutoff = _time.time() - 48 * 3600
            self.news_items = [n for n in news if n.get("providerPublishTime", 0) >= cutoff]
            self.news_count_48h = len(self.news_items)
        except Exception:
            self.news_items = []
            self.news_count_48h = 0

        self._loaded = True
        logger.info(
            "TickerData(%s): daily=%d rows, hourly=%d rows, float=%dM, rvol=%.1fx, news=%d",
            self.ticker, len(self.daily), len(self.hourly),
            self.float_shares // 1_000_000, self.rvol, self.news_count_48h,
        )
        return self


class DataCache:
    """Session-scoped cache: one TickerData per ticker per pipeline run."""

    def __init__(self):
        self._cache: dict[str, TickerData] = {}

    def get(self, ticker: str) -> TickerData:
        """Returns loaded TickerData, fetching if not already cached."""
        key = ticker.upper()
        if key not in self._cache:
            self._cache[key] = TickerData(key).load()
        return self._cache[key]

    def clear(self):
        self._cache.clear()
