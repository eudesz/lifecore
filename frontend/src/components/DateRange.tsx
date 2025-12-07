import { useState, useEffect } from 'react'

type Props = {
  since?: string
  until?: string
  onApply: (range: { since?: string; until?: string }) => void
}

export default function DateRange({ since, until, onApply }: Props) {
  const [s, setS] = useState(since || '')
  const [u, setU] = useState(until || '')

  useEffect(() => { setS(since || '') }, [since])
  useEffect(() => { setU(until || '') }, [until])

  return (
    <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 12 }}>
      <div>
        <label>Desde</label>
        <input type="date" value={s} onChange={e => setS(e.target.value)} style={{ display: 'block', padding: 6 }} />
      </div>
      <div>
        <label>Hasta</label>
        <input type="date" value={u} onChange={e => setU(e.target.value)} style={{ display: 'block', padding: 6 }} />
      </div>
      <button onClick={() => onApply({ since: s ? new Date(s).toISOString() : undefined, until: u ? new Date(u).toISOString() : undefined })} style={{ padding: '6px 10px', marginTop: 18 }}>Aplicar</button>
    </div>
  )
}
