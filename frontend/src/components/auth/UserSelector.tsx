import React from 'react'
import { useRouter } from 'next/router'
import { useAuth } from '@/context/AuthContext'

const DEMO_USERS = [
  { id: 8, name: 'Alexander Synthetic', role: 'Full History (50y)', color: 'var(--primary)' },
  { id: 5, name: 'Demo User 5', role: 'Diabetes & Cardio', color: '#9333ea' },
  { id: 6, name: 'Demo User 6', role: 'Recent Surgery', color: '#10b981' },
]

interface Props {
  isOpen: boolean
  onClose: () => void
}

export default function UserSelector({ isOpen, onClose }: Props) {
  const { user, setUser } = useAuth()
  const router = useRouter()

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose} style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0,0,0,0.8)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100,
      animation: 'fadeInSlide 0.3s ease-out'
    }}>
      <div
        className="card"
        style={{
          width: '100%',
          maxWidth: '480px',
          padding: '32px',
          background: 'rgba(9, 14, 26, 0.9)',
          border: '1px solid var(--border-light)',
          boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
          borderRadius: '24px',
          position: 'relative'
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Decorative Elements */}
        <div style={{ 
          position: 'absolute', 
          top: -1, left: '20%', right: '20%', 
          height: '1px', 
          background: 'linear-gradient(90deg, transparent, var(--primary), transparent)',
          boxShadow: '0 0 10px var(--primary)'
        }} />

        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ 
            width: 48, height: 48, margin: '0 auto 16px', 
            background: 'linear-gradient(135deg, rgba(0,242,234,0.2), rgba(147,51,234,0.2))',
            borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            border: '1px solid var(--border-light)',
            boxShadow: 'var(--glow-primary)'
          }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2">
              <path d="M12 2a5 5 0 1 0 0 10 5 5 0 0 0 0-10z" />
              <path d="M20 21v-2a7 7 0 0 0-14 0v2" />
            </svg>
          </div>
          <h2 style={{ 
            fontSize: '24px', 
            fontWeight: 700, 
            marginBottom: '8px',
            fontFamily: 'Playfair Display, serif',
            color: 'var(--text-main)'
          }}>
            Identity Verification
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
            Select a secure profile to initialize the QuantIA environment.
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {DEMO_USERS.map(u => {
            const active = user?.id === u.id
            return (
              <button
                key={u.id}
                type="button"
                onClick={() => {
                  setUser({ id: u.id, name: u.name })
                  try {
                    const defaultKey = process.env.NEXT_PUBLIC_PLATFORM_API_KEY || 'dev-secret-key'
                    if (typeof window !== 'undefined') {
                      window.localStorage.setItem('PLATFORM_API_KEY', defaultKey)
                    }
                  } catch {}
                  onClose()
                  router.push('/chat').catch(() => {})
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '16px 20px',
                  background: active ? 'rgba(0, 242, 234, 0.1)' : 'rgba(255,255,255,0.03)',
                  border: `1px solid ${active ? 'var(--primary)' : 'var(--border-light)'}`,
                  borderRadius: '16px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  textAlign: 'left',
                  position: 'relative',
                  overflow: 'hidden'
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.background = 'rgba(0, 242, 234, 0.05)'
                  e.currentTarget.style.borderColor = 'var(--primary-dim)'
                }}
                onMouseLeave={e => {
                  if (!active) {
                    e.currentTarget.style.background = 'rgba(255,255,255,0.03)'
                    e.currentTarget.style.borderColor = 'var(--border-light)'
                  }
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ 
                    width: 8, height: 8, borderRadius: '50%', 
                    background: u.color, 
                    boxShadow: `0 0 8px ${u.color}` 
                  }} />
                  <div>
                    <div style={{ color: 'var(--text-main)', fontWeight: 600, fontSize: '15px' }}>{u.name}</div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{u.role}</div>
                  </div>
                </div>
                <div style={{ 
                  fontFamily: 'monospace', 
                  color: 'var(--text-dim)', 
                  fontSize: '12px', 
                  opacity: 0.6 
                }}>
                  ID: {u.id.toString().padStart(4, '0')}
                </div>
              </button>
            )
          })}
        </div>

        <button 
          onClick={onClose}
          style={{
            marginTop: '24px',
            width: '100%',
            padding: '12px',
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            fontSize: '13px',
            cursor: 'pointer',
            textDecoration: 'underline'
          }}
        >
          Cancel Access
        </button>
      </div>
    </div>
  )
}
