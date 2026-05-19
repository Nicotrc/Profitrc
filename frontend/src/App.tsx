import { useState } from 'react'
import { useApi } from './hooks/useApi'
import { RegimePanel } from './components/RegimePanel'
import { ScanPanel } from './components/ScanPanel'
import { WatchlistTable } from './components/WatchlistTable'
import { SetupCard } from './components/SetupCard'
import { PostMortemTable } from './components/PostMortemTable'
import { PdufaPanel } from './components/PdufaPanel'
import type { Regime, WatchlistItem, PostMortemEntry, TickerAnalysis, PdufaEntry } from './types'

type Tab = 'scan' | 'watchlist' | 'postmortem' | 'pdufa'

const TABS: { id: Tab; label: string }[] = [
  { id: 'scan',      label: 'Scan' },
  { id: 'watchlist', label: 'Watchlist' },
  { id: 'postmortem',label: 'Post-Mortem' },
  { id: 'pdufa',     label: 'PDUFA' },
]

export default function App() {
  const [tab, setTab] = useState<Tab>('scan')
  const [selectedAnalysis, setSelectedAnalysis] = useState<TickerAnalysis | null>(null)
  const [tickerInput, setTickerInput] = useState('')
  const [capital] = useState(10_000)
  const [analyzing, setAnalyzing] = useState(false)
  const [analyzeError, setAnalyzeError] = useState<string | null>(null)

  const regime = useApi<Regime>('/api/regime', true, 5 * 60 * 1000)  // refresh every 5 min
  const watchlist = useApi<WatchlistItem[]>('/api/watchlist', true, 30_000)
  const postmortem = useApi<PostMortemEntry[]>('/api/postmortem', true)
  const pdufa = useApi<PdufaEntry[]>('/api/pdufa', tab === 'pdufa', 60 * 60 * 1000) // refresh each hour

  async function handleTickerSearch(e: React.FormEvent) {
    e.preventDefault()
    const t = tickerInput.trim().toUpperCase()
    if (!t) return
    setAnalyzing(true)
    setAnalyzeError(null)
    try {
      const res = await fetch(`/api/analyze/${t}`)
      const data = await res.json()
      if (!res.ok) {
        const msg = typeof data?.detail === 'string' ? data.detail : `HTTP ${res.status}`
        throw new Error(msg)
      }
      if (!data?.scorecard?.verdict) {
        throw new Error('Risposta analisi non valida — riavvia Docker con --rebuild')
      }
      setSelectedAnalysis(data as TickerAnalysis)
      setTickerInput('')
    } catch (err) {
      setAnalyzeError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg-base text-slate-200">
      {/* Top bar */}
      <header className="border-b border-bg-border bg-bg-surface sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 h-12 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-bold text-accent-cyan tracking-wider text-sm">PROFITRC</span>
            <span className="text-[10px] text-slate-600 border border-bg-border rounded px-1.5 py-0.5">v2.0</span>
            {regime.data && (
              <span className={`text-[11px] font-semibold ml-2 ${
                regime.data.regime === 'TRADE' ? 'text-accent-green' :
                regime.data.regime === 'SELECTIVE' ? 'text-accent-yellow' :
                regime.data.regime === 'CAUTION' ? 'text-accent-orange' : 'text-accent-red'
              }`}>
                {regime.data.regime}
              </span>
            )}
          </div>

          {/* Quick ticker search */}
          <form onSubmit={handleTickerSearch} className="flex items-center gap-2">
            <input
              value={tickerInput}
              onChange={e => setTickerInput(e.target.value.toUpperCase())}
              placeholder="TICKER →"
              disabled={analyzing}
              className="w-28 bg-bg-panel border border-bg-border rounded px-2 py-1 text-xs text-slate-200 focus:outline-none focus:border-accent-cyan placeholder-slate-600 uppercase disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={analyzing}
              className="relative text-xs px-2 py-1 bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20 rounded hover:bg-accent-cyan/20 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {analyzing ? (
                <span className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-accent-cyan rounded-full animate-pulse inline-block" />
                  Loading…
                </span>
              ) : 'Analyze'}
            </button>
            {analyzeError && (
              <span className="text-[10px] text-accent-red max-w-[120px] truncate" title={analyzeError}>
                {analyzeError}
              </span>
            )}
          </form>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-5">
        {/* Regime panel — always visible */}
        <RegimePanel
          regime={regime.data}
          loading={regime.loading}
          onRefresh={regime.refetch}
        />

        {/* Tab nav */}
        <div className="flex items-center gap-1 border-b border-bg-border">
          {TABS.map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`px-4 py-2 text-xs font-medium transition-colors border-b-2 -mb-px ${
                tab === t.id
                  ? 'text-accent-cyan border-accent-cyan'
                  : 'text-slate-500 border-transparent hover:text-slate-300'
              }`}
            >
              {t.label}
              {t.id === 'watchlist' && watchlist.data && watchlist.data.length > 0 && (
                <span className="ml-1.5 text-[9px] bg-accent-cyan/20 text-accent-cyan px-1 rounded-full">
                  {watchlist.data.length}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="animate-fade-in">
          {tab === 'scan' && (
            <ScanPanel
              capital={capital}
              regime={regime.data?.regime}
              onSelectTicker={setSelectedAnalysis}
            />
          )}
          {tab === 'watchlist' && (
            <WatchlistTable
              items={watchlist.data ?? []}
              loading={watchlist.loading}
              onRefresh={watchlist.refetch}
              onAnalyze={setSelectedAnalysis}
            />
          )}
          {tab === 'postmortem' && (
            <PostMortemTable
              entries={postmortem.data ?? []}
              loading={postmortem.loading}
              onRefresh={postmortem.refetch}
            />
          )}
          {tab === 'pdufa' && (
            <PdufaPanel
              entries={pdufa.data ?? []}
              loading={pdufa.loading}
              onRefresh={pdufa.refetch}
            />
          )}
        </div>
      </main>

      {/* Setup Card modal */}
      {selectedAnalysis && (
        <SetupCard
          analysis={selectedAnalysis}
          onClose={() => setSelectedAnalysis(null)}
        />
      )}

      {/* Footer */}
      <footer className="border-t border-bg-border mt-12 py-4 text-center text-[10px] text-slate-700">
        PROFITRC v2.0 · Speculative Trading Intelligence · Not financial advice
      </footer>
    </div>
  )
}
