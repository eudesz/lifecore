import React, { useEffect, useState } from 'react'
import RequireApiKey from '../../components/RequireApiKey'

function getApiKey(): string | undefined {
  if (process.env.NEXT_PUBLIC_PLATFORM_API_KEY) return process.env.NEXT_PUBLIC_PLATFORM_API_KEY
  if (typeof window !== 'undefined') return localStorage.getItem('PLATFORM_API_KEY') || undefined
  return undefined
}

export default function AuditDashboard() {
  const [logs, setLogs] = useState<any[]>([])
  const [limit, setLimit] = useState<number>(100)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    try {
      setLoading(true)
      setError(null)
      const key = getApiKey()
      const res = await fetch(`/api/lifecore/audit?limit=${limit}`, {
        headers: key ? { Authorization: `Bearer ${key}` } : undefined,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`)
      setLogs(data.logs || [])
    } catch (e: any) {
      setError(e.message)
      setLogs([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <RequireApiKey>
      <div style={{ maxWidth: 1000, margin: '0 auto', padding: 24 }}>
        <h1>Auditoría (Admin)</h1>
        <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end' }}>
          <div>
            <label>Límite</label>
            <input type="number" min={1} max={500} value={limit} onChange={(e) => setLimit(parseInt(e.target.value || '100', 10))} style={{ display: 'block', padding: 6, width: 120 }} />
          </div>
          <button onClick={load} disabled={loading} style={{ padding: '8px 12px', height: 38 }}>
            {loading ? 'Cargando…' : 'Actualizar'}
          </button>
        </div>
        {error && <div style={{ marginTop: 12, color: '#b91c1c' }}>Error: {error}</div>}
        <div style={{ marginTop: 16, overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: 8 }}>Fecha</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: 8 }}>User</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: 8 }}>Rol</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: 8 }}>Recurso</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: 8 }}>Acción</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: 8 }}>OK</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: 8 }}>Status</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: 8 }}>Path</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: 8 }}>IP</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((l, idx) => (
                <tr key={idx}>
                  <td style={{ borderBottom: '1px solid #f3f4f6', padding: 8 }}>{l.created_at}</td>
                  <td style={{ borderBottom: '1px solid #f3f4f6', padding: 8 }}>{l.user ?? '-'}</td>
                  <td style={{ borderBottom: '1px solid #f3f4f6', padding: 8 }}>{l.actor_role}</td>
                  <td style={{ borderBottom: '1px solid #f3f4f6', padding: 8 }}>{l.resource}</td>
                  <td style={{ borderBottom: '1px solid #f3f4f6', padding: 8 }}>{l.action}</td>
                  <td style={{ borderBottom: '1px solid #f3f4f6', padding: 8 }}>{l.success ? 'Sí' : 'No'}</td>
                  <td style={{ borderBottom: '1px solid #f3f4f6', padding: 8 }}>{l.status_code}</td>
                  <td style={{ borderBottom: '1px solid #f3f4f6', padding: 8 }}>{l.path}</td>
                  <td style={{ borderBottom: '1px solid #f3f4f6', padding: 8 }}>{l.ip || '-'}</td>
                </tr>
              ))}
              {logs.length === 0 && !loading && (
                <tr>
                  <td colSpan={9} style={{ padding: 12, color: '#6b7280' }}>Sin registros</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </RequireApiKey>
  )
}
