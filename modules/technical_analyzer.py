"""
PROFITRC — LAYER 3: Technical Structure (Smart Money Concepts)
Implements BOS, CHoCH, FVG, Orderblock detection on OHLCV data from yfinance.
"""

import logging
import time
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import yfinance as yf

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

logger = logging.getLogger(__name__)


@dataclass
class SwingPoint:
    index: int
    date: str
    price: float
    kind: str  # "high" | "low"


class TechnicalAnalyzer:
    """
    All analysis runs on daily OHLCV (primary) and hourly OHLCV (secondary).
    yfinance free tier: 1m/2m intraday (last 7d), 1h (last 730d), 1d (full history).
    """

    def _fetch_ohlcv(self, ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        try:
            df = yf.download(ticker, period=period, interval=interval,
                             progress=False, auto_adjust=True)
            if df.empty:
                logger.warning("_fetch_ohlcv(%s, %s, %s): empty", ticker, period, interval)
                return pd.DataFrame()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.dropna(subset=["Close"])
            time.sleep(config.REQUEST_DELAY)
            return df
        except Exception as exc:
            logger.error("_fetch_ohlcv(%s): %s", ticker, exc)
            return pd.DataFrame()

    # ── Swing Points ─────────────────────────────────────────────────────────

    def identify_swing_points(
        self, df: pd.DataFrame, lookback: int = config.SWING_LOOKBACK
    ) -> dict:
        """
        A swing high at index i: high[i] > all highs in [i-lookback … i+lookback].
        A swing low  at index i: low[i]  < all lows  in [i-lookback … i+lookback].
        Returns {swing_highs: list[SwingPoint], swing_lows: list[SwingPoint]}.
        """
        highs: list[SwingPoint] = []
        lows: list[SwingPoint] = []
        n = len(df)

        for i in range(lookback, n - lookback):
            window_h = df["High"].iloc[i - lookback: i + lookback + 1]
            window_l = df["Low"].iloc[i - lookback: i + lookback + 1]

            if df["High"].iloc[i] == window_h.max():
                highs.append(SwingPoint(
                    index=i,
                    date=str(df.index[i])[:10],
                    price=float(df["High"].iloc[i]),
                    kind="high",
                ))

            if df["Low"].iloc[i] == window_l.min():
                lows.append(SwingPoint(
                    index=i,
                    date=str(df.index[i])[:10],
                    price=float(df["Low"].iloc[i]),
                    kind="low",
                ))

        return {"swing_highs": highs, "swing_lows": lows}

    # ── Break of Structure ────────────────────────────────────────────────────

    def check_bos(self, df: pd.DataFrame) -> dict:
        """
        BOS: the most recent close is above the most recent significant swing high,
        with the candle closing above that level.

        Returns {confirmed, bos_level, bos_candle_date, timeframe}.
        """
        if len(df) < config.SWING_LOOKBACK * 2 + 2:
            return {"confirmed": False, "bos_level": None, "bos_candle_date": None, "timeframe": "daily"}

        swings = self.identify_swing_points(df)
        swing_highs = swings["swing_highs"]

        if not swing_highs:
            return {"confirmed": False, "bos_level": None, "bos_candle_date": None, "timeframe": "daily"}

        # Most recent swing high (not the last bar since we need look-forward)
        last_swing_high = swing_highs[-1]
        bos_level = last_swing_high.price

        # Check if any subsequent close exceeded that level
        subsequent = df.iloc[last_swing_high.index + 1:]
        for i, (idx, row) in enumerate(subsequent.iterrows()):
            if float(row["Close"]) > bos_level:
                return {
                    "confirmed": True,
                    "bos_level": round(bos_level, 4),
                    "bos_candle_date": str(idx)[:10],
                    "timeframe": "daily",
                }

        return {"confirmed": False, "bos_level": round(bos_level, 4), "bos_candle_date": None, "timeframe": "daily"}

    # ── Change of Character ───────────────────────────────────────────────────

    def check_choch(self, df: pd.DataFrame) -> dict:
        """
        CHoCH: a swing low is broken (price dips below it) but then the
        next close reclaims above the broken swing low level — indicating
        institutional re-accumulation / failed breakdown.
        """
        if len(df) < config.SWING_LOOKBACK * 2 + 3:
            return {"detected": False, "choch_level": None, "date": None}

        swings = self.identify_swing_points(df)
        swing_lows = swings["swing_lows"]
        if len(swing_lows) < 2:
            return {"detected": False, "choch_level": None, "date": None}

        # Look at the last 2 swing lows
        sl = swing_lows[-1]
        sl_level = sl.price

        # Check if price dipped below sl_level then recovered
        window = df.iloc[sl.index:]
        breach_found = False
        for i, (idx, row) in enumerate(window.iterrows()):
            if not breach_found and float(row["Low"]) < sl_level:
                breach_found = True
                continue
            if breach_found and float(row["Close"]) > sl_level:
                return {
                    "detected": True,
                    "choch_level": round(sl_level, 4),
                    "date": str(idx)[:10],
                }

        return {"detected": False, "choch_level": round(sl_level, 4), "date": None}

    # ── Fair Value Gap ────────────────────────────────────────────────────────

    def identify_fvg(self, df: pd.DataFrame) -> list[dict]:
        """
        Bullish FVG: candle[i-1].high < candle[i+1].low
        (gap between candle i-1 top and candle i+1 bottom — price skipped over it).
        Minimum gap size: FVG_MIN_GAP_PCT.
        Returns unfilled FVGs sorted newest-first.
        """
        fvgs: list[dict] = []
        n = len(df)
        for i in range(1, n - 1):
            c0_high = float(df["High"].iloc[i - 1])
            c2_low = float(df["Low"].iloc[i + 1])
            c1_close = float(df["Close"].iloc[i])

            if c2_low > c0_high:
                gap_pct = (c2_low - c0_high) / c0_high
                if gap_pct >= config.FVG_MIN_GAP_PCT:
                    # Check if FVG has since been filled (price retraced into it)
                    filled = False
                    future = df.iloc[i + 2:]
                    for _, frow in future.iterrows():
                        if float(frow["Low"]) <= c2_low and float(frow["High"]) >= c0_high:
                            filled = True
                            break
                    fvgs.append({
                        "bottom": round(c0_high, 4),
                        "top": round(c2_low, 4),
                        "midpoint": round((c0_high + c2_low) / 2, 4),
                        "date": str(df.index[i])[:10],
                        "gap_pct": round(gap_pct * 100, 2),
                        "filled": filled,
                    })

        # Newest-first, unfilled first
        fvgs.sort(key=lambda x: (x["filled"], x["date"]), reverse=True)
        return fvgs

    # ── Orderblock ────────────────────────────────────────────────────────────

    def identify_orderblock(self, df: pd.DataFrame) -> list[dict]:
        """
        Orderblock: last bearish (red) candle immediately before a BOS.
        This is the zone where institutions placed buy orders.
        """
        bos = self.check_bos(df)
        orderblocks: list[dict] = []

        if not bos["confirmed"] or bos["bos_level"] is None:
            return orderblocks

        bos_level = bos["bos_level"]
        # Find the BOS candle index
        bos_idx = None
        for i in range(len(df) - 1, -1, -1):
            if float(df["Close"].iloc[i]) > bos_level:
                bos_idx = i
                break

        if bos_idx is None or bos_idx < 2:
            return orderblocks

        # Last bearish candle before the BOS
        for i in range(bos_idx - 1, max(bos_idx - 10, 0), -1):
            o = float(df["Open"].iloc[i])
            c = float(df["Close"].iloc[i])
            if o > c:  # bearish candle
                orderblocks.append({
                    "bottom": round(min(o, c), 4),
                    "top": round(max(o, c), 4),
                    "date": str(df.index[i])[:10],
                    "type": "demand",
                })
                break  # only the most recent OB

        return orderblocks

    # ── Blow-off Top ──────────────────────────────────────────────────────────

    def check_blowoff_top(self, df: pd.DataFrame) -> bool:
        """
        Returns True if the last candle shows:
          - volume > BLOWOFF_VOLUME_MULTIPLIER × 20-day avg volume
          - upper shadow ≥ BLOWOFF_UPPER_SHADOW_MIN × full range
        If True: setup is auto-rejected.
        """
        if len(df) < 22:
            return False

        last = df.iloc[-1]
        avg_vol = float(df["Volume"].iloc[-21:-1].mean())
        last_vol = float(last["Volume"])
        candle_range = float(last["High"]) - float(last["Low"])
        upper_shadow = float(last["High"]) - max(float(last["Open"]), float(last["Close"]))

        if candle_range == 0:
            return False

        vol_spike = last_vol > config.BLOWOFF_VOLUME_MULTIPLIER * avg_vol
        big_upper_shadow = (upper_shadow / candle_range) >= config.BLOWOFF_UPPER_SHADOW_MIN

        if vol_spike and big_upper_shadow:
            logger.warning("Blow-off top detected: vol_mult=%.1f shadow_pct=%.0f%%",
                           last_vol / avg_vol, (upper_shadow / candle_range) * 100)
            return True
        return False

    # ── Composite Technical Score (0–20) ─────────────────────────────────────

    def get_technical_score(self, ticker: str) -> dict:
        """
        Fetches daily and hourly OHLCV, runs all SMC checks, and returns:
        {
            score (0–20), bos, choch, fvg_zones, orderblocks,
            entry_zone {low, high}, invalidation, pattern, blow_off_top
        }
        """
        df_daily = self._fetch_ohlcv(ticker, period="6mo", interval="1d")
        df_hourly = self._fetch_ohlcv(ticker, period="60d", interval="1h")

        result = {
            "score": 0,
            "bos": {"confirmed": False},
            "choch": {"detected": False},
            "fvg_zones": [],
            "orderblocks": [],
            "entry_zone": {"low": None, "high": None},
            "invalidation": None,
            "pattern": "no_structure",
            "blow_off_top": False,
        }

        if df_daily.empty:
            result["pattern"] = "data_unavailable"
            return result

        score = 0
        flags: list[str] = []

        # ── Blow-off check (hard stop) ────────────────────────────────────────
        blow_off = self.check_blowoff_top(df_daily)
        result["blow_off_top"] = blow_off
        if blow_off:
            result["score"] = -10
            result["pattern"] = "blow_off_top"
            return result  # no further analysis needed

        # ── BOS (5 pts) ───────────────────────────────────────────────────────
        bos = self.check_bos(df_daily)
        result["bos"] = bos
        if bos["confirmed"]:
            score += 5
            flags.append("BOS_DAILY")

        # ── CHoCH (4 pts) ─────────────────────────────────────────────────────
        choch = self.check_choch(df_daily)
        result["choch"] = choch
        if choch["detected"]:
            score += 4
            flags.append("CHOCH_DAILY")

        # ── FVG zones (5 pts) ─────────────────────────────────────────────────
        fvg_daily = self.identify_fvg(df_daily)
        unfilled = [f for f in fvg_daily if not f["filled"]][:5]
        result["fvg_zones"] = unfilled
        if unfilled:
            score += 5
            flags.append(f"FVG_{len(unfilled)}_ZONES")

        # ── Orderblock (3 pts) ────────────────────────────────────────────────
        obs = self.identify_orderblock(df_daily)
        result["orderblocks"] = obs
        if obs:
            score += 3
            flags.append("ORDERBLOCK")

        # ── Hourly structure bonus ────────────────────────────────────────────
        if not df_hourly.empty and len(df_hourly) > 20:
            bos_1h = self.check_bos(df_hourly)
            if bos_1h["confirmed"]:
                score += 2
                flags.append("BOS_1H_BONUS")
            fvg_1h = self.identify_fvg(df_hourly)
            if fvg_1h:
                score += 1
                flags.append("FVG_1H_BONUS")

        # ── Entry zone ────────────────────────────────────────────────────────
        entry_low: float | None = None
        entry_high: float | None = None

        if unfilled:
            # Use most recent unfilled FVG as entry zone
            best_fvg = unfilled[0]
            entry_low = best_fvg["bottom"]
            entry_high = best_fvg["top"]
        elif obs:
            entry_low = obs[0]["bottom"]
            entry_high = obs[0]["top"]
        else:
            # Fallback: last CHoCH level ±2%
            if choch["choch_level"]:
                lvl = choch["choch_level"]
                entry_low = round(lvl * 0.98, 4)
                entry_high = round(lvl * 1.02, 4)

        result["entry_zone"] = {"low": entry_low, "high": entry_high}

        # ── Invalidation level (below last swing low) ─────────────────────────
        swings = self.identify_swing_points(df_daily)
        if swings["swing_lows"]:
            result["invalidation"] = round(swings["swing_lows"][-1].price * 0.99, 4)

        # ── Pattern classification ────────────────────────────────────────────
        if "FVG_" in " ".join(flags) and "BOS_DAILY" in flags and "CHOCH_DAILY" in flags:
            result["pattern"] = "fvg_reclaim"
        elif "BOS_DAILY" in flags and "FVG_" in " ".join(flags):
            result["pattern"] = "bos_fvg"
        elif "CHOCH_DAILY" in flags:
            result["pattern"] = "choch_reversal"
        elif "BOS_DAILY" in flags:
            result["pattern"] = "bos_only"
        elif score > 0:
            result["pattern"] = "partial_structure"

        result["score"] = min(score, config.TECHNICAL_MAX)
        logger.debug("technical_score(%s) = %d  pattern=%s  flags=%s",
                     ticker, result["score"], result["pattern"], flags)
        return result
