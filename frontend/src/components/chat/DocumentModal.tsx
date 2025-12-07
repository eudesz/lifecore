import React from 'react'
import { ChatReference } from './ChatMessage'

interface DocumentModalProps {
  reference: ChatReference | null
  onClose: () => void
}

export default function DocumentModal({ reference, onClose }: DocumentModalProps) {
  if (!reference) return null

  return (
    <>
      {/* Backdrop con blur */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          zIndex: 9998,
          animation: 'fadeIn 0.2s ease-out'
        }}
      />

      {/* Modal */}
      <div
        style={{
          position: 'fixed',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '90%',
          maxWidth: '900px',
          maxHeight: '85vh',
          backgroundColor: 'var(--card-bg)',
          border: '1px solid rgba(147, 51, 234, 0.3)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5), var(--glow-purple)',
          zIndex: 9999,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          animation: 'modalSlideIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)'
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: 'var(--space-lg)',
            borderBottom: '1px solid rgba(147, 51, 234, 0.2)',
            background: 'linear-gradient(135deg, rgba(147, 51, 234, 0.1), rgba(0, 212, 255, 0.05))',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexShrink: 0
          }}
        >
          <div style={{ flex: 1, minWidth: 0 }}>
            <h2
              style={{
                margin: 0,
                fontSize: '1.5rem',
                fontWeight: 700,
                color: 'var(--text-bright)',
                textShadow: 'var(--glow-purple)',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}
            >
              {reference.title || 'Medical document'}
            </h2>
            {reference.source && (
              <div
                style={{
                  marginTop: '4px',
                  fontSize: '0.875rem',
                  color: 'var(--text-dim)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <span
                  style={{
                    display: 'inline-block',
                    padding: '2px 8px',
                    background: 'rgba(147, 51, 234, 0.2)',
                    border: '1px solid rgba(147, 51, 234, 0.4)',
                    borderRadius: '4px',
                    fontSize: '0.75rem',
                    color: 'var(--text-bright)'
                  }}
                >
                  {reference.source}
                </span>
                {reference.score !== undefined && (
                  <span style={{ color: 'var(--text-dim)' }}>
                    Relevance: {(reference.score * 100).toFixed(0)}%
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Close button */}
          <button
            onClick={onClose}
            style={{
              marginLeft: '16px',
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              background: 'rgba(255, 255, 255, 0.05)',
              color: 'var(--text-bright)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.5rem',
              transition: 'all 0.2s ease',
              flexShrink: 0
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)'
              e.currentTarget.style.transform = 'rotate(90deg)'
              e.currentTarget.style.boxShadow = 'var(--glow-cyan)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'
              e.currentTarget.style.transform = 'rotate(0deg)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div
          style={{
            flex: 1,
            overflow: 'auto',
            padding: 'var(--space-xl)',
            backgroundColor: 'rgba(0, 0, 0, 0.2)'
          }}
        >
          <div
            style={{
              fontFamily: 'monospace',
              fontSize: '0.9rem',
              lineHeight: 1.7,
              color: 'var(--text-base)',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word'
            }}
          >
            {reference.content || reference.snippet || 'No content available.'}
          </div>
        </div>

        {/* Footer */}
        <div
          style={{
            padding: 'var(--space-md)',
            borderTop: '1px solid rgba(147, 51, 234, 0.2)',
            background: 'rgba(0, 0, 0, 0.3)',
            display: 'flex',
            justifyContent: 'flex-end',
            gap: '12px',
            flexShrink: 0
          }}
        >
          <button
            onClick={() => {
              const text = reference.content || reference.snippet || ''
              navigator.clipboard.writeText(text)
              alert('Document copied to clipboard')
            }}
            className="btn"
            style={{
              padding: '8px 16px',
              fontSize: '0.875rem'
            }}
          >
            Copy
          </button>
          <button
            onClick={onClose}
            className="btn"
            style={{
              padding: '8px 16px',
              fontSize: '0.875rem',
              background: 'linear-gradient(135deg, rgba(147, 51, 234, 0.3), rgba(0, 212, 255, 0.3))'
            }}
          >
            Close
          </button>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes modalSlideIn {
          from {
            opacity: 0;
            transform: translate(-50%, -48%) scale(0.95);
          }
          to {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
          }
        }

        /* Custom scrollbar for modal content */
        div::-webkit-scrollbar {
          width: 8px;
        }

        div::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.2);
          border-radius: 4px;
        }

        div::-webkit-scrollbar-thumb {
          background: rgba(147, 51, 234, 0.5);
          border-radius: 4px;
        }

        div::-webkit-scrollbar-thumb:hover {
          background: rgba(147, 51, 234, 0.7);
        }
      `}</style>
    </>
  )
}

