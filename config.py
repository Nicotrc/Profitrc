"""
PROFITRC — Global Configuration
All parametric thresholds and constants. No business logic here.
"""

# ── Regime Gate ───────────────────────────────────────────────────────────────
VIX_BULLISH: float = 18.0
VIX_BEARISH: float = 25.0
VIX_TREND_WINDOW: int = 3      # days to evaluate VIX trend direction
VIX_STABLE_BAND: float = 0.5   # ±0.5 pts = "stable" for 3-day delta

SPY_NEUTRAL_BAND: float = 0.01  # ±1% from MA50 = "neutral"
SPY_MA_WINDOW: int = 50

DXY_NEUTRAL_BAND: float = 0.003  # ±0.3% 5-day change = lateral
DXY_BEARISH_THRESHOLD: float = 0.005  # >0.5% 3-day rise = bearish

YIELD_NEUTRAL_BPS: float = 5.0   # ±5 bps 3-day change = stable
YIELD_BEARISH_BPS: float = 10.0  # >10 bps 3-day rise = bearish

# Score → Regime mapping
REGIME_TRADE_MIN: int = 3       # score 3-4 → TRADE
REGIME_SELECTIVE_MIN: int = 1   # score 1-2 → SELECTIVE
REGIME_CAUTION_MIN: int = -1    # score -1 to 0 → CAUTION
# below -1 → NO_TRADE

FOMC_WARNING_DAYS: int = 2      # warn if FOMC within N days

# ── Scanner / Discovery ───────────────────────────────────────────────────────
PRICE_MIN: float = 1.0
PRICE_MAX: float = 20.0
FLOAT_MAX_TIER1: int = 15_000_000   # 15M
FLOAT_MAX_TIER2: int = 30_000_000   # 30M

RVOL_MIN: float = 5.0               # minimum relative volume to qualify
RVOL_WINDOW: int = 20               # days for avg volume baseline

EPS_BEAT_MIN_PCT: float = 25.0      # >25% EPS surprise to qualify
REVENUE_BEAT_MIN_PCT: float = 20.0  # >20% revenue surprise to qualify

AH_GAP_MAX_PCT: float = 0.50        # reject tickers already gapped >50%
PREMARKET_GAP_MAX_PCT: float = 0.50

WATCHLIST_MAX: int = 3              # max candidates per nightly scan
CATALYST_MAX_DAYS: int = 30         # max days ahead to track a catalyst

# ── Scoring Weights (must total 100) ─────────────────────────────────────────
CATALYST_MAX: int = 25
VOLUME_MAX: int = 25
SENTIMENT_MAX: int = 20
TECHNICAL_MAX: int = 20
RISK_MAX: int = 10

SCORE_THRESHOLD: int = 65           # minimum total score to proceed to Layer 2

# ── Catalyst Scores (individual event values) ─────────────────────────────────
CATALYST_SCORES: dict[str, int] = {
    "signed_contract_8k":       25,
    "fda_approval":             22,
    "earnings_beat_guidance":   20,
    "dod_contract":             22,
    "ma_announcement":          23,
    "pdufa_within_14d":         22,
    "partnership_no_terms":     12,
    "conference_7d":            10,
    "mou_nonbinding":            3,   # TIER 3 → auto-skip
    "catalyst_already_priced":   0,
}

CATALYST_SCORE_MIN_TO_PROCEED: int = 10  # below this → auto-skip

# ── TIER Classification ───────────────────────────────────────────────────────
TIER1_KEYWORDS: list[str] = [
    "signed agreement", "definitive agreement", "contract awarded",
    "fda approves", "fda grants", "fda approved", "approval letter",
    "department of defense", "dod contract", "us army", "us navy", "us air force",
    "term sheet", "binding agreement", "closes acquisition",
    "closes merger", "completes acquisition", "receives purchase order",
]

TIER2_KEYWORDS: list[str] = [
    "memorandum of understanding", "letter of intent",
    "partnership agreement", "collaboration agreement",
    "phase 2", "phase 3", "clinical trial", "phase ii", "phase iii",
    "conference", "product launch", "pilot program",
    "pending regulatory", "subject to approval",
]

TIER3_KEYWORDS: list[str] = [
    "non-binding", "reverse stock split", "at-the-market offering",
    "atm offering", "ai-powered", "rebranding", "name change",
    "changes its name", "announces name", "enters into mou",
    "forward stock split",   # often used for cosmetic float manipulation
    "promotional", "paid advertisement",
]

TIER3_TRIGGERS: list[str] = [
    "MOU", "reverse split", "AI-washing", "pump", "name change"
]

