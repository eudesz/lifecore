import React, { type ReactNode } from 'react'
import { useRouter } from 'next/router'
import { useAuth } from '@/context/AuthContext'

interface Props {
  children: ReactNode
}

/**
 * Minimal protected route wrapper.
 *
 * For now, if there is no user selected we simply show a gentle
 * message and a link back to the landing page. This keeps the
 * UX simple while avoiding hard redirects that can be confusing
 * during local development.
 */
export default function ProtectedRoute({ children }: Props) {
  const { user } = useAuth()
  const router = useRouter()

  if (!user) {
    return (
      <main
        style={{
          minHeight: '60vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '2rem',
        }}
      >
        <div
          style={{
            maxWidth: 480,
            padding: '2rem',
            borderRadius: '1.5rem',
            background: 'white',
            boxShadow: '0 20px 45px rgba(15,23,42,0.12)',
            textAlign: 'center',
          }}
        >
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.75rem' }}>Sign in to continue</h1>
          <p style={{ color: '#6b7280', marginBottom: '1.5rem' }}>
            Please select a demo user from the landing page before accessing {router.pathname}.
          </p>
          <button
            type="button"
            className="btn-primary"
            onClick={() => router.push('/')}
          >
            Go to landing
          </button>
        </div>
      </main>
    )
  }

  return <>{children}</>
}


