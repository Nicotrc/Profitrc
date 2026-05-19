import { useState, useEffect } from 'react'
import { Regime, RegimeName } from '../types'

const REGIME_COLOR: Record<RegimeName, string> = {
  TRADE:     'text-accent-green border-accent-green',
  SELECTIVE: 'text-accent-yellow border-accent-yellow',
  CAUTION:   'text-accent-orange border-accent-orange',
  NO_TRADE:  'text-accent-red border-accent-red',
}
const REGIME_BG: Record<RegimeName, string> = {
  TRADE:     'bg-accent-green/10',
  SELECTIVE: 'bg-accent-yellow/10',
  CAUTION:   'bg-accent-orange/10',
  NO_TRADE:  'bg-accent-red/10',
}
const REGIME_DOT: Record<RegimeName, string> = {
  TRADE:     'bg-accent-green',
  SELECTIVE: 'bg-accent-yellow',
  CAUTION:   'bg-accent-orange',
  NO_TRADE:  'bg-accent-red',
}

function ScoreDot({ score }: { score: number }) {
  const color = score > 0 ? 'bg-accent-green' : score < 0 ? 'bg-accent-red' : 'bg-accent-yellow'
  return (
    <span className={`inline-flex items-center justify-center w-5 h-5 rounded-sm text-[10px] font-bold text-bg-base ${color}`}>
      {score > 0 ? `+${score}` : score}
    </span>
  )
}

interface Props {
  regime: Regime | null
  loading: boolean
  onRefresh: () => void
}

export function RegimePanel({ regime, loading, onRefresh }: Props) {
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    setElapsed(0)
    const timer = setInterval(() => setElapsed(e => e + 1), 1000)
    return () => clearInterval(timer)
  }, [regime?.timestamp])

  if (loading && !regime) {
    return (
      <div className="bg-bg-surface border border-bg-border rounded-lg p-4 animate-pulse">
        <div className="h-4 bg-bg-panel rounded w-32 mb-3" />
        <div className="h-8 bg-bg-panel rounded w-24" />
      </div>
    )
  }

  if (!regime) return null

  const r = regime.regime
  const indicators = [
    {
      label: 'VIX',
      score: regime.components.vix.score,
      detail: regime.components.vix.value != null
        ? `${regime.components.vix.value.toFixed(1)}  Δ3d ${(regime.components.vix.delta_3d ?? 0) > 0 ? '+' : ''}${(regime.components.vix.delta_3d ?? 0).toFixed(1)}`
        : '—',
    },
    {
      label: 'SPY vs MA50',
      score: regime.components.spy.score,
      detail: regime.components.spy.value != null
        ? `$${regime.components.spy.value.toFixed(1)}  MA50 $${(regime.components.spy.ma50 ?? 0).toFixed(1)}`
        : '—',
    },
    {
      label: 'DXY',
      score: regime.components.dxy.score,
      detail: regime.components.dxy.value != null
        ? `${regime.components.dxy.value.toFixed(2)}  Δ5d ${(regime.components.dxy.change_5d_pct ?? 0) >= 0 ? '+' : ''}${(regime.components.dxy.change_5d_pct ?? 0).toFixed(2)}%`
        : '—',
    },
    {
      label: '10Y Yield',
      score: regime.components.yield.score,
      detail: regime.components.yield.value_pct != null
        ? `${regime.components.yield.value_pct.toFixed(2)}%  Δ3d ${(regime.components.yield.delta_3d_bps ?? 0) >= 0 ? '+' : ''}${(regime.components.yield.delta_3d_bps ?? 0).toFixed(0)}bps`
        : '—',
    },
  ]

  return (
    <div className={`border rounded-lg p-4 ${REGIME_COLOR[r]} ${REGIME_BG[r]}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full animate-pulse-slow ${REGIME_DOT[r]}`} />
          <span className="text-xs text-slate-400 uppercase tracking-widest">Market Regime</span>
        </div>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="text-[10px] text-slate-500 hover:text-slate-300 transition-colors px-2 py-1 rounded border border-bg-border hover:border-slate-500"
        >
          {loading ? '↻ …' : '↻ refresh'}
        </button>
      </div>

      <div className="flex items-baseline gap-3 mb-4">
        <span className={`text-2xl font-bold tracking-tight ${REGIME_COLOR[r]}`}>{r}</span>
        <span className="text-slate-500 text-sm">score {regime.score > 0 ? `+${regime.score}` : regime.score}/4</span>
      </div>

      <div className="grid grid-cols-2 gap-2 mb-3">
        {indicators.map(ind => (
          <div key={ind.label} className="bg-bg-base/60 rounded px-3 py-2 flex items-center justify-between gap-2">
            <div>
              <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">{ind.label}</div>
              <div className="text-[11px] text-slate-400 number">{ind.detail}</div>
            </div>
            <ScoreDot score={ind.score} />
          </div>
        ))}
      </div>

      {(regime.fomc_warning || regime.megacap_earnings) && (
        <div className="flex flex-col gap-1">
          {regime.fomc_warning && (
            <div className="text-[11px] text-accent-red bg-accent-red/10 border border-accent-red/20 rounded px-2 py-1">
              ⚠ FOMC meeting within 48h — reduce exposure
            </div>
          )}
          {regime.megacap_earnings && (
            <div className="text-[11px] text-accent-yellow bg-accent-yellow/10 border border-accent-yellow/20 rounded px-2 py-1">
              ⚠ Mega-cap earnings this week — elevated volatility
            </div>
          )}
        </div>
      )}

      <div className="mt-2 text-[10px] text-slate-600 flex items-center gap-1">
        {elapsed < 60
          ? `Updated ${elapsed}s ago`
          : `Updated ${Math.floor(elapsed / 60)}min ago`}
        {' · '}
        {`Next refresh in ${Math.max(1, Math.ceil((300 - elapsed) / 60))}min`}
      </div>
    </div>
  )
}
