import React, { useEffect, useState } from 'react'
import RequireApiKey from '../../components/RequireApiKey'

function getApiKey(): string | undefined {
  if (process.env.NEXT_PUBLIC_PLATFORM_API_KEY) return process.env.NEXT_PUBLIC_PLATFORM_API_KEY
  if (typeof window !== 'undefined') return localStorage.getItem('PLATFORM_API_KEY') || undefined
  return undefined
}

export default function ConsentDashboard() {
  const [userId, setUserId] = useState<string>('1')
  const [items, setItems] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [form, setForm] = useState<{ resource: string; purpose: string; allowed: boolean; scope: string; expires_at: string }>({ resource: '', purpose: '', allowed: true, scope: 'read', expires_at: '' })

  const key = getApiKey()

  async function load() {
    if (!userId) return
    try {
      setLoading(true)
      setError(null)
      const res = await fetch(`/api/lifecore/consent/list?user_id=${encodeURIComponent(userId)}`, { headers: key ? { Authorization: `Bearer ${key}` } : undefined })
      const data = await res.json()
      if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`)
      setItems(data.consents || [])
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  async function upsert() {
    try {
      setLoading(true)
      setError(null)
      const body: any = { user: Number(userId), resource: form.resource, purpose: form.purpose, allowed: form.allowed, scope: form.scope }
      if (form.expires_at) body.expires_at = new Date(form.expires_at).toISOString()
      const res = await fetch('/api/lifecore/consent/upsert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(key ? { Authorization: `Bearer ${key}` } : {}) },
        body: JSON.stringify(body)
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`)
      await load()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function remove(item: any) {
    try {
      setLoading(true)
      setError(null)
      const res = await fetch('/api/lifecore/consent/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(key ? { Authorization: `Bearer ${key}` } : {}) },
        body: JSON.stringify({ id: item.id })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`)
      await load()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <RequireApiKey>
      <div style={{ maxWidth: 1000, margin: '0 auto', padding: 24 }}>
        <h1>Gestión de Consentimientos</h1>
        <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end', marginBottom: 12 }}>
          <div>
            <label>Usuario (ID)</label>
            <input type="text" value={userId} onChange={(e) => setUserId(e.target.value)} style={{ display: 'block', padding: 6 }} />
          </div>
          <button onClick={load} disabled={loading} style={{ padding: '8px 12px', height: 38 }}>{loading ? 'Cargando…' : 'Cargar'}</button>
        </div>

        <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 16, marginTop: 8 }}>
          <h3 style={{ marginTop: 0 }}>Nuevo / Actualizar</h3>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <div>
              <label>Recurso</label>
              <input value={form.resource} onChange={(e) => setForm({ ...form, resource: e.target.value })} style={{ display: 'block', padding: 6 }} />
            </div>
            <div>
              <label>Propósito</label>
              <input value={form.purpose} onChange={(e) => setForm({ ...form, purpose: e.target.value })} style={{ display: 'block', padding: 6 }} />
            </div>
            <div>
              <label>Scope</label>
              <input value={form.scope} onChange={(e) => setForm({ ...form, scope: e.target.value })} style={{ display: 'block', padding: 6 }} />
            </div>
            <div>
              <label>Vence</label>
              <input type="datetime-local" value={form.expires_at} onChange={(e) => setForm({ ...form, expires_at: e.target.value })} style={{ display: 'block', padding: 6 }} />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <input id="allowed" type="checkbox" checked={form.allowed} onChange={(e) => setForm({ ...form, allowed: e.target.checked })} />
              <label htmlFor="allowed">Permitido</label>
            </div>
            <button onClick={upsert} disabled={loading} style={{ padding: '8px 12px' }}>{loading ? 'Guardando…' : 'Guardar'}</button>
          </div>
        </div>

        {error && <div style={{ marginTop: 12, color: '#b91c1c' }}>Error: {error}</div>}
        <div style={{ marginTop: 16, overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: 8 }}>ID</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: 8 }}>Recurso</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: 8 }}>Propósito</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: 8 }}>Scope</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: 8 }}>Permitido</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: 8 }}>Expira</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: 8 }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {items.map((it) => (
                <tr key={it.id}>
                  <td style={{ borderBottom: '1px solid #f3f4f6', padding: 8 }}>{it.id}</td>
                  <td style={{ borderBottom: '1px solid #f3f4f6', padding: 8 }}>{it.resource}</td>
                  <td style={{ borderBottom: '1px solid #f3f4f6', padding: 8 }}>{it.purpose}</td>
                  <td style={{ borderBottom: '1px solid #f3f4f6', padding: 8 }}>{it.scope}</td>
                  <td style={{ borderBottom: '1px solid #f3f4f6', padding: 8 }}>{it.allowed ? 'Sí' : 'No'}</td>
                  <td style={{ borderBottom: '1px solid #f3f4f6', padding: 8 }}>{it.expires_at || '-'}</td>
                  <td style={{ borderBottom: '1px solid #f3f4f6', padding: 8 }}>
                    <button onClick={() => remove(it)} style={{ padding: '6px 10px' }}>Eliminar</button>
                  </td>
                </tr>
              ))}
              {items.length === 0 && !loading && (
                <tr>
                  <td colSpan={7} style={{ padding: 12, color: '#6b7280' }}>Sin consentimientos</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </RequireApiKey>
  )
}
