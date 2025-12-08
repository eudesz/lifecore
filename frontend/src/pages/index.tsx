import { useState } from 'react'
import ParticlesBackground from '@/components/ParticlesBackground'
import UserSelector from '@/components/auth/UserSelector'

export default function Index() {
  const [showUserSelector, setShowUserSelector] = useState(false)

  return (
    <div style={{ position: 'relative', minHeight: '100vh', overflowX: 'hidden', background: 'var(--bg-deep)' }}>
      <ParticlesBackground />
      
      {/* Main Container */}
      <div style={{ position: 'relative', zIndex: 10 }}>
        
        {/* Hero Section */}
        <section style={{
          minHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          padding: '20px',
          background: 'radial-gradient(circle at center, rgba(0, 242, 234, 0.05) 0%, transparent 60%)'
        }}>
          <div className="animate-in" style={{ maxWidth: '900px' }}>
            <div style={{ 
              display: 'inline-block', 
              padding: '8px 16px', 
              borderRadius: '30px', 
              background: 'rgba(255,255,255,0.05)', 
              border: '1px solid var(--border-light)',
              color: 'var(--primary)', 
              fontSize: '12px', 
              fontWeight: 600, 
              letterSpacing: '0.1em',
              marginBottom: '24px',
              textTransform: 'uppercase'
            }}>
              The Future of Health Intelligence
            </div>
          
          <h1 style={{
              fontSize: 'clamp(3rem, 6vw, 5rem)',
              lineHeight: 1.1,
              marginBottom: '24px',
              background: 'linear-gradient(135deg, #fff 0%, #94a3b8 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
              fontFamily: 'Roboto, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif'
          }}>
              Your Health Data,<br />
              <span style={{ color: 'var(--primary)', WebkitTextFillColor: 'var(--primary)' }}>Decoded by AI.</span>
          </h1>
          
          <p style={{
              fontSize: 'clamp(1.1rem, 2vw, 1.3rem)',
              color: 'var(--text-muted)',
              marginBottom: '40px',
              maxWidth: '600px',
              marginLeft: 'auto',
              marginRight: 'auto',
              lineHeight: 1.6
          }}>
              Connect your biometric streams, analyze decades of history, and receive clinical-grade insights in seconds.
          </p>
          <p
            style={{
              fontSize: '0.95rem',
              color: 'var(--text-muted)',
              marginBottom: '32px',
              maxWidth: '720px',
              marginLeft: 'auto',
              marginRight: 'auto',
              lineHeight: 1.6,
            }}
          >
            Ask the assistant any type of question about your health data —{' '}
            <strong>descriptive</strong>, <strong>exploratory</strong>,{' '}
            <strong>inferential</strong>, <strong>predictive</strong>,{' '}
            <strong>causal</strong>, or <strong>deterministic</strong> — and it will
            respond in clear, human language, tailored to your level of expertise.
          </p>

            <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={() => setShowUserSelector(true)}
                className="btn"
              style={{
                  background: 'var(--primary)',
                  color: '#000',
                border: 'none',
                  padding: '16px 40px',
                  fontSize: '16px',
                  fontWeight: 600,
                  boxShadow: '0 0 30px rgba(0, 242, 234, 0.3)'
              }}
            >
                Login
            </button>
              <button
                className="btn secondary"
              style={{
                  padding: '16px 40px',
                  fontSize: '16px'
              }}
              >
                View Demo
              </button>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section style={{ padding: '80px 20px', background: 'var(--bg-dark)' }}>
          <div className="container">
            <div style={{ textAlign: 'center', marginBottom: '60px' }}>
              <h2 style={{ fontSize: '32px', marginBottom: '16px' }}>Engineered for Longevity</h2>
              <p style={{ color: 'var(--text-muted)' }}>A complete operating system for your biological data.</p>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: '30px' 
            }}>
              {[
                { title: 'Biometric Integration', desc: 'Unified stream from wearables, lab reports, and clinical notes.', icon: '🧬' },
                { title: 'Neural Analysis', desc: 'GPT-4o powered correlation engine detecting hidden patterns.', icon: '🧠' },
                { title: 'Temporal Intelligence', desc: 'Visualize 50+ years of medical history in a fluid timeline.', icon: '⏳' },
                { title: 'Predictive Risk', desc: 'Early detection of potential health risks based on historical data patterns.', icon: '🛡️' },
                { title: 'Document Intelligence', desc: 'Process unstructured PDFs and clinical notes into structured data.', icon: '📄' },
                { title: 'Secure Sharing', desc: 'Share ephemeral, encrypted access links with your doctors.', icon: '🔒' }
              ].map((f, i) => (
                <div key={i} className="card" style={{ padding: '32px', transition: 'all 0.3s', borderTop: '1px solid var(--border-light)' }}>
                  <div style={{ fontSize: '40px', marginBottom: '20px' }}>{f.icon}</div>
                  <h3 style={{ fontSize: '20px', marginBottom: '12px', color: 'var(--text-main)' }}>{f.title}</h3>
                  <p style={{ color: 'var(--text-muted)', lineHeight: 1.6 }}>{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Stats / Trust */}
        <section style={{ padding: '80px 20px', borderTop: '1px solid var(--border-light)' }}>
          <div className="container" style={{ textAlign: 'center' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '40px' }}>
              <div>
                <div style={{ fontSize: '48px', fontWeight: 700, color: 'var(--primary)' }}>100%</div>
                <div style={{ color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', fontSize: '12px' }}>Private & Local</div>
              </div>
              <div>
                <div style={{ fontSize: '48px', fontWeight: 700, color: 'var(--primary)' }}>50+</div>
                <div style={{ color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', fontSize: '12px' }}>Years History</div>
              </div>
              <div>
                <div style={{ fontSize: '48px', fontWeight: 700, color: 'var(--primary)' }}>0.2s</div>
                <div style={{ color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', fontSize: '12px' }}>Query Latency</div>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer style={{ padding: '40px 20px', borderTop: '1px solid var(--border-light)', textAlign: 'center' }}>
          <div style={{ opacity: 0.5, fontSize: '14px' }}>
            <p>&copy; 2025 QuantIA Inc. San Francisco, CA.</p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '10px' }}>
              <span>Privacy</span>
              <span>Terms</span>
              <span>Security</span>
            </div>
          </div>
        </footer>

      </div>

      <UserSelector 
        isOpen={showUserSelector} 
        onClose={() => setShowUserSelector(false)} 
      />
    </div>
  )
}
