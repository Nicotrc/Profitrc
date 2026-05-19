"""
PROFITRC — Entry Point & Orchestrator

Modes:
  python main.py                    → full scheduler (all phases)
  python main.py --scan phase0      → run Phase 0 (AH evening scan) now
  python main.py --scan phase1      → run Phase 1 (premarket)
  python main.py --scan phase2      → run Phase 2 (opening)
  python main.py --scan phase3      → run Phase 3 (midday)
  python main.py --watchlist        → display active watchlist
  python main.py --postmortem       → display post-mortem log
  python main.py --regime           → show current regime only
  python main.py --ticker ACHV      → full analysis on single ticker
  python main.py --capital 10000    → override capital (default 10,000)
"""

import argparse
import logging
import logging.handlers
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import schedule
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# ── bootstrap path ────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

import config
from modules.regime_gate import RegimeGate
from modules.scanner import Scanner
from modules.scorer import Scorer
from modules.technical_analyzer import TechnicalAnalyzer
from modules.catalyst_verifier import CatalystVerifier
from modules.behavioral_filter import BehavioralFilter
from modules.risk_manager import RiskManager
from modules.alert_engine import AlertEngine
from modules.watchlist_manager import WatchlistManager
from modules.data_cache import DataCache
from output.trade_card import TradeCardGenerator

load_dotenv()
console = Console()


# ── Logging setup ─────────────────────────────────────────────────────────────

def _setup_logging() -> None:
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Console handler (WARNING+ only to avoid noise)
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    root.addHandler(ch)

    # Rotating file handler
    fh = logging.handlers.RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
    )
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    root.addHandler(fh)


# ── Core pipeline ─────────────────────────────────────────────────────────────

def run_pipeline(
    phase: int,
    capital: float = 10_000.0,
    interactive: bool = True,
) -> list[dict]:
    """
    Full PROFITRC decision pipeline for a given scan phase.
    Returns list of setup dicts that passed all 4 layers.
    """
    console.print()
    console.print(Panel(
        Text.assemble(
            ("PROFITRC\n", "bold cyan"),
            (f"Phase {phase} Scan  |  ", "dim"),
            (datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "dim"),
        ),
        border_style="cyan",
        expand=False,
        title="[bold cyan]PROFITRC v2.0[/bold cyan]",
    ))

    gate = RegimeGate()
    scanner = Scanner()
    scorer = Scorer()
    tech = TechnicalAnalyzer()
    catalyst_v = CatalystVerifier()
    behavior = BehavioralFilter()
    risk_mgr = RiskManager(capital=capital)
    alert_eng = AlertEngine()
    wm = WatchlistManager()
    card_gen = TradeCardGenerator()

    # ── LAYER 0: Regime Gate ──────────────────────────────────────────────────
    regime = gate.get_regime()
    _print_regime(regime)

    if regime["regime"] == "NO_TRADE":
        console.print(Panel(
            Text("🚫  NO_TRADE regime — system in standby. Cash is a position.", style="bold red"),
            border_style="red", expand=False,
        ))
        return []

    # ── LAYER 1: Scan ─────────────────────────────────────────────────────────
    console.print(f"\n[bold yellow]► Phase {phase} scan running…[/bold yellow]")
    raw_candidates = scanner.run_phase_scan(phase)

    if not raw_candidates:
        console.print("[dim]  No candidates from scan. Try again later.[/dim]")
        return []

    console.print(f"  [dim]{len(raw_candidates)} raw candidates found[/dim]")

    # ── Process each candidate ────────────────────────────────────────────────
    passed: list[dict] = []
    skipped: list[dict] = []
    data_cache = DataCache()

    for c in raw_candidates:
        ticker = c.get("ticker")
        if not ticker:
            continue

        try:
            ticker_data = data_cache.get(ticker)
            if ticker_data.rvol > 0:
                c["rvol"] = ticker_data.rvol

            result = _process_candidate(
                ticker=ticker,
                candidate=c,
                regime=regime,
                scorer=scorer,
                tech=tech,
                catalyst_v=catalyst_v,
                behavior=behavior,
                risk_mgr=risk_mgr,
                card_gen=card_gen,
                alert_eng=alert_eng,
                wm=wm,
                interactive=interactive,
                ticker_data=ticker_data,
            )
            if result:
                passed.append(result)
            else:
                skipped.append({"ticker": ticker, "reason": "pipeline_filter"})

        except Exception as exc:
            logging.getLogger(__name__).error("Pipeline error for %s: %s", ticker, exc)
            skipped.append({"ticker": ticker, "reason": str(exc)})
        finally:
            time.sleep(config.REQUEST_DELAY)

    # ── Summary ───────────────────────────────────────────────────────────────
    _print_summary(raw_candidates, passed, skipped)

    # ── Purge stale watchlist entries ─────────────────────────────────────────
    wm.purge_stale()

    return passed


