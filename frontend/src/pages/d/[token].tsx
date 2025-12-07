import React, { useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/router'
import { analyze } from '@/lib/api'
import ChatMessage, { type ChatReference } from '@/components/chat/ChatMessage'

export default function DoctorViewPage() {
  const router = useRouter()
  const { token } = router.query
  const [userId, setUserId] = useState<string | null>(null)
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string; references?: ChatReference[] }[]>([])
  const [loading, setLoading] = useState(false)
  const disabled = useMemo(() => loading || !input.trim() || !userId, [loading, input, userId])

  useEffect(() => {
    const load = async () => {
      if (!token) return
      try {
        const res = await fetch(`/d/${token}`)
        if (!res.ok) throw new Error('Invalid token')
        const data = await res.json()
        setUserId(String(data.user))
      } catch (e) {
        // keep null
      }
    }
    load()
  }, [token])

  const onSend = async () => {
    const q = input.trim()
    if (!q || !userId) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: q }])
    try {
      setLoading(true)
      const res = await analyze(q, userId)
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: res.final_text || 'Sin respuesta', references: (res.references || []) as ChatReference[] },
      ])
    } catch (e: any) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${e.message}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <main id="content" className="container">
      <header>
        <h1 style={{ marginBottom: 8 }}>Vista del médico</h1>
        <p className="muted" style={{ marginTop: 0 }}>Solo lectura - Modo médico (con consentimiento)</p>
      </header>
      <section className="card card-pad" aria-label="Conversación" style={{ minHeight: 400, display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 12 }}>
          {messages.length === 0 ? (
            <div className="muted">Escribe una consulta clínica para ver resúmenes y referencias.</div>
          ) : (
            messages.map((m, idx) => <ChatMessage key={idx} role={m.role} content={m.content} references={m.references} />)
          )}
        </div>
        <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
          <input
            type="text"
            placeholder={userId ? 'Consulta del médico...' : 'Cargando usuario...'}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            style={{ flex: 1 }}
            disabled={!userId}
          />
          <button className="btn" disabled={disabled} onClick={onSend}>Enviar</button>
        </div>
      </section>
    </main>
  )
}


