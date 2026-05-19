"""
PROFITRC — Alert Engine
Fires the 6 alert types defined in PROFITRC_v2.md.
Channels: terminal (rich), file log, optional desktop notification.
"""

import json
import logging
import logging.handlers
import os
from datetime import datetime, timezone
from typing import Literal

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

console = Console()
logger = logging.getLogger(__name__)

AlertType = Literal[
    "EARLY_VOLUME",
    "PRE_CATALYST",
    "SOCIAL_ACCELERATION",
    "TECHNICAL_COMPRESSION",
    "REGIME_SHIFT_UP",
    "INVALIDATION",
]

# ── Alert visual config ───────────────────────────────────────────────────────
ALERT_CONFIG: dict[str, dict] = {
    "EARLY_VOLUME": {
        "emoji": "🔴",
        "label": "EARLY VOLUME",
        "style": "bold red",
        "urgency": "IMMEDIATE",
        "border": "red",
    },
    "PRE_CATALYST": {
        "emoji": "🟠",
        "label": "PRE CATALYST",
        "style": "bold dark_orange",
        "urgency": "HIGH",
        "border": "dark_orange",
    },
    "SOCIAL_ACCELERATION": {
        "emoji": "🟡",
        "label": "SOCIAL ACCEL",
        "style": "bold yellow",
        "urgency": "MEDIUM",
        "border": "yellow",
    },
    "TECHNICAL_COMPRESSION": {
        "emoji": "🟡",
        "label": "TECH COMPRESS",
        "style": "bold yellow",
        "urgency": "MEDIUM",
        "border": "yellow",
    },
    "REGIME_SHIFT_UP": {
        "emoji": "🟢",
        "label": "REGIME ↑",
        "style": "bold green",
        "urgency": "OPPORTUNISTIC",
        "border": "green",
    },
    "INVALIDATION": {
        "emoji": "⚫",
        "label": "INVALIDATION — EXIT",
        "style": "bold white on red",
        "urgency": "EXIT_IMMEDIATELY",
        "border": "bright_red",
    },
}


