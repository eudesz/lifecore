import React, { useEffect, useState } from 'react';
import ChartCard from '../../components/ChartCard';
import { fetchObservations, analyze, downloadReport } from '../../lib/api';
import DateRange from '../../components/DateRange';
import TimeSeriesChart from '../../components/charts/TimeSeriesChart';
import ProtectedRoute from '../../components/auth/ProtectedRoute';
import { useAuth } from '../../context/AuthContext';

export default function TemporalDashboard() {
  const { user } = useAuth()
  const userId = user?.id?.toString() || '1'
  const [glucose, setGlucose] = useState<any[]>([])
  const [bpSys, setBpSys] = useState<any[]>([])
  const [bpDia, setBpDia] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const [analysis, setAnalysis] = useState('')
  const [loading, setLoading] = useState(false)
  const [since, setSince] = useState<string | undefined>(undefined)
  const [until, setUntil] = useState<string | undefined>(undefined)
  const [maWindow, setMaWindow] = useState<number>(3)
  const [zThreshold, setZThreshold] = useState<number>(2.0)

  const load = async (u: string, s?: string, e?: string) => {
    let cancelled = false
    try {
      const [g, s1, d1] = await Promise.all([
        fetchObservations({ user_id: u, code: 'glucose', ...(s ? { since: s } : {}), ...(e ? { until: e } : {}) }),
        fetchObservations({ user_id: u, code: 'blood_pressure_systolic', ...(s ? { since: s } : {}), ...(e ? { until: e } : {}) }),
        fetchObservations({ user_id: u, code: 'blood_pressure_diastolic', ...(s ? { since: s } : {}), ...(e ? { until: e } : {}) }),
      ])
      if (!cancelled) {
        setGlucose((g.observations || []).map((o: any) => ({ ...o, taken_at: o.taken_at })))
        setBpSys((s1.observations || []).map((o: any) => ({ ...o, taken_at: o.taken_at })))
        setBpDia((d1.observations || []).map((o: any) => ({ ...o, taken_at: o.taken_at })))
      }
    } catch (e: any) {
      setError(e.message)
    }
    return () => { cancelled = true }
  }

  useEffect(() => {
    load(userId, since, until)
  }, [userId, since, until])

  const runAnalysis = async () => {
    try {
      setLoading(true)
      setAnalysis('')
      const q = 'Analiza la evolución de la glucosa en el rango seleccionado'
      const res = await analyze(q, userId, { code: 'glucose', ma_window: maWindow, z_threshold: zThreshold, ...(since ? { since } : {}), ...(until ? { until } : {}) })
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
      <h1>Dashboard Temporal</h1>
      <DateRange onApply={({ since: s, until: e }) => { setSince(s); setUntil(e) }} />
      <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end', marginBottom: 12 }}>
        <div>
          <label>Ventana media móvil</label>
          <input type="number" min={1} max={60} value={maWindow} onChange={(e) => setMaWindow(parseInt(e.target.value || '1', 10))} style={{ display: 'block', padding: 6, width: 140 }} />
        </div>
        <div>
          <label>Umbral z-score</label>
          <input type="number" step="0.1" min={0.1} max={10} value={zThreshold} onChange={(e) => setZThreshold(parseFloat(e.target.value || '2'))} style={{ display: 'block', padding: 6, width: 140 }} />
        </div>
        <button onClick={runAnalysis} disabled={loading} style={{ padding: '8px 12px', height: 38 }}>
          {loading ? 'Consultando…' : 'Analizar evolución'}
        </button>
      </div>
      {error && <div style={{ color: '#b91c1c' }}>Error: {error}</div>}
      <ChartCard title="Serie de Glucosa">
        <div>Total de mediciones: {glucose.length}</div>
        <TimeSeriesChart data={glucose} xKey="taken_at" yKey="value" />
        <div style={{ marginTop: 8 }}>
          <button onClick={() => downloadReport('/api/reports/observations.csv', { user_id: userId, code: 'glucose', ...(since ? { since } : {} as any), ...(until ? { until } : {} as any) })} style={{ padding: '6px 10px', marginRight: 8 }}>Exportar CSV</button>
          <button onClick={() => downloadReport('/api/reports/summary.md', { user_id: userId, code: 'glucose', ...(since ? { since } : {} as any), ...(until ? { until } : {} as any) })} style={{ padding: '6px 10px' }}>Exportar Resumen</button>
        </div>
      </ChartCard>
      <ChartCard title="Presión Arterial">
        <div>Mediciones sistólica: {bpSys.length}</div>
        <TimeSeriesChart data={bpSys} xKey="taken_at" yKey="value" />
        <div>Mediciones diastólica: {bpDia.length}</div>
        <TimeSeriesChart data={bpDia} xKey="taken_at" yKey="value" />
      </ChartCard>
      <ChartCard title="Consulta rápida">
        <button onClick={runAnalysis} disabled={loading} style={{ padding: '8px 12px' }}>
          {loading ? 'Consultando…' : 'Analizar evolución de glucosa'}
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
