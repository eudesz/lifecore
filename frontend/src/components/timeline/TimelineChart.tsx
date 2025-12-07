import React, { useMemo, useState, useRef, useEffect } from 'react'
import {
  ResponsiveContainer,
  ScatterChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Scatter,
} from 'recharts'

export interface TimelineEvent {
  id: string | number
  date: string
  category: string
  title?: string
  description?: string
  metrics?: Record<string, any>
  severity?: string | null
  related_conditions?: string[]
  document_id?: string | number | null
}

interface Props {
  events: TimelineEvent[]
  onSelect?: (event: TimelineEvent) => void
  groupByCondition?: boolean
  selectedConditions?: string[]
}

interface ChartPoint extends TimelineEvent {
  timestamp: number
}

function formatDateShort(ts: number) {
  const d = new Date(ts)
  return d.toLocaleDateString(undefined, { year: '2-digit', month: 'short', day: 'numeric' })
}

function formatYear(ts: number) {
  return new Date(ts).getFullYear().toString()
}

export default function TimelineChart({ events, onSelect, groupByCondition, selectedConditions }: Props) {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768)
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  const filtered = useMemo(() => {
    let out = [...events]
    if (groupByCondition && selectedConditions && selectedConditions.length) {
      out = out.filter(ev => {
        const rel = ev.related_conditions || []
        return rel.length ? selectedConditions.some(s => rel.includes(s)) : false
      })
    }
    return out
  }, [events, groupByCondition, selectedConditions])

  // --- MOBILE "CYBER-STREAM" RENDER ---
  if (isMobile) {
    const groupedByYear = useMemo(() => {
      const groups: Record<string, TimelineEvent[]> = {}
      filtered.forEach(ev => {
        const year = new Date(ev.date).getFullYear()
        if (!groups[year]) groups[year] = []
        groups[year].push(ev)
      })
      return Object.entries(groups)
        .sort((a, b) => Number(b[0]) - Number(a[0]))
        .map(([year, evs]) => ({
          year,
          events: evs.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
        }))
    }, [filtered])

    if (!filtered.length) {
      return <div className="muted" style={{ padding: 16, textAlign: 'center' }}>No events found in this period.</div>
    }

    return (
      <div style={{ 
        height: '100%', 
        overflowY: 'auto', 
        padding: '10px', 
        position: 'relative',
        scrollBehavior: 'smooth'
      }}>
        <div style={{
          position: 'absolute',
          left: '20px',
          top: 0,
          bottom: 0,
          width: '2px',
          background: 'linear-gradient(to bottom, transparent, var(--primary) 10%, var(--primary) 90%, transparent)',
          opacity: 0.3,
          zIndex: 0
        }} />

        {groupedByYear.map(({ year, events }) => (
          <div key={year} style={{ marginBottom: 30, position: 'relative', zIndex: 1 }}>
            <div style={{ 
              position: 'sticky', 
              top: 0, 
              background: 'var(--bg-dark)', 
              padding: '8px 0', 
              zIndex: 10,
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              marginBottom: 12
            }}>
              <div style={{ 
                background: 'rgba(0, 242, 234, 0.1)', 
                color: 'var(--primary)', 
                padding: '4px 12px', 
                borderRadius: '12px', 
                fontSize: '12px', 
                fontWeight: 700,
                border: '1px solid rgba(0, 242, 234, 0.3)'
              }}>
                {year}
              </div>
              <div style={{ height: 1, flex: 1, background: 'var(--border-light)' }}></div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {events.map(ev => (
                <div 
                  key={ev.id}
                  onClick={() => onSelect && onSelect(ev)}
                  style={{
                    marginLeft: '20px',
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid var(--border-light)',
                    borderRadius: '12px',
                    padding: '12px',
                    position: 'relative',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{
                    position: 'absolute',
                    left: '-25px',
                    top: '18px',
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    background: 'var(--bg-deep)',
                    border: '2px solid var(--primary)',
                    boxShadow: '0 0 8px var(--primary)'
                  }} />

                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ 
                      fontSize: '10px', 
                      textTransform: 'uppercase', 
                      color: 'var(--text-muted)', 
                      letterSpacing: '0.05em' 
                    }}>
                      {new Date(ev.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                    </span>
                    <span style={{ 
                      fontSize: '10px', 
                      background: 'rgba(255,255,255,0.1)', 
                      padding: '2px 6px', 
                      borderRadius: '4px',
                      color: 'var(--text-main)'
                    }}>
                      {ev.category}
                    </span>
                  </div>

                  <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-main)', marginBottom: 6 }}>
                    {ev.title || 'Event'}
                  </div>

                  {ev.metrics && Object.keys(ev.metrics).length > 0 && (
                    <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap' }}>
                      {Object.entries(ev.metrics).slice(0, 2).map(([k, v]) => (
                        <div key={k} style={{ 
                          fontSize: '11px', 
                          color: 'var(--primary)', 
                          background: 'rgba(0, 242, 234, 0.05)',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          border: '1px solid rgba(0, 242, 234, 0.2)'
                        }}>
                          {k}: {v}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    )
  }

  // --- DESKTOP RENDER ---
  const chartData: ChartPoint[] = useMemo(
    () =>
      filtered.map(ev => ({
        ...ev,
        timestamp: new Date(ev.date).getTime(),
      })),
    [filtered],
  )

  const [xDomain, setXDomain] = useState<[number, number] | null>(null)

  useEffect(() => {
    setXDomain(null)
  }, [events])

  if (!chartData.length) {
    return <div className="muted" style={{ padding: 16 }}>No events in the selected range.</div>
  }

  const categories = Array.from(new Set(chartData.map(e => e.category || 'other')))

  // Custom Scatter Shape for Desktop
  const renderCustomShape = (props: any) => {
    const { cx, cy } = props
    return (
      <g style={{ cursor: 'pointer' }}>
        <circle cx={cx} cy={cy} r={6} fill="var(--primary)" fillOpacity={0.3} />
        <circle cx={cx} cy={cy} r={3} fill="var(--primary)" stroke="var(--bg-deep)" strokeWidth={1} />
      </g>
    )
  }

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      {/* Grid Background FX */}
      <div style={{
        position: 'absolute',
        inset: 0,
        background: 'radial-gradient(circle at center, rgba(0, 242, 234, 0.03) 0%, transparent 70%)',
        pointerEvents: 'none'
      }} />

      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
          <CartesianGrid 
            strokeDasharray="3 3" 
            vertical={true} 
            horizontal={true} 
            stroke="rgba(255,255,255,0.03)" 
          />
          <XAxis
            type="number"
            dataKey="timestamp"
            domain={xDomain || ['dataMin', 'dataMax']}
            tickFormatter={formatDateShort}
            tick={{ fontSize: 11, fill: '#64748b' }} 
            tickCount={8}
            axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
            tickLine={false}
            dy={10}
          />
          <YAxis
            type="category"
            dataKey="category"
            tick={{ fontSize: 11, fill: '#94a3b8', fontWeight: 500 }}
            allowDuplicatedCategory={false}
            width={100}
            domain={categories as any}
            axisLine={false}
            tickLine={false}
            dx={-10}
          />
          <Tooltip
            cursor={{ strokeDasharray: '3 3', stroke: 'rgba(255,255,255,0.2)' }}
            wrapperStyle={{ zIndex: 1000, outline: 'none' }}
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null
              const p = payload[0].payload as ChartPoint
              return (
                <div
                  style={{
                    padding: '16px',
                    background: 'rgba(9, 14, 26, 0.9)',
                    backdropFilter: 'blur(16px)',
                    border: '1px solid rgba(0, 242, 234, 0.2)',
                    borderRadius: '16px',
                    boxShadow: '0 20px 40px rgba(0,0,0,0.6)',
                    minWidth: 240,
                    color: '#e2e8f0'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                    <span style={{ 
                      fontSize: 10, 
                      color: 'var(--primary)', 
                      textTransform: 'uppercase', 
                      letterSpacing: '0.05em',
                      fontWeight: 700
                    }}>
                      {p.category}
                    </span>
                    <span style={{ fontSize: 11, color: '#64748b' }}>
                      {new Date(p.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                  
                  {p.title && (
                    <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 6, color: '#fff', lineHeight: 1.3 }}>
                      {p.title}
                    </div>
                  )}
                  
                  {p.metrics && Object.keys(p.metrics).length > 0 && (
                    <div style={{ marginTop: 8, paddingTop: 8, borderTop: '1px solid rgba(255,255,255,0.1)', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                      {Object.entries(p.metrics).slice(0, 4).map(([k, v]) => (
                        <div key={k}>
                          <div style={{ fontSize: 10, color: '#64748b', textTransform: 'uppercase' }}>{k}</div>
                          <div style={{ fontSize: 12, color: 'var(--primary)', fontFamily: 'monospace' }}>{v}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )
            }}
          />
          <Scatter
            name="Events"
            data={chartData}
            shape={renderCustomShape}
            onClick={(entry: any) => {
              const p = (entry && entry.payload) as ChartPoint | undefined
              if (!p) return
              const original = filtered.find(e => e.id === p.id)
              if (original && onSelect) onSelect(original)
            }}
          />
        </ScatterChart>
      </ResponsiveContainer>
      
      {xDomain && (
        <button 
          onClick={() => setXDomain(null)}
          style={{
            position: 'absolute',
            top: 20,
            right: 20,
            background: 'rgba(0, 242, 234, 0.1)',
            border: '1px solid rgba(0, 242, 234, 0.3)',
            color: 'var(--primary)',
            fontSize: '11px',
            fontWeight: 600,
            padding: '6px 16px',
            borderRadius: '20px',
            cursor: 'pointer',
            zIndex: 10,
            backdropFilter: 'blur(4px)',
            transition: 'all 0.2s'
          }}
        >
          RESET ZOOM
        </button>
      )}
    </div>
  )
}
