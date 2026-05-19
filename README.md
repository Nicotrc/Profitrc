# PROFITRC

**Speculative Trading Intelligence System** — v2.0

A multi-layer event-driven scanner for US small/micro-cap equities ($1–$20, NYSE/NASDAQ).  
Implements the full PROFITRC_v2.md spec: Regime Gate → Catalyst Verification → SMC Technical Analysis → Behavioral Filter.

---

## Quick Start (Docker — no local Python/Node required)

```bash
# 1. Clone
git clone https://github.com/Nicotrc/profitrc.git
cd profitrc

# 2. Run
docker compose up --build

# 3. Open browser
open http://localhost:8080
```

The Docker build compiles the React frontend internally. No Node.js needed on your machine.

---

## CLI (requires Python 3.11+)

```bash
cd profitrc
pip install -r requirements.txt fastapi "uvicorn[standard]"

# Show current market regime
python main.py --regime

# Run evening AH scan (Phase 0)
python main.py --scan phase0

# Analyze single ticker
python main.py --ticker ACHV

# Show active watchlist
python main.py --watchlist

# Show trade post-mortem log
python main.py --postmortem

# Start full scheduler (all phases)
python main.py --capital 25000
```

---

## Architecture

```
LAYER 0  Regime Gate          VIX / SPY / DXY / 10Y → TRADE | SELECTIVE | CAUTION | NO_TRADE
LAYER 1  Scan & Discovery     AH movers · SEC 8-K RSS · Earnings · Premarket gainers
LAYER 2  Catalyst Verifier    TIER 1 / 2 / 3 classification · SEC EDGAR verification
LAYER 3  Technical (SMC)      BOS · CHoCH · FVG · Orderblock · Blow-off top detection
LAYER 4  Behavioral Filter    BIRD rule (>300% auto-block) · 7-question anti-bias checklist
OUTPUT   Setup Card           Score 0–100 · Entry zone · Stop · Targets · R/R · GBM probabilities
```

## Stack

| Layer    | Technology |
|----------|-----------|
| Backend  | Python 3.12 · FastAPI · yfinance · feedparser · BeautifulSoup |
| Frontend | React 18 · Vite · TypeScript · Tailwind CSS |
| Data     | SQLite (watchlist.db · postmortem.db) |
| Deploy   | Docker multi-stage (Node build → Python runtime) |

---

## Environment Variables (optional)

```bash
TELEGRAM_BOT_TOKEN=   # optional: Telegram alert bot
TELEGRAM_CHAT_ID=     # optional: Telegram chat ID
```

---

*Not financial advice. For educational and research purposes only.*
