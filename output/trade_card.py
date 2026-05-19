"""
PROFITRC — Setup Card Generator
Renders the full trade card in the PROFITRC_v2.md format using rich.
"""

import logging
import math
from datetime import datetime, timezone

import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
from modules.scorer import ScoreCard

logger = logging.getLogger(__name__)
console = Console()

# ── Regime colour mapping ─────────────────────────────────────────────────────
REGIME_STYLE = {
    "TRADE":     "bold green",
    "SELECTIVE": "bold yellow",
    "CAUTION":   "bold orange1",
    "NO_TRADE":  "bold red",
}

TIER_STYLE = {1: "bold green", 2: "bold yellow", 3: "bold red"}
VERDICT_STYLE = {"PROCEED": "bold green", "REVIEW": "bold yellow", "SKIP": "bold red"}


class TradeCardGenerator:

    def estimate_probabilities(
        self,
        entry: float,
        target1: float,
        stop: float,
        volatility: float = 0.80,
        holding_days: int = config.DEFAULT_HOLDING_DAYS,
    ) -> dict:
        """
        GBM-based heuristic probability estimates (Monte Carlo simplified).

        Uses the analytical normal approximation:
            d_target = ln(target / entry) / (σ * √T)
            d_stop   = ln(stop   / entry) / (σ * √T)

        P(reach target) ≈ Φ(-d_target)  [right tail]
        P(hit stop)     ≈ Φ(d_stop)      [left tail, d_stop is negative]

        This is a fast heuristic — not a proper barrier option pricer.
        Annotated as "stima euristica" per PROFITRC_v2.md.
        """
        try:
            if entry <= 0 or target1 <= entry or stop >= entry:
                return {"p_target": 0.35, "p_stop": 0.35, "p_neutral": 0.30,
                        "expected_value": 0.0, "note": "invalid_levels"}

            T = holding_days / config.TRADING_DAYS_YEAR
            sigma_T = volatility * math.sqrt(T)

            d_target = math.log(target1 / entry) / sigma_T
            d_stop = math.log(stop / entry) / sigma_T  # negative

            from scipy.stats import norm
            p_target = float(norm.sf(d_target))   # P(Z > d_target)
            p_stop = float(norm.cdf(d_stop))       # P(Z < d_stop)
        except ImportError:
            # Fallback without scipy: use quick erf approximation
            def phi(x: float) -> float:
                return 0.5 * (1 + math.erf(x / math.sqrt(2)))
            p_target = 1 - phi(d_target)
            p_stop = phi(d_stop)
        except Exception:
            p_target, p_stop = 0.40, 0.35

        p_target = max(0.05, min(0.95, p_target))
        p_stop = max(0.05, min(0.95, p_stop))
        p_neutral = max(0.0, 1.0 - p_target - p_stop)

        win = target1 - entry
        loss = stop - entry   # negative
        ev = p_target * win + p_stop * loss

        return {
            "p_target": round(p_target, 2),
            "p_stop": round(p_stop, 2),
            "p_neutral": round(p_neutral, 2),
            "expected_value": round(ev, 4),
            "note": "heuristic_gbm",
        }

    def generate(
        self,
        ticker: str,
        regime: dict,
        scorecard: ScoreCard,
        technical: dict,
        catalyst: dict,
        risk: dict,
    ) -> None:
        """
        Renders the full PROFITRC Setup Card to the terminal with rich formatting.
        Also persists to WatchlistManager if available.
        """
        now = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
        regime_name = regime.get("regime", "UNKNOWN")
        tier = catalyst.get("tier", 2)

        # ── Entry / stop / target levels ─────────────────────────────────────
        entry_zone = technical.get("entry_zone", {})
        entry_low = entry_zone.get("low") or risk.get("entry_low")
        entry_high = entry_zone.get("high") or risk.get("entry_high")
        entry_mid = (
            round((entry_low + entry_high) / 2, 4)
            if entry_low and entry_high else None
        )
        stop_loss = technical.get("invalidation") or risk.get("stop_loss")

        # Targets: T1 = +30%, T2 = +60%, T3 = +100% from entry midpoint (heuristic)
        t1 = round(entry_mid * 1.30, 2) if entry_mid else None
        t2 = round(entry_mid * 1.60, 2) if entry_mid else None
        t3 = round(entry_mid * 2.00, 2) if entry_mid else None

        # R/R ratios
        def rr(target: float | None) -> str:
            if target and entry_mid and stop_loss and entry_mid != stop_loss:
                ratio = (target - entry_mid) / (entry_mid - stop_loss)
                return f"{ratio:.1f}:1"
            return "N/A"

        # Probability estimates
        current_price = entry_mid or 0
        volatility = risk.get("volatility", 0.80)
        probs = self.estimate_probabilities(
            entry=current_price or 1.0,
            target1=t1 or (current_price * 1.30),
            stop=stop_loss or (current_price * 0.75),
            volatility=volatility,
        )

        # Position sizing
        shares = risk.get("shares", "N/A")
        dollar_risk = risk.get("dollar_risk", "N/A")

        # ── Header Panel ─────────────────────────────────────────────────────
        header_text = Text()
        header_text.append("PROFITRC SETUP CARD\n", style="bold white")
        header_text.append(f"{'─' * 36}\n", style="dim")
        header_text.append(f"TICKER:  ", style="dim")
        header_text.append(f"{ticker}\n", style="bold cyan")
        header_text.append(f"DATE:    {now}\n", style="dim")
        header_text.append(f"REGIME:  ", style="dim")
        header_text.append(f"{regime_name}", style=REGIME_STYLE.get(regime_name, "white"))
        header_text.append(f"  (score {regime.get('score', 0):+d}/4)\n", style="dim")

        if regime.get("fomc_warning"):
            header_text.append("⚠ FOMC WARNING: meeting within 48h — reduce exposure\n", style="bold red")
        if regime.get("megacap_earnings"):
            header_text.append("⚠ Mega-cap earnings this week — elevated volatility\n", style="yellow")

        # ── Catalyst Panel ────────────────────────────────────────────────────
        cat_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        cat_table.add_column("Key", style="dim", width=18)
        cat_table.add_column("Value")
        cat_text = catalyst.get("trigger_keywords", [])
        cat_summary = (", ".join(cat_text[:3]) if cat_text else catalyst.get("event_type", "N/A"))
        cat_table.add_row("Catalyst", cat_summary[:60])
        cat_table.add_row(
            "Tier",
            Text(f"TIER {tier}", style=TIER_STYLE.get(tier, "white"))
        )
        cat_table.add_row("Action", catalyst.get("action", "N/A"))
        cat_table.add_row("Source verified", "✓" if catalyst.get("source_verified") else "✗")
        if catalyst.get("sec_filing", {}).get("has_recent_8k"):
            cat_table.add_row("SEC 8-K", f"✓ {catalyst['sec_filing'].get('filing_date', '')[:16]}")
        days = catalyst.get("days_to_event", "N/A")
        if isinstance(days, int):
            cat_table.add_row("Days to catalyst", str(days))

        # ── Scoring Panel ─────────────────────────────────────────────────────
        score_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        score_table.add_column("Dimension", style="dim", width=20)
        score_table.add_column("Score", justify="right")
        score_table.add_column("Max", justify="right", style="dim")

        def score_style(val: int, mx: int) -> str:
            pct = val / mx if mx else 0
            return "green" if pct >= 0.7 else "yellow" if pct >= 0.4 else "red"

        def add_score_row(label: str, val: int, mx: int) -> None:
            score_table.add_row(
                label,
                Text(str(val), style=score_style(val, mx)),
                f"/{mx}",
            )

        add_score_row("Catalyst", scorecard.catalyst_score, config.CATALYST_MAX)
        add_score_row("Volume", scorecard.volume_score, config.VOLUME_MAX)
        add_score_row("Sentiment", scorecard.sentiment_score, config.SENTIMENT_MAX)
        add_score_row("Technical", scorecard.technical_score, config.TECHNICAL_MAX)
        add_score_row("Risk", scorecard.risk_score, config.RISK_MAX)
        score_table.add_row("", Text(""), Text(""))
        total_style = score_style(scorecard.total, 100)
        score_table.add_row(
            "[bold]TOTAL[/bold]",
            Text(str(scorecard.total), style=f"bold {total_style}"),
            "/100",
        )
        score_table.add_row(
            "Verdict",
            Text(scorecard.verdict, style=VERDICT_STYLE.get(scorecard.verdict, "white")),
            "",
        )

        # ── Technical Panel ───────────────────────────────────────────────────
        tech_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        tech_table.add_column("Key", style="dim", width=18)
        tech_table.add_column("Value")

        bos = technical.get("bos", {})
        choch = technical.get("choch", {})
        fvgs = technical.get("fvg_zones", [])
        obs = technical.get("orderblocks", [])

        tech_table.add_row("BOS confirmed",
            Text("✓ " + (bos.get("bos_candle_date") or ""), style="green")
            if bos.get("confirmed") else Text("✗", style="red"))
        tech_table.add_row("CHoCH detected",
            Text("✓ " + (choch.get("date") or ""), style="green")
            if choch.get("detected") else Text("✗", style="dim"))
        if fvgs:
            best = fvgs[0]
            tech_table.add_row("FVG zone", f"${best['bottom']:.2f} – ${best['top']:.2f}")
        if obs:
            ob = obs[0]
            tech_table.add_row("Orderblock", f"${ob['bottom']:.2f} – ${ob['top']:.2f}")
        tech_table.add_row("Pattern", technical.get("pattern", "N/A"))
        tech_table.add_row("Blow-off top",
            Text("⚠ YES — DO NOT TRADE", style="bold red")
            if technical.get("blow_off_top") else Text("✓ No", style="green"))

        # ── Trade Plan Panel ──────────────────────────────────────────────────
        plan_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        plan_table.add_column("Key", style="dim", width=18)
        plan_table.add_column("Value")

        if entry_low and entry_high:
            plan_table.add_row("Entry Zone", f"${entry_low:.4f} – ${entry_high:.4f}")
        if stop_loss:
            plan_table.add_row("Stop Loss", f"${stop_loss:.4f}")
        if t1:
            plan_table.add_row("Target 1 (T1)", f"${t1:.2f}  R/R = {rr(t1)}")
        if t2:
            plan_table.add_row("Target 2 (T2)", f"${t2:.2f}  R/R = {rr(t2)}")
        if t3:
            plan_table.add_row("Target 3 (T3)", f"${t3:.2f}+  R/R = {rr(t3)}")
        plan_table.add_row("Horizon", f"7–14 days (adjust per catalyst)")
        plan_table.add_row("Tier sizing",
            f"TIER 1 = full size" if tier == 1 else f"TIER 2 = 50% size")

        # ── Sizing Panel ─────────────────────────────────────────────────────
        sizing_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        sizing_table.add_column("Key", style="dim", width=18)
        sizing_table.add_column("Value")
        sizing_table.add_row("Max $ risk", f"${dollar_risk:.2f}" if isinstance(dollar_risk, float) else str(dollar_risk))
        sizing_table.add_row("Shares", str(shares))
        if entry_mid:
            sizing_table.add_row("Entry cost", f"${entry_mid:.4f} × {shares}" if isinstance(shares, int) else "N/A")

        # ── Scenarios Panel ───────────────────────────────────────────────────
        scen_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        scen_table.add_column("Scenario", style="dim", width=10)
        scen_table.add_column("Description")

        scen_table.add_row(
            Text("BULL", style="bold green"),
            f"Catalyst fires fully → T3 (${t3:.2f}+)" if t3 else "Full catalyst play"
        )
        scen_table.add_row(
            Text("BASE", style="bold yellow"),
            f"Pre-run / partial catalyst → T1–T2 (${t1:.2f}–${t2:.2f})" if t1 and t2 else "Moderate follow-through"
        )
        scen_table.add_row(
            Text("BEAR", style="bold red"),
            f"No follow-through → stop hit (${stop_loss:.4f})" if stop_loss else "Stop hit"
        )

        # ── Probability Panel ─────────────────────────────────────────────────
        prob_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        prob_table.add_column("Metric", style="dim", width=22)
        prob_table.add_column("Value")
        prob_table.add_row("P(reach T1)",
            Text(f"{probs['p_target']:.0%}", style="green" if probs['p_target'] >= 0.45 else "yellow"))
        prob_table.add_row("P(stop hit)",
            Text(f"{probs['p_stop']:.0%}", style="red" if probs['p_stop'] >= 0.40 else "yellow"))
        prob_table.add_row("P(neutral)", f"{probs['p_neutral']:.0%}")
        ev = probs["expected_value"]
        prob_table.add_row(
            "Expected Value (per share)",
            Text(f"${ev:+.4f}", style="green" if ev > 0 else "red")
        )
        prob_table.add_row("[dim]Note[/dim]", "[dim]Heuristic GBM estimate — not a guarantee[/dim]")

        # ── Flags Panel ───────────────────────────────────────────────────────
        flags = scorecard.flags
        flag_text = Text()
        skip_flags = [f for f in flags if "SKIP" in f or "RED" in f or "AUTO" in f]
        info_flags = [f for f in flags if f not in skip_flags]

        if skip_flags:
            flag_text.append("SKIP FLAGS: ", style="bold red")
            flag_text.append(", ".join(skip_flags) + "\n", style="red")
        if info_flags:
            flag_text.append("INFO FLAGS: ", style="dim")
            flag_text.append(", ".join(info_flags[:8]), style="dim")

        # Anti-pattern check result
        behavioral = risk.get("behavioral_passed", None)
        if behavioral is True:
            behavioral_text = Text("✓ PASSED", style="bold green")
        elif behavioral is False:
            reason = risk.get("behavioral_block_reason", "unknown")
            behavioral_text = Text(f"✗ BLOCKED — {reason}", style="bold red")
        else:
            behavioral_text = Text("⏳ Pending interactive check", style="yellow")

        # ── Assemble & print ─────────────────────────────────────────────────
        console.print()
        console.print(Panel(header_text, border_style="cyan", expand=False, title="[bold cyan]PROFITRC[/bold cyan]"))

        grid = Table.grid(expand=True, padding=(0, 2))
        grid.add_column(ratio=1)
        grid.add_column(ratio=1)

        grid.add_row(
            Panel(cat_table, title="[yellow]CATALYST[/yellow]", border_style="yellow"),
            Panel(score_table, title="[cyan]SCORING[/cyan]", border_style="cyan"),
        )
        grid.add_row(
            Panel(tech_table, title="[blue]TECHNICAL STRUCTURE (SMC)[/blue]", border_style="blue"),
            Panel(plan_table, title="[green]TRADE PLAN[/green]", border_style="green"),
        )
        grid.add_row(
            Panel(sizing_table, title="[magenta]SIZING[/magenta]", border_style="magenta"),
            Panel(scen_table, title="[white]SCENARIOS[/white]", border_style="white"),
        )
        grid.add_row(
            Panel(prob_table, title="[cyan]PROBABILITY ESTIMATES[/cyan]", border_style="cyan"),
            Panel(
                Text.assemble(
                    ("ANTI-PATTERN CHECK: ", "dim"), behavioral_text, "\n",
                    ("BEHAVIORAL FILTER:  ", "dim"), behavioral_text,
                    "\n\n",
                    ("FLAGS:\n", "dim"), flag_text,
                ),
                title="[red]FILTER STATUS[/red]",
                border_style="red",
            ),
        )
        console.print(grid)
        console.print()

        # Persist to watchlist
        try:
            from modules.watchlist_manager import WatchlistManager
            wm = WatchlistManager()
            wm.add_candidate(ticker, {
                "catalyst": cat_summary,
                "tier": tier,
                "score": scorecard.total,
                "entry_zone_low": entry_low,
                "entry_zone_high": entry_high,
                "stop_loss": stop_loss,
                "target1": t1,
                "target2": t2,
                "target3": t3,
                "status": "watching",
                "catalyst_date": catalyst.get("sec_filing", {}).get("filing_date", ""),
                "days_to_catalyst": catalyst.get("days_to_event", 0),
            })
        except Exception as exc:
            logger.debug("watchlist persist: %s", exc)
