import { useState } from 'react'
import { PostMortemEntry } from '../types'
import { post } from '../hooks/useApi'

interface Props {
  entries: PostMortemEntry[]
  loading: boolean
  onRefresh: () => void
}

export function PostMortemTable({ entries, loading, onRefresh }: Props) {
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    ticker: '', entry_price: '', exit_price: '',
    entry_date: '', exit_date: '',
    catalyst_outcome: '', lesson: '',
    score_at_entry: '', tier: '2',
  })
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    try {
      await post('/api/postmortem', {
        ticker: form.ticker.toUpperCase(),
        entry_price: parseFloat(form.entry_price),
        exit_price: parseFloat(form.exit_price),
        entry_date: form.entry_date,
        exit_date: form.exit_date,
        catalyst_outcome: form.catalyst_outcome,
        lesson: form.lesson,
        score_at_entry: parseInt(form.score_at_entry) || 0,
        tier: parseInt(form.tier),
      })
      setShowForm(false)
      setForm({ ticker: '', entry_price: '', exit_price: '', entry_date: '', exit_date: '', catalyst_outcome: '', lesson: '', score_at_entry: '', tier: '2' })
      onRefresh()
    } catch (e) {
      console.error(e)
    } finally {
      setSubmitting(false)
    }
  }

  // Stats
  const wins = entries.filter(e => e.outcome === 'win').length
  const losses = entries.filter(e => e.outcome === 'loss').length
  const total = wins + losses
  const avgPnl = entries.length ? (entries.reduce((s, e) => s + (e.pnl_pct ?? 0), 0) / entries.length) : 0
  const winRate = total ? wins / total : 0

  return (
    <div className="space-y-4">
      {/* Stats bar */}
      {entries.length > 0 && (
        <div className="grid grid-cols-4 gap-3">
          {[
            { label: 'Trades', value: entries.length },
            { label: 'Win rate', value: `${(winRate * 100).toFixed(0)}%`, color: winRate >= 0.5 ? 'text-accent-green' : 'text-accent-red' },
            { label: 'Avg PnL', value: `${avgPnl >= 0 ? '+' : ''}${avgPnl.toFixed(1)}%`, color: avgPnl >= 0 ? 'text-accent-green' : 'text-accent-red' },
            { label: 'W/L', value: `${wins}/${losses}`, color: wins > losses ? 'text-accent-green' : wins < losses ? 'text-accent-red' : 'text-accent-yellow' },
          ].map(stat => (
            <div key={stat.label} className="bg-bg-panel border border-bg-border rounded-lg p-3 text-center">
              <div className="text-[10px] text-slate-600 uppercase mb-1">{stat.label}</div>
              <div className={`text-lg font-bold number ${stat.color ?? 'text-slate-200'}`}>{stat.value}</div>
            </div>
          ))}
        </div>
      )}

      {/* Log button */}
      <div className="flex justify-between items-center">
        <span className="text-[11px] text-slate-600">{entries.length} trade(s) logged</span>
        <button
          onClick={() => setShowForm(!showForm)}
          className="text-[11px] px-3 py-1.5 bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20 rounded hover:bg-accent-cyan/20 transition-colors"
        >
          {showForm ? '✕ Cancel' : '+ Log Trade'}
        </button>
      </div>

      {/* Form */}
      {showForm && (
        <form onSubmit={handleSubmit} className="bg-bg-panel border border-bg-border rounded-lg p-4 space-y-3 animate-fade-in">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {[
              { key: 'ticker', label: 'Ticker', type: 'text', placeholder: 'ACHV' },
              { key: 'entry_price', label: 'Entry $', type: 'number', placeholder: '5.50' },
              { key: 'exit_price', label: 'Exit $', type: 'number', placeholder: '7.80' },
              { key: 'entry_date', label: 'Entry Date', type: 'date', placeholder: '' },
              { key: 'exit_date', label: 'Exit Date', type: 'date', placeholder: '' },
              { key: 'score_at_entry', label: 'Score', type: 'number', placeholder: '72' },
            ].map(f => (
              <div key={f.key}>
                <label className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">{f.label}</label>
                <input
                  type={f.type}
                  placeholder={f.placeholder}
                  value={(form as Record<string, string>)[f.key]}
                  onChange={e => setForm(prev => ({ ...prev, [f.key]: e.target.value }))}
                  className="w-full bg-bg-base border border-bg-border rounded px-2 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-accent-cyan number"
                  required={['ticker', 'entry_price', 'exit_price'].includes(f.key)}
                />
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">Catalyst outcome</label>
              <input
                placeholder="FDA approved / contract signed / …"
                value={form.catalyst_outcome}
                onChange={e => setForm(prev => ({ ...prev, catalyst_outcome: e.target.value }))}
                className="w-full bg-bg-base border border-bg-border rounded px-2 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-accent-cyan"
              />
            </div>
            <div>
              <label className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">Lesson (post-mortem)</label>
              <input
                placeholder="What would you do differently?"
                value={form.lesson}
                onChange={e => setForm(prev => ({ ...prev, lesson: e.target.value }))}
                className="w-full bg-bg-base border border-bg-border rounded px-2 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-accent-cyan"
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2 bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/30 rounded hover:bg-accent-cyan/30 transition-colors disabled:opacity-50 text-sm font-medium"
          >
            {submitting ? 'Saving…' : 'Save Trade'}
          </button>
        </form>
      )}

      {/* Entries */}
      {loading && entries.length === 0 ? (
        <div className="space-y-2">
          {[...Array(3)].map((_, i) => <div key={i} className="h-12 bg-bg-panel rounded-lg animate-pulse" />)}
        </div>
      ) : entries.length === 0 ? (
        <div className="text-center py-10 text-slate-600 bg-bg-panel rounded-lg border border-bg-border text-sm">
          No trades logged yet. Log your first trade above.
        </div>
      ) : (
        <div className="space-y-1.5">
          {/* Header */}
          <div className="grid grid-cols-[80px_80px_80px_80px_80px_60px_1fr] gap-2 px-3 py-1 text-[10px] text-slate-600 uppercase tracking-wider">
            <span>Ticker</span><span>Entry</span><span>Exit</span><span>PnL</span><span>Date</span><span>Score</span><span>Lesson</span>
          </div>
          {entries.map(e => {
            const pnlColor = e.pnl_pct > 0 ? 'text-accent-green' : e.pnl_pct < 0 ? 'text-accent-red' : 'text-accent-yellow'
            const outcomeColor = e.outcome === 'win' ? 'bg-accent-green/10 border-accent-green/20 text-accent-green'
              : e.outcome === 'loss' ? 'bg-accent-red/10 border-accent-red/20 text-accent-red'
              : 'bg-accent-yellow/10 border-accent-yellow/20 text-accent-yellow'
            return (
              <div key={e.id} className="grid grid-cols-[80px_80px_80px_80px_80px_60px_1fr] gap-2 items-center bg-bg-panel border border-bg-border rounded px-3 py-2 text-[11px]">
                <span className="font-bold text-accent-cyan">{e.ticker}</span>
                <span className="number text-slate-400">${e.entry_price?.toFixed(3)}</span>
                <span className="number text-slate-400">${e.exit_price?.toFixed(3)}</span>
                <span className={`number font-semibold ${pnlColor}`}>{e.pnl_pct >= 0 ? '+' : ''}{e.pnl_pct?.toFixed(1)}%</span>
                <span className="text-slate-600">{(e.exit_date ?? '').slice(0, 10)}</span>
                <span className="text-slate-500">{e.score_at_entry}</span>
                <span className="text-slate-500 truncate">{e.lesson}</span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
