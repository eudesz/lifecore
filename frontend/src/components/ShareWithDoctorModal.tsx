import React, { useEffect, useState } from 'react'

export default function ShareWithDoctorModal({
  isOpen,
  onClose,
  userId,
}: {
  isOpen: boolean
  onClose: () => void
  userId: string
}) {
  const [expires, setExpires] = useState<number>(7)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [links, setLinks] = useState<Array<{ id: number; token: string; revoked: boolean; created_at: string; expires_at?: string; url: string }>>([])
  const [conditions, setConditions] = useState<Array<{ slug: string; name: string; color: string; count: number }>>([])
  const [selectedConds, setSelectedConds] = useState<string[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [range, setRange] = useState<{ from?: string; to?: string }>({})

  const loadLinks = async () => {
    try {
      setError(null)
      const key = (typeof window !== 'undefined') ? (localStorage.getItem('PLATFORM_API_KEY') || process.env.NEXT_PUBLIC_PLATFORM_API_KEY || '') : ''
      const res = await fetch(`/api/lifecore/doctor-links?user_id=${userId}`, {
        headers: key ? { Authorization: `Bearer ${key}` } : undefined
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setLinks(data.links || [])
    } catch (e: any) {
      setError(e.message)
    }
  }

  useEffect(() => {
    if (isOpen) loadLinks()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen])
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`/api/lifecore/conditions/list?user_id=${userId}`)
        if (res.ok) {
          const data = await res.json()
          setConditions(data.conditions || [])
        }
      } catch {
        // ignore
      }
    })()
  }, [userId, isOpen])

  const createLink = async () => {
    try {
      setLoading(true)
      setError(null)
      const key = (typeof window !== 'undefined') ? (localStorage.getItem('PLATFORM_API_KEY') || process.env.NEXT_PUBLIC_PLATFORM_API_KEY || '') : ''
      const res = await fetch('/api/doctor-link', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(key ? { Authorization: `Bearer ${key}` } : {}) },
        body: JSON.stringify({
          user: userId,
          expires_in_days: expires,
          scope: 'chat',
          conditions: selectedConds,
          categories,
          date_from: range.from,
          date_to: range.to,
        })
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json = await res.json()
      const url = `${window.location.origin}/doctor/${json.token}`
      await navigator.clipboard.writeText(url)
      await loadLinks()
      alert(`Link created and copied:\n${url}`)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const revoke = async (token: string) => {
    try {
      const key = (typeof window !== 'undefined') ? (localStorage.getItem('PLATFORM_API_KEY') || process.env.NEXT_PUBLIC_PLATFORM_API_KEY || '') : ''
      const res = await fetch('/api/lifecore/doctor-links/revoke', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(key ? { Authorization: `Bearer ${key}` } : {}) },
        body: JSON.stringify({ token })
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      await loadLinks()
    } catch (e: any) {
      alert(`Could not revoke: ${e.message}`)
    }
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="card modal-card" style={{ padding: 16 }} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 12 }}>
          <h3 style={{ margin: 0 }}>Share with doctor</h3>
          <button className="btn secondary" onClick={onClose} style={{ padding: '6px 10px' }}>Close</button>
        </div>
        <p className="muted" style={{ marginTop: 6 }}>Generate a read-only link with an expiration time.</p>

        <div className="card" style={{ padding: 12, marginTop: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <label style={{ fontWeight: 600 }}>Expiration</label>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {[1, 7, 30].map(d => (
                <label key={d} style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                  <input type="radio" name="exp" checked={expires === d} onChange={() => setExpires(d)} />
                  {d === 1 ? '24 hours' : `${d} days`}
                </label>
              ))}
            </div>
            <button className="btn" onClick={createLink} disabled={loading} style={{ padding: '6px 12px' }}>
              {loading ? 'Creating…' : 'Create & copy link'}
            </button>
            {error && <span style={{ color: '#b91c1c' }}>Error: {error}</span>}
          </div>
        </div>

        <div className="card" style={{ padding: 12, marginTop: 8 }}>
          <h4 style={{ marginTop: 0 }}>Scope (optional)</h4>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
            <div>
              <label style={{ display: 'block', fontWeight: 600 }}>From</label>
              <input type="date" onChange={e => setRange(r => ({ ...r, from: e.target.value || undefined }))} />
            </div>
            <div>
              <label style={{ display: 'block', fontWeight: 600 }}>To</label>
              <input type="date" onChange={e => setRange(r => ({ ...r, to: e.target.value || undefined }))} />
            </div>
          </div>
          <div style={{ marginTop: 8 }}>
            <label style={{ display: 'block', fontWeight: 600 }}>Conditions</label>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {conditions.map(c => {
                const active = selectedConds.includes(c.slug)
                return (
                  <button
                    key={c.slug}
                    className={`btn ${active ? '' : 'secondary'}`}
                    onClick={() => setSelectedConds(prev => active ? prev.filter(x => x !== c.slug) : [...prev, c.slug])}
                    style={{ padding: '6px 10px', borderColor: c.color }}
                  >
                    {c.name} ({c.count})
                  </button>
                )
              })}
              <button className="btn secondary" onClick={() => setSelectedConds([])} style={{ padding: '6px 10px' }}>
                Clear
              </button>
            </div>
          </div>
          <div style={{ marginTop: 8 }}>
            <label style={{ display: 'block', fontWeight: 600 }}>Categories</label>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {['diagnosis','treatment','lab','consultation','event'].map(k => {
                const active = categories.includes(k)
                return (
                  <button
                    key={k}
                    className={`btn ${active ? '' : 'secondary'}`}
                    onClick={() => setCategories(prev => active ? prev.filter(x => x !== k) : [...prev, k])}
                    style={{ padding: '6px 10px' }}
                  >
                    {k}
                  </button>
                )
              })}
              <button className="btn secondary" onClick={() => setCategories([])} style={{ padding: '6px 10px' }}>
                Clear
              </button>
            </div>
          </div>
        </div>

        <section className="card" style={{ padding: 12, marginTop: 12 }}>
          <h4 style={{ marginTop: 0 }}>Active links</h4>
          <table className="table">
            <thead>
              <tr>
                <th>Created</th>
                <th>Expires</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {links.map(l => (
                <tr key={l.token}>
                  <td>{new Date(l.created_at).toLocaleString()}</td>
                  <td>{l.expires_at ? new Date(l.expires_at).toLocaleString() : '—'}</td>
                  <td>{l.revoked ? 'Revoked' : 'Active'}</td>
                  <td style={{ display: 'flex', gap: 8 }}>
                    <button className="btn secondary" onClick={() => navigator.clipboard.writeText(`${window.location.origin}${l.url}`)} style={{ padding: '4px 8px' }}>
                      Copy
                    </button>
                    {!l.revoked && (
                      <button className="btn secondary" onClick={() => revoke(l.token)} style={{ padding: '4px 8px' }}>
                        Revoke
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {!links.length && (
                <tr><td colSpan={4} className="muted">No links yet.</td></tr>
              )}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  )
}


