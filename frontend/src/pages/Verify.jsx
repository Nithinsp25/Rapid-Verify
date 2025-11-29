import { useState } from 'react'

export default function Verify() {
  const [activeTab, setActiveTab] = useState('url')
  const [urlInput, setUrlInput] = useState('')
  const [textInput, setTextInput] = useState('')
  const [imageInput, setImageInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const validateInput = (type) => {
    if (type === 'url') {
      if (!urlInput.trim()) {
        setResult({ error: 'Please enter a URL' })
        return false
      }
      try {
        new URL(urlInput) // Validate URL format
      } catch {
        setResult({ error: 'Please enter a valid URL (e.g., https://example.com)' })
        return false
      }
    } else if (type === 'text') {
      if (!textInput.trim()) {
        setResult({ error: 'Please enter text to verify' })
        return false
      }
      if (textInput.trim().length < 10) {
        setResult({ error: 'Text must be at least 10 characters long' })
        return false
      }
    } else if (type === 'image') {
      if (!imageInput.trim()) {
        setResult({ error: 'Please enter an image URL' })
        return false
      }
      try {
        new URL(imageInput)
      } catch {
        setResult({ error: 'Please enter a valid image URL' })
        return false
      }
    }
    return true
  }

  const handleVerify = async (type) => {
    // Input validation
    if (!validateInput(type)) {
      return
    }

    setLoading(true)
    setResult(null)
    
    try {
      let endpoint = '/api/verify'
      let body = {}
      
      if (type === 'url') {
        endpoint = '/api/verify/url'
        body = { url: urlInput.trim() }
      } else if (type === 'text') {
        body = { claim: textInput.trim() }
      } else if (type === 'image') {
        endpoint = '/api/verify/image'
        body = { image_url: imageInput.trim() }
      }
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: `Server error: ${response.status}` }))
        throw new Error(errorData.error || `HTTP ${response.status}`)
      }
      
      const data = await response.json()
      
      if (!data.success && data.error) {
        throw new Error(data.error)
      }
      
      setResult({ ...data, type })
      
      // Auto-scroll to results section after verification completes
      setTimeout(() => {
        const resultElement = document.querySelector('.result-container')
        if (resultElement) {
          resultElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      }, 100)
    } catch (error) {
      setResult({ error: error.message || 'Failed to verify. Please try again.' })
    } finally {
      setLoading(false)
    }
  }

  const getScoreClass = (score) => {
    if (score < 0.4) return 'low'
    if (score < 0.7) return 'medium'
    return 'high'
  }

  const getStatusText = (score) => {
    if (score >= 0.7) return 'LIKELY AUTHENTIC'
    if (score >= 0.4) return 'NEEDS VERIFICATION'
    return 'LIKELY FAKE'
  }

  return (
    <div className="verify-page">
      <main className="verify-container">
        {/* Header */}
        <div className="verify-header animate-slide-up">
          <span className="section-badge glass-badge">
            <i className="fas fa-shield-alt"></i> AI-Powered Verification
          </span>
          <h1>Verify <span className="gradient-text">News & Claims</span></h1>
          <p>Paste a news link, WhatsApp forward, or suspicious claim. We'll scrape the content, verify against trusted sources, and show you WHERE we verified it.</p>
        </div>

        {/* Verification Card */}
        <div className="verify-card glass-panel-heavy animate-slide-up delay-1">
          {/* Tabs */}
          <div className="verify-tabs">
            <button 
              className={`verify-tab ${activeTab === 'url' ? 'active' : ''}`}
              onClick={() => { setActiveTab('url'); setResult(null); }}
            >
              <i className="fas fa-link"></i>
              <span>News Link</span>
            </button>
            <button 
              className={`verify-tab ${activeTab === 'text' ? 'active' : ''}`}
              onClick={() => { setActiveTab('text'); setResult(null); }}
            >
              <i className="fas fa-comment"></i>
              <span>Text/Message</span>
            </button>
            <button 
              className={`verify-tab ${activeTab === 'image' ? 'active' : ''}`}
              onClick={() => { setActiveTab('image'); setResult(null); }}
            >
              <i className="fas fa-image"></i>
              <span>Image</span>
            </button>
          </div>

          {/* URL Tab */}
          {activeTab === 'url' && (
            <div className="tab-content">
              <div className="form-group">
                <label>
                  <i className="fas fa-newspaper" style={{ color: 'var(--primary)', marginRight: '8px' }}></i>
                  Paste News Article URL
                </label>
                <input 
                  type="url"
                  className="neo-input"
                  style={{ minHeight: 'auto', padding: 'var(--space-md)' }}
                  placeholder="https://example.com/news-article"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                />
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 'var(--space-sm)' }}>
                  We'll scrape the article, extract claims, and verify against fact-checking sources.
                </p>
              </div>
              <button 
                className={`neo-btn-primary ${loading ? 'loading' : ''}`}
                style={{ width: '100%', marginTop: 'var(--space-md)' }}
                onClick={() => handleVerify('url')}
                disabled={loading || !urlInput}
              >
                <i className="fas fa-search"></i>
                <span>Verify News Article</span>
                <div className="btn-loader"></div>
              </button>
            </div>
          )}

          {/* Text Tab */}
          {activeTab === 'text' && (
            <div className="tab-content">
              <div className="form-group">
                <label>
                  <i className="fas fa-comment-dots" style={{ color: 'var(--primary)', marginRight: '8px' }}></i>
                  Paste WhatsApp Forward / Claim / Message
                </label>
                <textarea 
                  className="neo-input"
                  placeholder={`Paste the suspicious message, claim, or WhatsApp forward here...

Example:
'URGENT: Government giving free ₹10,000 to all citizens! Share to 10 groups to claim. Forward before deleted!'`}
                  rows="5"
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                ></textarea>
              </div>
              <button 
                className={`neo-btn-primary ${loading ? 'loading' : ''}`}
                style={{ width: '100%', marginTop: 'var(--space-md)' }}
                onClick={() => handleVerify('text')}
                disabled={loading || !textInput}
              >
                <i className="fas fa-check-double"></i>
                <span>Verify Message</span>
                <div className="btn-loader"></div>
              </button>
            </div>
          )}

          {/* Image Tab */}
          {activeTab === 'image' && (
            <div className="tab-content">
              <div className="form-group">
                <label>
                  <i className="fas fa-image" style={{ color: 'var(--primary)', marginRight: '8px' }}></i>
                  Paste Image URL
                </label>
                <input 
                  type="url"
                  className="neo-input"
                  style={{ minHeight: 'auto', padding: 'var(--space-md)' }}
                  placeholder="https://example.com/suspicious-image.jpg"
                  value={imageInput}
                  onChange={(e) => setImageInput(e.target.value)}
                />
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 'var(--space-sm)' }}>
                  We'll analyze the image for manipulation and extract any text for verification.
                </p>
              </div>
              <button 
                className={`neo-btn-primary ${loading ? 'loading' : ''}`}
                style={{ width: '100%', marginTop: 'var(--space-md)' }}
                onClick={() => handleVerify('image')}
                disabled={loading || !imageInput}
              >
                <i className="fas fa-eye"></i>
                <span>Analyze Image</span>
                <div className="btn-loader"></div>
              </button>
            </div>
          )}

          {/* Results */}
          {result && !result.error && (
            <div className="result-container" style={{ marginTop: 'var(--space-xl)', paddingTop: 'var(--space-xl)', borderTop: '1px solid var(--glass-border)' }}>
              <div className="verification-display">
                {/* Header */}
                <div className="result-header">
                  <div className="result-status">
                    <div className={`status-icon ${result.status || 'investigating'}`}>
                      <i className={`fas ${result.status === 'verified' ? 'fa-check-circle' : result.status === 'debunked' ? 'fa-times-circle' : 'fa-question-circle'}`}></i>
                    </div>
                    <div className="status-text">
                      <h4>{getStatusText(result.score || 0.5)}</h4>
                      <span>{result.confidence || 'medium'} confidence</span>
                    </div>
                  </div>
                  <div className="score-display">
                    <span className={`score-value ${getScoreClass(result.score || 0.5)}`}>
                      {Math.round((result.score || 0.5) * 100)}%
                    </span>
                    <span className="score-label">Authenticity</span>
                  </div>
                </div>

                {/* Article Preview */}
                {result.article?.title && (
                  <div style={{
                    background: 'rgba(0, 0, 0, 0.3)',
                    borderRadius: 'var(--radius-md)',
                    padding: 'var(--space-lg)',
                    marginBottom: 'var(--space-lg)',
                    borderLeft: '4px solid var(--primary)'
                  }}>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: 'var(--space-sm)', color: 'var(--text-primary)' }}>
                      {result.article.title}
                    </h3>
                    <div style={{ display: 'flex', gap: 'var(--space-lg)', marginBottom: 'var(--space-md)', flexWrap: 'wrap' }}>
                      {result.article.source && (
                        <span style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                          <i className="fas fa-newspaper" style={{ color: 'var(--primary)' }}></i> {result.article.source}
                        </span>
                      )}
                    </div>
                    {result.source_credibility?.tier && (
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 'var(--space-sm)',
                        padding: 'var(--space-sm) var(--space-md)',
                        borderRadius: 'var(--radius-md)',
                        fontSize: '0.85rem',
                        fontWeight: 500,
                        background: result.source_credibility.tier === 'tier1' ? 'rgba(107, 203, 119, 0.2)' :
                                   result.source_credibility.tier === 'tier2' ? 'rgba(0, 245, 212, 0.2)' :
                                   'rgba(255, 217, 61, 0.2)',
                        color: result.source_credibility.tier === 'tier1' ? 'var(--success)' :
                               result.source_credibility.tier === 'tier2' ? 'var(--primary)' :
                               'var(--warning)'
                      }}>
                        <i className={`fas fa-${result.source_credibility.tier === 'tier1' ? 'check-double' : result.source_credibility.tier === 'tier2' ? 'check' : 'question'}`}></i>
                        {result.source_credibility.tier === 'tier1' ? 'Highly Trusted Source' : 
                         result.source_credibility.tier === 'tier2' ? 'Trusted Source' : 
                         result.source_credibility.tier === 'tier3' ? 'Generally Reliable' : 'Unknown Source'}
                      </span>
                    )}
                  </div>
                )}

                {/* Verdict */}
                <div style={{
                  padding: 'var(--space-md)',
                  background: 'rgba(0, 245, 212, 0.05)',
                  borderLeft: '3px solid var(--primary)',
                  borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
                  margin: 'var(--space-lg) 0'
                }}>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                    <strong>Verdict:</strong> {result.verdict || 'Analysis complete'}
                  </p>
                </div>

                {/* Warnings */}
                {result.warnings && result.warnings.length > 0 && (
                  <div style={{
                    background: 'rgba(255, 107, 107, 0.1)',
                    border: '1px solid rgba(255, 107, 107, 0.3)',
                    borderRadius: 'var(--radius-md)',
                    padding: 'var(--space-lg)',
                    marginTop: 'var(--space-lg)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', color: 'var(--danger)', fontWeight: 600, marginBottom: 'var(--space-md)' }}>
                      <i className="fas fa-exclamation-triangle"></i> Warnings Detected
                    </div>
                    {result.warnings.map((w, i) => (
                      <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-sm)', padding: 'var(--space-sm) 0', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                        <i className="fas fa-flag" style={{ color: 'var(--danger)', marginTop: '3px' }}></i> {w}
                      </div>
                    ))}
                  </div>
                )}

                {/* Key Claims */}
                {result.key_claims && result.key_claims.length > 0 && (
                  <div style={{ marginTop: 'var(--space-lg)' }}>
                    <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: 'var(--space-md)' }}>
                      <i className="fas fa-quote-left" style={{ color: 'var(--secondary)' }}></i> Key Claims Extracted
                    </div>
                    {result.key_claims.slice(0, 5).map((claim, i) => (
                      <div key={i} style={{
                        background: 'rgba(123, 44, 191, 0.1)',
                        borderLeft: '3px solid var(--secondary)',
                        padding: 'var(--space-md)',
                        marginBottom: 'var(--space-sm)',
                        borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
                        fontSize: '0.9rem',
                        color: 'var(--text-secondary)'
                      }}>
                        {typeof claim === 'string' ? claim.substring(0, 150) : claim}...
                      </div>
                    ))}
                  </div>
                )}

                {/* Verification Sources */}
                <div style={{ marginTop: 'var(--space-xl)', paddingTop: 'var(--space-xl)', borderTop: '1px solid var(--glass-border)' }}>
                  <h3 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', fontSize: '1.1rem', fontWeight: 600, marginBottom: 'var(--space-lg)' }}>
                    <i className="fas fa-search" style={{ color: 'var(--primary)' }}></i> Verification Sources
                  </h3>
                  <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-lg)', fontSize: '0.9rem' }}>
                    We checked these sources to verify this news:
                  </p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
                    {(result.fact_checks || []).map((fc, i) => (
                      <div key={i} style={{
                        background: 'rgba(0, 0, 0, 0.2)',
                        borderRadius: 'var(--radius-md)',
                        padding: 'var(--space-md)',
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: 'var(--space-md)'
                      }}>
                        <div style={{
                          width: '40px',
                          height: '40px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          background: 'rgba(0, 245, 212, 0.1)',
                          borderRadius: 'var(--radius-sm)',
                          color: 'var(--primary)',
                          flexShrink: 0
                        }}>
                          <i className="fas fa-clipboard-check"></i>
                        </div>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: 600, marginBottom: 'var(--space-xs)' }}>{fc.source}</div>
                          {fc.rating && fc.rating !== 'Unknown' && (
                            <span style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: 'var(--space-xs)',
                              padding: 'var(--space-xs) var(--space-sm)',
                              borderRadius: 'var(--radius-sm)',
                              fontSize: '0.75rem',
                              fontWeight: 600,
                              background: fc.rating?.toLowerCase().includes('false') ? 'rgba(255, 107, 107, 0.2)' : 'rgba(107, 203, 119, 0.2)',
                              color: fc.rating?.toLowerCase().includes('false') ? 'var(--danger)' : 'var(--success)'
                            }}>{fc.rating}</span>
                          )}
                          {(fc.search_url || fc.url) && (
                            <a href={fc.search_url || fc.url} target="_blank" rel="noopener noreferrer" style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: 'var(--space-xs)',
                              marginTop: 'var(--space-sm)',
                              padding: 'var(--space-xs) var(--space-sm)',
                              background: 'rgba(0, 245, 212, 0.1)',
                              borderRadius: 'var(--radius-sm)',
                              color: 'var(--primary)',
                              textDecoration: 'none',
                              fontSize: '0.8rem'
                            }}>
                              <i className="fas fa-external-link-alt"></i> Search
                            </a>
                          )}
                        </div>
                      </div>
                    ))}
                    
                    {(result.cross_references || []).map((ref, i) => (
                      <div key={i} style={{
                        background: 'rgba(0, 0, 0, 0.2)',
                        borderRadius: 'var(--radius-md)',
                        padding: 'var(--space-md)',
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: 'var(--space-md)'
                      }}>
                        <div style={{
                          width: '40px',
                          height: '40px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          background: 'rgba(107, 203, 119, 0.1)',
                          borderRadius: 'var(--radius-sm)',
                          color: 'var(--success)',
                          flexShrink: 0
                        }}>
                          <i className="fas fa-newspaper"></i>
                        </div>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: 600, marginBottom: 'var(--space-xs)' }}>{ref.source}</div>
                          {ref.note && <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 'var(--space-xs)' }}>{ref.note}</div>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommendation */}
                <div style={{
                  marginTop: 'var(--space-xl)',
                  padding: 'var(--space-lg)',
                  background: `rgba(${(result.score || 0.5) < 0.4 ? '255, 107, 107' : (result.score || 0.5) < 0.7 ? '255, 217, 61' : '107, 203, 119'}, 0.1)`,
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'center'
                }}>
                  <span style={{ fontSize: '1.5rem', display: 'block', marginBottom: 'var(--space-sm)' }}>
                    {(result.score || 0.5) < 0.4 ? '🚫' : (result.score || 0.5) < 0.7 ? '⚠️' : '✅'}
                  </span>
                  <span style={{
                    color: (result.score || 0.5) < 0.4 ? 'var(--danger)' : (result.score || 0.5) < 0.7 ? 'var(--warning)' : 'var(--success)',
                    fontWeight: 600,
                    fontSize: '1.1rem'
                  }}>
                    {(result.score || 0.5) < 0.4 ? 'DO NOT SHARE - Likely Misinformation!' : 
                     (result.score || 0.5) < 0.7 ? 'VERIFY before sharing' : 'Appears Credible'}
                  </span>
                </div>

                {/* Blockchain Proof Section - Always Visible */}
                <div style={{
                  marginTop: 'var(--space-xl)',
                  padding: 'var(--space-lg)',
                  background: 'linear-gradient(135deg, rgba(138, 43, 226, 0.15), rgba(75, 0, 130, 0.08))',
                  border: '1px solid rgba(138, 43, 226, 0.3)',
                  borderRadius: 'var(--radius-lg)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', marginBottom: 'var(--space-lg)' }}>
                    <span style={{ fontSize: '1.5rem' }}>⛓️</span>
                    <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#9B59B6' }}>Blockchain Proof</h3>
                    {result.blockchain ? (
                      <span style={{
                        padding: '2px 8px',
                        fontSize: '0.7rem',
                        borderRadius: '4px',
                        background: result.blockchain.mode === 'live' ? 'rgba(0, 255, 136, 0.2)' : 'rgba(255, 170, 0, 0.2)',
                        color: result.blockchain.mode === 'live' ? '#00ff88' : '#ffaa00'
                      }}>
                        {result.blockchain.mode === 'live' ? '🔗 On-Chain' : '⏳ Demo Mode'}
                      </span>
                    ) : (
                      <span style={{
                        padding: '2px 8px',
                        fontSize: '0.7rem',
                        borderRadius: '4px',
                        background: 'rgba(255, 255, 255, 0.1)',
                        color: 'var(--text-muted)'
                      }}>
                        Not Recorded
                      </span>
                    )}
                  </div>
                  
                  {result.blockchain ? (
                    <>
                    
                    <div style={{ display: 'grid', gap: 'var(--space-sm)' }}>
                      <div style={{
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                        padding: 'var(--space-sm) var(--space-md)',
                        background: 'rgba(0, 0, 0, 0.2)',
                        borderRadius: 'var(--radius-sm)'
                      }}>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Record ID</span>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--primary)' }}>
                          {result.blockchain.record_id?.slice(0, 12)}...{result.blockchain.record_id?.slice(-8)}
                        </span>
                      </div>
                      
                      <div style={{
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                        padding: 'var(--space-sm) var(--space-md)',
                        background: 'rgba(0, 0, 0, 0.2)',
                        borderRadius: 'var(--radius-sm)'
                      }}>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Network</span>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
                          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#8247e5' }}></span>
                          {result.blockchain.network}
                        </span>
                      </div>
                      
                      {result.blockchain.transaction_hash && (
                        <div style={{
                          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                          padding: 'var(--space-sm) var(--space-md)',
                          background: 'rgba(0, 0, 0, 0.2)',
                          borderRadius: 'var(--radius-sm)'
                        }}>
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Transaction</span>
                          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                            {result.blockchain.transaction_hash?.slice(0, 10)}...{result.blockchain.transaction_hash?.slice(-6)}
                          </span>
                        </div>
                      )}
                      
                      {result.blockchain.block_number && (
                        <div style={{
                          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                          padding: 'var(--space-sm) var(--space-md)',
                          background: 'rgba(0, 0, 0, 0.2)',
                          borderRadius: 'var(--radius-sm)'
                        }}>
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Block</span>
                          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
                            #{result.blockchain.block_number.toLocaleString()}
                          </span>
                        </div>
                      )}
                      
                      <div style={{
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                        padding: 'var(--space-sm) var(--space-md)',
                        background: 'rgba(0, 0, 0, 0.2)',
                        borderRadius: 'var(--radius-sm)'
                      }}>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Timestamp</span>
                        <span style={{ fontSize: '0.8rem' }}>{result.blockchain.timestamp}</span>
                      </div>
                    </div>
                    
                      {result.blockchain.explorer_url && (
                        <a
                          href={result.blockchain.explorer_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--space-sm)',
                            marginTop: 'var(--space-lg)',
                            padding: 'var(--space-md)',
                            background: 'linear-gradient(135deg, rgba(138, 43, 226, 0.3), rgba(75, 0, 130, 0.2))',
                            border: '1px solid rgba(138, 43, 226, 0.5)',
                            borderRadius: 'var(--radius-md)',
                            color: '#9B59B6',
                            textDecoration: 'none',
                            fontWeight: 500,
                            transition: 'all 0.2s ease'
                          }}
                          onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                          onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                        >
                          <i className="fas fa-external-link-alt"></i>
                          View on Block Explorer
                        </a>
                      )}
                      
                      <p style={{ 
                        textAlign: 'center', 
                        fontSize: '0.75rem', 
                        color: 'var(--text-muted)', 
                        marginTop: 'var(--space-md)',
                        marginBottom: 0
                      }}>
                        🔒 This verification is permanently recorded for transparency and tamper-proof evidence
                      </p>
                    </>
                  ) : (
                    <div style={{
                      padding: 'var(--space-lg)',
                      textAlign: 'center',
                      background: 'rgba(0, 0, 0, 0.2)',
                      borderRadius: 'var(--radius-md)'
                    }}>
                      <p style={{ 
                        color: 'var(--text-secondary)', 
                        marginBottom: 'var(--space-sm)',
                        fontSize: '0.9rem'
                      }}>
                        {result.score < 0.4 
                          ? '⚠️ High-risk content detected. Blockchain recording is available but not configured.'
                          : 'ℹ️ Blockchain recording is only enabled for high-risk content (score < 40%). This verification scored ' + Math.round((result.score || 0.5) * 100) + '%.'
                        }
                      </p>
                      <p style={{ 
                        fontSize: '0.75rem', 
                        color: 'var(--text-muted)',
                        marginTop: 'var(--space-sm)'
                      }}>
                        🔒 Blockchain anchoring provides tamper-proof evidence for critical misinformation alerts
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Error */}
          {result?.error && (
            <div className="result-container" style={{ marginTop: 'var(--space-xl)', paddingTop: 'var(--space-xl)', borderTop: '1px solid var(--glass-border)' }}>
              <div style={{ textAlign: 'center', padding: 'var(--space-xl)', color: 'var(--danger)' }}>
                <i className="fas fa-exclamation-triangle" style={{ fontSize: '2rem', marginBottom: 'var(--space-md)' }}></i>
                <p>Error: {result.error}</p>
              </div>
            </div>
          )}
        </div>

        {/* WhatsApp Banner */}
        <div className="whatsapp-banner animate-slide-up delay-2">
          <div className="whatsapp-icon">
            <i className="fab fa-whatsapp"></i>
          </div>
          <div>
            <h4 style={{ color: '#25D366', marginBottom: 'var(--space-xs)' }}>
              <i className="fas fa-robot"></i> WhatsApp Bot Available!
            </h4>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: 'var(--space-sm)' }}>
              Forward suspicious messages directly to our bot for instant verification!
            </p>
            <p style={{ fontFamily: 'var(--font-mono)', background: 'rgba(37, 211, 102, 0.2)', padding: 'var(--space-xs) var(--space-sm)', borderRadius: 'var(--radius-sm)', color: '#25D366', display: 'inline-block' }}>
              +1 415 523 8886
            </p>
          </div>
        </div>

        {/* Verification Sources Info */}
        <div className="animate-slide-up delay-3" style={{ marginTop: 'var(--space-2xl)', textAlign: 'center' }}>
          <h3 style={{ marginBottom: 'var(--space-lg)', color: 'var(--text-secondary)' }}>
            <i className="fas fa-check-circle" style={{ color: 'var(--success)' }}></i> We Verify Against
          </h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 'var(--space-md)' }}>
            {['Google Fact Check', 'Snopes', 'PolitiFact', 'Alt News India', 'BOOM FactCheck', 'PIB India', 'Reuters', 'WHO'].map(src => (
              <span key={src} className="glass-badge">{src}</span>
            ))}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="footer" style={{ marginTop: 'var(--space-3xl)' }}>
        <div className="container">
          <div className="footer-bottom" style={{ borderTop: 'none', paddingTop: 0 }}>
            <p>&copy; 2025 RapidVerify. Mumbai Hacks '25</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
