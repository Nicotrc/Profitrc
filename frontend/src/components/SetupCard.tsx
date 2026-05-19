import { TickerAnalysis } from '../types'

function pct(n: number) { return `${(n * 100).toFixed(0)}%` }
function fmt(n: number | null | undefined, prefix = '$') {
  if (n == null) return '—'
  const decimals = n >= 1 ? 2 : 4
  return `${prefix}${n.toFixed(decimals)}`
}

function ScoreBar({ value, max, color }: { value: number; max: number; color: string }) {
  const w = Math.max(0, Math.min(100, (value / max) * 100))
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-bg-border rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${w}%` }} />
      </div>
      <span className="text-xs number w-8 text-right">{value}/{max}</span>
    </div>
  )
}

function Row({ label, value, valueClass = '' }: { label: string; value: React.ReactNode; valueClass?: string }) {
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-bg-border/50 last:border-0">
      <span className="text-[11px] text-slate-500 uppercase tracking-wider">{label}</span>
      <span className={`text-[12px] font-medium number ${valueClass}`}>{value}</span>
    </div>
  )
}

interface Props {
  analysis: TickerAnalysis
  onClose: () => void
}

export function SetupCard({ analysis, onClose }: Props) {
  const { ticker, scorecard, technical, catalyst, risk, probabilities } = analysis

  if (!scorecard?.verdict) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70" onClick={onClose}>
        <div className="bg-bg-surface border border-accent-red/30 rounded-xl p-6 max-w-md" onClick={e => e.stopPropagation()}>
          <p className="text-accent-red text-sm">Analisi non disponibile per {ticker}.</p>
          <p className="text-slate-500 text-xs mt-2">Riavvia il container: ./deploy-local.sh --rebuild</p>
          <button onClick={onClose} className="mt-4 text-xs text-accent-cyan">Chiudi</button>
        </div>
      </div>
    )
  }

  const verdictColor = scorecard.verdict === 'PROCEED' ? 'text-accent-green'
    : scorecard.verdict === 'REVIEW' ? 'text-accent-yellow'
    : 'text-accent-red'

  const tierColor = catalyst.tier === 1 ? 'text-accent-green bg-accent-green/10 border-accent-green/20'
    : catalyst.tier === 2 ? 'text-accent-yellow bg-accent-yellow/10 border-accent-yellow/20'
    : 'text-accent-red bg-accent-red/10 border-accent-red/20'

  const evColor = (probabilities.expected_value ?? 0) >= 0 ? 'text-accent-green' : 'text-accent-red'

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-8 px-4 bg-black/70 backdrop-blur-sm" onClick={onClose}>
      <div
        className="bg-bg-surface border border-bg-border rounded-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto animate-fade-in"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-bg-border">
          <div className="flex items-center gap-3">
            <span className="text-2xl font-bold text-accent-cyan">{ticker}</span>
            <span className={`text-xs px-2 py-0.5 rounded border font-medium ${tierColor}`}>TIER {catalyst.tier}</span>
            <span className={`text-sm font-bold ${verdictColor}`}>{scorecard.verdict}</span>
          </div>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-200 text-xl transition-colors">✕</button>
        </div>

        <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Scoring */}
          <div className="bg-bg-panel rounded-lg p-4">
            <div className="text-xs text-slate-400 uppercase tracking-widest mb-3">Score  {scorecard.total}/100</div>
            <div className="space-y-2.5">
              <div>
                <div className="text-[11px] text-slate-500 mb-1">Catalyst</div>
                <ScoreBar value={scorecard.catalyst_score} max={25} color="bg-accent-cyan" />
              </div>
              <div>
                <div className="text-[11px] text-slate-500 mb-1">Volume</div>
                <ScoreBar value={scorecard.volume_score} max={25} color="bg-accent-green" />
              </div>
              <div>
                <div className="text-[11px] text-slate-500 mb-1">Sentiment</div>
                <ScoreBar value={scorecard.sentiment_score} max={20} color="bg-accent-yellow" />
              </div>
              <div>
                <div className="text-[11px] text-slate-500 mb-1">Technical</div>
                <ScoreBar value={scorecard.technical_score} max={20} color="bg-accent-orange" />
              </div>
              <div>
                <div className="text-[11px] text-slate-500 mb-1">Risk</div>
                <ScoreBar value={scorecard.risk_score} max={10} color="bg-accent-red" />
              </div>
            </div>
            {scorecard.flags.length > 0 && (
              <div className="mt-3 pt-3 border-t border-bg-border">
                <div className="text-[10px] text-slate-600 uppercase mb-1">Flags</div>
                <div className="flex flex-wrap gap-1">
                  {scorecard.flags.slice(0, 6).map(f => (
                    <span key={f} className="text-[9px] px-1.5 py-0.5 bg-bg-border text-slate-400 rounded">{f}</span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Catalyst */}
          <div className="bg-bg-panel rounded-lg p-4">
            <div className="text-xs text-slate-400 uppercase tracking-widest mb-3">Catalyst</div>
            <Row label="Event" value={catalyst.event_type.replace(/_/g, ' ')} />
            <Row label="Action" value={catalyst.action}
              valueClass={catalyst.action === 'TRADE' ? 'text-accent-green' : catalyst.action === 'SKIP' ? 'text-accent-red' : 'text-accent-yellow'} />
            <Row label="Confidence" value={catalyst.confidence}
              valueClass={catalyst.confidence === 'HIGH' ? 'text-accent-green' : catalyst.confidence === 'LOW' ? 'text-accent-red' : 'text-accent-yellow'} />
            <Row label="SEC Verified" value={catalyst.source_verified ? '✓ Yes' : '✗ No'}
              valueClass={catalyst.source_verified ? 'text-accent-green' : 'text-slate-500'} />
            {catalyst.sec_filing?.has_recent_8k && (
              <Row label="8-K Filed" value={catalyst.sec_filing.filing_date?.slice(0, 16) ?? 'Yes'} valueClass="text-accent-green" />
            )}
            {catalyst.days_to_event != null && (
              <Row label="Days to event" value={`${catalyst.days_to_event}d`} />
            )}
            {catalyst.trigger_keywords?.length > 0 && (
              <div className="mt-3 pt-3 border-t border-bg-border">
                <div className="text-[10px] text-slate-600 uppercase mb-1">Keywords</div>
                <div className="text-[11px] text-slate-400">{catalyst.trigger_keywords.slice(0, 3).join(', ')}</div>
              </div>
            )}
          </div>

          {/* Technical */}
          <div className="bg-bg-panel rounded-lg p-4">
            <div className="text-xs text-slate-400 uppercase tracking-widest mb-3">Technical (SMC)</div>
            <Row label="Pattern" value={technical.pattern.replace(/_/g, ' ')} valueClass="text-accent-cyan" />
            <Row label="BOS" value={technical.bos.confirmed ? `✓ ${technical.bos.bos_candle_date ?? ''}` : '✗ No'}
              valueClass={technical.bos.confirmed ? 'text-accent-green' : 'text-slate-500'} />
            <Row label="CHoCH" value={technical.choch.detected ? `✓ ${technical.choch.date ?? ''}` : '—'}
              valueClass={technical.choch.detected ? 'text-accent-green' : 'text-slate-500'} />
            <Row label="FVG zones" value={technical.fvg_zones.filter(f => !f.filled).length} />
            {technical.entry_zone.low && technical.entry_zone.high && (
              <Row label="Entry zone"
                value={`${fmt(technical.entry_zone.low)} – ${fmt(technical.entry_zone.high)}`}
                valueClass="text-accent-yellow" />
            )}
            {technical.invalidation && (
              <Row label="Invalidation" value={fmt(technical.invalidation)} valueClass="text-accent-red" />
            )}
            {technical.blow_off_top && (
              <div className="mt-2 text-[11px] text-accent-red bg-accent-red/10 rounded px-2 py-1 border border-accent-red/20">
                ⚠ BLOW-OFF TOP — DO NOT TRADE
              </div>
            )}
          </div>

          {/* Trade Plan */}
          <div className="bg-bg-panel rounded-lg p-4">
            <div className="text-xs text-slate-400 uppercase tracking-widest mb-3">Trade Plan</div>
            <Row label="Entry zone"
              value={`${fmt(risk.entry_low)} – ${fmt(risk.entry_high)}`}
              valueClass="text-accent-yellow" />
            <Row label="Stop loss" value={fmt(risk.stop_loss)} valueClass="text-accent-red" />
            <Row label="Target 1" value={`${fmt(risk.target1)}  ${risk.rr_t1}R`} valueClass="text-accent-green" />
            <Row label="Target 2" value={`${fmt(risk.target2)}  ${risk.rr_t2}R`} valueClass="text-accent-green" />
            <Row label="Target 3" value={`${fmt(risk.target3)}  ${risk.rr_t3}R`} valueClass="text-accent-green" />
            <div className="mt-3 pt-3 border-t border-bg-border grid grid-cols-2 gap-2">
              <div className="bg-bg-base rounded px-2 py-1.5 text-center">
                <div className="text-[10px] text-slate-500 mb-0.5">Shares</div>
                <div className="text-sm font-bold number">{risk.shares}</div>
              </div>
              <div className="bg-bg-base rounded px-2 py-1.5 text-center">
                <div className="text-[10px] text-slate-500 mb-0.5">$ Risk</div>
                <div className="text-sm font-bold text-accent-red number">${risk.dollar_risk?.toFixed(2)}</div>
              </div>
            </div>
          </div>

          {/* Probabilities */}
          <div className="bg-bg-panel rounded-lg p-4 md:col-span-2">
            <div className="text-xs text-slate-400 uppercase tracking-widest mb-3">
              Probability Estimates  <span className="text-[9px] text-slate-600 normal-case">heuristic GBM — not a guarantee</span>
            </div>
            <div className="grid grid-cols-4 gap-3">
              <div className="bg-bg-base rounded p-3 text-center">
                <div className="text-[10px] text-slate-500 mb-1">P(reach T1)</div>
                <div className="text-xl font-bold text-accent-green number">{pct(probabilities.p_target)}</div>
              </div>
              <div className="bg-bg-base rounded p-3 text-center">
                <div className="text-[10px] text-slate-500 mb-1">P(stop hit)</div>
                <div className="text-xl font-bold text-accent-red number">{pct(probabilities.p_stop)}</div>
              </div>
              <div className="bg-bg-base rounded p-3 text-center">
                <div className="text-[10px] text-slate-500 mb-1">P(neutral)</div>
                <div className="text-xl font-bold text-slate-400 number">{pct(probabilities.p_neutral)}</div>
              </div>
              <div className="bg-bg-base rounded p-3 text-center">
                <div className="text-[10px] text-slate-500 mb-1">EV / share</div>
                <div className={`text-xl font-bold number ${evColor}`}>
                  {(probabilities.expected_value ?? 0) >= 0 ? '+' : ''}${(probabilities.expected_value ?? 0).toFixed(4)}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
