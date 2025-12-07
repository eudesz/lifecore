import React, { useEffect, useState } from 'react';
import ChartCard from '../../components/ChartCard';
import { fetchObservations, analyze, downloadReport } from '../../lib/api';
import RequireApiKey from '../../components/RequireApiKey';
import ProtectedRoute from '../../components/auth/ProtectedRoute';
import { useAuth } from '../../context/AuthContext';

export default function InformationalDashboard() {
  const { user } = useAuth()
  const userId = user?.id?.toString() || '1'
  const [latest, setLatest] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const [analysis, setAnalysis] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [code, setCode] = useState<string>('')

  useEffect(() => {
    let cancelled = false
    async function run() {
      try {
        const res = await fetchObservations({ user_id: userId })
        const obs = res.observations || []
        const byCode: Record<string, any[]> = {}
        obs.forEach(o => {
          byCode[o.code] = byCode[o.code] || []
          byCode[o.code].push(o)
        })
        const latestList = Object.entries(byCode).map(([code, arr]) => arr[arr.length - 1])
        if (!cancelled) setLatest(latestList)
      } catch (e: any) {
        if (!cancelled) setError(e.message)
      }
    }
    run()
    return () => { cancelled = true }
  }, [userId])

  const runAnalysis = async () => {
    try {
      setLoading(true)
      setAnalysis('')
      const q = '¿Cuál es el último valor disponible de glucosa?'
      const res = await analyze(q, userId)
      setAnalysis(res.final_text || '')
    } catch (e: any) {
      setAnalysis(`Error: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  const exportCsv = () => downloadReport('/api/reports/observations.csv', { user_id: userId, ...(code ? { code } : {} as any) })
  const exportSummary = () => downloadReport('/api/reports/summary.md', { user_id: userId, ...(code ? { code } : {} as any) })

  return (
    <ProtectedRoute>
    <RequireApiKey>
        <main id="content" className="container" style={{ paddingTop: 'var(--space-lg)' }}>
        <h1>Dashboard Informacional</h1>
        <ChartCard title="Últimos valores">
          {error && <div role="alert" style={{ color: '#b91c1c' }}>Error: {error}</div>}
          {!error && (
            <table className="table" aria-label="Últimos valores por código">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Valor</th>
                  <th>Unidad</th>
                  <th>Fecha</th>
                </tr>
              </thead>
              <tbody>
                {latest.map((o: any) => (
                  <tr key={o.id}>
                    <td>{o.code}</td>
                    <td>{o.value}</td>
                    <td>{o.unit}</td>
                    <td>{new Date(o.taken_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </ChartCard>
        <ChartCard title="Consulta rápida">
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
            <button className="btn" onClick={runAnalysis} disabled={loading} aria-busy={loading}>
              {loading ? 'Consultando…' : 'Preguntar último valor de glucosa'}
            </button>
            <label htmlFor="code" className="muted" style={{ fontWeight: 600 }}>Parámetro</label>
            <select id="code" value={code} onChange={e => setCode(e.target.value)} style={{ padding: 8 }} aria-label="Filtrar exportación por código">
              <option value="">(todos los parámetros)</option>
              <option value="glucose">glucose</option>
              <option value="cholesterol">cholesterol</option>
              <option value="weight">weight</option>
              <option value="blood_pressure_systolic">blood_pressure_systolic</option>
              <option value="blood_pressure_diastolic">blood_pressure_diastolic</option>
            </select>
            <button className="btn secondary" onClick={exportCsv}>Exportar CSV</button>
            <button className="btn secondary" onClick={exportSummary}>Exportar Resumen (.md)</button>
          </div>
          {analysis && (
            <pre style={{ marginTop: 12, background: 'var(--bg-muted)', padding: 12, whiteSpace: 'pre-wrap' }}>{analysis}</pre>
          )}
        </ChartCard>
      </main>
    </RequireApiKey>
  </ProtectedRoute>
  );
}
