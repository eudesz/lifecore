import Link from 'next/link'

export default function Navbar() {
  return (
    <header
      className="navbar"
      style={{
        padding: '12px 20px',
        marginBottom: '1rem',
        position: 'sticky',
        top: '0',
        zIndex: 40,
        background: 'rgba(2, 4, 10, 0.8)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid var(--border-light)'
      }}
    >
      <div className="navbar-row" style={{ justifyContent: 'center', width: '100%' }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none' }}>
          <img src="/quantia-logo.svg" alt="QuantIA" width={28} height={28} />
          <span className="text-gradient" style={{ fontWeight: 700, fontSize: '18px', fontFamily: 'Playfair Display, serif' }}>QuantIA</span>
        </Link>
      </div>
    </header>
  )
}
