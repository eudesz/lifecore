import React, { useEffect, useMemo, useState } from 'react'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import RequireApiKey from '@/components/RequireApiKey'
import { useAuth } from '@/context/AuthContext'
import DateRange from '@/components/DateRange'
import { fetchObservations } from '@/lib/api'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  Area,
  ScatterChart,
  Scatter,
  ZAxis,
} from 'recharts'

type ObsPoint = { taken_at: string; value: number }
type SeriesMap = Record<string, ObsPoint[]>

const PARAMS = [
  { code: 'glucose', label: 'Glucosa', color: '#ef4444' },
  { code: 'blood_pressure_systolic', label: 'PA Sistólica', color: '#3b82f6' },
  { code: 'cholesterol', label: 'Colesterol', color: '#10b981' },
  { code: 'weight', label: 'Peso', color: '#f59e0b' },
  { code: 'sleep_hours', label: 'Sueño (h)', color: '#8b5cf6' },
  { code: 'steps', label: 'Pasos', color: '#22c55e' },
  { code: 'mood', label: 'Ánimo (1-10)', color: '#ec4899' },
]

function mergeSeriesToChartData(seriesMap: SeriesMap) {
  const allTimestamps = new Set<number>()
  Object.values(seriesMap).forEach(arr => {
    arr.forEach(p => {
      const t = new Date(p.taken_at).getTime()
      if (!isNaN(t)) allTimestamps.add(t)
    })
  })
  const sorted = Array.from(allTimestamps).sort((a, b) => a - b)
  return sorted.map(ts => {
    const row: any = { x: ts }
    for (const key of Object.keys(seriesMap)) {
      const found = seriesMap[key].find(p => new Date(p.taken_at).getTime() === ts)
      row[key] = typeof found?.value === 'number' ? Number(found.value) : undefined
    }
    return row
  })
}

