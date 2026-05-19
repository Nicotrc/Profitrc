import { PdufaEntry } from '../types'

interface Props {
  entries: PdufaEntry[]
  loading: boolean
  onRefresh: () => void
}

export function PdufaPanel({ entries, loading, onRefresh }: Props) {
  if (loading && entries.length === 0) {
    return (
      <div className="space-y-2">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-14 bg-bg-panel rounded-lg border border-bg-border animate-pulse" />
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <span className="text-[11px] text-slate-600">{entries.length} upcoming PDUFA dates</span>
        <button onClick={onRefresh} className="text-[10px] text-slate-600 hover:text-slate-400 transition-colors">
          ↻ refresh
        </button>
      </div>

      {entries.length === 0 ? (
        <div className="text-center py-12 text-slate-600 border border-bg-border rounded-lg bg-bg-panel">
          <div className="text-2xl mb-2">💊</div>
          <div className="text-sm">No PDUFA dates in the next 30 days.</div>
        </div>
      ) : (
        <div className="space-y-2">
          {entries.map(e => (
            <div
              key={`${e.ticker}-${e.pdufa_date}`}
              className="bg-bg-panel border border-bg-border rounded-lg px-4 py-3 hover:border-slate-500 transition-colors"
            >
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-3">
                  <span className="text-base font-bold text-accent-cyan w-16 shrink-0">{e.ticker}</span>
                  <span className="text-[11px] text-slate-400 truncate max-w-[200px]">{e.drug}</span>
                </div>
                <div className="flex items-center gap-4 text-[11px]">
                  <span className="text-slate-500">
                    PDUFA <span className="text-slate-300">{e.pdufa_date}</span>
                  </span>
                  <span className={`font-semibold ${e.days_to_pdufa <= 7 ? 'text-accent-red' : e.days_to_pdufa <= 14 ? 'text-accent-orange' : 'text-accent-yellow'}`}>
                    {e.days_to_pdufa}d
                  </span>
                </div>
              </div>
              {e.indication && (
                <div className="mt-1 text-[10px] text-slate-600 truncate">{e.indication}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
