import React, { useMemo, useState, useEffect } from 'react'

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
          events: evs.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()),
        }))
    }, [filtered])

    if (!filtered.length) {
      return (
        <div className="muted" style={{ padding: 16, textAlign: 'center' }}>
          No events found in this period.
        </div>
      )
    }

    return (
      <div
        style={{
          height: '100%',
          overflowY: 'auto',
          padding: '10px',
          position: 'relative',
          scrollBehavior: 'smooth',
        }}
      >
        <div
          style={{
            position: 'absolute',
            left: '20px',
            top: 0,
            bottom: 0,
            width: '2px',
            background: 'linear-gradient(to bottom, transparent, var(--primary) 10%, var(--primary) 90%, transparent)',
            opacity: 0.3,
            zIndex: 0,
          }}
        />

        {groupedByYear.map(({ year, events: yearEvents }) => (
          <div key={year} style={{ marginBottom: 30, position: 'relative', zIndex: 1 }}>
            <div
              style={{
                position: 'sticky',
                top: 0,
                background: 'var(--bg-dark)',
                padding: '8px 0',
                zIndex: 10,
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                marginBottom: 12,
              }}
            >
              <div
                style={{
                  background: 'rgba(0, 242, 234, 0.1)',
                  color: 'var(--primary)',
                  padding: '4px 12px',
                  borderRadius: '12px',
                  fontSize: '12px',
                  fontWeight: 700,
                  border: '1px solid rgba(0, 242, 234, 0.3)',
                }}
              >
                {year}
              </div>
              <div style={{ height: 1, flex: 1, background: 'var(--border-light)' }} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {yearEvents.map(ev => (
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
                    transition: 'all 0.2s',
                  }}
                >
                  <div
                    style={{
                      position: 'absolute',
                      left: '-25px',
                      top: '18px',
                      width: '10px',
                      height: '10px',
                      borderRadius: '50%',
                      background: 'var(--bg-deep)',
                      border: '2px solid var(--primary)',
                      boxShadow: '0 0 8px var(--primary)',
                    }}
                  />

                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span
                      style={{
                        fontSize: '10px',
                        textTransform: 'uppercase',
                        color: 'var(--text-muted)',
                        letterSpacing: '0.05em',
                      }}
                    >
                      {new Date(ev.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                    </span>
                    <span
                      style={{
                        fontSize: '10px',
                        background: 'rgba(255,255,255,0.1)',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        color: 'var(--text-main)',
                      }}
                    >
                      {ev.category}
                    </span>
                  </div>

                  <div
                    style={{
                      fontSize: '14px',
                      fontWeight: 600,
                      color: 'var(--text-main)',
                      marginBottom: 6,
                    }}
                  >
                    {ev.title || 'Event'}
                  </div>

                  {ev.metrics && Object.keys(ev.metrics).length > 0 && (
                    <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap' }}>
                      {Object.entries(ev.metrics)
                        .slice(0, 2)
                        .map(([k, v]) => (
                          <div
                            key={k}
                            style={{
                              fontSize: '11px',
                              color: 'var(--primary)',
                              background: 'rgba(0, 242, 234, 0.05)',
                              padding: '2px 8px',
                              borderRadius: '4px',
                              border: '1px solid rgba(0, 242, 234, 0.2)',
                            }}
                          >
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

  // --- DESKTOP RENDER: GRID TIMELINE ---
  const desktopEvents = useMemo(
    () =>
      filtered
        .map(ev => ({ ...ev, ts: new Date(ev.date).getTime() }))
        .sort((a, b) => (a.ts as number) - (b.ts as number)),
    [filtered]
  )

  if (!desktopEvents.length) {
    return (
      <div className="muted" style={{ padding: 16 }}>
        No events in the selected range.
      </div>
    )
  }

  const minTs = desktopEvents[0].ts as number
  const maxTs = desktopEvents[desktopEvents.length - 1].ts as number
  const span = Math.max(maxTs - minTs, 1)
  const NUM_COLS = 20
  const bucket = span / NUM_COLS

  const cols = Array.from({ length: NUM_COLS }, (_, i) => {
    const start = minTs + i * bucket
    const end = i === NUM_COLS - 1 ? maxTs + 1 : minTs + (i + 1) * bucket
    return { index: i, from: start, to: end }
  })

  const ROWS: {
    key: string
    label: string
    color: string
    predicate: (ev: TimelineEvent) => boolean
  }[] = [
    {
      key: 'diagnosis',
      label: 'DIAGNOSIS CODES',
      color: '#f97316',
      predicate: ev => ev.category === 'diagnosis' || ev.kind === 'diagnosis',
    },
    {
      key: 'lab',
      label: 'LAB RESULTS',
      color: '#22c55e',
      predicate: ev => ev.category === 'lab',
    },
    {
      key: 'biometric',
      label: 'BIOMETRICS / WEARABLES',
      color: '#38bdf8',
      predicate: ev => ev.category === 'biometric',
    },
    {
      key: 'medication',
      label: 'MEDICATION',
      color: '#0ea5e9',
      predicate: ev => ev.category === 'treatment',
    },
    {
      key: 'notes',
      label: 'TEXT NOTES',
      color: '#a855f7',
      predicate: ev => ev.category === 'consultation' || ev.kind === 'medical_encounter',
    },
    {
      key: 'imaging',
      label: 'IMAGING',
      color: '#e879f9',
      predicate: ev => ev.category === 'imaging',
    },
    {
      key: 'procedures',
      label: 'PROCEDURES',
      color: '#f97373',
      predicate: ev => ev.category === 'procedure',
    },
  ]

  type Bucketed = { col: number; ev: TimelineEvent & { ts: number } }
  const bucketed: Bucketed[] = desktopEvents.map(ev => {
    const col = Math.min(
      NUM_COLS - 1,
      Math.max(0, Math.floor(((ev.ts as number) - minTs) / bucket))
    )
    return { col, ev }
  })

  // Only keep columns that actually contain at least one event, to compress empty space
  const usedColIndexes = new Set(bucketed.map(b => b.col))
  const effectiveCols = cols.filter(c => usedColIndexes.has(c.index))
  const activeCols = effectiveCols.length ? effectiveCols : cols
  const activeNumCols = activeCols.length

  const grid = ROWS.map(row => ({
    ...row,
    cells: activeCols.map(col => {
      const matches = bucketed.filter(b => b.col === col.index && row.predicate(b.ev))
      return {
        has: matches.length > 0,
        event: matches[0]?.ev as TimelineEvent | undefined,
      }
    }),
  }))

  const formatTick = (ts: number) => new Date(ts).getFullYear().toString()

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', padding: '4px 4px' }}>
      {/* Top timeline line with nodes */}
      <div style={{ marginBottom: 8, padding: '0 32px', position: 'relative' }}>
        <div
          style={{
            height: 2,
            background: 'rgba(148, 163, 184, 0.4)',
            borderRadius: 999,
          }}
        />
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          {activeCols.map(col => (
            <div
              key={col.index}
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: 'var(--bg-dark)',
                border: '2px solid rgba(148,163,184,0.8)',
              }}
            />
          ))}
        </div>
      </div>

      {/* Matrix grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: `160px repeat(${activeNumCols}, 1fr)`,
          rowGap: 4,
          columnGap: 2,
          alignItems: 'center',
          paddingLeft: 8,
          paddingRight: 8,
        }}
      >
        {/* Header row (time ticks) */}
        <div />
        {activeCols.map(col => {
          // Only show first and last year label, and keep them inside the grid
          const isFirst = col.index === activeCols[0].index
          const isLast = col.index === activeCols[activeCols.length - 1].index
          const show = isFirst || isLast
          const align = isFirst ? 'left' : isLast ? 'right' : 'center'
          return (
          <div
            key={col.index}
            style={{
                textAlign: align as 'left' | 'center' | 'right',
              fontSize: 10,
              color: 'var(--text-dim)',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
            }}
          >
              {show ? formatTick(col.from) : ''}
          </div>
          )
        })}

        {/* Data rows */}
        {grid.map(row => (
          <React.Fragment key={row.key}>
            <div
              style={{
                fontSize: 10,
                fontWeight: 600,
                color: 'var(--text-muted)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              {row.label}
            </div>
            {row.cells.map((cell, idx) => (
              <div
                key={idx}
                onClick={() => cell.event && onSelect && onSelect(cell.event)}
                style={{
                  width: '100%',
                  height: 10,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: cell.event ? 'pointer' : 'default',
                }}
              >
                <div
                  style={{
                    width: 9,
                    height: 9,
                    borderRadius: 3,
                    background: cell.has ? row.color : 'transparent',
                    opacity: cell.has ? 0.9 : 0.1,
                    boxShadow: cell.has ? `0 0 6px ${row.color}66` : 'none',
                    border: cell.has ? 'none' : '1px solid rgba(148,163,184,0.2)',
                  }}
                />
              </div>
            ))}
          </React.Fragment>
        ))}
      </div>
    </div>
  )
}

