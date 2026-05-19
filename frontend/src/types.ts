export type RegimeName = 'TRADE' | 'SELECTIVE' | 'CAUTION' | 'NO_TRADE'

export interface RegimeComponent {
  value?: number
  score: number
  delta_3d?: number
  ma50?: number
  deviation_pct?: number
  change_5d_pct?: number
  change_3d_pct?: number
  value_pct?: number
  delta_3d_bps?: number
  error?: string
}

export interface Regime {
  regime: RegimeName
  score: number
  components: {
    vix: RegimeComponent
    spy: RegimeComponent
    dxy: RegimeComponent
    yield: RegimeComponent
  }
  fomc_warning: boolean
  megacap_earnings: boolean
  timestamp: string
}

export interface Scorecard {
  ticker: string
  catalyst_score: number
  volume_score: number
  sentiment_score: number
  technical_score: number
  risk_score: number
  total: number
  tier: number
  verdict: 'PROCEED' | 'REVIEW' | 'SKIP'
  flags: string[]
}

export interface TechnicalResult {
  score: number
  pattern: string
  blow_off_top: boolean
  bos: { confirmed: boolean; bos_level?: number; bos_candle_date?: string }
  choch: { detected: boolean; choch_level?: number; date?: string }
  fvg_zones: Array<{ bottom: number; top: number; date: string; filled: boolean }>
  orderblocks: Array<{ bottom: number; top: number; date: string }>
  entry_zone: { low: number | null; high: number | null }
  invalidation: number | null
}

export interface CatalystResult {
  tier: number
  confidence: 'HIGH' | 'MEDIUM' | 'LOW'
  trigger_keywords: string[]
  action: 'TRADE' | 'SELECTIVE' | 'SKIP'
  source_verified: boolean
  event_type: string
  days_to_event?: number
  sec_filing?: {
    has_recent_8k: boolean
    filing_date?: string
    url?: string
    summary?: string
  }
}

export interface RiskPackage {
  shares: number
  dollar_risk: number
  risk_pct_actual: number
  entry_cost: number
  entry_low: number
  entry_high: number
  entry_mid: number
  stop_loss: number
  target1: number
  target2: number
  target3: number
  rr_t1: number
  rr_t2: number
  rr_t3: number
  volatility: number
  tier_adjustment: number
}

export interface Probabilities {
  p_target: number
  p_stop: number
  p_neutral: number
  expected_value: number
  note: string
}

export interface TickerAnalysis {
  ticker: string
  scorecard: Scorecard
  technical: TechnicalResult
  catalyst: CatalystResult
  risk: RiskPackage
  probabilities: Probabilities
  source?: string
  change_pct?: number
  price?: number
}

export interface WatchlistItem {
  ticker: string
  added_date: string
  catalyst: string
  tier: number
  score: number
  entry_zone_low: number | null
  entry_zone_high: number | null
  stop_loss: number | null
  target1: number | null
  target2: number | null
  target3: number | null
  status: 'watching' | 'entered' | 'invalidated' | 'closed'
  catalyst_date: string
  days_to_catalyst: number
  last_updated: string
}

export interface PdufaEntry {
  ticker: string
  drug: string
  pdufa_date: string
  days_to_pdufa: number
  indication: string
  source: string
}

export interface PostMortemEntry {
  id: number
  ticker: string
  entry_date: string
  entry_price: number
  exit_date: string
  exit_price: number
  pnl_pct: number
  outcome: 'win' | 'loss' | 'breakeven'
  catalyst_outcome: string
  lesson: string
  score_at_entry: number
  tier: number
  created_at: string
}