def _process_candidate(
    ticker: str,
    candidate: dict,
    regime: dict,
    scorer: Scorer,
    tech: TechnicalAnalyzer,
    catalyst_v: CatalystVerifier,
    behavior: BehavioralFilter,
    risk_mgr: RiskManager,
    card_gen: TradeCardGenerator,
    alert_eng: AlertEngine,
    wm: WatchlistManager,
    interactive: bool,
    ticker_data=None,
) -> dict | None:
    """
    Runs the full 4-layer pipeline on a single candidate.
    Returns setup dict if all layers pass, None if any layer skips.
    """
    console.print(f"\n  [cyan]→ Analyzing {ticker}…[/cyan]")

    # ── Catalyst info from candidate or SEC ──────────────────────────────────
    catalyst_text = candidate.get("summary", "") or candidate.get("catalyst", "")
    catalyst_data = catalyst_v.verify_candidate(ticker, catalyst_text)
    catalyst_data["days_to_event"] = candidate.get("days_to_catalyst", 99)

    if catalyst_data["tier"] == 3:
        console.print(f"    [red]✗ TIER 3 catalyst — SKIP[/red]")
        return None

    # Enforce SELECTIVE regime: only TIER 1 allowed
    if regime["regime"] == "SELECTIVE" and catalyst_data["tier"] != 1:
        console.print(f"    [yellow]✗ SELECTIVE regime — TIER {catalyst_data['tier']} not allowed[/yellow]")
        return None

    # ── Technical analysis ────────────────────────────────────────────────────
    tech_result = tech.get_technical_score(ticker, ticker_data=ticker_data)

    if tech_result.get("blow_off_top"):
        console.print(f"    [red]✗ Blow-off top detected — SKIP (hard rule)[/red]")
        return None

    # ── Scoring ───────────────────────────────────────────────────────────────
    rvol = (ticker_data.rvol if ticker_data else None) or candidate.get("rvol") or scanner_rvol_or_zero(ticker)
    catalyst_data["blow_off_top"] = tech_result.get("blow_off_top", False)

    scorecard = scorer.score_ticker(
        ticker=ticker,
        catalyst_data=catalyst_data,
        rvol=rvol,
        technical_score=tech_result.get("score", 0),
        ticker_data=ticker_data,
    )

    if scorecard.verdict == "SKIP":
        skip_reason = next((f for f in scorecard.flags if "SKIP_REASON" in f), "score_too_low")
        console.print(f"    [red]✗ Score={scorecard.total}/100 — SKIP ({skip_reason})[/red]")
        return None

    console.print(
        f"    [green]✓ Score={scorecard.total}/100  TIER {catalyst_data['tier']}  "
        f"verdict={scorecard.verdict}[/green]"
    )

    # ── Behavioral filter (auto only for non-interactive runs) ────────────────
    entry_zone = tech_result.get("entry_zone", {})
    entry_mid_approx = (
        ((entry_zone.get("low") or 0) + (entry_zone.get("high") or 0)) / 2
        or candidate.get("price", 5.0)
    )

    behavioral = behavior.run_filter(
        ticker,
        entry_price=entry_mid_approx,
        interactive=interactive,
        ticker_data=ticker_data,
    )

    if not behavioral["passed"]:
        console.print(
            f"    [red]✗ Behavioral filter BLOCKED — {behavioral.get('block_reason')}[/red]"
        )
        return None

    # ── Risk package ──────────────────────────────────────────────────────────
    last_price = None
    if ticker_data is not None and not ticker_data.daily.empty:
        last_price = float(ticker_data.daily["Close"].iloc[-1])
    entry_low, entry_high, stop_price = risk_mgr.normalize_long_levels(
        entry_zone.get("low"),
        entry_zone.get("high"),
        tech_result.get("invalidation"),
        last_price=last_price or entry_mid_approx,
    )

    risk_pkg = risk_mgr.build_risk_package(
        ticker=ticker,
        entry_low=entry_low,
        entry_high=entry_high,
        stop_price=stop_price,
        tier=catalyst_data["tier"],
        ticker_data=ticker_data,
    )
    risk_pkg["behavioral_passed"] = behavioral["passed"]
    risk_pkg["behavioral_block_reason"] = behavioral.get("block_reason")

    # ── Trade Card ────────────────────────────────────────────────────────────
    card_gen.generate(
        ticker=ticker,
        regime=regime,
        scorecard=scorecard,
        technical=tech_result,
        catalyst=catalyst_data,
        risk=risk_pkg,
    )

    # ── Alert ─────────────────────────────────────────────────────────────────
    alert_candidate = {
        "ticker": ticker,
        "rvol": rvol,
        "tier": catalyst_data["tier"],
        "verdict": scorecard.verdict,
        "sentiment_flag": next((f for f in scorecard.flags if "SENTIMENT" in f), ""),
        "technical_pattern": tech_result.get("pattern", ""),
        "days_to_catalyst": catalyst_data.get("days_to_event", 99),
        "change_pct": candidate.get("change_pct", 0),
    }
    alert_eng.check_and_fire_alerts([alert_candidate])

    return {
        "ticker": ticker,
        "scorecard": scorecard.to_dict(),
        "technical": tech_result,
        "catalyst": catalyst_data,
        "risk": risk_pkg,
        "regime": regime["regime"],
    }