export default function AnalyticsDashboard() {
  const { user } = useAuth()
  const userId = user?.id?.toString() || ''
  const [selectedParams, setSelectedParams] = useState<string[]>(['glucose', 'blood_pressure_systolic'])
  const [chartMode, setChartMode] = useState<'line' | 'area'>('line')
  const [seriesMap, setSeriesMap] = useState<SeriesMap>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [since, setSince] = useState<string | undefined>(undefined)
  const [until, setUntil] = useState<string | undefined>(undefined)
  const [xParam, setXParam] = useState<string>('glucose')
  const [yParam, setYParam] = useState<string>('weight')

  useEffect(() => {
    if (!userId || selectedParams.length === 0) return
    const load = async () => {
      try {
        setLoading(true)
        setError(null)
        const entries = await Promise.all(
          selectedParams.map(async (code) => {
            const res = await fetchObservations({ user_id: userId, code, ...(since ? { since } : {} as any), ...(until ? { until } : {} as any) })
            const pts = (res.observations || []).map((o: any) => ({
              taken_at: o.taken_at,
              value: Number(o.value),
            })) as ObsPoint[]
            return [code, pts] as const
          })
        )
        const map: SeriesMap = {}
        entries.forEach(([code, pts]) => { map[code] = pts })
        setSeriesMap(map)
      } catch (e: any) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [userId, selectedParams.join(','), since, until])

  const chartData = useMemo(() => mergeSeriesToChartData(seriesMap), [seriesMap])

  const scatterData = useMemo(() => {
    const xs = seriesMap[xParam] || []
    const ys = seriesMap[yParam] || []
    // Join by nearest timestamp day-level
    const byDay = (arr: ObsPoint[]) => {
      const m = new Map<string, number>()
      arr.forEach(p => {
        const d = new Date(p.taken_at)
        const key = new Date(d.getFullYear(), d.getMonth(), d.getDate()).toISOString()
        m.set(key, Number(p.value))
      })
      return m
    }
    const mx = byDay(xs)
    const my = byDay(ys)
    const keys = Array.from(new Set([...mx.keys(), ...my.keys()])).sort()
    return keys
      .map(k => ({ x: mx.get(k), y: my.get(k) }))
      .filter(p => typeof p.x === 'number' && typeof p.y === 'number')
  }, [seriesMap, xParam, yParam])

  const toggleParam = (code: string) => {
    setSelectedParams(prev => prev.includes(code) ? prev.filter(c => c !== code) : [...prev, code])
  }

  return (
    <ProtectedRoute>
      <RequireApiKey>
        <main id="content" className="container" style={{ paddingTop: 'var(--space-lg)' }}>
          <h1 style={{ marginBottom: 8 }}>Analítica Interactiva</h1>
          <p className="muted">Visualiza la evolución de múltiples parámetros y sus relaciones.</p>

          <section className="card" style={{ padding: 16, marginTop: 12 }}>
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'flex-end' }}>
              <div>
                <label style={{ display: 'block', fontWeight: 600 }}>Rango temporal</label>
                <DateRange onApply={({ since: s, until: u }) => { setSince(s); setUntil(u) }} />
              </div>
              <div>
                <label style={{ display: 'block', fontWeight: 600 }}>Modo gráfico</label>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button className={`btn ${chartMode === 'line' ? '' : 'secondary'}`} onClick={() => setChartMode('line')}>Líneas</button>
                  <button className={`btn ${chartMode === 'area' ? '' : 'secondary'}`} onClick={() => setChartMode('area')}>Áreas</button>
                </div>
              </div>
            </div>
            <div style={{ marginTop: 12, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {PARAMS.map(p => {
                const active = selectedParams.includes(p.code)
                return (
                  <button
                    key={p.code}
                    onClick={() => toggleParam(p.code)}
                    className={`btn ${active ? '' : 'secondary'}`}
                    style={{ borderColor: p.color }}
                  >
                    {p.label}
                  </button>
                )
              })}
            </div>
          </section>

          <section className="card" style={{ marginTop: 16 }}>
            <h3 style={{ margin: '12px 16px' }}>Evolución temporal</h3>
            {loading && <div style={{ padding: 16, color: '#6b7280' }}>Cargando…</div>}
            {error && <div style={{ padding: 16, color: '#b91c1c' }}>Error: {error}</div>}
            {!loading && !error && (
              <div style={{ width: '100%', height: 'min(65vh, 420px)' }}>
                <ResponsiveContainer>
                  <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="x"
                      tickFormatter={(v) => new Date(v).toLocaleDateString()}
                      type="number"
                      domain={['auto', 'auto']}
                    />
                    <YAxis />
                    <Tooltip labelFormatter={(v) => new Date(v as number).toLocaleString()} />
                    <Legend />
                    {selectedParams.map(code => {
                      const conf = PARAMS.find(p => p.code === code)!
                      return chartMode === 'line' ? (
                        <Line
                          key={code}
                          type="monotone"
                          dataKey={code}
                          stroke={conf.color}
                          dot={false}
                          name={conf.label}
                          connectNulls
                        />
                      ) : (
                        <Area
                          key={code}
                          type="monotone"
                          dataKey={code}
                          stroke={conf.color}
                          fill={conf.color + '33'}
                          name={conf.label}
                          connectNulls
                        />
                      )
                    })}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </section>

          <section className="card" style={{ marginTop: 16 }}>
            <h3 style={{ margin: '12px 16px' }}>Relaciones entre parámetros</h3>
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', padding: '0 16px 12px' }}>
              <div>
                <label style={{ display: 'block', fontWeight: 600 }}>Eje X</label>
                <select value={xParam} onChange={e => setXParam(e.target.value)} style={{ padding: 6 }}>
                  {PARAMS.map(p => <option key={p.code} value={p.code}>{p.label}</option>)}
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontWeight: 600 }}>Eje Y</label>
                <select value={yParam} onChange={e => setYParam(e.target.value)} style={{ padding: 6 }}>
                  {PARAMS.map(p => <option key={p.code} value={p.code}>{p.label}</option>)}
                </select>
              </div>
            </div>
            <div style={{ width: '100%', height: 'min(60vh, 360px)' }}>
              <ResponsiveContainer>
                <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" dataKey="x" name="X" />
                  <YAxis type="number" dataKey="y" name="Y" />
                  <ZAxis type="number" dataKey="z" range={[60, 200]} />
                  <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                  <Scatter data={scatterData} fill="#64748b" />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </section>
        </main>
      </RequireApiKey>
    </ProtectedRoute>
  )
}


