import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import DocumentModal from './DocumentModal'

export type ChatReference = {
  title?: string
  source?: string
  snippet?: string
  score?: number
  content?: string
  id?: string
  href?: string
}

export default function ChatMessage({ role, content, references }: { role: 'user' | 'assistant'; content: string; references?: ChatReference[] }) {
  const isUser = role === 'user'
  const [selectedReference, setSelectedReference] = useState<ChatReference | null>(null)
  
  return (
    <div className="animate-in" style={{ display: 'flex', gap: 16, alignItems: 'flex-start', margin: '20px 0', maxWidth: '100%' }}>
      {/* Avatar */}
      <div style={{
        width: 36,
        height: 36,
        borderRadius: '50%',
        background: isUser 
          ? 'rgba(255,255,255,0.1)' 
          : 'linear-gradient(135deg, var(--primary), var(--secondary))',
        border: isUser
          ? '1px solid rgba(255,255,255,0.2)'
          : 'none',
        color: isUser ? 'var(--text-main)' : '#000',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 700,
        fontSize: '14px',
        boxShadow: !isUser ? 'var(--glow-primary)' : 'none',
        flexShrink: 0
      }}>
        {isUser ? 'U' : 'AI'}
      </div>
      
      {/* Message Bubble */}
      <div style={{ flex: 1, minWidth: 0, overflow: 'hidden' }}>
        <div style={{
          background: isUser
            ? 'transparent'
            : 'rgba(255, 255, 255, 0.03)',
          border: isUser
            ? 'none'
            : '1px solid var(--border-light)',
          borderRadius: 'var(--radius-md)',
          padding: isUser ? '0' : '24px',
          position: 'relative',
          color: 'var(--text-main)'
        }}>
          {/* Label */}
          <div style={{
            fontSize: 11,
            fontWeight: 600,
            marginBottom: 8,
            color: isUser ? 'var(--text-muted)' : 'var(--primary)',
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            opacity: 0.8
          }}>
            {isUser ? 'You' : 'QuantIA Assistant'}
          </div>
          
          {/* Content */}
          <div
            style={{
            whiteSpace: 'pre-wrap',
            lineHeight: 1.6,
            fontSize: '15px',
            color: isUser ? 'var(--text-main)' : 'var(--text-main)',
              letterSpacing: '0.01em',
            }}
          >
            {isUser ? (
              content
            ) : (
              <ReactMarkdown
                components={{
                  strong: ({ children }) => (
                    <strong style={{ fontWeight: 600 }}>{children}</strong>
                  ),
                  p: ({ children }) => <p style={{ margin: '0 0 0.75em 0' }}>{children}</p>,
                  ul: ({ children }) => (
                    <ul style={{ paddingLeft: '1.2em', margin: '0 0 0.75em 0' }}>{children}</ul>
                  ),
                  li: ({ children }) => <li style={{ marginBottom: '0.25em' }}>{children}</li>,
                }}
              >
            {content}
              </ReactMarkdown>
            )}
          </div>
          
          {/* References */}
        {!!references?.length && (
            <div style={{ marginTop: 20 }}>
              <div style={{
                display: 'grid',
                gap: '8px',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))'
              }}>
                {references.map((r, i) => (
                  <div 
                    key={i} 
                    onClick={() => setSelectedReference(r)}
                    style={{
                      background: 'rgba(0,0,0,0.2)',
                      border: '1px solid var(--border-light)',
                      borderRadius: '8px',
                      padding: '12px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      fontSize: '12px'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = 'var(--primary)'
                      e.currentTarget.style.background = 'rgba(0, 242, 234, 0.05)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = 'var(--border-light)'
                      e.currentTarget.style.background = 'rgba(0,0,0,0.2)'
                    }}
                    >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ color: 'var(--primary)', fontWeight: 600 }}>REF {i + 1}</span>
                      {r.score && <span style={{ color: 'var(--text-muted)' }}>{Math.round(r.score * 100)}% Match</span>}
                    </div>
                    <div style={{ fontWeight: 600, marginBottom: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {r.title || 'Medical Document'}
                    </div>
                    <div style={{ color: 'var(--text-muted)', fontStyle: 'italic', height: '36px', overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                      {r.snippet}
                    </div>
                        </div>
              ))}
              </div>
          </div>
        )}
        </div>
      </div>

      {/* Document Modal */}
      {selectedReference && (
        <DocumentModal
          reference={selectedReference}
          onClose={() => setSelectedReference(null)}
        />
      )}
    </div>
  )
}
