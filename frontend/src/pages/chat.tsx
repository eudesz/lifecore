import React, { useMemo, useState, useEffect, useRef } from 'react'
import RequireApiKey from '@/components/RequireApiKey'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import { useAuth } from '@/context/AuthContext'
import { analyze, getIntelligentPrompts, type IntelligentPromptsResponse, fetchTimelineAdvanced, fetchConditionsList, fetchDocumentsList } from '@/lib/api'
import ChatMessage, { type ChatReference } from '@/components/chat/ChatMessage'
import ChatInputBar from '@/components/chat/ChatInputBar'
import ParticlesBackground from '@/components/ParticlesBackground'
import WelcomeMessage from '@/components/chat/WelcomeMessage'
import ShareWithDoctorModal from '@/components/ShareWithDoctorModal'
import TimelineChart, { type TimelineEvent } from '@/components/timeline/TimelineChart'
import DocumentModal from '@/components/chat/DocumentModal'
import KnowledgeGraph from '@/components/KnowledgeGraph'

export type ChatMessageT = {
  role: 'user' | 'assistant'
  content: string
  references?: ChatReference[]
}

export default function ChatPage() {
  const { user } = useAuth()
  const userId = user?.id?.toString() || '1'
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<ChatMessageT[]>([])
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [intelligentData, setIntelligentData] = useState<IntelligentPromptsResponse | null>(null)
  const [loadingPrompts, setLoadingPrompts] = useState(true)
  const [shareOpen, setShareOpen] = useState(false)
  
  // Timeline scope
  const [events, setEvents] = useState<TimelineEvent[]>([])
  const [tLoading, setTLoading] = useState(true)
  const [tError, setTError] = useState<string | null>(null)
  const [range, setRange] = useState<{ from?: string; to?: string }>({})
  
  // Year/month range bars
  const THIS_YEAR = new Date().getFullYear()
  const [yearFrom, setYearFrom] = useState<number>(1975)
  const [yearTo, setYearTo] = useState<number>(THIS_YEAR)
  const [monthFrom, setMonthFrom] = useState<number>(1)
  const [monthTo, setMonthTo] = useState<number>(12)
  const [categories, setCategories] = useState<string[]>([])
  const [conditions, setConditions] = useState<string[]>([])
  const [availableConditions, setAvailableConditions] = useState<Array<{ slug: string; name: string; color: string; count: number }>>([])
  const [selectedEvent, setSelectedEvent] = useState<TimelineEvent | null>(null)
  const [docModalRef, setDocModalRef] = useState<ChatReference | null>(null)
  
  // View state
  const [activeTab, setActiveTab] = useState<'timeline' | 'chat' | 'graph'>('chat') // (kept for potential future mobile switch)
  const [activeView, setActiveView] = useState<'timeline' | 'graph'>('timeline') // Desktop Left Panel
  const [filtersCollapsed, setFiltersCollapsed] = useState(false)
  const [analysisFullscreen, setAnalysisFullscreen] = useState(false)
  
  const [contextMode, setContextMode] = useState<'general' | 'filter'>(() => {
    if (typeof window !== 'undefined') {
      const v = localStorage.getItem('quantia_context_mode')
      if (v === 'filter' || v === 'general') return v
    }
    return 'general'
  })

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('quantia_context_mode', contextMode)
    }
  }, [contextMode])

  const lastContextAnnouncedRef = useRef<string | null>(null)
  const disabled = useMemo(() => loading, [loading])
  const canSend = useMemo(() => !loading && input.trim().length > 0, [loading, input])

  // Load intelligent prompts
  useEffect(() => {
    if (!userId) return
    const loadPrompts = async () => {
      try {
        setLoadingPrompts(true)
        const data = await getIntelligentPrompts(userId)
        setIntelligentData(data)
      } catch (error) {
        console.error('Error loading intelligent prompts:', error)
      } finally {
        setLoadingPrompts(false)
      }
    }
    loadPrompts()
  }, [userId])

  // Load timeline
  useEffect(() => {
    if (!userId) return
    const pad = (n: number) => String(n).padStart(2, '0')
    const lastDayOf = (y: number, m: number) => new Date(y, m, 0).getDate()
    const df = `${yearFrom}-${pad(monthFrom)}-01`
    const dt = `${yearTo}-${pad(monthTo)}-${pad(lastDayOf(yearTo, monthTo))}`
    setRange({ from: df, to: dt })
    
    const load = async () => {
      try {
        setTLoading(true)
        setTError(null)
        const data = await fetchTimelineAdvanced({
          user_id: userId,
          date_from: df,
          date_to: dt,
          categories,
          conditions,
        })
        setEvents((data.events || []) as TimelineEvent[])
      } catch (e: any) {
        setTError(e.message)
      } finally {
        setTLoading(false)
      }
    }
    load()
  }, [userId, yearFrom, yearTo, monthFrom, monthTo, categories, conditions])

  // Announce context changes
  useEffect(() => {
    if (contextMode !== 'filter') return
    const pad = (n: number) => String(n).padStart(2, '0')
    const rangeStr = `${yearFrom}-${pad(monthFrom)} to ${yearTo}-${pad(monthTo)}`
    const catsStr = categories.length ? categories.join(', ') : 'all'
    const condNames = conditions.length
      ? conditions.map(slug => availableConditions.find(c => c.slug === slug)?.name || slug)
      : []
    const condsStr = conditions.length ? condNames.join(', ') : 'all'
    const text = `Context filtered: Years ${rangeStr} | Categories: ${catsStr} | Conditions: ${condsStr}.`
    
    if (text !== lastContextAnnouncedRef.current) {
      setMessages(prev => [...prev, { role: 'assistant', content: text }])
      lastContextAnnouncedRef.current = text
    }
  }, [contextMode, yearFrom, yearTo, monthFrom, monthTo, categories, conditions, availableConditions])

  useEffect(() => {
    if (!userId) return
    const loadConds = async () => {
      try {
        const data = await fetchConditionsList(userId)
        setAvailableConditions(data.conditions || [])
      } catch {}
    }
    loadConds()
  }, [userId])

  const handlePromptClick = (prompt: string) => {
    setInput(prompt)
  }

  const onSend = async () => {
    const q = input.trim()
    if (!q) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: q }])
    
    try {
      setLoading(true)
      if (!conversationId) {
        setConversationId(`${Date.now()}-${Math.random().toString(36).slice(2)}`)
        }
      
      const filters = contextMode === 'filter'
        ? {
            categories: categories.length ? categories : undefined,
            conditions: conditions.length ? conditions : undefined,
            date_from: range.from,
            date_to: range.to,
          }
        : undefined
        
      const res = await analyze(q, userId, {
        conversation_id: conversationId || undefined,
        ...(filters ? { context_filters: filters } : {}),
      })
      
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: res.final_text || 'Sin respuesta',
          references: (res.references || []) as ChatReference[],
        },
      ])
    } catch (e: any) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${e.message}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <ProtectedRoute>
    <RequireApiKey>
      <ParticlesBackground />
        
        <main
          id="content"
          className="container"
          style={{
            height: '100vh',
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          {/* Header */}
        <header style={{ 
            padding: '24px 0',
            borderBottom: '1px solid var(--border-light)',
            marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
            gap: '16px'
        }}>
          <div>
              <h1 className="text-gradient" style={{ margin: 0, lineHeight: 1, fontSize: '28px', fontFamily: 'Roboto, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif' }}>
              QuantIA
            </h1>
              <p className="hidden-mobile" style={{ margin: '4px 0 0 0', color: 'var(--text-muted)', fontSize: '14px', letterSpacing: '0.02em' }}>
                INTELLIGENT HEALTH ORCHESTRATOR
            </p>
          </div>
          
            <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
              <button className="btn secondary" onClick={() => setShareOpen(true)} style={{ padding: '8px 20px', fontSize: '13px' }}>
                Share Access
              </button>
            </div>
          </header>

          {/* Main Layout */}
          <section style={{ display: 'flex', gap: 24, alignItems: 'stretch', flex: 1, minHeight: 0, height: '100%', position: 'relative' }}>
            
            {/* Left Column: Timeline & Graph */}
            <div 
              className={`card ${activeTab === 'chat' ? 'hidden-mobile' : ''}`} 
              style={{ 
                flex: analysisFullscreen ? '1 1 100%' : '1 1 50%', 
                display: 'flex', 
                flexDirection: 'column',
                padding: '24px',
                minWidth: 0
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                  <h2 style={{ margin: 0, fontSize: '20px' }}>Analysis View</h2>
                  <div className="hidden-mobile" style={{ display: 'flex', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', padding: 2 }}>
                    <button 
                      onClick={() => setActiveView('timeline')}
                      style={{
                        background: activeView === 'timeline' ? 'var(--primary)' : 'transparent',
                        color: activeView === 'timeline' ? '#000' : 'var(--text-muted)',
                        border: 'none', borderRadius: '6px', padding: '4px 12px', fontSize: '12px', fontWeight: 600, cursor: 'pointer'
                      }}
                    >
                      Timeline
                    </button>
                    <button 
                      onClick={() => setActiveView('graph')}
                      style={{
                        background: activeView === 'graph' ? 'var(--primary)' : 'transparent',
                        color: activeView === 'graph' ? '#000' : 'var(--text-muted)',
                        border: 'none', borderRadius: '6px', padding: '4px 12px', fontSize: '12px', fontWeight: 600, cursor: 'pointer'
                      }}
                    >
                      Graph
                    </button>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <button
                    type="button"
                    onClick={() => setFiltersCollapsed(f => !f)}
                    className="btn secondary"
                    style={{ padding: '4px 10px', fontSize: 11 }}
                  >
                    {filtersCollapsed ? 'Show Filters' : 'Hide Filters'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setAnalysisFullscreen(f => !f)}
                    className="btn secondary hidden-mobile"
                    style={{ padding: '4px 10px', fontSize: 11 }}
                  >
                    {analysisFullscreen ? 'Show Assistant' : 'Full Width'}
                  </button>
                <div className="badge">LIVE DATA</div>
                </div>
              </div>

              {/* Filters Container */}
              {!filtersCollapsed && (
              <div style={{ 
                background: 'rgba(255,255,255,0.02)', 
                borderRadius: '16px', 
                padding: '20px',
                marginBottom: '20px',
                border: '1px solid var(--border-light)'
              }}>
                {/* Range Slider */}
                <div style={{ marginBottom: 20 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                    <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Time Horizon</label>
                    <span style={{ fontSize: '13px', fontFamily: 'monospace', color: 'var(--primary)' }}>
                      {yearFrom} — {yearTo}
                    </span>
                  </div>
                  
                  <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                  <input
                    type="range"
                      min={1975}
                    max={THIS_YEAR}
                    value={yearFrom}
                      onChange={e => setYearFrom(Math.min(Number(e.target.value), yearTo))}
                      style={{ flex: 1, accentColor: 'var(--primary)', background: 'rgba(255,255,255,0.1)', height: '4px' }}
                  />
                  <input
                    type="range"
                      min={1975}
                    max={THIS_YEAR}
                    value={yearTo}
                      onChange={e => setYearTo(Math.max(Number(e.target.value), yearFrom))}
                      style={{ flex: 1, accentColor: 'var(--primary)', background: 'rgba(255,255,255,0.1)', height: '4px' }}
                  />
                </div>

                  {/* Quick Filters */}
                  <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                    {[
                      { label: '3Y', val: 3 },
                      { label: '5Y', val: 5 },
                      { label: '10Y', val: 10 }
                    ].map(opt => (
                  <button
                        key={opt.label}
                    className="btn secondary"
                    onClick={() => {
                      setYearTo(THIS_YEAR)
                          setYearFrom(Math.max(2000, THIS_YEAR - opt.val))
                    }}
                        style={{ padding: '4px 12px', fontSize: '11px', borderRadius: '8px' }}
                  >
                        {opt.label}
                  </button>
                    ))}
                  <button
                    className="btn secondary"
                    onClick={() => { setYearFrom(1975); setYearTo(THIS_YEAR) }}
                      style={{ padding: '4px 12px', fontSize: '11px', borderRadius: '8px', marginLeft: 'auto' }}
                  >
                      RESET
                  </button>
                </div>
                </div>

                {/* Categories (Data Sources) */}
                <div style={{ marginBottom: 16 }}>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase' }}>Data Sources</label>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {['diagnosis', 'treatment', 'lab', 'consultation', 'biometric', 'imaging'].map(key => {
                    const active = categories.includes(key)
                    return (
                      <button
                        key={key}
                        onClick={() => setCategories(prev => active ? prev.filter(x => x !== key) : [...prev, key])}
                          style={{
                            padding: '6px 14px',
                            fontSize: '12px',
                            borderRadius: '20px',
                            background: active ? 'rgba(0, 242, 234, 0.1)' : 'transparent',
                            border: `1px solid ${active ? 'var(--primary)' : 'var(--border-light)'}`,
                            color: active ? 'var(--primary)' : 'var(--text-muted)',
                            cursor: 'pointer',
                            transition: 'all 0.2s'
                          }}
                      >
                          {key.charAt(0).toUpperCase() + key.slice(1)}
                      </button>
                    )
                  })}
                  </div>
                </div>

                {/* Conditions */}
              <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase' }}>Conditions</label>
                  <div style={{ 
                    display: 'flex', 
                    gap: 8, 
                    overflowX: 'auto', 
                    paddingBottom: 4,
                    scrollbarWidth: 'none'
                  }}>
                  {availableConditions.map(c => {
                      const active = conditions.includes(c.slug)
                    return (
                      <button
                          key={c.slug}
                          onClick={() => setConditions(prev => active ? prev.filter(x => x !== c.slug) : [...prev, c.slug])}
                          style={{
                            padding: '6px 14px',
                            fontSize: '12px',
                            borderRadius: '20px',
                            background: active ? `rgba(from ${c.color} r g b / 0.15)` : 'transparent',
                            border: `1px solid ${active ? c.color : 'var(--border-light)'}`,
                            color: active ? c.color : 'var(--text-muted)',
                            whiteSpace: 'nowrap',
                            cursor: 'pointer'
                          }}
                      >
                        {c.name}
                      </button>
                    )
                  })}
                  </div>
                </div>
              </div>
              )}

              {/* Chart Area (Toggle between Timeline and Graph) */}
              <div style={{ flex: 1, minHeight: 0, position: 'relative' }}>
                {(activeTab === 'timeline' || (activeTab !== 'graph' && activeView === 'timeline')) && (
                  tLoading ? (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
                      Loading data streams...
            </div>
                  ) : tError ? (
                    <div style={{ color: '#ef4444' }}>Error: {tError}</div>
                  ) : (
                  <TimelineChart events={events} onSelect={setSelectedEvent} groupByCondition={true} selectedConditions={conditions} />
                  )
                )}

                {(activeTab === 'graph' || (activeTab !== 'timeline' && activeView === 'graph')) && (
                  <KnowledgeGraph />
              )}
            </div>

              {/* Event Detail Overlay */}
            {selectedEvent && activeView === 'timeline' && (
                <div style={{
                  position: 'absolute',
                  bottom: 24,
                  left: 24,
                  right: 24,
                  background: 'rgba(9, 14, 26, 0.95)',
                  backdropFilter: 'blur(20px)',
                  border: '1px solid var(--border-light)',
                  borderRadius: '16px',
                  padding: '20px',
                  boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
                  zIndex: 10
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                    <div>
                      <h3 style={{ margin: 0, fontSize: '18px', color: 'var(--primary)' }}>{selectedEvent.title}</h3>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: 4 }}>
                        {new Date(selectedEvent.date).toLocaleDateString(undefined, { dateStyle: 'full' })}
                </div>
                </div>
                    <button 
                      onClick={() => setSelectedEvent(null)}
                      style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '20px' }}
                    >
                      ×
                    </button>
                  </div>
                  
                  {selectedEvent.description && (
                    <p style={{ fontSize: '14px', lineHeight: 1.6, color: 'var(--text-main)', margin: '0 0 12px 0' }}>
                      {selectedEvent.description}
                    </p>
                )}

                  {selectedEvent.metrics && Object.keys(selectedEvent.metrics || {}).length > 0 && (
                    <div
                      style={{
                        marginBottom: 12,
                        padding: '10px 12px',
                        borderRadius: 12,
                        background: 'rgba(15,23,42,0.9)',
                        border: '1px solid var(--border-light)',
                        maxHeight: 160,
                        overflowY: 'auto',
                      }}
                    >
                      <div
                        style={{
                          fontSize: 11,
                          textTransform: 'uppercase',
                          letterSpacing: '0.08em',
                          color: 'var(--text-muted)',
                          marginBottom: 6,
                        }}
                      >
                        Measurements
                      </div>
                      <div
                        style={{
                          display: 'grid',
                          gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                          gap: 6,
                          fontSize: 12,
                        }}
                      >
                        {Object.entries(selectedEvent.metrics || {}).map(([k, v]) => (
                          <div
                            key={k}
                            style={{
                              padding: '4px 8px',
                              borderRadius: 8,
                              background: 'rgba(15,23,42,0.9)',
                              border: '1px solid rgba(148,163,184,0.4)',
                            }}
                          >
                            <div style={{ color: 'var(--text-muted)', fontSize: 11, marginBottom: 2 }}>
                              {k}
                            </div>
                            <div style={{ color: 'var(--text-main)', fontWeight: 500 }}>{String(v)}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: 12 }}>
                  <button
                       className="btn primary" 
                       style={{ padding: '8px 20px', fontSize: '12px', opacity: (String(selectedEvent.id).startsWith('doc_') || selectedEvent.document_id) ? 1 : 0.5, cursor: (String(selectedEvent.id).startsWith('doc_') || selectedEvent.document_id) ? 'pointer' : 'not-allowed' }}
                       disabled={!(String(selectedEvent.id).startsWith('doc_') || selectedEvent.document_id)}
                       onClick={() => {
                         let docId: string | null = null;
                         if (String(selectedEvent.id).startsWith('doc_')) {
                           docId = String(selectedEvent.id).replace('doc_', '');
                         } else if (selectedEvent.document_id) {
                           docId = String(selectedEvent.document_id);
                         }
                         
                         if (docId) {
                          setDocModalRef({
                             title: selectedEvent.title || 'Document',
                             source: 'Timeline',
                             snippet: selectedEvent.description || '',
                             docId: parseInt(docId)
                           });
                         }
                       }}
                     >
                       View Details
                  </button>
                </div>
              </div>
            )}
          </div>

            {/* Right Column: AI Assistant */}
            <div 
              className={`card ${activeTab !== 'chat' ? 'hidden-mobile' : ''}`} 
              style={{ 
                flex: analysisFullscreen ? '0 0 0%' : '1 1 50%', 
                display: analysisFullscreen ? 'none' : 'flex', 
                flexDirection: 'column',
                padding: '24px',
                minWidth: 0
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
                <h2 style={{ margin: 0, fontSize: '20px' }}>Neural Assistant</h2>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button
                    onClick={() => setContextMode('general')}
                    style={{ 
                      padding: '6px 12px', 
                      borderRadius: '8px', 
                      background: contextMode === 'general' ? 'rgba(255,255,255,0.1)' : 'transparent',
                      border: 'none',
                      color: contextMode === 'general' ? 'white' : 'var(--text-muted)',
                      fontSize: '12px',
                      cursor: 'pointer'
                    }}
                  >
                    General
                  </button>
                  <button
                    onClick={() => setContextMode('filter')}
                    style={{ 
                      padding: '6px 12px', 
                      borderRadius: '8px', 
                      background: contextMode === 'filter' ? 'rgba(0, 242, 234, 0.1)' : 'transparent',
                      border: 'none',
                      color: contextMode === 'filter' ? 'var(--primary)' : 'var(--text-muted)',
                      fontSize: '12px',
                      cursor: 'pointer'
                    }}
                  >
                     Context Aware
                  </button>
                </div>
              </div>

              {/* Patient safety disclaimer */}
              <p style={{ margin: '0 0 16px 0', fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                QuantIA es una herramienta informativa basada en tus datos de salud. No sustituye una consulta médica
                presencial, no establece diagnósticos y no indica cambios concretos de tratamiento. Usa estas respuestas
                para entender mejor tu historia clínica y prepara preguntas para tu equipo médico.
              </p>

              {/* Chat Area */}
          <div style={{ 
            flex: 1, 
                overflowY: 'auto', 
                paddingRight: '8px', 
                marginBottom: '16px',
            display: 'flex', 
                flexDirection: 'column'
          }}>
            {messages.length === 0 ? (
              loadingPrompts ? (
                    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', opacity: 0.7 }}>
                      <div className="status-dot" style={{ width: 12, height: 12, background: 'var(--primary)', boxShadow: '0 0 20px var(--primary)' }} />
                      <p style={{ marginTop: 20, fontSize: '14px', letterSpacing: '0.05em' }}>INITIALIZING NEURAL LINK...</p>
                </div>
              ) : intelligentData ? (
                <WelcomeMessage
                  username={intelligentData.username}
                  categories={intelligentData.categories}
                  intelligentPrompts={intelligentData.intelligent_prompts}
                  summary={intelligentData.summary}
                  onPromptClick={handlePromptClick}
                />
              ) : (
                    <div style={{ textAlign: 'center', marginTop: 'auto', marginBottom: 'auto' }}>
                      <h3 style={{ fontFamily: 'Playfair Display', fontSize: '24px', marginBottom: '8px' }}>QuantIA System Ready</h3>
                      <p style={{ color: 'var(--text-muted)' }}>Connect with your health data stream.</p>
                </div>
              )
              ) : (
                messages.map((m, idx) => (
                    <div key={idx} style={{ marginBottom: 24 }}>
                    <ChatMessage role={m.role} content={m.content} references={m.references} />
                  </div>
                ))
              )}
            
            {loading && (
                   <div style={{ display: 'flex', gap: 16, marginTop: 12, paddingLeft: 12 }}>
                <div style={{
                       width: 32, height: 32, borderRadius: '50%', 
                       background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
                       display: 'flex', alignItems: 'center', justifyContent: 'center',
                       boxShadow: 'var(--glow-primary)'
                     }}>
                       <span style={{ fontSize: '14px' }}>AI</span>
                </div>
                     <div className="typing-indicator" style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '12px', padding: '12px 20px' }}>
                       <div className="typing-dot" style={{ background: 'var(--primary)' }}></div>
                       <div className="typing-dot" style={{ background: 'var(--primary)', animationDelay: '0.2s' }}></div>
                       <div className="typing-dot" style={{ background: 'var(--primary)', animationDelay: '0.4s' }}></div>
            </div>
                      </div>
                    )}
          </div>
          
              {/* Input Area */}
              <div style={{ position: 'relative' }}>
            <ChatInputBar 
              value={input} 
              onChange={setInput} 
              onSend={onSend} 
              disabled={disabled}
              canSend={canSend}
              loading={loading} 
            />
          </div>
          </div>

          {/* Floating assistant tab when hidden in fullscreen analysis (desktop only) */}
          {analysisFullscreen && (
            <button
              type="button"
              onClick={() => setAnalysisFullscreen(false)}
              className="hidden-mobile"
              style={{
                position: 'absolute',
                right: -6,
                top: '50%',
                transform: 'translateY(-50%)',
                writingMode: 'vertical-rl',
                padding: '8px 6px',
                borderRadius: '12px 0 0 12px',
                border: '1px solid var(--border-light)',
                background: 'rgba(15,23,42,0.9)',
                color: 'var(--text-main)',
                fontSize: 11,
                cursor: 'pointer',
                zIndex: 20,
              }}
            >
              Assistant
            </button>
          )}
        </section>
      </main>
        
      <ShareWithDoctorModal isOpen={shareOpen} onClose={() => setShareOpen(false)} userId={userId} />
      <DocumentModal reference={docModalRef} onClose={() => setDocModalRef(null)} />
    </RequireApiKey>
  </ProtectedRoute>
  )
}
