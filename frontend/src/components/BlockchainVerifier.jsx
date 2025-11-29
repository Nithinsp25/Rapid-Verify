import { useState } from 'react'
import { motion } from 'framer-motion'

/**
 * Blockchain Verifier Component
 * Allows users to verify blockchain records by record ID or claim text
 */
export default function BlockchainVerifier() {
  const [recordId, setRecordId] = useState('')
  const [claimText, setClaimText] = useState('')
  const [verifying, setVerifying] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleVerifyById = async () => {
    if (!recordId.trim()) {
      setError('Please enter a record ID')
      return
    }

    setVerifying(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch(`/api/blockchain/verify/${recordId}`)
      const data = await response.json()

      if (data.success) {
        setResult(data)
      } else {
        setError(data.error || 'Verification failed')
      }
    } catch (err) {
      setError('Failed to verify record. Please try again.')
    } finally {
      setVerifying(false)
    }
  }

  const handleVerifyContent = async () => {
    if (!recordId.trim() || !claimText.trim()) {
      setError('Please enter both record ID and claim text')
      return
    }

    setVerifying(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/api/blockchain/verify-content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          record_id: recordId,
          claim_text: claimText
        })
      })

      const data = await response.json()

      if (data.success) {
        setResult(data)
      } else {
        setError(data.error || 'Verification failed')
      }
    } catch (err) {
      setError('Failed to verify content. Please try again.')
    } finally {
      setVerifying(false)
    }
  }

  return (
    <div style={{
      padding: 'var(--space-lg)',
      background: 'var(--glass-bg)',
      borderRadius: 'var(--radius-lg)',
      border: '1px solid var(--glass-border)'
    }}>
      <h3 style={{ 
        marginBottom: 'var(--space-lg)', 
        display: 'flex', 
        alignItems: 'center', 
        gap: 'var(--space-sm)',
        color: '#9B59B6'
      }}>
        <span>⛓️</span> Verify Blockchain Record
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
        {/* Record ID Input */}
        <div>
          <label style={{ 
            display: 'block', 
            marginBottom: 'var(--space-xs)', 
            fontSize: '0.85rem',
            color: 'var(--text-secondary)'
          }}>
            Record ID
          </label>
          <input
            type="text"
            value={recordId}
            onChange={(e) => setRecordId(e.target.value)}
            placeholder="0x..."
            style={{
              width: '100%',
              padding: 'var(--space-sm) var(--space-md)',
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid var(--glass-border)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-primary)',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.85rem'
            }}
          />
        </div>

        {/* Claim Text Input (for content verification) */}
        <div>
          <label style={{ 
            display: 'block', 
            marginBottom: 'var(--space-xs)', 
            fontSize: '0.85rem',
            color: 'var(--text-secondary)'
          }}>
            Original Claim Text (optional, for content verification)
          </label>
          <textarea
            value={claimText}
            onChange={(e) => setClaimText(e.target.value)}
            placeholder="Paste the original claim text to verify it matches the blockchain record..."
            rows={3}
            style={{
              width: '100%',
              padding: 'var(--space-sm) var(--space-md)',
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid var(--glass-border)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-primary)',
              fontSize: '0.85rem',
              resize: 'vertical'
            }}
          />
        </div>

        {/* Buttons */}
        <div style={{ display: 'flex', gap: 'var(--space-sm)' }}>
          <motion.button
            onClick={handleVerifyById}
            disabled={verifying || !recordId.trim()}
            style={{
              flex: 1,
              padding: 'var(--space-sm) var(--space-md)',
              background: 'var(--primary)',
              border: 'none',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--bg-primary)',
              fontWeight: 500,
              cursor: verifying || !recordId.trim() ? 'not-allowed' : 'pointer',
              opacity: verifying || !recordId.trim() ? 0.5 : 1
            }}
            whileHover={{ scale: verifying ? 1 : 1.02 }}
            whileTap={{ scale: verifying ? 1 : 0.98 }}
          >
            {verifying ? 'Verifying...' : 'Verify Record'}
          </motion.button>

          {claimText.trim() && (
            <motion.button
              onClick={handleVerifyContent}
              disabled={verifying || !recordId.trim() || !claimText.trim()}
              style={{
                flex: 1,
                padding: 'var(--space-sm) var(--space-md)',
                background: 'linear-gradient(135deg, rgba(138, 43, 226, 0.3), rgba(75, 0, 130, 0.2))',
                border: '1px solid rgba(138, 43, 226, 0.5)',
                borderRadius: 'var(--radius-sm)',
                color: '#9B59B6',
                fontWeight: 500,
                cursor: verifying || !recordId.trim() || !claimText.trim() ? 'not-allowed' : 'pointer',
                opacity: verifying || !recordId.trim() || !claimText.trim() ? 0.5 : 1
              }}
              whileHover={{ scale: verifying ? 1 : 1.02 }}
              whileTap={{ scale: verifying ? 1 : 0.98 }}
            >
              {verifying ? 'Verifying...' : 'Verify Content Match'}
            </motion.button>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            style={{
              padding: 'var(--space-sm) var(--space-md)',
              background: 'rgba(255, 107, 107, 0.15)',
              border: '1px solid rgba(255, 107, 107, 0.3)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--danger)',
              fontSize: '0.85rem'
            }}
          >
            ⚠️ {error}
          </motion.div>
        )}

        {/* Result Display */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            style={{
              padding: 'var(--space-md)',
              background: result.verified 
                ? 'rgba(107, 203, 119, 0.15)' 
                : 'rgba(255, 170, 0, 0.15)',
              border: `1px solid ${result.verified ? 'rgba(107, 203, 119, 0.3)' : 'rgba(255, 170, 0, 0.3)'}`,
              borderRadius: 'var(--radius-sm)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', marginBottom: 'var(--space-sm)' }}>
              <span style={{ fontSize: '1.2rem' }}>
                {result.verified ? '✅' : '⚠️'}
              </span>
              <span style={{ 
                fontWeight: 600,
                color: result.verified ? 'var(--success)' : 'var(--warning)'
              }}>
                {result.verified ? 'Record Verified' : result.reason || 'Verification Failed'}
              </span>
            </div>

            {result.record && (
              <div style={{ 
                marginTop: 'var(--space-sm)', 
                padding: 'var(--space-sm)',
                background: 'rgba(0, 0, 0, 0.2)',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.8rem'
              }}>
                <div style={{ display: 'grid', gap: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Network:</span>
                    <span>{result.record.network || 'Unknown'}</span>
                  </div>
                  {result.record.timestamp && (
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Timestamp:</span>
                      <span>{new Date(result.record.timestamp).toLocaleString()}</span>
                    </div>
                  )}
                  {result.record.verification_score !== undefined && (
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Score:</span>
                      <span>{(result.record.verification_score * 100).toFixed(1)}%</span>
                    </div>
                  )}
                  {result.record.status && (
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Status:</span>
                      <span style={{ textTransform: 'capitalize' }}>{result.record.status}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {result.message && (
              <p style={{ 
                marginTop: 'var(--space-sm)', 
                fontSize: '0.8rem',
                color: 'var(--text-secondary)'
              }}>
                {result.message}
              </p>
            )}
          </motion.div>
        )}
      </div>
    </div>
  )
}


