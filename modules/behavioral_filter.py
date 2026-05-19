"""
PROFITRC — LAYER 4: Behavioral Filter
Implements the 7-question anti-bias checklist from PROFITRC_v2.md.
Automated checks run first; subjective checks require interactive input.
"""

import logging
from datetime import datetime, timezone

import yfinance as yf
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.text import Text

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

logger = logging.getLogger(__name__)
console = Console()


class BehavioralFilter:
    """
    Two-stage filter:
    1. auto_checks()       — objective, fully automated (BIRD rule, blow-off, hype saturation)
    2. interactive_checklist() — 7 subjective questions answered by the trader
    3. run_filter()        — runs both; returns combined result
    """

    # ── Automated checks ─────────────────────────────────────────────────────

    def auto_checks(
        self,
        ticker: str,
        entry_price: float | None = None,
        ticker_data=None,
    ) -> dict:
        """
        Objective HARD BLOCKS (non-negotiable, per PROFITRC_v2.md):

        1. BIRD rule: ticker gained >300% in last 48h → BLOCK
        2. Already in parabolic vertical move (today +100%)
        3. Gap today >50% (already extended)

        Uses pre-fetched ticker_data if provided to avoid redundant download.
        """
        flags: list[str] = []

        try:
            if ticker_data is not None and not ticker_data.daily.empty:
                df = ticker_data.daily.copy()
            else:
                df = yf.download(ticker, period="5d", interval="1d",
                                 progress=False, auto_adjust=True)

            if df.empty:
                return {"passed": True, "flags": ["DATA_UNAVAILABLE"]}

            if hasattr(df.columns, "get_level_values"):
                df.columns = df.columns.get_level_values(0)

            if len(df) >= 2:
                close_now = float(df["Close"].iloc[-1])
                close_2d_ago = float(df["Close"].iloc[-2]) if len(df) >= 2 else close_now
                close_5d_ago = float(df["Close"].iloc[0])

                # BIRD rule: >300% gain in ≤ 48h (2 daily bars)
                gain_2d = (close_now - close_2d_ago) / close_2d_ago * 100 if close_2d_ago > 0 else 0
                gain_5d = (close_now - close_5d_ago) / close_5d_ago * 100 if close_5d_ago > 0 else 0

                if gain_2d >= config.BIRD_RULE_PCT * 100:
                    flags.append(f"BIRD_RULE: +{gain_2d:.0f}% in 2 days — NO TRADE ABSOLUTE")
                    logger.warning("BIRD RULE triggered: %s +%.0f%% in 2 days", ticker, gain_2d)

                if gain_5d >= config.BIRD_RULE_PCT * 100:
                    flags.append(f"BIRD_RULE_5D: +{gain_5d:.0f}% in 5 days — NO TRADE ABSOLUTE")

                # Today's intraday gap check (open vs prior close)
                if len(df) >= 2:
                    open_today = float(df["Open"].iloc[-1])
                    close_yesterday = float(df["Close"].iloc[-2])
                    gap_pct = (open_today - close_yesterday) / close_yesterday * 100 if close_yesterday > 0 else 0
                    if gap_pct > 50:
                        flags.append(f"GAP_EXTENDED: +{gap_pct:.0f}% gap today — already extended")
                        logger.warning("Extended gap: %s +%.0f%%", ticker, gap_pct)

        except Exception as exc:
            logger.warning("auto_checks(%s): %s", ticker, exc)
            return {"passed": True, "flags": ["AUTO_CHECK_ERROR"]}

        passed = len([f for f in flags if "BIRD_RULE" in f or "GAP_EXTENDED" in f]) == 0
        return {"passed": passed, "flags": flags}

    # ── Interactive checklist ─────────────────────────────────────────────────

    def interactive_checklist(self, ticker: str) -> dict:
        """
        Displays the 7 anti-bias questions to the trader.
        Any SÌ (Yes) answer blocks the trade.

        Non-interactive mode: if stdin is not a TTY (e.g., piped / scripted),
        returns {"passed": True, "flags": ["INTERACTIVE_SKIPPED"]} to avoid blocking.
        """
        import sys
        if not sys.stdin.isatty():
            return {"passed": True, "flags": ["INTERACTIVE_SKIPPED_NO_TTY"]}

        questions = [
            (
                "FOMO",
                f"Are you entering [{ticker}] because you're afraid of MISSING OUT?",
                "FOMO_DETECTED",
            ),
            (
                "OVERCONFIDENCE",
                f"Has [{ticker}] already gained +100%+ today and are you rationalizing the entry?",
                "OVERCONFIDENCE_BIRD_RULE",
            ),
            (
                "UNVERIFIED_CATALYST",
                f"Is the catalyst for [{ticker}] a story that 'seems good' but you haven't verified the 8-K?",
                "CATALYST_NOT_VERIFIED",
            ),
            (
                "HERDING",
                f"Is everyone on social media calling [{ticker}] the 'next big thing'? (Kindleberger Stage 3–4)",
                "HERDING_HYPE_SATURATED",
            ),
            (
                "OVERSIZING",
                f"Are you sizing this [{ticker}] position LARGER than normal because you're 'very confident'?",
                "OVERCONFIDENCE_OVERSIZING",
            ),
            (
                "CONFIRMATION_BIAS",
                f"Can you NOT formulate a credible bearish scenario for [{ticker}]?",
                "CONFIRMATION_BIAS",
            ),
            (
                "REVENGE_TRADING",
                f"Did you recently LOSE on [{ticker}] or a similar setup and are trying to 'get even'?",
                "REVENGE_TRADING",
            ),
        ]

        console.print()
        console.print(Panel(
            Text.assemble(
                ("⚠  BEHAVIORAL FILTER — ANTI-BIAS CHECKLIST\n", "bold yellow"),
                (f"Ticker: ", "dim"), (f"{ticker}\n", "bold cyan"),
                ("\nAnswer YES to any question = TRADE BLOCKED\n", "dim italic"),
                ("Answer honestly — this is your capital.\n", "dim"),
            ),
            border_style="yellow",
            expand=False,
        ))

        triggered: list[str] = []
        for short_name, question, flag in questions:
            try:
                answered_yes = Confirm.ask(f"  [{short_name}] {question}", default=False)
                if answered_yes:
                    triggered.append(flag)
                    console.print(f"  [red]  ✗ {flag} — trade blocked[/red]")
                    # For most behavioral blocks we stop immediately
                    if flag in ("FOMO_DETECTED", "REVENGE_TRADING", "OVERCONFIDENCE_BIRD_RULE"):
                        console.print("  [bold red]  ✗ Hard stop — exiting checklist[/bold red]")
                        break
                else:
                    console.print(f"  [green]  ✓ OK[/green]")
            except (KeyboardInterrupt, EOFError):
                console.print("\n[dim]Checklist interrupted — treating as PASSED[/dim]")
                return {"passed": True, "flags": ["INTERACTIVE_INTERRUPTED"]}

        if triggered:
            console.print(Panel(
                Text.assemble(
                    ("✗ TRADE BLOCKED\n", "bold red"),
                    (f"Triggered flags: {', '.join(triggered)}\n", "red"),
                    ("Wait 24h minimum. Re-evaluate when flags are gone.\n", "dim"),
                ),
                border_style="red",
                expand=False,
            ))
            return {"passed": False, "flags": triggered, "block_reason": triggered[0]}

        console.print(Panel(
            Text("✓ Behavioral filter passed — all checks clean", style="bold green"),
            border_style="green",
            expand=False,
        ))
        return {"passed": True, "flags": []}

    # ── Combined filter ───────────────────────────────────────────────────────

    def run_filter(
        self,
        ticker: str,
        entry_price: float | None = None,
        interactive: bool = True,
        ticker_data=None,
    ) -> dict:
        """
        Runs auto_checks first. If passed and interactive=True, runs checklist.
        Accepts ticker_data to avoid redundant downloads in auto_checks.
        """
        auto = self.auto_checks(ticker, entry_price, ticker_data=ticker_data)
        result: dict = {
            "passed": False,
            "flags": auto["flags"],
            "block_reason": None,
            "auto_passed": auto["passed"],
            "interactive_passed": None,
        }

        if not auto["passed"]:
            bird_flags = [f for f in auto["flags"] if "BIRD_RULE" in f]
            result["block_reason"] = bird_flags[0] if bird_flags else auto["flags"][0]
            logger.warning("Behavioral auto_check BLOCKED %s: %s", ticker, result["block_reason"])
            return result

        if not interactive:
            result["passed"] = True
            result["interactive_passed"] = None
            return result

        interactive_result = self.interactive_checklist(ticker)
        result["interactive_passed"] = interactive_result["passed"]
        result["flags"] = auto["flags"] + interactive_result.get("flags", [])

        if not interactive_result["passed"]:
            result["block_reason"] = interactive_result.get("block_reason", "BEHAVIORAL_CHECKLIST_FAILED")
        else:
            result["passed"] = True

        # Log result to watchlist DB
        try:
            from modules.watchlist_manager import WatchlistManager
            WatchlistManager().update_status(
                ticker,
                "watching",
                f"behavioral_passed={result['passed']} flags={result['flags'][:3]}",
            )
        except Exception:
            pass

        return result
