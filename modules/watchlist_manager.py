"""
PROFITRC — Watchlist & Post-Mortem Manager
SQLite persistence for candidates and trade results.
"""

import json
import logging
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich import box

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

logger = logging.getLogger(__name__)
console = Console()

# Ensure data/ directory exists
Path(config.DB_WATCHLIST).parent.mkdir(parents=True, exist_ok=True)
Path(config.DB_POSTMORTEM).parent.mkdir(parents=True, exist_ok=True)


class WatchlistManager:

    def __init__(self):
        self._wl_conn = self._connect(config.DB_WATCHLIST)
        self._pm_conn = self._connect(config.DB_POSTMORTEM)
        self._create_tables()

    # ── Setup ─────────────────────────────────────────────────────────────────

    @staticmethod
    def _connect(path: str) -> sqlite3.Connection:
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self) -> None:
        self._wl_conn.executescript("""
            CREATE TABLE IF NOT EXISTS watchlist (
                ticker            TEXT PRIMARY KEY,
                added_date        TEXT NOT NULL,
                catalyst          TEXT,
                tier              INTEGER DEFAULT 2,
                score             INTEGER DEFAULT 0,
                entry_zone_low    REAL,
                entry_zone_high   REAL,
                stop_loss         REAL,
                target1           REAL,
                target2           REAL,
                target3           REAL,
                status            TEXT DEFAULT 'watching',
                catalyst_date     TEXT,
                days_to_catalyst  INTEGER DEFAULT 0,
                last_updated      TEXT,
                regime_at_add     TEXT,
                notes             TEXT
            );
        """)
        self._wl_conn.commit()

        self._pm_conn.executescript("""
            CREATE TABLE IF NOT EXISTS postmortem (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker            TEXT NOT NULL,
                entry_date        TEXT,
                entry_price       REAL,
                exit_date         TEXT,
                exit_price        REAL,
                pnl_pct           REAL,
                outcome           TEXT,
                catalyst_outcome  TEXT,
                behavioral_flags  TEXT,
                lesson            TEXT,
                score_at_entry    INTEGER,
                tier              INTEGER,
                created_at        TEXT
            );
        """)
        self._pm_conn.commit()

    # ── Watchlist operations ──────────────────────────────────────────────────

    def add_candidate(self, ticker: str, data: dict) -> None:
        """
        Inserts or replaces a candidate in the watchlist.
        If ticker already exists, updates the score and last_updated.
        """
        now = datetime.now(timezone.utc).isoformat()
        try:
            self._wl_conn.execute("""
                INSERT INTO watchlist
                    (ticker, added_date, catalyst, tier, score,
                     entry_zone_low, entry_zone_high, stop_loss,
                     target1, target2, target3,
                     status, catalyst_date, days_to_catalyst,
                     last_updated, regime_at_add, notes)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(ticker) DO UPDATE SET
                    catalyst        = excluded.catalyst,
                    tier            = excluded.tier,
                    score           = excluded.score,
                    entry_zone_low  = excluded.entry_zone_low,
                    entry_zone_high = excluded.entry_zone_high,
                    stop_loss       = excluded.stop_loss,
                    target1         = excluded.target1,
                    target2         = excluded.target2,
                    target3         = excluded.target3,
                    status          = CASE WHEN watchlist.status = 'entered'
                                        THEN 'entered' ELSE excluded.status END,
                    catalyst_date   = excluded.catalyst_date,
                    days_to_catalyst= excluded.days_to_catalyst,
                    last_updated    = excluded.last_updated,
                    notes           = excluded.notes
            """, (
                ticker.upper(),
                now,
                data.get("catalyst", ""),
                data.get("tier", 2),
                data.get("score", 0),
                data.get("entry_zone_low"),
                data.get("entry_zone_high"),
                data.get("stop_loss"),
                data.get("target1"),
                data.get("target2"),
                data.get("target3"),
                data.get("status", "watching"),
                data.get("catalyst_date", ""),
                data.get("days_to_catalyst", 0),
                now,
                data.get("regime", ""),
                data.get("notes", ""),
            ))
            self._wl_conn.commit()
            logger.info("Watchlist: upserted %s (score=%s, tier=%s)", ticker, data.get("score"), data.get("tier"))
        except Exception as exc:
            logger.error("add_candidate(%s): %s", ticker, exc)

    def update_status(self, ticker: str, status: str, notes: str = "") -> None:
        """
        Valid statuses: 'watching' | 'entered' | 'invalidated' | 'closed'
        """
        now = datetime.now(timezone.utc).isoformat()
        self._wl_conn.execute(
            "UPDATE watchlist SET status=?, last_updated=?, notes=? WHERE ticker=?",
            (status, now, notes, ticker.upper()),
        )
        self._wl_conn.commit()
        logger.info("Watchlist: %s → status=%s", ticker, status)

    def purge_stale(self, days: int = config.STALE_CANDIDATE_DAYS) -> int:
        """
        Removes 'watching' candidates added more than `days` ago.
        Per spec: catalysts beyond 14 days = stale = purged.
        Returns count removed.
        """
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        cur = self._wl_conn.execute(
            "DELETE FROM watchlist WHERE status='watching' AND added_date < ?",
            (cutoff,),
        )
        self._wl_conn.commit()
        removed = cur.rowcount
        if removed > 0:
            logger.info("Watchlist: purged %d stale candidates (>%d days)", removed, days)
        return removed

    def get_active_watchlist(self) -> list[dict]:
        """Returns all non-closed candidates ordered by score descending."""
        cur = self._wl_conn.execute(
            "SELECT * FROM watchlist WHERE status != 'closed' ORDER BY score DESC"
        )
        return [dict(row) for row in cur.fetchall()]

    def get_ticker(self, ticker: str) -> dict | None:
        cur = self._wl_conn.execute(
            "SELECT * FROM watchlist WHERE ticker=?", (ticker.upper(),)
        )
        row = cur.fetchone()
        return dict(row) if row else None

    # ── Post-mortem ───────────────────────────────────────────────────────────

    def log_trade_result(self, trade_data: dict) -> None:
        """
        Records a completed trade for post-mortem analysis.
        trade_data keys: ticker, entry_date, entry_price, exit_date, exit_price,
                         outcome, catalyst_outcome, behavioral_flags, lesson,
                         score_at_entry, tier
        """
        now = datetime.now(timezone.utc).isoformat()
        entry = trade_data.get("entry_price", 0)
        exit_ = trade_data.get("exit_price", 0)
        pnl = ((exit_ - entry) / entry * 100) if entry else 0

        outcome = trade_data.get("outcome")
        if not outcome:
            outcome = "win" if pnl > 0 else "loss" if pnl < -1 else "breakeven"

        self._pm_conn.execute("""
            INSERT INTO postmortem
                (ticker, entry_date, entry_price, exit_date, exit_price,
                 pnl_pct, outcome, catalyst_outcome, behavioral_flags,
                 lesson, score_at_entry, tier, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            trade_data.get("ticker", "").upper(),
            trade_data.get("entry_date", ""),
            entry,
            trade_data.get("exit_date", ""),
            exit_,
            round(pnl, 2),
            outcome,
            trade_data.get("catalyst_outcome", ""),
            json.dumps(trade_data.get("behavioral_flags", [])),
            trade_data.get("lesson", ""),
            trade_data.get("score_at_entry", 0),
            trade_data.get("tier", 2),
            now,
        ))
        self._pm_conn.commit()
        logger.info("Post-mortem logged: %s  pnl=%.2f%%  outcome=%s", trade_data.get("ticker"), pnl, outcome)

        # Auto-update watchlist status
        ticker = trade_data.get("ticker")
        if ticker:
            self.update_status(ticker, "closed", f"PnL={pnl:.1f}%")

    def generate_postmortem_report(self) -> None:
        """Prints a rich summary table of all logged trades."""
        cur = self._pm_conn.execute(
            "SELECT * FROM postmortem ORDER BY created_at DESC LIMIT 50"
        )
        rows = cur.fetchall()
        if not rows:
            console.print("[dim]No post-mortem entries found.[/dim]")
            return

        table = Table(
            title="📋 PROFITRC — Post-Mortem Log",
            box=box.ROUNDED,
            show_lines=True,
        )
        table.add_column("Ticker", style="cyan bold")
        table.add_column("Entry Date", style="dim")
        table.add_column("Entry $", justify="right")
        table.add_column("Exit $", justify="right")
        table.add_column("PnL %", justify="right")
        table.add_column("Outcome")
        table.add_column("Catalyst", style="dim")
        table.add_column("Lesson", style="dim", max_width=30)

        win_count = loss_count = 0
        total_pnl = 0.0

        for row in rows:
            pnl = row["pnl_pct"] or 0
            total_pnl += pnl
            outcome = row["outcome"] or ""
            outcome_style = "green" if "win" in outcome else "red" if "loss" in outcome else "yellow"
            if "win" in outcome:
                win_count += 1
            elif "loss" in outcome:
                loss_count += 1

            table.add_row(
                row["ticker"],
                (row["entry_date"] or "")[:10],
                f"${row['entry_price']:.4f}" if row["entry_price"] else "—",
                f"${row['exit_price']:.4f}" if row["exit_price"] else "—",
                f"[{outcome_style}]{pnl:+.1f}%[/{outcome_style}]",
                f"[{outcome_style}]{outcome}[/{outcome_style}]",
                (row["catalyst_outcome"] or "")[:20],
                (row["lesson"] or "")[:30],
            )

        console.print(table)
        total = win_count + loss_count
        win_rate = win_count / total if total else 0
        console.print(
            f"\n[bold]Stats:[/bold] {total} trades | "
            f"[green]{win_count} wins[/green] | "
            f"[red]{loss_count} losses[/red] | "
            f"Win rate: [bold]{win_rate:.0%}[/bold] | "
            f"Avg PnL: [bold]{total_pnl / len(rows):+.1f}%[/bold]"
        )

    # ── Display watchlist ─────────────────────────────────────────────────────

    def display_watchlist(self) -> None:
        """Prints the active watchlist as a rich table."""
        items = self.get_active_watchlist()
        if not items:
            console.print("[dim]Watchlist is empty.[/dim]")
            return

        table = Table(
            title="👁 PROFITRC — Active Watchlist",
            box=box.ROUNDED,
            show_lines=False,
        )
        table.add_column("Ticker", style="cyan bold")
        table.add_column("Score", justify="right")
        table.add_column("Tier", justify="center")
        table.add_column("Status")
        table.add_column("Entry Zone")
        table.add_column("Stop")
        table.add_column("T1")
        table.add_column("Days→Cat", justify="right")
        table.add_column("Added", style="dim")

        for item in items:
            tier = item.get("tier", 2)
            tier_style = "green" if tier == 1 else "yellow" if tier == 2 else "red"
            status = item.get("status", "")
            status_style = "green" if status == "entered" else "yellow" if status == "watching" else "dim"

            entry_low = item.get("entry_zone_low")
            entry_high = item.get("entry_zone_high")
            entry_str = (f"${entry_low:.2f}–${entry_high:.2f}"
                         if entry_low and entry_high else "—")

            table.add_row(
                item["ticker"],
                str(item.get("score", 0)),
                f"[{tier_style}]TIER {tier}[/{tier_style}]",
                f"[{status_style}]{status}[/{status_style}]",
                entry_str,
                f"${item['stop_loss']:.4f}" if item.get("stop_loss") else "—",
                f"${item['target1']:.2f}" if item.get("target1") else "—",
                str(item.get("days_to_catalyst", "—")),
                (item.get("added_date") or "")[:10],
            )

        console.print(table)
        console.print(f"[dim]Total active: {len(items)} | Auto-purge after {config.STALE_CANDIDATE_DAYS} days[/dim]")
