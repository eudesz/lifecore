import React, { useEffect, useState } from 'react'
import ApiKeyInput from './ApiKeyInput'

function getApiKey(): string | null {
  if (typeof window === 'undefined') return process.env.NEXT_PUBLIC_PLATFORM_API_KEY || null
  return process.env.NEXT_PUBLIC_PLATFORM_API_KEY || localStorage.getItem('PLATFORM_API_KEY')
}

export default function RequireApiKey({ children }: { children: React.ReactNode }) {
  const [hasKey, setHasKey] = useState<boolean>(false)

  useEffect(() => {
    setHasKey(!!getApiKey())
  }, [])

  if (!hasKey) {
    return (
      <div style={{ maxWidth: 640, margin: '0 auto', padding: 24 }}>
        <h1>Configuración requerida</h1>
        <p>Este módulo requiere una API key válida. Puedes establecerla aquí para la sesión actual.</p>
        <ApiKeyInput onSaved={() => setHasKey(true)} />
      </div>
    )
  }
  return <>{children}</>
}
