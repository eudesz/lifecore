import React, { useEffect, useMemo, useState } from 'react'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import RequireApiKey from '@/components/RequireApiKey'
import { useAuth } from '@/context/AuthContext'
import TimelineChart, { type TimelineEvent } from '@/components/timeline/TimelineChart'
import { fetchTimelineAdvanced } from '@/lib/api'

export default function TimelinePage() {
  const { user } = useAuth()
  const userId = user?.id?.toString() || ''
  const [events, setEvents] = useState<TimelineEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [range, setRange] = useState<{ from?: string; to?: string }>({})
  const [categories, setCategories] = useState<string[]>([])
  const [selected, setSelected] = useState<TimelineEvent | null>(null)
  const [showFullDoc, setShowFullDoc] = useState(false)
  const [showDocModal, setShowDocModal] = useState(false)
  const [preset, setPreset] = useState<'90d' | '6m' | '1y' | 'all' | null>('90d')

  const handleCopy = (text: string) => {
    try {
      if (navigator?.clipboard?.writeText) {
        navigator.clipboard.writeText(text || '')
      } else {
        const el = document.createElement('textarea')
        el.value = text || ''
        document.body.appendChild(el)
        el.select()
        document.execCommand('copy')
        document.body.removeChild(el)
      }
    } catch {
      // ignore
    }
  }

  const handleDownloadTxt = (filenameBase: string, text: string) => {
    try {
      const blob = new Blob([text || ''], { type: 'text/plain;charset=utf-8' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const safeName = (filenameBase || 'documento').replace(/[^a-z0-9-_]+/gi, '_').slice(0, 64)
      a.download = `${safeName}.txt`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch {
      // ignore
    }
  }

  useEffect(() => {
    if (!userId) return
    const load = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await fetchTimelineAdvanced({
          user_id: userId,
          date_from: range.from,
          date_to: range.to,
          categories,
        })
        setEvents((data.events || []) as TimelineEvent[])
      } catch (e: any) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [userId, range.from, range.to, categories])

  const availableCategories = useMemo(() => ([
    { key: 'diagnosis', label: 'Diagnosis' },
    { key: 'treatment', label: 'Treatment' },
    { key: 'lab', label: 'Lab' },
    { key: 'consultation', label: 'Consultation' },
    { key: 'event', label: 'Event' },
  ]), [])

  const categoryCounts = useMemo(() => {
    const m = new Map<string, number>()
    for (const e of events) {
      m.set(e.category, (m.get(e.category) || 0) + 1)
    }
    return m
  }, [events])

  const setPresetRange = (p: '90d' | '6m' | '1y' | 'all') => {
    const today = new Date()
    const to = today.toISOString().slice(0, 10)
    if (p === 'all') {
      setRange({ from: undefined, to: undefined })
    } else {
      const d = new Date(today)
      if (p === '90d') d.setDate(d.getDate() - 90)
      if (p === '6m') d.setMonth(d.getMonth() - 6)
      if (p === '1y') d.setFullYear(d.getFullYear() - 1)
      const from = d.toISOString().slice(0, 10)
      setRange({ from, to })
    }
    setPreset(p)
  }

  const colorForCategory = (key: string) => {
    switch (key) {
      case 'diagnosis': return '#ef4444'
      case 'treatment': return '#3b82f6'
      case 'lab': return '#10b981'
      case 'consultation': return '#8b5cf6'
      case 'event': return '#f59e0b'
      default: return '#64748b'
    }
  }

  return (
    <ProtectedRoute>
      <RequireApiKey>
      <main id="content" className="container" style={{ paddingTop: 'var(--space-lg)' }}>
        <h1 style={{ marginBottom: 8 }}>Timeline</h1>
        <p style={{ color: 'var(--text-muted)', marginTop: 0 }}>Explore 20 years of health history with time and category filters.</p>

        <section className="card" style={{ marginTop: 16, padding: 16 }}>
          {/* Quick presets */}
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center', marginBottom: 8 }}>
            <span className="muted" style={{ fontWeight: 600 }}>Quick range</span>
            {[
              { id: '90d', label: 'Last 90 days' },
              { id: '6m', label: 'Last 6 months' },
              { id: '1y', label: 'Last year' },
              { id: 'all', label: 'All' },
            ].map(b => (
              <button
                key={b.id}
                className={`btn ${preset === (b.id as any) ? '' : 'secondary'}`}
                onClick={() => setPresetRange(b.id as any)}
                style={{ padding: '6px 10px' }}
              >
                {b.label}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center', marginTop: 8 }}>
            <div>
              <label style={{ display: 'block', fontWeight: 600 }}>From</label>
              <input type="date" onChange={e => setRange(r => ({ ...r, from: e.target.value || undefined }))} />
            </div>
            <div>
              <label style={{ display: 'block', fontWeight: 600 }}>To</label>
              <input type="date" onChange={e => setRange(r => ({ ...r, to: e.target.value || undefined }))} />
            </div>
            <div>
              <label style={{ display: 'block', fontWeight: 600 }}>Categories</label>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {availableCategories.map(c => {
                  const active = categories.includes(c.key)
                  return (
                    <button
                      key={c.key}
                      onClick={() => setCategories(prev => active ? prev.filter(x => x !== c.key) : [...prev, c.key])}
                      style={{
                        padding: '6px 10px',
                        borderRadius: 8,
                        border: '1px solid var(--glass-border)',
                        background: active ? 'var(--bg-muted)' : 'transparent',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 6
                      }}
                    >
                      <span style={{ width: 8, height: 8, borderRadius: '50%', background: colorForCategory(c.key) }} />
                      {c.label}
                      <span className="muted" style={{ fontSize: 12 }}>({categoryCounts.get(c.key) || 0})</span>
                    </button>
                  )
                })}
                <button
                  className="btn secondary"
                  onClick={() => setCategories([])}
                  style={{ padding: '6px 10px' }}
                >
                  Clear
                </button>
                <button
                  className="btn secondary"
                  onClick={() => setCategories(availableCategories.map(c => c.key))}
                  style={{ padding: '6px 10px' }}
                >
                  Select all
                </button>
              </div>
            </div>
          </div>
          <div className="muted" style={{ marginTop: 8 }}>
            Showing <strong>{events.length}</strong> events {categories.length ? <>· filtered by {categories.join(', ')}</> : null}
          </div>
        </section>

          <section className="card" style={{ marginTop: 16 }}>
          {loading && <div style={{ padding: 16, color: '#6b7280' }}>Loading timeline…</div>}
          {error && <div style={{ padding: 16, color: '#b91c1c' }}>Error: {error}</div>}
          {!loading && !error && (
            <div style={{ width: '100%', height: 'min(65vh, 420px)' }}>
              <TimelineChart events={events} onSelect={(e) => setSelected(e)} />
            </div>
          )}
        </section>

        {/* Visor de documento / Detalle del evento */}
        {selected && (
          <section className="card" style={{ marginTop: 16, padding: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 12 }}>
              <h3 style={{ margin: 0 }}>{selected.title}</h3>
              <button
                onClick={() => setSelected(null)}
                className="btn secondary"
                style={{ padding: '6px 10px' }}
              >
                Close
              </button>
            </div>
            <div style={{ color: '#6b7280', marginTop: 4 }}>
              {new Date(selected.date).toLocaleString()} · {selected.category}
            </div>
            {/* Resumen compacto */}
            <div style={{ display: 'flex', gap: 16, marginTop: 12, flexWrap: 'wrap' }}>
              {typeof selected.metrics?.glucose !== 'undefined' && (
                <div className="badge">Glucose: <strong>{selected.metrics.glucose}</strong></div>
              )}
              {typeof selected.metrics?.bp_sys !== 'undefined' && (
                <div className="badge">Systolic BP: <strong>{selected.metrics.bp_sys}</strong></div>
              )}
              {typeof selected.metrics?.weight !== 'undefined' && (
                <div className="badge">Weight: <strong>{selected.metrics.weight}</strong></div>
              )}
            </div>
            {/* Visor de documento / descripción */}
            {selected.description && (
              <>
                <div style={{
                  marginTop: 12,
                  background: 'var(--bg-muted)',
                  border: '1px solid var(--glass-border)',
                  borderRadius: 8,
                  padding: 12,
                  whiteSpace: 'pre-wrap',
                  lineHeight: 1.5
                }}>
                  {showFullDoc ? selected.description : (selected.description.length > 600 ? (selected.description.slice(0, 600) + '…') : selected.description)}
                </div>
                <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap' }}>
                  {selected.description.length > 600 && (
                    <button className="btn secondary" onClick={() => setShowFullDoc(v => !v)} style={{ padding: '6px 10px' }}>
                      {showFullDoc ? 'Show less' : 'Show more'}
                    </button>
                  )}
                  <button className="btn" onClick={() => setShowDocModal(true)} style={{ padding: '6px 10px' }}>
                    Open as document
                  </button>
                  <button className="btn secondary" onClick={() => handleCopy(selected.description!)} style={{ padding: '6px 10px' }}>
                    Copy
                  </button>
                  <button className="btn secondary" onClick={() => handleDownloadTxt(selected.title || 'documento', selected.description!)} style={{ padding: '6px 10px' }}>
                    Download .txt
                  </button>
                </div>
              </>
            )}
            {!selected.description && (
              <div className="muted" style={{ marginTop: 12 }}>
                No document content for this event.
              </div>
            )}
          </section>
        )}

        {/* Modal visor de documento */}
        {selected && showDocModal && (
          <div
            role="dialog"
            aria-modal="true"
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0,0,0,0.6)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 16,
              zIndex: 1000
            }}
            onClick={() => setShowDocModal(false)}
          >
            <div
              className="card"
              style={{ maxWidth: 900, width: '100%', maxHeight: '85vh', overflow: 'auto', padding: 16 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 12 }}>
                <h3 style={{ margin: 0 }}>{selected.title}</h3>
                <button className="btn secondary" onClick={() => setShowDocModal(false)} style={{ padding: '6px 10px' }}>
                  Close
                </button>
              </div>
              <div style={{ color: '#6b7280', marginTop: 4 }}>
                {new Date(selected.date).toLocaleString()} · {selected.category}
              </div>
              <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap' }}>
                <button className="btn secondary" onClick={() => handleCopy(selected.description || '')} style={{ padding: '6px 10px' }}>
                  Copy
                </button>
                <button className="btn secondary" onClick={() => handleDownloadTxt(selected.title || 'documento', selected.description || '')} style={{ padding: '6px 10px' }}>
                  Download .txt
                </button>
              </div>
              <div style={{
                marginTop: 12,
                background: 'var(--bg-muted)',
                border: '1px solid var(--glass-border)',
                borderRadius: 8,
                padding: 12,
                whiteSpace: 'pre-wrap',
                lineHeight: 1.6
              }}>
                {selected.description || 'No content.'}
              </div>
            </div>
          </div>
        )}
      </main>
      </RequireApiKey>
    </ProtectedRoute>
  )
}