# ── Technical / SMC ───────────────────────────────────────────────────────────
SWING_LOOKBACK: int = 5          # candles each side to define swing point
BOS_MIN_CANDLES_ABOVE: int = 1   # close candles needed above swing high for BOS
FVG_MIN_GAP_PCT: float = 0.005   # min 0.5% gap to qualify as FVG
BLOWOFF_VOLUME_MULTIPLIER: float = 3.0  # volume > N × avg to flag blow-off
BLOWOFF_UPPER_SHADOW_MIN: float = 0.50  # upper shadow ≥ 50% of candle range

# ── Risk Management ───────────────────────────────────────────────────────────
MAX_RISK_PCT: float = 0.02            # 2% of capital per trade
PORTFOLIO_STOP_MONTHLY: float = 0.20  # -20% drawdown → halt all activity
FLOOR_GAIN_PCT: float = 0.08          # trailing stop floor: +8% from entry
KELLY_DIVISOR: int = 4                # quarter-Kelly for position sizing
TIER2_SIZE_FACTOR: float = 0.50       # TIER 2 → 50% of normal size

# ── Alert System ─────────────────────────────────────────────────────────────
ALERT_LOG_FILE: str = "profitrc.log"
ALERT_LOG_MAX_BYTES: int = 10 * 1024 * 1024   # 10 MB
ALERT_LOG_BACKUP_COUNT: int = 5

PRE_CATALYST_ALERT_DAYS: int = 7      # fire PRE_CATALYST alert if within N days

# ── Phase Timings (EST, 24h format) ──────────────────────────────────────────
PHASE_0_TIME: str = "16:00"   # after-hours evening scan
PHASE_1_TIME: str = "04:00"   # pre-market scan
PHASE_2_TIME: str = "09:35"   # opening momentum (silence window 09:30–09:35)
PHASE_3_TIME: str = "11:00"   # midday accumulation
PHASE_4_TIME: str = "16:00"   # AH swing scan (= next day Phase 0)

MARKET_OPEN_SILENCE_START: str = "09:30"  # no alerts during this window (EST)
MARKET_OPEN_SILENCE_END: str = "09:35"

# ── Database ──────────────────────────────────────────────────────────────────
DB_WATCHLIST: str = "data/watchlist.db"
DB_POSTMORTEM: str = "data/postmortem.db"

STALE_CANDIDATE_DAYS: int = 14   # purge watchlist entries older than N days

# ── Data Sources (URLs) ───────────────────────────────────────────────────────
URL_SEC_8K_ATOM: str = (
    "https://www.sec.gov/cgi-bin/browse-edgar"
    "?action=getcurrent&type=8-K&dateb=&owner=include&count=40&output=atom"
)
URL_SEC_COMPANY_FILINGS: str = (
    "https://www.sec.gov/cgi-bin/browse-edgar"
    "?action=getcompany&CIK={cik}&type=8-K&dateb=&owner=include&count=5&output=atom"
)
URL_AH_MOVERS: str = "https://stockmarketwatch.com/movers/afterhours"
URL_PREMARKET_GAINERS: str = "https://stockanalysis.com/markets/premarket/gainers/"
URL_YAHOO_EARNINGS: str = "https://finance.yahoo.com/calendar/earnings"
URL_BIOPHARM_CATALYST: str = "https://www.biopharmcatalyst.com/calendars/fda-calendar"

# Rate limiting (seconds between requests to same host)
REQUEST_DELAY: float = 0.5
SEC_REQUEST_DELAY: float = 0.15   # SEC allows 10 req/sec

# HTTP request timeout (seconds)
REQUEST_TIMEOUT: int = 15

# yfinance tickers for macro indicators
TICKER_VIX: str = "^VIX"
TICKER_SPY: str = "SPY"
TICKER_DXY: str = "DX-Y.NYB"
TICKER_TNX: str = "^TNX"   # 10-year yield (×10 = actual %)

# ── Behavioral Filter ─────────────────────────────────────────────────────────
BIRD_RULE_PCT: float = 3.00   # >300% gain in 48h → hard block (BIRD rule)

# ── Probability Estimation (GBM heuristic) ───────────────────────────────────
MONTE_CARLO_SIMS: int = 10_000
DEFAULT_HOLDING_DAYS: int = 14   # default time horizon for probability estimates
TRADING_DAYS_YEAR: int = 252

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE: str = "profitrc.log"
LOG_MAX_BYTES: int = 10 * 1024 * 1024
LOG_BACKUP_COUNT: int = 5
