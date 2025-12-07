import React, { useState } from 'react'

export default function ApiKeyInput({ onSaved }: { onSaved?: () => void }) {
  const [value, setValue] = useState('')
  const save = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('PLATFORM_API_KEY', value)
      onSaved && onSaved()
    }
  }
  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 8 }}>
      <input value={value} onChange={e => setValue(e.target.value)} placeholder="API key" style={{ padding: 8, flex: 1 }} />
      <button onClick={save} style={{ padding: '8px 12px' }}>Guardar</button>
    </div>
  )
}
