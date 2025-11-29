import BlockchainVerifier from '../components/BlockchainVerifier'

export default function BlockchainPage() {
  return (
    <div className="blockchain-page" style={{ paddingTop: '100px', minHeight: '100vh' }}>
      <div className="container" style={{ maxWidth: '800px', margin: '0 auto', padding: 'var(--space-xl)' }}>
        
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-2xl)' }}>
          <span className="section-badge glass-badge" style={{ marginBottom: 'var(--space-md)', display: 'inline-block' }}>
            <i className="fas fa-link"></i> Immutable Evidence
          </span>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 700, marginBottom: 'var(--space-md)' }}>
            Blockchain <span className="gradient-text">Ledger</span>
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', lineHeight: 1.6 }}>
            Every verification performed by RapidVerify is anchored to the Polygon blockchain. 
            This ensures that our fact-checks are tamper-proof, transparent, and permanently accessible.
          </p>
        </div>

        <BlockchainVerifier />

        <div style={{ marginTop: 'var(--space-3xl)', padding: 'var(--space-xl)', background: 'rgba(0,0,0,0.2)', borderRadius: 'var(--radius-lg)' }}>
          <h3 style={{ marginBottom: 'var(--space-lg)', textAlign: 'center' }}>How it works</h3>
          <div style={{ display: 'grid', gap: 'var(--space-lg)' }}>
            <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
              <div style={{ width: '32px', height: '32px', background: 'var(--primary)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>1</div>
              <div>
                <h4 style={{ marginBottom: 'var(--space-xs)' }}>Content Hashing</h4>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>We create a unique cryptographic fingerprint (SHA-256) of the verified content.</p>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
              <div style={{ width: '32px', height: '32px', background: 'var(--secondary)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>2</div>
              <div>
                <h4 style={{ marginBottom: 'var(--space-xs)' }}>Smart Contract Recording</h4>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>The hash, along with the verification score and verdict, is sent to our smart contract on Polygon.</p>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
              <div style={{ width: '32px', height: '32px', background: 'var(--success)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>3</div>
              <div>
                <h4 style={{ marginBottom: 'var(--space-xs)' }}>Permanent Proof</h4>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Anyone can verify the record using the Record ID, ensuring the fact-check hasn't been altered.</p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
