import React, { useEffect, useState } from 'react';
import ChartCard from '../../components/ChartCard';
import { fetchObservations, analyze, downloadReport } from '../../lib/api';
import DateRange from '../../components/DateRange';
import ScatterChartBasic from '../../components/charts/ScatterChartBasic';
import ProtectedRoute from '../../components/auth/ProtectedRoute';
import { useAuth } from '../../context/AuthContext';

function corr(a: number[], b: number[]) {
  const n = Math.min(a.length, b.length)
  if (n < 3) return NaN
  const x = a.slice(-n)
  const y = b.slice(-n)
  const mean = (arr: number[]) => arr.reduce((s, v) => s + v, 0) / arr.length
  const mx = mean(x), my = mean(y)
  let num = 0, dx = 0, dy = 0
  for (let i = 0; i < n; i++) {
    const vx = x[i] - mx
    const vy = y[i] - my
    num += vx * vy
    dx += vx * vx
    dy += vy * vy
  }
  const den = Math.sqrt(dx * dy)
  return den === 0 ? NaN : num / den
}

const OPTIONS = [
  { value: 'glucose', label: 'Glucosa' },
  { value: 'weight', label: 'Peso' },
  { value: 'cholesterol', label: 'Colesterol' },
  { value: 'blood_pressure_systolic', label: 'PA Sistólica' },
  { value: 'blood_pressure_diastolic', label: 'PA Diastólica' },
]

export default function CorrelationDashboard() {
  const { user } = useAuth()
  const userId = user?.id?.toString() || '1'
  const [code1, setCode1] = useState<string>('glucose')
  const [code2, setCode2] = useState<string>('weight')
  const [s1, setS1] = useState<number[]>([])
  const [s2, setS2] = useState<number[]>([])
  const [r, setR] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [analysis, setAnalysis] = useState('')
  const [loading, setLoading] = useState(false)
  const [since, setSince] = useState<string | undefined>(undefined)
  const [until, setUntil] = useState<string | undefined>(undefined)

  useEffect(() => {
    let cancelled = false
    async function run() {
      try {
        const [a, b] = await Promise.all([
          fetchObservations({ user_id: userId, code: code1, ...(since ? { since } : {} as any), ...(until ? { until } : {} as any) }),
          fetchObservations({ user_id: userId, code: code2, ...(since ? { since } : {} as any), ...(until ? { until } : {} as any) }),
        ])
        const av = (a.observations || []).map((o: any) => Number(o.value))
        const bv = (b.observations || []).map((o: any) => Number(o.value))
        const c = corr(av, bv)
        if (!cancelled) {
          setS1(av)
          setS2(bv)
          setR(isNaN(c) ? null : c)
        }
      } catch (e: any) {
        if (!cancelled) setError(e.message)
      }
    }
    run()
    return () => { cancelled = true }
  }, [userId, code1, code2, since, until])

  const runAnalysis = async () => {
    try {
      setLoading(true)
      setAnalysis('')
      const q = `Analiza la correlación entre ${code1} y ${code2}`
      const res = await analyze(q, userId, { code1, code2, ...(since ? { since } : {}), ...(until ? { until } : {}) })
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
      <h1>Dashboard de Correlación</h1>
      <DateRange onApply={({ since: s, until: e }) => { setSince(s); setUntil(e) }} />
      <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end', marginBottom: 12 }}>
        <div>
          <label>Parámetro X</label>
          <select value={code1} onChange={(e) => setCode1(e.target.value)} style={{ display: 'block', padding: 6, width: 220 }}>
            {OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>
        <div>
          <label>Parámetro Y</label>
          <select value={code2} onChange={(e) => setCode2(e.target.value)} style={{ display: 'block', padding: 6, width: 220 }}>
            {OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>
        <button onClick={runAnalysis} disabled={loading} style={{ padding: '8px 12px', height: 38 }}>
          {loading ? 'Consultando…' : 'Analizar correlación'}
        </button>
      </div>
      {error && <div style={{ color: '#b91c1c' }}>Error: {error}</div>}
      <ChartCard title="Dispersión">
        <div>Observaciones X: {s1.length}</div>
        <div>Observaciones Y: {s2.length}</div>
        <div>Correlación (r): {r === null ? 'N/D' : r.toFixed(3)}</div>
        <ScatterChartBasic x={s1} y={s2} />
        <div style={{ marginTop: 8 }}>
          <button onClick={() => downloadReport('/api/reports/observations.csv', { user_id: userId, code: code1, ...(since ? { since } : {} as any), ...(until ? { until } : {} as any) })} style={{ padding: '6px 10px', marginRight: 8 }}>Exportar CSV (X)</button>
          <button onClick={() => downloadReport('/api/reports/observations.csv', { user_id: userId, code: code2, ...(since ? { since } : {} as any), ...(until ? { until } : {} as any) })} style={{ padding: '6px 10px', marginRight: 8 }}>Exportar CSV (Y)</button>
          <button onClick={() => downloadReport('/api/reports/summary.md', { user_id: userId, ...(since ? { since } : {} as any), ...(until ? { until } : {} as any) })} style={{ padding: '6px 10px' }}>Exportar Resumen</button>
        </div>
      </ChartCard>
      <ChartCard title="Consulta rápida">
        <button onClick={runAnalysis} disabled={loading} style={{ padding: '8px 12px' }}>
          {loading ? 'Consultando…' : `Analizar correlación ${code1} vs ${code2}`}
        </button>
        {analysis && (
          <pre style={{ marginTop: 12, background: '#f9fafb', padding: 12, whiteSpace: 'pre-wrap' }}>{analysis}</pre>
        )}
      </ChartCard>
    </div>
  </ProtectedRoute>
  );
}

export async function getServerSideProps() {
  return { props: {} }
}
