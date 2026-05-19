"""
PROFITRC — LAYER 2: Catalyst Verification
Classifies catalysts into TIER 1 / 2 / 3 and verifies against SEC EDGAR.
"""

import logging
import re
import time
from datetime import datetime, timezone

import feedparser
import requests
from bs4 import BeautifulSoup

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "PROFITRC Research Bot nicola.research@example.com"  # SEC requires User-Agent
    )
}


def _get(url: str, timeout: int = config.REQUEST_TIMEOUT) -> requests.Response | None:
    for attempt in range(3):
        try:
            r = requests.get(url, headers=_HEADERS, timeout=timeout)
            r.raise_for_status()
            return r
        except requests.RequestException as exc:
            logger.warning("GET %s attempt %d: %s", url, attempt + 1, exc)
            time.sleep(2 ** attempt)
    return None


class CatalystVerifier:
    _cik_by_ticker: dict[str, str] | None = None

    @classmethod
    def _ticker_to_cik(cls, ticker: str) -> str | None:
        """Resolve ticker → zero-padded CIK via SEC company_tickers.json (cached)."""
        if cls._cik_by_ticker is None:
            cls._cik_by_ticker = {}
            resp = _get("https://www.sec.gov/files/company_tickers.json", timeout=20)
            if resp is not None:
                try:
                    payload = resp.json()
                    for item in payload.values():
                        sym = str(item.get("ticker", "")).upper()
                        cik = str(item.get("cik_str", "")).zfill(10)
                        if sym and cik:
                            cls._cik_by_ticker[sym] = cik
                except Exception as exc:
                    logger.warning("SEC company_tickers load failed: %s", exc)
        return cls._cik_by_ticker.get(ticker.upper())

    @staticmethod
    def _parse_atom_feed(url: str):
        """Parse Atom/RSS via requests (avoids feedparser SSL issues on some hosts)."""
        resp = _get(url, timeout=20)
        if resp is not None:
            return feedparser.parse(resp.content)
        return feedparser.parse(url)

    # ── Tier Classification ───────────────────────────────────────────────────

    def classify_tier(self, catalyst_text: str, source_url: str = "") -> dict:
        """
        Keyword-based tier classification.
        Precedence: TIER 3 > TIER 1 > TIER 2.

        Returns:
        {
            "tier": 1|2|3,
            "confidence": "HIGH"|"MEDIUM"|"LOW",
            "trigger_keywords": list[str],
            "action": "TRADE"|"SELECTIVE"|"SKIP",
            "source_verified": bool,
            "event_type": str,   # maps to config.CATALYST_SCORES key
        }
        """
        text_lower = catalyst_text.lower()

        # ── TIER 3 (hard skip) ─────────────────────────────────────────────
        tier3_hits = [kw for kw in config.TIER3_KEYWORDS if kw.lower() in text_lower]
        if tier3_hits:
            logger.info("TIER 3 classified: %s", tier3_hits)
            return {
                "tier": 3,
                "confidence": "HIGH",
                "trigger_keywords": tier3_hits,
                "action": "SKIP",
                "source_verified": bool(source_url),
                "event_type": "tier3_auto_skip",
            }

        # ── TIER 1 ──────────────────────────────────────────────────────────
        tier1_hits = [kw for kw in config.TIER1_KEYWORDS if kw.lower() in text_lower]
        if tier1_hits:
            event_type = self._infer_event_type(text_lower, tier=1)
            logger.info("TIER 1 classified: %s → %s", tier1_hits[:3], event_type)
            return {
                "tier": 1,
                "confidence": "HIGH",
                "trigger_keywords": tier1_hits,
                "action": "TRADE",
                "source_verified": bool(source_url),
                "event_type": event_type,
            }

        # ── TIER 2 ──────────────────────────────────────────────────────────
        tier2_hits = [kw for kw in config.TIER2_KEYWORDS if kw.lower() in text_lower]
        if tier2_hits:
            event_type = self._infer_event_type(text_lower, tier=2)
            logger.info("TIER 2 classified: %s → %s", tier2_hits[:3], event_type)
            return {
                "tier": 2,
                "confidence": "MEDIUM",
                "trigger_keywords": tier2_hits,
                "action": "SELECTIVE",
                "source_verified": bool(source_url),
                "event_type": event_type,
            }

        # ── Unclassified → default TIER 2 LOW confidence ────────────────────
        return {
            "tier": 2,
            "confidence": "LOW",
            "trigger_keywords": [],
            "action": "SELECTIVE",
            "source_verified": bool(source_url),
            "event_type": "unknown",
        }

    @staticmethod
    def _infer_event_type(text_lower: str, tier: int) -> str:
        """Map free text to config.CATALYST_SCORES key."""
        patterns = [
            ("fda approves", "fda_approval"),
            ("fda grants", "fda_approval"),
            ("approval letter", "fda_approval"),
            ("pdufa", "pdufa_within_14d"),
            ("department of defense", "dod_contract"),
            ("dod contract", "dod_contract"),
            ("definitive agreement", "signed_contract_8k"),
            ("signed agreement", "signed_contract_8k"),
            ("closes acquisition", "ma_announcement"),
            ("closes merger", "ma_announcement"),
            ("merges with", "ma_announcement"),
            ("earnings", "earnings_beat_guidance"),
            ("term sheet", "signed_contract_8k"),
            ("memorandum of understanding", "mou_nonbinding"),
            ("letter of intent", "mou_nonbinding"),
            ("partnership", "partnership_no_terms"),
            ("collaboration", "partnership_no_terms"),
            ("conference", "conference_7d"),
        ]
        for pattern, event_type in patterns:
            if pattern in text_lower:
                return event_type
        return "signed_contract_8k" if tier == 1 else "partnership_no_terms"

    # ── SEC EDGAR Verification ────────────────────────────────────────────────

    def verify_sec_filing(self, ticker: str) -> dict:
        """
        Checks for recent 8-K filing on SEC EDGAR for a given ticker.
        Uses the EDGAR full-text search API (free, no key required).

        Returns:
        {
            "has_recent_8k": bool,
            "filing_date": str | None,
            "url": str | None,
            "summary": str,
        }
        """
        cik = self._ticker_to_cik(ticker) or ticker.upper()
        feed_url = (
            f"https://www.sec.gov/cgi-bin/browse-edgar"
            f"?action=getcompany&CIK={cik}&type=8-K"
            f"&dateb=&owner=include&count=5&output=atom"
        )

        empty = {"has_recent_8k": False, "filing_date": None, "url": None, "summary": ""}

        feed = self._parse_atom_feed(feed_url)
        if feed.bozo and not feed.entries:
            logger.warning("verify_sec_filing(%s): feed parse issue", ticker)
            return empty

        time.sleep(config.SEC_REQUEST_DELAY)

        if not feed.entries:
            return empty

        latest = feed.entries[0]
        try:
            pub = latest.published  # RFC-2822 string
            pub_dt = datetime(*latest.published_parsed[:6], tzinfo=timezone.utc)
            days_old = (datetime.now(timezone.utc) - pub_dt).days

            title = latest.get("title", "")
            summary = latest.get("summary", "")
            link = latest.get("link", "")

            return {
                "has_recent_8k": days_old <= 30,
                "filing_date": pub,
                "days_old": days_old,
                "url": link,
                "summary": (title + " " + summary)[:800],
            }
        except Exception as exc:
            logger.debug("verify_sec_filing(%s) parse error: %s", ticker, exc)
            return empty

    # ── PDUFA Calendar ────────────────────────────────────────────────────────

    def get_pdufa_dates(self) -> list[dict]:
        """
        Scrapes BioPharmCatalyst FDA calendar for PDUFA dates within 30 days.
        Returns [{"ticker", "drug", "pdufa_date", "days_to_pdufa", "indication"}]
        """
        resp = _get(config.URL_BIOPHARM_CATALYST, timeout=25)
        if resp is None:
            logger.error("get_pdufa_dates: request failed")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        results: list[dict] = []
        today = datetime.now(timezone.utc).date()

        # BioPharmCatalyst table structure: rows with ticker, drug, date, indication
        rows = soup.select("table.fda-table tr, table tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            try:
                ticker_text = cells[0].get_text(strip=True).upper()
                drug = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                date_text = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                indication = cells[3].get_text(strip=True) if len(cells) > 3 else ""

                # Parse date (various formats)
                pdufa_date = None
                for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y", "%B %d, %Y"):
                    try:
                        pdufa_date = datetime.strptime(date_text[:12], fmt).date()
                        break
                    except ValueError:
                        continue

                if pdufa_date is None:
                    continue

                days_to = (pdufa_date - today).days
                if 0 <= days_to <= config.CATALYST_MAX_DAYS:
                    results.append({
                        "ticker": ticker_text,
                        "drug": drug,
                        "pdufa_date": str(pdufa_date),
                        "days_to_pdufa": days_to,
                        "indication": indication,
                        "source": "biopharmcatalyst",
                    })
            except (ValueError, IndexError, AttributeError):
                continue

        logger.info("get_pdufa_dates: %d PDUFA events within %d days", len(results), config.CATALYST_MAX_DAYS)
        return results

    # ── Full verification pipeline ────────────────────────────────────────────

    def verify_candidate(self, ticker: str, catalyst_text: str = "") -> dict:
        """
        Combines classify_tier + verify_sec_filing for a single candidate.
        Returns merged dict with tier, sec_filing data, and final action.
        """
        tier_result = self.classify_tier(catalyst_text)
        sec_result = self.verify_sec_filing(ticker)

        # Upgrade confidence if SEC filing found
        if sec_result["has_recent_8k"] and tier_result["tier"] <= 2:
            tier_result["source_verified"] = True
            # Re-classify if filing text provides stronger evidence
            if sec_result["summary"]:
                enriched = self.classify_tier(
                    catalyst_text + " " + sec_result["summary"]
                )
                if enriched["tier"] < tier_result["tier"]:
                    tier_result = enriched

        return {**tier_result, "sec_filing": sec_result}
