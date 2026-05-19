"""
PROFITRC — LAYER 0: Regime Gate
Determines market regime before any scan is allowed to proceed.
Output: "TRADE" | "SELECTIVE" | "CAUTION" | "NO_TRADE"
"""

import logging
import time
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import yfinance as yf

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

logger = logging.getLogger(__name__)


class RegimeGate:
    """
    Scores 4 macro indicators (+1 / 0 / -1 each) and maps the sum to a regime.

    Score  3–4  → TRADE       (full sizing allowed)
    Score  1–2  → SELECTIVE   (TIER 1 only, reduced sizing)
    Score -1–0  → CAUTION     (scouting only, no entries)
    Score < -1  → NO_TRADE    (cash, system standby)
    """

    def __init__(self):
        self._cache: dict = {}   # lightweight in-process cache keyed by ticker+date

    # ── data helpers ─────────────────────────────────────────────────────────

    def _fetch(self, ticker: str, period: str = "3mo") -> pd.DataFrame:
        key = f"{ticker}_{period}_{datetime.utcnow().strftime('%Y-%m-%d')}"
        if key in self._cache:
            return self._cache[key]
        try:
            df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
            if df.empty:
                logger.warning("No data returned for %s", ticker)
                return pd.DataFrame()
            # Flatten MultiIndex columns if present (yfinance ≥ 0.2.40)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            self._cache[key] = df
            time.sleep(config.REQUEST_DELAY)
        except Exception as exc:
            logger.error("Failed to fetch %s: %s", ticker, exc)
            return pd.DataFrame()
        return df

    # ── individual indicator scores ───────────────────────────────────────────

    def get_vix_score(self) -> tuple[int, dict]:
        """
        +1  VIX < VIX_BULLISH (18) AND 3-day trend is falling
         0  VIX between thresholds or stable
        -1  VIX > VIX_BEARISH (25) OR 3-day trend is rising
        """
        df = self._fetch(config.TICKER_VIX)
        if df.empty:
            return 0, {"error": "no data", "value": None}

        latest = float(df["Close"].iloc[-1])
        delta_3d = float(df["Close"].iloc[-1] - df["Close"].iloc[-config.VIX_TREND_WINDOW])

        if latest > config.VIX_BEARISH or delta_3d > config.VIX_STABLE_BAND:
            score = -1
        elif latest < config.VIX_BULLISH and delta_3d < -config.VIX_STABLE_BAND:
            score = 1
        else:
            score = 0

        detail = {
            "value": round(latest, 2),
            "delta_3d": round(delta_3d, 2),
            "score": score,
        }
        logger.debug("VIX score=%d  value=%.2f  delta_3d=%.2f", score, latest, delta_3d)
        return score, detail

    def get_spy_score(self) -> tuple[int, dict]:
        """
        +1  SPY above MA50 AND close > close 3 days ago
         0  SPY within ±1% of MA50
        -1  SPY below MA50
        """
        df = self._fetch(config.TICKER_SPY)
        if df.empty:
            return 0, {"error": "no data", "value": None}

        close = df["Close"]
        ma50 = float(close.rolling(config.SPY_MA_WINDOW).mean().iloc[-1])
        latest = float(close.iloc[-1])
        trend = float(close.iloc[-1] - close.iloc[-4])  # 3-day change

        deviation = (latest - ma50) / ma50

        if deviation < -config.SPY_NEUTRAL_BAND:
            score = -1
        elif abs(deviation) <= config.SPY_NEUTRAL_BAND:
            score = 0
        else:  # above MA50
            score = 1 if trend > 0 else 0

        detail = {
            "value": round(latest, 2),
            "ma50": round(ma50, 2),
            "deviation_pct": round(deviation * 100, 2),
            "trend_3d": round(trend, 2),
            "score": score,
        }
        logger.debug("SPY score=%d  close=%.2f  ma50=%.2f", score, latest, ma50)
        return score, detail

    def get_dxy_score(self) -> tuple[int, dict]:
        """
        +1  DXY falling  (5-day change < -DXY_NEUTRAL_BAND)
         0  DXY lateral
        -1  DXY rising   (3-day change > DXY_BEARISH_THRESHOLD)
        """
        df = self._fetch(config.TICKER_DXY)
        if df.empty:
            return 0, {"error": "no data", "value": None}

        close = df["Close"]
        latest = float(close.iloc[-1])
        change_5d = (float(close.iloc[-1]) - float(close.iloc[-6])) / float(close.iloc[-6])
        change_3d = (float(close.iloc[-1]) - float(close.iloc[-4])) / float(close.iloc[-4])

        if change_3d > config.DXY_BEARISH_THRESHOLD:
            score = -1
        elif change_5d < -config.DXY_NEUTRAL_BAND:
            score = 1
        else:
            score = 0

        detail = {
            "value": round(latest, 3),
            "change_5d_pct": round(change_5d * 100, 3),
            "change_3d_pct": round(change_3d * 100, 3),
            "score": score,
        }
        logger.debug("DXY score=%d  value=%.3f  chg5d=%.3f%%", score, latest, change_5d * 100)
        return score, detail

    def get_yield_score(self) -> tuple[int, dict]:
        """
        +1  10Y yield stable or falling  (3-day change < +YIELD_NEUTRAL_BPS)
         0  lateral
        -1  yield rising aggressively  (> YIELD_BEARISH_BPS in 3 days)
        Note: ^TNX is quoted in percent (×10 of the yield), so 4.50% = 45.0.
              We work in "yield units" (i.e., already divided by 10 internally).
        """
        df = self._fetch(config.TICKER_TNX)
        if df.empty:
            return 0, {"error": "no data", "value": None}

        close = df["Close"]
        # ^TNX is already in percent (e.g. 4.50 = 4.50%)
        latest = float(close.iloc[-1])
        delta_3d_bps = (float(close.iloc[-1]) - float(close.iloc[-4])) * 100  # convert % to bps

        if delta_3d_bps > config.YIELD_BEARISH_BPS:
            score = -1
        elif abs(delta_3d_bps) <= config.YIELD_NEUTRAL_BPS:
            score = 1
        else:
            score = 0

        detail = {
            "value_pct": round(latest, 3),
            "delta_3d_bps": round(delta_3d_bps, 1),
            "score": score,
        }
        logger.debug("10Y score=%d  yield=%.3f%%  delta_3d=%.1fbps", score, latest, delta_3d_bps)
        return score, detail

    # ── FOMC / mega-cap earnings warnings ────────────────────────────────────

    def _fomc_warning(self) -> bool:
        """
        Placeholder: returns True if a known FOMC date is within 2 days.
        In v1 this checks a hardcoded near-term list; a future version can
        scrape the Fed calendar.
        """
        # Known 2026 FOMC meeting dates (update quarterly)
        fomc_dates = [
            "2026-01-28", "2026-03-18", "2026-05-06", "2026-06-17",
            "2026-07-29", "2026-09-16", "2026-10-28", "2026-12-16",
        ]
        today = datetime.now(timezone.utc).date()
        for d in fomc_dates:
            meeting = datetime.strptime(d, "%Y-%m-%d").date()
            if 0 <= (meeting - today).days <= config.FOMC_WARNING_DAYS:
                logger.warning("FOMC warning: meeting on %s (within %d days)", d, config.FOMC_WARNING_DAYS)
                return True
        return False

    def _megacap_earnings_week(self) -> bool:
        """
        True if this week contains earnings from AAPL, MSFT, NVDA, GOOGL, AMZN, META.
        Uses yfinance calendar — lightweight check. Result cached per day.
        """
        today = datetime.now(timezone.utc).date()
        cache_key = f"megacap_earnings_{today}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        megacaps = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META"]
        week_end = today + timedelta(days=7)
        for ticker in megacaps:
            try:
                t = yf.Ticker(ticker)
                cal = t.calendar
                if cal is None:
                    continue
                # calendar can be a dict with 'Earnings Date' key
                if isinstance(cal, dict):
                    earning_dates = cal.get("Earnings Date", [])
                    if not isinstance(earning_dates, (list, tuple)):
                        earning_dates = [earning_dates]
                    for ed in earning_dates:
                        if ed is None:
                            continue
                        if hasattr(ed, "date"):
                            ed = ed.date()
                        elif isinstance(ed, str):
                            ed = datetime.strptime(ed[:10], "%Y-%m-%d").date()
                        if today <= ed <= week_end:
                            logger.info("Mega-cap earnings this week: %s on %s", ticker, ed)
                            self._cache[cache_key] = True
                            return True
                time.sleep(0.2)
            except Exception:
                pass
        self._cache[cache_key] = False
        return False

    # ── main entry point ──────────────────────────────────────────────────────

    def get_regime(self) -> dict:
        """
        Aggregates all 4 indicator scores and returns a full regime dict:
        {
            "regime":            "TRADE" | "SELECTIVE" | "CAUTION" | "NO_TRADE",
            "score":             int  (-4 to +4),
            "components": {
                "vix":   {"value", "delta_3d", "score"},
                "spy":   {"value", "ma50", "deviation_pct", "score"},
                "dxy":   {"value", "change_5d_pct", "score"},
                "yield": {"value_pct", "delta_3d_bps", "score"},
            },
            "fomc_warning":        bool,
            "megacap_earnings":    bool,
            "timestamp":           str (ISO-8601 UTC),
        }
        """
        vix_score, vix_detail = self.get_vix_score()
        spy_score, spy_detail = self.get_spy_score()
        dxy_score, dxy_detail = self.get_dxy_score()
        yld_score, yld_detail = self.get_yield_score()

        total = vix_score + spy_score + dxy_score + yld_score

        if total >= config.REGIME_TRADE_MIN:
            regime = "TRADE"
        elif total >= config.REGIME_SELECTIVE_MIN:
            regime = "SELECTIVE"
        elif total >= config.REGIME_CAUTION_MIN:
            regime = "CAUTION"
        else:
            regime = "NO_TRADE"

        fomc = self._fomc_warning()
        megacap = self._megacap_earnings_week()

        result = {
            "regime": regime,
            "score": total,
            "components": {
                "vix": vix_detail,
                "spy": spy_detail,
                "dxy": dxy_detail,
                "yield": yld_detail,
            },
            "fomc_warning": fomc,
            "megacap_earnings": megacap,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        logger.info(
            "Regime=%s  score=%d  VIX=%d SPY=%d DXY=%d YLD=%d  fomc=%s",
            regime, total, vix_score, spy_score, dxy_score, yld_score, fomc,
        )
        return result

    def is_tradeable(self) -> bool:
        """True only if regime is TRADE or SELECTIVE."""
        regime_data = self.get_regime()
        return regime_data["regime"] in ("TRADE", "SELECTIVE")