def scanner_rvol_or_zero(ticker: str) -> float:
    """Lightweight RVOL fetch with silent failure."""
    try:
        return Scanner().calculate_rvol(ticker)
    except Exception:
        return 0.0


# ── Single-ticker analysis ────────────────────────────────────────────────────

def analyze_ticker(ticker: str, capital: float = 10_000.0) -> None:
    """
    python main.py --ticker ACHV
    Runs the full pipeline on a single ticker regardless of scan phase.
    Uses DataCache to avoid redundant yfinance downloads.
    """
    gate = RegimeGate()
    regime = gate.get_regime()
    _print_regime(regime)

    scorer = Scorer()
    tech = TechnicalAnalyzer()
    catalyst_v = CatalystVerifier()
    behavior = BehavioralFilter()
    risk_mgr = RiskManager(capital=capital)
    alert_eng = AlertEngine()
    wm = WatchlistManager()
    card_gen = TradeCardGenerator()

    data_cache = DataCache()
    ticker_data = data_cache.get(ticker.upper())

    current_price = (
        ticker_data.info.get("currentPrice")
        or ticker_data.info.get("regularMarketPrice")
        or 5.0
    )

    sec_filing = catalyst_v.verify_sec_filing(ticker)
    catalyst_data = catalyst_v.classify_tier(
        sec_filing.get("summary", ""),
        sec_filing.get("url", ""),
    )
    catalyst_data["sec_filing"] = sec_filing
    catalyst_data["days_to_event"] = 7

    _process_candidate(
        ticker=ticker.upper(),
        candidate={"ticker": ticker, "price": current_price},
        regime=regime,
        scorer=scorer,
        tech=tech,
        catalyst_v=catalyst_v,
        behavior=behavior,
        risk_mgr=risk_mgr,
        card_gen=card_gen,
        alert_eng=alert_eng,
        wm=wm,
        interactive=True,
        ticker_data=ticker_data,
    )


# ── Rich helpers ──────────────────────────────────────────────────────────────

def _print_regime(regime: dict) -> None:
    regime_name = regime.get("regime", "UNKNOWN")
    style_map = {
        "TRADE":     ("bold green", "🟢"),
        "SELECTIVE": ("bold yellow", "🟡"),
        "CAUTION":   ("bold orange1", "🟠"),
        "NO_TRADE":  ("bold red", "🔴"),
    }
    style, emoji = style_map.get(regime_name, ("white", "•"))
    score = regime.get("score", 0)

    comp = regime.get("components", {})
    body = Text()
    body.append(f"{emoji} Regime: ", "dim")
    body.append(f"{regime_name}  ", style)
    body.append(f"(score {score:+d}/4)\n", "dim")
    body.append("─" * 36 + "\n", "dim")

    labels = {"vix": "VIX", "spy": "SPY vs MA50", "dxy": "DXY", "yield": "10Y Yield"}
    for key, label in labels.items():
        c = comp.get(key, {})
        s = c.get("score", 0)
        s_style = "green" if s > 0 else "red" if s < 0 else "yellow"
        body.append(f"  {label:<14} ", "dim")
        body.append(f"{s:+d}", s_style)
        val_str = ""
        if key == "vix" and c.get("value"):
            val_str = f"  (VIX={c['value']:.1f}  Δ3d={c['delta_3d']:+.1f})"
        elif key == "spy" and c.get("value"):
            val_str = f"  (${c['value']:.1f}  MA50=${c['ma50']:.1f})"
        elif key == "dxy" and c.get("value"):
            val_str = f"  (DXY={c['value']:.2f}  Δ5d={c['change_5d_pct']:+.2f}%)"
        elif key == "yield" and c.get("value_pct"):
            val_str = f"  ({c['value_pct']:.2f}%  Δ3d={c['delta_3d_bps']:+.0f}bps)"
        body.append(val_str + "\n", "dim")

    if regime.get("fomc_warning"):
        body.append("⚠  FOMC meeting within 48h — reduce exposure\n", "bold red")
    if regime.get("megacap_earnings"):
        body.append("⚠  Mega-cap earnings this week\n", "yellow")

    console.print(Panel(body, title="[bold]Market Regime[/bold]", border_style=style.split()[-1], expand=False))


