"""
PROFITRC — FastAPI backend
Exposes PROFITRC Python modules as REST endpoints.
Also serves the pre-built React frontend from /static.
"""

import asyncio
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from modules.regime_gate import RegimeGate
from modules.scanner import Scanner
from modules.scorer import Scorer
from modules.technical_analyzer import TechnicalAnalyzer
from modules.catalyst_verifier import CatalystVerifier
from modules.risk_manager import RiskManager
from modules.watchlist_manager import WatchlistManager
import config

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=4)

app = FastAPI(title="PROFITRC API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Shared instances (stateless modules, safe to reuse) ──────────────────────
_regime_gate = RegimeGate()
_scanner = Scanner()
_scorer = Scorer()
_tech = TechnicalAnalyzer()
_catalyst_v = CatalystVerifier()
_wm = WatchlistManager()


# ── Pydantic models ───────────────────────────────────────────────────────────

class TradeLogRequest(BaseModel):
    ticker: str
    entry_date: str = ""
    entry_price: float
    exit_date: str = ""
    exit_price: float
    catalyst_outcome: str = ""
    lesson: str = ""
    score_at_entry: int = 0
    tier: int = 2


class StatusUpdate(BaseModel):
    status: str
    notes: str = ""


class CapitalRequest(BaseModel):
    capital: float = 10_000.0


# ── Helpers ───────────────────────────────────────────────────────────────────

def _run_sync(fn, *args):
    """Run a blocking function in a thread pool to avoid blocking the event loop."""
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(executor, fn, *args)


def _build_ticker_analysis(ticker: str, capital: float = 10_000.0) -> dict:
    """Full per-ticker pipeline (sync, runs in executor)."""
    ticker = ticker.upper()
    sec = _catalyst_v.verify_sec_filing(ticker)
    cat = _catalyst_v.classify_tier(sec.get("summary", ""), sec.get("url", ""))
    cat["sec_filing"] = sec
    cat["days_to_event"] = 7

    tech = _tech.get_technical_score(ticker)

    rvol = _scanner.calculate_rvol(ticker)
    cat["blow_off_top"] = tech.get("blow_off_top", False)

    card = _scorer.score_ticker(
        ticker=ticker,
        catalyst_data=cat,
        rvol=rvol,
        technical_score=tech.get("score", 0),
    )

    rm = RiskManager(capital=capital)
    entry_zone = tech.get("entry_zone", {})
    entry_low = entry_zone.get("low") or 5.0
    entry_high = entry_zone.get("high") or 5.5
    stop = tech.get("invalidation") or (entry_low * 0.75)

    risk = rm.build_risk_package(
        ticker=ticker,
        entry_low=entry_low,
        entry_high=entry_high,
        stop_price=stop,
        tier=cat.get("tier", 2),
    )

    from output.trade_card import TradeCardGenerator
    probs = TradeCardGenerator().estimate_probabilities(
        entry=(entry_low + entry_high) / 2,
        target1=risk.get("target1", entry_high * 1.3),
        stop=stop,
        volatility=risk.get("volatility", 0.80),
    )

    return {
        "ticker": ticker,
        "scorecard": card.to_dict(),
        "technical": tech,
        "catalyst": cat,
        "risk": risk,
        "probabilities": probs,
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/api/regime")
async def get_regime():
    """Current macro regime + 4-indicator breakdown."""
    try:
        data = await _run_sync(_regime_gate.get_regime)
        return data
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/scan/{phase}")
async def run_scan(phase: int, body: CapitalRequest = CapitalRequest()):
    """
    Run a scan phase (0–3). Returns candidates that passed all filters.
    phase 0 = AH evening, 1 = premarket, 2 = opening, 3 = midday
    Non-blocking: runs in thread pool.
    """
    if phase not in (0, 1, 2, 3):
        raise HTTPException(400, "phase must be 0–3")

    def _scan():
        regime = _regime_gate.get_regime()
        if regime["regime"] == "NO_TRADE":
            return {"regime": regime, "candidates": [], "skipped": 0,
                    "message": "NO_TRADE regime — system in standby"}

        raw = _scanner.run_phase_scan(phase)
        results = []
        for c in raw:
            ticker = c.get("ticker")
            if not ticker:
                continue
            try:
                analysis = _build_ticker_analysis(ticker, body.capital)
                analysis["source"] = c.get("source", "")
                analysis["change_pct"] = c.get("change_pct", 0)
                analysis["price"] = c.get("price")
                if analysis["scorecard"]["verdict"] != "SKIP":
                    results.append(analysis)
            except Exception as ex:
                logger.warning("scan skip %s: %s", ticker, ex)

        return {"regime": regime, "candidates": results,
                "raw_count": len(raw), "passed_count": len(results)}

    try:
        result = await _run_sync(_scan)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/analyze/{ticker}")
async def analyze_ticker(ticker: str, capital: float = 10_000.0):
    """Full pipeline analysis for a single ticker."""
    try:
        result = await _run_sync(_build_ticker_analysis, ticker.upper(), capital)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/watchlist")
async def get_watchlist():
    """Active watchlist from SQLite."""
    return _wm.get_active_watchlist()


@app.patch("/api/watchlist/{ticker}")
async def update_ticker_status(ticker: str, body: StatusUpdate):
    valid = ("watching", "entered", "invalidated", "closed")
    if body.status not in valid:
        raise HTTPException(400, f"status must be one of {valid}")
    _wm.update_status(ticker.upper(), body.status, body.notes)
    return {"ok": True, "ticker": ticker.upper(), "status": body.status}


@app.delete("/api/watchlist/{ticker}")
async def remove_ticker(ticker: str):
    _wm.update_status(ticker.upper(), "closed", "removed via UI")
    return {"ok": True}


@app.get("/api/postmortem")
async def get_postmortem():
    """All logged trade results."""
    import sqlite3
    from pathlib import Path
    db_path = Path(ROOT) / config.DB_POSTMORTEM
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM postmortem ORDER BY created_at DESC LIMIT 100").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/postmortem")
async def log_trade(body: TradeLogRequest):
    _wm.log_trade_result(body.model_dump())
    return {"ok": True}


@app.get("/api/pdufa")
async def get_pdufa():
    """PDUFA dates from BioPharmCatalyst (within 30 days)."""
    try:
        data = await _run_sync(_catalyst_v.get_pdufa_dates)
        return data
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Serve React frontend ──────────────────────────────────────────────────────
STATIC_DIR = ROOT / "frontend" / "dist"
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        index = STATIC_DIR / "index.html"
        return FileResponse(index)
else:
    @app.get("/")
    async def root():
        return {"status": "ok", "message": "PROFITRC API running. Frontend not built yet."}
