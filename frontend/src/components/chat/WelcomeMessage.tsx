import React, { useEffect, useState } from 'react'
import type { DataCategory, IntelligentPrompt } from '@/lib/api'

interface WelcomeMessageProps {
  username: string
  categories: DataCategory[]
  intelligentPrompts: IntelligentPrompt[]
  summary: {
    total_categories: number
    total_observations: number
    total_documents: number
  }
  onPromptClick: (prompt: string) => void
}

export default function WelcomeMessage({
  username,
  categories,
  intelligentPrompts,
  summary,
  onPromptClick,
}: WelcomeMessageProps) {
  const [showIntro, setShowIntro] = useState(false)

  useEffect(() => {
    setShowIntro(false)
  }, [])

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '40px',
        padding: '20px',
        maxWidth: '100%',
        margin: '0 auto',
        animation: 'fadeInSlide 0.8s ease-out',
      }}
    >
      {/* Intro removed for cleaner look */}

      {/* Hero Greeting */}
      <div style={{ textAlign: 'center' }}>
        <h1
          style={{
            fontSize: '3rem',
            marginBottom: '16px',
            background: 'linear-gradient(135deg, var(--text-main) 0%, var(--text-muted) 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '-0.03em',
            fontFamily: 'Roboto, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif'
          }}
        >
          Hello, {username}
        </h1>
        <p style={{ fontSize: '1.1rem', color: 'var(--text-muted)', maxWidth: '600px', margin: '0 auto', lineHeight: 1.6 }}>
          I am <strong>QuantIA</strong>, your neural health architect. Select a starting point below or ask any question to analyze your biometric streams.
        </p>
      </div>

      {/* Intelligent Prompts Grid */}
      <div>
        <h2 style={{ fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)', marginBottom: '20px', textAlign: 'center', fontFamily: 'Inter, sans-serif' }}>
          Recommended Analysis
        </h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {intelligentPrompts.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => onPromptClick(prompt.prompt)}
              className="card"
              style={{
                padding: '20px',
                textAlign: 'left',
                cursor: 'pointer',
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid var(--border-light)',
                transition: 'all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1)',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
                position: 'relative',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)'
                e.currentTarget.style.borderColor = 'var(--primary)'
                e.currentTarget.style.boxShadow = 'var(--glow-primary)'
                e.currentTarget.style.background = 'rgba(0, 242, 234, 0.05)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.borderColor = 'var(--border-light)'
                e.currentTarget.style.boxShadow = 'none'
                e.currentTarget.style.background = 'rgba(255,255,255,0.02)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                 <span style={{ fontSize: '24px' }}>{prompt.emoji || '✨'}</span>
                 {prompt.priority === 'high' && (
                   <span className="badge" style={{ color: 'var(--primary)', borderColor: 'var(--primary)', background: 'rgba(0, 242, 234, 0.1)' }}>Priority</span>
                 )}
              </div>
              
              <div>
                <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px', lineHeight: 1.4 }}>
                    {prompt.prompt}
                  </div>
                <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                    {prompt.insight}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Footer Stat */}
      <div style={{ textAlign: 'center', marginTop: '20px' }}>
        <div style={{ display: 'inline-flex', gap: '32px', padding: '16px 32px', borderRadius: '100px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-light)' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-main)' }}>{summary.total_categories}</div>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Metrics</div>
          </div>
          <div style={{ width: 1, background: 'var(--border-light)' }}></div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-main)' }}>{summary.total_observations}</div>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Datapoints</div>
          </div>
          <div style={{ width: 1, background: 'var(--border-light)' }}></div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-main)' }}>{summary.total_documents}</div>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Reports</div>
          </div>
        </div>
      </div>
    </div>
  )
}
