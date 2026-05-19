"""
PROFITRC — Scoring Engine (0–100)
Aggregates Catalyst / Volume / Sentiment / Technical / Risk scores.
"""

import logging
import re
import time
from dataclasses import dataclass, field

import yfinance as yf

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

POSITIVE_KEYWORDS = [
    "beat", "beats", "exceeds", "raises guidance", "contract", "awarded",
    "approved", "approval", "partnership", "deal", "record", "growth",
    "acquisition", "buy", "upgrade", "bullish",
]

NEGATIVE_KEYWORDS = [
    "miss", "misses", "below", "lowers guidance", "lawsuit", "investigation",
    "sec probe", "delisting", "bankruptcy", "downgrade", "dilution",
    "offering", "selloff", "resign", "fraud",
]

logger = logging.getLogger(__name__)


@dataclass
class ScoreCard:
    ticker: str
    catalyst_score: int = 0      # 0–25
    volume_score: int = 0        # 0–25
    sentiment_score: int = 0     # 0–20
    technical_score: int = 0     # 0–20
    risk_score: int = 0          # 0–10
    total: int = 0
    tier: int = 2                # 1, 2, or 3
    verdict: str = "SKIP"        # "PROCEED" | "REVIEW" | "SKIP"
    flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "catalyst_score": self.catalyst_score,
            "volume_score": self.volume_score,
            "sentiment_score": self.sentiment_score,
            "technical_score": self.technical_score,
            "risk_score": self.risk_score,
            "total": self.total,
            "tier": self.tier,
            "verdict": self.verdict,
            "flags": self.flags,
        }