def _print_summary(raw: list, passed: list, skipped: list) -> None:
    body = Text()
    body.append(f"Scanned:  {len(raw)} candidates\n", "dim")
    body.append(f"Passed:   ", "dim")
    body.append(f"{len(passed)}", "bold green" if passed else "dim")
    body.append(" setup(s) generated\n", "dim")
    body.append(f"Skipped:  {len(skipped)}\n", "dim")

    if skipped[:5]:
        body.append("Skip reasons:\n", "dim")
        for s in skipped[:5]:
            body.append(f"  {s.get('ticker','?')} → {s.get('reason','unknown')}\n", "dim")

    console.print(Panel(body, title="[bold]Scan Summary[/bold]", border_style="cyan", expand=False))


# ── Scheduler ─────────────────────────────────────────────────────────────────

def _make_scheduler(capital: float) -> None:
    """Sets up daily schedule for all 4 phases (EST times)."""

    schedule.every().day.at("16:00").do(run_pipeline, phase=0, capital=capital, interactive=False)
    schedule.every().day.at("04:00").do(run_pipeline, phase=1, capital=capital, interactive=False)
    schedule.every().day.at("09:35").do(run_pipeline, phase=2, capital=capital, interactive=False)
    schedule.every().day.at("11:00").do(run_pipeline, phase=3, capital=capital, interactive=False)

    console.print(Panel(
        Text.assemble(
            ("PROFITRC scheduler running\n", "bold green"),
            ("Press Ctrl+C to stop\n", "dim"),
            (f"\nPhase 0: 16:00 EST  (AH evening scan)\n", "dim"),
            (f"Phase 1: 04:00 EST  (premarket)\n", "dim"),
            (f"Phase 2: 09:35 EST  (opening)\n", "dim"),
            (f"Phase 3: 11:00 EST  (midday)\n", "dim"),
        ),
        border_style="green", expand=False,
        title="[bold green]Scheduler Active[/bold green]",
    ))

    while True:
        schedule.run_pending()
        time.sleep(30)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    _setup_logging()

    parser = argparse.ArgumentParser(
        prog="profitrc",
        description="PROFITRC — Speculative Trading Intelligence System",
    )
    parser.add_argument(
        "--scan",
        choices=["phase0", "phase1", "phase2", "phase3"],
        help="Run a specific scan phase immediately",
    )
    parser.add_argument(
        "--ticker",
        metavar="TICKER",
        help="Run full analysis on a single ticker",
    )
    parser.add_argument(
        "--watchlist",
        action="store_true",
        help="Display current watchlist",
    )
    parser.add_argument(
        "--postmortem",
        action="store_true",
        help="Display post-mortem log",
    )
    parser.add_argument(
        "--regime",
        action="store_true",
        help="Show current market regime only",
    )
    parser.add_argument(
        "--capital",
        type=float,
        default=10_000.0,
        metavar="AMOUNT",
        help="Trading capital in USD (default: 10,000)",
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Skip interactive behavioral checklist (useful for automation)",
    )

    args = parser.parse_args()
    interactive = not args.no_interactive

    if args.watchlist:
        WatchlistManager().display_watchlist()

    elif args.postmortem:
        WatchlistManager().generate_postmortem_report()

    elif args.regime:
        gate = RegimeGate()
        regime = gate.get_regime()
        _print_regime(regime)

    elif args.ticker:
        analyze_ticker(args.ticker.upper(), capital=args.capital)

    elif args.scan:
        phase_map = {"phase0": 0, "phase1": 1, "phase2": 2, "phase3": 3}
        phase_num = phase_map[args.scan]
        run_pipeline(phase=phase_num, capital=args.capital, interactive=interactive)

    else:
        # Full scheduler mode
        _make_scheduler(capital=args.capital)


if __name__ == "__main__":
    main()