class AlertEngine:

    def __init__(self):
        self._setup_file_logger()
        self._fired_today: set[str] = set()  # deduplicate same alert within session

    def _setup_file_logger(self) -> None:
        """Configures a rotating file handler for alert persistence."""
        file_handler = logging.handlers.RotatingFileHandler(
            config.ALERT_LOG_FILE,
            maxBytes=config.ALERT_LOG_MAX_BYTES,
            backupCount=config.ALERT_LOG_BACKUP_COUNT,
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        )
        # Attach to root logger so all modules write to same file
        root = logging.getLogger()
        if not any(isinstance(h, logging.handlers.RotatingFileHandler) for h in root.handlers):
            root.addHandler(file_handler)

    def _is_silence_window(self) -> bool:
        """Returns True during the market open silence window (09:30–09:35 EST)."""
        from datetime import time as dt_time
        import pytz
        try:
            est = pytz.timezone("America/New_York")
            now_est = datetime.now(est).time()
            start = dt_time(9, 30)
            end = dt_time(9, 35)
            return start <= now_est <= end
        except ImportError:
            # pytz not available — skip silence check
            return False

    def send_alert(
        self,
        alert_type: AlertType,
        ticker: str,
        message: str,
        data: dict | None = None,
    ) -> None:
        """
        Fires an alert to all configured channels.
        Deduplicates: same (alert_type, ticker) fires only once per session.
        Respects the 09:30–09:35 EST silence window (except INVALIDATION).
        """
        if alert_type != "INVALIDATION" and self._is_silence_window():
            logger.debug("Silence window active — suppressing %s for %s", alert_type, ticker)
            return

        dedup_key = f"{alert_type}:{ticker}"
        if dedup_key in self._fired_today and alert_type != "INVALIDATION":
            return
        self._fired_today.add(dedup_key)

        cfg = ALERT_CONFIG.get(alert_type, ALERT_CONFIG["EARLY_VOLUME"])
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # ── Terminal output (rich) ────────────────────────────────────────────
        body = Text()
        body.append(f"{'─' * 38}\n", style="dim")
        body.append(f"Ticker:   ", style="dim")
        body.append(f"{ticker}\n", style="bold cyan")
        body.append(f"Urgency:  ", style="dim")
        body.append(f"{cfg['urgency']}\n", style=cfg["style"])
        body.append(f"Message:  {message}\n")
        body.append(f"Time:     {ts}\n", style="dim")

        if data:
            for k, v in list(data.items())[:6]:
                body.append(f"{k:<10}: {v}\n", style="dim")

        title = f"{cfg['emoji']} {cfg['label']} — {ticker}"
        console.print(Panel(body, title=title, border_style=cfg["border"], expand=False))

        # ── File log ──────────────────────────────────────────────────────────
        log_entry = {
            "ts": ts,
            "type": alert_type,
            "ticker": ticker,
            "urgency": cfg["urgency"],
            "message": message,
            "data": data or {},
        }
        logger.info("ALERT | %s", json.dumps(log_entry))

        # ── Desktop notification (optional, requires plyer) ───────────────────
        try:
            from plyer import notification
            notification.notify(
                title=f"PROFITRC: {cfg['label']} — {ticker}",
                message=message[:200],
                timeout=8,
            )
        except (ImportError, Exception):
            pass  # plyer not installed or platform unsupported

        # ── Telegram (optional, requires BOT_TOKEN + CHAT_ID in .env) ─────────
        self._send_telegram(alert_type, ticker, message, ts)

    def _send_telegram(self, alert_type: str, ticker: str, message: str, ts: str) -> None:
        """Sends Telegram message if BOT_TOKEN and CHAT_ID are set in environment."""
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not token or not chat_id:
            return
        try:
            import requests
            cfg = ALERT_CONFIG.get(alert_type, {})
            text = (
                f"{cfg.get('emoji', '•')} *{cfg.get('label', alert_type)}*\n"
                f"Ticker: `{ticker}`\n"
                f"{message}\n"
                f"_{ts}_"
            )
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
                timeout=5,
            )
        except Exception as exc:
            logger.debug("Telegram send failed: %s", exc)

    # ── Batch check ───────────────────────────────────────────────────────────

    def check_and_fire_alerts(self, candidates: list[dict]) -> None:
        """
        Iterates over scored candidates and fires the appropriate alert(s).
        A single candidate can trigger multiple alert types.
        """
        for c in candidates:
            ticker = c.get("ticker", "UNKNOWN")
            rvol = c.get("rvol", 0)
            tier = c.get("tier", 2)
            verdict = c.get("verdict", "SKIP")
            sentiment_flag = c.get("sentiment_flag", "")
            tech_pattern = c.get("technical_pattern", "")
            days_to_catalyst = c.get("days_to_catalyst", 99)
            is_invalidated = c.get("invalidated", False)
            regime_shift_up = c.get("regime_shift_up", False)

            # Skip anything that doesn't proceed
            if verdict == "SKIP" and not is_invalidated:
                continue

            # INVALIDATION — highest priority
            if is_invalidated:
                self.send_alert(
                    "INVALIDATION",
                    ticker,
                    c.get("invalidation_reason", "Catalyst or structure invalidated — EXIT POSITION"),
                    {"stop_level": c.get("stop_loss"), "current_price": c.get("price")},
                )
                continue

            # EARLY VOLUME — high RVOL without extended breakout
            if rvol >= config.RVOL_MIN:
                change_pct = abs(c.get("change_pct", 0))
                if change_pct < 50:
                    self.send_alert(
                        "EARLY_VOLUME",
                        ticker,
                        f"RVOL {rvol:.1f}x with only {change_pct:.1f}% move — early accumulation window",
                        {"rvol": rvol, "change_pct": change_pct, "tier": tier},
                    )

            # PRE_CATALYST — catalyst within alert window
            if days_to_catalyst <= config.PRE_CATALYST_ALERT_DAYS and tier in (1, 2):
                self.send_alert(
                    "PRE_CATALYST",
                    ticker,
                    f"TIER {tier} catalyst in {days_to_catalyst} day(s)",
                    {"days": days_to_catalyst, "tier": tier},
                )

            # SOCIAL_ACCELERATION
            if sentiment_flag == "SENTIMENT_ACCELERATING":
                self.send_alert(
                    "SOCIAL_ACCELERATION",
                    ticker,
                    "Nascent social acceleration detected — early stage, not saturated",
                    {"source": "yahoo_news"},
                )

            # TECHNICAL_COMPRESSION
            if tech_pattern in ("bos_fvg", "fvg_reclaim", "choch_reversal"):
                self.send_alert(
                    "TECHNICAL_COMPRESSION",
                    ticker,
                    f"Technical pattern: {tech_pattern} — potential breakout incoming",
                    {"pattern": tech_pattern},
                )

            # REGIME_SHIFT_UP
            if regime_shift_up:
                self.send_alert(
                    "REGIME_SHIFT_UP",
                    ticker,
                    "Market regime upgraded — scan window now active",
                    {},
                )

    def fire_portfolio_stop(self, drawdown_pct: float) -> None:
        """Fires a critical alert when the monthly portfolio stop is hit."""
        console.print(
            Panel(
                Text.assemble(
                    ("⛔  PORTFOLIO MONTHLY STOP HIT\n", "bold white on red"),
                    (f"Drawdown: {drawdown_pct:.1%} (threshold: {config.PORTFOLIO_STOP_MONTHLY:.0%})\n", "red"),
                    ("ACTION: Halt all activity 48h. Run full post-mortem. Restart at 50% sizing.\n", "bold"),
                ),
                title="[bold red]CRITICAL RISK ALERT[/bold red]",
                border_style="red",
                expand=False,
            )
        )
        logger.critical("PORTFOLIO_STOP_HIT: drawdown=%.2f%%", drawdown_pct * 100)