class Scorer:
    """
    All score methods return an int in their respective range.
    score_ticker() assembles the full ScoreCard and enforces hard skips.
    """

    # ── Catalyst Score (0–25) ─────────────────────────────────────────────────

    def calculate_catalyst_score(self, catalyst_data: dict) -> tuple[int, list[str]]:
        """
        catalyst_data keys (all optional):
          event_type   str   one of the keys in config.CATALYST_SCORES
          tier         int   1 | 2 | 3 (pre-classified by CatalystVerifier)
          days_to_event int  days until the catalyst fires
        Returns (score, flags).
        """
        flags: list[str] = []
        tier = catalyst_data.get("tier", 2)
        event_type = catalyst_data.get("event_type", "")
        days = catalyst_data.get("days_to_event", 99)

        if tier == 3:
            flags.append("TIER3_AUTO_SKIP")
            return 3, flags  # minimal score, triggers SKIP downstream

        # Map event_type to base score
        # Use sentinel -1 to distinguish "unknown event" from "explicitly 0"
        base = config.CATALYST_SCORES.get(event_type, -1)

        if base == -1:
            # Unknown event type: apply tier-based generous default
            base = 20 if tier == 1 else 10
        # If base == 0 (e.g. "catalyst_already_priced"), keep it at 0 — no override

        # Proximity bonus: catalyst within 7 days adds urgency
        if days <= 7:
            bonus = 3
            base = min(base + bonus, config.CATALYST_MAX)
            flags.append(f"CATALYST_WITHIN_{days}D")

        if base < config.CATALYST_SCORE_MIN_TO_PROCEED:
            flags.append("CATALYST_SCORE_TOO_LOW")

        return min(base, config.CATALYST_MAX), flags

    # ── Volume Score (0–25) ───────────────────────────────────────────────────

    def calculate_volume_score(self, ticker: str, rvol: float | None = None, ticker_data=None) -> tuple[int, list[str]]:
        """
        Uses pre-computed RVOL if provided, otherwise fetches from yfinance.
        Uses ticker_data.daily for multi-day check if available.
        """
        flags: list[str] = []

        if rvol is None:
            if ticker_data is not None:
                rvol = ticker_data.rvol
            else:
                from modules.scanner import Scanner
                rvol = Scanner().calculate_rvol(ticker)

        if rvol >= 20:
            score = 25
        elif rvol >= 10:
            score = 20
        elif rvol >= 5:
            score = 14
        elif rvol >= 3:
            score = 8
        else:
            score = 2
            flags.append("LOW_RVOL")

        # Multi-day accumulation bonus: 3 of last 5 days above average volume
        try:
            import pandas as pd
            if ticker_data is not None and not ticker_data.daily.empty:
                df = ticker_data.daily
            else:
                df = yf.download(ticker, period="1mo", progress=False, auto_adjust=True)
                time.sleep(config.REQUEST_DELAY)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                avg = df["Volume"].mean()
                recent = df["Volume"].iloc[-5:]
                above_avg_days = int((recent > avg).sum())
                if above_avg_days >= 3:
                    score = min(score + 5, config.VOLUME_MAX)
                    flags.append("MULTI_DAY_ACCUM")
                if len(df) >= 4:
                    pullback_vol = df["Volume"].iloc[-2:].mean()
                    prior_vol = df["Volume"].iloc[-4:-2].mean()
                    if pullback_vol < prior_vol * 0.7:
                        score = min(score + 3, config.VOLUME_MAX)
                        flags.append("PULLBACK_LOW_VOL")
        except Exception as exc:
            logger.debug("volume multi-day check(%s): %s", ticker, exc)

        return min(score, config.VOLUME_MAX), flags

    # ── Sentiment Score (0–20) ────────────────────────────────────────────────

    def calculate_sentiment_score(self, ticker: str, ticker_data=None) -> tuple[int, list[str]]:
        """
        Counts news headline mentions from Yahoo Finance in the last 48h.
        Applies keyword polarity analysis before scoring.
        Classifies as: absent (5) | nascent (12) | acceleration (20) | saturated (0)
        """
        flags: list[str] = []

        try:
            if ticker_data is not None:
                news_items = ticker_data.news_items
                count = ticker_data.news_count_48h
            else:
                import time as _time
                t = yf.Ticker(ticker)
                news = t.news or []
                cutoff = _time.time() - 48 * 3600
                news_items = [n for n in news if n.get("providerPublishTime", 0) >= cutoff]
                count = len(news_items)
                time.sleep(config.REQUEST_DELAY)
        except Exception as exc:
            logger.debug("sentiment(%s): %s", ticker, exc)
            return 5, ["SENTIMENT_DATA_ERROR"]

        if count == 0:
            return 5, flags

        # Keyword polarity check on titles and summaries
        positive_hits = 0
        negative_hits = 0
        for item in news_items:
            text = (item.get("title", "") + " " + item.get("summary", "")).lower()
            if any(kw in text for kw in POSITIVE_KEYWORDS):
                positive_hits += 1
            if any(kw in text for kw in NEGATIVE_KEYWORDS):
                negative_hits += 1

        # Dominant negative news overrides count-based scoring
        if negative_hits > positive_hits and negative_hits >= 2:
            flags.append("NEGATIVE_NEWS_DOMINANT")
            return 5, flags

        if count <= 3:
            score, sentiment_flag = 12, "NASCENT_SENTIMENT"
        elif count <= 8:
            score, sentiment_flag = 20, "SENTIMENT_ACCELERATING"
        else:
            score, sentiment_flag = 0, "HYPE_SATURATED_RED_FLAG"

        flags.append(sentiment_flag)
        return score, flags

    # ── Risk Score (0–10, higher = LOWER risk) ────────────────────────────────

    def calculate_risk_score(
        self,
        ticker: str,
        ticker_data=None,
        catalyst_data: dict | None = None,
    ) -> tuple[int, list[str]]:
        """
        Evaluates dilution / float / structural red flags.
        Uses ticker_data.info if available to avoid redundant downloads.
        """
        flags: list[str] = []
        try:
            if ticker_data is not None and ticker_data.info:
                info = ticker_data.info
                float_shares = ticker_data.float_shares
            else:
                info = yf.Ticker(ticker).info
                float_shares = info.get("floatShares") or info.get("sharesOutstanding") or 0
                time.sleep(config.REQUEST_DELAY)
        except Exception as exc:
            logger.warning("risk_score(%s) info fetch: %s", ticker, exc)
            return 5, ["INFO_FETCH_FAILED"]

        # Float-based base score
        if 0 < float_shares <= config.FLOAT_MAX_TIER1:
            score = 10
            flags.append(f"FLOAT_CLEAN_{float_shares // 1_000_000}M")
        elif float_shares <= config.FLOAT_MAX_TIER2:
            score = 8
        elif float_shares <= config.FLOAT_MAX_TIER2 * 2:
            score = 5
        else:
            score = 3
            flags.append("LARGE_FLOAT")

        # Check recent SEC filings for red-flag language (reuse pipeline data when available)
        try:
            if catalyst_data and catalyst_data.get("sec_filing"):
                filing = catalyst_data["sec_filing"]
            else:
                from modules.catalyst_verifier import CatalystVerifier
                filing = CatalystVerifier().verify_sec_filing(ticker)
            summary_lower = filing.get("summary", "").lower()

            DILUTION_SIGNALS = [
                "reverse stock split", "at-the-market", "atm offering",
                "prospectus supplement", "shelf registration",
            ]
            for sig in DILUTION_SIGNALS:
                if sig in summary_lower:
                    score = max(score - 4, 0)
                    flags.append(f"DILUTION_SIGNAL:{sig.upper()}")
                    break

            if "reverse stock split" in summary_lower:
                score = 0
                flags.append("REVERSE_SPLIT_AUTO_SKIP")
        except Exception as exc:
            logger.debug("risk_score SEC check(%s): %s", ticker, exc)

        return min(score, config.RISK_MAX), flags

    # ── Master scorer ─────────────────────────────────────────────────────────

    def score_ticker(
        self,
        ticker: str,
        catalyst_data: dict,
        rvol: float | None = None,
        technical_score: int | None = None,
        ticker_data=None,
    ) -> ScoreCard:
        """
        Calculates full ScoreCard.

        Hard-skip conditions (enforced before total threshold check):
          1. TIER3 in catalyst_data
          2. Any AUTO_SKIP flag
          3. HYPE_SATURATED_RED_FLAG (Kindleberger Stage 3–4)
          4. blow_off_top = True in catalyst_data
          5. total < SCORE_THRESHOLD
        """
        card = ScoreCard(ticker=ticker)

        cat_score, cat_flags = self.calculate_catalyst_score(catalyst_data)
        vol_score, vol_flags = self.calculate_volume_score(ticker, rvol=rvol, ticker_data=ticker_data)
        sent_score, sent_flags = self.calculate_sentiment_score(ticker, ticker_data=ticker_data)
        risk_score, risk_flags = self.calculate_risk_score(
            ticker, ticker_data=ticker_data, catalyst_data=catalyst_data,
        )

        # Technical score supplied externally (from TechnicalAnalyzer) or default
        tech_score = technical_score if technical_score is not None else 0
        tech_flags: list[str] = [] if technical_score is not None else ["TECHNICAL_NOT_RUN"]

        all_flags = cat_flags + vol_flags + sent_flags + tech_flags + risk_flags

        total = cat_score + vol_score + sent_score + tech_score + risk_score
        tier = catalyst_data.get("tier", 2)

        card.catalyst_score = cat_score
        card.volume_score = vol_score
        card.sentiment_score = sent_score
        card.technical_score = tech_score
        card.risk_score = risk_score
        card.total = total
        card.tier = tier
        card.flags = all_flags

        # ── Hard-skip checks (non-negotiable, PROFITRC_v2.md) ─────────────────
        skip_reason: str | None = None

        if tier == 3:
            skip_reason = "TIER3_CATALYST"
        elif "TIER3_AUTO_SKIP" in all_flags:
            skip_reason = "TIER3_AUTO_SKIP"
        elif "REVERSE_SPLIT_AUTO_SKIP" in all_flags:
            skip_reason = "REVERSE_SPLIT"
        elif "HYPE_SATURATED_RED_FLAG" in all_flags:
            skip_reason = "HYPE_SATURATED"
        elif catalyst_data.get("blow_off_top", False):
            skip_reason = "BLOW_OFF_TOP"
        elif cat_score < config.CATALYST_SCORE_MIN_TO_PROCEED:
            skip_reason = "CATALYST_SCORE_TOO_LOW"
        elif total < config.SCORE_THRESHOLD:
            skip_reason = f"SCORE_{total}_BELOW_{config.SCORE_THRESHOLD}"

        if skip_reason:
            card.verdict = "SKIP"
            card.flags.append(f"SKIP_REASON:{skip_reason}")
            logger.info("SKIP %s  reason=%s  score=%d", ticker, skip_reason, total)
        elif total >= 80:
            card.verdict = "PROCEED"
            logger.info("PROCEED %s  score=%d  tier=%d", ticker, total, tier)
        else:
            card.verdict = "REVIEW"
            logger.info("REVIEW %s  score=%d  tier=%d", ticker, total, tier)

        return card
