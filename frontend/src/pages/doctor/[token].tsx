import React, { useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/router'
import ChartCard from '@/components/ChartCard'
import TimeSeriesChart from '@/components/charts/TimeSeriesChart'
import ChatMessage, { type ChatReference } from '@/components/chat/ChatMessage'
import ChatInputBar from '@/components/chat/ChatInputBar'
import ParticlesBackground from '@/components/ParticlesBackground'

type ObservationDto = {
  code: string
  value: number
  unit: string
  taken_at: string
  source?: string
}

type DoctorLinkPayload = {
  user: number
  latest_observations: ObservationDto[]
}

type ChatTurn = { occurred_at: string; role: 'user' | 'assistant'; text: string }
type ChatMessageT = { role: 'user' | 'assistant'; content: string; references?: ChatReference[] }

export default function DoctorPublicView() {
  const router = useRouter()
  const { token } = router.query
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<DoctorLinkPayload | null>(null)
  const [selectedCode, setSelectedCode] = useState<string | null>(null)
  const [since, setSince] = useState<string>('')
  const [until, setUntil] = useState<string>('')
  const [activeTab, setActiveTab] = useState<'vitals' | 'assistant'>('vitals')
  const [conversation, setConversation] = useState<ChatTurn[]>([])
  const [prompt, setPrompt] = useState('')
  const [convId, setConvId] = useState<string | null>(null)
  const [sending, setSending] = useState(false)
  const [insightRequested, setInsightRequested] = useState(false)
  const messages: ChatMessageT[] = conversation.map(t => ({ role: t.role, content: t.text }))

  useEffect(() => {
    if (!token) return
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const r = await fetch(`/d/${token}`)
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        const json = await r.json()
        setData(json)
        const codes: string[] = Array.from(new Set((json.latest_observations || []).map((o: ObservationDto) => o.code)))
        setSelectedCode((codes[0] as string | undefined) ?? null)
      } catch (e: any) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
      try {
        const rc = await fetch(`/d/chat/${token}`)
        if (rc.ok) {
          const chatJson = await rc.json()
          setConversation(chatJson.conversation || [])
        }
      } catch {
        // ignore
      }
    }
    load()
  }, [token])

  // Auto-request patient insights when switching to chat tab
  useEffect(() => {
    if (activeTab === 'assistant' && !insightRequested && conversation.length === 0 && token) {
      setInsightRequested(true)
      setSending(true)
      const autoQuery = 'Genera un resumen clínico ejecutivo del paciente basándote en los datos disponibles. Incluye alertas recientes y tendencias.'
      
      let id = convId
      if (!id) {
        const newId = `${Date.now()}-${Math.random().toString(36).slice(2)}`
        setConvId(newId)
        id = newId
      }

      fetch(`/d/ask/${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: autoQuery, conversation_id: id })
      })
        .then(async res => {
          if (!res.ok) throw new Error(`HTTP ${res.status}`)
          const json = await res.json()
          const finalText = json.final_text || 'No se pudo generar el resumen.'
          setConversation([
            { occurred_at: new Date().toISOString(), role: 'user', text: autoQuery },
            { occurred_at: new Date().toISOString(), role: 'assistant', text: finalText }
          ])
        })
        .catch(e => {
          setConversation([
            { occurred_at: new Date().toISOString(), role: 'user', text: autoQuery },
            { occurred_at: new Date().toISOString(), role: 'assistant', text: `Error de conexión: ${e.message}` }
          ])
        })
        .finally(() => setSending(false))
    }
  }, [activeTab, insightRequested, conversation.length, token, convId])

  const codes = useMemo(() => Array.from(new Set((data?.latest_observations || []).map(o => o.code))), [data])
  const filtered = useMemo(() => {
    let arr = (data?.latest_observations || [])
    if (selectedCode) arr = arr.filter(o => o.code === selectedCode)
    if (since) arr = arr.filter(o => new Date(o.taken_at) >= new Date(since))
    if (until) arr = arr.filter(o => new Date(o.taken_at) <= new Date(until))
    return arr
  }, [data, selectedCode, since, until])

  const summary = useMemo(() => {
    if (!filtered.length) return null
    const values = filtered.map(o => Number(o.value)).filter(v => !Number.isNaN(v))
    if (!values.length) return null
    const avg = values.reduce((a, b) => a + b, 0) / values.length
    const min = Math.min(...values)
    const max = Math.max(...values)
    const last = filtered[0] // Assuming sorted desc
    
    // Trend calculation
    const mid = Math.floor(values.length / 2) || 1
    const recent = values.slice(0, mid) // "Recent" is first half if sorted desc
    const older = values.slice(mid)
    
    // Correct logic assuming sorted DESC (latest first)
    const avgRecent = recent.reduce((a, b) => a + b, 0) / (recent.length || 1)
    const avgOlder = older.reduce((a, b) => a + b, 0) / (older.length || 1)
    
    const delta = avgRecent - avgOlder
    const pct = avgOlder ? (delta / avgOlder) * 100 : 0
    const direction = delta > 0 ? '↑' : delta < 0 ? '↓' : '→'
    
    return { count: values.length, avg, min, max, last, delta, pct, direction }
  }, [filtered])

  const exportCsv = () => {
    const rows = [
      ['Date', 'Metric', 'Value', 'Unit', 'Source'],
      ...filtered.map(o => [o.taken_at, o.code, String(o.value), o.unit, o.source || ''])
    ]
    const body = rows.map(r => r.map(f => `"${String(f).replace(/"/g, '""')}"`).join(',')).join('\n')
    const blob = new Blob([body], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `patient_${data?.user}_data.csv`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }

  return (
    <div style={{ minHeight: '100vh', position: 'relative', background: 'var(--bg-deep)' }}>
      <ParticlesBackground />
      
      <main className="container" style={{ position: 'relative', zIndex: 10 }}>
        {/* Top Bar */}
        <header style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          padding: '20px 0',
          borderBottom: '1px solid var(--border-light)',
          marginBottom: '32px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{ 
              width: 48, height: 48, borderRadius: '12px', 
              background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: '#000', fontWeight: 'bold', fontSize: '20px'
            }}>
              Rx
            </div>
            <div>
              <h1 style={{ margin: 0, fontSize: '24px', lineHeight: 1.2 }}>QuantIA Professional</h1>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-muted)', fontSize: '13px' }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10b981', boxShadow: '0 0 8px #10b981' }}></span>
                SECURE ACCESS • TOKEN VALID
              </div>
            </div>
          </div>
          
          {data && (
            <div className="hidden-mobile" style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Patient ID</div>
              <div style={{ fontSize: '18px', fontWeight: 600, fontFamily: 'monospace', color: 'var(--primary)' }}>#{data.user.toString().padStart(4, '0')}</div>
            </div>
          )}
        </header>

        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '400px', flexDirection: 'column', gap: 16 }}>
            <div className="status-dot" style={{ width: 16, height: 16, background: 'var(--primary)' }} />
            <div style={{ color: 'var(--text-muted)', letterSpacing: '0.1em' }}>DECRYPTING PATIENT STREAM...</div>
          </div>
        )}

        {error && (
          <div className="card card-pad" style={{ borderColor: 'var(--lifecore-error)', background: 'rgba(239, 68, 68, 0.1)' }}>
            <h3 style={{ color: 'var(--lifecore-error)', marginTop: 0 }}>Access Denied</h3>
            <p>{error}</p>
            <p className="muted">The access token may have expired or been revoked.</p>
          </div>
        )}

        {!!data && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            
            {/* Navigation Tabs */}
            <div style={{ display: 'flex', gap: 4, background: 'rgba(255,255,255,0.03)', padding: 4, borderRadius: '12px', width: 'fit-content' }}>
              <button 
                onClick={() => setActiveTab('vitals')}
                style={{
                  padding: '10px 24px',
                  borderRadius: '8px',
                  background: activeTab === 'vitals' ? 'var(--primary)' : 'transparent',
                  color: activeTab === 'vitals' ? '#000' : 'var(--text-muted)',
                  border: 'none',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                Clinical Vitals
              </button>
              <button 
                onClick={() => setActiveTab('assistant')}
                style={{
                  padding: '10px 24px',
                  borderRadius: '8px',
                  background: activeTab === 'assistant' ? 'var(--primary)' : 'transparent',
                  color: activeTab === 'assistant' ? '#000' : 'var(--text-muted)',
                  border: 'none',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                AI Consultant
              </button>
            </div>

            {/* === VITALS DASHBOARD === */}
            {activeTab === 'vitals' && (
              <div className="animate-in">
                {/* Controls Toolbar */}
                <div className="card" style={{ padding: '16px', marginBottom: '24px', display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center' }}>
                  <div style={{ flex: 1, minWidth: '200px' }}>
                    <label style={{ display: 'block', fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 6 }}>Metric</label>
                    <select 
                      value={selectedCode || ''} 
                      onChange={e => setSelectedCode(e.target.value)}
                      style={{ width: '100%', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border-light)', color: 'white' }}
                    >
                      {codes.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                  </div>
                  
                  <div style={{ display: 'flex', gap: 12 }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 6 }}>From</label>
                      <input type="date" value={since} onChange={e => setSince(e.target.value)} style={{ background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border-light)', color: 'white' }} />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 6 }}>To</label>
                      <input type="date" value={until} onChange={e => setUntil(e.target.value)} style={{ background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border-light)', color: 'white' }} />
                    </div>
                  </div>

                  <button className="btn secondary" onClick={exportCsv} style={{ height: '42px', alignSelf: 'flex-end' }}>
                    Export CSV
                  </button>
                </div>

                {/* Stats Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 16, marginBottom: 24 }}>
                  <div className="card" style={{ padding: '20px', background: 'linear-gradient(160deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01))' }}>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Latest Reading</div>
                    <div style={{ fontSize: '28px', fontWeight: 700, color: 'var(--primary)', marginTop: 4 }}>
                      {summary ? summary.last.value : '—'}
                      <span style={{ fontSize: '14px', color: 'var(--text-muted)', marginLeft: 4 }}>{summary?.last.unit}</span>
                    </div>
                  </div>
                  <div className="card" style={{ padding: '20px' }}>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Average</div>
                    <div style={{ fontSize: '24px', fontWeight: 600, marginTop: 4 }}>{summary ? summary.avg.toFixed(1) : '—'}</div>
                  </div>
                  <div className="card" style={{ padding: '20px' }}>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Min / Max</div>
                    <div style={{ fontSize: '24px', fontWeight: 600, marginTop: 4 }}>
                      {summary ? <>{summary.min} <span style={{ color: 'var(--text-muted)', fontSize: 16 }}>/</span> {summary.max}</> : '—'}
                    </div>
                  </div>
                  <div className="card" style={{ padding: '20px' }}>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Trend</div>
                    <div style={{ fontSize: '24px', fontWeight: 600, marginTop: 4, color: summary?.direction === '↑' ? '#ef4444' : summary?.direction === '↓' ? '#10b981' : '#94a3b8' }}>
                      {summary ? summary.direction : '—'} {summary ? Math.abs(summary.pct).toFixed(1) + '%' : ''}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24 }}>
                  {/* Main Chart */}
                  <div className="card card-pad" style={{ minHeight: '400px', display: 'flex', flexDirection: 'column' }}>
                    <h3 style={{ margin: '0 0 20px 0', fontSize: '16px', fontWeight: 600 }}>Time Series Analysis</h3>
                    <div style={{ flex: 1 }}>
                      <TimeSeriesChart data={filtered.map(o => ({ taken_at: o.taken_at, value: o.value }))} />
                    </div>
                  </div>

                  {/* Recent Records List */}
                  <div className="card" style={{ display: 'flex', flexDirection: 'column', maxHeight: '450px' }}>
                    <div style={{ padding: '16px', borderBottom: '1px solid var(--border-light)' }}>
                      <h3 style={{ margin: 0, fontSize: '16px' }}>Recent Logs</h3>
                    </div>
                    <div style={{ overflowY: 'auto', flex: 1 }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                        <tbody>
                          {(filtered || []).slice(0, 20).map((o, idx) => (
                            <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                              <td style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>
                                {new Date(o.taken_at).toLocaleDateString()}
                              </td>
                              <td style={{ padding: '12px 16px', fontWeight: 600, textAlign: 'right' }}>
                                {o.value} {o.unit}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* === AI ASSISTANT DASHBOARD === */}
            {activeTab === 'assistant' && (
              <div className="animate-in" style={{ display: 'flex', gap: 24, height: 'calc(100vh - 200px)' }}>
                <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                  <div style={{ padding: '20px', borderBottom: '1px solid var(--border-light)', background: 'rgba(255,255,255,0.02)' }}>
                    <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{ width: 10, height: 10, background: 'var(--primary)', borderRadius: '50%', boxShadow: '0 0 10px var(--primary)' }}></span>
                      QuantIA Clinical Assistant
                    </h3>
                    <p className="muted" style={{ margin: '4px 0 0 0', fontSize: '13px' }}>
                      Authorized to analyze patient records and answer clinical queries.
                    </p>
                  </div>
                  
                  <div style={{ flex: 1, overflowY: 'auto', padding: '20px', background: 'rgba(0,0,0,0.2)' }}>
                    {messages.length === 0 ? (
                      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                        Initializing secure conversation...
                      </div>
                    ) : (
                      messages.map((m, i) => (
                        <ChatMessage key={i} role={m.role} content={m.content} references={m.references} />
                      ))
                    )}
                  </div>

                  <div style={{ padding: '20px', borderTop: '1px solid var(--border-light)', background: 'rgba(255,255,255,0.02)' }}>
                    <ChatInputBar
                      value={prompt}
                      onChange={setPrompt}
                      onSend={async () => {
                        if (!token || !prompt.trim()) return
                        const message = prompt.trim()
                        setPrompt('')
                        setSending(true)
                        try {
                          setConversation(prev => [...prev, { occurred_at: new Date().toISOString(), role: 'user', text: message }])
                          let id = convId
                          if (!id) {
                            const newId = `${Date.now()}-${Math.random().toString(36).slice(2)}`
                            setConvId(newId)
                            id = newId
                          }
                          const res = await fetch(`/d/ask/${token}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ query: message, conversation_id: id })
                          })
                          if (!res.ok) throw new Error(`HTTP ${res.status}`)
                          const json = await res.json()
                          const finalText = json.final_text || 'Sin respuesta'
                          setConversation(prev => [...prev, { occurred_at: new Date().toISOString(), role: 'assistant', text: finalText }])
                        } catch (e: any) {
                          setConversation(prev => [...prev, { occurred_at: new Date().toISOString(), role: 'assistant', text: `Error: ${e.message}` }])
                        } finally {
                          setSending(false)
                        }
                      }}
                      disabled={sending}
                      canSend={!!prompt.trim()}
                      loading={sending}
                    />
                  </div>
                </div>
              </div>
            )}

          </div>
        )}
      </main>
    </div>
  )
}
