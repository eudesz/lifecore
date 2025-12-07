import React, { useEffect, useState } from 'react';
import ChartCard from '../../components/ChartCard';
import { fetchObservations, analyze, downloadReport } from '../../lib/api';
import DateRange from '../../components/DateRange';
import ProtectedRoute from '../../components/auth/ProtectedRoute';
import { useAuth } from '../../context/AuthContext';

function latest(series: any[]) { return series && series.length ? series[series.length - 1] : null }

function framinghamSimplified(params: { age: number; total_chol: number; systolic: number; smoking: boolean; diabetes: boolean }) {
  let points = 0
  if (params.age >= 40) points += (params.age - 40) * 0.5
  if (params.total_chol > 240) points += 2; else if (params.total_chol > 200) points += 1
  if (params.systolic > 160) points += 3; else if (params.systolic > 140) points += 2; else if (params.systolic > 120) points += 1
  if (params.diabetes) points += 2
  if (params.smoking) points += 2
  const risk = Math.min(points * 2, 30)
  let cat = 'Bajo'
  if (risk >= 20) cat = 'Muy Alto'; else if (risk >= 10) cat = 'Alto'; else if (risk >= 5) cat = 'Moderado'
  return { risk: Number(risk.toFixed(1)), category: cat }
}

export default function RiskDashboard() {
  const { user } = useAuth()
  const userId = user?.id?.toString() || '1'
  const [risk, setRisk] = useState<{ risk: number; category: string } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [analysis, setAnalysis] = useState('')
  const [loading, setLoading] = useState(false)
  const [since, setSince] = useState<string | undefined>(undefined)
  const [until, setUntil] = useState<string | undefined>(undefined)

  useEffect(() => {
    let cancelled = false
    async function run() {
      try {
        const [chol, sys] = await Promise.all([
          fetchObservations({ user_id: userId, code: 'cholesterol', ...(since ? { since } : {} as any), ...(until ? { until } : {} as any) }),
          fetchObservations({ user_id: userId, code: 'blood_pressure_systolic', ...(since ? { since } : {} as any), ...(until ? { until } : {} as any) }),
        ])
        const lc = latest(chol.observations || [])
        const ls = latest(sys.observations || [])
        const r = framinghamSimplified({
          age: 45,
          total_chol: lc ? Number(lc.value) : 200,
          systolic: ls ? Number(ls.value) : 120,
          smoking: false,
          diabetes: false,
        })
        if (!cancelled) setRisk(r)
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
      const q = 'Evalúa factores de riesgo cardiovascular con los datos disponibles (sin diagnóstico)'
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
      <h1>Dashboard de Riesgo</h1>
      <DateRange onApply={({ since: s, until: e }) => { setSince(s); setUntil(e) }} />
      {error && <div style={{ color: '#b91c1c' }}>Error: {error}</div>}
      <ChartCard title="Riesgo Cardiovascular (simplificado)">
        {risk ? (
          <div>
            <div>Riesgo estimado: {risk.risk}%</div>
            <div>Categoría: {risk.category}</div>
            <div style={{ marginTop: 8 }}>
              <button onClick={() => downloadReport('/api/reports/observations.csv', { user_id: userId, code: 'cholesterol', ...(since ? { since } : {} as any), ...(until ? { until } : {} as any) })} style={{ padding: '6px 10px', marginRight: 8 }}>Exportar CSV (colesterol)</button>
              <button onClick={() => downloadReport('/api/reports/observations.csv', { user_id: userId, code: 'blood_pressure_systolic', ...(since ? { since } : {} as any), ...(until ? { until } : {} as any) })} style={{ padding: '6px 10px', marginRight: 8 }}>Exportar CSV (PA sistólica)</button>
              <button onClick={() => downloadReport('/api/reports/summary.md', { user_id: userId, ...(since ? { since } : {} as any), ...(until ? { until } : {} as any) })} style={{ padding: '6px 10px' }}>Exportar Resumen</button>
            </div>
          </div>
        ) : (
          <div>Datos insuficientes</div>
        )}
      </ChartCard>
      <ChartCard title="Consulta rápida">
        <button onClick={runAnalysis} disabled={loading} style={{ padding: '8px 12px' }}>
          {loading ? 'Consultando…' : 'Evaluación de factores de riesgo'}
        </button>
        {analysis && (
          <pre style={{ marginTop: 12, background: '#f9fafb', padding: 12, whiteSpace: 'pre-wrap' }}>{analysis}</pre>
        )}
      </ChartCard>
    </div>
  </ProtectedRoute>
  );
}
