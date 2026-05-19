"""
PROFITRC — LAYER 1: Scan & Discovery
Implements the 5-phase scanning pipeline (Phase 0 evening through Phase 4 AH).
Returns raw candidate lists for downstream scoring.
"""

import logging
import re
import time
from datetime import datetime, timezone

import feedparser
import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _get(url: str, timeout: int = config.REQUEST_TIMEOUT) -> requests.Response | None:
    """GET with retry on transient errors."""
    for attempt in range(3):
        try:
            r = requests.get(url, headers=_HEADERS, timeout=timeout)
            r.raise_for_status()
            return r
        except requests.RequestException as exc:
            logger.warning("GET %s attempt %d failed: %s", url, attempt + 1, exc)
            time.sleep(2 ** attempt)
    return None


def _price_in_range(price: float) -> bool:
    return config.PRICE_MIN <= price <= config.PRICE_MAX


class Scanner:

    # ── Relative Volume ───────────────────────────────────────────────────────

    def calculate_rvol(self, ticker: str, window: int = config.RVOL_WINDOW) -> float:
        """
        RVOL = today's volume / average volume over the last `window` trading days.
        Returns 0.0 on failure.
        """
        try:
            df = yf.download(ticker, period="3mo", progress=False, auto_adjust=True)
            if df.empty or len(df) < window + 1:
                return 0.0
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            avg_vol = float(df["Volume"].iloc[-(window + 1):-1].mean())
            today_vol = float(df["Volume"].iloc[-1])
            if avg_vol == 0:
                return 0.0
            rvol = today_vol / avg_vol
            time.sleep(config.REQUEST_DELAY)
            return round(rvol, 2)
        except Exception as exc:
            logger.error("calculate_rvol(%s): %s", ticker, exc)
            return 0.0

    def get_float(self, ticker: str) -> int:
        """
        Returns floatShares from yfinance info.
        Falls back to sharesOutstanding if floatShares is missing.
        Returns 0 on failure.
        """
        try:
            info = yf.Ticker(ticker).info
            val = info.get("floatShares") or info.get("sharesOutstanding") or 0
            time.sleep(config.REQUEST_DELAY)
            return int(val)
        except Exception as exc:
            logger.warning("get_float(%s): %s", ticker, exc)
            return 0

    # ── Phase 0 / Phase 4 : After-Hours ──────────────────────────────────────

    def fetch_ah_movers(self) -> list[dict]:
        """
        Scrapes StockMarketWatch AH movers.
        Returns [{"ticker", "price", "change_pct", "volume_str"}]
        filtered to PRICE_MIN–PRICE_MAX.
        """
        resp = _get(config.URL_AH_MOVERS)
        if resp is None:
            logger.error("fetch_ah_movers: request failed")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        candidates: list[dict] = []

        # The page uses a table with class containing 'moverTable' or similar.
        # We parse all <tr> rows and extract symbol, price, change columns.
        rows = soup.select("table tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 4:
                continue
            try:
                ticker_el = cells[0].find("a") or cells[0]
                ticker = ticker_el.get_text(strip=True).upper()
                if not re.match(r'^[A-Z]{1,5}$', ticker):
                    continue

                price_text = cells[1].get_text(strip=True).replace("$", "").replace(",", "")
                price = float(price_text)
                if not _price_in_range(price):
                    continue

                change_text = cells[2].get_text(strip=True).replace("%", "").replace("+", "")
                change_pct = float(change_text)

                # Skip if already gapped too much
                if abs(change_pct) > config.AH_GAP_MAX_PCT * 100:
                    logger.debug("AH skip %s: gap %.1f%% exceeds max", ticker, change_pct)
                    continue

                volume_str = cells[3].get_text(strip=True) if len(cells) > 3 else "N/A"

                candidates.append({
                    "ticker": ticker,
                    "price": price,
                    "change_pct": change_pct,
                    "volume_str": volume_str,
                    "source": "ah_movers",
                })
            except (ValueError, IndexError, AttributeError):
                continue

        logger.info("fetch_ah_movers: %d candidates in price range", len(candidates))
        return candidates

    def fetch_sec_8k_filings(self, hours_back: int = 4) -> list[dict]:
        """
        Parses the SEC EDGAR 8-K Atom feed.
        Returns [{"company", "cik", "filing_date", "url", "summary"}]
        for filings within the last `hours_back` hours.
        """
        feed = feedparser.parse(config.URL_SEC_8K_ATOM)
        if feed.bozo:
            logger.warning("fetch_sec_8k_filings: feed parse warning: %s", feed.bozo_exception)

        cutoff = datetime.now(timezone.utc).timestamp() - hours_back * 3600
        results: list[dict] = []

        for entry in feed.entries:
            try:
                # published_parsed is a time.struct_time in UTC
                pub_ts = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).timestamp()
                if pub_ts < cutoff:
                    continue

                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", "")

                # Extract company name and CIK from title: "COMPANY NAME (CIK 0001234567) ..."
                cik_match = re.search(r'\(CIK\s+(\d+)\)', title, re.IGNORECASE)
                cik = cik_match.group(1) if cik_match else ""
                company = re.sub(r'\s*\(CIK.*', '', title).strip()

                results.append({
                    "company": company,
                    "cik": cik,
                    "filing_date": entry.published,
                    "url": link,
                    "summary": summary[:500],
                    "source": "sec_8k",
                })
                time.sleep(config.SEC_REQUEST_DELAY)
            except Exception as exc:
                logger.debug("8-K entry parse error: %s", exc)

        logger.info("fetch_sec_8k_filings: %d filings in last %dh", len(results), hours_back)
        return results

    def fetch_earnings_movers(self) -> list[dict]:
        """
        Scrapes Yahoo Finance earnings calendar for AH beats.
        Returns [{"ticker", "eps_actual", "eps_estimate", "surprise_pct", "revenue_beat"}]
        filtered by EPS beat >25% OR revenue beat >20%.
        """
        resp = _get(config.URL_YAHOO_EARNINGS, timeout=20)
        if resp is None:
            logger.error("fetch_earnings_movers: request failed")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        candidates: list[dict] = []

        # Yahoo Finance earnings table rows
        rows = soup.select("table tbody tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 5:
                continue
            try:
                ticker_el = cells[0].find("a") or cells[0]
                ticker = ticker_el.get_text(strip=True).upper()
                if not re.match(r'^[A-Z]{1,5}(\.[A-Z])?$', ticker):
                    continue

                # Columns vary — try to extract EPS actual vs estimate
                eps_actual_text = cells[2].get_text(strip=True).replace(",", "") if len(cells) > 2 else ""
                eps_est_text = cells[3].get_text(strip=True).replace(",", "") if len(cells) > 3 else ""

                eps_actual = float(eps_actual_text) if eps_actual_text not in ("N/A", "", "--") else None
                eps_est = float(eps_est_text) if eps_est_text not in ("N/A", "", "--") else None

                surprise_pct = 0.0
                if eps_actual is not None and eps_est is not None and eps_est != 0:
                    surprise_pct = ((eps_actual - eps_est) / abs(eps_est)) * 100

                # Only keep significant beats
                if surprise_pct < config.EPS_BEAT_MIN_PCT:
                    continue

                candidates.append({
                    "ticker": ticker,
                    "eps_actual": eps_actual,
                    "eps_estimate": eps_est,
                    "surprise_pct": round(surprise_pct, 1),
                    "revenue_beat": False,  # upgraded if revenue data available
                    "source": "yahoo_earnings",
                })
            except (ValueError, IndexError, AttributeError):
                continue

        logger.info("fetch_earnings_movers: %d candidates pass beat filter", len(candidates))
        return candidates

    def fetch_premarket_gainers(self) -> list[dict]:
        """
        Scrapes StockAnalysis premarket gainers.
        Returns [{"ticker", "price", "change_pct", "volume_str"}]
        filtered to price range and gap ≤ AH_GAP_MAX_PCT.
        """
        resp = _get(config.URL_PREMARKET_GAINERS)
        if resp is None:
            logger.error("fetch_premarket_gainers: request failed")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        candidates: list[dict] = []

        rows = soup.select("table tbody tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            try:
                ticker_el = cells[0].find("a") or cells[0]
                ticker = ticker_el.get_text(strip=True).upper()
                if not re.match(r'^[A-Z]{1,5}$', ticker):
                    continue

                price_text = cells[1].get_text(strip=True).replace("$", "").replace(",", "")
                price = float(price_text)
                if not _price_in_range(price):
                    continue

                change_text = cells[2].get_text(strip=True).replace("%", "").replace("+", "")
                change_pct = float(change_text)

                if change_pct > config.PREMARKET_GAP_MAX_PCT * 100:
                    logger.debug("PM skip %s: gap %.1f%% exceeds max", ticker, change_pct)
                    continue

                volume_str = cells[3].get_text(strip=True) if len(cells) > 3 else "N/A"

                candidates.append({
                    "ticker": ticker,
                    "price": price,
                    "change_pct": change_pct,
                    "volume_str": volume_str,
                    "source": "premarket_gainers",
                })
            except (ValueError, IndexError, AttributeError):
                continue

        logger.info("fetch_premarket_gainers: %d candidates in range", len(candidates))
        return candidates

    def fetch_yahoo_trending(self) -> list[dict]:
        """
        Fetches Yahoo Finance most-active / trending tickers via yfinance screener.
        Returns [{"ticker", "price", "change_pct", "volume"}]
        """
        try:
            # yfinance doesn't expose trending directly — use most_actives screener
            import yfinance.screener as yfsc
        except ImportError:
            yfsc = None

        candidates: list[dict] = []

        # Fallback: scrape Yahoo Finance most-active page
        url = "https://finance.yahoo.com/most-active?count=50&offset=0"
        resp = _get(url, timeout=20)
        if resp is None:
            return candidates

        soup = BeautifulSoup(resp.text, "lxml")
        rows = soup.select("table tbody tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            try:
                ticker_el = cells[0].find("a") or cells[0]
                ticker = ticker_el.get_text(strip=True).upper()
                if not re.match(r'^[A-Z]{1,5}$', ticker):
                    continue

                price_text = cells[2].get_text(strip=True).replace("$", "").replace(",", "")
                price = float(price_text)
                if not _price_in_range(price):
                    continue

                change_text = cells[4].get_text(strip=True).replace("%", "").replace("+", "") if len(cells) > 4 else "0"
                change_pct = float(change_text)

                candidates.append({
                    "ticker": ticker,
                    "price": price,
                    "change_pct": change_pct,
                    "volume_str": cells[6].get_text(strip=True) if len(cells) > 6 else "N/A",
                    "source": "yahoo_trending",
                })
            except (ValueError, IndexError, AttributeError):
                continue

        logger.info("fetch_yahoo_trending: %d candidates in range", len(candidates))
        return candidates

    # ── Deduplication helper ─────────────────────────────────────────────────

    @staticmethod
    def _deduplicate(candidates: list[dict]) -> list[dict]:
        seen: set[str] = set()
        out: list[dict] = []
        for c in candidates:
            t = c.get("ticker", "")
            if t and t not in seen:
                seen.add(t)
                out.append(c)
        return out

    # ── Phase runner ─────────────────────────────────────────────────────────

    def run_phase_scan(self, phase: int) -> list[dict]:
        """
        Executes the scan for the given phase (0–4).
        Applies primary filters: price range, float cap.
        Returns deduplicated candidate list.

        Phase 0 / 4  → AH movers + earnings movers + SEC 8-K
        Phase 1       → premarket gainers + SEC 8-K (last 12h)
        Phase 2 / 3   → Yahoo trending + RVOL check on watchlist
        """
        logger.info("=== Phase %d scan started ===", phase)
        raw: list[dict] = []

        if phase in (0, 4):
            raw += self.fetch_ah_movers()
            raw += self.fetch_earnings_movers()
            raw += self.fetch_sec_8k_filings(hours_back=4)

        elif phase == 1:
            raw += self.fetch_premarket_gainers()
            raw += self.fetch_sec_8k_filings(hours_back=12)

        elif phase in (2, 3):
            raw += self.fetch_yahoo_trending()

        # Apply primary float filter (skip tickers where float >> FLOAT_MAX_TIER2)
        filtered: list[dict] = []
        for c in raw:
            ticker = c.get("ticker")
            if not ticker:
                # SEC 8-K entries may not have ticker yet; pass through for later enrichment
                filtered.append(c)
                continue
            # Price already filtered upstream; only float-check if ticker present
            fl = self.get_float(ticker)
            if fl == 0 or fl <= config.FLOAT_MAX_TIER2 * 3:
                # Keep unknowns and anything up to 3× TIER2 cap (scorer will penalise)
                c["float_shares"] = fl
                filtered.append(c)
            else:
                logger.debug("Phase%d skip %s: float %dM too large", phase, ticker, fl // 1_000_000)

        deduped = self._deduplicate(filtered)
        logger.info("Phase %d: %d raw → %d after dedup/float filter", phase, len(raw), len(deduped))
        return deduped
