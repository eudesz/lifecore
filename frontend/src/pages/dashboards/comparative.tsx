import React, { useEffect, useState } from 'react';
import ChartCard from '../../components/ChartCard';
import { fetchObservations, analyze, downloadReport } from '../../lib/api';
import DateRange from '../../components/DateRange';
import ProtectedRoute from '../../components/auth/ProtectedRoute';
import { useAuth } from '../../context/AuthContext';

function summarizeChange(series: any[]) {
  if (!series || series.length < 2) return null
  const mid = Math.floor(series.length / 2)
  const early = series.slice(0, mid)
  const recent = series.slice(mid)
  const avg = (arr: any[]) => arr.reduce((s, x) => s + Number(x.value || 0), 0) / (arr.length || 1)
  const a1 = avg(early), a2 = avg(recent)
  const delta = a2 - a1
  const pct = a1 !== 0 ? (delta / a1) * 100 : 0
  return { from: a1, to: a2, delta, pct }
}

export default function ComparativeDashboard() {
  const { user } = useAuth()
  const userId = user?.id?.toString() || '1'
  const [chol, setChol] = useState<any[]>([])
  const [summary, setSummary] = useState<any | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [analysis, setAnalysis] = useState('')
  const [loading, setLoading] = useState(false)
  const [since, setSince] = useState<string | undefined>(undefined)
  const [until, setUntil] = useState<string | undefined>(undefined)

  useEffect(() => {
    let cancelled = false
    async function run() {
      try {
        const c = await fetchObservations({ user_id: userId, code: 'cholesterol', ...(since ? { since } : {} as any), ...(until ? { until } : {} as any) })
        const series = c.observations || []
        if (!cancelled) {
          setChol(series)
          setSummary(summarizeChange(series))
        }
      } catch (e: any) {
        if (!cancelled) setError(e.message)
      }
    }
    run()
    return () => { cancelled = true }
  }, [userId, since, until])

  const runAnalysis = async () => {
    try {
      setLoading(true)
      setAnalysis('')
      const q = 'Compara los niveles de colesterol antes y después del tratamiento'
      const res = await analyze(q, userId)
      setAnalysis(res.final_text || '')
    } catch (e: any) {
      setAnalysis(`Error: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <ProtectedRoute>
    <div style={{ maxWidth: 960, margin: '0 auto', padding: 24 }}>
      <h1>Dashboard Comparativo</h1>
      <DateRange onApply={({ since: s, until: e }) => { setSince(s); setUntil(e) }} />
      {error && <div style={{ color: '#b91c1c' }}>Error: {error}</div>}
      <ChartCard title="Colesterol: antes vs después">
        {summary ? (
          <div>
            <div>Promedio inicial: {summary.from.toFixed(1)}</div>
            <div>Promedio reciente: {summary.to.toFixed(1)}</div>
            <div>Cambio absoluto: {summary.delta.toFixed(1)}</div>
            <div>Cambio relativo: {summary.pct.toFixed(1)}%</div>
            <div style={{ marginTop: 8 }}>
              <button onClick={() => downloadReport('/api/reports/observations.csv', { user_id: userId, code: 'cholesterol', ...(since ? { since } : {} as any), ...(until ? { until } : {} as any) })} style={{ padding: '6px 10px', marginRight: 8 }}>Exportar CSV</button>
              <button onClick={() => downloadReport('/api/reports/summary.md', { user_id: userId, code: 'cholesterol', ...(since ? { since } : {} as any), ...(until ? { until } : {} as any) })} style={{ padding: '6px 10px' }}>Exportar Resumen</button>
            </div>
          </div>
        ) : (
          <div>Datos insuficientes</div>
        )}
      </ChartCard>
      <ChartCard title="Consulta rápida">
        <button onClick={runAnalysis} disabled={loading} style={{ padding: '8px 12px' }}>
          {loading ? 'Consultando…' : 'Comparar colesterol antes/después'}
        </button>
        {analysis && (
          <pre style={{ marginTop: 12, background: '#f9fafb', padding: 12, whiteSpace: 'pre-wrap' }}>{analysis}</pre>
        )}
      </ChartCard>
    </div>
  </ProtectedRoute>
  );
}
