import { useState } from 'react'
import { WatchlistItem, TickerAnalysis } from '../types'
import { patch, del } from '../hooks/useApi'

const STATUS_COLOR: Record<string, string> = {
  watching:    'text-accent-yellow bg-accent-yellow/10 border-accent-yellow/20',
  entered:     'text-accent-green bg-accent-green/10 border-accent-green/20',
  invalidated: 'text-accent-red bg-accent-red/10 border-accent-red/20',
  closed:      'text-slate-500 bg-slate-500/10 border-slate-500/20',
}

interface Props {
  items: WatchlistItem[]
  loading: boolean
  onRefresh: () => void
  onAnalyze: (a: TickerAnalysis) => void
}

export function WatchlistTable({ items, loading, onRefresh, onAnalyze }: Props) {
  const [analyzing, setAnalyzing] = useState<string | null>(null)
  const [updating, setUpdating] = useState<string | null>(null)

  async function handleAnalyze(ticker: string) {
    setAnalyzing(ticker)
    try {
      const res = await fetch(`/api/analyze/${ticker}`)
      const data: TickerAnalysis = await res.json()
      onAnalyze(data)
    } catch (e) {
      console.error(e)
    } finally {
      setAnalyzing(null)
    }
  }

  async function handleStatusChange(ticker: string, status: string) {
    setUpdating(ticker)
    try {
      await patch(`/api/watchlist/${ticker}`, { status })
      onRefresh()
    } finally {
      setUpdating(null)
    }
  }

  async function handleRemove(ticker: string) {
    setUpdating(ticker)
    try {
      await del(`/api/watchlist/${ticker}`)
      onRefresh()
    } finally {
      setUpdating(null)
    }
  }

  if (loading && items.length === 0) {
    return (
      <div className="space-y-2">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-16 bg-bg-panel rounded-lg border border-bg-border animate-pulse" />
        ))}
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="text-center py-12 text-slate-600 border border-bg-border rounded-lg bg-bg-panel">
        <div className="text-2xl mb-2">👁</div>
        <div className="text-sm">Watchlist is empty. Run a scan to add candidates.</div>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center mb-1">
        <span className="text-[11px] text-slate-600">{items.length} active</span>
        <button onClick={onRefresh} className="text-[10px] text-slate-600 hover:text-slate-400 transition-colors">
          ↻ refresh
        </button>
      </div>

      {/* Table header */}
      <div className="hidden sm:grid grid-cols-[80px_50px_60px_120px_100px_100px_80px_auto] gap-2 px-4 py-1 text-[10px] text-slate-600 uppercase tracking-wider">
        <span>Ticker</span>
        <span>Score</span>
        <span>Tier</span>
        <span>Entry Zone</span>
        <span>Stop</span>
        <span>T1</span>
        <span>Status</span>
        <span />
      </div>

      {items.map(item => (
        <div
          key={item.ticker}
          className="bg-bg-panel border border-bg-border rounded-lg px-4 py-3 hover:border-slate-500 transition-colors"
        >
          <div className="flex items-center justify-between gap-3 flex-wrap">
            {/* Ticker + meta */}
            <div className="flex items-center gap-3 min-w-0">
              <span className="text-base font-bold text-accent-cyan w-16 shrink-0">{item.ticker}</span>
              <span className="text-[11px] font-semibold text-slate-400 w-10">{item.score}</span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded border w-14 text-center ${item.tier === 1 ? 'text-accent-green border-accent-green/30 bg-accent-green/10' : 'text-accent-yellow border-accent-yellow/30 bg-accent-yellow/10'}`}>
                TIER {item.tier}
              </span>
            </div>

            {/* Levels */}
            <div className="flex items-center gap-4 text-[11px] text-slate-500 flex-wrap">
              {item.entry_zone_low && item.entry_zone_high && (
                <span className="number">
                  ${item.entry_zone_low.toFixed(2)}–${item.entry_zone_high.toFixed(2)}
                </span>
              )}
              {item.stop_loss && (
                <span className="text-accent-red number">${item.stop_loss.toFixed(2)}</span>
              )}
              {item.target1 && (
                <span className="text-accent-green number">${item.target1.toFixed(2)}</span>
              )}
              <span className={`text-[10px] px-1.5 py-0.5 rounded border ${STATUS_COLOR[item.status] ?? 'text-slate-500'}`}>
                {item.status}
              </span>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => handleAnalyze(item.ticker)}
                disabled={analyzing === item.ticker}
                className="text-[10px] px-2 py-1 bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20 rounded hover:bg-accent-cyan/20 transition-colors disabled:opacity-50"
              >
                {analyzing === item.ticker ? '…' : 'Analyze →'}
              </button>

              {item.status === 'watching' && (
                <button
                  onClick={() => handleStatusChange(item.ticker, 'entered')}
                  disabled={updating === item.ticker}
                  className="text-[10px] px-2 py-1 bg-accent-green/10 text-accent-green border border-accent-green/20 rounded hover:bg-accent-green/20 transition-colors disabled:opacity-50"
                >
                  Enter
                </button>
              )}
              {item.status === 'entered' && (
                <button
                  onClick={() => handleStatusChange(item.ticker, 'closed')}
                  disabled={updating === item.ticker}
                  className="text-[10px] px-2 py-1 bg-slate-500/10 text-slate-400 border border-slate-500/20 rounded hover:bg-slate-500/20 transition-colors disabled:opacity-50"
                >
                  Close
                </button>
              )}
              <button
                onClick={() => handleRemove(item.ticker)}
                disabled={updating === item.ticker}
                className="text-[10px] px-2 py-1 text-slate-600 hover:text-accent-red transition-colors"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Catalyst snippet */}
          {item.catalyst && (
            <div className="mt-1.5 text-[10px] text-slate-600 truncate">{item.catalyst}</div>
          )}
        </div>
      ))}
    </div>
  )
}
