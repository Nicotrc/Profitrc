import { useState } from 'react'
import { post } from '../hooks/useApi'
import { TickerAnalysis, RegimeName } from '../types'

const PHASES = [
  { id: 0, label: 'Phase 0', desc: 'AH Evening', time: '16:00 EST' },
  { id: 1, label: 'Phase 1', desc: 'Pre-Market', time: '04:00 EST' },
  { id: 2, label: 'Phase 2', desc: 'Opening', time: '09:35 EST' },
  { id: 3, label: 'Phase 3', desc: 'Midday', time: '11:00 EST' },
]

interface ScanResult {
  regime: { regime: RegimeName; score: number }
  candidates: TickerAnalysis[]
  raw_count: number
  passed_count: number
  message?: string
}

interface Props {
  capital: number
  onSelectTicker: (a: TickerAnalysis) => void
}

export function ScanPanel({ capital, onSelectTicker }: Props) {
  const [activePhase, setActivePhase] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function runScan(phase: number) {
    setLoading(true)
    setActivePhase(phase)
    setError(null)
    setResult(null)
    try {
      const data = await post<ScanResult>(`/api/scan/${phase}`, { capital })
      setResult(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Scan failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Phase buttons */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {PHASES.map(p => (
          <button
            key={p.id}
            onClick={() => runScan(p.id)}
            disabled={loading}
            className={`relative p-3 rounded-lg border text-left transition-all
              ${activePhase === p.id && loading
                ? 'border-accent-cyan/50 bg-accent-cyan/10 text-accent-cyan'
                : 'border-bg-border bg-bg-panel hover:border-slate-500 hover:bg-bg-hover text-slate-300'
              }
              disabled:opacity-60 disabled:cursor-not-allowed`}
          >
            {activePhase === p.id && loading && (
              <span className="absolute top-2 right-2 w-1.5 h-1.5 bg-accent-cyan rounded-full animate-pulse" />
            )}
            <div className="text-xs font-semibold mb-0.5">{p.label}</div>
            <div className="text-[10px] text-slate-500">{p.desc}</div>
            <div className="text-[10px] text-slate-600">{p.time}</div>
          </button>
        ))}
      </div>

      {loading && (
        <div className="text-center py-8 text-slate-500 text-sm animate-pulse">
          Running Phase {activePhase} scan — fetching live data…
        </div>
      )}

      {error && (
        <div className="bg-accent-red/10 border border-accent-red/20 rounded-lg p-3 text-accent-red text-sm">
          {error}
        </div>
      )}

      {result && !loading && (
        <div className="space-y-3 animate-fade-in">
          {/* Summary bar */}
          <div className="flex items-center gap-4 text-[11px] text-slate-500 bg-bg-panel rounded-lg px-4 py-2">
            <span>Scanned: <span className="text-slate-300">{result.raw_count ?? '—'}</span></span>
            <span>Passed: <span className="text-accent-green font-semibold">{result.passed_count ?? result.candidates.length}</span></span>
            {result.message && <span className="text-accent-yellow">{result.message}</span>}
          </div>

          {result.candidates.length === 0 ? (
            <div className="text-center py-6 text-slate-600 text-sm bg-bg-panel rounded-lg border border-bg-border">
              No candidates passed all filters in this scan.
            </div>
          ) : (
            <div className="space-y-2">
              {result.candidates.map(a => (
                <CandidateRow key={a.ticker} analysis={a} onClick={() => onSelectTicker(a)} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function CandidateRow({ analysis, onClick }: { analysis: TickerAnalysis; onClick: () => void }) {
  const { ticker, scorecard, catalyst, risk, probabilities } = analysis
  const verdictColor = scorecard.verdict === 'PROCEED' ? 'text-accent-green'
    : scorecard.verdict === 'REVIEW' ? 'text-accent-yellow' : 'text-accent-red'
  const tierColor = catalyst.tier === 1 ? 'bg-accent-green/10 text-accent-green border-accent-green/30'
    : 'bg-accent-yellow/10 text-accent-yellow border-accent-yellow/30'
  const evPos = (probabilities?.expected_value ?? 0) >= 0

  return (
    <button
      onClick={onClick}
      className="w-full text-left bg-bg-panel border border-bg-border hover:border-slate-500 rounded-lg p-4 transition-all hover:bg-bg-hover group"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-lg font-bold text-accent-cyan group-hover:text-white transition-colors">{ticker}</span>
          <span className={`text-[10px] px-2 py-0.5 rounded border ${tierColor}`}>TIER {catalyst.tier}</span>
          <span className={`text-xs font-semibold ${verdictColor}`}>{scorecard.verdict}</span>
        </div>
        <div className="flex items-center gap-4 text-[11px]">
          <span className="text-slate-500">Score <span className="text-slate-300 font-medium">{scorecard.total}/100</span></span>
          <span className={evPos ? 'text-accent-green' : 'text-accent-red'}>
            EV {evPos ? '+' : ''}${(probabilities?.expected_value ?? 0).toFixed(3)}
          </span>
          <span className="text-slate-600 group-hover:text-slate-400 transition-colors">→</span>
        </div>
      </div>
      <div className="flex items-center gap-6 mt-2 text-[11px] text-slate-500">
        <span>Entry <span className="text-slate-300 number">${risk.entry_low?.toFixed(2)}–${risk.entry_high?.toFixed(2)}</span></span>
        <span>Stop <span className="text-accent-red number">${risk.stop_loss?.toFixed(2)}</span></span>
        <span>T1 <span className="text-accent-green number">${risk.target1?.toFixed(2)}</span> ({risk.rr_t1}R)</span>
        <span className="text-accent-cyan">{analysis.technical?.pattern?.replace(/_/g, ' ')}</span>
      </div>
    </button>
  )
}
