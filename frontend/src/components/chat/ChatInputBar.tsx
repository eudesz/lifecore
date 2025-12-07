import React, { useCallback } from 'react'

export default function ChatInputBar({ value, onChange, onSend, disabled, canSend, loading, suggestions }: {
  value: string
  onChange: (v: string) => void
  onSend: () => void
  disabled?: boolean
  canSend?: boolean
  loading?: boolean
  suggestions?: string[]
}) {
  const onKey = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      if (!disabled && canSend !== false) onSend()
    }
  }, [onSend, disabled, canSend])

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <input
        type="text"
            id="chat-input"
            value={value}
            onChange={e => onChange(e.target.value)}
            onKeyDown={onKey}
        placeholder="Escribe tu mensaje..."
        disabled={disabled}
        autoComplete="off"
        autoCorrect="off"
        autoCapitalize="off"
        spellCheck="false"
        style={{
          width: '100%',
          height: '56px',
          padding: '0 60px 0 20px',
          fontSize: '15px',
          border: '2px solid rgba(0, 212, 255, 0.3)',
          borderRadius: '28px',
          background: 'rgba(26, 31, 58, 0.6)',
          color: 'var(--text)',
          transition: 'all 0.3s ease',
          fontFamily: 'inherit',
          outline: 'none',
          boxSizing: 'border-box'
        }}
        onFocus={(e) => {
          e.target.style.borderColor = 'var(--lifecore-cyan)'
          e.target.style.boxShadow = 'var(--glow-cyan), inset 0 0 20px rgba(0, 212, 255, 0.1)'
          e.target.style.background = 'rgba(26, 31, 58, 0.8)'
        }}
        onBlur={(e) => {
          e.target.style.borderColor = 'rgba(0, 212, 255, 0.3)'
          e.target.style.boxShadow = 'none'
          e.target.style.background = 'rgba(26, 31, 58, 0.6)'
        }}
      />
      
      {/* Send Button */}
      <button 
        onClick={onSend} 
        disabled={!!disabled}
        aria-label="Enviar mensaje"
        style={{
          position: 'absolute',
          right: '8px',
          top: '8px',
          width: '40px',
          height: '40px',
          borderRadius: '50%',
          border: 'none',
          background: disabled 
            ? 'rgba(100, 116, 139, 0.3)'
            : 'linear-gradient(135deg, var(--lifecore-cyan), var(--lifecore-purple))',
          color: 'white',
          fontSize: '20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: disabled ? 'not-allowed' : 'pointer',
          transition: 'all 0.3s ease',
          boxShadow: disabled ? 'none' : 'var(--glow-cyan)',
          opacity: disabled ? 0.5 : 1
        }}
        onMouseEnter={(e) => {
          if (!disabled) {
            e.currentTarget.style.transform = 'scale(1.1)'
            e.currentTarget.style.boxShadow = '0 0 30px rgba(0, 212, 255, 0.8)'
          }
        }}
        onMouseLeave={(e) => {
          if (!disabled) {
            e.currentTarget.style.transform = 'scale(1)'
            e.currentTarget.style.boxShadow = 'var(--glow-cyan)'
          }
        }}
      >
        {loading ? (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true" style={{ animation: 'spin 1s linear infinite' }}>
            <circle cx="12" cy="12" r="9" stroke="rgba(255,255,255,0.6)" strokeWidth="3" />
            <path d="M21 12a9 9 0 0 1-9 9" stroke="white" strokeWidth="3" />
          </svg>
        ) : (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M2 12l19-9-6 18-3-7-10-2z"></path>
          </svg>
        )}
        </button>
      
      {!!suggestions?.length && (
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 12 }}>
          {suggestions.map((s, i) => (
            <button key={i} className="btn secondary" onClick={() => onChange(s)}>{s}</button>
          ))}
        </div>
      )}
    </div>
  )
}





