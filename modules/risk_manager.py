"""
PROFITRC — Risk Manager
Position sizing (formula + Kelly), trailing stop (SMC-based), portfolio stop.
"""

import logging
import math

import numpy as np
import yfinance as yf
import pandas as pd

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

logger = logging.getLogger(__name__)


class RiskManager:

    def __init__(self, capital: float):
        if capital <= 0:
            raise ValueError("Capital must be positive")
        self.capital = capital

    # ── Position Sizing ───────────────────────────────────────────────────────

    def calculate_position_size(
        self,
        entry_price: float,
        stop_price: float,
        risk_pct: float = config.MAX_RISK_PCT,
        tier: int = 1,
    ) -> dict:
        """
        Formula: shares = (capital × risk_pct) / (entry - stop)
        TIER 2 automatically halves the position.

        Returns:
        {
            shares, dollar_risk, risk_pct_actual,
            entry_cost, tier_adjustment,
            max_loss_scenario, r_multiple_t1 (placeholder)
        }
        """
        if entry_price <= 0 or stop_price <= 0:
            raise ValueError("Prices must be positive")
        if stop_price >= entry_price:
            raise ValueError(f"Stop ({stop_price}) must be below entry ({entry_price})")

        tier_factor = config.TIER2_SIZE_FACTOR if tier == 2 else 1.0
        effective_risk = self.capital * risk_pct * tier_factor
        distance = entry_price - stop_price

        shares_raw = effective_risk / distance
        shares = max(1, int(shares_raw))  # at least 1 share

        dollar_risk = shares * distance
        entry_cost = shares * entry_price
        risk_pct_actual = dollar_risk / self.capital

        result = {
            "shares": shares,
            "dollar_risk": round(dollar_risk, 2),
            "risk_pct_actual": round(risk_pct_actual * 100, 3),
            "entry_cost": round(entry_cost, 2),
            "tier_adjustment": tier_factor,
            "max_loss_scenario": round(dollar_risk, 2),
            "entry_price": entry_price,
            "stop_price": stop_price,
        }
        logger.debug(
            "Position size: %d shares @ $%.4f  risk=$%.2f (%.2f%%)",
            shares, entry_price, dollar_risk, risk_pct_actual * 100,
        )
        return result

    # ── Kelly Criterion ───────────────────────────────────────────────────────

    def kelly_size(
        self,
        win_rate: float,
        avg_win_pct: float,
        avg_loss_pct: float,
    ) -> float:
        """
        Quarter-Kelly fraction of capital to risk.

        f* = (win_rate × avg_win_pct − loss_rate × avg_loss_pct) / avg_win_pct
        f_practical = f* / KELLY_DIVISOR

        Edge cases:
        - win_rate = 0 → returns 0
        - avg_win_pct = 0 → returns 0
        - negative f* → returns 0 (no edge, don't trade)
        """
        if win_rate <= 0 or avg_win_pct <= 0:
            return 0.0

        loss_rate = 1.0 - win_rate
        numerator = (win_rate * avg_win_pct) - (loss_rate * avg_loss_pct)
        f_full = numerator / avg_win_pct

        if f_full <= 0:
            logger.debug("Kelly: no positive edge (f*=%.4f)", f_full)
            return 0.0

        f_practical = f_full / config.KELLY_DIVISOR
        logger.debug(
            "Kelly: win_rate=%.2f avg_win=%.2f avg_loss=%.2f → f*=%.4f → quarter=%.4f",
            win_rate, avg_win_pct, avg_loss_pct, f_full, f_practical,
        )
        return round(f_practical, 4)

    # ── Trailing Stop ─────────────────────────────────────────────────────────

    def calculate_trailing_stop(
        self,
        entry_price: float,
        current_price: float,
        last_bos_level: float | None = None,
    ) -> float:
        """
        SMC trailing stop rules (PROFITRC_v2.md):
        1. Stop only moves AFTER a new BOS is confirmed above current stop.
        2. Stop NEVER falls below the floor_gain level (entry × (1 + FLOOR_GAIN_PCT)).
        3. If no BOS yet, stop stays at the original stop level passed in (not tracked here).

        This method computes the CURRENT recommended stop given:
        - entry_price: original entry
        - current_price: current market price
        - last_bos_level: most recent confirmed BOS level (if any)

        Returns the stop level to use.
        """
        floor = entry_price * (1 + config.FLOOR_GAIN_PCT)

        if current_price <= entry_price:
            # Trade hasn't moved; return floor as minimum
            return round(floor, 4)

        if last_bos_level is None or last_bos_level <= entry_price:
            # No BOS yet: return floor
            return round(floor, 4)

        # BOS confirmed: trail stop below the BOS level (last swing low before BOS)
        # Heuristic: set stop 2% below the BOS level as buffer
        bos_derived_stop = last_bos_level * 0.98

        # Never drop below floor
        stop = max(bos_derived_stop, floor)
        return round(stop, 4)

    def should_move_trailing_stop(
        self,
        current_stop: float,
        new_bos_level: float,
        entry_price: float,
    ) -> tuple[bool, float]:
        """
        Returns (should_move: bool, new_stop: float).
        Only moves if new_bos_level > current_stop + some buffer.
        Never moves below floor.
        """
        floor = entry_price * (1 + config.FLOOR_GAIN_PCT)
        proposed = new_bos_level * 0.98
        proposed = max(proposed, floor)

        if proposed > current_stop:
            return True, round(proposed, 4)
        return False, current_stop

    # ── Portfolio Stop ────────────────────────────────────────────────────────

    def check_portfolio_stop(
        self,
        portfolio_value: float,
        peak_value: float,
    ) -> bool:
        """
        Returns True if monthly drawdown from peak exceeds PORTFOLIO_STOP_MONTHLY.
        If True: all activity halts for 48h (enforced by caller).
        """
        if peak_value <= 0:
            return False
        drawdown = (peak_value - portfolio_value) / peak_value
        if drawdown >= config.PORTFOLIO_STOP_MONTHLY:
            logger.critical(
                "PORTFOLIO STOP HIT: drawdown=%.2f%% (threshold=%.0f%%)",
                drawdown * 100, config.PORTFOLIO_STOP_MONTHLY * 100,
            )
            return True
        return False

    # ── Volatility estimate ───────────────────────────────────────────────────

    def estimate_volatility(self, ticker: str, window: int = 20) -> float:
        """
        Annualised historical volatility from daily log-returns.
        Used by TradeCardGenerator for probability estimates.
        Returns 0.80 (80%) as a conservative default on failure.
        """
        try:
            df = yf.download(ticker, period="3mo", progress=False, auto_adjust=True)
            if df.empty or len(df) < window + 1:
                return 0.80
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            log_returns = np.log(df["Close"] / df["Close"].shift(1)).dropna()
            daily_std = float(log_returns.iloc[-window:].std())
            annual_vol = daily_std * math.sqrt(config.TRADING_DAYS_YEAR)
            return round(annual_vol, 4)
        except Exception as exc:
            logger.debug("estimate_volatility(%s): %s", ticker, exc)
            return 0.80

    # ── Full pre-trade risk package ───────────────────────────────────────────

    def build_risk_package(
        self,
        ticker: str,
        entry_low: float,
        entry_high: float,
        stop_price: float,
        tier: int = 1,
    ) -> dict:
        """
        Convenience method: computes sizing + volatility + R/R metrics.
        entry_mid = midpoint of entry zone.
        """
        entry_mid = (entry_low + entry_high) / 2

        sizing = self.calculate_position_size(
            entry_price=entry_mid,
            stop_price=stop_price,
            tier=tier,
        )

        vol = self.estimate_volatility(ticker)
        t1 = round(entry_mid * 1.30, 4)
        t2 = round(entry_mid * 1.60, 4)
        t3 = round(entry_mid * 2.00, 4)

        def rr(target: float) -> float:
            return round((target - entry_mid) / (entry_mid - stop_price), 2) if entry_mid != stop_price else 0.0

        return {
            **sizing,
            "entry_low": entry_low,
            "entry_high": entry_high,
            "entry_mid": entry_mid,
            "stop_loss": stop_price,
            "target1": t1,
            "target2": t2,
            "target3": t3,
            "rr_t1": rr(t1),
            "rr_t2": rr(t2),
            "rr_t3": rr(t3),
            "volatility": vol,
        }
